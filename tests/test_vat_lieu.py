"""Test bảng tra vật liệu — đối chiếu trực tiếp số liệu RULES_TCVN5574.md mục 1."""

import pytest

from src.rule_engine import vat_lieu


def test_be_tong_B25():
    bt = vat_lieu.lay_be_tong("B25")
    assert bt.Rb == 14.5
    assert bt.Rbt == 1.05
    assert bt.Eb == 30_000.0


def test_be_tong_B30():
    bt = vat_lieu.lay_be_tong("B30")
    assert bt.Rb == 17.0
    assert bt.Rbt == 1.15
    assert bt.Eb == 32_500.0


def test_thep_CB500_V():
    th = vat_lieu.lay_thep("CB500-V")
    assert th.Rs == 435.0
    assert th.Rsc == 435.0
    assert th.Rsw == 300.0


def test_thep_CB240_T():
    th = vat_lieu.lay_thep("CB240-T")
    assert th.Rs == 210.0
    assert th.Rsw == 170.0


def test_quy_doi_thep_nuoc_ngoai():
    # A-III (GOST) ~ CB400-V — Phụ lục C, mục 8.
    th = vat_lieu.lay_thep("A-III")
    assert th.Rs == 350.0


def test_dien_tich_1_thanh():
    assert vat_lieu.dien_tich_1_thanh(18) == 254.5
    assert vat_lieu.dien_tich_1_thanh(25) == 490.9


def test_dien_tich_nhieu_thanh_cot_22():
    # 2ϕ25 + 1ϕ22 = 1361,9 mm² — mục 10.4.
    As = vat_lieu.dien_tich_nhieu_thanh(25, 2) + vat_lieu.dien_tich_nhieu_thanh(22, 1)
    assert As == pytest.approx(1361.9, abs=0.1)


def test_duong_kinh_khong_hop_le():
    with pytest.raises(ValueError):
        vat_lieu.dien_tich_1_thanh(19)
