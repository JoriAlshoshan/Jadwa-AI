from ai.services.feasibility import predict_project

project = {
    "type_project": "Service",
    "region_project": "Riyadh",
    "budget_project": 1200000,
    "project_duration_days": 180,
    "num_saudi_employees": 8,
    "num_enterprises": 85,
    "economic_indicator": 2   
}

result = predict_project(project)
print(result)
