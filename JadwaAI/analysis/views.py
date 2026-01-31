import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

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


# ===================== Arabic RTL helper =====================
def rtl(txt: str) -> str:
    txt = (txt or "").strip()
    if not txt:
        return ""
    reshaped = arabic_reshaper.reshape(txt)
    return get_display(reshaped)


# ===================== Font (Windows safe) =====================
def ensure_arabic_font():
    font_path = r"C:\Windows\Fonts\tahoma.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("tahoma.ttf not found in C:\\Windows\\Fonts")

    if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))


# ===================== Text wrapping for PDF (RTL) =====================
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


# ===================== Corporate meta row helper (NO STICKING) =====================
def draw_kv_row(
    p, *, right, y, label_ar, value, font,
    label_size=11, value_size=11,
    label_color=colors.HexColor("#5B6475"),
    value_color=colors.HexColor("#0B0F1A"),
    gap=0.35 * cm,
    value_max_w=7.2 * cm
):
    """
    Row: [Value .........]    [Label:]
    - label on the far right (RTL)
    - value on the left of it (LTR-safe)
    """
    # label
    p.setFillColor(label_color)
    p.setFont(font, label_size)
    label = rtl(label_ar) + rtl(":")
    label_w = p.stringWidth(label, font, label_size)
    p.drawRightString(right, y, label)

    # value (truncate if too long)
    p.setFillColor(value_color)
    p.setFont(font, value_size)
    v_full = str(value or "").strip()
    v = v_full

    while v and p.stringWidth(v, font, value_size) > value_max_w:
        v = v[:-1]
    if v_full != v:
        v = v.rstrip() + "…"

    value_x = right - label_w - gap
    p.drawRightString(value_x, y, v)


# ===================== Static path helpers =====================
def get_logo_path():
    candidates = []
    for d in getattr(settings, "STATICFILES_DIRS", []):
        candidates.append(os.path.join(d, "img", "jadwa-logo.png"))

    candidates.append(os.path.join(settings.BASE_DIR, "static", "img", "jadwa-logo.png"))
    candidates.append(os.path.join(settings.BASE_DIR, "analysis", "static", "img", "jadwa-logo.png"))
    candidates.append(os.path.join(settings.BASE_DIR, "JadwaAI", "static", "img", "jadwa-logo.png"))

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_pattern_path():
    """
    لازم يكون عندك ملف:
    static/img/pdf-pattern_light.png
    """
    candidates = []
    for d in getattr(settings, "STATICFILES_DIRS", []):
        candidates.append(os.path.join(d, "img", "pdf-pattern_light.png"))

    candidates.append(os.path.join(settings.BASE_DIR, "static", "img", "pdf-pattern_light.png"))
    candidates.append(os.path.join(settings.BASE_DIR, "analysis", "static", "img", "pdf-pattern_light.png"))
    candidates.append(os.path.join(settings.BASE_DIR, "JadwaAI", "static", "img", "pdf-pattern_light.png"))

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


# ===================== Background (WHITE + EXTRA LIGHT watermark) =====================
def draw_pdf_background(p: canvas.Canvas, page_w: float, page_h: float):
    """
    White background + very subtle corner watermark + logo.
    We also add a soft white overlay to force the watermark to be lighter.
    """
    # base white
    p.setFillColor(colors.white)
    p.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    # watermark in corner
    pattern_path = get_pattern_path()
    if pattern_path:
        try:
            pat_w = 11.0 * cm   # أصغر = أهدى
            pat_h = 11.0 * cm
            x = -2.4 * cm
            y = -3.0 * cm

            p.drawImage(
                ImageReader(pattern_path),
                x, y,
                width=pat_w,
                height=pat_h,
                preserveAspectRatio=True,
                mask="auto"
            )

            # ✅ طبقة بيضاء شفافة فوقها لتخفيفها أكثر (بدون تعديل الصورة)
            p.setFillColor(colors.Color(1, 1, 1, alpha=0.55))  # زيديها 0.65 لو تبين أخف
            p.rect(0, 0, page_w, page_h, stroke=0, fill=1)

        except Exception:
            pass

    # logo top-left
    logo_path = get_logo_path()
    if logo_path:
        try:
            logo_w = 3.6 * cm
            logo_h = 1.2 * cm
            p.drawImage(
                ImageReader(logo_path),
                2.0 * cm,
                page_h - 2.3 * cm,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                mask="auto"
            )
        except Exception:
            pass


# ===================== Existing views (unchanged) =====================
@login_required
def run_analysis(request, project_id):
    from ai.services.analyzer import analyze_project

    project_data = {
        "type_project": "Service",
        "region_project": "Riyadh",
        "budget_project": 120000,
        "project_duration_days": 90,
        "num_saudi_employees": 3,
        "num_enterprises": 20,
        "economic_indicator": 2,
    }

    out = analyze_project(project_data, include_recommendations=False)

    saved_result = AnalysisResult.objects.create(
        user=request.user,
        project_id=project_id,
        project_name="Sample Project",
        probability=out["probability"],
        threshold=out["threshold"],
        label=out["label"],
        recommendations="",
        recommendations_status="pending",
    )

    return redirect("analysis_result", result_id=saved_result.id)


@login_required
def recs_loading(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    return render(
        request,
        "analysis/recs_loading.html",
        {"result": result, "feasibility_percent": feasibility_percent},
    )


@login_required
def generate_recs(request, result_id):
    from ai.services.analyzer import analyze_project

    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)

    if request.method != "POST":
        return JsonResponse({"ok": False, "status": result_obj.recommendations_status}, status=405)

    project_data = {
        "type_project": "Service",
        "region_project": "Riyadh",
        "budget_project": 120000,
        "project_duration_days": 90,
        "num_saudi_employees": 3,
        "num_enterprises": 20,
        "economic_indicator": 2,
    }

    try:
        out = analyze_project(project_data, include_recommendations=True)
        result_obj.recommendations = out.get("recommendations", "")
        result_obj.recommendations_status = "ready"
    except Exception as e:
        result_obj.recommendations = f"Failed to generate recommendations: {e}"
        result_obj.recommendations_status = "failed"

    result_obj.save(update_fields=["recommendations", "recommendations_status"])
    return JsonResponse({"ok": True, "status": result_obj.recommendations_status})


@login_required
def recs_status(request, result_id):
    result_obj = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    return JsonResponse({"status": result_obj.recommendations_status})


@login_required
def analysis_result(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    return render(
        request,
        "analysis/result.html",
        {"result": result, "feasibility_percent": feasibility_percent},
    )


# ===================== PDF (WHITE + calm + corporate) =====================
@login_required
def analysis_pdf(request, result_id):
    ensure_arabic_font()

    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    safe_name = (result.project_name or "Project").replace(" ", "_")
    filename = f'JadwaAI_Feasibility_Report_{safe_name}_{result_id}.pdf'

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=A4)
    p.setTitle(f"Jadwa AI | Feasibility Report | {result.project_name}")

    page_w, page_h = A4

    margin = 2.2 * cm
    left = margin
    right = page_w - margin

    text = colors.HexColor("#0B0F1A")
    muted = colors.HexColor("#5B6475")
    light = colors.HexColor("#98A2B3")
    line_c = colors.HexColor("#E6E8EC")

    font = "ArabicFont"

    def draw_footer():
        p.setFillColor(light)
        p.setFont(font, 9)
        p.drawString(left, margin - 0.35 * cm, "Jadwa AI © 2026  |  contact@jadwa-ai.com  |  Saudi Arabia")

    def new_page(title_follow=False):
        p.showPage()
        ensure_arabic_font()
        draw_pdf_background(p, page_w, page_h)
        y0 = page_h - margin - 2.4 * cm

        if title_follow:
            p.setFillColor(text)
            p.setFont(font, 12)
            p.drawRightString(right, y0, rtl("توصيات الذكاء الاصطناعي (متابعة)"))
            y0 -= 0.7 * cm

            p.setStrokeColor(line_c)
            p.setLineWidth(1)
            p.line(left, y0, right, y0)
            y0 -= 0.9 * cm

        return y0

    # ===== Page 1 =====
    draw_pdf_background(p, page_w, page_h)
    y = page_h - margin - 2.4 * cm

    # Title (calm & luxury)
    p.setFillColor(text)
    p.setFont(font, 20)
    p.drawRightString(right, y, rtl("تقرير الجدوى"))
    y -= 0.75 * cm

    p.setFillColor(muted)
    p.setFont(font, 11)
    p.drawRightString(right, y, rtl("Feasibility Report • AI-powered insights"))
    y -= 1.05 * cm

    # Meta rows (aligned, not stuck)
    draw_kv_row(p, right=right, y=y, label_ar="اسم المشروع", value=result.project_name, font=font)
    y -= 0.70 * cm
    draw_kv_row(p, right=right, y=y, label_ar="نسبة الجدوى", value=f"{feasibility_percent:.2f}%", font=font)
    y -= 0.70 * cm
    draw_kv_row(p, right=right, y=y, label_ar="الحالة", value=str(result.label), font=font)
    y -= 0.85 * cm

    # Divider
    p.setStrokeColor(line_c)
    p.setLineWidth(1)
    p.line(left, y, right, y)
    y -= 1.0 * cm

    # Section title
    p.setFillColor(text)
    p.setFont(font, 13)
    p.drawRightString(right, y, rtl("توصيات الذكاء الاصطناعي"))
    y -= 0.85 * cm

    recs = (result.recommendations or "").strip()
    if not recs:
        p.setFillColor(muted)
        p.setFont(font, 11)
        p.drawRightString(right, y, rtl("لم يتم توليد توصيات بعد."))
        draw_footer()
        p.save()
        return response

    max_text_width = (right - left)
    lines = wrap_rtl_lines(p, recs, max_text_width, font, 11)

    p.setFillColor(text)
    p.setFont(font, 11)

    bottom_limit = margin + 2.0 * cm
    line_gap = 0.62 * cm

    for line in lines:
        if y < bottom_limit:
            draw_footer()
            y = new_page(title_follow=True)
            p.setFillColor(text)
            p.setFont(font, 11)

        if line == "":
            y -= line_gap
            continue

        p.drawRightString(right, y, line)
        y -= line_gap

    draw_footer()
    p.save()
    return response
