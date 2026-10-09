"""Vẽ MẶT ĐỨNG khung bố trí thép theo bản vẽ mẫu: cột + dầm treo dưới cốt sàn, thép dọc, đai theo vùng, móng + thép chờ,
COS, kích thước, số hiệu thanh, ký hiệu mặt cắt. Toạ độ cục bộ: trục đầu tiên x=0; y = cao độ ETABS (Mong = 0 = đỉnh móng).
"""

from __future__ import annotations

import math

from .. import layers
from ...rule_engine import bo_tri_dai as dai
from .co_so import _Cot, _Dam, _Ve, _ten_tang
from .ke_hoach import KeHoach

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_OUT = layers.OUTLINE.ten
L_AXIS = layers.AXIS.ten
L_DIM = layers.DIM.ten


def _the(v: _Ve, x_tro, y_tro, x_the, y_the, so, noi_dung, huong=1):
    """Số hiệu: đường dẫn kết thúc ở MÉP vòng tròn (không xuyên vào chữ)."""
    r = v.r_the
    dx, dy = x_the - x_tro, y_the - y_tro
    d = math.hypot(dx, dy) or 1.0
    xe, ye = x_the - dx / d * r, y_the - dy / d * r
    v.doan(x_tro, y_tro, xe, ye, layers.SO_HIEU.ten)
    v.tron(x_the, y_the, r, layers.SO_HIEU.ten)
    v.chu(x_the, y_the, str(so), v.h_chu, layers.SO_HIEU.ten, giua=True)
    if noi_dung:
        if huong >= 0:
            v.chu(x_the + r + 0.5 * v.h_chu_nho, y_the, noi_dung, v.h_chu)
        else:
            v.chu(x_the - r - 0.5 * v.h_chu_nho, y_the, noi_dung, v.h_chu, phai=True)


def _vach_mat_cat(v: _Ve, x, y, so, huong=1):
    """Ký hiệu mặt cắt trên mặt đứng: số + vạch đậm đứng (bản mẫu: '7 ▌')."""
    h = 1.6 * v.cfg.ty_le * 2.4
    v.doan_net_dam(x, y - h / 2, y + h / 2, 0.9 * v.cfg.ty_le)
    # số đặt cách vạch: nửa bề rộng chữ + khe (không chồng lên vạch — bản mẫu: "7 ▌")
    nua = 0.5 * len(str(so)) * 0.62 * v.h_chu * 1.25 + 0.9 * v.cfg.ty_le * 1.2
    v.chu(x + (nua if huong >= 0 else -nua), y, str(so), v.h_chu * 1.25, giua=True)


class _Cho:
    """Bộ đặt nhãn: giữ danh sách hộp đã chiếm; `dat` thử các độ lệch dọc cho tới khi hết chồng (nếu hết cách thì vẽ
    ở vị trí gốc và đếm vào `loi_chong`). Hộp ước lượng theo bề rộng chữ ≈ 0,6 × chiều cao × số ký tự."""

    LE = 40.0

    def __init__(self, v: _Ve):
        self.v = v
        self.hop: list[tuple[float, float, float, float]] = []
        self.loi_chong = 0

    def vat_can(self, x0, y0, x1, y1):
        self.hop.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def hop_the(self, x, y, noi_dung, huong):
        v = self.v
        r = v.r_the
        w = len(noi_dung) * 0.6 * v.h_chu if noi_dung else 0.0
        if huong >= 0:
            return (x - r, y - r, x + r + 0.5 * v.h_chu_nho + w, y + r)
        return (x - r - 0.5 * v.h_chu_nho - w, y - r, x + r, y + r)

    def trong(self, b):
        le = self.LE
        for (a0, b0, a1, b1) in self.hop:
            if b[0] < a1 + le and b[2] > a0 - le and b[1] < b1 + le and b[3] > b0 - le:
                return False
        return True

    def dat(self, xa, ya, x, y, so, noi_dung, huong=1, dys=(0.0,), dxs=(0.0, 300.0, -300.0, 600.0, -600.0)) -> bool:
        for dy in dys:
            for dx in dxs:
                b = self.hop_the(x + dx, y + dy, noi_dung, huong)
                if self.trong(b):
                    _the(self.v, xa, ya, x + dx, y + dy, so, noi_dung, huong)
                    self.hop.append(b)
                    return True
        b = self.hop_the(x, y, noi_dung, huong)
        _the(self.v, xa, ya, x, y, so, noi_dung, huong)
        self.hop.append(b)
        self.loi_chong += 1
        return False

    def vach(self, v: _Ve, x, y, so, huong=1, dys=(0.0,), dxs=(0.0,), bat_buoc=True) -> bool:
        w = 0.9 * v.cfg.ty_le * 2.4 + len(str(so)) * 0.7 * v.h_chu * 1.25
        for dy in dys:
            for dx in dxs:
                xx = x + dx
                b = (xx - 60, y + dy - 130, xx + w, y + dy + 130) if huong >= 0 else (xx - w, y + dy - 130, xx + 60, y + dy + 130)
                if self.trong(b):
                    _vach_mat_cat(v, xx, y + dy, so, huong)
                    self.hop.append(b)
                    return True
        if not bat_buoc:
            return False
        _vach_mat_cat(v, x, y, so, huong)
        self.loi_chong += 1
        return False


def ve_mat_dung(kh: KeHoach, v: _Ve) -> dict:
    """Vẽ vào `v`; trả {"so_vong_tron_so_hieu": n} để kiểm chứng đếm ký hiệu."""
    cfg = kh.cfg
    T = cfg.ty_le
    cv_d, cv_c = cfg.lop_bao_ve_dam, cfg.lop_bao_ve_cot
    truc = kh.truc
    moc = kh.moc
    ten_truc = sorted(truc, key=lambda k: truc[k])
    x_min, x_max = truc[ten_truc[0]], truc[ten_truc[-1]]
    y_ton_nen = cfg.cao_do_ton_nen_tren_dinh_mong
    y_tu_nhien = y_ton_nen - cfg.cao_do_tu_nhien_duoi_ton_nen
    y_dai = -cfg.day_dai_mong
    y_lot = y_dai - cfg.day_lot
    cos = lambda y: y - y_ton_nen  # noqa: E731
    cac_moc = sorted(moc.items(), key=lambda kv: kv[1])
    y_top = cac_moc[-1][1]
    rong_cot_cuoi = max((c.h for c in kh.cots if c.truc == ten_truc[-1]), default=300.0)
    rong_cot_dau = max((c.h for c in kh.cots if c.truc == ten_truc[0]), default=300.0)
    x_trai_cuoi, x_phai_cuoi = x_min - rong_cot_dau / 2 - 2600.0, x_max + rong_cot_cuoi / 2 + 5600.0
    n_so_hieu = 0

    # ---- 1. đường mốc cao độ (nét chấm gạch) + nhãn bên phải ----
    x_nhan = x_max + rong_cot_cuoi / 2 + 3300.0
    for ten, y in cac_moc:
        if ten.lower().startswith("mong"):
            continue
        v.doan(x_trai_cuoi + 300, y, x_phai_cuoi, y, L_AXIS)
        v.chu(x_nhan, y + 80, _ten_tang(ten), v.h_chu)
        v.tam_giac_cao_do(x_nhan + 1800, y)
        v.chu(x_nhan + 1800 + 260, y + 80, f"{cos(y) / 1000:+.3f}", v.h_chu)
    for y, ten in ((y_ton_nen, "COS TÔN NỀN"), (y_tu_nhien, "COS TỰ NHIÊN"), (0.0, "COS ĐỈNH MÓNG")):
        v.doan(x_trai_cuoi + 300, y, x_phai_cuoi, y, L_AXIS)
        v.chu(x_nhan, y + 80, ten, v.h_chu)

    # ---- 2. móng ----
    for t in ten_truc:
        w = kh.be_rong_dai.get(t)
        if not w:
            continue
        xc = truc[t]
        v.hcn(xc - w / 2, y_dai, xc + w / 2, 0.0, L_OUT)  # đài
        v.hcn(xc - w / 2 - cfg.day_lot, y_lot, xc + w / 2 + cfg.day_lot, y_dai, L_OUT)  # bê tông lót
        # lưới thép đáy: 1 nét + chấm
        y_l = y_dai + 70.0
        v.doan(xc - w / 2 + 60, y_l, xc + w / 2 - 60, y_l, L_REBAR)
        n = int((w - 200) // 150)
        for i in range(n + 1):
            v.tron(xc - (n * 150) / 2 + i * 150, y_l + 35, 18, L_REBAR)
        v.doan(xc, y_lot - 300, xc, y_top + 2400, L_AXIS)  # tim trục (kéo suốt)

    # ---- 3. cột ----
    for c in kh.cots:
        xc = truc[c.truc]
        x0, x1 = xc - c.h / 2, xc + c.h / 2
        la_t1 = abs(c.y0) < 1.0
        yb = y_dai if la_t1 else c.y0
        v.doan(x0, yb, x0, c.y1, L_OUT)
        v.doan(x1, yb, x1, c.y1, L_OUT)
        if abs(c.y1 - y_top) < 1.0:
            v.doan(x0, c.y1, x1, c.y1, L_OUT)
        dw = c.vung[0].duong_kinh if c.vung else 6
        xn, xf = x0 + cv_c + dw + c.d / 2, x1 - cv_c - dw - c.d / 2
        # thép dọc (2 mặt cạnh)
        y_dau_thanh = (y_dai + 75.0) if la_t1 else c.y0
        v.doan(xn, y_dau_thanh, xn, c.y1, L_REBAR)
        v.doan(xf, y_dau_thanh, xf, c.y1, L_REBAR)
        if la_t1:  # thép chờ bẻ L ra hai phía
            v.doan(xn, y_dau_thanh, xn - 200, y_dau_thanh, L_REBAR)
            v.doan(xf, y_dau_thanh, xf + 200, y_dau_thanh, L_REBAR)
        # đai theo vùng
        for y in dai.vi_tri_dai(c.vung):
            v.doan(x0 + cv_c, c.y0 + y, x1 - cv_c, c.y0 + y, L_DAI)
        if la_t1:  # 3 đai trong đài
            for i in range(3):
                v.doan(x0 + cv_c, -100.0 - i * 120.0, x1 - cv_c, -100.0 - i * 120.0, L_DAI)

    # nối cạnh đứng khi tiết diện đổi giữa các tầng
    for t in ten_truc:
        seg = sorted((c for c in kh.cots if c.truc == t), key=lambda c: c.y0)
        for a, b in zip(seg, seg[1:]):
            if abs(a.h - b.h) > 1.0:
                xc = truc[t]
                v.doan(xc - a.h / 2, a.y1, xc - b.h / 2, a.y1, L_OUT)
                v.doan(xc + a.h / 2, a.y1, xc + b.h / 2, a.y1, L_OUT)

    # ---- 4. dầm ----
    def cos_dam_tren(d: _Dam) -> float:
        return d.y

    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        yt, yb = d.y, d.y - d.h
        v.hcn(xf1, yb, xf2, yt, L_OUT)
        dw = d.vung[0].duong_kinh
        # thanh dưới
        if d.bot:
            dd = max(d.bot)
            y_d = yb + cv_d + dw + dd / 2
            ke_t = any(abs(k.x2 - d.x1) < 1 and k.tang == d.tang for k in kh.dams if k is not d)
            ke_p = any(abs(k.x1 - d.x2) < 1 and k.tang == d.tang for k in kh.dams if k is not d)
            l_hook = max(100.0, min(max(15.0 * dd, 250.0), d.h - 2 * cv_d - 50.0))
            xs = d.x1 if ke_t else d.x1 - d.hc1 / 2 + cv_d
            xe = d.x2 if ke_p else d.x2 + d.hc2 / 2 - cv_d
            pts = []
            if not ke_t:
                pts.append((xs, y_d + l_hook))
            pts += [(xs, y_d), (xe, y_d)]
            if not ke_p:
                pts.append((xe, y_d + l_hook))
            v.duong(pts, L_REBAR)
        # đai
        for pos in dai.vi_tri_dai(d.vung):
            v.doan(xf1 + pos, yb + cv_d, xf1 + pos, yt - cv_d, L_DAI)

    # thanh trên suốt + gia cường — theo từng dầm
    da_ve_suot: set[tuple[str, float]] = set()
    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        yt = d.y
        dw = d.vung[0].duong_kinh
        tl = kh.thanh_doc_dam[d.ten]
        ke_t = next((k for k in kh.dams if abs(k.x2 - d.x1) < 1 and k.tang == d.tang and k is not d), None)
        ke_p = next((k for k in kh.dams if abs(k.x1 - d.x2) < 1 and k.tang == d.tang and k is not d), None)
        suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        d_c = suot.duong_kinh if suot else 16
        y_suot = yt - cv_d - dw - d_c / 2
        y_ex = y_suot - 60.0
        l_hook = max(100.0, min(max(15.0 * d_c, 250.0), d.h - 2 * cv_d - 50.0))
        if suot and suot.vai_tro == "tren_suot":  # vẽ 1 lần cho cả chuỗi
            chuoi = [d]
            while True:
                nx = next((k for k in kh.dams if abs(k.x1 - chuoi[-1].x2) < 1 and k.tang == d.tang and k not in chuoi), None)
                if nx is None:
                    break
                chuoi.append(nx)
            xs = chuoi[0].x1 - chuoi[0].hc1 / 2 + cv_d
            xe = chuoi[-1].x2 + chuoi[-1].hc2 / 2 - cv_d
            h_min = min(k.h for k in chuoi)
            lh = min(max(15.0 * d_c, 250.0), h_min - 2 * cv_d - 50.0)
            v.duong([(xs, y_suot - lh), (xs, y_suot), (xe, y_suot), (xe, y_suot - lh)], L_REBAR)
        # thanh gia cường: vẽ theo nhóm trong d._so_ben
        for ben in ("trai", "phai"):
            for dk, lst in d._so_ben[ben].items():  # type: ignore[attr-defined]
                for n, th in lst:
                    if th.vai_tro == "tren_cat_nut":
                        if ben == "phai":
                            continue  # vẽ 1 lần ở dầm bên phải của nút
                        kt_ = ke_t
                        xa = (kt_.x2 - kt_.hc2 / 2 - kt_._x_cat) if kt_ else xf1 - d._x_cat  # type: ignore[attr-defined]
                        xb = xf1 + d._x_cat  # type: ignore[attr-defined]
                        v.doan(xa, y_ex, xb, y_ex, L_REBAR)
                    elif ben == "trai":
                        if ke_t is None:
                            xo = d.x1 - d.hc1 / 2 + cv_d
                            v.duong([(xo, y_ex - l_hook), (xo, y_ex), (xf1 + d._x_cat, y_ex)], L_REBAR)  # type: ignore[attr-defined]
                        else:
                            v.doan(xf1 + d._x_cat, y_ex, d.x1 - d.hc1 / 2 + 0, y_ex, L_REBAR)  # type: ignore[attr-defined]
                            v.doan(d.x1 - d.hc1 / 2, y_ex, d.x1 + d.hc1 / 2 + 20 * dk, y_ex, L_REBAR)
                    else:
                        if ke_p is None:
                            xo = d.x2 + d.hc2 / 2 - cv_d
                            v.duong([(xo, y_ex - l_hook), (xo, y_ex), (xf2 - d._x_cat, y_ex)], L_REBAR)  # type: ignore[attr-defined]
                        else:
                            v.doan(xf2 - d._x_cat, y_ex, d.x2 + d.hc2 / 2 + 20 * dk, y_ex, L_REBAR)  # type: ignore[attr-defined]

    # ---- 5. nhãn (bộ đặt nhãn tránh chồng) ----
    cho = _Cho(v)
    for c in kh.cots:  # vật cản: thân cột
        xc = truc[c.truc]
        cho.vat_can(xc - c.h / 2, c.y0, xc + c.h / 2, c.y1)
    for d in kh.dams:  # vật cản: thân dầm (nhãn đặt NGOÀI dầm)
        cho.vat_can(d.x1 + d.hc1 / 2, d.y - d.h, d.x2 - d.hc2 / 2, d.y)
    for t_ in ten_truc:
        w = kh.be_rong_dai.get(t_)
        if w:
            cho.vat_can(truc[t_] - w / 2 - 100, y_lot, truc[t_] + w / 2 + 100, 0.0)

    HA, HB, HC, HD = 450.0, 950.0, 1500.0, 1950.0
    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        yt, yb = d.y, d.y - d.h
        xm = (xf1 + xf2) / 2
        tl = kh.thanh_doc_dam[d.ten]
        dw = d.vung[0].duong_kinh
        suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        d_c = suot.duong_kinh if suot else 16
        y_suot = yt - cv_d - dw - d_c / 2
        # hàng A: thanh trên suốt (giữa nhịp) + gia cường (gần gối)
        if suot:
            if cho.dat(xm, y_suot, xm, yt + HA, suot.so_hieu, f"{suot.so_luong}Ø{suot.duong_kinh}", 1, dys=(0, 420, -0.0)):
                pass
            n_so_hieu += 1
        for ben, fx in (("trai", 0.2), ("phai", 0.8)):
            xa = xf1 + fx * d.l_tt
            for dk, lst in sorted(d._so_ben[ben].items(), reverse=True):  # type: ignore[attr-defined]
                for n, th in lst:
                    cho.dat(xa, y_suot - 60.0, xa, yt + HA, th.so_hieu, f"{n}Ø{dk}", 1 if ben == "trai" else -1,
                            dys=(0, 420, 840), dxs=(0.0,))
                    n_so_hieu += 1
        # thanh dưới: tag treo dưới dầm
        if d.bot:
            dd = max(d.bot)
            y_d = yb + cv_d + dw + dd / 2
            for i, (dk, n) in enumerate(sorted({k: d.bot.count(k) for k in set(d.bot)}.items(), reverse=True)):
                th = next(t for t in tl if t.vai_tro == "duoi" and t.duong_kinh == dk)
                x_bd = min(max(xm - 700.0, xf1 + 400.0), xf2 - 1100.0) if d.l_tt > 2500 else xm - 250.0
                cho.dat(x_bd, y_d, x_bd, yb - HA - i * 420.0, th.so_hieu, f"{n}Ø{dk}", 1, dys=(0, -420, -840))
                n_so_hieu += 1
        # đai: tag theo vùng (hàng B) + dây kích thước vùng (hàng C)
        yC = yt + HC
        kh_dai = kh.dai_dam[d.ten]
        da_tag: set[int] = set()
        for i, (vg, th_dai) in enumerate(zip(d.vung, kh_dai)):
            xa, xb = xf1 + vg.tu_mm, xf1 + vg.den_mm
            xt = (xa + xb) / 2
            if th_dai.so_hieu not in da_tag or len(d.vung) == 1:
                cho.dat(xt, yt - cv_d, xt - 350.0, yt + HB, th_dai.so_hieu, vg.nhan(), 1, dys=(0, 0.0), dxs=(0, 500.0, -500.0))
                n_so_hieu += 1
                da_tag.add(th_dai.so_hieu)
            v.kt((xa, yC), (xb, yC), f"{vg.chieu_dai:g}({vg.nhan()})", L_DIM)
            v.doan(xa, yC - 110, xa, yC + 110, L_DIM)
            v.doan(xb, yC - 110, xb, yC + 110, L_DIM)
            cho.vat_can(xa, yC - 60, xb, yC + 330)
        # ký hiệu mặt cắt (hàng D)
        for ben, xs_ in (("trai", xf1 + 0.08 * d.l_tt), ("giua", xm + 900.0), ("phai", xf2 - 0.08 * d.l_tt)):
            so = kh.gan_mat_cat_dam[(d.ten, ben)]
            cho.vach(v, xs_, yt + HD, so, huong=1, dys=(0, 250, -250))

    # ---- 6. nhãn cột (quét tìm chỗ trống theo chiều cao) ----
    for c in kh.cots:
        xc = truc[c.truc]
        x0, x1 = xc - c.h / 2, xc + c.h / 2
        trai = c.truc != ten_truc[-1]
        dw = c.vung[0].duong_kinh
        xn, xf = x0 + cv_c + dw + c.d / 2, x1 - cv_c - dw - c.d / 2
        so_h, n_tong, _ = kh.thanh_doc_cot[c.ten]
        hb = max([d.h for d in kh.dams if abs(d.y - c.y1) < 1.0 and c.truc in (d.truc1, d.truc2)] or [0.0])
        ymid = c.y0 + (c.y1 - c.y0) * 0.5
        y_lo, y_hi = c.y0 + 250.0, c.y1 - hb - 250.0
        quet = [0.0]
        for k in range(1, 12):
            quet += [k * 300.0, -k * 300.0]

        def dat_cot(y_neo, so, noi_dung):
            """Thử bên ưu tiên rồi bên kia, quét theo chiều cao quanh y_neo."""
            nonlocal n_so_hieu
            for cho_trai in (trai, not trai):
                x_bar = (xn if cho_trai else xf) if noi_dung.startswith(f"{n_tong}Ø") else (x0 + cv_c if cho_trai else x1 - cv_c)
                x_tag = (x0 - 500.0) if cho_trai else (x1 + 500.0)
                for dy in quet:
                    y_ = y_neo + dy
                    if y_ < y_lo or y_ > y_hi:
                        continue
                    b = cho.hop_the(x_tag, y_, noi_dung, -1 if cho_trai else 1)
                    if cho.trong(b):
                        _the(v, x_bar, y_neo, x_tag, y_, so, noi_dung, -1 if cho_trai else 1)
                        cho.hop.append(b)
                        n_so_hieu += 1
                        return True
            cho.loi_chong += 1
            return False

        dat_cot(ymid, so_h, f"{n_tong}Ø{c.d}")
        da_tag_ = set()
        for i, vg in enumerate(c.vung):
            if i == len(c.vung) - 1 and hb:
                continue  # vùng nút: cùng bước đầu cột, không tag riêng
            sh, nhan = c.nhan_dai[i]
            if sh in da_tag_:
                continue
            da_tag_.add(sh)
            y_t = c.y0 + (vg.tu_mm + vg.den_mm) / 2
            dat_cot(y_t, sh, nhan)
        da_vach: set[int] = set()
        for i, vg in enumerate(c.vung):
            if i == len(c.vung) - 1 and hb:
                continue
            so_mc = kh.gan_mat_cat_cot.get((c.ten, i))
            if so_mc is None or so_mc in da_vach:
                continue
            da_vach.add(so_mc)
            y_t = c.y0 + (vg.tu_mm + vg.den_mm) / 2
            xs_ = (x0 - 350.0) if (c.truc == ten_truc[1] and len(ten_truc) > 2 and c.truc != ten_truc[-1]) else (x1 + 350.0)
            ok = False
            huong_v = -1 if xs_ < xc else 1
            for dy in quet:
                yy = y_t + dy
                if yy < y_lo or yy > y_hi:
                    continue
                if cho.vach(v, xs_, yy, so_mc, huong=huong_v, bat_buoc=False):
                    ok = True
                    break
            if not ok:
                cho.vach(v, xs_, y_t, so_mc, huong=huong_v)

    # ---- 7. kích thước chân + trục + chiều cao ----
    y_k1, y_k2 = y_lot - 700.0, y_lot - 1250.0
    for a, b in zip(ten_truc, ten_truc[1:]):
        v.kt((truc[a], y_k1), (truc[b], y_k1), f"{truc[b] - truc[a]:g}", L_AXIS)
        v.doan(truc[a], y_lot - 300, truc[a], y_k1 + 80, L_DIM)
    v.doan(truc[ten_truc[-1]], y_lot - 300, truc[ten_truc[-1]], y_k1 + 80, L_DIM)
    if len(ten_truc) >= 2:
        v.kt((x_min, y_k2), (x_max, y_k2), f"{x_max - x_min:g}", L_AXIS)
        v.doan(x_min, y_k1, x_min, y_k2 + 80, L_DIM)
        v.doan(x_max, y_k1, x_max, y_k2 + 80, L_DIM)
    for t in ten_truc:
        v.bong_bong_truc(truc[t], y_k2 - 900.0, t)
        v.doan(truc[t], y_k2 - 450.0 + 80, truc[t], y_k2 - 0, L_AXIS)

    xc_cuoi = truc[ten_truc[-1]]
    x_d1, x_d2 = xc_cuoi + rong_cot_cuoi / 2 + 1900.0, xc_cuoi + rong_cot_cuoi / 2 + 2600.0
    mc = [(0.0, "dinh")] + [(y, n) for n, y in cac_moc if not n.lower().startswith("mong")]
    ys = sorted({0.0, y_tu_nhien, y_ton_nen} | {y for _, y in cac_moc})
    for a, b in zip(ys, ys[1:]):
        v.kt((x_d2, a), (x_d2, b), f"{b - a:g}", L_AXIS)
        v.doan(xc_cuoi + rong_cot_cuoi / 2 + 100, a, x_d2 + 120, a, L_DIM)
    v.doan(xc_cuoi + rong_cot_cuoi / 2 + 100, ys[-1], x_d2 + 120, ys[-1], L_DIM)
    v.kt((x_d2 + 700, 0.0), (x_d2 + 700, y_ton_nen), f"{y_ton_nen:g}", L_AXIS)
    # chiều cao thông thuỷ: sàn → đáy dầm tầng trên (theo dầm tại trục cuối)
    for (n1, y1), (n2, y2) in zip(cac_moc, cac_moc[1:]):
        if n1.lower().startswith("mong"):
            continue
        hb = max([d.h for d in kh.dams if abs(d.y - y2) < 1.0 and ten_truc[-1] in (d.truc1, d.truc2)] or [0.0])
        if hb:
            v.kt((x_d1, y1), (x_d1, y2 - hb), f"{y2 - hb - y1:g}", L_AXIS)
            v.kt((x_d1, y2 - hb), (x_d1, y2), f"{hb:g}", L_AXIS)
            v.doan(xc_cuoi + rong_cot_cuoi / 2 + 100, y2 - hb, x_d1 + 120, y2 - hb, L_DIM)

    # tên bản vẽ
    v.chu((x_min + x_max) / 2, y_k2 - 2500.0, f"BỐ TRÍ THÉP KHUNG TRỤC {cfg.ten_khung_truc}".strip(), v.h_chu * 1.8, giua=True)
    return {"so_vong_tron_so_hieu": n_so_hieu, "loi_chong_nhan": cho.loi_chong, "x_trai": x_trai_cuoi, "x_phai": x_phai_cuoi, "y_thap": y_k2 - 3200.0,
            "y_cao": y_top + 2600.0}
