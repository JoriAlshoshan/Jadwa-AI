from ai.services.feasibility import predict_project
from ai.services.recommendations import build_prompt
from ai.services.generative_ai import generate_recommendations


def analyze_project(project_dict: dict) -> dict:
    """
    Full AI pipeline:
    - ML prediction
    - Prompt building
    - Generative AI recommendations
    """

    ml_result = predict_project(project_dict)
    prompt = build_prompt(project_dict, ml_result)
    recommendations = generate_recommendations(prompt)

    return {
        "probability": ml_result["probability"],
        "threshold": ml_result["threshold"],
        "label": ml_result["label"],
        "recommendations": recommendations
    }
