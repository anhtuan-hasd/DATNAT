"""
Điều phối Input Adapter: xác định ánh xạ cột (heuristic -> tuỳ chọn LLM ->
xác nhận người dùng) rồi chuẩn hoá DataFrame thô thành BoDuLieuKhung.

Đây là nơi triển khai "vòng lặp xác nhận dữ liệu" của TONGQUAN_AI_AGENT.md
mục 5 dưới dạng hàm THUẦN (không phụ thuộc CLI/orchestrator cụ thể nào) —
lớp Agent điều phối (Phase 4, dùng OpenAI API) sẽ gọi các hàm ở đây và
tự quyết định CÁCH hỏi người dùng thật (CLI, tool-call, UI...). Việc tách
riêng như vậy giúp toàn bộ logic ở đây unit-test được mà không cần dựng agent
thật hay gọi mạng.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from . import heuristics
from .heuristics import DeXuatAnhXa
from .llm_mapping import NhaCungCapLLM, de_xuat_anh_xa_bang_llm
from .models import BoDuLieuKhung, DonViLucGoc, DuLieuViTri, LoaiCauKien, NoiLuc, PhanTuKhung, TietDien

# Các trường BẮT BUỘC phải có để Rule Engine chạy được tối thiểu — thiếu 1
# trong số này thì KHÔNG được chuẩn hoá tiếp, phải báo người dùng bổ sung.
TRUONG_BAT_BUOC = ["ten_phan_tu", "loai", "b", "h", "M", "Q"]
NGUONG_TIN_CAY_MAC_DINH = 0.75

_HE_SO_QUY_DOI: dict[DonViLucGoc, dict[str, float]] = {
    DonViLucGoc.KN_KNM: {"luc": 1.0, "momen": 1.0},
    DonViLucGoc.N_NMM: {"luc": 1e-3, "momen": 1e-6},
}


@dataclass
class KetQuaAnhXa:
    anh_xa: dict[str, DeXuatAnhXa]
    can_xac_nhan: list[str]  # trường có độ tin cậy thấp (kể cả sau khi hỏi LLM)
    thieu_bat_buoc: list[str]  # trường bắt buộc hoàn toàn không tìm được cột


def xac_dinh_anh_xa(
    df: pd.DataFrame,
    nha_cung_cap_llm: NhaCungCapLLM | None = None,
    nguong_tin_cay: float = NGUONG_TIN_CAY_MAC_DINH,
    truong_bat_buoc: list[str] = TRUONG_BAT_BUOC,
) -> KetQuaAnhXa:
    """Chạy heuristic trước; nếu còn trường bắt buộc/tin cậy thấp VÀ có
    nha_cung_cap_llm, hỏi LLM đề xuất thêm — nhưng đề xuất từ LLM KHÔNG
    tự động được chấp nhận: vẫn nằm trong can_xac_nhan để lớp gọi (Agent điều
    phối) hỏi người dùng thật trước khi dùng để tính toán."""
    cot_goc = [str(c) for c in df.columns]
    anh_xa = heuristics.du_doan_anh_xa_cot(cot_goc)

    can_hoi = heuristics.truong_can_hoi_nguoi_dung(anh_xa, nguong_tin_cay)
    thieu = heuristics.truong_bat_buoc_con_thieu(anh_xa, truong_bat_buoc)

    if nha_cung_cap_llm is not None and (thieu or can_hoi):
        truong_can_llm = sorted(set(thieu) | set(can_hoi))
        mau_du_lieu = {c: df[c].dropna().astype(str).head(3).tolist() for c in cot_goc}
        try:
            de_xuat_llm = de_xuat_anh_xa_bang_llm(nha_cung_cap_llm, cot_goc, truong_can_llm, mau_du_lieu)
        except ValueError:
            de_xuat_llm = {}  # LLM trả JSON hỏng — coi như không có đề xuất, không sập cả pipeline

        for truong, dx in de_xuat_llm.items():
            if truong not in anh_xa or dx.do_tin_cay > anh_xa[truong].do_tin_cay:
                anh_xa[truong] = dx

        can_hoi = sorted(set(can_hoi) | set(de_xuat_llm.keys()))
        thieu = heuristics.truong_bat_buoc_con_thieu(anh_xa, truong_bat_buoc)

    if "tiet_dien_ky_hieu" in anh_xa:
        # b/h có thể suy được từ 1 cột ký hiệu tiết diện kiểu "D250x700"
        # (xem _suy_b_h_tu_ky_hieu) — không còn coi là "thiếu bắt buộc" nếu
        # có cột này, dù không có cột b/h riêng.
        thieu = [t for t in thieu if t not in ("b", "h")]

    return KetQuaAnhXa(anh_xa=anh_xa, can_xac_nhan=can_hoi, thieu_bat_buoc=thieu)


HamXacNhan = Callable[[str, DeXuatAnhXa], bool]


def ap_dung_xac_nhan_nguoi_dung(ket_qua: KetQuaAnhXa, xac_nhan: HamXacNhan) -> dict[str, DeXuatAnhXa]:
    """Với mỗi trường trong can_xac_nhan, gọi xac_nhan(truong, de_xuat) — hàm
    này do lớp trên (CLI/Agent điều phối) cung cấp để THỰC SỰ hỏi người dùng.
    True -> giữ đề xuất; False -> loại khỏi ánh xạ (coi như chưa xác định)."""
    anh_xa_cuoi = dict(ket_qua.anh_xa)
    for truong in ket_qua.can_xac_nhan:
        if truong in anh_xa_cuoi and not xac_nhan(truong, anh_xa_cuoi[truong]):
            del anh_xa_cuoi[truong]
    return anh_xa_cuoi


_MAU_KY_HIEU_TIET_DIEN = re.compile(r"(\d+)\s*[xX]\s*(\d+)")


def _suy_b_h_tu_ky_hieu(gia_tri) -> tuple[float, float] | None:
    """Suy b,h (mm) từ 1 ô ký hiệu tiết diện dạng "D250x700"/"C250x600" —
    nhiều báo cáo ETABS không tách sẵn cột b/h riêng mà gộp vào 1 cột
    "Section". Chỉ dùng làm phương án DỰ PHÒNG khi không có cột b/h trực
    tiếp (mục 11 RULES: cần validate tiết diện hợp lý, nhưng việc đó thuộc
    Rule Engine, ở đây chỉ trích số ra)."""
    if gia_tri is None:
        return None
    khop = _MAU_KY_HIEU_TIET_DIEN.search(str(gia_tri))
    if not khop:
        return None
    return float(khop.group(1)), float(khop.group(2))


def _lay_gia_tri(row: pd.Series, anh_xa: dict[str, str], truong: str, mac_dinh=None):
    cot = anh_xa.get(truong)
    if cot is None or cot not in row.index:
        return mac_dinh
    gia_tri = row[cot]
    if pd.isna(gia_tri):
        return mac_dinh
    return gia_tri


def chuan_hoa_thanh_phan_tu(
    df: pd.DataFrame,
    anh_xa: dict[str, str],
    don_vi_luc_goc: DonViLucGoc = DonViLucGoc.KN_KNM,
    loai_mac_dinh: LoaiCauKien | None = None,
) -> list[PhanTuKhung]:
    """Chuyển DataFrame thô + ánh xạ đã xác nhận thành list[PhanTuKhung].

    Giả định mỗi dòng là dữ liệu của 1 (phần_tử, vị_trí) — nếu nhiều dòng
    trùng (phần_tử, vị_trí) (vd nhiều tổ hợp tải), GIỮ dòng có |M| lớn nhất,
    coi đây là báo cáo dạng envelope (đúng cách ETABS thường xuất As yêu cầu
    theo tổ hợp nguy hiểm nhất — mục 11 RULES). anh_xa: dict truong_chuan ->
    tên cột gốc (đã qua xác nhận, KHÔNG phải DeXuatAnhXa).

    loai_mac_dinh: nhiều báo cáo ETABS thật tách RIÊNG sheet Dầm/Cột (không
    có cột "loại" trong từng dòng — loại được biết từ NGỮ CẢNH sheet, không
    phải từ dữ liệu) — truyền loai_mac_dinh khi gọi hàm này cho 1 sheet đã
    biết chắc toàn bộ là dầm hoặc toàn bộ là cột, thay vì để heuristic đoán
    nhầm cột "loại" không tồn tại.
    """
    he_so = _HE_SO_QUY_DOI[don_vi_luc_goc]
    nhom: dict[str, dict] = {}

    for _, row in df.iterrows():
        ten = _lay_gia_tri(row, anh_xa, "ten_phan_tu")
        if ten is None:
            continue
        ten = str(ten)

        if loai_mac_dinh is not None:
            loai = loai_mac_dinh
        else:
            loai_raw = str(_lay_gia_tri(row, anh_xa, "loai", "dam")).lower()
            loai = LoaiCauKien.COT if ("cot" in loai_raw or "col" in loai_raw) else LoaiCauKien.DAM

        M_raw = _lay_gia_tri(row, anh_xa, "M")
        N_raw = _lay_gia_tri(row, anh_xa, "N")
        Q_raw = _lay_gia_tri(row, anh_xa, "Q")
        As_yc_raw = _lay_gia_tri(row, anh_xa, "As_yc")
        to_hop = _lay_gia_tri(row, anh_xa, "combo")
        vi_tri = str(_lay_gia_tri(row, anh_xa, "vi_tri", "khong_xac_dinh"))

        noi_luc = NoiLuc(
            M=None if M_raw is None else float(M_raw) * he_so["momen"],
            N=None if N_raw is None else float(N_raw) * he_so["luc"],
            Q=None if Q_raw is None else float(Q_raw) * he_so["luc"],
            to_hop_chi_phoi=None if to_hop is None else str(to_hop),
        )
        du_lieu_vt = DuLieuViTri(
            vi_tri=vi_tri,
            As_yc=None if As_yc_raw is None else float(As_yc_raw),
            noi_luc=noi_luc,
        )

        if ten not in nhom:
            b_truc_tiep = _lay_gia_tri(row, anh_xa, "b")
            h_truc_tiep = _lay_gia_tri(row, anh_xa, "h")
            if b_truc_tiep is None or h_truc_tiep is None:
                suy_ra = _suy_b_h_tu_ky_hieu(_lay_gia_tri(row, anh_xa, "tiet_dien_ky_hieu"))
                if suy_ra is not None:
                    b_truc_tiep = b_truc_tiep if b_truc_tiep is not None else suy_ra[0]
                    h_truc_tiep = h_truc_tiep if h_truc_tiep is not None else suy_ra[1]
            nhom[ten] = {
                "loai": loai,
                "b": b_truc_tiep,
                "h": h_truc_tiep,
                "mac_be_tong": _lay_gia_tri(row, anh_xa, "mac_be_tong", ""),
                "nhom_thep": _lay_gia_tri(row, anh_xa, "nhom_thep", ""),
                "tang": _lay_gia_tri(row, anh_xa, "tang"),
                "truc": _lay_gia_tri(row, anh_xa, "truc"),
                "vi_tri": {},
            }

        vi_tri_map = nhom[ten]["vi_tri"]
        hien_co = vi_tri_map.get(vi_tri)
        M_moi = du_lieu_vt.noi_luc.M
        M_cu = hien_co.noi_luc.M if hien_co is not None else None
        if hien_co is None or (M_moi is not None and (M_cu is None or abs(M_moi) > abs(M_cu))):
            vi_tri_map[vi_tri] = du_lieu_vt

    ket_qua: list[PhanTuKhung] = []
    for ten, thong_tin in nhom.items():
        b = thong_tin["b"]
        h = thong_tin["h"]
        ket_qua.append(
            PhanTuKhung(
                ten=ten,
                loai=thong_tin["loai"],
                tiet_dien=TietDien(b=float(b) if b is not None else 0.0, h=float(h) if h is not None else 0.0),
                mac_be_tong=str(thong_tin["mac_be_tong"]),
                nhom_thep_doc=str(thong_tin["nhom_thep"]),
                tang=None if thong_tin["tang"] is None else str(thong_tin["tang"]),
                truc=None if thong_tin["truc"] is None else str(thong_tin["truc"]),
                du_lieu_vi_tri=list(thong_tin["vi_tri"].values()),
            )
        )
    return ket_qua


def chuan_hoa_bang(
    ten_khung: str,
    df: pd.DataFrame,
    anh_xa: dict[str, str],
    don_vi_luc_goc: DonViLucGoc = DonViLucGoc.KN_KNM,
    loai_mac_dinh: LoaiCauKien | None = None,
) -> BoDuLieuKhung:
    """Điểm vào tiện lợi: bọc chuan_hoa_thanh_phan_tu thành BoDuLieuKhung hoàn chỉnh."""
    return BoDuLieuKhung(
        ten_khung=ten_khung,
        don_vi_luc_goc=don_vi_luc_goc,
        phan_tu=chuan_hoa_thanh_phan_tu(df, anh_xa, don_vi_luc_goc, loai_mac_dinh),
    )
