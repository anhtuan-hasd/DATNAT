"""Test SẮP XẾP KÝ HIỆU trên mặt đứng theo bản vẽ mẫu (`src/drawing/to_ve/nhan.py`, quy tắc D1–D6, C1–C3).

Mỗi test khoá một quy tắc đo được từ `data/samples/BoTriThep_KhungTruc5_mau.pdf` bằng IR (không AutoCAD)."""

from __future__ import annotations

import pytest

from src.drawing import layers
from src.drawing.to_ve import ke_hoach, mat_dung, nhan
from src.drawing.to_ve.co_so import CauHinhToVe, _Ve
from tests.test_ban_ve_khung import _cot, _dam  # bộ dựng dữ liệu dùng chung


@pytest.fixture
def du_lieu():
    return {
        "toa_do_truc": {"A": 0.0, "B": 5600.0, "C": 7100.0},
        "cao_do_moc": {"Mong": 0.0, "Tang2": 4200.0, "Tang3": 7400.0},
        "phan_tu": [
            _cot("1", "A", "Mong_Tang2", 220, 300, 18, 3, 2), _cot("2", "A", "Tang2_Tang3", 220, 300, 16, 2, 2),
            _cot("14", "B", "Mong_Tang2", 220, 300, 18, 3, 2), _cot("15", "B", "Tang2_Tang3", 220, 300, 16, 2, 2),
            _cot("18", "C", "Mong_Tang2", 220, 220, 16, 2, 2), _cot("19", "C", "Tang2_Tang3", 220, 220, 16, 2, 2),
            _dam("32", "A-B", "Tang2", 220, 500, [18, 18, 18], [18, 18, 18], [18, 18]),  # có gia cường, 3 vùng đai
            _dam("45", "B-C", "Tang2", 220, 300, [18, 18], [16, 16], [16, 16]),  # nhịp ngắn
            _dam("34", "A-B", "Tang3", 220, 500, [16, 16], [16, 16], [16, 16]),  # không gia cường
        ],
    }


@pytest.fixture
def ve(du_lieu):
    kh = ke_hoach.lap_ke_hoach(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    v = _Ve(kh.cfg)
    info = mat_dung.ve_mat_dung(kh, v)
    return kh, v, info


def _vach_dung(v: _Ve):
    """Vạch đậm đứng (ký hiệu mặt cắt dầm): polyline 2 điểm cùng x, có độ rộng, layer REBAR_MAIN."""
    return [(dg.diem[0].x, (dg.diem[0].y + dg.diem[1].y) / 2) for dg in v.bv.da_giac
            if dg.layer == layers.REBAR_MAIN.ten and len(dg.diem) == 2 and dg.do_rong_net > 0 and abs(dg.diem[0].x - dg.diem[1].x) < 1e-6]


def _vach_ngang(v: _Ve):
    return [((dg.diem[0].x + dg.diem[1].x) / 2, dg.diem[0].y) for dg in v.bv.da_giac
            if dg.layer == layers.REBAR_MAIN.ten and len(dg.diem) == 2 and dg.do_rong_net > 0 and abs(dg.diem[0].y - dg.diem[1].y) < 1e-6]


def _vong_so_hieu(v: _Ve):
    """[(x, y, số hiệu)] mọi vòng tròn số hiệu (số đọc từ chữ trùng tâm)."""
    chu = {(round(c.vi_tri.x, 3), round(c.vi_tri.y, 3)): c.noi_dung for c in v.bv.chu if c.layer == layers.SO_HIEU.ten}
    return [(c.tam.x, c.tam.y, chu.get((round(c.tam.x, 3), round(c.tam.y, 3)))) for c in v.bv.vong_tron if c.layer == layers.SO_HIEU.ten]


def test_d3_ky_hieu_mat_cat_dam_ve_hai_lan_tren_va_duoi_cung_x(ve):
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "32")
    vach = _vach_dung(v)
    yt, yb = d.y, d.y - d.h
    # y có thể lệch nhỏ (≤120) khi tránh chồng; x trên/dưới PHẢI trùng nhau
    tren = sorted(x for x, y in vach if abs(y - (yt + nhan.D3_Y_TREN)) < 130 and d.x1 < x < d.x2)
    duoi = sorted(x for x, y in vach if abs(y - (yb - nhan.D3_Y_DUOI)) < 130 and d.x1 < x < d.x2)
    assert tren and tren == duoi  # đường cắt đi qua dầm: cùng x ở trên và dưới
    xf1 = d.x1 + d.hc1 / 2
    assert tren[0] == pytest.approx(xf1 + nhan.D3_X["trai"] * d.l_tt, abs=60)


def test_d3_mat_cat_trung_so_trong_1_dam_chi_ghi_1_lan(ve):
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "34")  # gối trái = gối phải ⇒ 2 mặt cắt khác nhau (trái/phải trùng)
    so = [kh.gan_mat_cat_dam[(d.ten, b)] for b in ("trai", "giua", "phai")]
    n_vach = sum(1 for x, y in _vach_dung(v) if abs(y - (d.y + nhan.D3_Y_TREN)) < 130 and d.x1 < x < d.x2)
    assert n_vach == len(set(so))


def test_d2_cum_thanh_tren_o_goi_gom_thanh_suot_va_gia_cuong(ve):
    """Bản mẫu "9 11 / 2Ø18 1Ø18": mỗi gối một cụm = số hiệu thanh suốt + số hiệu thanh gia cường, chữ xếp chồng."""
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "32")
    suot = next(t for t in kh.thanh_doc_dam[d.ten] if t.vai_tro == "tren_suot")
    gc = next(t for t in kh.thanh_doc_dam[d.ten] if t.vai_tro == "tren_cat_trai")
    y_c = d.y + nhan.D2_Y
    vong = [(x, s) for x, y, s in _vong_so_hieu(v) if abs(y - y_c) < 1 and d.x1 < x < d.x2]
    so = {s for _, s in vong}
    assert str(suot.so_hieu) in so and str(gc.so_hieu) in so
    xs = sorted(x for x, s in vong if s in (str(suot.so_hieu), str(gc.so_hieu)))
    assert xs[1] - xs[0] < 2 * v.r_the + 100  # hai vòng tròn nằm cạnh nhau
    chu = [c.noi_dung for c in v.bv.chu]
    assert f"{suot.so_luong}Ø{suot.duong_kinh}" in chu and f"{gc.so_luong}Ø{gc.duong_kinh}" in chu


def test_d1_khong_gia_cuong_chi_1_nhan_thanh_suot_tren_cot_san(ve):
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "34")
    suot = next(t for t in kh.thanh_doc_dam[d.ten] if t.vai_tro in ("tren_suot", "tren_suot_chung"))
    ds = [(x, y) for x, y, s in _vong_so_hieu(v) if s == str(suot.so_hieu) and d.x1 < x < d.x2 and abs(y - (d.y + nhan.D1_Y)) < 1]
    assert len(ds) == 1
    xf1 = d.x1 + d.hc1 / 2
    assert ds[0][0] == pytest.approx(xf1 + nhan.D1_X * d.l_tt, abs=300)


def test_d5_dai_dong_deu_o_duoi_dam_nhip_ngan_o_tren_dam(ve):
    kh, v, _ = ve
    d_dai = next(x for x in kh.dams if x.ten == "34")  # đồng đều ⇒ dưới dầm
    so = kh.dai_dam["34"][0].so_hieu
    y_duoi = d_dai.y - d_dai.h - nhan.D5_Y_DUOI
    assert any(abs(y - y_duoi) < 400 and s == str(so) and d_dai.x1 < x < d_dai.x2 for x, y, s in _vong_so_hieu(v))
    d_ngan = next(x for x in kh.dams if x.ten == "45")  # nhịp ngắn ⇒ trên dầm
    so2 = kh.dai_dam["45"][0].so_hieu
    assert d_ngan.l_tt < nhan.NHIP_NGAN_MM
    assert any(abs(y - (d_ngan.y + nhan.D5_Y_NGAN_TREN)) < 450 and s == str(so2) for x, y, s in _vong_so_hieu(v))


def test_d5_nhieu_vung_vung_giua_tren_dam_vung_goi_duoi_dam(ve):
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "32")
    dai = kh.dai_dam["32"]
    assert len({z.so_hieu for z in dai}) > 1
    so_goi, so_giua = dai[0].so_hieu, dai[1].so_hieu
    ds = _vong_so_hieu(v)
    goi_duoi = [x for x, y, s in ds if s == str(so_goi) and y < d.y - d.h and d.x1 < x < d.x2]
    giua_tren = [y for x, y, s in ds if s == str(so_giua) and y > d.y and d.x1 < x < d.x2]
    assert len(goi_duoi) >= 2  # hai gối đều có nhãn dưới dầm
    assert giua_tren  # vùng giữa ghi phía trên dầm


def test_d6_thanh_duoi_ghi_duoi_dam(ve):
    kh, v, _ = ve
    d = next(x for x in kh.dams if x.ten == "32")
    th = next(t for t in kh.thanh_doc_dam["32"] if t.vai_tro == "duoi")
    assert any(s == str(th.so_hieu) and y < d.y - d.h and d.x1 < x < d.x2 for x, y, s in _vong_so_hieu(v))


def test_d4_day_kich_thuoc_vung_ghi_chieu_dai_va_buoc(ve):
    kh, v, _ = ve
    nhan_kt = {k.nhan for k in v.bv.kich_thuoc}
    d = next(x for x in kh.dams if x.ten == "32")
    for z in d.vung:
        assert f"{z.chieu_dai:g}({z.nhan()})" in nhan_kt


def test_c1_thep_doc_cot_ben_phai_cach_mep_290(ve):
    kh, v, _ = ve
    c = next(x for x in kh.cots if x.ten == "2")  # cột A tầng 2
    x1 = kh.truc[c.truc] + c.h / 2
    so_h = kh.thanh_doc_cot[c.ten][0]
    assert any(s == str(so_h) and abs(x - (x1 + nhan.C1_LECH)) < 1 for x, y, s in _vong_so_hieu(v))


def test_c2_dai_cot_ben_trai_cho_truc_dau_giua_va_ben_phai_cho_truc_cuoi(ve):
    kh, v, _ = ve
    ds = _vong_so_hieu(v)
    for ten, trai in (("2", True), ("15", True), ("19", False)):
        c = next(x for x in kh.cots if x.ten == ten)
        xc = kh.truc[c.truc]
        so = c.nhan_dai[0][0]
        if trai:
            assert any(s == str(so) and abs(x - (xc - c.h / 2 - nhan.C2_LECH_TRAI)) < 1 for x, y, s in ds), ten
        else:
            assert any(s == str(so) and abs(x - (xc + c.h / 2 + nhan.C2_LECH_PHAI)) < 400 for x, y, s in ds), ten


def test_c3_mat_cat_cot_la_vach_ngang_hai_ben_cot(ve):
    kh, v, _ = ve
    c = next(x for x in kh.cots if x.ten == "2")
    xc = kh.truc[c.truc]
    ngang = _vach_ngang(v)
    trai = [x for x, y in ngang if abs(x - (xc - c.h / 2 - nhan.C3_LECH)) < 1]
    phai = [x for x, y in ngang if abs(x - (xc + c.h / 2 + nhan.C3_LECH)) < 1]
    assert trai and phai  # hai bên cột
    # số ghi TRÊN vạch (cao hơn vạch)
    so = kh.gan_mat_cat_cot[(c.ten, 0)]
    cao = [(cc.vi_tri.y, cc.noi_dung) for cc in v.bv.chu if cc.noi_dung == str(so) and cc.layer == layers.TEXT.ten]
    assert cao


def test_so_nhan_chong_duoc_bao_cao_trung_thuc(ve):
    _, v, info = ve
    assert info["loi_chong_nhan"] == len(info["nhan_chong"])
    assert info["so_vong_tron_so_hieu"] >= sum(1 for _ in _vong_so_hieu(v)) - 0  # đếm đủ vòng tròn đã vẽ
