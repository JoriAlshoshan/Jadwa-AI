import os
import pandas as pd
from django.conf import settings

DATASET_PATH = os.path.join(settings.BASE_DIR, "dataset", "jadwa_ai_final_dataset.csv")

# نقرأ الداتا مرة واحدة
df = pd.read_csv(DATASET_PATH)

SECTOR_COL = "sectors"
REGION_COL = "region_project"
COUNT_COL = "عدد المنشآت"


def _norm(x) -> str:
    return ("" if x is None else str(x)).strip().lower()


def get_similar_enterprises(sector: str, region_loc: str) -> int:
    """
    ترجع تقدير عدد المنشآت المشابهة من الداتا ست بناءً على:
    - sectors + region_project
    مع Fallbacks ذكية إذا القطاع غير مطابق للداتا.
    """

    # تأكد الأعمدة موجودة
    required = [SECTOR_COL, REGION_COL, COUNT_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}. Found: {df.columns.tolist()}")

    sector = _norm(sector)
    region_loc = _norm(region_loc)

    d = df.copy()
    d[SECTOR_COL] = d[SECTOR_COL].map(_norm)
    d[REGION_COL] = d[REGION_COL].map(_norm)

    # هل sector اللي جاي من النظام موجود أصلًا في الداتا؟
    sector_exists = sector and (sector in set(d[SECTOR_COL].unique()))

    # 1) نفس القطاع + نفس المنطقة (إذا القطاع فعلاً موجود بالداتا)
    if sector_exists:
        exact = d[(d[SECTOR_COL] == sector) & (d[REGION_COL] == region_loc)]
        if not exact.empty:
            return int(exact[COUNT_COL].mean())

        # 2) نفس القطاع فقط
        same_sector = d[d[SECTOR_COL] == sector]
        if not same_sector.empty:
            return int(same_sector[COUNT_COL].mean())

    # 3) نفس المنطقة فقط (هذا مهم لأنه غالبًا Project_type عندك مو مطابق لـ sectors)
    same_region = d[d[REGION_COL] == region_loc]
    if not same_region.empty:
        return int(same_region[COUNT_COL].mean())

    # 4) متوسط عام
    return int(d[COUNT_COL].mean())
