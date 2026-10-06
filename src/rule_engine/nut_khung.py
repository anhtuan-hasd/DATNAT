"""
Cấu tạo tại nút khung — RULES_TCVN5574.md mục 7 (TCVN 5574:2018 mục 10.4.11,
sách hướng dẫn mục 5.4.3).

Đây là bảng tra loại nút → yêu cầu cấu tạo bằng chữ (không phải công thức số).
Rule Engine dùng bảng này để sinh GHI CHÚ/quyết định cấu tạo cho AutoCAD Tool
(Phase 3) tại vị trí nút khung, không tính ra một con số kỹ thuật mới nào.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YeuCauCauTaoNut:
    loai_nut: str
    yeu_cau: str


# Khoá đúng theo tên loại nút liệt kê ở mục 7 của RULES_TCVN5574.md.
BANG_CAU_TAO_NUT: dict[str, YeuCauCauTaoNut] = {
    "goc_mai_dong_e0_h_le_025": YeuCauCauTaoNut(
        "Góc mái \"đóng\", e0/h ≤ 0,25",
        "Thép kéo dầm uốn xuống mép ngoài cột, đoạn Lan.",
    ),
    "goc_mai_dong_025_lt_e0_h_le_05": YeuCauCauTaoNut(
        "Góc mái \"đóng\", 0,25<e0/h≤0,5",
        "Thêm ≥2 thanh kéo xuống đáy dầm đoạn Lan.",
    ),
    "goc_mai_dong_e0_h_gt_05": YeuCauCauTaoNut(
        "Góc mái \"đóng\", e0/h>0,5",
        "Một số thanh cột kéo lên mép trên dầm; thép dầm neo sâu vào cột.",
    ),
    "goc_mai_mo": YeuCauCauTaoNut(
        "Góc mái \"mở\"",
        "Thép dọc uốn chữ U nối dầm-cột; μ≥2% thêm thép chéo gia cường ≈20% "
        "thép chịu lực đầu dầm.",
    ),
    "giua_khung_mai": YeuCauCauTaoNut(
        "Giữa khung mái",
        "Thép cột kéo lên mặt dầm/sàn đoạn Lan, bán kính uốn ≥50mm.",
    ),
    "bien_tang_trung_gian_tiet_dien_khong_doi": YeuCauCauTaoNut(
        "Biên tầng trung gian, tiết diện cột không đổi",
        "Đai ≤min(300;10d_min) trong đoạn Lan tại nút.",
    ),
    "bien_doi_tiet_dien_tgbeta_le_1_6": YeuCauCauTaoNut(
        "Biên, cột đổi tiết diện tgβ≤1/6",
        "Cốt dọc cột dưới vuốt liên tục lên chờ nối cột trên.",
    ),
    "bien_doi_tiet_dien_tgbeta_gt_1_6": YeuCauCauTaoNut(
        "Biên, cột đổi tiết diện tgβ>1/6",
        "Cốt dọc cột dưới kéo lên mặt dầm, neo đoạn Lan riêng.",
    ),
    "giua_tang_trung_gian": YeuCauCauTaoNut(
        "Giữa tầng trung gian",
        "Thép dầm liên tục qua nút; dầm 2 bên chênh cao thì neo sâu dầm thấp hơn.",
    ),
    "cot_mong": YeuCauCauTaoNut(
        "Cột - móng",
        "Thép chờ chữ L từ móng tương đương thép cột nối lên.",
    ),
    "gay_khuc_alpha_ge_160": YeuCauCauTaoNut(
        "Gãy khúc, α≥160°",
        "Thép dọc chịu kéo liên tục qua nút, có cốt ngang gia cường.",
    ),
    "gay_khuc_alpha_lt_160": YeuCauCauTaoNut(
        "Gãy khúc, α<160°",
        "Thép dọc chịu kéo tách rời, neo vào vùng nén đoạn Lan; ôm cốt ngang.",
    ),
    "dam_phu_dam_chinh": YeuCauCauTaoNut(
        "Dầm phụ - dầm chính",
        "Đai gia cường ôm cốt dọc, đoạn b+2h (dầm chính)/h/3 (dầm phụ).",
    ),
}


def tra_yeu_cau_nut(loai_nut: str) -> YeuCauCauTaoNut:
    """Tra yêu cầu cấu tạo theo khoá loai_nut (xem BANG_CAU_TAO_NUT). Mục 7."""
    if loai_nut not in BANG_CAU_TAO_NUT:
        raise ValueError(
            f"Loại nút '{loai_nut}' không có trong RULES_TCVN5574.md mục 7 "
            f"(hỗ trợ: {sorted(BANG_CAU_TAO_NUT)})."
        )
    return BANG_CAU_TAO_NUT[loai_nut]
