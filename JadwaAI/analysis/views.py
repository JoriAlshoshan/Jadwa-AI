import os
import re

from django.conf import settings
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
from JADWA_AI.models import Projects


def rtl(txt: str) -> str:
    txt = (txt or "").strip()
    if not txt:
        return ""
    reshaped = arabic_reshaper.reshape(txt)
    return get_display(reshaped)


ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
_BIDI_CTRL_RE = re.compile(r"[\u200E\u200F\u202A-\u202E\u2066-\u2069\uFEFF]")


def strip_bidi_controls(text: str) -> str:
    return _BIDI_CTRL_RE.sub("", text or "")


def has_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text or ""))


def ensure_arabic_font():
    font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "tahoma.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError("Put tahoma.ttf inside static/fonts/")
    if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))


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
            text = text.replace("غير قابل للتنفيذ", "قابل للتنفيذ")
        else:
            text = text.replace("غير قابل للتنفيذ", "__TMP__")
            text = text.replace("قابل للتنفيذ", "غير قابل للتنفيذ")
            text = text.replace("__TMP__", "غير قابل للتنفيذ")
    else:
        final_word = "feasible" if ok else "not feasible"
        rule = f"Note: Final decision uses probability ({prob:.4f}) vs threshold ({thr:.2f}); therefore the project is {final_word}."

        if ok:
            text = re.sub(r"\bnot feasible\b", "feasible", text, flags=re.IGNORECASE)
        else:
            text = re.sub(r"\bis feasible\b", "is not feasible", text, flags=re.IGNORECASE)

    if not text:
        return rule

    if str(lang).startswith("ar"):
        if "القرار النهائي" not in text:
            text = f"{rule}\n\n{text}"
    else:
        if "final decision" not in text.lower():
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
    region = (getattr(project, "project_region", "") or "").strip()
    city = (getattr(project, "project_city", "") or "").strip()

    if region and city:
        location_for_ml = f"{region}, {city}"
    else:
        location_for_ml = region or city

    months = int(getattr(project, "project_duration", 0) or 0)

    # return {
    #     "type_project": getattr(project, "Project_type", "Service"),
    #     "region_project": location_for_ml,
    #     "budget_project": float(getattr(project, "project_budget", 0) or 0),
    #     "project_duration_days": months * 30,  # ✅ هنا التعديل
    #     "num_saudi_employees": int(getattr(project, "number_of_employees", 0) or 0),
    # }
    econ_map = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

    econ_value = getattr(project, "economic_indicator", 2)
    print("project_name:", project.project_name)
    print("type:", project.Project_type)
    print("region:", project.project_region)
    print("city:", project.project_city)
    print("budget:", project.project_budget)
    print("duration:", project.project_duration)
    print("employees:", project.number_of_employees)
    print("description:", project.description)
    return {
        "type_project": getattr(project, "Project_type", "Service"),
        "region_project": location_for_ml,
        "budget_project": float(getattr(project, "project_budget", 0) or 0),
        "project_duration_days": months * 30,
        "num_saudi_employees": int(getattr(project, "number_of_employees", 0) or 0),

        "description": (getattr(project, "description", "") or "").strip(),
        # "num_enterprises": int(getattr(project, "num_enterprises", 0) or 0),
        "num_of_similar_enterprises": int(getattr(project, "num_of_similar_enterprises", 0) or 0),
        # ✅ هنا الحل
        "economic_indicator": econ_map.get(econ_value, 2),
    }   

@login_required
def run_analysis(request, project_id):
    from ai.services.analyzer import analyze_project

    project = get_object_or_404(Projects, id=project_id)
    project.refresh_from_db()

    project_data = build_project_data(project)

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

    previous_result = (
        AnalysisResult.objects
        .filter(user=request.user, project_id=result.project_id, id__lt=result.id)
        .order_by("-id")
        .first()
    )

    previous_feasibility_percent = None
    improvement_value = None
    improvement_direction = None

    if previous_result:
        previous_feasibility_percent = round(previous_result.probability * 100, 2)
        improvement_value = round(feasibility_percent - previous_feasibility_percent, 2)

        if improvement_value > 0:
            improvement_direction = "up"
        elif improvement_value < 0:
            improvement_direction = "down"
        else:
            improvement_direction = "same"

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
            "previous_result": previous_result,
            "previous_feasibility_percent": previous_feasibility_percent,
            "improvement_value": improvement_value,
            "improvement_direction": improvement_direction,
        },
    )


@login_required
def generate_recs(request, result_id):
    print("🔥 دخلنا generate_recs")
    from ai.services.analyzer import analyze_project
    from django.utils.translation import get_language_from_request

    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)

    if request.method != "POST":
        return JsonResponse({"ok": False, "status": "method_not_allowed"}, status=405)

    req_lang = (request.POST.get("lang") or get_language_from_request(request) or current_lang(request) or "en").lower()
    lang = "ar" if req_lang.startswith("ar") else "en"

    if get_status_by_lang(result_obj, lang) == "ready" and get_recs_by_lang(result_obj, lang):
        return JsonResponse({"ok": True, "status": "ready"})

    project = get_object_or_404(Projects, id=result_obj.project_id)
    project_data = build_project_data(project)

    try:
        set_recs_by_lang(result_obj, lang, "", "generating")
        result_obj.save(update_fields=["recommendations_status_ar", "recommendations_status_en"])

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
    recs = strip_bidi_controls(recs)
    recs_is_ar = has_arabic(recs)

    previous_result = (
        AnalysisResult.objects
        .filter(user=request.user, project_id=result.project_id, id__lt=result.id)
        .order_by("-id")
        .first()
    )

    previous_feasibility_percent = None
    improvement_value = None
    improvement_direction = None

    if previous_result:
        previous_feasibility_percent = round(previous_result.probability * 100, 2)
        improvement_value = round(feasibility_percent - previous_feasibility_percent, 2)
        if improvement_value > 0:
            improvement_direction = "up"
        elif improvement_value < 0:
            improvement_direction = "down"
        else:
            improvement_direction = "same"

    safe_name = (result.project_name or "Project").replace(" ", "_")
    filename = f"JadwaAI_Analysis_Result_{safe_name}_{result_id}.pdf"

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(f"Jadwa AI | Analysis Result | {result.project_name}")

    page_w, page_h = A4
    margin = 1.8 * cm
    left = margin
    right = page_w - margin

    TEXT = colors.HexColor("#0F172A")
    MUTED = colors.HexColor("#667085")
    BORDER = colors.HexColor("#E6EBF2")
    PRIMARY = colors.HexColor("#183A9E")
    SUCCESS = colors.HexColor("#166534")
    SUCCESS_BG = colors.HexColor("#ECFDF3")
    DANGER = colors.HexColor("#B42318")
    DANGER_BG = colors.HexColor("#FEF3F2")
    LIGHT = colors.HexColor("#98A2B3")

    is_feasible = is_feasible_result(result)
    STATUS_COLOR = SUCCESS if is_feasible else DANGER
    STATUS_BG = SUCCESS_BG if is_feasible else DANGER_BG

    AR_FONT = "ArabicFont"
    EN_FONT = "Helvetica"
    EN_FONT_BOLD = "Helvetica-Bold"

    def static_path(rel_path: str) -> str:
        pth2 = os.path.join(settings.BASE_DIR, "static", rel_path)
        if os.path.exists(pth2):
            return pth2
        pth = finders.find(rel_path)
        return pth or pth2

    logo_path = static_path("img/jadwa-logo.png")
    bg_path = static_path("img/hero-bg.png")

    def pick_font(s: str = "", bold: bool = False) -> str:
        if has_arabic(s):
            return AR_FONT
        return EN_FONT_BOLD if bold else EN_FONT

    def display(s: str) -> str:
        s = strip_bidi_controls((s or "").strip())
        return rtl(s) if has_arabic(s) else s

    def display_recommendation_line(s: str) -> str:
        s = strip_bidi_controls((s or "").strip())
        return rtl(s) if has_arabic(s) else s

    def text_width(txt: str, size: float, bold: bool = False) -> float:
        shown = display(txt)
        return p.stringWidth(shown, pick_font(shown, bold=bold), size)

    def draw_bg_and_logo():
        p.setFillColor(colors.white)
        p.rect(0, 0, page_w, page_h, stroke=0, fill=1)

        if os.path.exists(bg_path):
            try:
                bg = ImageReader(bg_path)
                bw, bh = bg.getSize()
                target_w = page_w * 0.34
                scale = target_w / float(bw)
                target_h = bh * scale
                x = -0.8 * cm
                y = -1.8 * cm
                p.saveState()
                try:
                    p.setFillAlpha(0.08)
                    p.setStrokeAlpha(0.08)
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
                target_w = 1.5 * cm
                scale = target_w / float(lw)
                target_h = lh * scale
                x = left
                y = page_h - margin - target_h + 0.15 * cm
                p.drawImage(logo, x, y, width=target_w, height=target_h, mask="auto")
            except Exception:
                pass

    def draw_footer():
        foot = display(_("Jadwa AI © 2026 | contact@jadwa-ai.com | Saudi Arabia"))
        p.setFillColor(LIGHT)
        p.setFont(pick_font(foot), 8)
        p.drawCentredString(page_w / 2, margin - 0.3 * cm, foot)

    def card(x, y_top, w, h, radius=16):
        p.setFillColor(colors.white)
        p.setStrokeColor(BORDER)
        p.setLineWidth(1)
        p.roundRect(x, y_top - h, w, h, radius, stroke=1, fill=1)

    def inner_box(x, y_top, w, h, radius=12):
        p.setFillColor(colors.white)
        p.setStrokeColor(BORDER)
        p.setLineWidth(1)
        p.roundRect(x, y_top - h, w, h, radius, stroke=1, fill=1)

    def line_text(x_left, x_right, y, txt, size=11, color=TEXT, bold=False):
        shown = display(txt)
        p.setFillColor(color)
        p.setFont(pick_font(shown, bold=bold), size)
        if has_arabic(shown):
            p.drawRightString(x_right, y, shown)
        else:
            p.drawString(x_left, y, shown)

    def badge(x, y, txt, bg_color, fg_color):
        shown = display(txt)
        size = 9.2
        pad_x = 9
        h = 18
        w = text_width(shown, size, bold=True) + pad_x * 2
        p.setFillColor(bg_color)
        p.setStrokeColor(bg_color)
        p.roundRect(x, y - h + 4, w, h, 10, stroke=1, fill=1)
        p.setFillColor(fg_color)
        p.setFont(pick_font(shown, bold=True), size)
        if has_arabic(shown):
            p.drawRightString(x + w - pad_x, y - 7, shown)
        else:
            p.drawString(x + pad_x, y - 7, shown)
        return w

    def wrap_lines(text, max_width, font_name, font_size):
        p.setFont(font_name, font_size)
        out = []

        for raw in (text or "").splitlines():
            raw = strip_bidi_controls(raw.strip())
            if not raw:
                out.append("")
                continue

            words = raw.split(" ")
            current = ""

            for w in words:
                test = (current + " " + w).strip()
                if p.stringWidth(test, font_name, font_size) <= max_width:
                    current = test
                else:
                    if current:
                        out.append(current)
                    current = w

            if current:
                out.append(current)

        return out

    draw_bg_and_logo()

    y = page_h - margin - 1.65 * cm

    title = display(_("Analysis Result"))
    p.setFillColor(TEXT)
    p.setFont(pick_font(title, bold=True), 20)
    p.drawCentredString(page_w / 2, y, title)
    y -= 0.55 * cm

    sub = display(_("AI-powered feasibility insights for your project"))
    p.setFillColor(MUTED)
    p.setFont(pick_font(sub), 10.5)
    p.drawCentredString(page_w / 2, y, sub)
    y -= 0.85 * cm

    gap = 0.55 * cm
    col_w = (right - left - gap) / 2
    cards_top_y = y

    if is_ar_ui:
        rec_x = left
        proj_x = left + col_w + gap
    else:
        proj_x = left
        rec_x = left + col_w + gap

    proj_h = 6.95 * cm
    rec_h = 6.95 * cm

    card(proj_x, cards_top_y, col_w, proj_h)
    card(rec_x, cards_top_y, col_w, rec_h)

    proj_pad = 0.5 * cm
    proj_left = proj_x + proj_pad
    proj_right = proj_x + col_w - proj_pad

    rec_pad = 0.5 * cm
    rec_left = rec_x + rec_pad
    rec_right = rec_x + col_w - rec_pad

    line_text(proj_left, proj_right, cards_top_y - 0.72 * cm, _("Project Overview"), size=12.5, color=TEXT, bold=True)
    line_text(proj_left, proj_right, cards_top_y - 1.35 * cm, f"{_('Project')}: {result.project_name or ''}", size=10.2, color=MUTED)
    line_text(proj_left, proj_right, cards_top_y - 2.05 * cm, f"{_('Feasibility Probability')}: {feasibility_percent:.2f}%", size=10.4, color=PRIMARY, bold=True)

    current_y = cards_top_y - 2.75 * cm

    if previous_result:
        box_h = 1.95 * cm
        inner_box(proj_left, current_y, col_w - 2 * proj_pad, box_h)

        line_text(
            proj_left + 0.28 * cm,
            proj_right - 0.28 * cm,
            current_y - 0.42 * cm,
            _("Previous Feasibility"),
            size=10,
            color=MUTED,
            bold=True,
        )

        prev_val = f"{previous_feasibility_percent:.2f}%"
        p.setFillColor(TEXT)
        p.setFont(EN_FONT_BOLD, 10)
        if is_ar_ui:
            p.drawString(proj_left + 0.28 * cm, current_y - 0.42 * cm, prev_val)
        else:
            p.drawRightString(proj_right - 0.28 * cm, current_y - 0.42 * cm, prev_val)

        p.setStrokeColor(BORDER)
        p.setLineWidth(1)
        p.line(
            proj_left + 0.22 * cm,
            current_y - 0.82 * cm,
            proj_right - 0.22 * cm,
            current_y - 0.82 * cm,
        )

        if improvement_direction == "up":
            diff_text = f"+{abs(improvement_value):.2f}% {_('Improvement from previous analysis')}"
            diff_color = SUCCESS
            diff_prefix = "▲ "
        elif improvement_direction == "down":
            diff_text = f"{abs(improvement_value):.2f}% {_('Change from previous analysis')}"
            diff_color = DANGER
            diff_prefix = "▼ "
        else:
            diff_text = "0.00%"
            diff_color = MUTED
            diff_prefix = "• "

        diff_w = (col_w - 2 * proj_pad) - 0.60 * cm
        diff_font = AR_FONT if has_arabic(diff_text) else EN_FONT_BOLD
        diff_lines = wrap_lines(diff_prefix + diff_text, diff_w, diff_font, 9.1)

        diff_y = current_y - 1.14 * cm
        for line in diff_lines[:2]:
            shown_line = display_recommendation_line(line)
            p.setFillColor(diff_color)

            if is_ar_ui and has_arabic(line):
                p.setFont(AR_FONT, 9.1)
                p.drawRightString(proj_right - 0.28 * cm, diff_y, shown_line)
            else:
                p.setFont(EN_FONT_BOLD, 9.1)
                p.drawString(proj_left + 0.28 * cm, diff_y, shown_line)

            diff_y -= 0.34 * cm

        current_y -= 2.35 * cm

    line_text(
        proj_left,
        proj_right,
        current_y - 0.08 * cm,
        f"{_('Decision Threshold')}: {result.threshold:.2f}",
        size=10.2,
        color=MUTED,
    )

    status_label = f"{_('')} "
    line_text(proj_left, proj_right, current_y - 0.82 * cm, status_label, size=10.4, color=TEXT, bold=True)

    if is_ar_ui:
        badge_x = proj_right - 1.8 * cm
    else:
        badge_x = proj_left + text_width(status_label, 10.4, bold=True) + 10

    badge(badge_x, current_y - 0.73 * cm, status_text, STATUS_BG, STATUS_COLOR)

    line_text(rec_left, rec_right, cards_top_y - 0.72 * cm, _("AI Recommendations"), size=12.5, color=TEXT, bold=True)

    text_box_top = cards_top_y - 1.08 * cm
    text_box_h = rec_h - 1.55 * cm
    inner_box(rec_left, text_box_top, col_w - 2 * rec_pad, text_box_h)

    text_w = (col_w - 2 * rec_pad) - 0.7 * cm
    text_left = rec_left + 0.35 * cm
    text_right = rec_right - 0.35 * cm

    first_page_font_size = 9.4
    first_page_line_gap = 0.38 * cm

    if recs_is_ar:
        all_lines = wrap_lines(recs, text_w, AR_FONT, first_page_font_size)
    else:
        all_lines = wrap_lines(recs, text_w, EN_FONT, first_page_font_size)

    yy = text_box_top - 0.46 * cm
    bottom_limit = (text_box_top - text_box_h) + 0.75 * cm

    idx = 0
    while idx < len(all_lines) and yy >= bottom_limit:
        ln = all_lines[idx]
        if ln == "":
            yy -= first_page_line_gap
            idx += 1
            continue

        shown_ln = display_recommendation_line(ln)
        p.setFillColor(TEXT)

        if recs_is_ar:
            p.setFont(AR_FONT, first_page_font_size)
            p.drawRightString(text_right, yy, shown_ln)
        else:
            p.setFont(EN_FONT, first_page_font_size)
            p.drawString(text_left, yy, shown_ln)

        yy -= first_page_line_gap
        idx += 1

    if idx < len(all_lines):
        more_text = display(_("Continued on next page..."))
        p.setFillColor(MUTED)
        p.setFont(pick_font(more_text, bold=True), 8.8)
        if is_ar_ui:
            p.drawRightString(text_right, (text_box_top - text_box_h) + 0.35 * cm, more_text)
        else:
            p.drawString(text_left, (text_box_top - text_box_h) + 0.35 * cm, more_text)

    draw_footer()

    while idx < len(all_lines):
        p.showPage()
        draw_bg_and_logo()

        y2 = page_h - margin - 1.4 * cm

        title2 = display(_("AI Recommendations"))
        p.setFillColor(TEXT)
        p.setFont(pick_font(title2, bold=True), 16)
        p.drawCentredString(page_w / 2, y2, title2)
        y2 -= 0.75 * cm

        card(left, y2, right - left, 23.0 * cm)

        inner_left2 = left + 0.55 * cm
        inner_right2 = right - 0.55 * cm

        label2 = display(_(""))
        line_text(inner_left2, inner_right2, y2 - 0.72 * cm, label2, size=11.5, color=TEXT, bold=True)

        box_top2 = y2 - 1.05 * cm
        box_h2 = 21.5 * cm
        inner_box(inner_left2, box_top2, (right - left) - 1.1 * cm, box_h2)

        text_left2 = inner_left2 + 0.35 * cm
        text_right2 = inner_right2 - 0.35 * cm
        yy2 = box_top2 - 0.5 * cm
        bottom_inside2 = (box_top2 - box_h2) + 0.5 * cm
        line_gap2 = 0.44 * cm
        page2_font_size = 10.0

        while idx < len(all_lines) and yy2 >= bottom_inside2:
            ln = all_lines[idx]
            if ln == "":
                yy2 -= line_gap2
                idx += 1
                continue

            shown_ln = display_recommendation_line(ln)
            p.setFillColor(TEXT)

            if recs_is_ar:
                p.setFont(AR_FONT, page2_font_size)
                p.drawRightString(text_right2, yy2, shown_ln)
            else:
                p.setFont(EN_FONT, page2_font_size)
                p.drawString(text_left2, yy2, shown_ln)

            yy2 -= line_gap2
            idx += 1

        draw_footer()

    p.save()
    return response