"""Cốt đai dầm theo Asw/s do ETABS thiết kế (VRebar): đọc từ báo cáo, đổi ra bước đai, khớp thuyết minh Khung Trục 5
(dầm 32, 45 tầng 2: Ø6a150; các dầm còn lại Ø6a200)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.input_adapter import etabs_reader
from src.rule_engine import bo_tri_dai

FILE = Path(__file__).resolve().parent.parent / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"


def test_buoc_dai_tu_asw_s_khop_thuyet_minh():
    assert bo_tri_dai.buoc_dai_tu_asw_s(6, 0.377) == 150.0  # ETABS làm tròn VRebar: không được cắt xuống 100
    assert bo_tri_dai.buoc_dai_tu_asw_s(6, 0.283) == 200.0
    assert bo_tri_dai.buoc_dai_tu_asw_s(8, 0.283) == 350.0  # 100,5 mm² / 0,283


def test_quyet_dinh_dai_dam_co_asw_s_khong_ap_buoc_goi_h_chia_3_va_giua_toi_da_200():
    kq = bo_tri_dai.quyet_dinh_dai("dam", 500.0, 16, 16, asw_s=0.283)
    assert kq["nguon_buoc"] == "ETABS" and kq["buoc_goi"] == 200.0 and kq["buoc_giua"] == 200.0
    kq150 = bo_tri_dai.quyet_dinh_dai("dam", 500.0, 18, 18, asw_s=0.377)
    assert (kq150["buoc_goi"], kq150["buoc_giua"]) == (150.0, 200.0)  # tầng 2: gối 150, giữa 200


def test_khong_co_asw_s_giu_cau_tao_cu():
    kq = bo_tri_dai.quyet_dinh_dai("dam", 500.0, 16, 16)
    assert kq["nguon_buoc"] == "cau_tao" and kq["buoc_goi"] == 150.0


@pytest.mark.skipif(not FILE.exists(), reason="thiếu file ETABS mẫu")
def test_doc_etabs_lay_asw_s_tung_vi_tri_dam():
    bo, _, _ = etabs_reader.doc_etabs_thuc(FILE)
    asw = {p.ten: [v.noi_luc.Asw_s for v in p.du_lieu_vi_tri] for p in bo.phan_tu if p.loai.value == "dam"}
    assert asw["32"] == pytest.approx([0.377] * 3, rel=1e-3) and asw["45"] == pytest.approx([0.377] * 3, rel=1e-3)
    assert asw["38"] == pytest.approx([0.283] * 3, rel=1e-3)
