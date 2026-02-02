import pandas as pd
import os
from django.conf import settings

def calculate_update_economic_indicator():
    csv_path = os.path.join(settings.BASE_DIR, 'dataset', 'jadwa_ai_final_dataset.csv')
    df = pd.read_csv(r"C:\Users\رهف\Desktop\JadwaAI project\Jadwa-AI\JadwaAI\dataset\jadwa_ai_final_dataset.csv")

    df['establishments_norm'] = df['عدد المنشآت'] / df['عدد المنشآت'].max()
    df['number_of_saudi_employees_norm'] = df['عدد العاملين السعوديين'] / df['عدد العاملين السعوديين'].max()
    df['project_success_norm'] = df['project_success'] / df['project_success'].max()

    df['economic_indicator'] = df[
        ['establishments_norm', 'number_of_saudi_employees_norm', 'project_success_norm']
    ].mean(axis=1)

    region_avg = df.groupby('region_project')['economic_indicator'].mean().reset_index()
    return region_avg