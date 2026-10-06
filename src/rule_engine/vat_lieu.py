"""
Bảng tra vật liệu — RULES_TCVN5574.md mục 1.

Toàn bộ giá trị trong module này là số tra bảng trực tiếp từ TCVN 5574:2018
(Bảng 7, 10, 13, 14, 19 và Phụ lục C) đã được tổng hợp lại trong
docs/RULES_TCVN5574.md. KHÔNG được tự thêm/sửa số liệu ở đây nếu
RULES_TCVN5574.md chưa có — mọi bổ sung phải dẫn nguồn về đúng mục tài liệu.

Đơn vị dùng thống nhất trong toàn bộ rule_engine: lực (kN, kN·m), ứng suất/
cường độ (MPa = N/mm²), chiều dài hình học tiết diện (mm). Input Adapter
(Phase 2) chịu trách nhiệm quy đổi input thô về đúng bộ đơn vị này trước khi
gọi rule_engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VatLieuBeTong:
    """Cường độ tính toán bê tông theo TTGH1 — RULES_TCVN5574.md mục 1.1 (Bảng 7, 10)."""

    cap_do_ben: str
    Rb: float  # MPa — cường độ chịu nén tính toán
    Rbt: float  # MPa — cường độ chịu kéo tính toán
    Eb: float  # MPa — mô đun đàn hồi ban đầu


@dataclass(frozen=True)
class VatLieuThep:
    """Cường độ tính toán cốt thép — RULES_TCVN5574.md mục 1.2 (Bảng 13, 14)."""

    nhom: str
    Rs: float  # MPa — cường độ chịu kéo tính toán
    Rsc: float  # MPa — cường độ chịu nén tính toán
    Rsw: float  # MPa — cường độ tính toán cốt đai (đã chặn trần 300 MPa theo 6.2.2.3)
    Es: float  # MPa — mô đun đàn hồi


# Bảng 7 + Bảng 10 TCVN 5574:2018 — RULES_TCVN5574.md mục 1.1.
_BANG_BE_TONG: dict[str, VatLieuBeTong] = {
    "B15": VatLieuBeTong("B15", Rb=8.5, Rbt=0.75, Eb=24_000.0),
    "B20": VatLieuBeTong("B20", Rb=11.5, Rbt=0.90, Eb=27_500.0),
    "B25": VatLieuBeTong("B25", Rb=14.5, Rbt=1.05, Eb=30_000.0),
    "B30": VatLieuBeTong("B30", Rb=17.0, Rbt=1.15, Eb=32_500.0),
    "B35": VatLieuBeTong("B35", Rb=19.5, Rbt=1.30, Eb=34_500.0),
    "B40": VatLieuBeTong("B40", Rb=22.0, Rbt=1.40, Eb=36_000.0),
    "B45": VatLieuBeTong("B45", Rb=25.0, Rbt=1.50, Eb=37_000.0),
    "B50": VatLieuBeTong("B50", Rb=27.5, Rbt=1.60, Eb=38_000.0),
}

# Bảng 13 + Bảng 14 TCVN 5574:2018 — RULES_TCVN5574.md mục 1.2.
# Rsw đã lấy đúng giá trị bảng (mọi nhóm đều ≤ 300 MPa theo 6.2.2.3 nên không cần chặn thêm).
_BANG_THEP: dict[str, VatLieuThep] = {
    "CB240-T": VatLieuThep("CB240-T", Rs=210.0, Rsc=210.0, Rsw=170.0, Es=2.0e5),
    "CB300-T": VatLieuThep("CB300-T", Rs=260.0, Rsc=260.0, Rsw=210.0, Es=2.0e5),
    "CB300-V": VatLieuThep("CB300-V", Rs=260.0, Rsc=260.0, Rsw=210.0, Es=2.0e5),
    "CB400-V": VatLieuThep("CB400-V", Rs=350.0, Rsc=350.0, Rsw=280.0, Es=2.0e5),
    # CB500-V: Rsc dài hạn = 400 MPa (mục 1.2) — không mô hình riêng vì Rule Engine
    # dùng tải tính toán chuẩn (Rsc=435). Trường hợp cần xét tải dài hạn riêng cho
    # cột sẽ bổ sung khi có yêu cầu cụ thể (không tự suy diễn thêm ở đây).
    "CB500-V": VatLieuThep("CB500-V", Rs=435.0, Rsc=435.0, Rsw=300.0, Es=2.0e5),
}

# Bảng đường kính — diện tích 1 thanh, As = π·d²/4 — RULES_TCVN5574.md mục 1.3.
# Giá trị lấy đúng theo bảng tra (không tính lại bằng công thức để khớp số làm tròn
# tiêu chuẩn TCVN 1651-1:2008 mà tài liệu đã trích).
BANG_DUONG_KINH: dict[int, float] = {
    6: 28.3,
    8: 50.3,
    10: 78.5,
    12: 113.1,
    14: 153.9,
    16: 201.1,
    18: 254.5,
    20: 314.2,
    22: 380.1,
    25: 490.9,
    28: 615.8,
    32: 804.2,
}

RSW_MAX = 300.0  # MPa — trần Rsw mọi nhóm thép, mục 1.2 (6.2.2.3 TCVN 5574:2018).

# Phụ lục C — bảng quy đổi ký hiệu thép nước ngoài phổ biến sang nhóm TCVN gần nhất
# — RULES_TCVN5574.md mục 8. Dùng cho Input Adapter (Phase 2) khi input không theo
# ký hiệu TCVN; đặt ở đây vì thuộc "bảng tra vật liệu".
QUY_DOI_THEP_NUOC_NGOAI: dict[str, str] = {
    "A-I": "CB240-T",
    "A240": "CB240-T",
    "A-II": "CB300-V",
    "A300": "CB300-V",
    "A-III": "CB400-V",
    "A400": "CB400-V",
    "SD295": "CB300-V",
    "SD345": "CB400-V",
    "SD390": "CB400-V",
    "SD490": "CB500-V",
    "B500A": "CB500-V",
    "B500B": "CB500-V",
    "B500C": "CB500-V",
    "GR.280": "CB240-T",
    "GR.420": "CB400-V",
    "GR.520": "CB500-V",
    "HRB335": "CB300-V",
    "HRB400": "CB400-V",
    "HRB500": "CB500-V",
}


def lay_be_tong(cap_do_ben: str) -> VatLieuBeTong:
    """Tra Rb, Rbt, Eb theo cấp độ bền bê tông (vd "B25"). Mục 1.1."""
    key = cap_do_ben.strip().upper()
    if key not in _BANG_BE_TONG:
        raise ValueError(
            f"Không có cấp độ bền bê tông '{cap_do_ben}' trong bảng tra "
            f"(RULES_TCVN5574.md mục 1.1). Các cấp hỗ trợ: {sorted(_BANG_BE_TONG)}"
        )
    return _BANG_BE_TONG[key]


def lay_thep(nhom: str) -> VatLieuThep:
    """Tra Rs, Rsc, Rsw, Es theo nhóm cốt thép (vd "CB400-V"). Mục 1.2.

    Tự nhận diện ký hiệu nước ngoài phổ biến qua QUY_DOI_THEP_NUOC_NGOAI (Phụ lục C)
    trước khi tra bảng TCVN.
    """
    key = nhom.strip().upper()
    if key in QUY_DOI_THEP_NUOC_NGOAI:
        key = QUY_DOI_THEP_NUOC_NGOAI[key]
    if key not in _BANG_THEP:
        raise ValueError(
            f"Không có nhóm cốt thép '{nhom}' trong bảng tra (RULES_TCVN5574.md mục 1.2 "
            f"hoặc mục 8). Các nhóm hỗ trợ: {sorted(_BANG_THEP)}"
        )
    return _BANG_THEP[key]


def dien_tich_1_thanh(duong_kinh_mm: int) -> float:
    """As (mm²) của 1 thanh thép đường kính duong_kinh_mm. Mục 1.3."""
    if duong_kinh_mm not in BANG_DUONG_KINH:
        raise ValueError(
            f"Đường kính {duong_kinh_mm}mm không có trong bảng tra chuẩn "
            f"(RULES_TCVN5574.md mục 1.3). Các đường kính hỗ trợ: "
            f"{sorted(BANG_DUONG_KINH)}"
        )
    return BANG_DUONG_KINH[duong_kinh_mm]


def dien_tich_nhieu_thanh(duong_kinh_mm: int, so_luong: int) -> float:
    """As (mm²) của so_luong thanh cùng đường kính duong_kinh_mm. Mục 1.3."""
    return so_luong * dien_tich_1_thanh(duong_kinh_mm)


def duong_kinh_quy_doi_bo_thanh(danh_sach_duong_kinh_mm: list[int]) -> float:
    """d_red = sqrt(sum(d_i^2)) — đường kính quy đổi cho bó thanh thép. Mục 4.4."""
    return sum(d**2 for d in danh_sach_duong_kinh_mm) ** 0.5
