import os
import pandas as pd
from django.conf import settings

DATASET_PATH = os.path.join(
    settings.BASE_DIR, "dataset", "jadwa_ai_final_dataset.csv"
)

df = pd.read_csv(r"C:\Users\رهف\Desktop\JadwaAI project\Jadwa-AI\JadwaAI\dataset\jadwa_ai_final_dataset.csv")

def get_similar_enterprises(project_type, region):
    df["type_project"]=0
    exact = df[
        (df["type_project"] == project_type) &
        (df["region_project"] == region)
    ]
    if not exact.empty:
        return int(exact.iloc[0]["عدد المنشآت"])

    same_type = df[df["type_project"] == project_type]
    if not same_type.empty:
        return int(same_type["عدد المنشآت"].mean())

    same_region = df[df["region_project"] == region]
    if not same_region.empty:
        return int(same_region["عدد المنشآت"].mean())

    return int(df["عدد المنشآت"].mean())
    # df.to_csv("jadwa_ai_final_dataset.csv", index=False)
