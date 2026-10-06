"""Test thiết kế cốt đai theo lực cắt — RULES_TCVN5574.md mục 3 và mục 5."""

import pytest

from src.rule_engine import cot_dai


def test_kiem_tra_ep_vo_bung():
    # Rb=17MPa, b=250, h0=560 -> gioi_han = 0,3*17*250*560/1000 = 714kN.
    dat, gioi_han = cot_dai.kiem_tra_ep_vo_bung(Q=240.3, Rb=17, b=250, h0=560)
    assert gioi_han == pytest.approx(714.0, rel=0.001)
    assert dat


def test_qsw_va_Qsw1():
    qsw = cot_dai.tinh_qsw(Rsw=170, Asw=2 * 50.3, sw=150)  # 2 nhánh ϕ8, s=150mm
    assert qsw == pytest.approx(170 * 100.6 / 150, rel=1e-6)
    Qsw1 = cot_dai.tinh_Qsw1(qsw, h0=560)
    assert Qsw1 == pytest.approx(qsw * 560 / 1000, rel=1e-6)


def test_dieu_kien_dat_dai_theo_tinh_toan():
    # qsw đủ lớn thì thoả 0,25*Rbt*b.
    assert cot_dai.can_dat_dai_theo_tinh_toan(qsw=200, Rbt=1.15, b=250)
    assert not cot_dai.can_dat_dai_theo_tinh_toan(qsw=10, Rbt=1.15, b=250)


def test_phi_n_nen_3_nhanh():
    # sigma_m/Rb = 0,1 (<=0,25) -> phi_n=1+0,1=1,1
    phi_n = cot_dai.tinh_phi_n_nen(N=42.5, A=25000.0, Rb=17.0)  # sigma_m=1,7MPa -> ty_so=0,1
    assert phi_n == pytest.approx(1.1, rel=1e-3)

    phi_n_2 = cot_dai.tinh_phi_n_nen(N=212.5, A=25000.0, Rb=17.0)  # sigma_m=8,5 -> ty_so=0,5 -> 1,25
    assert phi_n_2 == pytest.approx(1.25, rel=1e-3)

    phi_n_3 = cot_dai.tinh_phi_n_nen(N=382.5, A=25000.0, Rb=17.0)  # sigma_m=15,3 -> ty_so=0,9 -> 5*(1-0,9)=0,5
    assert phi_n_3 == pytest.approx(0.5, rel=1e-3)


def test_bo_qua_xoan():
    assert cot_dai.duoc_phep_bo_qua_xoan(T=0.0, Rb=17, b=250, h=700)


def test_buoc_dai_max_dam():
    assert cot_dai.buoc_dai_max_dam(h0=560, can_tinh_toan=True) == pytest.approx(280.0)
    assert cot_dai.buoc_dai_max_dam(h0=560, can_tinh_toan=False) == pytest.approx(420.0)


def test_buoc_dai_max_cot():
    # cột 22: bước ngoài đoạn nối = min(15dmin;500) -> dmin=25mm (thanh nhỏ nhất
    # trong 2ϕ25+1ϕ22) => 15*22=330mm? Ví dụ sách dùng dmin của thanh NHỎ NHẤT
    # trong tổ hợp: 2ϕ25+1ϕ22 -> dmin=22mm; 15*22=330 nhưng sách chọn 350mm là
    # bước THIẾT KẾ làm tròn xuống bội số quy ước, không phải bước tối đa; ở
    # đây chỉ kiểm tra công thức bước tối đa theo đúng mục 5.3.
    assert cot_dai.buoc_dai_max_cot(d_doc_min=25, dieu_kien_dac_biet=False) == pytest.approx(375.0)
    assert cot_dai.buoc_dai_max_cot(d_doc_min=25, dieu_kien_dac_biet=True) == pytest.approx(250.0)


def test_duong_kinh_dai_toi_thieu():
    assert cot_dai.duong_kinh_dai_toi_thieu(d_doc_max=25) == pytest.approx(6.25)
    assert cot_dai.duong_kinh_dai_toi_thieu(d_doc_max=12) == pytest.approx(6.0)


def test_Ms_Msw_kiem_tra_tiet_dien_nghieng():
    Ms = cot_dai.tinh_Ms(Rs=435, As=1954, h0=643.53)
    assert Ms > 0
    Msw = cot_dai.tinh_Msw(Qsw=100.0, C=1000.0)
    assert Msw == pytest.approx(50.0)
    assert cot_dai.kiem_tra_tiet_dien_nghieng_mo_men(M=Ms + Msw - 1, Ms=Ms, Msw=Msw)
    assert not cot_dai.kiem_tra_tiet_dien_nghieng_mo_men(M=Ms + Msw + 1, Ms=Ms, Msw=Msw)
