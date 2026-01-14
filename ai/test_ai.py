from ai.services.feasibility import predict_project
from ai.services.recommendations import build_prompt

project = {
    "type_project": "Service",
    "region_project": "Riyadh",
    "budget_project": 1200000,
    "project_duration_days": 180,
    "num_saudi_employees": 8,
    "num_enterprises": 85,
    "economic_indicator": 2   
}

ml_result = predict_project(project)
print("ML Result:", ml_result)

prompt = build_prompt(project, ml_result)
print("\n--- Prompt Ready ---\n")
print(prompt)
