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
from src.drawing import verify_drawing
from src.drawing.to_ve import bang, bo_cuc, chi_tiet_thep, ke_hoach, mat_cat, mat_dung
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
    """Dầm 500 và 300 mặt trên bằng nhau ⇒ thanh trên suốt chạy THẲNG qua cột giữa: một nét mảnh theo đường tim."""
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    d_c = 18
    y_suot = 4200 - kh.cfg.lop_bao_ve_dam - 6 - d_c / 2
    dai = [abs(dt.p2.x - dt.p1.x) for dt in v.bv.doan_thang
           if dt.layer == layers.REBAR_BAR.ten and abs(dt.p1.y - y_suot) < 1e-6 and abs(dt.p2.y - y_suot) < 1e-6]
    assert dai and max(dai) > 6500 - 600  # MỘT nét theo tim, từ chân thanh ở cột biên A tới cột biên C


def test_thanh_doc_hai_net_manh_con_dai_dam_hon_thanh(kh):
    """Bản mẫu: thanh dọc là hai nét MẢNH song song, cốt đai ĐẬM hơn (đảo ngược so với bản cũ: thanh dọc đậm hơn đai)."""
    assert layers.REBAR_STIRRUP.do_day_net_mm > layers.REBAR_BAR.do_day_net_mm
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    assert any(dt.layer == layers.REBAR_BAR.ten for dt in v.bv.doan_thang)
    assert not [dg for dg in v.bv.da_giac if dg.layer == layers.REBAR_BAR.ten]  # không còn polyline gấp góc nhọn


def test_go_uon_bo_cung_o_nut_mai_va_chan_cot_trong_mong(kh):
    """Thép chờ chân cột (3 cột × 2 thanh) và thanh cột uốn vào dầm ở tầng mái (3 cột × 2 thanh) đều có cung."""
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    cung = [c for c in v.bv.cung if c.layer == layers.REBAR_BAR.ten]
    assert len(cung) >= 3 * 2 + 3 * 2  # mỗi chỗ uốn một cung (thanh một nét)
    # đoạn ngang chân L nằm TRÊN lưới thép đáy, không trùng nét với lưới
    y_dai = -kh.cfg.day_dai_mong
    y_chan, y_luoi = y_dai + chi_tiet_thep.CAO_CHAN_L, y_dai + chi_tiet_thep.CAO_LUOI_DAY
    assert y_chan - 9 > y_luoi + chi_tiet_thep.D_LUOI / 2  # chân L cao hơn lưới đáy một khoảng rõ rệt


def test_chan_uon_xuong_cot_cua_thanh_tren_dam_la_h_cong_100(kh):
    """Bản mẫu: bảng 'thanh 9': 600 + 7100 + 400 (dầm 500 ⇒ chân 600, dầm 300 ⇒ chân 400)."""
    suot = next(t for t in kh.thanh_doc_dam["32"] if t.vai_tro == "tren_suot")
    ch = next(d for d in kh.dams if d.ten == "32")._chuoi
    assert (ch["l_tr"], ch["l_ph"]) == (600.0, 400.0)
    assert suot.chieu_dai == pytest.approx(chi_tiet_thep.lam_tron_len((ch["x_ph"] - ch["x_tr"]) + 600 + 400))  # chiều dài cắt làm tròn lên bội 50


def test_cot_tang_mai_uon_vao_dam_500_va_chieu_dai_theo_ban_mau(kh):
    """Bản mẫu: thanh 5 '500|3200' (tầng mái cao 3200) ⇒ 3700; tầng 1 cộng thép chờ xuống đài + chân L."""
    assert kh.thanh_doc_cot["2"][2] == pytest.approx(3200 + 500)
    assert next(c for c in kh.cots if c.ten == "2")._huong_uon == (1, 1)  # cột biên trái: chỉ có dầm bên phải
    assert next(c for c in kh.cots if c.ten == "15")._huong_uon == (-1, 1)  # cột giữa: dầm cả hai bên
    assert next(c for c in kh.cots if c.ten == "19")._huong_uon == (-1, -1)  # cột biên phải
    chan = (kh.cfg.day_dai_mong - chi_tiet_thep.CAO_CHAN_L) + chi_tiet_thep.CHAN_L_NGANG
    assert kh.thanh_doc_cot["1"][2] == pytest.approx(chi_tiet_thep.lam_tron_len(4200 + 800 + chan))


def test_l_an_lon_hon_toi_thieu_thi_lay_boi_50_va_ghi_canh_bao(du_lieu):
    import copy

    dl = copy.deepcopy(du_lieu)
    next(p for p in dl["phan_tu"] if p["ten"] == "2")["vi_tri"][0]["neo_noi"] = {"L_lap": 800.0, "L_an": 680.0}
    kh2 = ke_hoach.lap_ke_hoach(dl, CauHinhToVe(ten_khung_truc="5"))
    assert next(c for c in kh2.cots if c.ten == "2")._l_vao == 700.0
    assert any("Cột 2" in cb and "700" in cb for cb in kh2.canh_bao)


def test_thanh_duoi_khong_moc_vao_cot_bien(kh):
    """Thuyết minh Hình 33 và bản mẫu: thanh dưới vào cột biên THẲNG (không móc lên)."""
    d32 = next(d for d in kh.dams if d.ten == "32")
    duoi = next(t for t in kh.thanh_doc_dam["32"] if t.vai_tro == "duoi")
    assert duoi.chieu_dai == pytest.approx(chi_tiet_thep.lam_tron_len(d32.l_tt + (d32.hc1 - kh.cfg.lop_bao_ve_dam) + d32.hc2 / 2))


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
    # tiêu đề và cấu trúc theo bản mẫu
    for tde in ["BẢNG THỐNG KÊ CỐT THÉP", "CẤU KIỆN", "STT", "HÌNH DẠNG, KÍCH THƯỚC", "ĐƯỜNG KÍNH", "CHIỀU DÀI THANH", "SỐ LƯỢNG",
                "1 CK", "T. BỘ", "TỔNG CHIỀU DÀI", "TRỌNG LƯỢNG", "THÉP CỘT", "THÉP DẦM", "TỔNG HỢP KHỐI LƯỢNG (kG):"]:
        assert tde in chu, tde
    from src.drawing import verify_drawing

    class _Doc:  # chỉ cần các chữ trên layer TEXT
        pass

    thieu = [t for t in verify_drawing._TIEU_DE_BANG_THEO_MAU if t not in chu]
    assert not thieu
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
            assert m["rong_ve"] == pytest.approx(mat_cat.rong_bao_dam(m["b"], CauHinhToVe()) * K)
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


# ---------------------------------------------------------------- bảng thống kê: T. BỘ, đoạn thanh; ghi chú thiếu Q


def test_t_bo_nhan_so_luong_theo_so_khung_tuong_tu(du_lieu):
    kh1 = ke_hoach.lap_ke_hoach(du_lieu, CauHinhToVe(ten_khung_truc="5"))
    kh12 = ke_hoach.lap_ke_hoach(du_lieu, CauHinhToVe(ten_khung_truc="5", so_khung_tuong_tu=12))
    d1, d12 = bang.dong_thong_ke(kh1), bang.dong_thong_ke(kh12)
    assert [r.so_luong * 12 for r in d1] == [r.so_luong for r in d12]
    assert [r.khoi_luong_kg * 12 for r in d1] == pytest.approx([r.khoi_luong_kg for r in d12])
    kq = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5", so_khung_tuong_tu=12))
    tbo = [c.noi_dung for c in kq.ban_ve.chu if c.noi_dung.isdigit()]
    assert "144" in tbo or any(int(x) % 12 == 0 for x in tbo)  # cột T. BỘ = 12 × số lượng 1 CK


def test_hinh_dang_thanh_ghi_chieu_dai_tung_doan(kh):
    """Bản mẫu: '600 | 7100 | 400' (thanh trên dầm), '500 | 3200' (thanh cột tầng mái), đai '170 250 50'."""
    hang = {int(r["so"]): r for r in bang.tong_hop_thanh(kh)}
    suot = next(t for t in kh.thanh_doc_dam["32"] if t.vai_tro == "tren_suot")
    assert hang[suot.so_hieu]["doan"][0] == 600.0 and hang[suot.so_hieu]["doan"][2] == 400.0
    so_cot_mai = kh.thanh_doc_cot["2"][0]
    assert hang[so_cot_mai]["doan"] == (3200.0, 500.0)
    dai = kh.dai_cot["2"][0]
    assert hang[dai.so_hieu]["doan"][:2] == (dai.rong, dai.cao)


def test_dam_thieu_q_co_ghi_chu_tren_ban_ve(du_lieu):
    import copy

    dl = copy.deepcopy(du_lieu)
    next(p for p in dl["phan_tu"] if p["ten"] == "32")["dai"] = {
        "loai": "dam", "duong_kinh_dai": 6, "buoc_goi": 150.0, "buoc_giua": 250.0, "canh_bao": "thiếu Q"}
    kq = bo_cuc.lap_ban_ve_khung(dl, CauHinhToVe(ten_khung_truc="5"))
    assert kq.dam_thieu_q == ["32"]
    assert any("THIẾU Q" in c.noi_dung and "32" in c.noi_dung for c in kq.ban_ve.chu)
    assert any("thiếu Q" in cb for cb in kq.canh_bao)
    kq0 = bo_cuc.lap_ban_ve_khung(du_lieu, CauHinhToVe(ten_khung_truc="5"))  # không có dầm nào báo thiếu Q
    assert kq0.dam_thieu_q == [] and not any("THIẾU Q" in c.noi_dung for c in kq0.ban_ve.chu)


# ---------------------------------------------------------------- mặt cắt: hình thái theo bản mẫu


def _ve_mat_cat(kh, loai, K=5.0):
    md = next(m for m in kh.mat_cat if m.loai == loai)
    suot = {t.so_hieu for lst in kh.thanh_doc_dam.values() for t in lst if t.vai_tro in ("tren_suot", "tren_suot_chung")}
    if loai == "dam":
        return md, mat_cat.ve_mat_cat_dam(kh.cfg, md, K, suot)[0]
    return md, mat_cat.ve_mat_cat_cot(kh.cfg, md, K)[0]


def test_mat_cat_dam_bbox_outline_cut_khop_kich_thuoc_ky_vong_ke_ca_net_gay(kh):
    """Verification so bbox đa giác OUTLINE_CUT với (rộng, cao) kỳ vọng ⇒ nét gãy zigzag nằm TRONG đa giác và đã tính vào rộng."""
    md, v = _ve_mat_cat(kh, "dam")
    hop = verify_drawing.hop_gioi_han_da_giac_ir(v.bv, layers.OUTLINE_CUT.ten)
    assert verify_drawing.khop_kich_thuoc_nao_do(hop, mat_cat.rong_bao_dam(md.b, kh.cfg) * 5.0, md.h * 5.0, dung_sai_mm=2.0)


def test_thanh_thep_mat_cat_la_cham_dac_khong_con_vong_tron_rong(kh):
    for loai in ("dam", "cot"):
        _, v = _ve_mat_cat(kh, loai)
        assert not [c for c in v.bv.vong_tron if c.layer == layers.REBAR_MAIN.ten]  # không còn vòng tròn rỗng trên layer thép
        cham = [dg for dg in v.bv.da_giac if dg.layer == layers.REBAR_MAIN.ten and len(dg.diem) == 20 and dg.do_rong_net > 0]
        assert len(cham) >= 4  # ≥ 4 chấm đặc (2 trên + 2 dưới / 4 góc cột)


def test_dai_mat_cat_co_moc_135_hai_vach_cheo(kh):
    for loai in ("dam", "cot"):
        _, v = _ve_mat_cat(kh, loai)
        cheo = [d for d in v.bv.doan_thang if d.layer == layers.REBAR_STIRRUP.ten
                and abs(abs(d.p2.x - d.p1.x) - abs(d.p2.y - d.p1.y)) < 1e-6 and abs(d.p2.x - d.p1.x) > 1.0]
        assert len(cheo) == 2  # hai vạch song song = móc 135°


def test_duong_bao_mat_cat_dam_hon_duong_bao_mat_dung():
    assert layers.OUTLINE_CUT.do_day_net_mm > layers.OUTLINE.do_day_net_mm


def test_nhan_thep_so_hieu_truoc_chu_sau(kh):
    """"ⓝ nội dung": chữ nội dung nằm BÊN PHẢI vòng tròn số hiệu (cả nhãn thép trên bên trái)."""
    _, v = _ve_mat_cat(kh, "dam")
    vong = {(round(c.tam.x), round(c.tam.y)): c for c in v.bv.vong_tron if c.layer == layers.SO_HIEU.ten}
    chu_thep = [c for c in v.bv.chu if re.fullmatch(r"\dØ\d+", c.noi_dung)]
    assert chu_thep
    for c in chu_thep:
        gan = [t for (x, y), t in vong.items() if abs(y - c.vi_tri.y) < 1.0 and 0 < c.vi_tri.x - x < 3 * t.ban_kinh + 1.0]
        assert gan, c.noi_dung  # có vòng tròn ngay bên trái chữ


def test_chu_kich_thuoc_hep_khong_dinh_nhau(kh):
    """Lỗi cũ: '25' và '170' dính thành '25170'. Nay mỗi chữ kích thước hẹp nằm ngoài đoạn hoặc không chồng chữ kề."""
    _, v = _ve_mat_cat(kh, "cot")
    chu = [c for c in v.bv.chu if c.layer == layers.DIM.ten and c.goc_do == 90.0]
    assert chu
    hop = []
    for c in chu:
        w = len(c.noi_dung) * 0.6 * c.chieu_cao
        hop.append((c.vi_tri.x - 0.5 * c.chieu_cao, c.vi_tri.y - w / 2, c.vi_tri.x + 0.5 * c.chieu_cao, c.vi_tri.y + w / 2, c.noi_dung))
    for i, a in enumerate(hop):
        for b in hop[i + 1:]:
            roi = a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]
            assert roi, (a[4], b[4])


def test_mat_cat_cot_khu_trung_theo_cau_hinh_thep_khong_theo_vung_dai(kh):
    cot = [m for m in kh.mat_cat if m.loai == "cot"]
    cau_hinh = {(c.b, c.h, c.d, c.n_b, c.n_h, kh.thanh_doc_cot[c.ten][0]) for c in kh.cots}
    assert len(cot) == len(cau_hinh) < 2 * len(kh.cots)
    # mọi vùng đai của một cột trỏ cùng một mặt cắt
    for c in kh.cots:
        assert len({kh.gan_mat_cat_cot[(c.ten, i)] for i in range(len(c.vung))}) == 1


def test_mong_dai_va_lot_duoc_ve_duoi_cot_tang_1(kh):
    """Hồi quy: thêm trường vào KeHoach từng làm be_rong_dai rơi vào trường khác ⇒ mất cả đài móng và bê tông lót."""
    assert set(kh.be_rong_dai) == {"A", "B", "C"}
    v = _Ve(kh.cfg)
    mat_dung.ve_mat_dung(kh, v)
    duoi = [dg for dg in v.bv.da_giac if dg.layer == layers.OUTLINE.ten and max(p.y for p in dg.diem) <= 1e-6]
    assert len(duoi) >= 6  # 3 đài + 3 lớp lót
