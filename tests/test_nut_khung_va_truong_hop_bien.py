"""Test bảng cấu tạo nút khung (mục 7) và 7 nguyên tắc xử lý biên (mục 10.6)."""

import pytest

from src.rule_engine import cot_dai, nut_khung, truong_hop_bien


def test_tra_yeu_cau_nut_hop_le():
    yc = nut_khung.tra_yeu_cau_nut("goc_mai_mo")
    assert "chữ U" in yc.yeu_cau


def test_tra_yeu_cau_nut_khong_hop_le():
    with pytest.raises(ValueError):
        nut_khung.tra_yeu_cau_nut("khong_ton_tai")


def test_nguyen_tac_1_gan_bang_nhau():
    # Gối trái/phải dầm 44-45 tầng 3: 1212 vs 1103 (mục 10.2) — chênh ~9%.
    assert truong_hop_bien.la_gan_bang_nhau(1212, 1103, ty_le_chenh_lech_toi_da=0.10)
    assert not truong_hop_bien.la_gan_bang_nhau(1212, 500, ty_le_chenh_lech_toi_da=0.10)
    assert truong_hop_bien.gia_tri_thiet_ke_chung(462, 435) == 462


def test_nguyen_tac_2_cau_kien_phu():
    qd = truong_hop_bien.xu_ly_cau_kien_phu(M_phu=28, M_chinh=462, ty_le_nho_hon_toi_thieu=0.2)
    assert qd.dung_thep_cau_kien_chinh


def test_nguyen_tac_3_chon_nhanh():
    assert truong_hop_bien.chon_nhanh_lech_tam(x_thu_lech_tam_lon=356, xiR=0.493, h0=560) == "be"
    assert truong_hop_bien.chon_nhanh_lech_tam(x_thu_lech_tam_lon=100, xiR=0.493, h0=560) == "lon"


def test_nguyen_tac_4_kiem_tra_toan_bo_to_hop():
    to_hop = [1, 2, 3, 4]
    ket_qua = truong_hop_bien.kiem_tra_toan_bo_to_hop_tai_trong(to_hop, lambda t: t < 4)
    assert ket_qua[-1].dat is False
    assert all(k.dat for k in ket_qua[:-1])


def test_nguyen_tac_7_buoc_dai_min_cua_3():
    s = truong_hop_bien.buoc_dai_thiet_ke_day_du(
        sw_max_theo_kha_nang_chiu_cat=400, s_tt=150.0, s_ct_cau_tao=280.0
    )
    assert s == 150.0
