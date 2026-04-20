import os
import joblib
import pandas as pd
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(AI_DIR, "models", "rf_pipeline.pkl")
FEATURES_PATH = os.path.join(AI_DIR, "models", "feature_columns.pkl")

# Load model & feature columns once
model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURES_PATH)


# def dynamic_threshold(budget):
#     if budget < 100000:
#         return 0.90   # Micro-scale (high risk)
#     elif budget < 500000:
#         return 0.85   # Small-scale (still risky)
#     else:
#         return 0.60   # Medium & Large-scale

def dynamic_threshold(budget):
    if budget < 100000:
        return 0.75   # Small projects
    elif budget < 500000:
        return 0.80   # Medium projects
    else:
        return 0.70   # Large projects


# def predict_project(project_dict):
#     # Convert input to DataFrame
#     x = pd.DataFrame([project_dict])

#     # Ensure all required columns exist
#     for col in feature_columns:
#         if col not in x.columns:
#             x[col] = np.nan

#     # Reorder columns
#     x = x[feature_columns]
#     x = x.fillna(0)
#     # Predict probability
#     probability = float(model.predict_proba(x)[0][1])

#     # Threshold
#     budget = float(project_dict.get("budget_project", 0))
#     threshold = dynamic_threshold(budget)

#     # Final label
#     label = int(probability >= threshold)

#     return {
#         "probability": probability,
#         "threshold": threshold,
#         "label": label
#     }

def predict_project(project_dict):
    x = pd.DataFrame([project_dict])

    for col in feature_columns:
        if col not in x.columns:
            x[col] = np.nan

    x = x[feature_columns]
    x = x.fillna(0)

    if "budget_project" in x.columns:
        x["budget_project"] = np.log1p(x["budget_project"])

    # Predict
    probability = float(model.predict_proba(x)[0][1])

    # Get budget
    budget = float(project_dict.get("budget_project", 0))

    # Adjust probability
    if budget < 100000:
        factor = 0.85 + (budget / 100000) * 0.10
        probability *= factor

    elif budget < 500000:
        factor = 0.90 + (budget / 500000) * 0.05
        probability *= factor

    else:
        probability += ((budget % 10000000) / 1000000000) * 0.3

    probability = min(max(probability, 0.0), 1.0)

    # Threshold
    threshold = dynamic_threshold(budget)

    # Decision
    label = int(probability >= threshold)

    return {
        "probability": probability,
        "threshold": threshold,
        "label": label
    }