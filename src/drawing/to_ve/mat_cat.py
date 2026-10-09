"""Vẽ MẶT CẮT dầm (chữ T có cánh sàn) và cột theo bản vẽ mẫu: đường bao, đai uốn tròn góc, thép dọc, số hiệu có đường
dẫn, kích thước (lớp bảo vệ/trong/tổng; chiều cao sàn/sườn/tổng), cốt sàn, trục, tên `n-n`.

Mỗi mặt cắt dựng ở toạ độ thật rồi phóng `K` lần quanh gốc cục bộ; chữ/vòng tròn số hiệu GIỮ cỡ giấy (không phóng).
Trả về (hình, rộng_ô, cao_ô) — ô = vùng chiếm (gồm chú thích) để `bo_cuc` xếp lưới.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from .co_so import CauHinhToVe, _Ve
from .ke_hoach import MatCatDinhNghia

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_CUT = layers.OUTLINE_CUT.ten
L_OUT = layers.OUTLINE.ten
L_DIM = layers.DIM.ten
L_AXIS = layers.AXIS.ten
L_SH = layers.SO_HIEU.ten


class _Gom:
    """Ghi lại chiều rộng/cao thật đã vẽ để tính ô."""

    def __init__(self):
        self.x0 = self.y0 = 1e18
        self.x1 = self.y1 = -1e18

    def mo(self, x, y):
        self.x0, self.x1 = min(self.x0, x), max(self.x1, x)
        self.y0, self.y1 = min(self.y0, y), max(self.y1, y)


def _tag(v: _Ve, gom: _Gom, x_tro, y_tro, x_the, y_the, so, noi_dung, huong=1):
    r = v.r_the
    dx, dy = x_the - x_tro, y_the - y_tro
    d = math.hypot(dx, dy) or 1.0
    v.doan(x_tro, y_tro, x_the - dx / d * r, y_the - dy / d * r, L_SH)
    v.tron(x_the, y_the, r, L_SH)
    v.chu(x_the, y_the, str(so), v.h_chu, L_SH, giua=True)
    w = len(noi_dung) * 0.6 * v.h_chu if noi_dung else 0.0
    if noi_dung:
        if huong >= 0:
            v.chu(x_the + r + 0.5 * v.h_chu_nho, y_the, noi_dung, v.h_chu)
            gom.mo(x_the + r + 0.5 * v.h_chu_nho + w, y_the)
        else:
            v.chu(x_the - r - 0.5 * v.h_chu_nho, y_the, noi_dung, v.h_chu, phai=True)
            gom.mo(x_the - r - 0.5 * v.h_chu_nho - w, y_the)
    gom.mo(x_the - r, y_the - r)
    gom.mo(x_the + r, y_the + r)


def _kt_ngang(v: _Ve, gom: _Gom, x1, x2, y, nhan, co=None):
    v.kt((x1, y), (x2, y), nhan, L_DIM, co)
    gom.mo(x1, y - 100)
    gom.mo(x2, y + 200)


def _kt_doc(v: _Ve, gom: _Gom, x, y1, y2, nhan, co=None):
    v.kt((x, y1), (x, y2), nhan, L_DIM, co)
    gom.mo(x - 250, y1)
    gom.mo(x + 100, y2)


def _bong_bong(v: _Ve, gom: _Gom, x, y, ten):
    r = 3.6 * v.cfg.ty_le
    v.tron(x, y, r, L_AXIS)
    v.chu(x, y, ten, v.h_chu * 1.2, L_AXIS, giua=True)
    gom.mo(x - r, y - r)
    gom.mo(x + r, y + r)


def _sap_xep_thanh(nhom: list[tuple[int, int, int]], tru: set[int] | None = None) -> list[tuple[int, int]]:
    """Mở nhóm [(Ø, n, số hiệu)] → danh sách (Ø, số hiệu) từng thanh theo thứ tự đặt: thanh `tru` (liên tục) ra HAI ĐẦU,
    thanh còn lại ở giữa (đúng bản mẫu: 2Ø18 góc + 1Ø18 giữa)."""
    tru = tru or set()
    cont = [(d, so) for d, n, so in nhom if so in tru for _ in range(n)]
    giua = [(d, so) for d, n, so in nhom if so not in tru for _ in range(n)]
    if not cont:
        return giua
    nua = (len(cont) + 1) // 2
    return cont[:nua] + giua + cont[nua:]


def ve_mat_cat_dam(cfg: CauHinhToVe, md: MatCatDinhNghia, K: float, ten_so_hieu_suot: set[int]) -> tuple[_Ve, float, float]:
    v = _Ve(cfg, f"MC_{md.so}")
    gom = _Gom()
    b, h = md.b, md.h
    cv = cfg.lop_bao_ve_dam
    hf = cfg.day_san
    ext = cfg.canh_ban_cua_t
    dw = md.dai[0] and 6  # đường kính đai thực lấy từ nhãn
    try:
        dw = int(md.dai[1].split("a")[0].replace("Ø", ""))
    except Exception:
        dw = 6
    X = lambda x: x * K  # noqa: E731
    Y = lambda y: y * K  # noqa: E731

    # --- đường bao chữ T (dầm + cánh sàn) ---
    pts = [(0, 0), (b, 0), (b, h - hf), (b + ext, h - hf), (b + ext, h), (-ext, h), (-ext, h - hf), (0, h - hf)]
    v.duong([(X(x), Y(y)) for x, y in pts], L_CUT, True)
    for x in (b + ext, -ext):  # ký hiệu cắt đứt đầu cánh (//)
        for dx in (-25, 25):
            v.doan(X(x + dx) - 20, Y(h - hf) + 12 * K * 0.2, X(x + dx) + 20, Y(h) - 12 * K * 0.2, L_OUT)
    # cốt sàn
    xl, xr = X(-ext) - 700.0, X(b + ext) + 700.0
    v.doan(xl, Y(h), xr, Y(h), L_OUT)
    gom.mo(xl, Y(h))
    gom.mo(xr, Y(h))
    # đai
    r_uon = g.ban_kinh_uon_dai(dw)
    ds, cs = g.duong_bao_chu_nhat_bo_tron(cv, cv, b - cv, h - cv, r_uon, L_DAI)
    for d_ in ds:
        v.doan(X(d_.p1.x), Y(d_.p1.y), X(d_.p2.x), Y(d_.p2.y), L_DAI)
    for c_ in cs:
        v.cung(X(c_.tam.x), Y(c_.tam.y), c_.ban_kinh * K, c_.goc_bat_dau_do, c_.goc_ket_thuc_do, L_DAI)

    # --- thép dọc ---
    tru = {so for _, _, so in md.tren if so in ten_so_hieu_suot}
    tren = _sap_xep_thanh(md.tren, tru)
    duoi = _sap_xep_thanh(md.duoi)
    vitri_tren: list[tuple[float, float, int, int]] = []  # (x,y,Ø,số hiệu)
    vitri_duoi: list[tuple[float, float, int, int]] = []

    def dat_hang(ds_: list[tuple[int, int]], tren_: bool):
        ket: list[tuple[float, float, int, int]] = []
        if not ds_:
            return ket
        lop = g.chia_lop_thep([d for d, _ in ds_], b, cv, dw)
        i0 = 0
        y = (h - cv - dw - max(lop[0]) / 2) if tren_ else (cv + dw + max(lop[0]) / 2)
        for li, ls in enumerate(lop):
            seg = ds_[i0 : i0 + len(ls)]
            i0 += len(ls)
            for (tam, d), (_, so) in zip(g.toa_do_1_hang(b, cv, dw, ls, y), seg):
                ket.append((tam.x, tam.y, d, so))
            if li + 1 < len(lop):
                dich = max(ls) / 2 + 25 + max(lop[li + 1]) / 2
                y += -dich if tren_ else dich
        return ket

    vitri_tren = dat_hang(tren, True)
    vitri_duoi = dat_hang(duoi, False)
    for x, y, d, _ in vitri_tren + vitri_duoi:
        v.tron(X(x), Y(y), max(d / 2 * K, 0.9 * cfg.ty_le * 0.45), L_REBAR)

    # --- trục + cos ---
    xm = X(b / 2)
    y_top_ax = Y(h) + 2300.0
    v.doan(xm, Y(0) - 150, xm, y_top_ax, L_AXIS)
    _bong_bong(v, gom, xm, y_top_ax + 3.6 * cfg.ty_le, cfg.ten_khung_truc or "")
    # nhãn cao độ sàn bên phải cốt sàn
    if md.cao_do_nhan:
        ten, _, cos = md.cao_do_nhan.rpartition("  ")
        v.chu(xr - 100, Y(h) + 120, ten, v.h_chu_nho, giua=False, phai=True)
        v.tam_giac_cao_do(xr + 150, Y(h))
        v.chu(xr + 150 + 200, Y(h) + 120, cos, v.h_chu_nho)
        gom.mo(xr + 150 + 200 + len(cos) * 0.6 * v.h_chu_nho, Y(h))

    # --- chú thích thép: nhóm trên (ngay trên cốt sàn), nhóm dưới (bên phải) ---
    nhom_t: dict[int, list[tuple[float, float, int, int]]] = {}
    for item in vitri_tren:
        nhom_t.setdefault(item[3], []).append(item)
    nl = 0
    for so, lst in nhom_t.items():
        xs = [X(i[0]) for i in lst]
        y_line = Y(h) + 800.0 + nl * 600.0
        xa, xb = min(xs), max(xs)
        v.doan(xa, y_line, xb, y_line, L_SH)
        for i in lst:
            v.doan(X(i[0]), y_line, X(i[0]), Y(i[1]) + max(i[2] / 2 * K, 20) , L_SH)
        d0 = lst[0][2]
        _tag(v, gom, xa, y_line, xa - 2.4 * cfg.ty_le - 60, y_line, so, f"{len(lst)}Ø{d0}", huong=-1)
        nl += 1
    nhom_d: dict[int, list[tuple[float, float, int, int]]] = {}
    for item in vitri_duoi:
        nhom_d.setdefault(item[3], []).append(item)
    nl = 0
    x_phai_tag = X(b + ext) + 500.0
    for so, lst in nhom_d.items():
        xs = [X(i[0]) for i in lst]
        ymin = min(Y(i[1]) for i in lst)
        y_tag = ymin + nl * 3.0 * v.r_the
        v.doan(min(xs), y_tag + 0.0, max(xs), y_tag, L_SH) if len(lst) > 1 else None
        d0 = lst[0][2]
        _tag(v, gom, max(xs), Y(lst[0][1]), x_phai_tag, y_tag, so, f"{len(lst)}Ø{d0}", huong=1)
        nl += 1
    # đai
    so_dai, nhan_dai = md.dai
    y_dai_tag = Y(h * 0.5) + 150.0
    _tag(v, gom, X(b - cv), Y(h * 0.55), x_phai_tag, Y(h * 0.55) + 1.6 * v.r_the * (1 if nhom_d else 0) + 400.0, so_dai, nhan_dai, huong=1)

    # --- kích thước ---
    co = v.h_chu_nho
    yb1, yb2 = Y(0) - 450.0, Y(0) - 950.0
    _kt_ngang(v, gom, X(0), X(cv), yb1, f"{cv:g}", co)
    _kt_ngang(v, gom, X(cv), X(b - cv), yb1, f"{b - 2 * cv:g}", co)
    _kt_ngang(v, gom, X(b - cv), X(b), yb1, f"{cv:g}", co)
    _kt_ngang(v, gom, X(0), X(b), yb2, f"{b:g}", co)
    xl1, xl2 = X(-ext) - 350.0 - 300.0, X(-ext) - 350.0 - 800.0
    xl1 = min(xl1, X(0) - 600.0)
    xl2 = xl1 - 500.0
    _kt_doc(v, gom, xl1, Y(h - hf), Y(h), f"{hf:g}", co)
    _kt_doc(v, gom, xl1, Y(0), Y(h - hf), f"{h - hf:g}", co)
    _kt_doc(v, gom, xl2, Y(0), Y(h), f"{h:g}", co)

    # --- tên ---
    ten = f"{md.so}-{md.so}"
    gom.mo(X(-ext) - 1200.0, Y(0) - 1700.0)
    v.chu(xm, Y(0) - 1500.0, ten, v.h_chu * 1.6, giua=True)
    gom.mo(xm, Y(0) - 1500.0 - v.h_chu)
    return v, gom.x1 - gom.x0, gom.y1 - gom.y0, (gom.x0, gom.y0)


def ve_mat_cat_cot(cfg: CauHinhToVe, md: MatCatDinhNghia, K: float) -> tuple[_Ve, float, float]:
    v = _Ve(cfg, f"MC_{md.so}")
    gom = _Gom()
    b, h = md.b, md.h  # b vuông góc khung; h trong mặt phẳng khung ⇒ hiển thị rộng = h, cao = b
    W, H = h, b
    cv = cfg.lop_bao_ve_cot
    try:
        dw = int(md.dai[1].split("a")[0].replace("Ø", ""))
    except Exception:
        dw = 6
    X = lambda x: x * K  # noqa: E731
    Y = lambda y: y * K  # noqa: E731
    v.hcn(0, 0, X(W), Y(H), L_CUT)
    r_uon = g.ban_kinh_uon_dai(dw)
    ds, cs = g.duong_bao_chu_nhat_bo_tron(cv, cv, W - cv, H - cv, r_uon, L_DAI)
    for d_ in ds:
        v.doan(X(d_.p1.x), Y(d_.p1.y), X(d_.p2.x), Y(d_.p2.y), L_DAI)
    for c_ in cs:
        v.cung(X(c_.tam.x), Y(c_.tam.y), c_.ban_kinh * K, c_.goc_bat_dau_do, c_.goc_ket_thuc_do, L_DAI)
    info = md.cot or {}
    d = info.get("d", 16)
    pos = g.toa_do_thep_chu_vi_hcn(W, H, cv, dw, info.get("n_h", 2), d, info.get("n_b", 2), d)
    for tam, dd in pos:
        v.tron(X(tam.x), Y(tam.y), max(dd / 2 * K, 0.9 * cfg.ty_le * 0.45), L_REBAR)
    # tim trục
    v.doan(X(W / 2), Y(0) - 150, X(W / 2), Y(H) + 1500.0, L_AXIS)
    v.doan(-1500.0 - 150, Y(H / 2), X(W) + 150, Y(H / 2), L_AXIS)
    _bong_bong(v, gom, X(W / 2), Y(H) + 1500.0 + 3.6 * cfg.ty_le, md.truc)
    _bong_bong(v, gom, -1500.0 - 3.6 * cfg.ty_le, Y(H / 2), cfg.ten_khung_truc or "")
    # số hiệu thép: các đường toả từ 1 điểm tới từng thanh
    so_h = info.get("so_hieu", 0)
    tx, ty = X(W) + 600.0, Y(H) + 800.0
    for tam, dd in pos:
        v.doan(tx, ty - v.r_the, X(tam.x), Y(tam.y), L_SH)
    _tag(v, gom, tx, ty - v.r_the, tx, ty, so_h, f"{len(pos)}Ø{d}", huong=1)
    so_dai, nhan_dai = md.dai
    _tag(v, gom, X(W - cv), Y(cv), X(W) + 600.0, Y(0) - 100.0, so_dai, nhan_dai, huong=1)
    co = v.h_chu_nho
    yb1, yb2 = Y(0) - 450.0, Y(0) - 950.0
    _kt_ngang(v, gom, X(0), X(cv), yb1, f"{cv:g}", co)
    _kt_ngang(v, gom, X(cv), X(W - cv), yb1, f"{W - 2 * cv:g}", co)
    _kt_ngang(v, gom, X(W - cv), X(W), yb1, f"{cv:g}", co)
    _kt_ngang(v, gom, X(0), X(W), yb2, f"{W:g}", co)
    xl1 = -500.0
    xl2 = -1000.0
    _kt_doc(v, gom, xl1, Y(0), Y(cv), f"{cv:g}", co)
    _kt_doc(v, gom, xl1, Y(cv), Y(H - cv), f"{H - 2 * cv:g}", co)
    _kt_doc(v, gom, xl1, Y(H - cv), Y(H), f"{cv:g}", co)
    _kt_doc(v, gom, xl2, Y(0), Y(H), f"{H:g}", co)
    # nửa bề rộng từ trục (cột đặt đối xứng quanh trục)
    yh = Y(H) + 800.0
    _kt_ngang(v, gom, X(0), X(W / 2), yh, f"{W / 2:g}", co)
    _kt_ngang(v, gom, X(W / 2), X(W), yh, f"{W / 2:g}", co)
    gom.mo(0, Y(0))
    gom.mo(X(W), Y(H))
    ten = f"{md.so}-{md.so}"
    v.chu(X(W / 2), Y(0) - 1500.0, ten, v.h_chu * 1.6, giua=True)
    gom.mo(X(W / 2), Y(0) - 1500.0 - v.h_chu)
    return v, gom.x1 - gom.x0, gom.y1 - gom.y0, (gom.x0, gom.y0)
