"""Bảng thống kê cốt thép, khối ghi chú, khung tên, khung bản vẽ — dựng từ `KeHoach`.

Bảng giữ ĐÚNG 8 cột bắt buộc (KY_HIEU mục 3.9): CẤU KIỆN, SỐ HIỆU, HÌNH DÁNG, Ø(mm), DÀI 1CK(mm), SL, TỔNG DÀI(m),
K.LƯỢNG(kG) — `verify_drawing.kiem_tra_bang_thong_ke_du_cot_com` dò đúng các tiêu đề này. Cột HÌNH DÁNG vẽ hình phác thanh.
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

TIEU_DE = ["CẤU KIỆN", "SỐ HIỆU", "HÌNH DÁNG", "Ø(mm)", "DÀI 1CK(mm)", "SL", "TỔNG DÀI(m)", "K.LƯỢNG(kG)"]
RONG_COT_MM_GIAY = [20.0, 12.0, 38.0, 10.0, 20.0, 10.0, 18.0, 20.0]  # tổng 148 mm giấy


def tong_hop_thanh(kh: KeHoach) -> list[dict]:
    """Gom mọi thanh thép của khung theo SỐ HIỆU: {so_hieu, d, dai, sl, cau_kien(set), hinh, loai}."""
    m: dict[int, dict] = {}

    def them(so, d, dai, sl, ten, hinh, loai):
        if so not in m:
            m[so] = {"so": so, "d": d, "dai": dai, "sl": 0, "ck": [], "hinh": hinh, "loai": loai}
        m[so]["sl"] += sl
        if ten not in m[so]["ck"]:
            m[so]["ck"].append(ten)

    for c in kh.cots:
        so, n, dai = kh.thanh_doc_cot[c.ten]
        la_t1 = abs(c.y0) < 1.0
        them(so, c.d, dai, n, c.ten, "chan_L" if la_t1 else "thang", "cot")
        for z in kh.dai_cot[c.ten]:
            them(z.so_hieu, z.duong_kinh, z.chieu_dai, z.so_luong, c.ten, "dai", "cot")
    for d in kh.dams:
        for t in kh.thanh_doc_dam[d.ten]:
            if t.chieu_dai <= 0:
                continue
            hinh = {"tren_suot": "moc_2", "tren_cat_trai": "moc_1", "tren_cat_phai": "moc_1", "tren_cat_nut": "thang", "duoi": "thang"}.get(t.vai_tro, "thang")
            them(t.so_hieu, t.duong_kinh, t.chieu_dai, t.so_luong, d.ten, hinh, "dam")
        for z in kh.dai_dam[d.ten]:
            them(z.so_hieu, z.duong_kinh, z.chieu_dai, z.so_luong, d.ten, "dai", "dam")
    return sorted(m.values(), key=lambda r: (r["loai"] != "cot", r["so"]))


def dong_thong_ke(kh: KeHoach) -> list[g.DongThongKe]:
    ds = []
    for r in tong_hop_thanh(kh):
        ck = ",".join(sorted(r["ck"], key=lambda s: (len(s), s)))
        ten = ("Cột " if r["loai"] == "cot" else "Dầm ") + ck
        ds.append(g.tinh_dong_thong_ke(ten[:22], str(r["so"]), r["hinh"], int(r["d"]), round(r["dai"]), int(r["sl"])))
    return ds


def _phac_hinh(v: _Ve, x, y, w, h, hinh: str):
    """Hình phác thanh trong ô (x,y là góc dưới-trái; w×h kích thước ô)."""
    cx, cy = x + w / 2, y + h / 2
    a = w * 0.36
    if hinh == "dai":
        r = h * 0.28
        v.hcn(cx - a * 0.55, cy - r, cx + a * 0.55, cy + r, L_REBAR)
    elif hinh == "moc_2":
        v.duong([(cx - a, cy - h * 0.25), (cx - a, cy + h * 0.15), (cx + a, cy + h * 0.15), (cx + a, cy - h * 0.25)], L_REBAR)
    elif hinh == "moc_1":
        v.duong([(cx - a, cy - h * 0.25), (cx - a, cy + h * 0.15), (cx + a, cy + h * 0.15)], L_REBAR)
    elif hinh == "chan_L":
        v.duong([(cx - a * 0.5, cy + h * 0.3), (cx - a * 0.5, cy - h * 0.25), (cx + a * 0.15, cy - h * 0.25)], L_REBAR)
    else:
        v.doan(cx - a, cy, cx + a, cy, L_REBAR)


def ve_bang_thong_ke(kh: KeHoach, v: _Ve, x0: float, y_tren: float) -> tuple[float, float]:
    """Vẽ bảng từ góc TRÊN-TRÁI (x0, y_tren) đi xuống; trả (rộng, cao) model."""
    cfg = kh.cfg
    T = cfg.ty_le
    rong = [w * T for w in RONG_COT_MM_GIAY]
    cao_dong = 5.0 * T
    dong = tong_hop_thanh(kh)
    n = len(dong) + 1
    tong_rong = sum(rong)
    x_cot = [x0]
    for w in rong:
        x_cot.append(x_cot[-1] + w)
    # tổng hợp khối lượng theo nhóm đường kính
    kl = {"≤10": 0.0, "≤18": 0.0, ">18": 0.0}
    tong_dai = 0.0
    tong_kl = 0.0
    cao_tong = 3 * cao_dong
    ytb = y_tren - cao_dong * n - cao_tong
    # khung
    for i in range(n + 1):
        y = y_tren - i * cao_dong
        v.doan(x0, y, x0 + tong_rong, y, L_TXT)
    for xc in x_cot:
        v.doan(xc, y_tren, xc, y_tren - n * cao_dong, L_TXT)
    for i, tde in enumerate(TIEU_DE):
        v.chu((x_cot[i] + x_cot[i + 1]) / 2, y_tren - cao_dong / 2, tde, v.h_chu_nho * 0.85, giua=True)
    for hang, r in enumerate(dong, start=1):
        y = y_tren - (hang + 0.5) * cao_dong
        ck = ",".join(sorted(r["ck"], key=lambda s: (len(s), s)))
        ten = ("Cột " if r["loai"] == "cot" else "Dầm ") + ck
        if len(ten) > 12:
            ten = ten[:11] + "…"
        tl = r["dai"] * r["sl"] / 1000.0
        kg = tl * g.khoi_luong_tren_1m(int(r["d"]))
        tong_dai += tl
        tong_kl += kg
        nh = "≤10" if r["d"] <= 10 else ("≤18" if r["d"] <= 18 else ">18")
        kl[nh] += kg
        gt = [ten, str(r["so"]), None, str(int(r["d"])), f"{round(r['dai'])}", str(int(r["sl"])), f"{tl:.2f}", f"{kg:.2f}"]
        for i, s in enumerate(gt):
            if s is None:
                _phac_hinh(v, x_cot[i], y_tren - (hang + 1) * cao_dong, rong[i], cao_dong, r["hinh"])
            else:
                v.chu((x_cot[i] + x_cot[i + 1]) / 2, y, s, v.h_chu_nho, giua=True)
    # hàng tổng
    yb = y_tren - n * cao_dong
    v.doan(x0, yb - cao_tong, x0 + tong_rong, yb - cao_tong, L_TXT)
    v.doan(x0, yb, x0, yb - cao_tong, L_TXT)
    v.doan(x0 + tong_rong, yb, x0 + tong_rong, yb - cao_tong, L_TXT)
    v.chu(x0 + 0.5 * T, yb - cao_dong * 0.5, "TỔNG HỢP KHỐI LƯỢNG (kG):", v.h_chu_nho)
    v.chu(x0 + 0.5 * T, yb - cao_dong * 1.5, f"Ø ≤ 10: {kl['≤10']:.1f}    Ø ≤ 18: {kl['≤18']:.1f}    Ø > 18: {kl['>18']:.1f}", v.h_chu_nho)
    v.chu(x0 + 0.5 * T, yb - cao_dong * 2.5, f"TỔNG CỘNG: {tong_kl:.1f} kG   (dài {tong_dai:.1f} m)", v.h_chu_nho)
    return tong_rong, n * cao_dong + cao_tong


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
