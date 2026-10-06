"""Test src/orchestrator/agents/input_adapter_agent.py — chủ yếu
`doc_etabs_that` (tool MỚI, nối `etabs_reader.py` vào agent) vì đây là đường
đọc dữ liệu ĐẦU VÀO THẬT của đồ án (`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx`
— xem docs/TONGQUAN_AI_AGENT.md mục 8). Các tool còn lại (doc_va_do_schema/
de_xuat_anh_xa/chuan_hoa_du_lieu) là chuyển nguyên logic đã test kỹ ở
tests/test_input_adapter_end_to_end.py — không lặp lại ở đây."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.orchestrator.agents import input_adapter_agent as iaa

FILE_ETABS_THAT = Path(__file__).parent.parent / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"
pytestmark = pytest.mark.skipif(not FILE_ETABS_THAT.exists(), reason="Thiếu file mẫu ETABS thật")


def _nc() -> iaa.NguCanhInputAdapter:
    return iaa.NguCanhInputAdapter(hoi_nguoi_dung=lambda c, l: "đồng ý")


def test_doc_etabs_that_nhan_dien_dung_file_that():
    nc = _nc()
    kq = iaa.doc_etabs_that(nc, {"duong_dan": str(FILE_ETABS_THAT)})
    assert kq["la_etabs_that"] is True
    assert len(kq["phan_tu"]) == 20
    assert {"A", "B"}.issubset(kq["toa_do_truc"].keys())


def test_doc_etabs_that_ghi_vao_ngu_canh_hoan_tat_ngay_khong_can_suy_luan():
    nc = _nc()
    iaa.doc_etabs_that(nc, {"duong_dan": str(FILE_ETABS_THAT)})
    assert nc.hinh_hoc_hoan_tat is True
    assert nc.toa_do_truc and nc.cao_do_moc
    assert len(nc.phan_tu_da_chuan_hoa) == 20


def test_doc_etabs_that_tu_choi_file_khong_phai_etabs(thu_muc_tam: Path):
    import pandas as pd

    file_thuong = thu_muc_tam / "khong_phai_etabs.xlsx"
    pd.DataFrame({"A": [1, 2]}).to_excel(file_thuong, index=False)

    nc = _nc()
    kq = iaa.doc_etabs_that(nc, {"duong_dan": str(file_thuong)})
    assert kq["la_etabs_that"] is False
    assert nc.hinh_hoc_hoan_tat is False  # KHÔNG bị ghi nhầm khi không phải ETABS thật


def test_trich_bo_du_lieu_chuan_hoa_sau_doc_etabs_that():
    nc = _nc()
    iaa.doc_etabs_that(nc, {"duong_dan": str(FILE_ETABS_THAT)})
    bo = iaa.trich_bo_du_lieu_chuan_hoa(nc)
    assert bo is not None
    assert len(bo.phan_tu) == 20
    assert bo.toa_do_truc == nc.toa_do_truc
