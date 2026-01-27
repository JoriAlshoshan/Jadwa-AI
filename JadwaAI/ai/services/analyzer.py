from ai.services.feasibility import predict_project
from ai.services.recommendations import build_prompt
from ai.services.generative_ai import generate_recommendations


def analyze_project(project_dict: dict, include_recommendations: bool = True) -> dict:
    """
    AI pipeline:
    - ML prediction (always)
    - Optional: prompt building + generative AI recommendations
    - Converts numeric label (0/1) into readable text (Feasible / Not Feasible)
    """

    ml_result = predict_project(project_dict)

    # Convert label to user-friendly text
    raw_label = ml_result.get("label")
    label_text = "Feasible" if raw_label in (1, "1", True, "True") else "Not Feasible"

    output = {
        "probability": ml_result.get("probability", 0.0),
        "threshold": ml_result.get("threshold", 0.5),
        "label": label_text,
        "recommendations": "",
    }

    if include_recommendations:
        prompt = build_prompt(project_dict, ml_result)
        output["recommendations"] = generate_recommendations(prompt)

    return output
