"""Test hình học chi tiết thép trên mặt đứng (`src/drawing/to_ve/chi_tiet_thep.py`): bán kính uốn, đường tim có cung, hai nét song
song, chân uốn ở nút. Thuần số học."""

from __future__ import annotations

import math

import pytest

from src.drawing.to_ve import chi_tiet_thep as ct


def test_ban_kinh_tim_theo_duong_kinh_uon_toi_thieu():
    assert ct.ban_kinh_tim(18) == pytest.approx(5 * 18 / 2 + 9)  # có gờ, d<20: đường kính trong 5d
    assert ct.ban_kinh_tim(22) == pytest.approx(8 * 22 / 2 + 11)  # d≥20: 8d


def test_chan_uon_nut_toi_thieu_va_vuot():
    assert ct.chieu_dai_neo_nut(None, 500.0) == (500.0, False)
    assert ct.chieu_dai_neo_nut(487.3, 500.0) == (500.0, False)  # thuyết minh KT5 nút 5: tính 487,3 ⇒ chọn 500
    assert ct.chieu_dai_neo_nut(645.93, 500.0) == (650.0, True)  # bội 50 ≥ L_an, vượt tối thiểu ⇒ có cờ cảnh báo
    assert ct.chieu_dai_neo_nut(720.0, 700.0) == (750.0, True)


def test_duong_tim_mot_goc_vuong_co_mot_cung_dung_tam_va_goc():
    pts = [(0.0, 0.0), (0.0, 1000.0), (500.0, 1000.0)]  # lên rồi rẽ phải (quay phải, ngược chiều lượng giác)
    r = ct.ban_kinh_tim(18)
    cung = [p for p in ct.duong_tim(pts, r) if p[0] == "cung"]
    assert len(cung) == 1
    _, tam, rr, a0, a1, trai = cung[0]
    assert (tam, rr, trai) == ((r, 1000.0 - r), r, False)
    assert (a0, a1) == (pytest.approx(180.0), pytest.approx(90.0))


def test_chieu_dai_duong_tim_co_cung_ngan_hon_duong_gap_goc():
    pts = [(0.0, 0.0), (0.0, 1000.0), (500.0, 1000.0)]
    r = ct.ban_kinh_tim(18)
    assert ct.chieu_dai_duong_uon(pts, r) == pytest.approx(1500.0 - (2 - math.pi / 2) * r)


def test_hai_net_song_song_cach_dung_duong_kinh_va_dong_hai_dau():
    pts = [(0.0, 0.0), (0.0, 1000.0), (500.0, 1000.0)]
    d = 18
    doan, cung = ct.net_song_song(pts, ct.ban_kinh_tim(d), d)
    assert len(cung) == 2 and len(doan) == 6  # 2 nét × 2 đoạn thẳng + 2 nắp đầu
    bk = sorted(c[2] for c in cung)
    assert bk[1] - bk[0] == pytest.approx(d)  # hai cung đồng tâm, bán kính lệch đúng Ø
    thang_dung = [x for x in doan if abs(x[0] - x[2]) < 1e-9 and abs(x[1] - x[3]) > 1.0]
    assert {round(x[0], 6) for x in thang_dung} >= {-9.0, 9.0}  # hai nét đứng cách tim ±Ø/2 (kèm nắp đầu cuối)


def test_thanh_thang_khong_co_cung_va_nap_hai_dau():
    doan, cung = ct.net_song_song([(0.0, 0.0), (1000.0, 0.0)], 54.0, 16)
    assert cung == [] and len(doan) == 4
    nap = [x for x in doan if abs(x[0] - x[2]) < 1e-9]
    assert len(nap) == 2 and all(abs(x[3] - x[1]) == pytest.approx(16.0) for x in nap)


def test_ban_kinh_bi_giam_khi_doan_ke_qua_ngan_nhung_khong_nho_hon_nua_duong_kinh():
    pts = [(0.0, 0.0), (0.0, 60.0), (500.0, 60.0)]  # đoạn đứng chỉ 60 mm < r = 54 + ...
    cung = [p for p in ct.duong_tim(pts, 200.0, ban_kinh_nho_nhat=9.45) if p[0] == "cung"]
    assert 9.45 <= cung[0][2] <= 60.0 + 1e-6
