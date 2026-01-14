# ai/services/recommendations.py
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "prompt_template.md"

def build_prompt(project_dict: dict, ml_result: dict) -> str:
    """
    Builds a feasibility recommendation prompt
    using project data and ML results.
    """

    # Read prompt template
    template = PROMPT_PATH.read_text(encoding="utf-8")

    # Handle project duration (support both names)
    duration_value = project_dict.get(
        "duration_project",
        project_dict.get("project_duration_days", 0)
    )

    # Normalize data (prevent KeyError)
    safe_data = {
        "type_project": project_dict.get("type_project", "غير محدد"),
        "region_project": project_dict.get("region_project", "غير محدد"),
        "budget_project": project_dict.get("budget_project", 0),

        "duration_project": duration_value,
        "project_duration_days": duration_value,

        "num_saudi_employees": project_dict.get("num_saudi_employees", 0),
        "num_enterprises": project_dict.get("num_enterprises", 0),
        "economic_indicator": project_dict.get("economic_indicator", "متوسط"),

        "probability": ml_result.get("probability", 0),
        "threshold": ml_result.get("threshold", 0.5),
        "label": ml_result.get("label", 0),
    }

    # Fill template safely
    return template.format(**safe_data)
