from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .models import AnalysisResult


@login_required
def run_analysis(request, project_id):
    """
    Run feasibility analysis (FAST – without recommendations),
    save the result, then redirect to result page.
    """
    # Import here to avoid startup/import issues
    from ai.services.analyzer import analyze_project

    # Temporary project data (will be replaced in Part 2)
    project_data = {
        "type_project": "Service",
        "region_project": "Riyadh",
        "budget_project": 120000,
        "project_duration_days": 90,
        "num_saudi_employees": 3,
        "num_enterprises": 20,
        "economic_indicator": 2,
    }

    #  Fast analysis (NO recommendations)
    result = analyze_project(project_data, include_recommendations=False)

    # Save result to database
    saved_result = AnalysisResult.objects.create(
        user=request.user,
        project_id=project_id,
        project_name="Sample Project",
        probability=result["probability"],
        threshold=result["threshold"],
        label=result["label"],
        recommendations="",                 # empty for now
        recommendations_status="pending",   # pending
    )

    # Redirect to analysis result page
    return redirect("analysis_result", result_id=saved_result.id)


@login_required
def generate_recs(request, result_id):
    """
    Generate AI recommendations ON DEMAND (can be slow).
    """
    from ai.services.analyzer import analyze_project

    result_obj = get_object_or_404(
        AnalysisResult,
        id=result_id,
        user=request.user
    )

    # Temporary project data (will be replaced in Part 2)
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
        #  Generate recommendations only here
        out = analyze_project(project_data, include_recommendations=True)
        result_obj.recommendations = out["recommendations"]
        result_obj.recommendations_status = "ready"
    except Exception as e:
        result_obj.recommendations = f"Failed to generate recommendations: {e}"
        result_obj.recommendations_status = "failed"

    result_obj.save(update_fields=["recommendations", "recommendations_status"])
    return redirect("analysis_result", result_id=result_obj.id)


@login_required
def analysis_result(request, result_id):
    """
    Display a single analysis result.
    """
    result = get_object_or_404(
        AnalysisResult,
        id=result_id,
        user=request.user
    )

    return render(request, "analysis/result.html", {
        "result": result
    })
