"""Hình chi tiết 3D (trục đo) cốt thép TẠI NÚT khung theo bản mẫu: lồng thép cột (thép dọc + đai) giao lồng thép dầm
(thép trên/dưới, móc vào cột, đai), có số hiệu thanh cùng hệ số hiệu với mặt đứng/bảng thống kê.

Không vẽ bê tông (bản mẫu chỉ thể hiện lồng thép). Mọi kích thước lấy từ `KeHoach` (tiết diện, thép, bước đai); đoạn
cột/dầm chỉ vẽ lân cận nút (đủ thấy cấu tạo): hai đầu cắt rời không có ký hiệu cắt.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from .co_so import _Dam, _Ve
from .ke_hoach import KeHoach

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_SH = layers.SO_HIEU.ten
L_AXIS = layers.AXIS.ten


def _iso(x: float, y: float, z: float, k: float, ox: float, oy: float):
    d = g.chieu_iso(x, y, z)
    return ox + d.x * k, oy + d.y * k


def _dem_hang_z(n: int, b: float, cv: float, dw: float, d: float) -> list[float]:
    """Toạ độ z của n thanh dàn đều theo bề rộng b (tâm 0)."""
    z0 = -b / 2 + cv + dw + d / 2
    z1 = b / 2 - cv - dw - d / 2
    if n <= 1:
        return [0.0]
    return [z0 + i * (z1 - z0) / (n - 1) for i in range(n)]


def ve_chi_tiet_nut(kh: KeHoach, ten: str, cot, dam_phai: _Dam | None, dam_trai: _Dam | None, la_mai: bool, K: float) -> tuple[_Ve, float, float, tuple]:
    """Một chi tiết nút. `cot` = đoạn cột DƯỚI nút (hoặc None nếu chỉ có đoạn trên); dầm phải/trái có thể None.
    Trả (hình, rộng, cao, (x0,y0)) — (x0,y0) là góc dưới-trái bao ngoài để bố cục đặt ô."""
    cfg = kh.cfg
    v = _Ve(cfg, f"CT_{ten}")
    cv_c, cv_d = cfg.lop_bao_ve_cot, cfg.lop_bao_ve_dam
    # ---- thông số hình học ----
    wc = cot.h
    dc = cot.b
    d_cot = cot.d
    dw_c = cot.vung[0].duong_kinh
    cot_tren = None if la_mai else next((c for c in kh.cots if c.truc == cot.truc and abs(c.y0 - cot.y1) < 1.0), None)
    h_dam_max = max([d.h for d in (dam_phai, dam_trai) if d] or [500.0])
    H_duoi, H_tren = 900.0, (0.0 if la_mai or cot_tren is None else 700.0)
    L_dam = 1500.0
    ox = oy = 0.0
    P = lambda x, y, z: _iso(x, y, z, K, ox, oy)  # noqa: E731

    def dd(p, q, layer=L_REBAR):
        v.doan(*P(*p), *P(*q), layer)

    def poly(pts, layer=L_REBAR):
        v.duong([P(*p) for p in pts], layer)

    # ---- cột: thép dọc ----
    pos = g.toa_do_thep_chu_vi_hcn(wc, dc, cv_c, dw_c, cot.n_h, d_cot, cot.n_b, d_cot)
    for tam, _d in pos:
        x, z = tam.x - wc / 2, tam.y - dc / 2
        dd((x, -H_duoi - h_dam_max, z), (x, H_tren, z))
    # đai cột: các vòng tại bước đầu cột (vùng nút) trong đoạn vẽ
    s_c = cot.vung[-1].buoc_mm if cot.vung else 150.0
    n_dai = int((H_duoi + h_dam_max + H_tren) // s_c)
    for i in range(n_dai + 1):
        y = -H_duoi - h_dam_max + 50.0 + i * s_c
        if y > H_tren:
            break
        x0, x1 = -wc / 2 + cv_c, wc / 2 - cv_c
        z0, z1 = -dc / 2 + cv_c, dc / 2 - cv_c
        poly([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), (x0, y, z0)], L_DAI)

    # ---- dầm ----
    def ve_dam(d: _Dam, huong: int):
        """huong=+1: dầm sang phải (x>0); −1: sang trái."""
        tl = kh.thanh_doc_dam[d.ten]
        suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        dw = d.vung[0].duong_kinh
        x_mat = huong * wc / 2  # mặt cột phía dầm
        x_xa = huong * (wc / 2 + L_dam)
        x_ngoai = -huong * (wc / 2 - cv_d)  # mặt ngoài cột phía đối diện
        co_dam_doi_dien = (dam_trai if huong > 0 else dam_phai) is not None
        # đai dầm
        s = d.vung[0].buoc_mm
        for i in range(int((L_dam - 50.0) // s) + 1):
            x = x_mat + huong * (50.0 + i * s)
            y0, y1 = -d.h + cv_d, -cv_d
            z0, z1 = -d.b / 2 + cv_d, d.b / 2 - cv_d
            poly([(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0), (x, y0, z0)], L_DAI)
        # thanh trên (suốt + gia cường), thanh dưới
        d_c = suot.duong_kinh if suot else 16
        l_hook = max(100.0, min(max(15.0 * d_c, 250.0), d.h - 2 * cv_d - 50.0))
        n_t = (suot.so_luong if suot else 2) + sum(n for lst in d._so_ben["trai" if huong > 0 else "phai"].values() for n, _ in lst)  # type: ignore[attr-defined]
        zt = _dem_hang_z(max(n_t, 2), d.b, cv_d, dw, d_c)
        y_t = -cv_d - dw - d_c / 2
        for i, z in enumerate(zt):
            ngoai = i < 2 or i >= len(zt) - 0 and False
            xe = x_ngoai if not co_dam_doi_dien else -huong * (wc / 2 + 0)
            if co_dam_doi_dien:
                dd((-huong * wc / 2, y_t, z), (x_xa, y_t, z))
            else:
                poly([(x_ngoai, y_t - l_hook, z), (x_ngoai, y_t, z), (x_xa, y_t, z)])
        d_b = max(d.bot) if d.bot else 16
        zb = _dem_hang_z(max(len(d.bot), 2), d.b, cv_d, dw, d_b)
        y_b = -d.h + cv_d + dw + d_b / 2
        for z in zb:
            if co_dam_doi_dien:
                dd((0.0, y_b, z), (x_xa, y_b, z))
            else:
                poly([(x_ngoai, y_b + l_hook, z), (x_ngoai, y_b, z), (x_xa, y_b, z)])
        return suot, d_c, d_b, zt, zb, y_t, y_b, x_xa

    kq_p = ve_dam(dam_phai, +1) if dam_phai else None
    kq_t = ve_dam(dam_trai, -1) if dam_trai else None

    # ---- số hiệu ----
    n_the = 0

    def the(p_tro, p_the, so, noi_dung, huong=1):
        nonlocal n_the
        xa, ya = P(*p_tro)
        xt, yt = P(*p_the)
        r = v.r_the
        dx, dy = xt - xa, yt - ya
        dist = math.hypot(dx, dy) or 1.0
        v.doan(xa, ya, xt - dx / dist * r, yt - dy / dist * r, L_SH)
        v.tron(xt, yt, r, L_SH)
        v.chu(xt, yt, str(so), v.h_chu, L_SH, giua=True)
        if huong >= 0:
            v.chu(xt + r + 0.5 * v.h_chu_nho, yt, noi_dung, v.h_chu)
        else:
            v.chu(xt - r - 0.5 * v.h_chu_nho, yt, noi_dung, v.h_chu, phai=True)
        n_the += 1

    # thép dọc cột
    so_h, n_tong, _ = kh.thanh_doc_cot[cot.ten]
    tam0 = pos[0][0]
    the((tam0.x - wc / 2, H_tren if H_tren else 0.0, tam0.y - dc / 2), (-wc / 2 - 700.0 / K, (H_tren or 250.0) + 500.0 / K, -dc / 2 - 600.0 / K), so_h, f"{n_tong}Ø{d_cot}", -1)
    # đai cột
    sh_dai = cot.nhan_dai[-1][0] if cot.nhan_dai else 0
    the((wc / 2 - cv_c, -H_duoi - h_dam_max + 50.0, -dc / 2 + cv_c), (wc / 2 + 600.0 / K, -H_duoi - h_dam_max - 400.0 / K, -dc / 2), sh_dai, cot.vung[-1].nhan() if cot.vung else "", 1)
    # dầm
    for kq, huong, dam in ((kq_p, +1, dam_phai), (kq_t, -1, dam_trai)):
        if not kq:
            continue
        suot, d_c, d_b, zt, zb, y_t, y_b, x_xa = kq
        tl = kh.thanh_doc_dam[dam.ten]
        if suot:
            the((huong * (wc / 2 + L_dam * 0.55), y_t, zt[-1]), (huong * (wc / 2 + L_dam * 0.55), y_t + 450.0 / K + 150, zt[-1] + 250.0 / K), suot.so_hieu, f"{suot.so_luong}Ø{suot.duong_kinh}", 1 if huong > 0 else -1)
        for dk, lst in dam._so_ben["trai" if huong > 0 else "phai"].items():  # type: ignore[attr-defined]
            for n, th in lst:
                the((huong * (wc / 2 + L_dam * 0.3), y_t - 60.0, zt[1]), (huong * (wc / 2 + L_dam * 0.2), y_t + 900.0 / K, zt[1] + 450.0 / K), th.so_hieu, f"{n}Ø{dk}", 1 if huong > 0 else -1)
        th_b = next((t for t in tl if t.vai_tro == "duoi"), None)
        if th_b:
            the((huong * (wc / 2 + L_dam * 0.6), y_b, zb[0]), (huong * (wc / 2 + L_dam * 0.6), y_b - 600.0 / K, zb[0] - 300.0 / K), th_b.so_hieu, f"{th_b.so_luong}Ø{th_b.duong_kinh}", 1 if huong > 0 else -1)
        dz = kh.dai_dam[dam.ten][0]
        the((huong * (wc / 2 + 200.0), -dam.h + cv_d, dam.b / 2 - cv_d), (huong * (wc / 2 + 700.0), -dam.h - 700.0 / K, dam.b / 2 + 250.0 / K), dz.so_hieu, f"Ø{dz.duong_kinh}a{dz.buoc:g}", 1 if huong > 0 else -1)

    # ---- bao ngoài + tên ----
    bx0, by0, bx1, by1 = v.bao()
    x0, x1, y0, y1 = bx0 - 200.0, bx1 + 200.0, by0 - 900.0, by1 + 200.0
    v.chu((bx0 + bx1) / 2, y0 + 250.0, f"CHI TIẾT {ten}", v.h_chu * 1.6, giua=True)
    return v, x1 - x0, y1 - y0, (x0, y0)
