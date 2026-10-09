"""Test bộ lắp ráp tờ vẽ bố trí thép `src/drawing/to_ve` — thuần IR/số liệu, KHÔNG cần AutoCAD/LLM.

Khoá các quy tắc rút từ bản vẽ mẫu `data/samples/BoTriThep_KhungTruc5_mau.pdf` (đã đối chiếu từng vùng):
- mặt trên mọi dầm bằng cốt sàn (dầm cao/thấp đều treo xuống) — lỗi cũ: dầm đối xứng qua cốt sàn;
- đai theo vùng (gối/giữa) lấy từ rule_engine.bo_tri_dai;
- số hiệu thanh dùng chung mặt đứng ↔ bảng thống kê ↔ mặt cắt;
- tờ vẽ có đủ thành phần (bảng 8 cột, ghi chú, khung tên, chi tiết nút) và các kỳ vọng kiểm chứng khớp nội dung đã vẽ.
"""

from __future__ import annotations

import re

import pytest

from src.drawing import layers
from src.drawing.to_ve import bang, bo_cuc, ke_hoach, mat_dung
from src.drawing.to_ve.co_so import CauHinhToVe, _Ve


def _vt(vi_tri, thanh, **kw):
    return {"vi_tri": vi_tri, "mo_ta_thep": "?", "As_yc": 100.0, "thanh": thanh, **kw}


def _cot(ten, truc, tang, b, h, d, n_b, n_h):
    n = 2 * (n_b + n_h) - 4
    thep = {"duong_kinh": d, "so_thanh_canh_b": n_b, "so_thanh_canh_h": n_h, "tong_so_thanh": n}
    return {"ten": ten, "loai": "cot", "b": b, "h": h, "truc": truc, "tang": tang, "mac_be_tong": "B25",
            "nhom_thep_doc": "CB500-V", "chieu_dai": 3200.0,
            "vi_tri": [_vt("dai_dien", [{"duong_kinh": d, "so_luong": n}], thep_doc=thep, neo_noi={"L_lap": 800.0})]}


def _dam(ten, truc, tang, b, h, top_l, top_r, bot):
    def th(ds):
        out: dict[int, int] = {}
        for d in ds:
            out[d] = out.get(d, 0) + 1
        return [{"duong_kinh": d, "so_luong": n} for d, n in sorted(out.items(), reverse=True)]

    return {"ten": ten, "loai": "dam", "b": b, "h": h, "truc": truc, "tang": tang, "mac_be_tong": "B25",
            "nhom_thep_doc": "CB500-V", "chieu_dai": 5000.0,
            "vi_tri": [_vt("goi_trai", th(top_l)), _vt("giua_nhip", th(bot)), _vt("goi_phai", th(top_r))]}


@pytest.fixture
def du_lieu():
    """2 nhịp (A–B 5000, B–C 1500), móng + 2 tầng; dầm A–B cao 500, dầm B–C cao 300 (khác chiều cao)."""
    return {
        "toa_do_truc": {"A": 0.0, "B": 5000.0, "C": 6500.0},
        "cao_do_moc": {"Mong": 0.0, "Tang2": 4200.0, "Tang3": 7400.0},
        "phan_tu": [
            _cot("1", "A", "Mong_Tang2", 220, 300, 18, 3, 2), _cot("2", "A", "Tang2_Tang3", 220, 300, 16, 2, 2),
            _cot("14", "B", "Mong_Tang2", 220, 300, 18, 3, 2), _cot("15", "B", "Tang2_Tang3", 220, 300, 16, 2, 2),
            _cot("18", "C", "Mong_Tang2", 220, 220, 16, 2, 2), _cot("19", "C", "Tang2_Tang3", 220, 220, 16, 2, 2),
            _dam("32", "A-B", "Tang2", 220, 500, [18, 18, 18], [18, 18, 18], [18, 18]),
            _dam("45", "B-C", "Tang2", 220, 300, [18, 18], [16, 16], [16, 16]),
            _dam("34", "A-B", "Tang3", 220, 500, [16, 16, 16], [18, 18], [16, 16]),
            _dam("43", "B-C", "Tang3", 220, 300, [16, 16], [16, 16], [16, 16]),
        ],
    }


@pytest.fixture
def kh(du_lieu):
    return ke_hoach.lap_ke_hoach(du_lieu, CauHinhToVe(ten_khung_truc="5"))


# ---------------------------------------------------------------- hình học mặt đứng


def _da_giac_dam(kh, v: _Ve):
    """Đa giác OUTLINE của từng dầm (nhận diện theo toạ độ x = mép cột..mép cột)."""
    kq = {}
    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        for dg in v.bv.da_giac:
            xs = [p.x for p in dg.diem]
            ys = [p.y for p in dg.diem]
            if dg.layer == layers.OUTLINE.ten and abs(min(xs) - xf1) < 1 and abs(max(xs) - xf2) < 1 and abs(max(ys) - d.y) < 1e-6 + d.h + 1:
                if abs((max(ys) - min(ys)) - d.h) < 1e-6:
                    kq[d.ten] = (min(ys), max(ys))
    return kq


def test_mat_tren_moi_dam_bang_cot_san_dam_treo_xuong(kh):
    """LỖI CŨ: dầm vẽ đối xứng qua cốt sàn (y ± h/2) ⇒ dầm 500 và 300 cùng tầng lệch mặt trên. Nay mặt trên = cốt sàn."""
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    hop = _da_giac_dam(kh, v)
    assert set(hop) == {d.ten for d in kh.dams}
    for d in kh.dams:
        y0, y1 = hop[d.ten]
        assert y1 == pytest.approx(d.y)  # mặt trên trùng cốt sàn tầng
        assert y0 == pytest.approx(d.y - d.h)  # treo xuống
    # hai dầm khác chiều cao cùng tầng: mặt trên bằng nhau, đáy khác nhau
    a, b = hop["32"], hop["45"]
    assert a[1] == pytest.approx(b[1]) and a[0] < b[0]


def test_thanh_tren_suot_cung_cao_do_tren_ca_chuoi_dam(kh):
    """Dầm 500 và 300 mặt trên bằng nhau ⇒ thanh trên suốt chạy THẲNG (1 đường ngang) qua cột giữa."""
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    d_c = 18
    y_suot = 4200 - kh.cfg.lop_bao_ve_dam - 6 - d_c / 2
    ngang = [dg for dg in v.bv.da_giac if dg.layer == layers.REBAR_MAIN.ten and len({round(p.y, 3) for p in dg.diem}) >= 1]
    # đường thép suốt: polyline có đoạn ngang dài suốt chuỗi A–C ở đúng y
    dai = [max(p.x for p in dg.diem) - min(p.x for p in dg.diem) for dg in ngang if any(abs(p.y - y_suot) < 1e-6 for p in dg.diem)]
    assert dai and max(dai) > 6500 - 300  # từ cột biên A tới cột biên C


def test_dai_dam_theo_vung_khop_mau(kh):
    d32 = next(d for d in kh.dams if d.ten == "32")
    # thông thuỷ 5000 − 300 = 4700 ⇒ vùng gối L/4 = 1175 → 1150 (làm tròn xuống bội 50), giữa 2400
    assert [round(z.chieu_dai) for z in d32.vung] == [1150, 2400, 1150]
    assert [z.buoc_mm for z in d32.vung] == [150, 250, 150]  # d_min = 18 ⇒ 15d = 270 → 250


def test_thong_thuy_dam_tru_nua_be_rong_cot(kh):
    d32 = next(d for d in kh.dams if d.ten == "32")
    assert d32.l_tt == pytest.approx(5000 - 150 - 150)  # cột 300 hai đầu


def test_so_hieu_chung_mat_dung_bang_thong_ke(kh):
    """Mọi số hiệu thanh ghi trên bản vẽ (mặt đứng, mặt cắt) đều có dòng trong bảng thống kê và ngược lại."""
    so_bang = {int(r["so"]) for r in bang.tong_hop_thanh(kh)}
    kq = bo_cuc.lap_ban_ve_khung({"toa_do_truc": kh.truc, "cao_do_moc": kh.moc, "phan_tu": [c.raw for c in kh.cots] + [d.raw for d in kh.dams]}, kh.cfg)
    so_tren_hinh = {int(c.noi_dung) for c in kq.ban_ve.chu if re.fullmatch(r"\d+", c.noi_dung) and c.layer == layers.SO_HIEU.ten}
    assert so_tren_hinh <= so_bang, f"số hiệu trên hình không có trong bảng: {so_tren_hinh - so_bang}"
    assert so_bang <= so_tren_hinh | {n for n in so_bang}  # bảng không có số hiệu "ma" ngoài kế hoạch


def test_bang_thong_ke_8_cot_dung_tieu_de_va_khoi_luong(kh):
    kq = bo_cuc.lap_ban_ve_khung({"toa_do_truc": kh.truc, "cao_do_moc": kh.moc, "phan_tu": [c.raw for c in kh.cots] + [d.raw for d in kh.dams]}, kh.cfg)
    chu = {c.noi_dung for c in kq.ban_ve.chu}
    for tde in ["CẤU KIỆN", "SỐ HIỆU", "HÌNH DÁNG", "Ø(mm)", "DÀI 1CK(mm)", "SL", "TỔNG DÀI(m)", "K.LƯỢNG(kG)"]:
        assert tde in chu
    tong = sum(dong.khoi_luong_kg for dong in kq.thong_ke)
    assert tong > 0
    # dòng bảng: khối lượng = dài × SL × kg/m
    for dong in kq.thong_ke:
        assert dong.tong_chieu_dai_m == pytest.approx(dong.chieu_dai_1_don_vi_mm * dong.so_luong / 1000)


def test_mat_cat_khu_trung_va_kich_thuoc_tren_ban_ve(kh, du_lieu):
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    K = kq.he_so_mat_cat
    assert len(kq.mat_cat) == len(kh.mat_cat) < 3 * len(kh.dams) + len(kh.cots)  # đã khử trùng
    for m in kq.mat_cat:
        if m["loai"] == "dam":
            assert m["cao_ve"] == pytest.approx(m["h"] * K)
            assert m["rong_ve"] == pytest.approx((m["b"] + 2 * CauHinhToVe().canh_ban_cua_t) * K)
        else:  # cột: rộng = h trong mặt phẳng khung, cao = b
            assert m["rong_ve"] == pytest.approx(m["h"] * K) and m["cao_ve"] == pytest.approx(m["b"] * K)
    # mỗi vị trí dầm đều trỏ tới 1 mặt cắt
    assert all((d.ten, ben) in kh.gan_mat_cat_dam for d in kh.dams for ben in ("trai", "giua", "phai"))


def test_ky_vong_kiem_chung_khop_noi_dung_da_ve(du_lieu):
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    so_sh = sum(1 for c in kq.ban_ve.vong_tron if c.layer == layers.SO_HIEU.ten)
    assert kq.so_ky_hieu_ky_vong == so_sh
    assert kq.so_da_giac_outline == sum(1 for g_ in kq.ban_ve.da_giac if g_.layer == layers.OUTLINE.ten)
    assert kq.so_cot == 6 and kq.so_dam == 4
    assert kq.kho_giay in ("A1", "A0")


def test_to_ve_nam_trong_khung_giay_va_co_chi_tiet_nut(du_lieu):
    cfg = CauHinhToVe(ten_khung_truc="5")
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, cfg)
    rong = {"A1": 841.0, "A0": 1189.0}[kq.kho_giay] * cfg.ty_le
    cao = {"A1": 594.0, "A0": 841.0}[kq.kho_giay] * cfg.ty_le
    xs = [p.x for g_ in kq.ban_ve.da_giac for p in g_.diem] + [d.p1.x for d in kq.ban_ve.doan_thang]
    ys = [p.y for g_ in kq.ban_ve.da_giac for p in g_.diem] + [d.p1.y for d in kq.ban_ve.doan_thang]
    assert min(xs) >= -1 and max(xs) <= rong + 1 and min(ys) >= -1 and max(ys) <= cao + 1
    chu = [c.noi_dung for c in kq.ban_ve.chu]
    assert any(s.startswith("CHI TIẾT") for s in chu)
    assert "GHI CHÚ:" in chu
    assert not [c for c in kq.canh_bao if "Không đủ chỗ" in c]


def test_cao_do_cos_theo_ton_nen(du_lieu):
    """COS ±0.000 = đỉnh móng + 1000: Tầng 2 (4200 so với đỉnh móng) ghi +3.200 như bản mẫu."""
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    chu = {c.noi_dung for c in kq.ban_ve.chu}
    assert "+3.200" in chu and "+6.400" in chu
    assert {"COS TÔN NỀN", "COS TỰ NHIÊN", "COS ĐỈNH MÓNG"} <= chu


def test_ghi_chu_noi_ro_gia_dinh_va_vat_lieu_tra_tu_bang(du_lieu):
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    chu = " ".join(c.noi_dung for c in kq.ban_ve.chu)
    assert "GIẢ ĐỊNH" in chu and "SƠ BỘ" in chu  # không giả vờ là kết quả tính toán
    assert "B25" in chu and "CB500-V" in chu


def test_du_lieu_thieu_truc_hoac_tang_khong_vo_kho(du_lieu):
    du_lieu["phan_tu"].append({"ten": "99", "loai": "dam", "b": 220, "h": 400, "truc": "A-Z", "tang": "TangX", "vi_tri": []})
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe())
    assert kq.so_dam == 4  # phần tử không đặt được lên lưới bị bỏ qua, không làm sập
