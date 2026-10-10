"""SẮP XẾP KÝ HIỆU trên mặt đứng theo ĐÚNG bản vẽ mẫu `data/samples/BoTriThep_KhungTruc5_mau.pdf`.

Quy tắc rút từ việc đo vị trí chữ/vòng tròn trong PDF mẫu (khoảng cách tính bằng mm THẬT của công trình; hệ số theo
chiều dài nhịp `L` = thông thuỷ dầm). Mỗi quy tắc có mã `Dn` (dầm) / `Cn` (cột) để test và tài liệu tham chiếu:

DẦM (đặt quanh từng dầm, mặt trên = cốt sàn `yt`, đáy `yb`):
  D1  thanh trên suốt (khi KHÔNG có thanh gia cường): ⓝ + "nØd" ngay TRÊN cốt sàn (yt+230) tại ~0,68L (nhịp ngắn 0,56L).
  D2  thanh trên tại gối (có gia cường): cụm [chữ xếp chồng "2Ø18 / 1Ø18"][vòng tròn ⓝ ⓝ] = thanh suốt + gia cường, ngay trên cốt sàn (yt+300); đường dẫn đứng
      ở 0,13L (gối trái) / 0,81L (gối phải); trái = chữ rồi vòng tròn, phải = vòng tròn rồi chữ.
  D3  ký hiệu mặt cắt = "số ▌" (số ở BÊN TRÁI vạch đậm đứng), vẽ HAI LẦN cho mỗi mặt cắt: trên dầm (yt+470) và dưới dầm
      (yb−480) cùng x (đường cắt đi qua dầm); x = 0,10L / 0,45L / 0,90L cho gối trái / giữa / gối phải; mặt cắt trùng số
      trong 1 dầm chỉ ghi 1 lần; nhịp ngắn ghi ở 0,94L.
  D4  dây kích thước vùng đai ở yt+900: nhiều vùng khác bước ⇒ "1300(Ø6a150) 2620(Ø6a200) 1300(Ø6a150)"; đồng đều ⇒ 1 dòng.
  D5  nhãn đai: đồng đều ⇒ ⓝ Ø/bước DƯỚI dầm (yb−320) tại 0,24L; 3 vùng ⇒ vùng gối dưới dầm tại 0,27L và 0,78L, vùng giữa
      TRÊN dầm (yt+210, 0,375L) đường dẫn xuống; nhịp ngắn ⇒ TRÊN dầm (yt+510) đường dẫn xuống.
  D6  thanh dưới: ⓝ "nØd" DƯỚI dầm (yb−320) tại 0,55L (nhịp ngắn: giữa nhịp).

CỘT (mỗi đoạn cột; `y_giua` = giữa khoảng thông thuỷ):
  C1  thép dọc: ⓝ "nØd" bên PHẢI cột tại giữa thông thuỷ, vòng tròn cách mép cột 290.
  C2  đai: bên TRÁI cột (trục đầu, trục giữa) hoặc PHẢI (trục cuối). Trái: vòng tròn cách mép cột 860, chữ rồi đường dẫn tới
      cột; phải: vòng tròn cách mép 250. Hai nhãn: vùng dày ở trên sàn 250 (tầng 1: trên đỉnh móng 300) và vùng giữa ngay
      dưới đáy dầm 190.
  C3  ký hiệu mặt cắt cột = vạch đậm NẰM NGANG, số ở TRÊN vạch, hai bên cột (cách mép 330): vùng dày tại sàn+470, vùng
      giữa tại đáy dầm−960.

Mọi nhãn qua `Cho` (bộ giữ hộp) để đếm chồng chéo; không tự dời xa vị trí quy tắc quá một khoảng nhỏ.
"""

from __future__ import annotations

import math

from .. import layers
from .co_so import HE_SO_RONG_CHU, _Cot, _Dam, _Ve
from .ke_hoach import KeHoach

L_REBAR = layers.REBAR_MAIN.ten
L_DAI = layers.REBAR_STIRRUP.ten
L_DIM = layers.DIM.ten
L_SH = layers.SO_HIEU.ten

# --- hệ số vị trí (xem docstring đầu file) ---
D1_X, D1_X_NGAN, D1_Y = 0.68, 0.56, 230.0
D2_X_TRAI, D2_X_PHAI, D2_Y = 0.13, 0.81, 300.0
D3_X = {"trai": 0.10, "giua": 0.45, "phai": 0.90}
D3_X_NGAN = 0.95
D3_Y_TREN, D3_Y_DUOI = 470.0, 480.0
D4_Y = 900.0
D5_X_DONG_DEU, D5_X_GOI_TRAI, D5_X_GOI_PHAI, D5_X_GIUA = 0.24, 0.27, 0.78, 0.375
D5_Y_DUOI, D5_Y_GIUA_TREN, D5_Y_NGAN_TREN = 320.0, 210.0, 510.0
D6_X, D6_Y = 0.55, 320.0
NHIP_NGAN_MM = 3000.0
C1_LECH = 290.0
C2_LECH_TRAI, C2_LECH_PHAI = 860.0, 250.0
C2_Y_DAY_TREN_SAN, C2_Y_DAY_MONG, C2_Y_GIUA_DUOI_DAM = 250.0, 300.0, 190.0
C3_LECH = 330.0
C3_Y_DAY_TREN_SAN, C3_Y_GIUA_DUOI_DAM = 470.0, 960.0


def vong_tron_so_hieu(v: _Ve, x_tro, y_tro, x_the, y_the, so, noi_dung, huong=1):
    """ⓝ + chữ; đường dẫn từ (x_tro,y_tro) tới MÉP vòng tròn (không xuyên vào chữ). huong=+1 chữ bên phải vòng tròn."""
    r = v.r_the
    dx, dy = x_the - x_tro, y_the - y_tro
    d = math.hypot(dx, dy) or 1.0
    v.doan(x_tro, y_tro, x_the - dx / d * r, y_the - dy / d * r, L_SH)
    v.tron(x_the, y_the, r, L_SH)
    v.chu(x_the, y_the, str(so), v.h_chu, L_SH, giua=True)
    if noi_dung:
        yc = y_the - 0.36 * v.h_chu  # AddText neo ở ĐƯỜNG CƠ SỞ: hạ xuống để chữ ngang tâm vòng tròn
        if huong >= 0:
            v.chu(x_the + r + 0.5 * v.h_chu_nho, yc, noi_dung, v.h_chu)
        else:
            v.chu(x_the - r - 0.5 * v.h_chu_nho, yc, noi_dung, v.h_chu, phai=True)


def vach_mat_cat_dung(v: _Ve, x, y, so):
    """Ký hiệu mặt cắt trên mặt đứng (dầm): "số ▌" — số ở BÊN TRÁI vạch đậm đứng (bản mẫu)."""
    h = 1.6 * v.cfg.ty_le * 2.4
    v.doan_net_dam(x, y - h / 2, y + h / 2, 0.9 * v.cfg.ty_le)
    nua = 0.5 * len(str(so)) * HE_SO_RONG_CHU * v.h_chu * 1.25 + 0.9 * v.cfg.ty_le * 1.2
    v.chu(x - nua, y, str(so), v.h_chu * 1.25, giua=True)


def vach_mat_cat_ngang(v: _Ve, x, y, so):
    """Ký hiệu mặt cắt cột: vạch đậm NẰM NGANG, số ở TRÊN vạch (bản mẫu "13 ▬")."""
    dai = 6.0 * v.cfg.ty_le
    v.duong([(x - dai / 2, y), (x + dai / 2, y)], layers.REBAR_MAIN.ten, False, 0.9 * v.cfg.ty_le)
    v.chu(x, y + 0.9 * v.cfg.ty_le + 0.75 * v.h_chu * 1.25, str(so), v.h_chu * 1.25, giua=True)


class Cho:
    """Bộ giữ hộp nhãn: đăng ký vị trí đã dùng, thử vài độ lệch nhỏ khi chồng, đếm chồng còn lại."""

    LE = 12.0

    def __init__(self, v: _Ve):
        self.v = v
        self.hop: list[tuple[float, float, float, float]] = []
        self.loi_chong = 0
        self.rut_gon = 0
        self.that_bai: list[tuple[str, float, float]] = []
        self.so_nhan = 0  # số vòng tròn số hiệu đã vẽ

    # ---- hộp ----
    def vat_can(self, x0, y0, x1, y1):
        self.hop.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def trong(self, b) -> bool:
        le = self.LE
        return not any(b[0] < a1 + le and b[2] > a0 - le and b[1] < b1 + le and b[3] > b0 - le for a0, b0, a1, b1 in self.hop)

    def chieu_rong_chu(self, s: str, cao: float | None = None) -> float:
        return len(s) * HE_SO_RONG_CHU * (cao or self.v.h_chu)

    def hop_the(self, x, y, noi_dung, huong):
        v = self.v
        r = v.r_the
        w = self.chieu_rong_chu(noi_dung) if noi_dung else 0.0
        if huong >= 0:
            return (x - r, y - r, x + r + 0.5 * v.h_chu_nho + w, y + r)
        return (x - r - 0.5 * v.h_chu_nho - w, y - r, x + r, y + r)

    # ---- nhãn ----
    def the(self, xa, ya, x, y, so, noi_dung, huong=1, dys=(0.0, 150.0, -150.0, 300.0, -300.0), dxs=(0.0, 250.0, -250.0)) -> bool:
        """ⓝ + chữ tại (x,y) (vị trí quy tắc); chồng ⇒ thử lệch nhỏ, rồi lật chiều chữ, rồi chỉ ghi số hiệu."""
        for hg in (huong, -huong):
            for dy in dys:
                for dx in dxs:
                    b = self.hop_the(x + dx, y + dy, noi_dung, hg)
                    if self.trong(b):
                        vong_tron_so_hieu(self.v, xa, ya, x + dx, y + dy, so, noi_dung, hg)
                        self.hop.append(b)
                        self.so_nhan += 1
                        return True
        for dy in dys:
            for dx in (0.0, 300.0, -300.0, 600.0, -600.0):
                b = self.hop_the(x + dx, y + dy, "", huong)
                if self.trong(b):
                    vong_tron_so_hieu(self.v, xa, ya, x + dx, y + dy, so, "", huong)
                    self.hop.append(b)
                    self.rut_gon += 1
                    self.so_nhan += 1
                    return True
        vong_tron_so_hieu(self.v, xa, ya, x, y, so, noi_dung, huong)
        self.hop.append(self.hop_the(x, y, noi_dung, huong))
        self.loi_chong += 1
        self.that_bai.append((f"{so} {noi_dung}", x, y))
        self.so_nhan += 1
        return False

    def vach_dung(self, x, y, so, dys=(0.0, 200.0, -200.0), dxs=(0.0, 300.0, -300.0)) -> bool:
        v = self.v
        w = 0.9 * v.cfg.ty_le * 2.4 + len(str(so)) * HE_SO_RONG_CHU * v.h_chu * 1.25
        for dy in dys:
            for dx in dxs:
                b = (x + dx - w, y + dy - 150, x + dx + 60, y + dy + 150)
                if self.trong(b):
                    vach_mat_cat_dung(v, x + dx, y + dy, so)
                    self.hop.append(b)
                    return True
        vach_mat_cat_dung(v, x, y, so)
        self.loi_chong += 1
        self.that_bai.append((f"VACH {so}", x, y))
        return False

    def vach_dung_cap(self, x, y_tren, y_duoi, so, dxs=(0.0, 120.0, -120.0, 240.0, -240.0), dys=(0.0, 120.0, -120.0)) -> bool:
        """Ký hiệu mặt cắt dầm vẽ HAI LẦN (trên và dưới dầm) CÙNG x — đường cắt đi qua dầm. Tìm độ lệch ngang chung để cả hai
        vị trí đều trống; không được thì vẽ ở vị trí quy tắc và ghi nhận chồng."""
        v = self.v
        w = 0.9 * v.cfg.ty_le * 2.4 + len(str(so)) * HE_SO_RONG_CHU * v.h_chu * 1.25
        for dx in dxs:
            for dy in dys:
                bs = [(x + dx - w, yy + dy - 150, x + dx + 60, yy + dy + 150) for yy in (y_tren, y_duoi)]
                if all(self.trong(b) for b in bs):
                    for yy in (y_tren, y_duoi):
                        vach_mat_cat_dung(v, x + dx, yy + dy, so)
                    self.hop.extend(bs)
                    return True
        for yy in (y_tren, y_duoi):
            vach_mat_cat_dung(v, x, yy, so)
        self.loi_chong += 1
        self.that_bai.append((f"VACH {so}", x, y_tren))
        return False

    def vach_ngang(self, x, y, so, dys=(0.0, 200.0, -200.0, 400.0, -400.0)) -> bool:
        v = self.v
        dai = 6.0 * v.cfg.ty_le
        for dy in dys:
            b = (x - dai / 2, y + dy - 60, x + dai / 2, y + dy + 0.9 * v.cfg.ty_le + 1.6 * v.h_chu * 1.25)
            if self.trong(b):
                vach_mat_cat_ngang(v, x, y + dy, so)
                self.hop.append(b)
                return True
        return False  # cột: không có chỗ ⇒ bỏ ký hiệu phía này (phía kia vẫn có)


# ---------------------------------------------------------------------------
# DẦM
# ---------------------------------------------------------------------------


def _cum_gia_cuong(v: _Ve, cho: Cho, x_dan: float, y_thanh: float, yt: float, items: list[tuple[int, int, int]], ben: str) -> None:
    """D2: cụm [chữ xếp chồng][vòng tròn] ngay trên cốt sàn; `items` = [(n, Ø, số hiệu)]."""
    r = v.r_the
    lh = 1.45 * v.h_chu
    k = len(items)
    y_c = yt + D2_Y
    dong = [f"{n}Ø{dk}" for n, dk, _ in items]
    w_chu = max(len(s) for s in dong) * HE_SO_RONG_CHU * v.h_chu
    gap = 70.0
    if ben == "trai":
        x_chu0 = x_dan + gap
        x_vt0 = x_chu0 + w_chu + gap + r
        buoc = 2 * r + 50.0
        xs_vt = [x_vt0 + i * buoc for i in range(k)]
        hop = (x_dan, y_c - r, xs_vt[-1] + r, y_c + k * lh / 2 + 40)
        for i, s in enumerate(dong):
            v.chu(x_chu0, y_c + (k - 1) * lh / 2 - i * lh - 0.5 * v.h_chu, s, v.h_chu)
    else:
        x_chu1 = x_dan - gap
        x_vt0 = x_chu1 - w_chu - gap - r
        buoc = 2 * r + 50.0
        xs_vt = [x_vt0 - i * buoc for i in range(k)]
        hop = (xs_vt[-1] - r, y_c - r, x_dan, y_c + k * lh / 2 + 40)
        for i, s in enumerate(dong):
            v.chu(x_chu1, y_c + (k - 1) * lh / 2 - i * lh - 0.5 * v.h_chu, s, v.h_chu, phai=True)
    if k == 2:  # vạch ngăn giữa hai dòng chữ (khung chữ như bản mẫu)
        xa, xb = (x_chu0, x_chu0 + w_chu) if ben == "trai" else (x_chu1 - w_chu, x_chu1)
        v.doan(xa, y_c, xb, y_c, layers.TEXT.ten)
    for (n, dk, so), xv in zip(items, xs_vt):
        v.tron(xv, y_c, r, L_SH)
        v.chu(xv, y_c, str(so), v.h_chu, L_SH, giua=True)
        cho.so_nhan += 1
    v.doan(x_dan, y_thanh, x_dan, y_c - k * lh / 2 - 20.0, L_SH)  # đường dẫn đứng từ thanh lên cụm
    cho.vat_can(*hop)


def nhan_dam(kh: KeHoach, v: _Ve, cho: Cho, d: _Dam) -> None:
    cfg = kh.cfg
    cv = cfg.lop_bao_ve_dam
    L = d.l_tt
    xf1, xf2 = d.x1 + d.hc1 / 2, d.x2 - d.hc2 / 2
    yt, yb = d.y, d.y - d.h
    ngan = L < NHIP_NGAN_MM
    fx = lambda f: xf1 + f * L  # noqa: E731
    tl = kh.thanh_doc_dam[d.ten]
    dw = d.vung[0].duong_kinh
    suot = next((t for t in tl if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
    d_c = suot.duong_kinh if suot else 16
    y_suot = yt - cv - dw - d_c / 2
    y_ex = y_suot - 60.0
    kh_dai = kh.dai_dam[d.ten]

    # D1/D2 — thanh trên: có thanh gia cường ở gối nào ⇒ MỖI gối một cụm [thanh suốt + gia cường] (như bản mẫu "9 11 / 2Ø18 1Ø18");
    #         không có gia cường ⇒ chỉ 1 nhãn thanh suốt giữa nhịp.
    co_gc = bool(d._so_ben["trai"] or d._so_ben["phai"])  # type: ignore[attr-defined]
    if co_gc:
        for ben, f in (("trai", D2_X_TRAI), ("phai", D2_X_PHAI)):
            items = [(n, dk, th.so_hieu) for dk, lst in sorted(d._so_ben[ben].items(), reverse=True) for n, th in lst]  # type: ignore[attr-defined]
            if suot:
                items = [(suot.so_luong, suot.duong_kinh, suot.so_hieu)] + items
            if items:
                _cum_gia_cuong(v, cho, fx(f), y_ex, yt, items, ben)
    elif suot:
        x = fx(D1_X_NGAN if ngan else D1_X)
        cho.the(x, y_suot, x, yt + D1_Y, suot.so_hieu, f"{suot.so_luong}Ø{suot.duong_kinh}", 1)

    # D4 — dây kích thước vùng đai
    yC = yt + D4_Y
    so_dai_khac = len({z.so_hieu for z in kh_dai}) > 1
    if so_dai_khac:
        for vg in d.vung:
            xa, xb = xf1 + vg.tu_mm, xf1 + vg.den_mm
            v.kt((xa, yC), (xb, yC), f"{vg.chieu_dai:g}({vg.nhan()})", L_DIM)
            v.doan(xa, yC - 110, xa, yC + 110, L_DIM)
            v.doan(xb, yC - 110, xb, yC + 110, L_DIM)
    else:
        xa, xb = xf1, xf2
        v.kt((xa, yC), (xb, yC), f"{L:g}({d.vung[0].nhan()})", L_DIM)
        v.doan(xa, yC - 110, xa, yC + 110, L_DIM)
        v.doan(xb, yC - 110, xb, yC + 110, L_DIM)
    cho.vat_can(xf1, yC - 60, xf2, yC + 330)

    # D5 — nhãn đai
    if ngan:
        x = fx(0.18)
        cho.the(x, yt - cv, x, yt + D5_Y_NGAN_TREN, kh_dai[0].so_hieu, d.vung[0].nhan(), 1)
    elif not so_dai_khac:
        x = fx(D5_X_DONG_DEU)
        cho.the(x, yb + cv, x, yb - D5_Y_DUOI, kh_dai[0].so_hieu, d.vung[0].nhan(), 1)
    else:
        z_goi, z_giua = (kh_dai[0], d.vung[0]), None
        for i, z in enumerate(kh_dai):
            if i not in (0, len(kh_dai) - 1):
                z_giua = (z, d.vung[i])
        x1_, x2_ = fx(D5_X_GOI_TRAI), fx(D5_X_GOI_PHAI)
        cho.the(x1_, yb + cv, x1_, yb - D5_Y_DUOI, z_goi[0].so_hieu, z_goi[1].nhan(), 1)
        z_cuoi = (kh_dai[-1], d.vung[-1])
        cho.the(x2_, yb + cv, x2_, yb - D5_Y_DUOI, z_cuoi[0].so_hieu, z_cuoi[1].nhan(), 1)
        if z_giua:
            x = fx(D5_X_GIUA)
            cho.the(x, yt - cv, x, yt + D5_Y_GIUA_TREN, z_giua[0].so_hieu, z_giua[1].nhan(), 1)

    # D6 — thanh dưới
    if d.bot:
        dd = max(d.bot)
        y_d = yb + cv + dw + dd / 2
        x = fx(0.5 if ngan else D6_X)
        for i, (dk, n) in enumerate(sorted({k: d.bot.count(k) for k in set(d.bot)}.items(), reverse=True)):
            th = next(t for t in tl if t.vai_tro == "duoi" and t.duong_kinh == dk)
            cho.the(x, y_d, x, yb - D6_Y - i * 420.0, th.so_hieu, f"{n}Ø{dk}", 1)

    # D3 — ký hiệu mặt cắt (trên và dưới dầm, cùng x)
    da_ghi: set[int] = set()
    cac_mc = []
    for ben in ("trai", "giua", "phai"):
        so = kh.gan_mat_cat_dam[(d.ten, ben)]
        if so in da_ghi:
            continue
        da_ghi.add(so)
        f = (D3_X_NGAN if ngan and len(da_ghi) == 1 else D3_X[ben])
        cac_mc.append((so, f))
    if ngan and len(cac_mc) > 1:
        cac_mc = [(s, [0.2, 0.5, 0.8][i]) for i, (s, _) in enumerate(cac_mc)]
    for so, f in cac_mc:
        cho.vach_dung_cap(fx(f), yt + D3_Y_TREN, yb - D3_Y_DUOI, so)


# ---------------------------------------------------------------------------
# CỘT
# ---------------------------------------------------------------------------


def nhan_cot(kh: KeHoach, v: _Ve, cho: Cho, c: _Cot, ten_truc: list[str]) -> None:
    cfg = kh.cfg
    cv = cfg.lop_bao_ve_cot
    xc = kh.truc[c.truc]
    x0, x1 = xc - c.h / 2, xc + c.h / 2
    cuoi = c.truc == ten_truc[-1]
    la_t1 = abs(c.y0) < 1.0
    hb = max([d.h for d in kh.dams if abs(d.y - c.y1) < 1.0 and c.truc in (d.truc1, d.truc2)] or [0.0])
    y_ton_nen = cfg.cao_do_ton_nen_tren_dinh_mong
    y_bot = y_ton_nen if la_t1 else c.y0
    y_top = c.y1 - hb
    y_giua = (y_bot + y_top) / 2
    so_h, n_tong, _ = kh.thanh_doc_cot[c.ten]
    r = v.r_the

    # C1 — thép dọc bên phải cột
    cho.the(x1, y_giua, x1 + C1_LECH, y_giua, so_h, f"{n_tong}Ø{c.d}", 1, dys=(0.0, 150.0, -150.0, 300.0, -300.0, 450.0, -450.0), dxs=(0.0,))

    # C2 — đai
    dense = c.nhan_dai[0] if c.nhan_dai else None
    mid = c.nhan_dai[1] if len(c.nhan_dai) > 1 else None
    y_dense = (C2_Y_DAY_MONG if la_t1 else c.y0 + C2_Y_DAY_TREN_SAN)
    y_mid = y_top - C2_Y_GIUA_DUOI_DAM
    ds = []
    if dense:
        ds.append((dense, y_dense))
    if mid and (not dense or mid[0] != dense[0]):
        ds.append((mid, y_mid))
    quet = (0.0, -200.0, -400.0, -600.0, -800.0, -1000.0, -1200.0, 200.0)
    for (so, nhan), y in ds:
        if cuoi:
            cho.the(x1, y, x1 + C2_LECH_PHAI, y, so, nhan, 1, dys=quet, dxs=(0.0,))
        else:
            xt = x0 - C2_LECH_TRAI
            for dy_ in quet:
                if cho.trong(cho.hop_the(xt, y + dy_, nhan, 1)):
                    y = y + dy_
                    break
            b = cho.hop_the(xt, y, nhan, 1)
            ok = cho.trong(b)
            vong_tron_so_hieu(v, xt, y, xt, y, so, nhan, 1)  # vòng tròn + chữ (đường dẫn dài 0)
            x_cuoi_chu = xt + r + 0.5 * v.h_chu_nho + cho.chieu_rong_chu(nhan)
            v.doan(x_cuoi_chu + 40.0, y, x0, y, L_SH)  # đường dẫn từ cuối chữ tới cột
            cho.hop.append((b[0], b[1], x0, b[3]))
            cho.so_nhan += 1
            if not ok:
                cho.loi_chong += 1
                cho.that_bai.append((f"COT {c.ten} {so} {nhan}", xt, y))

    # C3 — ký hiệu mặt cắt cột: vạch ngang, số trên vạch, hai bên cột
    cac = []
    s0 = kh.gan_mat_cat_cot.get((c.ten, 0))
    if s0:
        cac.append((s0, (700.0 if la_t1 else c.y0 + C3_Y_DAY_TREN_SAN)))
    s1 = kh.gan_mat_cat_cot.get((c.ten, 1)) if len(c.vung) > 1 else None
    if s1 and s1 != s0:
        cac.append((s1, y_top - C3_Y_GIUA_DUOI_DAM))
    for so, y in cac:
        cho.vach_ngang(x0 - C3_LECH, y, so)
        cho.vach_ngang(x1 + C3_LECH, y, so)
