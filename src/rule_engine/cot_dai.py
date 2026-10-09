"""
Cốt thép ngang chịu cắt (cốt đai) — RULES_TCVN5574.md mục 3 (TCVN 5574:2018
mục 8.1.3) + mục 5 (bước đai cấu tạo, mục 10.3.4).

Quy ước đơn vị trong module này: lực cắt Q, lực dọc N tính bằng kN (đầu vào
chuẩn hoá từ Input Adapter); Rb, Rbt, Rsw tính bằng MPa (N/mm²); b, h0, C, sw
tính bằng mm. Mọi hàm tự quy đổi nội bộ khi cần cộng/so sánh hai đơn vị khác
hệ (kN với N) — có ghi chú ngay tại chỗ quy đổi.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

PHI_B1 = 0.3  # mục 3.1 — hệ số điều kiện chống ép vỡ bụng.
PHI_B2 = 1.5  # mục 3.2 — hệ số trong công thức Qb tổng quát.
PHI_SW = 0.75  # mục 3.2 — hệ số trong Qsw tổng quát.


# ---------------------------------------------------------------------------
# 3.1 — Điều kiện chống ép vỡ bụng (khống chế kích thước tiết diện)
# ---------------------------------------------------------------------------


def kiem_tra_ep_vo_bung(
    Q: float, Rb: float, b: float, h0: float, phi_n: float = 1.0
) -> tuple[bool, float]:
    """Q ≤ φb1·Rb·b·h0 (nhân thêm φn nếu có N — mục 3.3). Mục 3.1.

    Trả về (đạt?, Q_gioi_han theo kN). Nếu không đạt: PHẢI tăng b, h hoặc cấp
    bê tông — không thể chỉ tăng cốt đai (ghi rõ trong tài liệu).
    """
    Q_gioi_han = phi_n * PHI_B1 * Rb * b * h0 / 1000  # N -> kN
    return Q <= Q_gioi_han, Q_gioi_han


# ---------------------------------------------------------------------------
# 3.2 — Điều kiện cơ bản chịu cắt (công thức đơn giản hoá, C = h0..2h0)
# ---------------------------------------------------------------------------


def tinh_qsw(Rsw: float, Asw: float, sw: float) -> float:
    """qsw = Rsw·Asw/sw (N/mm). Asw: tổng diện tích các nhánh đai trong 1 mặt
    cắt (mm²), sw: bước đai (mm)."""
    return Rsw * Asw / sw


def tinh_Qb1(Rbt: float, b: float, h0: float, phi_n: float = 1.0) -> float:
    """Qb,1 = φn·0,5·Rbt·b·h0 — công thức đơn giản hoá, mục 3.2. Trả về kN."""
    return phi_n * 0.5 * Rbt * b * h0 / 1000


def tinh_Qsw1(qsw: float, h0: float) -> float:
    """Qsw,1 = qsw·h0 — công thức đơn giản hoá, mục 3.2. Trả về kN."""
    return qsw * h0 / 1000


def he_so_gan_goi_tua_cho_Qb(a: float, h0: float) -> float:
    """Hệ số nhân thêm vào Qb,1 khi tiết diện gần gối tựa a < 2,5h0 — mục 3.2.

    Hệ số = 2,5/(a/h0), chặn sao cho Qb,1 sau khi nhân không vượt 2,5·Rbt·b·h0
    (việc chặn trần thực hiện ở nơi gọi vì cần biết Rbt·b·h0 gốc)."""
    if a >= 2.5 * h0:
        return 1.0
    return 2.5 / (a / h0)


def he_so_gan_goi_tua_cho_Qsw(a: float, h0: float) -> float:
    """Hệ số nhân thêm vào Qsw,1 khi a < h0 — mục 3.2: nhân với a/h0."""
    if a >= h0:
        return 1.0
    return a / h0


def dieu_kien_co_ban_chiu_cat(Q: float, Qb1: float, Qsw1: float) -> bool:
    """Q1 ≤ Qb,1 + Qsw,1 — điều kiện đơn giản hoá cơ bản. Mục 3.2."""
    return Q <= Qb1 + Qsw1


def can_dat_dai_theo_tinh_toan(qsw: float, Rbt: float, b: float) -> bool:
    """qsw ≥ 0,25·Rbt·b — điều kiện để kể cốt đai vào khả năng chịu cắt. Mục 3.2.

    Nếu không thỏa nhưng vẫn muốn kể cốt đai, dùng `tinh_Qb_khi_qsw_nho`."""
    return qsw >= 0.25 * Rbt * b


def tinh_Qb_khi_qsw_nho(phi_b2: float, h0: float, qsw: float, C: float) -> float:
    """Qb = 4·φb2·h0²·qsw/C khi qsw không đạt ngưỡng 0,25Rbt·b. Mục 3.2. Trả về kN."""
    return 4 * phi_b2 * h0**2 * qsw / C / 1000


def buoc_dai_toi_da_theo_kha_nang_chiu_cat(Rbt: float, b: float, h0: float, Q: float) -> float:
    """sw,max sao cho khả năng chịu cắt của riêng bê tông (không kể đai) vẫn đủ:
    sw,max/h0 = Rbt·b·h0/Q → sw,max = Rbt·b·h0²/Q. Mục 3.2. Q tính bằng kN,
    quy đổi sang N để cùng hệ với Rbt·b·h0² (N·mm²)."""
    Q_N = Q * 1000
    return Rbt * b * h0**2 / Q_N


# ---------------------------------------------------------------------------
# 3.3 — Hệ số φn khi cấu kiện chịu đồng thời N (quan trọng cho CỘT)
# ---------------------------------------------------------------------------


def tinh_phi_n_nen(N: float, A: float, Rb: float) -> float:
    """φn khi N là lực NÉN — mục 3.3. N: kN, A: mm² (tiết diện bê tông).

    σm = N/A (MPa, N quy đổi sang N từ kN). 3 nhánh theo tỷ số σm/Rb.
    """
    sigma_m = N * 1000 / A
    ty_so = sigma_m / Rb
    if ty_so < 0:
        raise ValueError("N phải >= 0 khi gọi tinh_phi_n_nen (N là lực nén).")
    if ty_so <= 0.25:
        return 1 + sigma_m / Rb
    if ty_so <= 0.75:
        return 1.25
    if ty_so <= 1.0:
        return 5 * (1 - ty_so)
    raise ValueError("σm > Rb — tiết diện quá bé so với N, kiểm tra lại trước khi tính đai.")


def tinh_phi_n_keo(N: float, A: float, Rbt: float) -> float:
    """φn khi N là lực KÉO — mục 3.3. σt = N/A (MPa). φn = 1 − σt/(2Rbt)."""
    sigma_t = N * 1000 / A
    return 1 - sigma_t / (2 * Rbt)


def bo_qua_anh_huong_cot_thep_khi_tinh_sigma(mu_doc_phan_tram: float) -> bool:
    """Cho phép bỏ qua ảnh hưởng cốt thép dọc khi tính σm, σt nếu μ_dọc ≤ 3%. Mục 3.3."""
    return mu_doc_phan_tram <= 3.0


# ---------------------------------------------------------------------------
# 3.4 — Kiểm tra theo tiết diện nghiêng chịu mô men (vị trí cắt/uốn cốt dọc)
# ---------------------------------------------------------------------------


def tinh_Ms(Rs: float, As: float, h0: float) -> float:
    """Ms = Rs·As·zs, zs = 0,9h0 — mục 3.4. Trả về kN·m."""
    zs = 0.9 * h0
    return Rs * As * zs / 1e6


def tinh_Msw(Qsw: float, C: float) -> float:
    """Msw = 0,5·Qsw·C — mục 3.4. Qsw: kN, C: mm → trả về kN·m."""
    return 0.5 * Qsw * C / 1000


def kiem_tra_tiet_dien_nghieng_mo_men(M: float, Ms: float, Msw: float) -> bool:
    """M ≤ Ms + Msw — dùng để xác định vị trí hợp lý cắt bớt/uốn cốt dọc. Mục 3.4."""
    return M <= Ms + Msw


# ---------------------------------------------------------------------------
# 3.5 — Xoắn (điều kiện được phép bỏ qua)
# ---------------------------------------------------------------------------


def duoc_phep_bo_qua_xoan(T: float, Rb: float, b: float, h: float) -> bool:
    """T ≤ 0,1·Rb·b²·h — mục 3.5. T: kN·m. Với khung phẳng, T ngoại lực ≈ 0
    nên điều kiện này gần như luôn thỏa — có thể bỏ qua kiểm tra xoắn an toàn."""
    gioi_han = 0.1 * Rb * b**2 * h / 1e6
    return T <= gioi_han


# ---------------------------------------------------------------------------
# 5.1-5.3 — Cấu tạo cốt đai: đường kính tối thiểu, bước đai dầm/cột
# ---------------------------------------------------------------------------


def duong_kinh_dai_toi_thieu(d_doc_max: float) -> float:
    """d_đai ≥ max(0,25×d_dọc,max ; 6mm). Mục 5.1."""
    return max(0.25 * d_doc_max, 6.0)


def buoc_dai_max_dam(h0: float, can_tinh_toan: bool) -> float:
    """Bước đai tối đa — dầm. Mục 5.2.

    can_tinh_toan=True (Q vượt khả năng chịu cắt riêng bê tông): min(0,5h0;300).
    can_tinh_toan=False (đai cấu tạo, Q ≤ khả năng bê tông): min(0,75h0;500).
    """
    return min(0.5 * h0, 300.0) if can_tinh_toan else min(0.75 * h0, 500.0)


def buoc_dai_max_cot(d_doc_min: float, dieu_kien_dac_biet: bool) -> float:
    """Bước đai tối đa — cột. Mục 5.3.

    dieu_kien_dac_biet=True (μ_dọc > 1,5% một mặt, hoặc trong đoạn nối chồng):
    min(10d_dọc,min; 300). Ngược lại: min(15d_dọc,min; 500). Làm tròn xuống bội số 50.
    """
    val = min(10 * d_doc_min, 300.0) if dieu_kien_dac_biet else min(15 * d_doc_min, 500.0)
    import math
    return math.floor(val / 50.0) * 50.0


def can_dai_phu_cho_cot(b: float, so_thanh_1_canh: int) -> bool:
    """b>400mm và >4 thanh/cạnh → bắt buộc thêm đai phụ. Mục 5.3."""
    return b > 400 and so_thanh_1_canh > 4


def buoc_dai_thiet_ke(s_max_cau_tao: float, Rsw: float, Asw: float, qsw_yeu_cau: float) -> float:
    """s thiết kế = min(s_max cấu tạo, s_tt = Rsw·Asw/qsw). Mục 5.2 (nguyên tắc 7,
    mục 10.6). s_ct theo vị trí đầu/giữa dầm áp dụng ở lớp gọi hàm này (tuỳ
    thuộc từng đoạn dầm cụ thể, không cố định trong hàm dùng chung)."""
    if qsw_yeu_cau <= 0:
        return s_max_cau_tao
    s_tt = Rsw * Asw / qsw_yeu_cau
    return min(s_max_cau_tao, s_tt)


# ---------------------------------------------------------------------------
# Cốt treo (giật đứt) khi dầm phụ gác vào dầm chính — mục 10.5, nguyên tắc 6/mục 10.6
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KetQuaCotTreo:
    so_dai_can_1_ben: int
    tong_Asw_yeu_cau: float  # mm²


def tinh_cot_treo(
    F: float, h: float, hs: float, h0: float, Rsw: float, Asw_1_dai: float
) -> KetQuaCotTreo:
    """Cốt treo chống giật đứt: F·(1 − hs/h0) ≤ ΣRsw·Asw. Mục 10.5.

    F: lực tập trung do dầm phụ truyền vào dầm chính (kN). hs: khoảng cách từ
    mép trên dầm chính đến mép trên dầm phụ (mm). Asw_1_dai: diện tích 1 đai
    (tất cả các nhánh của 1 đai, mm²). Số lượng đai LUÔN làm tròn lên (nguyên
    tắc 6, mục 10.6), chia đều 2 bên vị trí lực tập trung.
    """
    F_N = F * 1000
    tong_Asw_yeu_cau = F_N * (1 - hs / h0) / Rsw
    tong_so_dai = math.ceil(tong_Asw_yeu_cau / Asw_1_dai)
    so_dai_1_ben = math.ceil(tong_so_dai / 2)
    return KetQuaCotTreo(so_dai_can_1_ben=so_dai_1_ben, tong_Asw_yeu_cau=tong_Asw_yeu_cau)
