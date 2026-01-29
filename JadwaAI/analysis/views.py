from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import AnalysisResult


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

    return render(request, "analysis/recs_loading.html", {
        "result": result,
        "feasibility_percent": feasibility_percent,
    })


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

    return render(request, "analysis/result.html", {
        "result": result,
        "feasibility_percent": feasibility_percent,
    })
