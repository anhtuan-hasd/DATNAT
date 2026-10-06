"""
Tự kiểm tra tổng hợp (verify) — chạy lại toàn bộ điều kiện liên quan (mục 4-7
của RULES_TCVN5574.md) cho MỘT kết quả chọn thép đã có, trả về danh sách vi
phạm. Đây là "Action" mà vòng lặp tự sửa lỗi (self-correction, xem
TONGQUAN_AI_AGENT.md mục 5) gọi lại sau bước chọn thép — nếu vi_pham không
rỗng, Agent điều phối quyết định có quay lại bước chọn thép với điều kiện
khác hay báo người dùng, KHÔNG tự sửa số liệu ở đây.

Module này chỉ gọi lại các hàm THUẦN đã có ở cot_doc/cot_dai/neo_noi — không
định nghĩa thêm ngưỡng/công thức mới nào.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import cot_dai, cot_doc


@dataclass(frozen=True)
class KetQuaVerify:
    dat: bool
    vi_pham: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DauVaoVerifyDam:
    """Dữ liệu cần để verify 1 tiết diện dầm đã chọn thép xong."""

    As_yc: float  # mm² — As yêu cầu (từ ETABS hoặc tính lại theo mục 2)
    As_thuc: float  # mm² — As thực tế đã chọn
    danh_sach_duong_kinh: list[int]  # các đường kính đã dùng tại tiết diện này
    b: float  # mm
    h0: float  # mm
    do_manh_L0_h: float  # dùng tra mu_min (mục 4.1)
    so_lop: int
    so_lop_toi_da_cho_phep: int
    Q: float  # kN — lực cắt tại tiết diện
    Rb: float
    Rbt: float
    Rsw: float
    Asw: float  # mm² — tổng diện tích các nhánh đai trong 1 mặt cắt đã chọn
    sw: float  # mm — bước đai đã chọn
    mu_max: float = cot_doc.MU_MAX_PHAN_TRAM


def kiem_tra_tong_hop_dam(dau_vao: DauVaoVerifyDam) -> KetQuaVerify:
    """Chạy toàn bộ điều kiện liên quan cho 1 tiết diện dầm. Trả về vi_pham
    rỗng nếu đạt tất cả."""
    vi_pham: list[str] = []

    if dau_vao.As_thuc < dau_vao.As_yc:
        vi_pham.append(
            f"As_thuc ({dau_vao.As_thuc:.1f}mm²) < As_yc ({dau_vao.As_yc:.1f}mm²) — "
            "không đủ diện tích cốt thép (mục 4)."
        )

    mu = 100 * dau_vao.As_thuc / (dau_vao.b * dau_vao.h0)
    mu_min = cot_doc.tra_mu_min(dau_vao.do_manh_L0_h)
    if mu < mu_min:
        vi_pham.append(f"μ={mu:.3f}% < μ_min={mu_min:.3f}% (mục 4.1).")
    if mu > dau_vao.mu_max:
        vi_pham.append(f"μ={mu:.3f}% > μ_max={dau_vao.mu_max:.3f}% (mục 4.1, ngưỡng cảnh báo).")

    # mục 4.2 nói "loại đường kính" (giá trị PHÂN BIỆT), không phải số thanh —
    # vd tổ hợp 1Ø16+4Ø18 (danh_sach_duong_kinh=[16,18,18,18,18], 5 thanh) chỉ
    # có 2 LOẠI, không phải 5. Dùng set() để đếm đúng số loại phân biệt (lỗi
    # này từng bị phát hiện qua chạy thật Phase 4: Agent chọn nhầm tổ hợp ít
    # thanh hơn để "né" điều kiện do đếm sai số thanh thay vì số loại).
    loai_duong_kinh = sorted(set(dau_vao.danh_sach_duong_kinh))
    if len(loai_duong_kinh) > 3:
        vi_pham.append(f"Dùng {len(loai_duong_kinh)} loại đường kính > 3 (mục 4.2).")
    if len(loai_duong_kinh) >= 2:
        for i, d1 in enumerate(loai_duong_kinh):
            for d2 in loai_duong_kinh[i + 1 :]:
                if abs(d1 - d2) == 1:
                    vi_pham.append(f"Hai đường kính {d1}mm và {d2}mm chênh đúng 1mm — không hợp lệ (mục 4.2).")
        chenh = max(loai_duong_kinh) - min(loai_duong_kinh)
        if chenh > 6:
            vi_pham.append(f"Chênh lệch đường kính lớn nhất-nhỏ nhất = {chenh}mm > 6mm (mục 4.2).")

    if dau_vao.so_lop > dau_vao.so_lop_toi_da_cho_phep:
        vi_pham.append(
            f"Cần {dau_vao.so_lop} lớp thép, vượt quá {dau_vao.so_lop_toi_da_cho_phep} lớp cho phép (mục 4.4)."
        )

    dat_ep_vo_bung, Q_gioi_han = cot_dai.kiem_tra_ep_vo_bung(dau_vao.Q, dau_vao.Rb, dau_vao.b, dau_vao.h0)
    if not dat_ep_vo_bung:
        vi_pham.append(
            f"Q={dau_vao.Q:.1f}kN > Q_gioi_han ép vỡ bụng={Q_gioi_han:.1f}kN — phải tăng "
            "tiết diện/cấp bê tông, không thể chỉ tăng cốt đai (mục 3.1)."
        )

    qsw = cot_dai.tinh_qsw(dau_vao.Rsw, dau_vao.Asw, dau_vao.sw)
    Qb1 = cot_dai.tinh_Qb1(dau_vao.Rbt, dau_vao.b, dau_vao.h0)
    Qsw1 = cot_dai.tinh_Qsw1(qsw, dau_vao.h0)
    if not cot_dai.dieu_kien_co_ban_chiu_cat(dau_vao.Q, Qb1, Qsw1):
        vi_pham.append(
            f"Q={dau_vao.Q:.1f}kN > Qb,1+Qsw,1={Qb1 + Qsw1:.1f}kN — cốt đai đã chọn "
            "chưa đủ khả năng chịu cắt (mục 3.2)."
        )

    return KetQuaVerify(dat=not vi_pham, vi_pham=vi_pham)


@dataclass(frozen=True)
class DauVaoVerifyCot:
    """Dữ liệu cần để verify 1 tiết diện cột đã chọn thép xong (thép đối xứng)."""

    As_thuc: float  # mm² — As = A's đã chọn (mỗi phía)
    b: float
    h0: float
    do_manh_L0_h: float
    N: float  # kN
    e: float  # mm — cánh tay đòn đã tính theo mục 2.5 (tinh_e)
    Rb: float
    Rsc: float
    x: float  # mm — x đã xác định (nhánh lớn hoặc bé)
    a_prime: float
    mu_max_moi_phia: float = cot_doc.MU_MAX_COT_MOI_PHIA_PHAN_TRAM


def kiem_tra_tong_hop_cot(dau_vao: DauVaoVerifyCot) -> KetQuaVerify:
    """Chạy điều kiện Ne ≤ Mu và μ cho 1 tiết diện cột đối xứng đã chọn thép."""
    from . import uon_nen  # import cục bộ để tránh phụ thuộc vòng ở module-level

    vi_pham: list[str] = []

    Ne = dau_vao.N * dau_vao.e / 1000  # kN·m
    Mu = uon_nen.tinh_Mu_cot(dau_vao.Rb, dau_vao.b, dau_vao.x, dau_vao.h0, dau_vao.Rsc, dau_vao.As_thuc, dau_vao.a_prime)
    if Ne > Mu * 1.02:  # dung sai 2% theo mục 12 pseudocode "canh_bao_neu(N*e > Mu*1.02)"
        vi_pham.append(f"N·e={Ne:.1f}kN·m > Mu={Mu:.1f}kN·m (vượt quá 2% dung sai) — thép chưa đủ (mục 2.5).")

    mu_moi_phia = 100 * dau_vao.As_thuc / (dau_vao.b * dau_vao.h0)
    mu_min = cot_doc.tra_mu_min(dau_vao.do_manh_L0_h)
    if mu_moi_phia < mu_min:
        vi_pham.append(f"μ mỗi phía={mu_moi_phia:.3f}% < μ_min={mu_min:.3f}% (mục 4.1, mục 10.6 nguyên tắc 5).")
    if mu_moi_phia > dau_vao.mu_max_moi_phia:
        vi_pham.append(
            f"μ mỗi phía={mu_moi_phia:.3f}% > {dau_vao.mu_max_moi_phia:.3f}% "
            "(mục 4.1, mục 10.6 nguyên tắc 5 — tổng μt nên ≤6%)."
        )

    return KetQuaVerify(dat=not vi_pham, vi_pham=vi_pham)
