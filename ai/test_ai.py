from ai.services.analyzer import analyze_project

project = {
    "type_project": "Service",
    "region_project": "Riyadh",
    "budget_project": 1200000,
    "project_duration_days": 180,
    "num_saudi_employees": 8,
    "num_enterprises": 85,
    "economic_indicator": 2
}

result = analyze_project(project)

with open("jadwa_output.txt", "w", encoding="utf-8") as f:
    f.write(result["recommendations"])

print("Analysis complete and saved.")
