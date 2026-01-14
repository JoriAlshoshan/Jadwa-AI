import os
import joblib
import pandas as pd

# Set model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(BASE_DIR)
MODEL_PATH = os.path.join(AI_DIR, "models", "rf_pipeline.pkl")

# Load model once
model = joblib.load(MODEL_PATH)

def dynamic_threshold(budget):
    # Set threshold based on project budget
    if budget < 500000:
        return 0.5
    elif budget < 5000000:
        return 0.6
    else:
        return 0.7

def predict_project(project_dict):
    # Convert input to DataFrame
    x = pd.DataFrame([project_dict])

    # Predict feasibility probability
    probability = float(model.predict_proba(x)[0][1])

    # Calculate threshold using budget
    budget = float(project_dict.get("budget_project", 0))
    threshold = dynamic_threshold(budget)

    # Final feasibility label
    label = int(probability >= threshold)

    return {
        "probability": probability,
        "threshold": threshold,
        "label": label
    }
