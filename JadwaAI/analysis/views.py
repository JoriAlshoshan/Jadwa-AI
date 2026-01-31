import os
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from .models import AnalysisResult


# ---------- Arabic RTL helper ----------
def rtl(txt: str) -> str:
    txt = (txt or "").strip()
    if not txt:
        return ""
    reshaped = arabic_reshaper.reshape(txt)
    return get_display(reshaped)


# ---------- Font (Windows safe) ----------
def ensure_arabic_font():
    """
    Uses Windows Tahoma font (safe TTF) instead of Cairo file.
    This avoids missing/invalid Cairo-Regular.ttf issues.
    """
    font_path = r"C:\Windows\Fonts\tahoma.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("tahoma.ttf not found in C:\\Windows\\Fonts")

    if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))


# ---------- Text wrapping for PDF (RTL) ----------
def wrap_rtl_lines(p: canvas.Canvas, text: str, max_width: float, font_name: str, font_size: int):
    """
    Splits text into lines that fit within max_width.
    Handles Arabic by applying rtl() to each line AFTER wrapping.
    """
    p.setFont(font_name, font_size)

    lines_out = []
    for raw in (text or "").splitlines():
        raw = raw.strip()
        if not raw:
            lines_out.append("")  # empty line
            continue

        words = raw.split(" ")
        current = ""

        for w in words:
            test = (current + " " + w).strip()
            # measure in LTR before rtl shaping (width approx ok for wrapping)
            if p.stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines_out.append(rtl(current))
                current = w

        if current:
            lines_out.append(rtl(current))

    return lines_out


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


@login_required
def analysis_pdf(request, result_id):
    # Register Arabic font safely
    ensure_arabic_font()

    result = get_object_or_404(AnalysisResult, id=result_id, user=request.user)
    feasibility_percent = round(result.probability * 100, 2)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="JadwaAI_Report_{result_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    page_w, page_h = A4

    margin = 2 * cm
    right = page_w - margin
    left = margin
    max_text_width = page_w - (2 * margin)

    # Header
    p.setFont("ArabicFont", 16)
    p.drawRightString(right, page_h - 2.2 * cm, rtl("Jadwa AI - تقرير التحليل"))

    p.setFont("ArabicFont", 12)
    p.drawRightString(right, page_h - 3.4 * cm, rtl(f"المشروع: {result.project_name}"))
    p.drawRightString(right, page_h - 4.1 * cm, rtl(f"نسبة الجدوى: {feasibility_percent:.2f}%"))
    p.drawRightString(right, page_h - 4.8 * cm, rtl(f"الحالة: {result.label}"))

    p.line(left, page_h - 5.4 * cm, right, page_h - 5.4 * cm)

    # Recommendations title
    y = page_h - 6.3 * cm
    p.setFont("ArabicFont", 13)
    p.drawRightString(right, y, rtl("توصيات الذكاء الاصطناعي"))
    y -= 0.9 * cm

    # Body
    font_name = "ArabicFont"
    font_size = 11
    line_gap = 0.65 * cm
    bottom_limit = 2 * cm

    recs = (result.recommendations or "").strip()
    if not recs:
        p.setFont(font_name, font_size)
        p.drawRightString(right, y, rtl("لا توجد توصيات متاحة."))
    else:
        wrapped_lines = wrap_rtl_lines(p, recs, max_text_width, font_name, font_size)

        for line in wrapped_lines:
            if y < bottom_limit:
                p.showPage()
                y = page_h - 2.5 * cm
                p.setFont(font_name, font_size)

            if line == "":
                y -= line_gap  # empty line spacing
                continue

            p.drawRightString(right, y, line)
            y -= line_gap

    p.showPage()
    p.save()
    return response
