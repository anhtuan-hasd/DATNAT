"""
Neo, nối chồng, đường kính uốn cốt thép — RULES_TCVN5574.md mục 6
(TCVN 5574:2018 mục 10.3.5-10.3.7, công thức 255-259).
"""

from __future__ import annotations

import math

ETA1_THEP_GO = 2.5  # mục 6.1 — thép gờ, cán nóng.
ETA1_THEP_TRON = 1.5  # mục 6.1 — thép trơn.


def tinh_eta1(co_go: bool) -> float:
    """η1 theo loại thép — mục 6.1."""
    return ETA1_THEP_GO if co_go else ETA1_THEP_TRON


def tinh_eta2(duong_kinh_mm: float) -> float:
    """η2 theo đường kính — mục 6.1: 1,0 (d≤32mm); 0,9 (d≥36mm)."""
    return 1.0 if duong_kinh_mm <= 32 else 0.9


def tinh_R_bond(eta1: float, eta2: float, Rbt: float) -> float:
    """R_bond = η1·η2·Rbt (MPa) — mục 6.1."""
    return eta1 * eta2 * Rbt


def chu_vi_thanh(duong_kinh_mm: float) -> float:
    """us = π·d (mm) — chu vi tiết diện 1 thanh, dùng trong công thức neo."""
    return math.pi * duong_kinh_mm


def tinh_L0_an(Rs: float, As_1_thanh: float, R_bond: float, us: float) -> float:
    """L0,an = Rs·As/(R_bond·us) — chiều dài neo cơ sở (mm). Mục 6.1.

    As_1_thanh: diện tích 1 thanh (mm²); us: chu vi thanh đó (mm)."""
    return Rs * As_1_thanh / (R_bond * us)


def tinh_L_an(
    L0_an: float, As_cal: float, As_ef: float, d: float, keo: bool = True
) -> float:
    """Lan = α·L0,an·(As,cal/As,ef) — chiều dài neo tính toán (mm). Mục 6.2.

    α = 1,0 (kéo) hoặc 0,75 (nén). Ràng buộc: Lan ≥ max(15d; 200mm).
    As_cal: As yêu cầu theo tính toán; As_ef: As thực tế bố trí (As_cal/As_ef
    ≤ 1 khi As thực tế dư — không nhân hệ số > 1 nếu As_ef < As_cal, xem
    ghi chú tại nơi gọi để đảm bảo As_ef luôn ≥ As_cal trong thực tế thiết kế).
    """
    alpha = 1.0 if keo else 0.75
    L_an = alpha * L0_an * (As_cal / As_ef)
    return max(L_an, 15 * d, 200.0)


def tinh_L_lap(
    L0_an: float, As_cal: float, As_ef: float, d: float, keo: bool = True
) -> float:
    """Llap = α·L0,an·(As,cal/As,ef) — chiều dài nối chồng (mm). Mục 6.3.

    α = 1,2 (kéo) hoặc 0,9 (nén). Ràng buộc: Llap ≥ max(0,4αL0,an; 20d; 250mm).
    """
    alpha = 1.2 if keo else 0.9
    L_lap = alpha * L0_an * (As_cal / As_ef)
    return max(L_lap, 0.4 * alpha * L0_an, 20 * d, 250.0)


def khoang_cach_toi_thieu_2_moi_noi(d: float) -> float:
    """Khoảng cách giữa 2 mối nối cạnh nhau ≥ max(2d; 30mm). Mục 6.3."""
    return max(2 * d, 30.0)


def ty_le_thanh_noi_toi_da_phan_tram(co_moc: bool, co_chi_tiet_neo_bo_sung: bool = False) -> float:
    """Số thanh nối trong 1 tiết diện ≤ 50% (thép trơn có móc ≤25%); có thể
    tăng đến 100% nếu có chi tiết neo bổ sung. Mục 6.3."""
    if co_chi_tiet_neo_bo_sung:
        return 100.0
    return 25.0 if co_moc else 50.0


def duong_kinh_uon_toi_thieu(d: float, co_go: bool) -> float:
    """Đường kính uốn tối thiểu — mục 6.4.

    Trơn: 2,5d (d<20mm) / 4d (d≥20mm). Có gờ: 5d (d<20mm) / 8d (d≥20mm).
    """
    if co_go:
        return 5 * d if d < 20 else 8 * d
    return 2.5 * d if d < 20 else 4 * d
