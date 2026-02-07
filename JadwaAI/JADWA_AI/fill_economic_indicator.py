import os
import pandas as pd
from django.conf import settings


def calculate_update_economic_indicator():
    # ✅ مسار ملف الداتا ست داخل المشروع
    csv_path = os.path.join(settings.BASE_DIR, 'dataset', 'jadwa_ai_final_dataset.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")

    # ✅ اقرأ من المسار الصحيح
    df = pd.read_csv(csv_path)

    # ✅ تأكد الأعمدة المطلوبة موجودة
    required_cols = ['region_project', 'عدد المنشآت', 'عدد العاملين السعوديين', 'project_success']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}. Found columns: {list(df.columns)}")

    # ✅ تنظيف + تحويل لأرقام (لو فيه نصوص/فراغات)
    df['region_project'] = df['region_project'].astype(str).str.strip()
    for col in ['عدد المنشآت', 'عدد العاملين السعوديين', 'project_success']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # ✅ عالج NaN (اختياري: نخليها 0)
    df[['عدد المنشآت', 'عدد العاملين السعوديين', 'project_success']] = df[
        ['عدد المنشآت', 'عدد العاملين السعوديين', 'project_success']
    ].fillna(0)

    # ✅ احسب المؤشرات normalized (مع حماية من القسمة على صفر)
    est_max = df['عدد المنشآت'].max() or 1
    emp_max = df['عدد العاملين السعوديين'].max() or 1
    suc_max = df['project_success'].max() or 1

    df['establishments_norm'] = df['عدد المنشآت'] / est_max
    df['number_of_saudi_employees_norm'] = df['عدد العاملين السعوديين'] / emp_max
    df['project_success_norm'] = df['project_success'] / suc_max

    df['economic_indicator'] = df[
        ['establishments_norm', 'number_of_saudi_employees_norm', 'project_success_norm']
    ].mean(axis=1)

    # ✅ متوسط المؤشر لكل منطقة
    region_avg = df.groupby('region_project', as_index=False)['economic_indicator'].mean()

    return region_avg
