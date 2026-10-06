"""
Test verify.py — src/rule_engine/verify.py. Trước đây module này chỉ được
kiểm tra gián tiếp qua test_khung_truc3_kiem_chung.py (luôn dùng tổ hợp 1
loại đường kính) — không đủ để bắt lỗi đếm "số loại đường kính" (mục 4.2)
nhầm thành "số thanh". Lỗi này lộ ra qua chạy thật Phase 4 (Agent điều phối
với OpenAI): tổ hợp 1Ø16+4Ø18 (5 thanh, chỉ 2 loại) bị verify.py cũ báo sai
là "5 loại đường kính > 3" — Agent né tránh bằng cách chọn tổ hợp ít thanh
hơn (2Ø28) dù tổ hợp đầu vốn hợp lệ. Test dưới đây bám sát đúng tình huống
thật đã phát hiện lỗi.
"""

import pytest

from src.rule_engine import verify


def _dau_vao_dam_hop_le(**ghi_de) -> verify.DauVaoVerifyDam:
    mac_dinh = dict(
        As_yc=1212.0, As_thuc=1219.1, danh_sach_duong_kinh=[16, 18, 18, 18, 18],
        b=250.0, h0=650.0, do_manh_L0_h=10.0, so_lop=2, so_lop_toi_da_cho_phep=2,
        Q=180.2, Rb=17.0, Rbt=1.15, Rsw=170.0, Asw=100.6, sw=100.0,
    )
    mac_dinh.update(ghi_de)
    return verify.DauVaoVerifyDam(**mac_dinh)


def test_dem_dung_so_loai_duong_kinh_khong_phai_so_thanh():
    # 1Ø16+4Ø18 = 5 thanh nhưng chỉ 2 LOẠI đường kính — phải ĐẠT, không phải
    # bị báo "5 loại đường kính > 3" (lỗi thật đã phát hiện qua Phase 4).
    ket_qua = verify.kiem_tra_tong_hop_dam(_dau_vao_dam_hop_le())
    assert ket_qua.dat is True
    assert ket_qua.vi_pham == []


def test_bao_loi_khi_thuc_su_qua_3_loai_phan_biet():
    dau_vao = _dau_vao_dam_hop_le(danh_sach_duong_kinh=[12, 16, 20, 25], As_thuc=1300.0)
    ket_qua = verify.kiem_tra_tong_hop_dam(dau_vao)
    assert any("loại đường kính" in v for v in ket_qua.vi_pham)


def test_khong_bao_loi_trung_lap_khi_nhieu_thanh_cung_1_cap_lech_1mm():
    # 2 loại 17mm/18mm (chênh đúng 1mm) nhưng nhiều thanh mỗi loại — chỉ nên
    # báo lỗi 1 lần, không lặp lại theo từng cặp thanh trùng giá trị.
    dau_vao = _dau_vao_dam_hop_le(danh_sach_duong_kinh=[17, 17, 18, 18], As_thuc=900.0)
    ket_qua = verify.kiem_tra_tong_hop_dam(dau_vao)
    so_lan_bao_loi_chenh_1mm = sum("chênh đúng 1mm" in v for v in ket_qua.vi_pham)
    assert so_lan_bao_loi_chenh_1mm == 1


def test_as_thuc_khong_du_bi_bao_loi():
    dau_vao = _dau_vao_dam_hop_le(As_thuc=1000.0, danh_sach_duong_kinh=[16, 16])
    ket_qua = verify.kiem_tra_tong_hop_dam(dau_vao)
    assert ket_qua.dat is False
    assert any("As_thuc" in v for v in ket_qua.vi_pham)


def test_kiem_tra_tong_hop_cot_dat():
    dau_vao = verify.DauVaoVerifyCot(
        As_thuc=1361.9, b=250.0, h0=560.0, do_manh_L0_h=6.07,
        N=1514.38, e=550.0, Rb=17.0, Rsc=435.0, x=316.5, a_prime=40.0,
    )
    ket_qua = verify.kiem_tra_tong_hop_cot(dau_vao)
    assert ket_qua.dat is True
