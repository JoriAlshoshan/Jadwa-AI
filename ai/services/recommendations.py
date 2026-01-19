# ai/services/recommendations.py

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "prompt_template.md"


def build_prompt(project_dict: dict, ml_result: dict) -> str:
    """
    Builds a feasibility recommendation prompt
    using project data and ML results.
    """

    template = PROMPT_PATH.read_text(encoding="utf-8")

    duration_value = project_dict.get(
        "duration_project",
        project_dict.get("project_duration_days", 0)
    )

    econ_map = {1: "Low", 2: "Medium", 3: "High"}
    economic_indicator_text = econ_map.get(
        project_dict.get("economic_indicator"),
        "Medium"
    )

    safe_data = {
        "type_project": project_dict.get("type_project", "غير محدد"),
        "region_project": project_dict.get("region_project", "غير محدد"),
        "budget_project": project_dict.get("budget_project", 0),

        "project_duration_days": duration_value,
        "duration_project": duration_value,

        "num_saudi_employees": project_dict.get("num_saudi_employees", 0),
        "num_enterprises": project_dict.get("num_enterprises", 0),
        "economic_indicator": economic_indicator_text,

        "probability": ml_result.get("probability", 0),
        "threshold": ml_result.get("threshold", 0.6),
        "label": ml_result.get("label", 0),
    }

    return template.format(**safe_data)


def generate_recommendations(project_dict: dict, ml_result: dict) -> str:
    """
    Calls OpenAI API and returns AI-generated recommendations.
    """
    prompt = build_prompt(project_dict, ml_result)

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text
