import os
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import translation
from django.utils.translation import gettext as _

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

import arabic_reshaper
from bidi.algorithm import get_display

from .models import AnalysisResult
from JADWA_AI.models import Projects  # ✅ جدول المشاريع من تطبيقك الأساسي


# =======================
# Helpers
# =======================

def rtl(txt: str) -> str:
    txt = (txt or "").strip()
    if not txt:
        return ""
    reshaped = arabic_reshaper.reshape(txt)
    return get_display(reshaped)


ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def has_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text or ""))


def ensure_arabic_font():
    font_path = r"C:\Windows\Fonts\tahoma.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("tahoma.ttf not found in C:\\Windows\\Fonts")

    if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))


def wrap_ltr_lines(p: canvas.Canvas, text: str, max_width: float, font_name: str, font_size: int):
    p.setFont(font_name, font_size)
    lines_out = []
    for raw in (text or "").splitlines():
        raw = raw.strip()
        if not raw:
            lines_out.append("")
            continue
        words = raw.split(" ")
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if p.stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines_out.append(current)
                current = w
        if current:
            lines_out.append(current)
    return lines_out


def wrap_rtl_lines(p: canvas.Canvas, text: str, max_width: float, font_name: str, font_size: int):
    p.setFont(font_name, font_size)
    lines_out = []
    for raw in (text or "").splitlines():
        raw = raw.strip()
        if not raw:
            lines_out.append("")
            continue
        words = raw.split(" ")
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if p.stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines_out.append(rtl(current))
                current = w
        if current:
            lines_out.append(rtl(current))
    return lines_out


def current_lang(request) -> str:
    return translation.get_language() or getattr(request, "LANGUAGE_CODE", "en") or "en"


def get_recs_by_lang(result: AnalysisResult, lang: str) -> str:
    if str(lang).startswith("ar"):
        return (result.recommendations_ar or "").strip()
    return (result.recommendations_en or "").strip()


def get_status_by_lang(result: AnalysisResult, lang: str) -> str:
    if str(lang).startswith("ar"):
        return (result.recommendations_status_ar or "pending").strip()
    return (result.recommendations_status_en or "pending").strip()


def set_recs_by_lang(result: AnalysisResult, lang: str, recs_text: str, status: str):
    if str(lang).startswith("ar"):
        result.recommendations_ar = recs_text
        result.recommendations_status_ar = status
    else:
        result.recommendations_en = recs_text
        result.recommendations_status_en = status


# ✅ الحالة النهائية: تعتمد على probability و threshold فقط
def is_feasible_result(result: AnalysisResult) -> bool:
    try:
        return float(result.probability) >= float(result.threshold)
    except Exception:
        return False


def feasibility_label_by_lang(result: AnalysisResult, lang: str) -> str:
    ok = is_feasible_result(result)
    if str(lang).startswith("ar"):
        return "قابل للتنفيذ" if ok else "غير قابل للتنفيذ"
    return "Feasible" if ok else "Not Feasible"


def normalize_recommendations_text(result: AnalysisResult, lang: str, recs_text: str) -> str:
    text = (recs_text or "").strip()
    prob = float(getattr(result, "probability", 0) or 0)
    thr = float(getattr(result, "threshold", 0.5) or 0.5)
    ok = prob >= thr

    if str(lang).startswith("ar"):
        final_word = "قابل للتنفيذ" if ok else "غير قابل للتنفيذ"
        rule = f"تنبيه: القرار النهائي حسب النموذج = ({prob:.4f}) مقارنة بحد القرار ({thr:.2f})، لذلك المشروع {final_word}."
        if ok:
            text = re.sub(r"غير قابل للتنفيذ", "قابل للتنفيذ", text)
        else:
            text = re.sub(r"قابل للتنفيذ", "غير قابل للتنفيذ", text)
    else:
        final_word = "feasible" if ok else "not feasible"
        rule = f"Note: Final decision uses probability ({prob:.4f}) vs threshold ({thr:.2f}); therefore the project is {final_word}."
        if ok:
            text = re.sub(r"\bnot feasible\b", "feasible", text, flags=re.IGNORECASE)
        else:
            text = re.sub(r"\bis feasible\b", "is not feasible", text, flags=re.IGNORECASE)

    if not text:
        return rule
    if rule.lower() not in text.lower():
        text = f"{rule}\n\n{text}"
    return text


def map_economic_indicator(value):
    v = (value or "").strip()
    mapping = {
        "Low": 1, "Medium": 2, "High": 3,
        "low": 1, "medium": 2, "high": 3,
        "1": 1, "2": 2, "3": 3,
    }
    try:
        return float(v)
    except Exception:
        return float(mapping.get(v, 0))


def build_project_data(project: Projects) -> dict:
    # 1️⃣ نقرأ المنطقة والمدينة من المشروع
    region = (getattr(project, "project_region", "") or "").strip()
    city = (getattr(project, "project_city", "") or "").strip()

    # 2️⃣ نكوّن الموقع النهائي اللي يروح للـ ML
    if region and city:
        location_for_ml = f"{region}, {city}"
    else:
        location_for_ml = region or city

    # 3️⃣ نرجّع البيانات للذكاء الاصطناعي
    return {
        "type_project": getattr(project, "Project_type", "Service"),
        "region_project": location_for_ml,   # ⭐ هذا أهم سطر
        "budget_project": float(getattr(project, "project_budget", 0) or 0),
        "project_duration_days": int(getattr(project, "project_duration", 0) or 0),
        "num_saudi_employees": int(getattr(project, "number_of_employees", 0) or 0),
    }



# =======================
# Views
# =======================

@login_required
def run_analysis(request, project_id):
    from ai.services.analyzer import analyze_project

    project = get_object_or_404(Projects, id=project_id)
    project.refresh_from_db()

    project_data = build_project_data(project)

    # messages.info(
    #     request,
    #     f"DEBUG → region={getattr(project,'project_region',None)} | city={getattr(project,'project_city',None)} | location sent to ML={project_data.get('region_project')}"
    # )

    out = analyze_project(project_data, include_recommendations=False, lang=current_lang(request))

    saved_result = AnalysisResult.objects.create(
        user=request.user,
        project_id=project.id,
        project_name=getattr(project, "project_name", None)
                     or getattr(project, "name", None)
                     or getattr(project, "title", None)
                     or "Project",
        probability=float(out.get("probability", 0) or 0),
        threshold=float(out.get("threshold", 0.5) or 0.5),
        label=str(out.get("label", "") or ""),
        recommendations_ar="",
        recommendations_en="",
        recommendations_status_ar="pending",
        recommendations_status_en="pending",
    )

    messages.success(request, _("Analysis completed successfully!"))
    return redirect("analysis_result", result_id=saved_result.id)


@login_required
def analysis_result(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    lang = current_lang(request)
    is_ar = str(lang).startswith("ar")

    status_text = feasibility_label_by_lang(result, lang)

    recs_text = get_recs_by_lang(result, lang)
    recs_status = get_status_by_lang(result, lang)

    other_lang = "en" if is_ar else "ar"
    other_text = get_recs_by_lang(result, other_lang)
    other_status = get_status_by_lang(result, other_lang)

    return render(
        request,
        "analysis/result.html",
        {
            "result": result,
            "feasibility_percent": feasibility_percent,
            "status_text": status_text,
            "recs_text": recs_text,
            "recs_status": recs_status,
            "has_other_ready": bool(other_text and other_status == "ready"),
        },
    )


@login_required
def generate_recs(request, result_id):
    from ai.services.analyzer import analyze_project

    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)

    if request.method != "POST":
        return JsonResponse({"ok": False, "status": "method_not_allowed"}, status=405)

    lang = current_lang(request)

    project = get_object_or_404(Projects, id=result_obj.project_id)
    project_data = build_project_data(project)

    try:
        out = analyze_project(project_data, include_recommendations=True, lang=lang)
        raw_text = (out.get("recommendations") or "").strip()

        recs_text = normalize_recommendations_text(result_obj, lang, raw_text)
        set_recs_by_lang(result_obj, lang, recs_text, "ready")

    except Exception as e:
        set_recs_by_lang(result_obj, lang, f"Failed to generate recommendations: {e}", "failed")

    result_obj.save(
        update_fields=[
            "recommendations_ar",
            "recommendations_en",
            "recommendations_status_ar",
            "recommendations_status_en",
        ]
    )

    return JsonResponse({"ok": True, "status": get_status_by_lang(result_obj, lang)})


@login_required
def translate_recs(request, result_id):
    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)

    if request.method != "POST":
        return JsonResponse({"ok": False, "status": "method_not_allowed"}, status=405)

    lang = current_lang(request)
    is_ar = str(lang).startswith("ar")

    current_text = get_recs_by_lang(result_obj, lang)
    current_status = get_status_by_lang(result_obj, lang)
    if current_text and current_status == "ready":
        return JsonResponse({"ok": True, "status": "ready", "text": current_text})

    other_lang = "en" if is_ar else "ar"
    other_text = get_recs_by_lang(result_obj, other_lang)
    other_status = get_status_by_lang(result_obj, other_lang)

    if not other_text or other_status != "ready":
        return JsonResponse({"ok": False, "status": "no_source_text"}, status=400)

    try:
        set_recs_by_lang(result_obj, lang, "", "translating")
        result_obj.save(update_fields=["recommendations_status_ar", "recommendations_status_en"])

        from ai.services.translator import translate_text
        translated = translate_text(other_text, target_lang=("ar" if is_ar else "en"))

        translated = normalize_recommendations_text(result_obj, lang, translated)

        set_recs_by_lang(result_obj, lang, translated, "ready")
        result_obj.save(
            update_fields=[
                "recommendations_ar",
                "recommendations_en",
                "recommendations_status_ar",
                "recommendations_status_en",
            ]
        )

        return JsonResponse({"ok": True, "status": "ready", "text": translated})

    except Exception as e:
        set_recs_by_lang(result_obj, lang, f"Translation failed: {e}", "failed")
        result_obj.save(
            update_fields=[
                "recommendations_ar",
                "recommendations_en",
                "recommendations_status_ar",
                "recommendations_status_en",
            ]
        )
        return JsonResponse({"ok": False, "status": "failed"}, status=500)


@login_required
def recs_status(request, result_id):
    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    lang = current_lang(request)
    return JsonResponse({"status": get_status_by_lang(result_obj, lang)})


@login_required
def recs_loading(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    lang = current_lang(request)
    status = get_status_by_lang(result, lang)

    return render(
        request,
        "analysis/recs_loading.html",
        {"result": result, "feasibility_percent": feasibility_percent, "recs_status": status},
    )


@login_required
def analysis_pdf(request, result_id):
    ensure_arabic_font()

    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    lang = current_lang(request)
    is_ar_ui = str(lang).startswith("ar")

    status_text = feasibility_label_by_lang(result, lang)

    recs = get_recs_by_lang(result, lang) or _("No recommendations generated yet.")
    recs_is_ar = has_arabic(recs)

    safe_name = (result.project_name or "Project").replace(" ", "_")
    filename = f"JadwaAI_Analysis_Result_{safe_name}_{result_id}.pdf"

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(f"Jadwa AI | Analysis Result | {result.project_name}")

    page_w, page_h = A4
    margin = 2.2 * cm
    left = margin
    right = page_w - margin

    TEXT = colors.HexColor("#111827")
    MUTED = colors.HexColor("#6B7280")
    BORDER = colors.HexColor("#E5E7EB")
    PRIMARY = colors.HexColor("#2563EB")
    SUCCESS = colors.HexColor("#16A34A")
    DANGER = colors.HexColor("#DC2626")
    LIGHT = colors.HexColor("#98A2B3")

    is_feasible = is_feasible_result(result)
    STATUS_COLOR = SUCCESS if is_feasible else DANGER

    AR_FONT = "ArabicFont"
    EN_FONT = "Helvetica"

    def static_path(rel_path: str) -> str:
        pth2 = os.path.join(settings.BASE_DIR, "static", rel_path)
        if os.path.exists(pth2):
            return pth2
        pth = finders.find(rel_path)
        return pth or pth2

    logo_path = static_path("img/jadwa-logo.png")
    bg_path = static_path("img/hero-bg.png")

    def pick_font(s: str = "") -> str:
        if has_arabic(s):
            return AR_FONT
        return AR_FONT if is_ar_ui else EN_FONT

    def display(s: str) -> str:
        s = (s or "").strip()
        return rtl(s) if has_arabic(s) else s

    def draw_bg_and_logo():
        p.setFillColor(colors.white)
        p.rect(0, 0, page_w, page_h, stroke=0, fill=1)

        if os.path.exists(bg_path):
            try:
                bg = ImageReader(bg_path)
                bw, bh = bg.getSize()
                target_w = page_w * 0.75
                scale = target_w / float(bw)
                target_h = bh * scale

                x = -1.2 * cm
                y = -2.6 * cm

                p.saveState()
                try:
                    p.setFillAlpha(0.20)
                    p.setStrokeAlpha(0.20)
                except Exception:
                    pass

                p.drawImage(bg, x, y, width=target_w, height=target_h, mask="auto")
                p.restoreState()
            except Exception:
                try:
                    p.restoreState()
                except Exception:
                    pass

        if os.path.exists(logo_path):
            try:
                logo = ImageReader(logo_path)
                lw, lh = logo.getSize()
                target_w = 1.6 * cm
                scale = target_w / float(lw)
                target_h = lh * scale

                x = left - 0.4 * cm
                y = page_h - margin - target_h - 0.2 * cm

                p.drawImage(logo, x, y, width=target_w, height=target_h, mask="auto")
            except Exception:
                pass

    def draw_footer():
        foot = display(_("Jadwa AI © 2026 | contact@jadwa-ai.com | Saudi Arabia"))
        p.setFillColor(LIGHT)
        p.setFont(pick_font(foot), 9)
        p.drawRightString(right, margin - 0.35 * cm, foot)

    def card(x, y_top, w, h, radius=12):
        p.setStrokeColor(BORDER)
        p.setLineWidth(1)
        p.roundRect(x, y_top - h, w, h, radius, stroke=1, fill=0)

    def draw_line(x_left, x_right, y, s, size=11, color=TEXT):
        out = display(s)
        p.setFillColor(color)
        p.setFont(pick_font(out), size)
        if has_arabic(out):
            p.drawRightString(x_right, y, out)
        else:
            p.drawString(x_left, y, out)

    draw_bg_and_logo()

    y = page_h - margin - 2.4 * cm

    title = display(_("Analysis Result"))
    p.setFillColor(TEXT)
    p.setFont(pick_font(title), 22)
    p.drawCentredString(page_w / 2, y, title)
    y -= 0.75 * cm

    sub = display(_("AI-powered feasibility insights for your project"))
    p.setFillColor(PRIMARY)
    p.setFont(pick_font(sub), 11)
    p.drawCentredString(page_w / 2, y, sub)
    y -= 1.2 * cm

    gap = 0.9 * cm
    col_w = (right - left - gap) / 2

    if is_ar_ui:
        proj_x = left + col_w + gap
        rec_x = left
    else:
        proj_x = left
        rec_x = left + col_w + gap

    cards_top_y = y

    proj_h = 4.2 * cm
    card(proj_x, cards_top_y, col_w, proj_h)

    draw_line(proj_x + 0.6 * cm, proj_x + col_w - 0.6 * cm, cards_top_y - 0.9 * cm, _("Project Overview"), size=12)
    draw_line(
        proj_x + 0.6 * cm,
        proj_x + col_w - 0.6 * cm,
        cards_top_y - 1.8 * cm,
        f"{_('Project')}: {result.project_name or ''}",
        size=10.5,
        color=MUTED,
    )
    draw_line(
        proj_x + 0.6 * cm,
        proj_x + col_w - 0.6 * cm,
        cards_top_y - 2.6 * cm,
        f"{_('Feasibility Probability')}: {feasibility_percent:.2f}%",
        size=10.5,
        color=PRIMARY,
    )

    # ✅ الإضافة الوحيدة: سطر الثريشولد في الـ PDF
    draw_line(
        proj_x + 0.6 * cm,
        proj_x + col_w - 0.6 * cm,
        cards_top_y - 3.2 * cm,
        f"{_('Decision Threshold')}: {result.threshold:.2f}",
        size=10.5,
        color=MUTED,
    )

    # (نزلنا سطر الحالة شوي عشان يركب كل شيء)
    draw_line(
        proj_x + 0.6 * cm,
        proj_x + col_w - 0.6 * cm,
        cards_top_y - 3.8 * cm,
        f"{_('Status')}: {status_text}",
        size=10.5,
        color=STATUS_COLOR,
    )

    rec_h = 15.0 * cm
    card(rec_x, cards_top_y, col_w, rec_h)
    draw_line(rec_x + 0.6 * cm, rec_x + col_w - 0.6 * cm, cards_top_y - 0.9 * cm, _("AI Recommendations"), size=12)

    inner_w = col_w - 1.2 * cm
    inner_left = rec_x + 0.6 * cm
    inner_right = rec_x + col_w - 0.6 * cm

    if recs_is_ar:
        all_lines = wrap_rtl_lines(p, recs, inner_w, AR_FONT, 10.5)
    else:
        all_lines = wrap_ltr_lines(p, recs, inner_w, EN_FONT, 10.5)

    yy = cards_top_y - 1.6 * cm
    line_gap = 0.52 * cm
    bottom_inside = (cards_top_y - rec_h) + 1.0 * cm

    idx = 0
    while idx < len(all_lines) and yy >= bottom_inside:
        ln = all_lines[idx]
        if ln == "":
            yy -= line_gap
            idx += 1
            continue
        p.setFillColor(TEXT)
        if recs_is_ar:
            p.setFont(AR_FONT, 10.5)
            p.drawRightString(inner_right, yy, ln)
        else:
            p.setFont(EN_FONT, 10.5)
            p.drawString(inner_left, yy, ln)
        yy -= line_gap
        idx += 1

    draw_footer()

    def new_page_recs():
        p.showPage()
        draw_bg_and_logo()

    while idx < len(all_lines):
        new_page_recs()

        y2 = page_h - margin - 2.4 * cm
        y2 -= 1.1 * cm

        full_w = right - left
        full_h = 20.0 * cm
        card(left, y2, full_w, full_h)

        inner_left2 = left + 0.8 * cm
        inner_right2 = right - 0.8 * cm

        label2 = display(_("AI Recommendations (continued)"))
        p.setFillColor(TEXT)
        p.setFont(pick_font(label2), 12)
        if is_ar_ui:
            p.drawRightString(inner_right2, y2 - 0.9 * cm, label2)
        else:
            p.drawString(inner_left2, y2 - 0.9 * cm, label2)

        yy2 = y2 - 1.6 * cm
        bottom_inside2 = (y2 - full_h) + 1.0 * cm
        line_gap2 = 0.55 * cm

        while idx < len(all_lines) and yy2 >= bottom_inside2:
            ln = all_lines[idx]
            if ln == "":
                yy2 -= line_gap2
                idx += 1
                continue
            p.setFillColor(TEXT)
            if recs_is_ar:
                p.setFont(AR_FONT, 10.8)
                p.drawRightString(inner_right2, yy2, ln)
            else:
                p.setFont(EN_FONT, 10.8)
                p.drawString(inner_left2, yy2, ln)
            yy2 -= line_gap2
            idx += 1

        draw_footer()

    p.save()
    return response

