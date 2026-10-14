"""Vẽ MẶT CẮT dầm (chữ T có cánh sàn) và cột theo bản vẽ mẫu `BoTriThep_KhungTruc5_mau.pdf` (đã đo phóng to từng mặt cắt):

- thanh thép là CHẤM ĐẶC; đai bo góc có MÓC 135° (hai vạch chéo ở một góc); đường bao bê tông mặt cắt ĐẬM;
- cánh sàn chỉ lộ ra ngắn, đầu cánh là NÉT GÃY zigzag; mặt sàn là nét đậm, kèm ký hiệu cao độ (tam giác đặc);
- số hiệu thanh dạng "ⓝ nội dung" (vòng tròn TRƯỚC, chữ SAU); thanh trên: khung ngang phía trên cốt sàn thả xuống từng thanh;
  thanh dưới: khung ngang phía trên (web cao) hoặc phía dưới (web thấp) rồi thả tới từng thanh; đai: đoạn ngang ngắn;
  cột: các đường toả từ MỘT điểm neo sát mặt cắt tới từng thanh, rồi đoạn ngang ngắn ra vòng tròn;
- kích thước tính tới TIM ĐAI (28 · 164 · 28), chữ kích thước hẹp đặt NGOÀI vạch (không dính nhau), chữ đứng xoay 90°.

Mỗi mặt cắt dựng ở toạ độ thật rồi phóng `K` lần quanh gốc cục bộ; chữ/vòng tròn số hiệu và mọi khoảng chú thích tính theo mm GIẤY
(nhân tỷ lệ in) nên không phóng. Trả về (hình, rộng_ô, cao_ô, gốc) — ô = vùng chiếm (gồm chú thích) để `bo_cuc` xếp lưới.
"""

from __future__ import annotations

import math

from .. import geometry as g
from .. import layers
from .co_so import HE_SO_RONG_CHU, CauHinhToVe, _Ve
from .ke_hoach import MatCatDinhNghia

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_CUT = layers.OUTLINE_CUT.ten
L_OUT = layers.OUTLINE.ten
L_DIM = layers.DIM.ten
L_AXIS = layers.AXIS.ten
L_SH = layers.SO_HIEU.ten

# Nét gãy đầu cánh (mm thật, ứng với cánh dày 100; tỷ lệ theo bề dày sàn). Đo trên bản mẫu: dọc xuống 27, chéo sang phải 19 / xuống
# 20, ngang trái 39, chéo phải 20 / xuống 20, rồi dọc tiếp xuống đáy cánh; vạch đứng nhô lên trên mặt sàn 18.
ZIC_PHAI = 19.0
ZIC_TRAI = 20.0


def rong_bao_dam(b: float, cfg: CauHinhToVe) -> float:
    """Bề rộng bao của mặt cắt dầm (mm thật, trước khi phóng): thân + hai đoạn cánh + phần nét gãy lồi ra hai đầu."""
    return b + 2 * cfg.canh_ban_cua_t + 2 * ZIC_TRAI * cfg.day_san / 100.0


class _Gom:
    """Ghi lại chiều rộng/cao thật đã vẽ để tính ô."""

    def __init__(self):
        self.x0 = self.y0 = 1e18
        self.x1 = self.y1 = -1e18

    def mo(self, x, y):
        self.x0, self.x1 = min(self.x0, x), max(self.x1, x)
        self.y0, self.y1 = min(self.y0, y), max(self.y1, y)


def _rong_chu(v: _Ve, s: str, co: float | None = None) -> float:
    return len(s) * HE_SO_RONG_CHU * (co or v.h_chu)


def _vong_so(v: _Ve, gom: _Gom, cx, cy, so, noi_dung, huong_chu=1):
    """Vòng tròn số hiệu tại (cx, cy) kèm chữ nội dung nằm BÊN PHẢI vòng tròn ("ⓝ nội dung")."""
    r = v.r_the
    v.tron(cx, cy, r, L_SH)
    v.chu(cx, cy, str(so), v.h_chu, L_SH, giua=True)
    gom.mo(cx - r, cy - r)
    gom.mo(cx + r, cy + r)
    x_cuoi = cx + r
    if noi_dung:
        x_chu = cx + r + 0.5 * v.h_chu_nho
        v.chu(x_chu, cy, noi_dung, v.h_chu)
        x_cuoi = x_chu + _rong_chu(v, noi_dung)
        gom.mo(x_cuoi, cy)
    return x_cuoi


def _bong_bong(v: _Ve, gom: _Gom, x, y, ten):
    r = 3.6 * v.cfg.ty_le
    v.tron(x, y, r, L_AXIS)
    v.chu(x, y, ten, v.h_chu * 1.2, L_AXIS, giua=True)
    gom.mo(x - r, y - r)
    gom.mo(x + r, y + r)


def _chuoi_ngang(v: _Ve, gom: _Gom, xs: list[float], y: float, y_goc: float, nhan: list[str]):
    """Chuỗi kích thước NGANG: đường chuẩn tại `y`, vạch chéo 45° tại mỗi mốc, đường dóng từ `y_goc` (cạnh vật thể). Chữ đặt trên
    đường chuẩn; đoạn hẹp hơn chữ ⇒ chữ ra NGOÀI (đầu trái/đầu phải) hoặc nâng lên tầng trên (đoạn giữa)."""
    co = v.h_chu_nho
    t = 0.5 * co
    huong = 1.0 if y >= y_goc else -1.0
    v.doan(xs[0], y, xs[-1], y, L_DIM)
    for x in xs:
        v.doan(x, y_goc + huong * 0.4 * co, x, y + huong * 0.6 * co, L_DIM)
        v.doan(x - t, y - t, x + t, y + t, L_DIM)
    tang = 0
    for i, s in enumerate(nhan):
        w, seg = _rong_chu(v, s, co), xs[i + 1] - xs[i]
        cy = y + 0.75 * co
        if w + 0.4 * co <= seg:
            cx = (xs[i] + xs[i + 1]) / 2
        elif i == 0:
            cx = xs[0] - 0.5 * co - w / 2
        elif i == len(nhan) - 1:
            cx = xs[-1] + 0.5 * co + w / 2
        else:
            tang += 1
            cx, cy = (xs[i] + xs[i + 1]) / 2, y + 0.75 * co + 1.25 * co * tang
        v.chu(cx, cy, s, co, L_DIM, giua=True)
        gom.mo(cx - w / 2, cy - 0.6 * co)
        gom.mo(cx + w / 2, cy + 0.6 * co)
    gom.mo(xs[0], y - t)
    gom.mo(xs[-1], y + t)


def _chuoi_doc(v: _Ve, gom: _Gom, x: float, ys: list[float], x_goc: float, nhan: list[str]):
    """Chuỗi kích thước ĐỨNG (chữ xoay 90°, đọc từ dưới lên): như `_chuoi_ngang`; chữ hẹp ra phía dưới/trên."""
    co = v.h_chu_nho
    t = 0.5 * co
    huong = 1.0 if x >= x_goc else -1.0
    v.doan(x, ys[0], x, ys[-1], L_DIM)
    for y in ys:
        v.doan(x_goc + huong * 0.4 * co, y, x + huong * 0.6 * co, y, L_DIM)
        v.doan(x - t, y - t, x + t, y + t, L_DIM)
    tang = 0
    for i, s in enumerate(nhan):
        w, seg = _rong_chu(v, s, co), ys[i + 1] - ys[i]
        cx = x - 0.75 * co if huong < 0 else x + 0.75 * co
        if w + 0.4 * co <= seg:
            cy = (ys[i] + ys[i + 1]) / 2
        elif i == len(nhan) - 1:  # đoạn cuối (hoặc đoạn DUY NHẤT) ⇒ chữ ra phía TRÊN mốc trên
            cy = ys[-1] + 0.5 * co + w / 2
        elif i == 0:
            cy = ys[0] - 0.5 * co - w / 2
        else:
            tang += 1
            cy = (ys[i] + ys[i + 1]) / 2
            cx += huong * 1.25 * co * tang
        v.chu(cx, cy, s, co, L_DIM, giua=True, goc=90.0)
        gom.mo(cx - 0.6 * co, cy - w / 2)
        gom.mo(cx + 0.6 * co, cy + w / 2)
    gom.mo(x - t, ys[0])
    gom.mo(x + t, ys[-1])


def _moc_dai(v: _Ve, cx: float, cy: float, huong_x: float, K: float, dw: float):
    """Móc 135° của đai: hai vạch chéo song song xuất phát từ góc đai (cx, cy) đi vào trong theo hướng (huong_x, −1), dài 10·Ø đai,
    cách nhau 2·Ø đai (bản mẫu)."""
    l_ = 10.0 * dw * K / math.sqrt(2)
    s = 2.0 * dw * K
    for dx in (0.0, -huong_x * s):
        v.doan(cx + dx, cy, cx + dx + huong_x * l_, cy - l_, L_DAI)


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


def _duong_bao_t(b: float, h: float, hf: float, ext: float) -> list[tuple[float, float]]:
    """Đa giác ĐÓNG chữ T (mm thật): cạnh trên là mặt sàn; hai đầu cánh có nét gãy zigzag đo từ bản mẫu."""
    k = hf / 100.0
    tr = [(-ext, h), (-ext, h - 27 * k), (-ext + ZIC_PHAI * k, h - 47 * k), (-ext - ZIC_TRAI * k, h - 47 * k), (-ext, h - 67 * k),
          (-ext, h - hf)]
    ph = [(b + ext, h - hf), (b + ext, h - 67 * k), (b + ext + ZIC_TRAI * k, h - 47 * k), (b + ext - ZIC_PHAI * k, h - 47 * k),
          (b + ext, h - 27 * k), (b + ext, h)]
    return tr + [(0, h - hf), (0, 0), (b, 0), (b, h - hf)] + ph


def _nhan_cao_do(v: _Ve, gom: _Gom, x0: float, y: float, md: MatCatDinhNghia) -> None:
    """"TẦNG 2 ▼ +3.200": chữ tầng trên đường, tam giác ĐẶC đỉnh chạm đường, rồi cao độ; đường mảnh kéo dài tới hết nhãn."""
    ten, _, cos = md.cao_do_nhan.rpartition("  ")
    co = v.h_chu_nho
    k = 2.4 * v.cfg.ty_le
    x_tg = x0 + _rong_chu(v, ten, co) + 0.8 * co + k / 2
    x_cuoi = x_tg + k / 2 + 0.8 * co + _rong_chu(v, cos, co)
    v.doan(x0 - 0.5 * co, y, x_cuoi, y, L_OUT)
    v.chu(x0, y + 0.45 * co, ten, co)
    v.tam_giac_dac(x_tg, y, k)
    v.chu(x_tg + k / 2 + 0.8 * co, y + 0.45 * co, cos, co)
    gom.mo(x_cuoi, y + 1.6 * co)


def ve_mat_cat_dam(cfg: CauHinhToVe, md: MatCatDinhNghia, K: float, ten_so_hieu_suot: set[int]) -> tuple[_Ve, float, float, tuple]:
    v = _Ve(cfg, f"MC_{md.so}")
    gom = _Gom()
    T = cfg.ty_le
    P = lambda mm: mm * T  # noqa: E731 — mm GIẤY → model
    b, h = md.b, md.h
    cv = cfg.lop_bao_ve_dam
    hf = cfg.day_san
    ext = cfg.canh_ban_cua_t
    try:
        dw = int(md.dai[1].split("a")[0].replace("Ø", ""))
    except Exception:
        dw = 6
    cvs = cv + dw / 2.0  # tim đai cách mép bê tông
    k = hf / 100.0
    X = lambda x: x * K  # noqa: E731
    Y = lambda y: y * K  # noqa: E731

    # --- đường bao chữ T (đậm) + vạch nhô lên trên mặt sàn ở đầu cánh + mặt sàn đậm kéo dài ---
    v.duong([(X(x), Y(y)) for x, y in _duong_bao_t(b, h, hf, ext)], L_CUT, True)
    for xe in (-ext, b + ext):
        v.doan(X(xe), Y(h), X(xe), Y(h + 18 * k), L_OUT)
    v.duong([(X(-ext), Y(h)), (X(b + ext), Y(h))], L_OUT, False, 0.5 * T)  # mặt sàn đậm (đè lên cạnh trên đa giác)
    gom.mo(X(-ext - ZIC_TRAI * k), Y(h))
    gom.mo(X(b + ext + ZIC_TRAI * k), Y(0))

    # --- đai: nét đậm bo góc, tim đai cách mép `cvs`; móc 135° ở góc trên phải ---
    r_uon = g.ban_kinh_uon_dai(dw)
    ds, cs = g.duong_bao_chu_nhat_bo_tron(cvs, cvs, b - cvs, h - cvs, r_uon, L_DAI)
    for d_ in ds:
        v.doan(X(d_.p1.x), Y(d_.p1.y), X(d_.p2.x), Y(d_.p2.y), L_DAI)
    for c_ in cs:
        v.cung(X(c_.tam.x), Y(c_.tam.y), c_.ban_kinh * K, c_.goc_bat_dau_do, c_.goc_ket_thuc_do, L_DAI)
    _moc_dai(v, X(b - cvs), Y(h - cvs), -1.0, K, dw)

    # --- thép dọc: chấm đặc ---
    tru = {so for _, _, so in md.tren if so in ten_so_hieu_suot}
    tren = _sap_xep_thanh(md.tren, tru)
    duoi = _sap_xep_thanh(md.duoi)

    def dat_hang(ds_: list[tuple[int, int]], tren_: bool):
        ket: list[tuple[float, float, int, int]] = []  # (x, y, Ø, số hiệu)
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
        v.cham(X(x), Y(y), max(d / 2 * K, 0.9 * T * 0.45), L_REBAR)

    # --- trục (bong bóng sát mặt cắt) + nhãn cao độ ---
    xm = X(b / 2)
    y_top_ax = Y(h) + P(11.5)
    v.doan(xm, Y(0) - P(3), xm, y_top_ax, L_AXIS)
    _bong_bong(v, gom, xm, y_top_ax + 3.6 * T, cfg.ten_khung_truc or "")
    if md.cao_do_nhan:
        _nhan_cao_do(v, gom, X(b + ext + ZIC_TRAI * k) + P(3), Y(h), md)

    # --- nhãn thép trên: khung ngang phía trên cốt sàn thả xuống từng thanh; nhóm 1 bên TRÁI, nhóm 2 bên PHẢI ---
    r = v.r_the
    g_t: dict[int, list[tuple[float, float, int, int]]] = {}
    for item in vitri_tren:
        g_t.setdefault(item[3], []).append(item)
    for i_g, (so, lst) in enumerate(g_t.items()):
        xs = [X(i[0]) for i in lst]
        xa, xb = min(xs), max(xs)
        y_line = Y(h) + (P(9.0) if i_g % 2 == 0 else P(4.6)) + (i_g // 2) * P(5.0)
        if xb > xa:
            v.doan(xa, y_line, xb, y_line, L_SH)
        for i in lst:
            v.doan(X(i[0]), y_line, X(i[0]), Y(i[1]) + max(i[2] / 2 * K, 20), L_SH)
        noi_dung = f"{len(lst)}Ø{lst[0][2]}"
        if i_g % 2 == 0:  # [vòng tròn][chữ] rồi tới khung ngang
            w = _rong_chu(v, noi_dung)
            cx = xa - 0.8 * v.h_chu_nho - w - 0.5 * v.h_chu_nho - r
            _vong_so(v, gom, cx, y_line, so, noi_dung)
            v.doan(cx + r + 0.5 * v.h_chu_nho + w + 0.2 * v.h_chu_nho, y_line, xa, y_line, L_SH)
        else:  # khung ngang rồi [vòng tròn][chữ]
            cx = xb + 1.2 * r
            v.doan(xb, y_line, cx - r, y_line, L_SH)
            _vong_so(v, gom, cx, y_line, so, noi_dung)

    # --- nhãn thép dưới: khung ngang phía trên thanh (web cao) hoặc phía dưới (web thấp) rồi ra vòng tròn bên phải ---
    x_tag = X(b) + P(9.0)
    g_d: dict[int, list[tuple[float, float, int, int]]] = {}
    for item in vitri_duoi:
        g_d.setdefault(item[3], []).append(item)
    phia_tren = (h - hf) >= 300.0
    for nl, (so, lst) in enumerate(g_d.items()):
        xs = [X(i[0]) for i in lst]
        y_bar = min(Y(i[1]) for i in lst)
        # web cao: khung ngang phía TRÊN thanh; web thấp: ngay DƯỚI đáy dầm (bản mẫu 3-3), không đụng chuỗi kích thước phía dưới
        y_line = y_bar + P(6.5) + nl * P(5.0) if phia_tren else Y(0) - P(2.6) - nl * P(4.0)
        for i in lst:
            v.doan(X(i[0]), y_line, X(i[0]), Y(i[1]) + max(i[2] / 2 * K, 20) * (1 if phia_tren else -1), L_SH)
        v.doan(min(xs), y_line, x_tag - r, y_line, L_SH)
        _vong_so(v, gom, x_tag, y_line, so, f"{len(lst)}Ø{lst[0][2]}")

    # --- nhãn đai: đoạn NGANG ngắn từ cạnh phải đai ra vòng tròn (cùng cột với nhãn thép dưới) ---
    so_dai, nhan_dai = md.dai
    y_dai = Y(0.49 * h)
    v.doan(X(b - cvs), y_dai, x_tag - r, y_dai, L_SH)
    _vong_so(v, gom, x_tag, y_dai, so_dai, nhan_dai)

    # --- kích thước (tới TIM ĐAI: 28 · 164 · 28) ---
    xs_d = [X(0), X(cvs), X(b - cvs), X(b)]
    _chuoi_ngang(v, gom, xs_d, Y(0) - P(6.0), Y(0), [f"{cvs:g}", f"{b - 2 * cvs:g}", f"{cvs:g}"])
    _chuoi_ngang(v, gom, [X(0), X(b)], Y(0) - P(10.0), Y(0), [f"{b:g}"])
    x_goc = X(-ext - ZIC_TRAI * k)
    x1 = x_goc - P(4.0)
    x2 = x1 - P(4.5)
    _chuoi_doc(v, gom, x1, [Y(0), Y(h - hf), Y(h)], x_goc, [f"{h - hf:g}", f"{hf:g}"])
    _chuoi_doc(v, gom, x2, [Y(0), Y(h)], x_goc, [f"{h:g}"])
    _chuoi_doc(v, gom, X(0) - P(2.6), [Y(0), Y(cvs)], X(0), [f"{cvs:g}"])  # lớp bảo vệ đáy tới tim đai

    # --- tên mặt cắt ---
    ten = f"{md.so}-{md.so}"
    v.chu(xm, Y(0) - P(17.0), ten, v.h_chu * 1.6, giua=True)
    gom.mo(xm - 2 * v.h_chu, Y(0) - P(17.0) - v.h_chu)
    return v, gom.x1 - gom.x0, gom.y1 - gom.y0, (gom.x0, gom.y0)


def ve_mat_cat_cot(cfg: CauHinhToVe, md: MatCatDinhNghia, K: float) -> tuple[_Ve, float, float, tuple]:
    v = _Ve(cfg, f"MC_{md.so}")
    gom = _Gom()
    T = cfg.ty_le
    P = lambda mm: mm * T  # noqa: E731
    b, h = md.b, md.h  # b vuông góc khung; h trong mặt phẳng khung ⇒ hiển thị rộng = h, cao = b
    W, H = h, b
    cv = cfg.lop_bao_ve_cot
    try:
        dw = int(md.dai[1].split("a")[0].replace("Ø", ""))
    except Exception:
        dw = 6
    cvs = cv + dw / 2.0
    X = lambda x: x * K  # noqa: E731
    Y = lambda y: y * K  # noqa: E731
    v.hcn(0, 0, X(W), Y(H), L_CUT)
    r_uon = g.ban_kinh_uon_dai(dw)
    ds, cs = g.duong_bao_chu_nhat_bo_tron(cvs, cvs, W - cvs, H - cvs, r_uon, L_DAI)
    for d_ in ds:
        v.doan(X(d_.p1.x), Y(d_.p1.y), X(d_.p2.x), Y(d_.p2.y), L_DAI)
    for c_ in cs:
        v.cung(X(c_.tam.x), Y(c_.tam.y), c_.ban_kinh * K, c_.goc_bat_dau_do, c_.goc_ket_thuc_do, L_DAI)
    _moc_dai(v, X(cvs), Y(H - cvs), 1.0, K, dw)  # móc ở góc trên TRÁI (bản mẫu 13-13)
    info = md.cot or {}
    d = info.get("d", 16)
    pos = g.toa_do_thep_chu_vi_hcn(W, H, cv, dw, info.get("n_h", 2), d, info.get("n_b", 2), d)
    for tam, dd in pos:
        v.cham(X(tam.x), Y(tam.y), max(dd / 2 * K, 0.9 * T * 0.45), L_REBAR)
    # tim trục: bong bóng A phía trên, bong bóng khung (vd 5) bên trái, đều sát mặt cắt
    x_bt, y_bt = X(W / 2), Y(H) + P(14.5)
    v.doan(x_bt, Y(0) - P(3), x_bt, y_bt - 3.6 * T, L_AXIS)
    v.doan(X(0) - P(15.8) + 3.6 * T, Y(H / 2), X(W) + P(3), Y(H / 2), L_AXIS)
    _bong_bong(v, gom, x_bt, y_bt, md.truc)
    _bong_bong(v, gom, X(0) - P(15.8), Y(H / 2), cfg.ten_khung_truc or "")
    # số hiệu thép: các đường toả từ MỘT điểm neo ngay trên mặt cắt tới từng thanh, đoạn ngang ngắn ra vòng tròn
    so_h = info.get("so_hieu", 0)
    r = v.r_the
    ax, ay = X(0.58 * W), Y(H) + P(3.2)
    for tam, dd in pos:
        v.doan(ax, ay, X(tam.x), Y(tam.y), L_SH)
    v.doan(ax, ay, ax + P(6.0) - r, ay, L_SH)
    _vong_so(v, gom, ax + P(6.0), ay, so_h, f"{len(pos)}Ø{d}")
    # đai: từ cạnh dưới đai (≈73% bề rộng) thả xuống rồi ngang ra vòng tròn
    so_dai, nhan_dai = md.dai
    xs_, ys_ = X(0.73 * W), Y(0) - P(2.8)
    x_c = X(W) + P(7.0)
    v.doan(xs_, Y(cvs), xs_, ys_, L_SH)
    v.doan(xs_, ys_, x_c - r, ys_, L_SH)
    _vong_so(v, gom, x_c, ys_, so_dai, nhan_dai)
    # kích thước: dưới (tới tim đai) + tổng; trái (tim đai) + tổng; phải: hai nửa quanh trục; trên: hai nửa quanh trục
    _chuoi_ngang(v, gom, [X(0), X(cvs), X(W - cvs), X(W)], Y(0) - P(7.8), Y(0), [f"{cvs:g}", f"{W - 2 * cvs:g}", f"{cvs:g}"])
    _chuoi_ngang(v, gom, [X(0), X(W)], Y(0) - P(11.8), Y(0), [f"{W:g}"])
    _chuoi_doc(v, gom, X(0) - P(3.6), [Y(0), Y(cvs), Y(H - cvs), Y(H)], X(0), [f"{cvs:g}", f"{H - 2 * cvs:g}", f"{cvs:g}"])
    _chuoi_doc(v, gom, X(0) - P(7.6), [Y(0), Y(H)], X(0), [f"{H:g}"])
    _chuoi_doc(v, gom, X(W) + P(3.8), [Y(0), Y(H / 2), Y(H)], X(W), [f"{H / 2:g}", f"{H / 2:g}"])
    _chuoi_ngang(v, gom, [X(0), X(W / 2), X(W)], Y(H) + P(7.4), Y(H), [f"{W / 2:g}", f"{W / 2:g}"])
    gom.mo(0, Y(0))
    gom.mo(X(W), Y(H))
    ten = f"{md.so}-{md.so}"
    v.chu(X(W / 2), Y(0) - P(17.0), ten, v.h_chu * 1.6, giua=True)
    gom.mo(X(W / 2) - 2 * v.h_chu, Y(0) - P(17.0) - v.h_chu)
    return v, gom.x1 - gom.x0, gom.y1 - gom.y0, (gom.x0, gom.y0)
