"""Bảng thống kê cốt thép, khối ghi chú, khung tên, khung bản vẽ — dựng từ `KeHoach`.

Bảng theo ĐÚNG cấu trúc bản mẫu: tiêu đề bảng, ô gộp THÉP CỘT / THÉP DẦM, STT, HÌNH DẠNG KÈM SỐ ĐO, ĐƯỜNG KÍNH, CHIỀU DÀI THANH,
SỐ LƯỢNG (1 CK | T. BỘ), TỔNG CHIỀU DÀI, TRỌNG LƯỢNG và dòng TỔNG HỢP KHỐI LƯỢNG theo nhóm — `verify_drawing.kiem_tra_bang_thong_ke_du_cot_com`
dò các tiêu đề này (chấp nhận cả bộ 8 tiêu đề cũ của mục 3.9).
"""

from __future__ import annotations

from collections import defaultdict

from ...rule_engine import vat_lieu
from .. import geometry as g
from .. import layers
from .co_so import CauHinhToVe, _Ve
from .ke_hoach import KeHoach

L_TXT = layers.TEXT.ten
L_OUT = layers.OUTLINE.ten
L_REBAR = layers.REBAR_MAIN.ten

# Tiêu đề và bề rộng cột theo bản mẫu (cột SỐ LƯỢNG chia hai ô: 1 CK | T. BỘ ⇒ 9 ô)
TIEU_DE = ["CẤU KIỆN", "STT", "HÌNH DẠNG, KÍCH THƯỚC", "ĐƯỜNG KÍNH", "CHIỀU DÀI THANH", "SỐ LƯỢNG", "TỔNG CHIỀU DÀI", "TRỌNG LƯỢNG"]
RONG_COT_MM_GIAY = [11.0, 10.0, 46.0, 14.0, 18.0, 9.0, 11.0, 17.0, 19.0]  # tổng 155 mm giấy


def tong_hop_thanh(kh: KeHoach) -> list[dict]:
    """Gom mọi thanh thép của khung theo SỐ HIỆU: {so_hieu, d, dai, sl, cau_kien(set), hinh, loai}."""
    m: dict[int, dict] = {}

    def them(so, d, dai, sl, ten, hinh, loai, doan=()):
        if so not in m:
            m[so] = {"so": so, "d": d, "dai": dai, "sl": 0, "ck": [], "hinh": hinh, "loai": loai, "doan": tuple(doan)}
        m[so]["sl"] += sl
        if ten not in m[so]["ck"]:
            m[so]["ck"].append(ten)

    for c in kh.cots:
        so, n, dai = kh.thanh_doc_cot[c.ten]
        la_t1 = abs(c.y0) < 1.0
        la_mai = abs(c.y1 - max(kh.moc.values())) < 1.0
        them(so, c.d, dai, n, c.ten, "moc_1" if la_mai else ("chan_L" if la_t1 else "thang"), "cot", kh.doan_cot.get(c.ten, ()))
        for z in kh.dai_cot[c.ten]:
            them(z.so_hieu, z.duong_kinh, z.chieu_dai, z.so_luong, c.ten, "dai", "cot", (z.rong, z.cao, max(8.0 * z.duong_kinh, 50.0)))
    for d in kh.dams:
        for t in kh.thanh_doc_dam[d.ten]:
            if t.chieu_dai <= 0:
                continue
            hinh = {"tren_suot": "moc_2", "tren_cat_trai": "moc_1", "tren_cat_phai": "moc_1", "tren_cat_nut": "thang", "duoi": "thang"}.get(t.vai_tro, "thang")
            them(t.so_hieu, t.duong_kinh, t.chieu_dai, t.so_luong, d.ten, hinh, "dam", t.doan)
        for z in kh.dai_dam[d.ten]:
            them(z.so_hieu, z.duong_kinh, z.chieu_dai, z.so_luong, d.ten, "dai", "dam", (z.rong, z.cao, max(8.0 * z.duong_kinh, 50.0)))
    return sorted(m.values(), key=lambda r: (r["loai"] != "cot", r["so"]))


def dong_thong_ke(kh: KeHoach) -> list[g.DongThongKe]:
    ds = []
    for r in tong_hop_thanh(kh):
        ck = ",".join(sorted(r["ck"], key=lambda s: (len(s), s)))
        ten = ("Cột " if r["loai"] == "cot" else "Dầm ") + ck
        ds.append(g.tinh_dong_thong_ke(ten[:22], str(r["so"]), r["hinh"], int(r["d"]), round(r["dai"]), int(r["sl"]) * max(1, kh.cfg.so_khung_tuong_tu)))
    return ds


def _phac_hinh(v: _Ve, x, y, w, h, hinh: str, doan: tuple = (), dai_mm: float = 0.0):
    """Hình dạng thanh trong ô (x,y là góc dưới-trái; w×h kích thước ô) KÈM SỐ ĐO ngay trên hình như bản mẫu:
    thanh thẳng — nét ngang + chiều dài phía trên; thanh có móc — nét đứng ngắn ở đầu móc, số đo chân móc bên ngoài, số đo đoạn
    chính phía trên ("600 ┌ 7100 ┐ 400"); đai — hình chữ nhật, "cao [ rộng ] móc"."""
    co = v.h_chu_nho * 0.9
    cy = y + h * 0.46
    xa, xb = x + 0.2 * w, x + 0.8 * w
    cx = (xa + xb) / 2

    def so(t):  # số nguyên mm
        return f"{round(t):g}"

    if hinh == "dai" and len(doan) >= 3:
        rong, cao, moc = max(doan[0], doan[1]), min(doan[0], doan[1]), doan[2]  # giữa = cạnh dài, trái = cạnh ngắn (bản mẫu "170 [250] 50")
        r = 0.3 * h
        v.hcn(xa, cy - r, xb, cy + r, L_REBAR)
        v.doan(xb, cy - r, xb, cy + r + 0.25 * h, L_REBAR)  # móc
        v.chu(cx, cy, so(rong), co, L_TXT, giua=True)
        v.chu(xa - 0.4 * co, cy, so(cao), co, L_TXT, phai=True)
        v.chu(xb + 0.4 * co, cy, so(moc), co)
        return
    v.doan(xa, cy, xb, cy, L_REBAR)
    if hinh in ("moc_1", "chan_L") and len(doan) >= 2:
        chan, chinh = (min(doan), max(doan))
        x_tick = xb if hinh == "chan_L" else xa
        v.doan(x_tick, cy, x_tick, cy - 0.3 * h, L_REBAR)
        v.chu(cx, cy + 0.45 * co + 0.15 * h, so(chinh), co, L_TXT, giua=True)
        if hinh == "chan_L":
            v.chu(x_tick + 0.4 * co, cy - 0.15 * h, so(chan), co)
        else:
            v.chu(x_tick - 0.4 * co, cy - 0.15 * h, so(chan), co, L_TXT, phai=True)
    elif hinh == "moc_2" and len(doan) >= 3:
        v.doan(xa, cy, xa, cy - 0.3 * h, L_REBAR)
        v.doan(xb, cy, xb, cy - 0.3 * h, L_REBAR)
        v.chu(cx, cy + 0.45 * co + 0.15 * h, so(doan[1]), co, L_TXT, giua=True)
        v.chu(xa - 0.4 * co, cy - 0.15 * h, so(doan[0]), co, L_TXT, phai=True)
        v.chu(xb + 0.4 * co, cy - 0.15 * h, so(doan[2]), co)
    else:
        v.chu(cx, cy + 0.45 * co + 0.15 * h, so(dai_mm or (doan[0] if doan else 0)), co, L_TXT, giua=True)


def ve_bang_thong_ke(kh: KeHoach, v: _Ve, x0: float, y_tren: float) -> tuple[float, float]:
    """Bảng thống kê theo bản mẫu: tiêu đề bảng; cột CẤU KIỆN là ô gộp THÉP CỘT / THÉP DẦM (kèm "SL: n"); STT; HÌNH DẠNG, KÍCH
    THƯỚC (số đo trên hình); ĐƯỜNG KÍNH; CHIỀU DÀI THANH; SỐ LƯỢNG (1 CK | T. BỘ); TỔNG CHIỀU DÀI; TRỌNG LƯỢNG; mỗi nhóm kết bằng
    dòng TỔNG HỢP KHỐI LƯỢNG theo nhóm đường kính. Vẽ từ góc TRÊN-TRÁI (x0, y_tren) đi xuống; trả (rộng, cao) model."""
    cfg = kh.cfg
    T = cfg.ty_le
    rong = [w * T for w in RONG_COT_MM_GIAY]
    x_cot = [x0]
    for w in rong:
        x_cot.append(x_cot[-1] + w)
    tong_rong = x_cot[-1] - x0
    n_khung = max(1, int(cfg.so_khung_tuong_tu))
    h_tieu_de, h_dau, h_dong, h_tong = 9.0 * T, 14.0 * T, 8.0 * T, 9.0 * T
    co = v.h_chu_nho
    thanh = tong_hop_thanh(kh)
    nhom_thep = [("THÉP CỘT", len(kh.cots), [r for r in thanh if r["loai"] == "cot"]),
                 ("THÉP DẦM", len(kh.dams), [r for r in thanh if r["loai"] == "dam"])]
    # thanh dọc trước, đai sau (như bản mẫu), mỗi nhóm theo số hiệu
    nhom_thep = [(ten, sl, sorted(rs, key=lambda r: (r["hinh"] == "dai", r["so"]))) for ten, sl, rs in nhom_thep]

    # --- khung + tiêu đề ---
    y = y_tren
    v.doan(x0, y, x0 + tong_rong, y, L_TXT)
    v.chu(x0 + tong_rong / 2, y - h_tieu_de / 2, "BẢNG THỐNG KÊ CỐT THÉP", co * 1.6, giua=True)
    y -= h_tieu_de
    v.doan(x0, y, x0 + tong_rong, y, L_TXT)
    y_dau = y
    y -= h_dau
    v.doan(x0, y, x0 + tong_rong, y, L_TXT)
    tieu_de = [("CẤU KIỆN", None), ("STT", None), ("HÌNH DẠNG, KÍCH THƯỚC", None), ("ĐƯỜNG KÍNH", "(mm)"),
               ("CHIỀU DÀI THANH", "(mm)"), ("SỐ LƯỢNG", None), ("TỔNG CHIỀU DÀI", "(m)"), ("TRỌNG LƯỢNG", "(kG)")]
    # cột SỐ LƯỢNG gồm hai ô con (1 CK | T. BỘ) ⇒ RONG_COT_MM_GIAY có 9 phần tử; chỉ số cột tiêu đề → chỉ số ô
    idx_tieu_de = [0, 1, 2, 3, 4, (5, 6), 7, 8]
    for (t, dv), ix in zip(tieu_de, idx_tieu_de):
        xa, xb = (x_cot[ix[0]], x_cot[ix[1] + 1]) if isinstance(ix, tuple) else (x_cot[ix], x_cot[ix + 1])
        cy = y_dau - h_dau * (0.32 if isinstance(ix, tuple) else 0.42)
        v.chu((xa + xb) / 2, cy, t, co * 0.78, giua=True)
        if dv:
            v.chu((xa + xb) / 2, y_dau - h_dau * 0.76, dv, co * 0.78, giua=True)
    xs5, xs6, xs7 = x_cot[5], x_cot[6], x_cot[7]
    v.doan(xs5, y_dau - h_dau * 0.5, xs7, y_dau - h_dau * 0.5, L_TXT)
    v.chu((xs5 + xs6) / 2, y_dau - h_dau * 0.75, "1 CK", co * 0.78, giua=True)
    v.chu((xs6 + xs7) / 2, y_dau - h_dau * 0.75, "T. BỘ", co * 0.78, giua=True)
    y_dau_cot = y_dau  # đầu các đường dọc

    # --- các nhóm ---
    kl_nhom: list[dict[str, float]] = []
    seg_hang: list[tuple[float, float]] = []  # đoạn các hàng thanh của từng nhóm (không gồm dòng TỔNG HỢP) — vẽ đường dọc
    for ten, sl_ck, rows in nhom_thep:
        y_nhom = y
        kl = {"≤10": 0.0, "≤18": 0.0, ">18": 0.0}
        for r in rows:
            sl_bo = int(r["sl"]) * n_khung
            tl = r["dai"] * sl_bo / 1000.0
            kg = tl * g.khoi_luong_tren_1m(int(r["d"]))
            kl["≤10" if r["d"] <= 10 else ("≤18" if r["d"] <= 18 else ">18")] += kg
            cy = y - h_dong / 2
            gt = {1: str(r["so"]), 3: str(int(r["d"])), 4: f"{round(r['dai'])}", 5: str(int(r["sl"])), 6: str(sl_bo),
                  7: f"{tl:.2f}".rstrip("0").rstrip(".") if tl % 1 else f"{tl:.1f}", 8: f"{kg:.2f}"}
            for ix, txt in gt.items():
                v.chu((x_cot[ix] + x_cot[ix + 1]) / 2, cy, txt, co, giua=True)
            _phac_hinh(v, x_cot[2], y - h_dong, rong[2], h_dong, r["hinh"], r.get("doan", ()), r["dai"])
            y -= h_dong
            v.doan(x_cot[1], y, x0 + tong_rong, y, L_TXT)
        seg_hang.append((y_nhom, y))
        # ô gộp CẤU KIỆN: chữ đứng "THÉP CỘT" + "(SL: n)"
        cao_nhom = y_nhom - y
        xc = (x_cot[0] + x_cot[1]) / 2
        v.chu(xc - 0.55 * co, y_nhom - cao_nhom / 2, ten, co * 1.1, giua=True, goc=90.0)
        v.chu(xc + 0.75 * co, y_nhom - cao_nhom / 2, f"(SL: {sl_ck})", co * 0.8, giua=True, goc=90.0)
        # dòng TỔNG HỢP KHỐI LƯỢNG của nhóm
        v.doan(x_cot[1], y, x0 + tong_rong, y, L_TXT)
        v.chu(x_cot[1] + 0.5 * co, y - h_tong * 0.3, "TỔNG HỢP KHỐI LƯỢNG (kG):", co * 0.85)
        v.chu(x_cot[1] + 0.5 * co + 14 * T, y - h_tong * 0.72,
              f"Ø ≤ 10 : {kl['≤10']:.1f}      Ø ≤ 18 : {kl['≤18']:.1f}      Ø > 18 : {kl['>18']:.1f}", co * 0.85)
        y -= h_tong
        v.doan(x0, y, x0 + tong_rong, y, L_TXT)
        kl_nhom.append(kl)
    # đường dọc: cột 0, 1 và mép phải chạy suốt (ô gộp CẤU KIỆN); các cột còn lại chỉ ở tiêu đề và các hàng thanh (dòng TỔNG HỢP là
    # ô gộp, không có đường dọc đi qua chữ)
    for k, xc in enumerate(x_cot):
        if k in (0, 1) or k == len(x_cot) - 1:
            v.doan(xc, y_dau_cot, xc, y, L_TXT)
            continue
        y_ngang = y_dau_cot - (h_dau * 0.5 if k == 6 else 0.0)
        v.doan(xc, y_ngang, xc, y_dau_cot - h_dau, L_TXT)
        for ya, yb in seg_hang:
            v.doan(xc, ya, xc, yb, L_TXT)
    v.doan(x0, y_tren, x0, y, L_TXT)
    v.doan(x0 + tong_rong, y_tren, x0 + tong_rong, y, L_TXT)
    return tong_rong, y_tren - y


def ve_ghi_chu(kh: KeHoach, v: _Ve, x0: float, y_tren: float, rong: float) -> float:
    """Khối ghi chú: vật liệu (tra từ `vat_lieu`, không gõ tay), tiêu chuẩn, GIẢ ĐỊNH bản vẽ. Trả chiều cao."""
    cfg = kh.cfg
    T = cfg.ty_le
    dong: list[str] = ["GHI CHÚ:"]
    mac = next((p.raw.get("mac_be_tong") for p in kh.dams if p.raw.get("mac_be_tong")), None) or next(
        (c.raw.get("mac_be_tong") for c in kh.cots if c.raw.get("mac_be_tong")), None
    )
    nhom = next((c.raw.get("nhom_thep_doc") for c in kh.cots if c.raw.get("nhom_thep_doc")), None) or next(
        (d.raw.get("nhom_thep_doc") for d in kh.dams if d.raw.get("nhom_thep_doc")), None
    )
    try:
        if mac:
            bt = vat_lieu.lay_be_tong(mac)
            dong.append(f"- BÊ TÔNG CẤP ĐỘ BỀN {mac}: Rb = {bt.Rb:g} MPa; Rbt = {bt.Rbt:g} MPa; Eb = {bt.Eb:g} MPa.")
        if nhom:
            th = vat_lieu.lay_thep(nhom)
            dong.append(f"- CỐT THÉP DỌC NHÓM {nhom}: Rs = {th.Rs:g} MPa; Rsc = {th.Rsc:g} MPa.")
        dd = vat_lieu.lay_thep("CB240-T")
        dong.append(f"- CỐT THÉP ĐAI NHÓM CB240-T: Rsw = {dd.Rsw:g} MPa.")
    except Exception:  # vật liệu lạ — không bịa số
        dong.append("- VẬT LIỆU: xem hồ sơ thiết kế (không tra được từ bảng chuẩn).")
    dong += [
        "- CÁC QUY PHẠM VÀ TIÊU CHUẨN THIẾT KẾ:",
        "   + TCVN 2737:2023 — Tải trọng và tác động.",
        "   + TCVN 5574:2018 — Kết cấu bê tông và bê tông cốt thép.",
        "   + TCVN 4612:1988 — Ký hiệu quy ước và thể hiện bản vẽ kết cấu BTCT.",
        f"- LỚP BẢO VỆ: DẦM {cfg.lop_bao_ve_dam:g} mm, CỘT {cfg.lop_bao_ve_cot:g} mm (đến mép đai). Mọi kích thước: mm.",
        f"- GIẢ ĐỊNH (dữ liệu chưa có): COS ±0.000 = đỉnh móng + {cfg.cao_do_ton_nen_tren_dinh_mong:g}; COS TỰ NHIÊN = ±0.000 − "
        f"{cfg.cao_do_tu_nhien_duoi_ton_nen:g}; sàn dày {cfg.day_san:g}; đài {cfg.day_dai_mong:g} + lót {cfg.day_lot:g} MINH HOẠ.",
        "- ĐIỂM CẮT THÉP, ĐOẠN NEO VÀ ĐAI THEO VÙNG LÀ BỐ TRÍ SƠ BỘ [thực hành]: cần kỹ sư xác nhận trước khi thi công.",
    ]
    if kh.dam_dai_etabs:
        dong.append("- ĐAI DẦM " + ", ".join(kh.dam_dai_etabs[:10]) + (" …" if len(kh.dam_dai_etabs) > 10 else "")
                    + " LẤY THEO ASW/S DO ETABS THIẾT KẾ (VRebar); dữ liệu không có Q nên CHƯA kiểm lại khả năng chịu cắt bằng Q.")
    if kh.dam_thieu_q:
        dong.append("- ⚠ THIẾU Q (dữ liệu ETABS không có lực cắt dầm): cốt đai dầm " + ", ".join(kh.dam_thieu_q[:10])
                    + (" …" if len(kh.dam_thieu_q) > 10 else "") + " CHỈ THEO CẤU TẠO, CHƯA KIỂM KHẢ NĂNG CHỊU CẮT — phải kiểm bằng Q.")
    for cb in kh.canh_bao[:6]:
        dong.append("- " + cb)
    dy = 4.2 * T
    for i, s in enumerate(dong):
        v.chu(x0, y_tren - (i + 1) * dy + 0.6 * T, s, v.h_chu_nho * (1.15 if i == 0 else 1.0))
    return len(dong) * dy + 0.5 * T


def ve_khung_ten(cfg: CauHinhToVe, v: _Ve, x0: float, y0: float, rong: float, cao: float) -> None:
    """Khung tên: trái = trường/khoa/chuyên ngành, phải = tên đồ án (ô lớn); dưới = 3 hàng chức danh."""
    T = cfg.ty_le
    tt = {
        "ten_truong": "TRƯỜNG ĐẠI HỌC KIẾN TRÚC HÀ NỘI", "khoa": "KHOA XÂY DỰNG", "chuyen_nganh": "CHUYÊN NGÀNH XÂY DỰNG DD&CN",
        "ten_do_an": "KẾT CẤU BÊ TÔNG CỐT THÉP", "gvhd": "—", "svth": "—", "de_so": "—", "ngay_nhan": "—", "ngay_hoan_thanh": "—",
    }
    tt.update(cfg.thong_tin_khung_ten or {})
    v.hcn(x0, y0, x0 + rong, y0 + cao, L_OUT)
    c1 = x0 + rong * 0.52
    h_tren = cao * 0.46
    v.doan(x0, y0 + cao - h_tren, x0 + rong, y0 + cao - h_tren, L_OUT)
    v.doan(c1, y0 + cao - h_tren, c1, y0 + cao, L_OUT)
    for i, s in enumerate((tt["ten_truong"], tt["khoa"], tt["chuyen_nganh"])):
        v.chu(x0 + c1 * 0 + (c1 - x0) / 2, y0 + cao - (i + 1) * h_tren / 4, s, v.h_chu_nho, giua=True)
    v.chu((c1 + x0 + rong) / 2, y0 + cao - h_tren * 0.35, "ĐỒ ÁN", v.h_chu_nho, giua=True)
    v.chu((c1 + x0 + rong) / 2, y0 + cao - h_tren * 0.7, tt["ten_do_an"], v.h_chu, giua=True)
    hang = [("GVHD", tt["gvhd"], "NGÀY NHẬN", tt["ngay_nhan"]), ("SVTH", tt["svth"], "ĐỀ SỐ", tt["de_so"]),
            ("", "", "HOÀN THÀNH", tt["ngay_hoan_thanh"])]
    h_h = (cao - h_tren) / 3
    xs = [x0, x0 + rong * 0.18, x0 + rong * 0.55, x0 + rong * 0.75, x0 + rong]
    for i, (a, b_, c_, d_) in enumerate(hang):
        y_ = y0 + (2 - i) * h_h
        v.doan(x0, y_, x0 + rong, y_, L_OUT)
        for x_ in xs[1:-1]:
            v.doan(x_, y_, x_, y_ + h_h, L_OUT)
        for k, s in enumerate((a, b_, c_, d_)):
            v.chu((xs[k] + xs[k + 1]) / 2, y_ + h_h / 2, s, v.h_chu_nho, giua=True)


def ve_khung_to(cfg: CauHinhToVe, v: _Ve, rong: float, cao: float) -> None:
    """Đường mép tờ + khung bản vẽ (lề trái 25 mm giấy, còn lại 5 mm)."""
    T = cfg.ty_le
    v.hcn(0, 0, rong, cao, L_OUT)
    v.hcn(25 * T, 5 * T, rong - 5 * T, cao - 5 * T, L_OUT, rong=0.8 * T)
