"""Test đọc Excel/CSV thô — src/input_adapter/readers.py, dùng fixture tự tạo
trong tests/fixtures/ (KHÔNG phải dữ liệu ETABS thật, chỉ để test dò schema)."""

from pathlib import Path

from src.input_adapter import readers

FIXTURES = Path(__file__).parent / "fixtures"


def test_doc_csv_don_gian():
    df = readers.doc_csv(FIXTURES / "dam_don_gian.csv")
    assert len(df) == 4
    assert "Phan_tu" in df.columns


def test_doc_excel_nhieu_sheet():
    sheets = readers.doc_excel(FIXTURES / "bao_cao_etabs_day_du.xlsx")
    assert set(sheets) == {"Cover", "Concrete Beam Envelope", "Concrete Column Envelope", "Materials"}


def test_tim_sheet_co_du_lieu_khung_loc_duoc_sheet_nhieu():
    sheets = readers.doc_excel(FIXTURES / "bao_cao_etabs_day_du.xlsx")
    hop_le = readers.tim_sheet_co_du_lieu_khung(sheets, so_cot_toi_thieu=5)
    assert "Concrete Beam Envelope" in hop_le
    assert "Concrete Column Envelope" in hop_le
    assert "Cover" not in hop_le  # chỉ 2 cột -> bị lọc
    assert "Materials" not in hop_le  # chỉ 3 cột -> bị lọc với ngưỡng 5
