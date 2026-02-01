# ai/services/recommendations.py
from pathlib import Path

PROMPT_AR = Path(__file__).resolve().parents[1] / "prompts" / "prompt_ar.md"
PROMPT_EN = Path(__file__).resolve().parents[1] / "prompts" / "prompt_en.md"

def build_prompt(project_dict: dict, ml_result: dict, lang: str = "en") -> str:
    template_path = PROMPT_AR if str(lang).startswith("ar") else PROMPT_EN
    template = template_path.read_text(encoding="utf-8")

    duration_value = project_dict.get("duration_project", project_dict.get("project_duration_days", 0))
    econ_map = {1: "Low", 2: "Medium", 3: "High"}
    economic_indicator_text = econ_map.get(project_dict.get("economic_indicator"), "Medium")

    safe_data = {
        "type_project": project_dict.get("type_project", "Not specified"),
        "region_project": project_dict.get("region_project", "Not specified"),
        "budget_project": project_dict.get("budget_project", 0),
        "project_duration_days": duration_value,
        "num_saudi_employees": project_dict.get("num_saudi_employees", 0),
        "num_enterprises": project_dict.get("num_enterprises", 0),
        "economic_indicator": economic_indicator_text,
        "probability": ml_result.get("probability", 0),
        "threshold": ml_result.get("threshold", 0.6),
        "label": ml_result.get("label", 0),
    }

    return template.format(**safe_data)
