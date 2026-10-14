"""Bố cục TỜ VẼ và hàm vào chính `lap_ban_ve_khung`.

Bố cục (toạ độ model, mm thật ở tỷ lệ in 1:ty_le):
  trái: mặt đứng khung, phía trên là dải hình chi tiết nút 3D (thu nhỏ vừa MỘT hàng) | giữa: lưới mặt cắt (dầm trước, cột sau) |
  phải: bảng thống kê, ghi chú, khung tên.
Chọn tự động (tỷ lệ in, khổ giấy) nhỏ nhất đủ chỗ theo thứ tự ưu tiên `UU_TIEN`; hệ số phóng mặt cắt tự giảm khi cấu kiện
lớn. Không vừa khổ nào ⇒ vẽ ở phương án ít tràn nhất và ghi cảnh báo rõ.
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass

from .. import layers
from ..geometry import BanVe
from . import bang, chi_tiet_nut, mat_cat, mat_dung
from .co_so import CauHinhToVe, KetQuaToVe, _Ve
from .ke_hoach import lap_ke_hoach

KHO_GIAY = {"A1": (841.0, 594.0), "A0": (1189.0, 841.0)}
UU_TIEN = [("A1", 50.0), ("A0", 50.0), ("A1", 75.0), ("A0", 75.0), ("A1", 100.0), ("A0", 100.0)]
RONG_KHOI_PHAI = 7900.0
KHOANG = 400.0
HE_SO_3D = 1.6  # phóng hình chi tiết nút 3D (so với mm thật)
RONG_MAT_CAT_TOI_DA_GIAY_MM = 44.0  # bề rộng lớn nhất của một mặt cắt trên giấy (quyết định hệ số phóng)


def _dung_cho_khac(v: _Ve, x: float, y: float, w: float, h: float) -> bool:
    """Hộp chữ (x..x+w, y..y+h) có đè chữ hoặc vòng tròn số hiệu đã vẽ trong `v` không (ước lượng bề rộng chữ 0,6·cao·số ký tự)."""
    for c in v.bv.chu:
        wc = len(c.noi_dung) * 0.6 * c.chieu_cao
        xa = c.vi_tri.x - wc / 2 if c.canh_giua else (c.vi_tri.x - wc if c.canh_phai else c.vi_tri.x)
        if xa < x + w and x < xa + wc and c.vi_tri.y - 0.6 * c.chieu_cao < y + h and y < c.vi_tri.y + 1.1 * c.chieu_cao:
            return True
    for t in v.bv.vong_tron:
        if t.layer == layers.SO_HIEU.ten and abs(t.tam.x - (x + w / 2)) < t.ban_kinh + w / 2 and abs(t.tam.y - (y + h / 2)) < t.ban_kinh + h:
            return True
    return False


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


@dataclass
class _UngVien:
    cfg: CauHinhToVe
    kho: str
    vua: bool
    do_tran: float
    ket_qua: KetQuaToVe


def _he_so_phong(cfg: CauHinhToVe, kh) -> float:
    """Hệ số phóng mặt cắt: tối đa `cfg.he_so_mat_cat`, giảm khi cấu kiện lớn sao cho bề rộng mặt cắt ≤ ~44 mm giấy."""
    T = cfg.ty_le
    rong_max = max([mat_cat.rong_bao_dam(d.b, cfg) for d in kh.dams] + [c.h for c in kh.cots] + [1.0])
    k = RONG_MAT_CAT_TOI_DA_GIAY_MM * T / rong_max
    return max(1.0, min(cfg.he_so_mat_cat, math.floor(k * 2) / 2))


def _thu(du_lieu: dict, cfg: CauHinhToVe, kho: str) -> _UngVien:
    kh = lap_ke_hoach(du_lieu, cfg)
    T = cfg.ty_le
    K = _he_so_phong(cfg, kh)
    rg, cg = KHO_GIAY[kho]
    W, H = rg * T, cg * T
    canh_bao = list(kh.canh_bao)
    if kh.dam_thieu_q:
        canh_bao.append("Dầm " + ", ".join(kh.dam_thieu_q) + ": đai CHỈ theo cấu tạo, chưa kiểm chịu cắt (thiếu Q từ ETABS).")

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
        nhan_ct = f"CHI TIẾT {n['ten']}"
        if n["mai"]:  # tầng mái: nhãn phía trên khung (bản mẫu)
            v_md.chu((x0 + x1) / 2, y1 + 120.0, nhan_ct, v_md.h_chu_nho, giua=True)
        elif n["trai"] is None:  # nút biên trái: nhãn bên trái khung, ngang tâm khung
            v_md.chu(x0 - 120.0, (y0 + y1) / 2 - 0.36 * v_md.h_chu_nho, nhan_ct, v_md.h_chu_nho, phai=True)
        else:  # nút giữa: nhãn dưới khung, thử các vị trí cho tới khi không đè chữ/vòng tròn khác
            w_ct = len(nhan_ct) * 0.6 * v_md.h_chu_nho
            ung_vien = [(x0 + 100.0, y0 - 380.0, True), (x0 + 100.0, y0 - 1100.0, True), (x1 - 100.0 - w_ct, y0 - 1100.0, False),
                        (x0 + 100.0, y0 - 1800.0, True), (x1 + 200.0, y0 - 380.0, False)]
            chon = next((c for c in ung_vien if not _dung_cho_khac(v_md, c[0] if not c[2] else c[0] - w_ct, c[1], w_ct, v_md.h_chu_nho)), ung_vien[0])
            v_md.chu(chon[0], chon[1], nhan_ct, v_md.h_chu_nho, phai=chon[2])
    # ---- mặt cắt ----
    suot = {t.so_hieu for lst in kh.thanh_doc_dam.values() for t in lst if t.vai_tro in ("tren_suot", "tren_suot_chung")}
    mcs = []
    for md in kh.mat_cat:
        if md.loai == "dam":
            v, w, h, goc = mat_cat.ve_mat_cat_dam(cfg, md, K, suot)
        else:
            v, w, h, goc = mat_cat.ve_mat_cat_cot(cfg, md, K)
        mcs.append((md, v, w, h, goc))
    nhom = {"dam": [m for m in mcs if m[0].loai == "dam"], "cot": [m for m in mcs if m[0].loai == "cot"]}
    cell = {k: (max((m[2] for m in ls), default=0.0) + KHOANG, max((m[3] for m in ls), default=0.0) + KHOANG) for k, ls in nhom.items()}

    # ---- 3D ----
    def _ve_3d(he_so: float):
        return [chi_tiet_nut.ve_chi_tiet_nut(kh, n["ten"], n["cot"], n["phai"], n["trai"], n["mai"], he_so) for n in nut]

    he_3d = HE_SO_3D
    ds3 = _ve_3d(he_3d)
    # Hình chi tiết nút xếp lưới NGAY DƯỚI mặt đứng (cùng cột trái, như bản mẫu đặt cụm chi tiết cạnh mặt đứng). Cần ít nhất 2 hình
    # một hàng: thu nhỏ (chữ/nhãn giữ cỡ giấy nên bề rộng không tỷ lệ thuận) tới khi vừa, không nhỏ hơn 0,8.
    while ds3 and he_3d > 0.8 and w_el // (max(w for _, w, _, _ in ds3) + KHOANG) < min(2, len(ds3)):
        he_3d = max(0.8, he_3d * 0.9)
        ds3 = _ve_3d(he_3d)

    # ---- kiểm tra chỗ ----
    x_sec0 = 25 * T + 500.0 + w_el + KHOANG
    x_sec1 = W - 5 * T - RONG_KHOI_PHAI - KHOANG
    rong_vung = x_sec1 - x_sec0
    cao_vung = H - 10 * T - 800.0
    tran = 0.0
    luoi: dict[str, tuple[int, int]] = {}
    tong_cao = 0.0
    for k, ls in nhom.items():
        if not ls:
            luoi[k] = (1, 0)
            continue
        cw, ch = cell[k]
        cols = max(1, int(rong_vung // cw))
        rows = math.ceil(len(ls) / cols)
        luoi[k] = (cols, rows)
        tong_cao += rows * ch
        tran += max(0.0, cw - rong_vung)
    tran += max(0.0, tong_cao - cao_vung)
    if ds3:
        cw3 = max(w for _, w, _, _ in ds3) + KHOANG
        ch3 = max(h for _, _, h, _ in ds3) + KHOANG
        cols3 = max(1, int(w_el // cw3))
        rows3 = math.ceil(len(ds3) / cols3)
        y_free = 5 * T + 300.0  # mép dưới vùng vẽ (trên khung)
        y_dinh_3d = H - 5 * T - 400.0 - h_el - 600.0  # ngay dưới mặt đứng
        du_3d = (y_dinh_3d - rows3 * ch3) >= y_free
        if not du_3d:
            tran += y_free - (y_dinh_3d - rows3 * ch3)
    else:
        cw3 = ch3 = 0.0
        cols3 = 1
        du_3d = True
    tran += max(0.0, h_el - (H - 10 * T))
    vua = tran <= 1e-6

    # ---- ghép ----
    tong = BanVe(ten="TO_VE_KHUNG")
    khung = _Ve(cfg, "KHUNG")
    bang.ve_khung_to(cfg, khung, W, H)
    tong.gop(khung.bv)
    tong.gop(v_md.bv.dich_chuyen(25 * T + 500.0 - info["x_trai"], H - 5 * T - 400.0 - info["y_cao"]))  # mặt đứng ở ĐẦU cột trái

    mat_cat_ve: list[dict] = []
    y_cur = H - 5 * T - 400.0
    for k in ("dam", "cot"):
        ls = nhom[k]
        if not ls:
            continue
        cw, ch = cell[k]
        cols, rows = luoi[k]
        for i, (md, v, w, h, (ox, oy)) in enumerate(ls):
            c, r = i % cols, i // cols
            tong.gop(v.bv.dich_chuyen(x_sec0 + c * cw - ox, y_cur - (r + 1) * ch - oy))
            if md.loai == "dam":
                rong_ve, cao_ve = mat_cat.rong_bao_dam(md.b, cfg) * K, md.h * K
            else:
                rong_ve, cao_ve = md.h * K, md.b * K
            mat_cat_ve.append({"nhan": f"{md.so}-{md.so}", "loai": md.loai, "b": md.b, "h": md.h, "rong_ve": rong_ve, "cao_ve": cao_ve})
        y_cur -= rows * ch

    if ds3 and du_3d:
        y_3d_top = y_dinh_3d
        for i, (v3, w3, h3, (ox3, oy3)) in enumerate(ds3):
            c3, r3 = i % cols3, i // cols3
            tong.gop(v3.bv.dich_chuyen(25 * T + 500.0 + c3 * cw3 - ox3, y_3d_top - (r3 + 1) * ch3 - oy3))
    elif ds3:
        canh_bao.append("Không đủ chỗ cho hình chi tiết nút 3D trên khổ giấy đã chọn (bỏ qua).")

    # khối phải: bảng thống kê (trên) → ghi chú → khung tên (dưới cùng)
    x_ph = W - 5 * T - RONG_KHOI_PHAI
    vb = _Ve(cfg, "BANG")
    _, cao_bang = bang.ve_bang_thong_ke(kh, vb, x_ph, H - 5 * T - 400.0)
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
        tran += 1.0
        vua = False
        canh_bao.append("Bảng thống kê + ghi chú chạm khung tên — cần khổ giấy/tỷ lệ lớn hơn.")
    if info.get("loi_chong_nhan"):
        canh_bao.append(f"{info['loi_chong_nhan']} nhãn trên mặt đứng chưa tránh được chồng nhau — cần xem bằng mắt/dời tay.")
    if info.get("nhan_rut_gon"):
        canh_bao.append(f"{info['nhan_rut_gon']} nhãn thép ở nhịp ngắn chỉ ghi số hiệu (đủ chữ xem bảng thống kê).")
    if not vua:
        canh_bao.append(f"Không đủ chỗ trên khổ {kho} (1:{T:g}): có thể tràn {tran:.0f} mm.")
    elif T != 50.0 or kho != "A1":
        canh_bao.append(f"Tờ vẽ {kho} tỷ lệ 1:{T:g} (tự chọn để đủ chỗ).")

    kq = KetQuaToVe(
        ban_ve=tong, thong_ke=bang.dong_thong_ke(kh), so_cot=len(kh.cots), so_dam=len(kh.dams),
        so_ky_hieu_ky_vong=sum(1 for c in tong.vong_tron if c.layer == layers.SO_HIEU.ten),
        mat_cat=mat_cat_ve, he_so_mat_cat=K, canh_bao=canh_bao, kho_giay=kho,
        so_da_giac_outline=sum(1 for dg in tong.da_giac if dg.layer == layers.OUTLINE.ten),
        ty_le_in=T, so_cung_uon=sum(1 for c in tong.cung if c.layer == layers.REBAR_BAR.ten), dam_thieu_q=list(kh.dam_thieu_q),
    )
    return _UngVien(cfg, kho, vua, tran, kq)


def lap_ban_ve_khung(du_lieu: dict, cfg: CauHinhToVe | None = None) -> KetQuaToVe:
    """Dựng tờ vẽ. Tỷ lệ in/khổ giấy do hàm chọn (A1 1:50 → A0 1:50 → A1 1:75 → …) trừ khi `cfg.co_dinh_ty_le`."""
    cfg = cfg or CauHinhToVe()
    ung_vien: list[_UngVien] = []
    ds = [("A1", cfg.ty_le), ("A0", cfg.ty_le)] if cfg.co_dinh_ty_le else UU_TIEN
    for kho, T in ds:
        uv = _thu(du_lieu, dataclasses.replace(cfg, ty_le=T), kho)
        if uv.vua:
            return uv.ket_qua
        ung_vien.append(uv)
    return min(ung_vien, key=lambda u: u.do_tran).ket_qua
