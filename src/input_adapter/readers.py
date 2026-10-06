"""
Đọc file Excel/CSV không schema cố định — TONGQUAN_AI_AGENT.md mục 5 bước 2.

Module này CHỈ đọc thô (sheet -> DataFrame) và lọc sơ bộ sheet có khả năng
chứa dữ liệu khung; việc ánh xạ cột nằm ở heuristics.py/llm_mapping.py, việc
chuẩn hoá thành model nằm ở adapter.py — tách rời để mỗi phần test độc lập.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def doc_excel(duong_dan: str | Path) -> dict[str, pd.DataFrame]:
    """Đọc TẤT CẢ sheet của file Excel thành dict {tên_sheet: DataFrame}."""
    return pd.read_excel(duong_dan, sheet_name=None, engine="openpyxl")


def doc_csv(duong_dan: str | Path) -> pd.DataFrame:
    """Đọc 1 file CSV — ETABS đôi khi xuất CSV thay vì Excel cho báo cáo đơn giản."""
    return pd.read_csv(duong_dan)


def tim_sheet_co_du_lieu_khung(sheets: dict[str, pd.DataFrame], so_cot_toi_thieu: int = 3) -> list[str]:
    """Lọc sơ bộ sheet có khả năng chứa dữ liệu khung (đủ số cột, có ít nhất
    1 dòng dữ liệu) — loại các sheet trang bìa/ghi chú/tổng hợp thường gặp
    trong báo cáo ETABS nhiều sheet (vd sheet "Notes", "Units", "Cover")."""
    return [ten for ten, df in sheets.items() if df.shape[1] >= so_cot_toi_thieu and df.shape[0] >= 1]
