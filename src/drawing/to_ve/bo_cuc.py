"""Bố cục TỜ VẼ và hàm vào chính `lap_ban_ve_khung`.

Bố cục (toạ độ model, mm thật ở tỷ lệ in 1:ty_le; tờ chọn A1, không đủ chỗ thì A0):
  trái: mặt đứng khung (có dải trên để chi tiết nút/mặt bằng) | giữa: lưới mặt cắt | phải: bảng thống kê, ghi chú, khung tên.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from ..geometry import BanVe
from . import bang, chi_tiet_nut, mat_cat, mat_dung
from .co_so import CauHinhToVe, KetQuaToVe, _Ve
from .ke_hoach import lap_ke_hoach

KHO_GIAY = [("A1", 841.0, 594.0), ("A0", 1189.0, 841.0)]
RONG_KHOI_PHAI = 7900.0
KHOANG = 400.0
HE_SO_3D = 2.2  # phóng hình chi tiết nút 3D (so với mm thật)


def _chon_nut(kh) -> list[dict]:
    """Chọn tối đa 4 nút đại diện: nút biên + nút giữa ở tầng MÁI và ở tầng sàn thấp nhất có dầm (bản mẫu: CHI TIẾT 1–4)."""
    ten_truc = sorted(kh.truc, key=lambda k: kh.truc[k])
    moc = sorted(kh.moc.items(), key=lambda kv: kv[1])
    y_mai = moc[-1][1]
    y_san = min((d.y for d in kh.dams), default=None)
    nut = []
    for y, la_mai in ((y_mai, True), (y_san, False)):
        if y is None or (not la_mai and abs(y - y_mai) < 1.0):
            continue
        for i in (0, 1):
            if i >= len(ten_truc):
                continue
            tr = ten_truc[i]
            cot = next((c for c in kh.cots if c.truc == tr and abs(c.y1 - y) < 1.0), None)
            if cot is None:
                continue
            ph = next((d for d in kh.dams if abs(d.y - y) < 1.0 and d.truc1 == tr), None)
            tr_ = next((d for d in kh.dams if abs(d.y - y) < 1.0 and d.truc2 == tr), None)
            if ph is None and tr_ is None:
                continue
            nut.append({"truc": tr, "y": y, "cot": cot, "phai": ph, "trai": tr_, "mai": la_mai, "x": kh.truc[tr]})
    for i, n in enumerate(nut, start=1):
        n["ten"] = str(i)
    return nut


def lap_ban_ve_khung(du_lieu: dict, cfg: CauHinhToVe | None = None) -> KetQuaToVe:
    cfg = cfg or CauHinhToVe()
    kh = lap_ke_hoach(du_lieu, cfg)
    T = cfg.ty_le
    K = cfg.he_so_mat_cat

    # ---- mặt đứng ----
    v_md = _Ve(cfg, "MAT_DUNG")
    info = mat_dung.ve_mat_dung(kh, v_md)
    w_el = info["x_phai"] - info["x_trai"]
    h_el = info["y_cao"] - info["y_thap"]
    nut = _chon_nut(kh)
    for n in nut:  # khung nét đứt quanh nút + tên chi tiết (nối với hình 3D)
        hb = max([d.h for d in (n["phai"], n["trai"]) if d] or [500.0])
        x0, x1 = n["x"] - 700.0, n["x"] + 700.0
        y0, y1 = n["y"] - hb - 250.0, n["y"] + 450.0
        v_md.hcn(x0, y0, x1, y1, layers.HIDDEN.ten)
        v_md.chu((x0 + x1) / 2, y1 + 120.0, f"CHI TIẾT {n['ten']}", v_md.h_chu_nho, giua=True)

    # ---- mặt cắt ----
    suot = {t.so_hieu for lst in kh.thanh_doc_dam.values() for t in lst if t.vai_tro in ("tren_suot", "tren_suot_chung")}
    mcs = []
    for md in kh.mat_cat:
        if md.loai == "dam":
            v, w, h, goc = mat_cat.ve_mat_cat_dam(cfg, md, K, suot)
        else:
            v, w, h, goc = mat_cat.ve_mat_cat_cot(cfg, md, K)
        mcs.append((md, v, w, h, goc))
    cell_w = max((w for _, _, w, _, _ in mcs), default=0.0) + KHOANG
    cell_h = max((h for _, _, _, h, _ in mcs), default=0.0) + KHOANG

    # ---- chọn khổ giấy ----
    chon = None
    for ten, rg, cg in KHO_GIAY:
        W, H = rg * T, cg * T
        x_sec0 = 25 * T + 500.0 + w_el + KHOANG
        x_sec1 = W - 5 * T - RONG_KHOI_PHAI - KHOANG
        cols = max(1, int((x_sec1 - x_sec0) // cell_w))
        rows = math.ceil(len(mcs) / cols) if mcs else 0
        if x_sec1 - x_sec0 >= cell_w and rows * cell_h <= H - 10 * T - 300.0 and h_el + (2 * 5600.0 if nut else 0.0) <= H - 10 * T:
            chon = (ten, W, H, x_sec0, cols, rows)
            break
    canh_bao = list(kh.canh_bao)
    if chon is None:
        ten, rg, cg = KHO_GIAY[-1]
        W, H = rg * T, cg * T
        x_sec0 = 25 * T + 500.0 + w_el + KHOANG
        cols = max(1, int(((W - 5 * T - RONG_KHOI_PHAI - KHOANG) - x_sec0) // cell_w))
        rows = math.ceil(len(mcs) / cols) if mcs else 0
        chon = (ten, W, H, x_sec0, cols, rows)
        canh_bao.append(f"Không đủ chỗ trên khổ {ten}: lưới mặt cắt {cols}×{rows} có thể tràn — cần tăng khổ giấy/giảm tỷ lệ.")
    ten_kho, W, H, x_sec0, cols, rows = chon

    tong = BanVe(ten="TO_VE_KHUNG")
    khung = _Ve(cfg, "KHUNG")
    bang.ve_khung_to(cfg, khung, W, H)
    tong.gop(khung.bv)

    # mặt đứng đặt trái-dưới
    dx_el = 25 * T + 500.0 - info["x_trai"]
    dy_el = 5 * T + 700.0 - info["y_thap"]
    tong.gop(v_md.bv.dich_chuyen(dx_el, dy_el))

    # lưới mặt cắt (xếp từ trên xuống)
    y_top_sec = H - 5 * T - 400.0
    mat_cat_ve: list[dict] = []
    for i, (md, v, w, h, (ox, oy)) in enumerate(mcs):
        c, r = i % cols, i // cols
        x_cell = x_sec0 + c * cell_w
        y_cell = y_top_sec - (r + 1) * cell_h
        tong.gop(v.bv.dich_chuyen(x_cell - ox, y_cell - oy))
        if md.loai == "dam":
            rong_ve, cao_ve = (md.b + 2 * cfg.canh_ban_cua_t) * K, md.h * K
        else:
            rong_ve, cao_ve = md.h * K, md.b * K
        mat_cat_ve.append({"nhan": f"{md.so}-{md.so}", "loai": md.loai, "b": md.b, "h": md.h, "rong_ve": rong_ve, "cao_ve": cao_ve})

    # chi tiết nút 3D: dải phía TRÊN mặt đứng (cùng cột x với mặt đứng)
    y_3d_top = H - 5 * T - 400.0
    x_3d = 25 * T + 500.0
    cap = 0.0
    ds3 = []
    for n in nut:
        v3, w3, h3, goc3 = chi_tiet_nut.ve_chi_tiet_nut(kh, n["ten"], n["cot"], n["phai"], n["trai"], n["mai"], HE_SO_3D)
        ds3.append((v3, w3, h3, goc3))
    if ds3:
        cw = max(w for _, w, _, _ in ds3) + KHOANG
        ch = max(h for _, _, h, _ in ds3) + KHOANG
        cols3 = max(1, int(w_el // cw))
        y_free = 5 * T + 700.0 + h_el + 500.0  # trên mặt đứng
        rows3 = math.ceil(len(ds3) / cols3)
        if y_3d_top - rows3 * ch >= y_free:
            for i, (v3, w3, h3, (ox3, oy3)) in enumerate(ds3):
                c3, r3 = i % cols3, i // cols3
                tong.gop(v3.bv.dich_chuyen(x_3d + c3 * cw - ox3, y_3d_top - (r3 + 1) * ch - oy3))
        else:
            canh_bao.append("Không đủ chỗ cho hình chi tiết nút 3D trên khổ giấy đã chọn (bỏ qua).")

    # khối phải: bảng thống kê (trên) → ghi chú → khung tên (dưới cùng)
    x_ph = W - 5 * T - RONG_KHOI_PHAI
    vb = _Ve(cfg, "BANG")
    rong_bang, cao_bang = bang.ve_bang_thong_ke(kh, vb, x_ph, H - 5 * T - 400.0)
    tong.gop(vb.bv)
    vg = _Ve(cfg, "GHICHU")
    y_gc = H - 5 * T - 400.0 - cao_bang - 500.0
    cao_gc = bang.ve_ghi_chu(kh, vg, x_ph, y_gc, RONG_KHOI_PHAI)
    tong.gop(vg.bv)
    vt = _Ve(cfg, "KHUNGTEN")
    cao_kt = 24 * T
    bang.ve_khung_ten(cfg, vt, x_ph, 5 * T + 300.0, RONG_KHOI_PHAI, cao_kt)
    tong.gop(vt.bv)
    if y_gc - cao_gc < 5 * T + 300.0 + cao_kt:
        canh_bao.append("Khối ghi chú chạm khung tên — tăng khổ giấy.")

    so_sh = sum(1 for c in tong.vong_tron if c.layer == layers.SO_HIEU.ten)
    so_cot = len(kh.cots)
    so_dam = len(kh.dams)
    return KetQuaToVe(
        ban_ve=tong, thong_ke=bang.dong_thong_ke(kh), so_cot=so_cot, so_dam=so_dam, so_ky_hieu_ky_vong=so_sh,
        mat_cat=mat_cat_ve, he_so_mat_cat=K, canh_bao=canh_bao, kho_giay=ten_kho,
        so_da_giac_outline=sum(1 for dg in tong.da_giac if dg.layer == layers.OUTLINE.ten),
    )
