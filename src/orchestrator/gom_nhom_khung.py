"""Áp dụng luật gom nhóm thép R53 (cột cùng tầng/tiết diện) và R54 (hai gối dầm cùng bố trí thép trên) lên kết quả Rule
Engine của TOÀN khung — bước TẤT ĐỊNH của pipeline, chạy sau khi mọi phần tử đã đạt và trước khi lắp ráp bản vẽ.

Vì sao nằm ở pipeline mà không để Rule Engine Agent tự làm: mỗi phiên agent chỉ thấy MỘT phần tử, nên không có cách nào
biết cột bên cạnh (cùng tầng) cần bao nhiêu thép. Quy tắc và nguồn gốc: `src/rule_engine/gom_nhom.py`, skill
`huongdanchonthep/02` Bước 8d, `03` Bước 9d, `08` luật R53–R54.

Chỉ NÂNG thép: phần tử/vị trí bất lợi hơn làm chuẩn, As thực không bao giờ giảm. Các đại lượng phụ thuộc đường kính — đoạn
neo/nối (`neo_noi`) và Ø/bước đai (`dai`) — được tính lại cho phần tử bị nâng.
"""

from __future__ import annotations

from ..rule_engine import bo_tri_dai as bo_tri_dai_mod
from ..rule_engine import gom_nhom, neo_noi, vat_lieu
from .shared.hop_dong_du_lieu import BoDuLieuKhungChuanHoa, KetQuaPhanTu, KetQuaViTriDaThietKe, PhuongAnThepPhanTu

VI_TRI_GOI = ("goi_trai", "goi_phai")


def _duong_kinh_cua(thep_doc: dict) -> list[int]:
    if thep_doc.get("thanh"):
        return [int(t["duong_kinh"]) for t in thep_doc["thanh"]]
    if thep_doc.get("duong_kinh"):
        return [int(thep_doc["duong_kinh"])]
    return []


def _as_cua(thep_doc: dict, loai: str) -> float | None:
    gia_tri = thep_doc.get("As_thuc_moi_phia") if loai == "cot" else thep_doc.get("As_thuc")
    return float(gia_tri) if gia_tri else None


def _tinh_lai_neo_noi(thep_doc: dict, nhom_thep_doc: str, mac_be_tong: str, cu: dict) -> dict:
    """Tính lại đoạn neo/nối theo đường kính lớn nhất của bố trí mới (cùng công thức `tinh_neo_noi`, As_cal = As_ef nên
    thiên về an toàn). Không tra được vật liệu ⇒ giữ nguyên số cũ (không bịa)."""
    ds = _duong_kinh_cua(thep_doc)
    if not ds or not cu:
        return cu
    try:
        rs = vat_lieu.lay_thep(nhom_thep_doc).Rs
        rbt = vat_lieu.lay_be_tong(mac_be_tong).Rbt
    except ValueError:
        return cu
    d = max(ds)
    r_bond = neo_noi.tinh_R_bond(neo_noi.tinh_eta1(True), neo_noi.tinh_eta2(d), rbt)
    a1 = vat_lieu.dien_tich_1_thanh(d)
    l0 = neo_noi.tinh_L0_an(rs, a1, r_bond, neo_noi.chu_vi_thanh(d))
    return {
        "L0_an": l0, "L_an": neo_noi.tinh_L_an(l0, a1, a1, d, True), "L_lap": neo_noi.tinh_L_lap(l0, a1, a1, d, True),
        "duong_kinh_uon_toi_thieu": neo_noi.duong_kinh_uon_toi_thieu(d, True),
    }


def _tinh_lai_dai(pa: PhuongAnThepPhanTu) -> None:
    """Quyết định đai phụ thuộc Ø dọc lớn/nhỏ nhất của phần tử ⇒ tính lại sau khi nâng thép (giữ bước tính toán và cảnh báo)."""
    if not pa.dai:
        return
    ds = [d for v in pa.vi_tri for d in _duong_kinh_cua(v.thep_doc)]
    if not ds:
        return
    h_tinh = max(pa.b, pa.h) if pa.loai == "cot" else pa.h
    moi = bo_tri_dai_mod.quyet_dinh_dai(pa.loai, float(h_tinh), max(ds), min(ds), pa.dai.get("buoc_tinh_toan_da_xet"))
    moi["duong_kinh_doc_max"], moi["duong_kinh_doc_min"] = max(ds), min(ds)
    for khoa in ("buoc_tinh_toan_da_xet", "canh_bao"):
        if khoa in pa.dai:
            moi[khoa] = pa.dai[khoa]
    pa.dai = moi


def _nhan(nc: gom_nhom.NangCap) -> str:
    truoc = nc.mo_ta_truoc or f"{nc.as_truoc:.0f}mm²"
    sau = nc.mo_ta_sau or f"{nc.as_sau:.0f}mm²"
    return f"{truoc} → {sau}"


def _nang_thep(dich: KetQuaViTriDaThietKe, nguon: KetQuaViTriDaThietKe, nhan_nguon: str, goc) -> None:
    dich.thep_doc = {**nguon.thep_doc, "gom_nhom_tu": nhan_nguon}
    dich.neo_noi = _tinh_lai_neo_noi(dich.thep_doc, goc.nhom_thep_doc, goc.mac_be_tong, dich.neo_noi)


def ap_dung_gom_nhom(bo_du_lieu: BoDuLieuKhungChuanHoa, ket_qua_phan_tu: list[KetQuaPhanTu]) -> list[str]:
    """Gom nhóm in-place trên các `PhuongAnThepPhanTu` đã đạt Rule Engine; trả về các dòng nhật ký (mỗi lần nâng một dòng)."""
    goc = {p.ten: p for p in bo_du_lieu.phan_tu}
    phuong_an = {kq.ten_phan_tu: kq.phuong_an_thep for kq in ket_qua_phan_tu if kq.rule_engine_dat and kq.phuong_an_thep}
    nhat_ky: list[str] = []
    da_doi: set[str] = set()

    # R53 — cột cùng tầng, cùng tiết diện, cùng vật liệu.
    muc_cot: list[gom_nhom.MucGom] = []
    for ten, pa in phuong_an.items():
        g = goc.get(ten)
        if pa.loai != "cot" or g is None or len(pa.vi_tri) != 1:
            continue
        as_thuc = _as_cua(pa.vi_tri[0].thep_doc, "cot")
        if as_thuc is None:
            continue
        muc_cot.append(gom_nhom.MucGom(
            ten=ten, nhom=gom_nhom.khoa_nhom_cot(ten, g.tang, g.b, g.h, g.mac_be_tong, g.nhom_thep_doc),
            as_thuc=as_thuc, mo_ta=pa.vi_tri[0].thep_doc.get("mo_ta", ""),
        ))
    for nc in gom_nhom.tim_nang_cap(muc_cot, "R53"):
        dich, nguon = phuong_an[nc.ten], phuong_an[nc.nguon]
        _nang_thep(dich.vi_tri[0], nguon.vi_tri[0], f"cột {nc.nguon}", goc[nc.ten])
        _tinh_lai_dai(dich)
        da_doi.add(nc.ten)
        nhat_ky.append(f"Gom nhóm R53: cột '{nc.ten}' nâng {_nhan(nc)} theo cột '{nc.nguon}' (cùng tầng, cùng tiết diện).")

    # R54 — thép trên chạy suốt: hai gối cùng bố trí theo gối lớn hơn.
    for ten, pa in phuong_an.items():
        g = goc.get(ten)
        if pa.loai != "dam" or g is None:
            continue
        goi = {v.vi_tri: v for v in pa.vi_tri if v.vi_tri in VI_TRI_GOI}
        if len(goi) != 2:
            continue
        muc = []
        for ten_vt, v in goi.items():
            as_thuc = _as_cua(v.thep_doc, "dam")
            if as_thuc is None:
                break
            muc.append(gom_nhom.MucGom(ten=ten_vt, nhom=(ten,), as_thuc=as_thuc, mo_ta=v.thep_doc.get("mo_ta", "")))
        else:
            for nc in gom_nhom.tim_nang_cap(muc, "R54"):
                _nang_thep(goi[nc.ten], goi[nc.nguon], f"dầm {ten} {nc.nguon}", g)
                da_doi.add(ten)
                nhat_ky.append(f"Gom nhóm R54: dầm '{ten}' {nc.ten} nâng {_nhan(nc)} theo {nc.nguon} (thép trên chạy suốt).")
    for ten in sorted(da_doi):
        if phuong_an[ten].loai == "dam":
            _tinh_lai_dai(phuong_an[ten])
    return nhat_ky
