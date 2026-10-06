"""Test neo, nối chồng, đường kính uốn — RULES_TCVN5574.md mục 6."""

import math

import pytest

from src.rule_engine import neo_noi


def test_eta1_eta2():
    assert neo_noi.tinh_eta1(co_go=True) == 2.5
    assert neo_noi.tinh_eta1(co_go=False) == 1.5
    assert neo_noi.tinh_eta2(25) == 1.0
    assert neo_noi.tinh_eta2(36) == 0.9


def test_L0_an():
    R_bond = neo_noi.tinh_R_bond(eta1=2.5, eta2=1.0, Rbt=1.05)
    assert R_bond == pytest.approx(2.625)
    us = neo_noi.chu_vi_thanh(18)
    assert us == pytest.approx(math.pi * 18)
    As1 = 254.5
    L0_an = neo_noi.tinh_L0_an(Rs=260, As_1_thanh=As1, R_bond=R_bond, us=us)
    assert L0_an > 0


def test_L_an_rang_buoc_toi_thieu():
    # As_cal == As_ef -> Lan = alpha*L0_an, nhưng không nhỏ hơn max(15d;200).
    L_an = neo_noi.tinh_L_an(L0_an=100.0, As_cal=1000.0, As_ef=1000.0, d=18, keo=True)
    assert L_an >= max(15 * 18, 200.0)


def test_L_lap_rang_buoc_toi_thieu():
    L_lap = neo_noi.tinh_L_lap(L0_an=100.0, As_cal=1000.0, As_ef=1000.0, d=18, keo=True)
    assert L_lap >= max(20 * 18, 250.0)


def test_duong_kinh_uon_toi_thieu():
    assert neo_noi.duong_kinh_uon_toi_thieu(d=16, co_go=True) == 80  # 5d, d<20
    assert neo_noi.duong_kinh_uon_toi_thieu(d=25, co_go=True) == 200  # 8d, d>=20
    assert neo_noi.duong_kinh_uon_toi_thieu(d=16, co_go=False) == 40  # 2,5d trơn
