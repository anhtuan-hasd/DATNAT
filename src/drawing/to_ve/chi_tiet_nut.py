"""Hình chi tiết 3D (trục đo) cốt thép TẠI NÚT khung theo bản mẫu `BoTriThep_KhungTruc5_mau.pdf` (đo phóng to CHI TIẾT 1–4):

- chỉ thể hiện LỒNG THÉP (không vẽ bê tông); thanh dọc là MỘT NÉT MẢNH, đai là nét đậm hơn có móc 135° ở một góc;
- đai vẽ THƯA theo sơ đồ (cột 4 đai dưới nút, dầm 5 đai) — hình để thấy cấu tạo, KHÔNG phải số đai thật (bước đai thật ghi ở nhãn);
- nút mái: thép cột uốn ngang vào dầm; nút biên: thép trên dầm uốn xuống cột; thép dưới dầm thẳng;
- nhãn dạng "ⓝ nội dung": phía trái = [vòng tròn][chữ] rồi đường dẫn tới thanh, phía phải = đường dẫn rồi [vòng tròn][chữ];
  vòng tròn xếp theo cột dọc hai bên hình, tránh chồng nhau.

Số hiệu thanh dùng chung với mặt đứng / bảng thống kê (lấy từ `KeHoach`). Mọi kích thước tiết diện, số thanh, Ø lấy từ `KeHoach`.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from . import chi_tiet_thep
from .co_so import HE_SO_RONG_CHU, _Dam, _Ve
from .ke_hoach import KeHoach

L_BAR = layers.REBAR_BAR.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_SH = layers.SO_HIEU.ten
L_KHUAT = layers.HIDDEN.ten  # nét khuất (đứt, mảnh): phần lồng thép nằm phía SAU (xa người xem), bị các đai phía trước che

BUOC_DAI_COT_SO_DO = 430.0  # bước đai vẽ trong hình (sơ đồ)
BUOC_DAI_DAM_SO_DO = 330.0
SO_DAI_COT_DUOI = 4
SO_DAI_DAM = 5


def _iso(x: float, y: float, z: float, k: float):
    d = g.chieu_iso(x, y, z)
    return d.x * k, d.y * k


def _dem_hang_z(n: int, b: float, cv: float, dw: float, d: float) -> list[float]:
    """Toạ độ z của n thanh dàn đều theo bề rộng b (tâm 0)."""
    z0 = -b / 2 + cv + dw + d / 2
    z1 = b / 2 - cv - dw - d / 2
    if n <= 1:
        return [0.0]
    return [z0 + i * (z1 - z0) / (n - 1) for i in range(n)]


class _Nhan:
    """Gom nhãn rồi đặt vòng tròn theo hai cột dọc hai bên hình, tránh chồng nhau."""

    def __init__(self):
        self.ds: list[tuple[float, float, str, str, int]] = []  # (x, y, so, noi_dung, ben: -1 trái / +1 phải)

    def them(self, xy: tuple[float, float], so: int, noi_dung: str, ben: int) -> None:
        self.ds.append((xy[0], xy[1], str(so), noi_dung, ben))

    def ve(self, v: _Ve, x_trai: float, x_phai: float) -> None:
        r = v.r_the
        co = v.h_chu_nho
        for ben in (-1, 1):
            nhom = sorted((d for d in self.ds if d[4] == ben), key=lambda d: d[1])
            y_truoc = None
            for x, y, so, nd, _ in nhom:
                yc = y if y_truoc is None else max(y, y_truoc + 2.7 * r)
                y_truoc = yc
                w = len(nd) * HE_SO_RONG_CHU * v.h_chu
                if ben < 0:  # [vòng tròn][chữ] ─── thanh
                    cx = x_trai - 1.0 * co - w - 0.5 * co - r
                    v.tron(cx, yc, r, L_SH)
                    v.chu(cx, yc, so, v.h_chu, L_SH, giua=True)
                    v.chu(cx + r + 0.5 * co, yc, nd, v.h_chu)
                    x_dau = cx + r + 0.5 * co + w + 0.3 * co
                    v.doan(x_dau, yc, x, y, L_SH)
                else:  # thanh ─── [vòng tròn][chữ]
                    cx = x_phai + 1.0 * co + r
                    v.doan(x, y, cx - r, yc, L_SH)
                    v.tron(cx, yc, r, L_SH)
                    v.chu(cx, yc, so, v.h_chu, L_SH, giua=True)
                    v.chu(cx + r + 0.5 * co, yc, nd, v.h_chu)


def ve_chi_tiet_nut(kh: KeHoach, ten: str, cot, dam_phai: _Dam | None, dam_trai: _Dam | None, la_mai: bool, K: float) -> tuple[_Ve, float, float, tuple]:
    """Một chi tiết nút. `cot` = đoạn cột DƯỚI nút; dầm phải/trái có thể None. Trả (hình, rộng, cao, (x0,y0))."""
    cfg = kh.cfg
    v = _Ve(cfg, f"CT_{ten}")
    cv_c, cv_d = cfg.lop_bao_ve_cot, cfg.lop_bao_ve_dam
    wc, dc = cot.h, cot.b
    d_cot = cot.d
    dw_c = cot.vung[0].duong_kinh if cot.vung else 6
    cot_tren = None if la_mai else next((c for c in kh.cots if c.truc == cot.truc and abs(c.y0 - cot.y1) < 1.0), None)
    h_dam = max([d.h for d in (dam_phai, dam_trai) if d] or [500.0])
    H_duoi = h_dam + SO_DAI_COT_DUOI * BUOC_DAI_COT_SO_DO
    H_tren = 0.0 if cot_tren is None else 2 * BUOC_DAI_COT_SO_DO
    L_dam = max(1800.0, 3.2 * wc)
    nhan = _Nhan()

    def P(x, y, z):
        return _iso(x, y, z, K)

    def doan(p, q, layer=L_BAR):
        v.doan(*P(*p), *P(*q), layer)

    def doan_t(p, q, z_xa, layer=L_BAR):
        """Đoạn thẳng nằm hoàn toàn trên mặt PHỎNG XA (z = z_xa) ⇒ bị che bởi mặt gần ⇒ vẽ NÉT KHUẤT (đứt)."""
        doan(p, q, L_KHUAT if (abs(p[2] - z_xa) < 1e-6 and abs(q[2] - z_xa) < 1e-6) else layer)

    def thanh(pts3, d=16):
        """Thanh uốn: chiếu các đỉnh rồi bo cung (một nét) — bán kính bo theo đường kính uốn tối thiểu (mm thật × K)."""
        v.thanh([P(*p) for p in pts3], d, r=chi_tiet_thep.ban_kinh_tim(d) * K * 0.9)

    def dai_vong(y, x0, x1, z0, z1, x_moc=None):
        pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), (x0, y, z0)]
        for a, b in zip(pts, pts[1:]):  # cạnh ở mặt xa (z = z1) vẽ nét khuất
            doan_t(a, b, z1, L_DAI)
        # móc 135°: hai vạch ngắn ở góc (x1, z1), chếch vào trong
        lm = 0.12 * min(x1 - x0, z1 - z0) + 25.0
        for dz in (0.0, -0.18 * (z1 - z0)):
            doan((x1, y, z1 + dz), (x1 - lm, y, z1 + dz - lm * 0.8), L_DAI)

    # ---- đai cột: dưới nút (4 vòng) và trên nút (nếu nút tầng giữa) ----
    x0, x1 = -wc / 2 + cv_c, wc / 2 - cv_c
    z0, z1 = -dc / 2 + cv_c, dc / 2 - cv_c
    y_dau = -h_dam - 90.0
    ys_dai_cot = [y_dau - i * BUOC_DAI_COT_SO_DO for i in range(SO_DAI_COT_DUOI)]
    ys_dai_cot += [-cv_d - 70.0 - i * 120.0 for i in range(2)]  # đai cột chạy qua nút (trong chiều cao dầm)
    if cot_tren is not None:
        ys_dai_cot += [90.0 + i * BUOC_DAI_COT_SO_DO for i in range(2)]
    for y in ys_dai_cot:
        dai_vong(y, x0, x1, z0, z1)

    # ---- thép dọc cột: tầng mái ⇒ uốn ngang vào dầm; tầng giữa ⇒ chạy suốt ----
    pos = g.toa_do_thep_chu_vi_hcn(wc, dc, cv_c, dw_c, cot.n_h, d_cot, cot.n_b, d_cot)
    l_vao = min(getattr(cot, "_l_vao", 500.0) or 500.0, L_dam * 0.6)
    huong_uon = getattr(cot, "_huong_uon", (0, 0)) if la_mai else (0, 0)
    y_day = -H_duoi
    z_max_cot = max(t.y for t, _ in pos) - dc / 2  # mặt phỏng xa của lồng thép cột
    y_top_ban = H_tren if cot_tren is not None else -cv_d - 70.0
    for tam, _d in pos:
        x, z = tam.x - wc / 2, tam.y - dc / 2
        hu = 0
        if la_mai:
            hu = huong_uon[0] if x < 0 else huong_uon[1]
            if x == 0:
                hu = huong_uon[0]
        if hu:
            y_leg = -cv_d - 70.0 - (0.0 if abs(x) > wc / 4 and (hu > 0) == (x < 0) else 70.0)
            thanh([(x, y_day, z), (x, y_leg, z), (x + hu * l_vao, y_leg, z)], d_cot)
        else:
            doan_t((x, y_day, z), (x, y_top_ban, z), z_max_cot)

    # ---- dầm ----
    def ve_dam(d: _Dam, huong: int):
        tl = kh.thanh_doc_dam[d.ten]
        suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        dw = d.vung[0].duong_kinh
        x_mat = huong * wc / 2
        x_xa = huong * (wc / 2 + L_dam)
        x_ngoai = -huong * (wc / 2 - cv_c - 20.0)
        co_doi_dien = (dam_trai if huong > 0 else dam_phai) is not None
        # đai dầm: SO_DAI_DAM vòng đều theo sơ đồ
        sv = (L_dam - 150.0) / (SO_DAI_DAM - 1)
        zb0, zb1 = -d.b / 2 + cv_d, d.b / 2 - cv_d
        for i in range(SO_DAI_DAM):
            x = x_mat + huong * (110.0 + i * sv)
            vong = [(x, -d.h + cv_d, zb0), (x, -d.h + cv_d, zb1), (x, -cv_d, zb1), (x, -cv_d, zb0), (x, -d.h + cv_d, zb0)]
            for a, b in zip(vong, vong[1:]):
                doan_t(a, b, zb1, L_DAI)
            lm = 0.12 * (d.h - 2 * cv_d)
            for dz in (0.0, -0.2 * (zb1 - zb0)):
                doan((x, -cv_d, zb1 + dz), (x, -cv_d - lm, zb1 + dz - lm * 0.6), L_DAI)
        d_c = suot.duong_kinh if suot else 16
        n_t = (suot.so_luong if suot else 2) + sum(n for lst in d._so_ben["trai" if huong > 0 else "phai"].values() for n, _ in lst)  # type: ignore[attr-defined]
        zt = _dem_hang_z(max(n_t, 2), d.b, cv_d, dw, d_c)
        y_t = -cv_d - dw - d_c / 2
        for z in zt:
            if co_doi_dien:
                doan_t((-huong * wc / 2, y_t, z), (x_xa, y_t, z), zt[-1])
            elif z == zt[-1]:  # thanh ở mặt xa: nét khuất (không uốn cung)
                doan_t((x_ngoai, y_t, z), (x_xa, y_t, z), zt[-1])
            else:  # nút biên: uốn xuống trong cột
                thanh([(x_ngoai, y_t - 0.55 * d.h, z), (x_ngoai, y_t, z), (x_xa, y_t, z)], d_c)
        d_b = max(d.bot) if d.bot else 16
        zb = _dem_hang_z(max(len(d.bot), 2), d.b, cv_d, dw, d_b)
        y_b = -d.h + cv_d + dw + d_b / 2
        for z in zb:
            doan_t((-huong * (wc / 2 - cv_c) if not co_doi_dien else 0.0, y_b, z), (x_xa, y_b, z), zb[-1])
        return suot, d_c, d_b, zt, zb, y_t, y_b, x_xa, sv

    kq_p = ve_dam(dam_phai, +1) if dam_phai else None
    kq_t = ve_dam(dam_trai, -1) if dam_trai else None

    # ---- nhãn ----
    so_h, n_tong, _ = kh.thanh_doc_cot[cot.ten]
    tam0 = pos[0][0]
    nhan.them(P(tam0.x - wc / 2, -h_dam - 1.7 * BUOC_DAI_COT_SO_DO, tam0.y - dc / 2), so_h, f"{n_tong}Ø{d_cot}", -1)
    sh_dai = cot.nhan_dai[-1][0] if cot.nhan_dai else 0
    if cot.vung:
        nhan.them(P(x1, ys_dai_cot[1], z0), sh_dai, cot.vung[-1].nhan(), +1)
    for kq, huong, dam in ((kq_p, +1, dam_phai), (kq_t, -1, dam_trai)):
        if not kq:
            continue
        suot, d_c, d_b, zt, zb, y_t, y_b, x_xa, sv = kq
        tl = kh.thanh_doc_dam[dam.ten]
        ben = 1 if huong > 0 else -1
        if suot:
            nhan.them(P(huong * (wc / 2 + L_dam * 0.62), y_t, zt[-1]), suot.so_hieu, f"{suot.so_luong}Ø{suot.duong_kinh}", ben)
        for dk, lst in dam._so_ben["trai" if huong > 0 else "phai"].items():  # type: ignore[attr-defined]
            for n, th in lst:
                nhan.them(P(huong * (wc / 2 + L_dam * 0.3), y_t - 60.0, zt[len(zt) // 2]), th.so_hieu, f"{n}Ø{dk}", ben)
        th_b = next((t for t in tl if t.vai_tro == "duoi"), None)
        if th_b:
            nhan.them(P(huong * (wc / 2 + L_dam * 0.45), y_b, zb[0]), th_b.so_hieu, f"{th_b.so_luong}Ø{th_b.duong_kinh}", ben)
        dz = kh.dai_dam[dam.ten][0]
        nhan.them(P(huong * (wc / 2 + 110.0 + 3 * sv), -dam.h + cv_d, dam.b / 2 - cv_d), dz.so_hieu, f"Ø{dz.duong_kinh}a{dz.buoc:g}", ben)

    bx0, by0, bx1, by1 = v.bao()
    nhan.ve(v, bx0, bx1)
    bx0, by0, bx1, by2 = v.bao()
    # ---- tên ----
    v.chu((bx0 + bx1) / 2, by0 - 2.2 * v.h_chu, f"CHI TIẾT {ten}", v.h_chu * 1.6, giua=True)
    x0b, x1b, y0b, y1b = bx0 - 200.0, bx1 + 200.0, by0 - 4.4 * v.h_chu, by2 + 200.0
    return v, x1b - x0b, y1b - y0b, (x0b, y0b)
