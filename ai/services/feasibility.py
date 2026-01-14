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

def dynamic_threshold(budget):
    if budget < 500000:
        return 0.5
    elif budget < 5000000:
        return 0.6
    else:
        return 0.7

def predict_project(project_dict):
    # Convert input to DataFrame
    x = pd.DataFrame([project_dict])

    # Ensure all required columns exist
    for col in feature_columns:
        if col not in x.columns:
            x[col] = np.nan

    # Reorder columns
    x = x[feature_columns]

    # Predict probability
    probability = float(model.predict_proba(x)[0][1])

    # Threshold
    budget = float(project_dict.get("budget_project", 0))
    threshold = dynamic_threshold(budget)

    # Final label
    label = int(probability >= threshold)

    return {
        "probability": probability,
        "threshold": threshold,
        "label": label
    }
