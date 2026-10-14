"""Vẽ MẶT ĐỨNG khung bố trí thép theo bản vẽ mẫu: cột + dầm treo dưới cốt sàn, thép dọc, đai theo vùng, móng + thép chờ,
COS, kích thước, số hiệu thanh, ký hiệu mặt cắt. Toạ độ cục bộ: trục đầu tiên x=0; y = cao độ ETABS (Mong = 0 = đỉnh móng).
"""

from __future__ import annotations

import math

from .. import layers
from ...rule_engine import bo_tri_dai as dai
from .co_so import _Cot, _Dam, _Ve, _ten_tang
from . import chi_tiet_thep as ct
from . import nhan
from .ke_hoach import KeHoach

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_OUT = layers.OUTLINE.ten
L_AXIS = layers.AXIS.ten
L_DIM = layers.DIM.ten


def _thanh_cot(kh: KeHoach, v: _Ve, c, xn: float, xf: float, la_t1: bool, la_mai: bool, y_chan_l: float) -> None:
    """Hai thanh dọc cột nhìn thấy trên mặt đứng (mặt trái xn, mặt phải xf), hai nét song song, góc uốn bo cung.

    Tầng 1: thép chờ xuống sát lưới đáy rồi uốn chữ L RA NGOÀI (đoạn ngang nằm trên lưới, không trùng nét lưới).
    Tầng mái: mọi thanh uốn ngang vào dầm (đoạn `c._l_vao`): nút biên — thanh phía NGOÀI bẻ cao (phía trên thanh trên dầm,
    cung ngoài), thanh phía trong bẻ thấp hơn; nút giữa — mỗi mặt bẻ về dầm phía mình, dưới thanh trên dầm chạy suốt.
    Tầng giữa: thanh chạy suốt qua nút (thanh trên dầm biên uốn xuống nằm TRONG thanh cột)."""
    cfg = kh.cfg
    cv_d = cfg.lop_bao_ve_dam
    ke = [d for d in kh.dams if abs(d.y - c.y1) < 1.0 and c.truc in (d.truc1, d.truc2)]
    d_b = max([d._chuoi["d"] for d in ke if d._chuoi["d"]] or [16])  # type: ignore[attr-defined]
    dw_b = max([d.vung[0].duong_kinh for d in ke if d.vung] or [6])
    y_thanh_dam = c.y1 - cv_d - dw_b - d_b / 2.0  # tim thanh trên dầm
    y_leg_cao = c.y1 - cv_d - c.d / 2.0  # thanh cột phía ngoài (trên thanh dầm)
    y_leg_thap = y_thanh_dam - d_b / 2.0 - 3.0 - c.d / 2.0  # dưới thanh trên dầm
    huong = getattr(c, "_huong_uon", (0, 0)) if la_mai else (0, 0)
    l_vao = getattr(c, "_l_vao", 0.0)
    ngoai = 0 if huong == (1, 1) else 1 if huong == (-1, -1) else None  # thanh phía NGOÀI ở nút biên
    for mat, x, ra in ((0, xn, -1), (1, xf, 1)):
        hu = huong[mat]
        pts = [(x + ra * ct.CHAN_L_NGANG, y_chan_l), (x, y_chan_l)] if la_t1 else [(x, c.y0)]
        if hu:
            y_leg = y_leg_cao if ngoai == mat else y_leg_thap
            pts += [(x, y_leg), (x + hu * l_vao, y_leg)]
        else:
            pts.append((x, c.y1 - (40.0 if la_mai else 0.0)))
        v.thanh(pts, c.d)


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

    # ---- 2. móng: đài + lót + lưới thép đáy (thanh ngang hai nét; hàng chấm tiết diện thanh vuông góc nằm TRÊN lưới) ----
    y_chan_l = y_dai + ct.CAO_CHAN_L  # tim đoạn ngang chân L thép chờ — CAO HƠN lưới đáy, không trùng nét
    for t in ten_truc:
        w = kh.be_rong_dai.get(t)
        if not w:
            continue
        xc = truc[t]
        v.hcn(xc - w / 2, y_dai, xc + w / 2, 0.0, L_OUT)  # đài
        v.hcn(xc - w / 2 - cfg.day_lot, y_lot, xc + w / 2 + cfg.day_lot, y_dai, L_OUT)  # bê tông lót
        v.thanh([(xc - w / 2 + 60, y_dai + ct.CAO_LUOI_DAY), (xc + w / 2 - 60, y_dai + ct.CAO_LUOI_DAY)], ct.D_LUOI)
        n = int((w - 200) // 150)
        for i in range(n + 1):
            v.tron(xc - (n * 150) / 2 + i * 150, y_dai + 90.0, ct.D_LUOI / 2, L_REBAR)
        v.doan(xc, y_lot - 300, xc, y_top + 2400, L_AXIS)  # tim trục (kéo suốt)

    # ---- 3. cột ----
    for c in kh.cots:
        xc = truc[c.truc]
        x0, x1 = xc - c.h / 2, xc + c.h / 2
        la_t1 = abs(c.y0) < 1.0
        la_mai = abs(c.y1 - y_top) < 1.0
        yb = c.y0  # đường bao cột dừng ở mặt trên đài (bản mẫu); trong đài chỉ có thép chờ + đai, không có bao bê tông cột
        v.doan(x0, yb, x0, c.y1, L_OUT)
        v.doan(x1, yb, x1, c.y1, L_OUT)
        if la_mai:
            v.doan(x0, c.y1, x1, c.y1, L_OUT)
        dw = c.vung[0].duong_kinh if c.vung else 6
        xn, xf = x0 + cv_c + dw + c.d / 2, x1 - cv_c - dw - c.d / 2
        _thanh_cot(kh, v, c, xn, xf, la_t1, la_mai, y_chan_l)
        # đai theo vùng: nét ĐẬM + chấm tiết diện thanh dọc ở hai đầu + vạch móc ngắn luân phiên hai bên
        for k, y in enumerate(dai.vi_tri_dai(c.vung)):
            ya = c.y0 + y
            v.doan(x0 + cv_c, ya, x1 - cv_c, ya, L_DAI)
            xm = x0 + cv_c if k % 2 == 0 else x1 - cv_c
            v.doan(xm, ya, xm, ya - 6 * dw, L_DAI)
        if la_t1:  # 3 đai trong đài
            for i in range(3):
                v.doan(x0 + cv_c, -100.0 - i * 75.0, x1 - cv_c, -100.0 - i * 75.0, L_DAI)  # không chạm chân L ở y_chan_l

    # nối cạnh đứng khi tiết diện đổi giữa các tầng
    for t in ten_truc:
        seg = sorted((c for c in kh.cots if c.truc == t), key=lambda c: c.y0)
        for a, b in zip(seg, seg[1:]):
            if abs(a.h - b.h) > 1.0:
                xc = truc[t]
                v.doan(xc - a.h / 2, a.y1, xc - b.h / 2, a.y1, L_OUT)
                v.doan(xc + a.h / 2, a.y1, xc + b.h / 2, a.y1, L_OUT)

    # ---- 4. dầm ----
    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        yt, yb = d.y, d.y - d.h
        v.hcn(xf1, yb, xf2, yt, L_OUT)
        dw = d.vung[0].duong_kinh
        ch = d._chuoi  # type: ignore[attr-defined]
        d_c = ch["d"] or (max(d.top_l + d.top_r) if (d.top_l or d.top_r) else 16)
        y_suot = yt - cv_d - dw - d_c / 2  # tim thanh trên chạy suốt
        dd = max(d.bot) if d.bot else 0
        y_d = yb + cv_d + dw + dd / 2  # tim thanh dưới
        ke_t = any(abs(k.x2 - d.x1) < 1 and k.tang == d.tang for k in kh.dams if k is not d)
        ke_p = any(abs(k.x1 - d.x2) < 1 and k.tang == d.tang for k in kh.dams if k is not d)
        if d.bot:  # thanh dưới: THẲNG (không móc), hai nét; biên tới mặt ngoài cột − lớp bảo vệ, giữa tới tim cột
            xs = d.x1 if ke_t else d.x1 - d.hc1 / 2 + cv_d
            xe = d.x2 if ke_p else d.x2 + d.hc2 / 2 - cv_d
            v.thanh([(xs, y_d), (xe, y_d)], dd)
        # đai: nét ĐẬM + chấm tiết diện thanh trên/dưới ở hai đầu
        for pos in dai.vi_tri_dai(d.vung):
            xd = xf1 + pos
            v.doan(xd, yb + cv_d, xd, yt - cv_d, L_DAI)

    # thanh trên suốt + gia cường — theo từng dầm
    for d in kh.dams:
        xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
        yt = d.y
        dw = d.vung[0].duong_kinh
        tl = kh.thanh_doc_dam[d.ten]
        ch = d._chuoi  # type: ignore[attr-defined]
        ke_t = next((k for k in kh.dams if abs(k.x2 - d.x1) < 1 and k.tang == d.tang and k is not d), None)
        ke_p = next((k for k in kh.dams if abs(k.x1 - d.x2) < 1 and k.tang == d.tang and k is not d), None)
        suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        d_c = suot.duong_kinh if suot else 16
        y_suot = yt - cv_d - dw - d_c / 2
        y_ex = y_suot - 60.0
        if suot and suot.vai_tro == "tren_suot":  # vẽ 1 lần cho cả chuỗi: chạy suốt, uốn xuống cột ở hai đầu biên (bo cung)
            v.thanh([(ch["x_tr"], y_suot - ch["l_tr"]), (ch["x_tr"], y_suot), (ch["x_ph"], y_suot),
                     (ch["x_ph"], y_suot - ch["l_ph"])], d_c)
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
                        v.thanh([(xa, y_ex), (xb, y_ex)], dk)
                    elif ben == "trai":
                        if ke_t is None:  # biên: uốn xuống cột (nằm trong thanh suốt), rồi chạy tới L/4 thông thuỷ
                            xl = ch["x_tr0"] + ch["d"] + dk / 2 + (1.0 if ch["d"] else 0.0)
                            v.thanh([(xl, y_ex - ch["l_tr"]), (xl, y_ex), (xf1 + d._x_cat, y_ex)], dk)  # type: ignore[attr-defined]
                        else:
                            v.thanh([(xf1 + d._x_cat, y_ex), (d.x1 + d.hc1 / 2 + 20 * dk, y_ex)], dk)  # type: ignore[attr-defined]
                    else:
                        if ke_p is None:
                            xl = ch["x_ph0"] - ch["d"] - dk / 2 - (1.0 if ch["d"] else 0.0)
                            v.thanh([(xf2 - d._x_cat, y_ex), (xl, y_ex), (xl, y_ex - ch["l_ph"])], dk)  # type: ignore[attr-defined]
                        else:
                            v.thanh([(xf2 - d._x_cat, y_ex), (d.x2 + d.hc2 / 2 + 20 * dk, y_ex)], dk)  # type: ignore[attr-defined]

    # ---- 5. ký hiệu theo ĐÚNG bố cục bản vẽ mẫu (quy tắc D1–D6, C1–C3 trong nhan.py) ----
    cho = nhan.Cho(v)
    for c in kh.cots:  # vật cản: thân cột
        xc = truc[c.truc]
        cho.vat_can(xc - c.h / 2, c.y0, xc + c.h / 2, c.y1)
    for d in kh.dams:  # vật cản: thân dầm (nhãn đặt NGOÀI dầm)
        cho.vat_can(d.x1 + d.hc1 / 2, d.y - d.h, d.x2 - d.hc2 / 2, d.y)
    for t_ in ten_truc:
        w = kh.be_rong_dai.get(t_)
        if w:
            cho.vat_can(truc[t_] - w / 2 - 100, y_lot, truc[t_] + w / 2 + 100, 0.0)
    for d in kh.dams:
        nhan.nhan_dam(kh, v, cho, d)
    for c in kh.cots:
        nhan.nhan_cot(kh, v, cho, c, ten_truc)
    n_so_hieu = cho.so_nhan

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
    return {"so_vong_tron_so_hieu": n_so_hieu, "loi_chong_nhan": cho.loi_chong, "nhan_chong": cho.that_bai, "nhan_rut_gon": cho.rut_gon, "x_trai": x_trai_cuoi, "x_phai": x_phai_cuoi, "y_thap": y_k2 - 3200.0,
            "y_cao": y_top + 2600.0}
