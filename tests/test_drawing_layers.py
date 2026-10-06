"""Test khai báo layer/nét — RULES_TCVN5574.md mục 10.7.2."""

import pytest

from src.drawing import layers


def test_moi_layer_co_ten_duy_nhat():
    ten = [lp.ten for lp in layers.TAT_CA_LAYER]
    assert len(ten) == len(set(ten))


def test_do_day_net_theo_thu_tu_dam_nhat():
    # SỬA theo KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md mục 1.2 (TCVN 4612-88, nguồn
    # RIÊNG cho bản vẽ bố trí cốt thép — override RULES_TCVN5574.md mục
    # 10.7.2 vốn ghi nhầm OUTLINE_CUT "rất đậm nhất"): bê tông (OUTLINE/
    # OUTLINE_CUT) phải MẢNH NHẤT, cốt thép dọc (REBAR_MAIN) ĐẬM NHẤT.
    assert layers.REBAR_MAIN.do_day_net_mm > layers.REBAR_STIRRUP.do_day_net_mm
    assert layers.REBAR_STIRRUP.do_day_net_mm > layers.OUTLINE.do_day_net_mm
    assert layers.OUTLINE.do_day_net_mm == layers.OUTLINE_CUT.do_day_net_mm == layers.DIM.do_day_net_mm


def test_net_dut_va_net_cham_gach_dung_kieu():
    assert layers.HIDDEN.kieu_net == "Dashed"
    assert layers.AXIS.kieu_net == "Center"


def test_tra_layer_hop_le_va_khong_hop_le():
    assert layers.tra_layer("OUTLINE_CUT") is layers.OUTLINE_CUT
    with pytest.raises(ValueError):
        layers.tra_layer("KHONG_TON_TAI")
