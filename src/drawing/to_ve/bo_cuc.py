"""Bố cục TỜ VẼ và hàm vào chính `lap_ban_ve_khung`.

Bố cục (toạ độ model, mm thật ở tỷ lệ in 1:ty_le; tờ chọn A1, không đủ chỗ thì A0):
  trái: mặt đứng khung (có dải trên để chi tiết nút/mặt bằng) | giữa: lưới mặt cắt | phải: bảng thống kê, ghi chú, khung tên.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from ..geometry import BanVe
from . import bang, mat_cat, mat_dung
from .co_so import CauHinhToVe, KetQuaToVe, _Ve
from .ke_hoach import lap_ke_hoach

KHO_GIAY = [("A1", 841.0, 594.0), ("A0", 1189.0, 841.0)]
RONG_KHOI_PHAI = 7900.0
KHOANG = 400.0


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
        if x_sec1 - x_sec0 >= cell_w and rows * cell_h <= H - 10 * T - 300.0 and h_el <= H - 10 * T:
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
