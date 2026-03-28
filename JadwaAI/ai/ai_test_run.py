from ai.services.analyzer import analyze_project

projects = {
    "FAIL": {
        "type_project": "Service",
        "region_project": "Other",
        "budget_project": 80000,
        "project_duration_days": 45,
        "num_saudi_employees": 0,
        "num_enterprises": 5,
        "economic_indicator": 1
    },
    "BORDERLINE": {
        "type_project": "Service",
        "region_project": "Other",
        "budget_project": 250000,
        "project_duration_days": 120,
        "num_saudi_employees": 2,
        "num_enterprises": 25,
        "economic_indicator": 2
    },
    "SUCCESS": {
        "type_project": "Service",
        "region_project": "Riyadh",
        "budget_project": 1200000,
        "project_duration_days": 180,
        "num_saudi_employees": 8,
        "num_enterprises": 85,
        "economic_indicator": 3
    }
}

for name, project in projects.items():
    result = analyze_project(project)

    print("\n====================")
    print("CASE:", name)
    print("Probability:", result["probability"])
    print("Threshold:", result["threshold"])
    print("Label:", result["label"])

    with open(f"jadwa_output_{name.lower()}.txt", "w", encoding="utf-8") as f:
        f.write(result["recommendations"])

print("\nAll analyses completed and saved.")
