# ai/services/recommendations.py
from pathlib import Path

# Path to the prompt template file
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "prompt_template.md"

def build_prompt(project_dict: dict, ml_result: dict) -> str:
    """
    Returns a ready-to-use prompt by filling the template
    with project data and ML results.
    (Currently does NOT call the OpenAI API)
    """
    # Read prompt template
    template = PROMPT_PATH.read_text(encoding="utf-8")

    # Merge project data and ML result into one dictionary
    data = {**project_dict, **ml_result}

    # Fill the template with values
    return template.format(**data)
