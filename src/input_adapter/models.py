"""
Schema chuẩn hoá nội bộ cho Input Adapter — TONGQUAN_AI_AGENT.md mục 5 bước 2:
"Input Adapter — agent quét các sheet/cột, ánh xạ về schema chuẩn:
{phần_tử, loại (dầm/cột), vị_trí, As_yc, b, h, mác_bê_tông, nhóm_thép,
tổ_hợp_chi_phối}".

Đây là mô hình dữ liệu NỘI BỘ mà MỌI nguồn Excel/CSV (schema khác nhau tuỳ
nguồn xuất) phải được ánh xạ về, trước khi đưa vào src/rule_engine/. Thiết kế
mới hoàn toàn cho đồ án này — không dùng lại model của project cũ.

Đơn vị chuẩn nội bộ sau khi qua Input Adapter LUÔN là: lực/mô men → kN, kN·m;
kích thước hình học → mm — khớp đúng quy ước dùng trong src/rule_engine/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LoaiCauKien(str, Enum):
    DAM = "dam"
    COT = "cot"


class DonViLucGoc(str, Enum):
    """Đơn vị lực/mô men TRONG FILE GỐC (trước chuẩn hoá) — mục 11 RULES ghi
    rõ input không có schema cố định, và người dùng thực tế đã xác nhận mặc
    định là kN/kN·m; N/N·mm là trường hợp còn lại cần Input Adapter tự dò."""

    KN_KNM = "kN_kNm"
    N_NMM = "N_Nmm"


@dataclass(frozen=True)
class TietDien:
    """Tiết diện chữ nhật — RULES_TCVN5574.md chỉ trong phạm vi cột/dầm chữ
    nhật (mục 0, bảng đối chiếu phạm vi: Phụ lục F cột tròn nằm ngoài)."""

    b: float  # mm
    h: float  # mm


@dataclass(frozen=True)
class NoiLuc:
    """Nội lực nguy hiểm tại 1 vị trí, ứng với 1 tổ hợp tải trọng chi phối —
    đã quy đổi về kN, kN·m bất kể đơn vị gốc trong file (kN·m/kN hoặc N·mm/N)."""

    M: float | None = None  # kN·m
    N: float | None = None  # kN — lực dọc (thường 0 với dầm, khác 0 với cột)
    Q: float | None = None  # kN
    to_hop_chi_phoi: str | None = None


@dataclass(frozen=True)
class DuLieuViTri:
    """Dữ liệu tại 1 vị trí cụ thể trên 1 phần tử.

    vi_tri: "goi_trai" | "giua_nhip" | "goi_phai" (dầm nhịp thường);
    "ngam" (dầm công-xôn); "chan" | "dinh" | "dai_dien" (cột); hoặc chuỗi tự
    do khác nếu Input Adapter không nhận diện được (Rule Engine/AutoCAD Tool
    ở các Phase sau tự quyết định xử lý tiếp thế nào với vị trí lạ).
    """

    vi_tri: str
    As_yc: float | None = None  # mm² — As yêu cầu do ETABS xuất (None nếu file không có sẵn)
    noi_luc: NoiLuc = field(default_factory=NoiLuc)


@dataclass
class PhanTuKhung:
    """1 phần tử khung (1 dầm hoặc 1 cột) sau chuẩn hoá.

    ten: tên phần tử theo quy ước mục 11 RULES (vd "44-45", "22", "cột B-2").
    """

    ten: str
    loai: LoaiCauKien
    tiet_dien: TietDien
    mac_be_tong: str
    nhom_thep_doc: str
    nhom_thep_dai: str | None = None
    tang: str | None = None
    truc: str | None = None  # vd "A", "B", "C" (cột) hoặc "AB", "BC" (nhịp dầm) —
    # cần để vẽ mặt đứng khung (mục 10.7.1); tuỳ chọn, None nếu file không có.
    chieu_dai: float | None = None  # mm — nhịp dầm hoặc chiều cao đoạn cột (nếu file có)
    du_lieu_vi_tri: list[DuLieuViTri] = field(default_factory=list)


@dataclass
class BoDuLieuKhung:
    """Toàn bộ dữ liệu 1 khung sau chuẩn hoá — output cuối của Input Adapter,
    input đầu cho Rule Engine (src/rule_engine/)."""

    ten_khung: str
    don_vi_luc_goc: DonViLucGoc
    phan_tu: list[PhanTuKhung] = field(default_factory=list)
