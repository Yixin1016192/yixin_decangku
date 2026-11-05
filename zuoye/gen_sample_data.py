# -*- coding: utf-8 -*-
"""生成演示用示例数据集：电商销售数据（约 500 行）。"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 500

CATEGORIES = {
    "电子产品": (800, 6000),
    "家用电器": (500, 4000),
    "服饰鞋包": (80, 600),
    "食品生鲜": (30, 300),
    "美妆个护": (50, 400),
}
REGIONS = ["华东", "华南", "华北", "西南", "东北"]
# 月度季节因子：11月（大促）最高
MONTH_FACTOR = {1: 0.7, 2: 0.75, 3: 0.8, 4: 0.85, 5: 0.9, 6: 1.1,
                7: 1.0, 8: 1.0, 9: 0.95, 10: 1.05, 11: 1.6, 12: 1.2}
REGION_FACTOR = {"华东": 1.3, "华南": 1.1, "华北": 1.0, "西南": 0.8, "东北": 0.6}

rows = []
for i in range(N):
    month = int(rng.integers(1, 13))
    day = int(rng.integers(1, 29))
    date = f"2025-{month:02d}-{day:02d}"
    cat = str(rng.choice(list(CATEGORIES)))
    lo, hi = CATEGORIES[cat]
    region = str(rng.choice(REGIONS))
    price = round(float(rng.normal((lo + hi) / 2, (hi - lo) / 6)), 2)
    price = float(np.clip(price, lo * 0.5, hi * 1.3))
    qty = int(rng.integers(1, 8))
    amount = round(price * qty * MONTH_FACTOR[month] * REGION_FACTOR[region], 2)
    rating = float(np.clip(rng.normal(4.3, 0.7), 1, 5))
    repurchase = "是" if rng.random() < 0.42 else "否"
    rows.append([date, cat, region, round(price, 2), qty, amount,
                 round(rating, 1), repurchase])

df = pd.DataFrame(rows, columns=["订单日期", "商品类别", "地区", "单价(元)",
                                 "销量(件)", "销售额(元)", "客户评分", "是否复购"])

# 人为注入少量缺失值与异常值，用于演示缺失值/异常值检测功能
idx_rating = rng.choice(N, size=8, replace=False)
df.loc[idx_rating, "客户评分"] = np.nan
idx_region = rng.choice(N, size=5, replace=False)
df.loc[idx_region, "地区"] = np.nan
outlier_idx = rng.choice(N, size=6, replace=False)
df.loc[outlier_idx, "销售额(元)"] = df.loc[outlier_idx, "销售额(元)"] * rng.uniform(6, 10, 6)

out = Path(__file__).resolve().parent / "示例数据" / "电商销售数据.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False, encoding="utf-8-sig")
print("saved:", out, "rows:", len(df))
