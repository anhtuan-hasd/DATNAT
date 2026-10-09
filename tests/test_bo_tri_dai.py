"""Test src/rule_engine/bo_tri_dai.py — bố trí đai theo vùng (skill 06 B8/C4). Đối chiếu số với bản vẽ mẫu
`data/samples/BoTriThep_KhungTruc5_mau.pdf` (dầm 220×500, thông thuỷ 5220: 1300(Ø6a150) + 2620(Ø6a200) + 1300(Ø6a150))."""

from __future__ import annotations

from src.rule_engine import bo_tri_dai as bt


def test_dam_220x500_khop_ban_ve_mau():
    vung = bt.bo_tri_dai_dam(h=500, l_thong_thuy=5220, duong_kinh_doc_max=18, duong_kinh_doc_min=16)
    assert [(v.chieu_dai, v.buoc_mm, v.duong_kinh) for v in vung] == [(1300, 150, 6), (2620, 200, 6), (1300, 150, 6)]
    assert [v.nhan() for v in vung] == ["Ø6a150", "Ø6a200", "Ø6a150"]
    assert vung[0].tu_mm == 0 and vung[-1].den_mm == 5220  # phủ kín thông thuỷ, không hở/chồng


def test_buoc_goi_theo_chieu_cao_dam():
    assert bt.buoc_dai_goi_dam(300) == 150  # h ≤ 450: min(h/2; 300) = 150
    assert bt.buoc_dai_goi_dam(450) == 200
    assert bt.buoc_dai_goi_dam(500) == 150  # h > 450: min(h/3; 500) = 166 → 150
    assert bt.buoc_dai_goi_dam(900) == 300


def test_dam_ngan_chi_1_vung_buoc_goi():
    vung = bt.bo_tri_dai_dam(h=300, l_thong_thuy=1200, duong_kinh_doc_max=16, duong_kinh_doc_min=16)
    assert len(vung) == 1 and vung[0].chieu_dai == 1200 and vung[0].buoc_mm == 150


def test_buoc_tinh_toan_nho_hon_cau_tao_duoc_uu_tien():
    vung = bt.bo_tri_dai_dam(500, 5220, 18, 16, buoc_tinh_toan_goi=100)
    assert vung[0].buoc_mm == 100 and vung[1].buoc_mm >= 100


def test_duong_kinh_dai_toi_thieu():
    assert bt.chon_duong_kinh_dai(16) == 6
    assert bt.chon_duong_kinh_dai(25) == 8  # 25/4 = 6,25 > 6
    assert bt.chon_duong_kinh_dai(32) == 8
    assert bt.chon_duong_kinh_dai(40) == 10


def test_cot_220x300_hai_dau_10d_giua_15d():
    vung = bt.bo_tri_dai_cot(h_cot=300, h_thong_thuy=2700, duong_kinh_doc_max=18, duong_kinh_doc_min=16)
    assert vung[0].buoc_mm == 150 and vung[-1].buoc_mm == 150  # 10d = 160 → 150 (khớp mẫu a150)
    assert vung[0].chieu_dai == 450  # l_d = max(300; 2700/6 = 450; 450)
    assert vung[1].buoc_mm == 200  # 15d = 240 → 200 (mẫu ghi a250 — lệch có chủ đích, an toàn hơn)
    assert vung[0].tu_mm == 0 and vung[-1].den_mm == 2700


def test_cot_vung_noi_keo_dai_vung_chan():
    vung = bt.bo_tri_dai_cot(300, 2700, 18, 16, chieu_dai_noi=800)
    assert vung[0].chieu_dai == 800


def test_vi_tri_dai_dau_tien_cach_mep_50_va_so_luong():
    vung = bt.bo_tri_dai_dam(500, 5220, 18, 16)
    vt = bt.vi_tri_dai(vung)
    assert vt[0] == 50 and all(b - a > 0 for a, b in zip(vt, vt[1:]))
    assert len(vt) == sum(v.so_dai for v in vung)
    assert vt[-1] <= 5220
    assert vung[0].so_dai == (1300 - 50) // 150 + 1  # B8: n = ⌊(l−50)/s⌋+1


def test_vung_qua_ngan_khong_co_dai():
    assert bt.VungDai(0, 30, 150, 6).so_dai == 0
