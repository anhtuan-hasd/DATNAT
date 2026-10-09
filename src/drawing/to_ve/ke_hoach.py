"""Kế hoạch bố trí thép toàn khung (CHƯA vẽ): đọc dữ liệu, đặt cột/dầm theo lưới trục + cao độ THẬT, dựng lược đồ thanh
dọc dầm (skill 06 B2–B8), cốt đai theo vùng (`rule_engine.bo_tri_dai`), cấp số hiệu thanh, và danh sách mặt cắt cần vẽ.

Tách khỏi phần vẽ để test được số liệu (chiều dài thanh, số lượng, số hiệu, vùng đai) không cần hình học.
Nhãn nguồn các quy tắc nằm trong chú thích hàm; những chỗ là bố trí SƠ BỘ theo thực hành (skill ghi [thực hành]/
[kinh nghiệm]) được gom vào `KeHoach.canh_bao` để in ra tờ vẽ.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

from ...rule_engine import bo_tri_dai as dai
from ...rule_engine.vat_lieu import dien_tich_1_thanh
from ..so_hieu_thanh import SoDangKySoHieu, ThanhThep
from .co_so import CauHinhToVe, _Cot, _Dam, _ThanhDocVe, _dem_theo_d, _doc_cot, _doc_dam, _ten_tang, _tru_da_tap

KHOANG_HO_DAU_MUT_MM = 0.0


@dataclass
class ThanhDai:
    """Một nhóm cốt đai trên bản vẽ: cùng Ø, cùng kích thước, cùng bước (số hiệu riêng theo bước)."""

    so_hieu: int
    duong_kinh: int
    rong: float  # kích thước trong của đai (mm)
    cao: float
    chieu_dai: float
    buoc: float
    so_luong: int
    cau_kien: str


@dataclass
class MatCatDinhNghia:
    """Một mặt cắt cần vẽ (đã khử trùng)."""

    so: int
    loai: str  # "dam" | "cot"
    b: float
    h: float
    tren: list[tuple[int, int, int]]  # [(duong_kinh, so_luong, so_hieu)] — thép trên (dầm) / không dùng (cột)
    duoi: list[tuple[int, int, int]]
    dai: tuple[int, str]  # (số hiệu, "Ø6a150")
    ten_cau_kien: str = ""
    cao_do_nhan: str = ""  # nhãn cao độ sàn ('TẦNG 3 +3.200') cho dầm
    truc: str = ""  # tên trục (cột)
    cot: dict | None = None  # {"d","n_b","n_h","so_hieu"} cho cột


@dataclass
class KeHoach:
    cfg: CauHinhToVe
    truc: dict[str, float]
    moc: dict[str, float]
    cots: list[_Cot]
    dams: list[_Dam]
    so_dk: SoDangKySoHieu
    thanh_doc_dam: dict[str, list[_ThanhDocVe]]  # theo tên dầm
    dai_dam: dict[str, list[ThanhDai]]
    dai_cot: dict[str, list[ThanhDai]]
    thanh_doc_cot: dict[str, tuple[int, int, float]]  # tên cột → (số hiệu, số thanh, chiều dài)
    mat_cat: list[MatCatDinhNghia]
    gan_mat_cat_dam: dict[tuple[str, str], int]  # (tên dầm, "trai"/"giua"/"phai") → số mặt cắt
    gan_mat_cat_cot: dict[tuple[str, int], int]  # (tên cột, chỉ số vùng đai) → số mặt cắt
    canh_bao: list[str] = field(default_factory=list)
    be_rong_dai: dict[str, float] = field(default_factory=dict)  # theo trục


def _cot_tai(cots: list[_Cot], truc: str, y: float) -> _Cot | None:
    """Cột tại trục `truc` có đầu trên hoặc dưới trùng cao độ `y` (ưu tiên đoạn BÊN DƯỚI mặt sàn)."""
    ung = [c for c in cots if c.truc == truc]
    duoi = [c for c in ung if abs(c.y1 - y) < 1.0]
    tren = [c for c in ung if abs(c.y0 - y) < 1.0]
    return (duoi or tren or [None])[0]


def _lam_tron_50(x: float) -> float:
    return round(x / 50.0) * 50.0


def _thanh_gia_cuong(tap: list[int], d_c: int, n_c: int) -> dict[int, int]:
    """Thanh gia cường tại 1 gối = thép gối (`tap`) trừ phần đã có ở thanh trên chạy suốt (`n_c` thanh Ø`d_c`).
    Quy đổi theo Ø bằng nhau trước; nếu gối không có thanh Ø`d_c` thì quy theo DIỆN TÍCH (thanh suốt đã đủ ⇒ không cần
    thêm; thiếu ⇒ thêm thanh Ø lớn nhất của gối). Luôn bảo đảm As bố trí ≥ As của `tap`."""
    if not tap:
        return {}
    if not d_c:
        return _dem_theo_d(tap)
    con = list(tap)
    da_tru = 0
    for _ in range(n_c):
        if d_c in con:
            con.remove(d_c)
            da_tru += 1
    if da_tru == n_c:
        return _dem_theo_d(con)
    a_can = sum(dien_tich_1_thanh(x) for x in tap)
    a_co = n_c * dien_tich_1_thanh(d_c)
    if a_co >= a_can - 1e-6:
        return {}
    d_e = max(tap)
    return {d_e: int(math.ceil((a_can - a_co) / dien_tich_1_thanh(d_e) - 1e-9))}


def lap_ke_hoach(du_lieu: dict, cfg: CauHinhToVe) -> KeHoach:
    truc: dict[str, float] = {k: float(v) for k, v in du_lieu["toa_do_truc"].items()}
    moc: dict[str, float] = {k: float(v) for k, v in du_lieu["cao_do_moc"].items()}
    cots = [c for c in (_doc_cot(p, truc, moc) for p in du_lieu["phan_tu"] if p["loai"] == "cot") if c]
    dams = [d for d in (_doc_dam(p, truc, moc) for p in du_lieu["phan_tu"] if p["loai"] == "dam") if d]
    cots.sort(key=lambda c: (truc[c.truc], c.y0))
    dams.sort(key=lambda d: (d.y, d.x1))
    canh_bao: list[str] = []
    so_dk = SoDangKySoHieu()

    # --- thông thuỷ dầm, đầu biên/giữa ---
    for d in dams:
        c1, c2 = _cot_tai(cots, d.truc1, d.y), _cot_tai(cots, d.truc2, d.y)
        d.hc1 = c1.h if c1 else 300.0
        d.hc2 = c2.h if c2 else 300.0
        d.l_tt = (d.x2 - d.x1) - d.hc1 / 2 - d.hc2 / 2
    cung_tang: dict[str, list[_Dam]] = defaultdict(list)
    for d in dams:
        cung_tang[d.tang].append(d)

    def co_dam_ke(d: _Dam, ben: str) -> _Dam | None:
        for k in cung_tang[d.tang]:
            if k is d:
                continue
            if ben == "trai" and abs(k.x2 - d.x1) < 1.0:
                return k
            if ben == "phai" and abs(k.x1 - d.x2) < 1.0:
                return k
        return None

    cv = cfg.lop_bao_ve_dam
    thanh_doc_dam: dict[str, list[_ThanhDocVe]] = {d.ten: [] for d in dams}
    d_tren_suot: dict[str, int] = {}
    so_tren_suot: dict[str, int] = {}

    # --- thanh trên chạy suốt theo CHUỖI dầm liền nhau cùng tầng ---
    da_xet: set[str] = set()
    for d in dams:
        if d.ten in da_xet:
            continue
        chuoi = [d]
        while True:
            ke = co_dam_ke(chuoi[0], "trai")
            if ke is None or ke.ten in {c.ten for c in chuoi}:
                break
            chuoi.insert(0, ke)
        while True:
            ke = co_dam_ke(chuoi[-1], "phai")
            if ke is None or ke.ten in {c.ten for c in chuoi}:
                break
            chuoi.append(ke)
        for c in chuoi:
            da_xet.add(c.ten)
        tat_ca = [x for c in chuoi for x in (c.top_l, c.top_r) if x]
        if tat_ca:
            # Ø thanh suốt = lớn nhất trong các "Ø nhỏ nhất của từng gối" (thanh suốt phải có mặt ở MỌI gối; gối nào nhỏ hơn
            # thì thanh suốt đã đủ diện tích, không cần gia cường thêm — xem `_thanh_gia_cuong`)
            d_c = max(min(s) for s in tat_ca)
            n_c = min(2, min(len(s) for s in tat_ca))
        else:
            d_c, n_c = 0, 0
        for c in chuoi:
            d_tren_suot[c.ten], so_tren_suot[c.ten] = d_c, n_c
        if n_c:
            x_tr = chuoi[0].x1 - chuoi[0].hc1 / 2 + cv
            x_ph = chuoi[-1].x2 + chuoi[-1].hc2 / 2 - cv
            h_min = min(c.h for c in chuoi)
            l_hook = min(max(15.0 * d_c, 250.0), h_min - 2 * cv - 50.0)
            chieu_dai = (x_ph - x_tr) + 2 * l_hook
            thanh_doc_dam[chuoi[0].ten].append(_ThanhDocVe("tren_suot", d_c, n_c, chieu_dai))
            for c in chuoi[1:]:
                thanh_doc_dam[c.ten].append(_ThanhDocVe("tren_suot_chung", d_c, n_c, 0.0))

    # --- thanh gia cường gối (trên) + thanh dưới ---
    for d in dams:
        d_c, n_c = d_tren_suot.get(d.ten, 0), so_tren_suot.get(d.ten, 0)
        x_cat = max(50.0, _lam_tron_50(d.l_tt / 4.0))
        l_hook = max(100.0, min(max(15.0 * (d_c or 16), 250.0), d.h - 2 * cv - 50.0))
        d._extras_l = _thanh_gia_cuong(d.top_l, d_c, n_c)  # type: ignore[attr-defined]
        d._extras_r = _thanh_gia_cuong(d.top_r, d_c, n_c)  # type: ignore[attr-defined]
        d._x_cat, d._l_hook = x_cat, l_hook  # type: ignore[attr-defined]
        d._so_ben = {"trai": {}, "phai": {}}  # type: ignore[attr-defined]  # {Ø: [(số lượng, thanh)]}

    for d in dams:
        tl = thanh_doc_dam[d.ten]
        ke_trai, ke_phai = co_dam_ke(d, "trai"), co_dam_ke(d, "phai")
        # --- gối trái ---
        for dk, n in d._extras_l.items():  # type: ignore[attr-defined]
            if ke_trai is None:
                t = _ThanhDocVe("tren_cat_trai", dk, n, (d.hc1 - cv) + d._x_cat + d._l_hook)  # type: ignore[attr-defined]
                tl.append(t)
                d._so_ben["trai"].setdefault(dk, []).append((n, t))  # type: ignore[attr-defined]
            else:
                n_ke = ke_trai._extras_r.get(dk, 0)  # type: ignore[attr-defined]
                xuyen = min(n, n_ke)
                if xuyen:  # thanh xuyên cột: tính 1 lần (ở dầm bên phải của nút)
                    t = _ThanhDocVe("tren_cat_nut", dk, xuyen, ke_trai._x_cat + d.hc1 + d._x_cat)  # type: ignore[attr-defined]
                    tl.append(t)
                    d._so_ben["trai"].setdefault(dk, []).append((xuyen, t))  # type: ignore[attr-defined]
                    ke_trai._so_ben["phai"].setdefault(dk, []).append((xuyen, t))  # type: ignore[attr-defined]
                if n - xuyen:  # còn lại: nhô qua cột ≥ 20d (B5)
                    t = _ThanhDocVe("tren_cat_trai", dk, n - xuyen, d._x_cat + d.hc1 + 20.0 * dk)  # type: ignore[attr-defined]
                    tl.append(t)
                    d._so_ben["trai"].setdefault(dk, []).append((n - xuyen, t))  # type: ignore[attr-defined]
        # --- gối phải ---
        for dk, n in d._extras_r.items():  # type: ignore[attr-defined]
            if ke_phai is None:
                t = _ThanhDocVe("tren_cat_phai", dk, n, (d.hc2 - cv) + d._x_cat + d._l_hook)  # type: ignore[attr-defined]
                tl.append(t)
                d._so_ben["phai"].setdefault(dk, []).append((n, t))  # type: ignore[attr-defined]
            else:
                n_ke = ke_phai._extras_l.get(dk, 0)  # type: ignore[attr-defined]
                con = n - min(n, n_ke)
                if con:
                    t = _ThanhDocVe("tren_cat_phai", dk, con, d._x_cat + d.hc2 + 20.0 * dk)  # type: ignore[attr-defined]
                    tl.append(t)
                    d._so_ben["phai"].setdefault(dk, []).append((con, t))  # type: ignore[attr-defined]
        # --- thanh dưới: chạy hết thông thuỷ; biên = tới mặt ngoài cột − lớp bảo vệ + móc; giữa = tới tim cột ---
        for dk, n in _dem_theo_d(d.bot).items():
            e1 = (d.hc1 - cv) + d._l_hook if ke_trai is None else d.hc1 / 2  # type: ignore[attr-defined]
            e2 = (d.hc2 - cv) + d._l_hook if ke_phai is None else d.hc2 / 2  # type: ignore[attr-defined]
            tl.append(_ThanhDocVe("duoi", dk, n, d.l_tt + e1 + e2))

    # --- cấp số hiệu thanh dọc dầm theo thứ tự xuất hiện ---
    for d in dams:
        for t in thanh_doc_dam[d.ten]:
            if t.chieu_dai > 0:
                t.so_hieu = so_dk.lay_so_hieu(ThanhThep(t.duong_kinh, round(t.chieu_dai)))
    for d in dams:  # thanh suốt "chung": dùng số hiệu của thanh suốt đầu chuỗi (cùng tầng, cùng Ø, cùng chiều dài)
        for t in thanh_doc_dam[d.ten]:
            if t.vai_tro == "tren_suot_chung":
                for x in dams:
                    if x.tang == d.tang:
                        g_ = next((y for y in thanh_doc_dam[x.ten] if y.vai_tro == "tren_suot" and y.duong_kinh == t.duong_kinh), None)
                        if g_:
                            t.so_hieu = g_.so_hieu
                            break

    # --- cột: thanh dọc + đai ---
    thanh_doc_cot: dict[str, tuple[int, int, float]] = {}
    thieu_dai: list[str] = []  # phần tử mà agent chưa chốt đai (tool bo_tri_dai) — dùng đai cấu tạo mặc định
    dai_cot: dict[str, list[ThanhDai]] = {}
    tang_thap_nhat = min(moc.values())
    dai_dam: dict[str, list[ThanhDai]] = {}
    be_rong_dai: dict[str, float] = {}
    for c in cots:
        la_tang1 = abs(c.y0 - tang_thap_nhat) < 1.0
        la_tang_cuoi = abs(c.y1 - max(moc.values())) < 1.0
        l_lap = c.l_lap or cfg.chieu_dai_nen_noi_mac_dinh * c.d
        if not c.l_lap:
            canh_bao.append(f"Cột {c.ten}: không có L_lap từ tool — dùng {cfg.chieu_dai_nen_noi_mac_dinh:g}d [thực hành].")
        chan = 0.0
        if la_tang1:
            chan = (cfg.day_dai_mong - 75.0) + 200.0  # thép chờ: sâu hết đài (trừ lớp bảo vệ đáy) + chân L 200 [NK-16]
        chieu_dai = (c.y1 - c.y0) + (0.0 if la_tang_cuoi else l_lap) + chan
        so_hieu = so_dk.lay_so_hieu(ThanhThep(c.d, round(chieu_dai)))
        thanh_doc_cot[c.ten] = (so_hieu, c.n_tong, chieu_dai)
        c.so_hieu_thep = so_hieu
        # đai
        ag = c.raw.get("dai") or {}
        if not ag:
            thieu_dai.append(f"cột {c.ten}")
        dd = int(ag.get("duong_kinh_dai") or dai.chon_duong_kinh_dai(c.d))
        hb = max([d.h for d in dams if abs(d.y - c.y1) < 1.0 and c.truc in (d.truc1, d.truc2)] or [0.0])
        h_tt = (c.y1 - c.y0) - hb
        vung = dai.bo_tri_dai_cot(
            max(c.b, c.h), h_tt, c.d, c.d, chieu_dai_noi=0.0 if la_tang_cuoi else min(l_lap, h_tt / 3.0),
            duong_kinh_dai=ag.get("duong_kinh_dai"), buoc_dau=ag.get("buoc_dau"), buoc_giua=ag.get("buoc_giua"),
        )
        # vùng nút (trong chiều cao dầm trên): đai liên tục, bước hai đầu
        s_nut = vung[-1].buoc_mm
        vung = vung + [dai.VungDai(h_tt, h_tt + hb, s_nut, dd)] if hb else vung
        c.vung = vung
        ds: list[ThanhDai] = []
        cvc = cfg.lop_bao_ve_cot
        rong, cao = c.b - 2 * cvc, c.h - 2 * cvc
        chieu_dai_dai = 2 * (rong + cao) + 2 * max(8.0 * dd, 50.0)
        for i, v in enumerate(vung):
            nhom = v.buoc_mm
            so_luong = v.so_dai + (3 if (i == 0 and la_tang1) else 0)  # đai trong đài móng (NK-16)
            sh = so_dk.lay_so_hieu(ThanhThep(dd, round(chieu_dai_dai), f"a{nhom:g}"))
            ds.append(ThanhDai(sh, dd, rong, cao, chieu_dai_dai, nhom, so_luong, c.ten))
            c.nhan_dai.append((sh, v.nhan()))
        dai_cot[c.ten] = ds
        if la_tang1:
            be_rong_dai[c.truc] = max(be_rong_dai.get(c.truc, 0.0), c.h + 2 * cfg.rong_dai_them_moi_ben)

    # --- đai dầm ---
    for d in dams:
        d_all = [x for s in (d.top_l, d.top_r, d.bot) for x in s]
        d_max, d_min = (max(d_all), min(d_all)) if d_all else (16, 16)
        ag = d.raw.get("dai") or {}
        if not ag:
            thieu_dai.append(f"dầm {d.ten}")
        vung = dai.bo_tri_dai_dam(
            d.h, d.l_tt, d_max, d_min,
            duong_kinh_dai=ag.get("duong_kinh_dai"), buoc_goi=ag.get("buoc_goi"), buoc_giua=ag.get("buoc_giua"),
        )
        d.vung = vung
        dd = vung[0].duong_kinh
        rong, cao = d.b - 2 * cv, d.h - 2 * cv
        cd = 2 * (rong + cao) + 2 * max(8.0 * dd, 50.0)
        lst = []
        for v in vung:
            sh = so_dk.lay_so_hieu(ThanhThep(dd, round(cd), f"a{v.buoc_mm:g}"))
            lst.append(ThanhDai(sh, dd, rong, cao, cd, v.buoc_mm, v.so_dai, d.ten))
        dai_dam[d.ten] = lst

    if thieu_dai:
        canh_bao.append(
            f"{len(thieu_dai)} phần tử chưa có quyết định đai từ Rule Engine Agent (tool bo_tri_dai): "
            + ", ".join(thieu_dai[:6]) + (" …" if len(thieu_dai) > 6 else "") + " — dùng đai cấu tạo mặc định [thực hành]."
        )
    kh = KeHoach(cfg, truc, moc, cots, dams, so_dk, thanh_doc_dam, dai_dam, dai_cot, thanh_doc_cot, [], {}, {}, canh_bao, be_rong_dai)
    _lap_mat_cat(kh)
    return kh


# ---------------------------------------------------------------------------
# Mặt cắt (khử trùng)
# ---------------------------------------------------------------------------


def _nhom_so_hieu(kh: KeHoach, d: _Dam, ds: list[int], vai_tro_gom: tuple[str, ...]) -> list[tuple[int, int, int]]:
    """[(Ø, số lượng, số hiệu)] cho nhóm thanh `ds` của 1 mặt cắt — tra số hiệu từ lược đồ thanh dọc của dầm."""
    ket = []
    for dk, n in _dem_theo_d(ds).items():
        so = 0
        for t in kh.thanh_doc_dam[d.ten]:
            if t.duong_kinh == dk and t.vai_tro in vai_tro_gom and t.so_hieu:
                so = t.so_hieu
                break
        ket.append((dk, n, so))
    return ket


def _lap_mat_cat(kh: KeHoach) -> None:
    cfg = kh.cfg
    khoa_ds: dict[tuple, int] = {}
    ds_mc: list[MatCatDinhNghia] = []

    def them(khoa: tuple, tao) -> int:
        if khoa not in khoa_ds:
            so = len(ds_mc) + 1
            khoa_ds[khoa] = so
            ds_mc.append(tao(so))
        return khoa_ds[khoa]

    cos = lambda y: y - cfg.cao_do_ton_nen_tren_dinh_mong  # noqa: E731

    for d in kh.dams:
        dai_ds = kh.dai_dam[d.ten]
        tang_nhan = f"{_ten_tang(d.tang)}  {cos(d.y) / 1000:+.3f}"
        d_c = next((t for t in kh.thanh_doc_dam[d.ten] if t.vai_tro in ("tren_suot", "tren_suot_chung")), None)
        top_suot = [(d_c.duong_kinh, d_c.so_luong, d_c.so_hieu)] if d_c else []
        duoi = _nhom_so_hieu(kh, d, d.bot, ("duoi",))
        for ben, vz in (("trai", 0), ("giua", len(dai_ds) // 2), ("phai", len(dai_ds) - 1)):
            dai_ma = dai_ds[vz]
            tren = list(top_suot)  # thanh suốt luôn có mặt ở mọi mặt cắt
            if ben != "giua":
                for dk, lst in sorted(d._so_ben["trai" if ben == "trai" else "phai"].items(), reverse=True):  # type: ignore[attr-defined]
                    for n, th in lst:
                        tren.append((dk, n, th.so_hieu))
            khoa = ("dam", d.b, d.h, tuple(tren), tuple(duoi), dai_ma.so_hieu, dai_ma.buoc)
            so = them(khoa, lambda s, d=d, tren=tren, duoi=duoi, dai_ma=dai_ma, tn=tang_nhan: MatCatDinhNghia(
                s, "dam", d.b, d.h, tren, duoi, (dai_ma.so_hieu, f"Ø{dai_ma.duong_kinh}a{dai_ma.buoc:g}"), d.ten, tn))
            kh.gan_mat_cat_dam[(d.ten, ben)] = so

    for c in kh.cots:
        dai_ds = kh.dai_cot[c.ten]
        so_h = kh.thanh_doc_cot[c.ten][0]
        vung_dung = [(i, v) for i, v in enumerate(c.vung)]
        # mỗi bước đai khác nhau → 1 mặt cắt
        thay: dict[float, int] = {}
        for i, v in vung_dung:
            if v.buoc_mm in thay:
                kh.gan_mat_cat_cot[(c.ten, i)] = thay[v.buoc_mm]
                continue
            dm = dai_ds[i] if i < len(dai_ds) else dai_ds[-1]
            khoa = ("cot", c.b, c.h, c.d, c.n_b, c.n_h, dm.so_hieu, so_h)
            so = them(khoa, lambda s, c=c, dm=dm, so_h=so_h, v=v: MatCatDinhNghia(
                s, "cot", c.b, c.h, [], [(c.d, c.n_tong, so_h)], (dm.so_hieu, v.nhan()), c.ten, "", c.truc,
                {"d": c.d, "n_b": c.n_b, "n_h": c.n_h, "so_hieu": so_h}))
            thay[v.buoc_mm] = so
            kh.gan_mat_cat_cot[(c.ten, i)] = so
    kh.mat_cat = ds_mc
