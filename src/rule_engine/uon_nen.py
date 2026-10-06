"""
Uốn + nén/kéo lệch tâm (tiết diện thẳng góc) — RULES_TCVN5574.md mục 2
(TCVN 5574:2018 mục 8.1.2).

QUAN TRỌNG — phạm vi sử dụng đúng như tài liệu quy định (mục 2, đoạn mở đầu):
mô-đun này KHÔNG dùng để agent tự tính As thay ETABS. Hai công dụng hợp lệ:

1. Tự kiểm tra chéo (verify): có As đã chọn (đã làm tròn lên theo bảng đường
   kính) → tính lại Mu/Nu → so với M, N gốc để xác nhận vẫn đủ khả năng chịu lực.
2. Trường hợp đặc biệt của cột (ví dụ kiểm chứng "cột 22", mục 10.4 tài liệu):
   khi cần suy As đối xứng trực tiếp từ cặp (M, N) nguy hiểm nhất, dùng
   `thiet_ke_cot_doi_xung_lech_tam_be`, vốn CHỈ giải đồng thời hai phương trình
   đã có sẵn trong mục 2.5 (điều kiện Ne và công thức x lệch tâm bé) bằng
   phương pháp số (chia đôi khoảng - bisection, xác định/deterministic, không
   ngẫu nhiên) — không tự bịa thêm công thức thực nghiệm bậc 2 nào khác ngoài
   những gì mục 2.5 đã cho.
"""

from __future__ import annotations

from dataclasses import dataclass

EPS_B2 = 0.0035  # εb2 — biến dạng giới hạn bê tông vùng nén, tải ngắn hạn, mục 2.1.


def tinh_xiR(Rs: float, Es: float, be_tong_dac_biet: bool = False) -> float:
    """ξR — chiều cao tương đối giới hạn vùng nén. Mục 2.1.

    be_tong_dac_biet=True: bê tông B70-B100 hoặc bê tông hạt nhỏ → hệ số 0,7
    thay cho 0,8 (theo đúng ghi chú mục 2.1).
    """
    he_so = 0.7 if be_tong_dac_biet else 0.8
    eps_s_el = Rs / Es
    return he_so / (1 + eps_s_el / EPS_B2)


def tinh_alpha_R(xiR: float) -> float:
    """αR = ξR·(1 − ξR/2) — dùng trong kiểm tra αm ≤ αR khi tính As dầm bằng
    phương pháp hệ số αm (đối chiếu ví dụ mục 10.5: αm=0,262 < αR)."""
    return xiR * (1 - xiR / 2)


def tinh_ea(L: float, h: float) -> float:
    """Độ lệch tâm ngẫu nhiên ea (mm) — mục 2.2. L, h cùng đơn vị (mm)."""
    return max(L / 600, h / 30, 10.0)


def tinh_e0(e1: float, ea: float, sieu_tinh: bool = True) -> float:
    """e0 — độ lệch tâm ban đầu. Mục 2.2.

    sieu_tinh=True (kết cấu siêu tĩnh, trường hợp phổ biến của khung toàn khối):
    e0 = max(e1, ea). sieu_tinh=False (kết cấu tĩnh định): e0 = e1 + ea.
    """
    return max(e1, ea) if sieu_tinh else e1 + ea


# ---------------------------------------------------------------------------
# Dầm — tiết diện chữ nhật (mục 2.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KetQuaMuDam:
    Mu: float  # kN·m — khả năng chịu mô men
    x: float  # mm — chiều cao vùng nén
    dieu_kien_deo_thoa: bool  # x <= xiR*h0 ?


def tinh_Mu_dam_chu_nhat(
    Rb: float,
    b: float,
    h0: float,
    Rs: float,
    As: float,
    xiR: float,
    Rsc: float = 0.0,
    As_prime: float = 0.0,
    a_prime: float = 0.0,
    dat_doi_xung: bool = False,
) -> KetQuaMuDam:
    """Mu của dầm chữ nhật (cốt đơn hoặc kép) — mục 2.3.

    Rb (MPa), b,h0,a_prime (mm), Rs,Rsc (MPa), As,As_prime (mm²) → Mu (kN·m).
    Quy đổi đơn vị nội bộ: N·mm → kN·m bằng cách chia 1e6 (vì Rb tính bằng
    N/mm² = MPa, và b·x·h0 ra N·mm).

    dat_doi_xung=True: áp dụng nhánh "đặt cốt đối xứng" (RsAs = RscA's) —
    Mu = Rs·As·(h0−a′); nếu x tính không kể A's < 2a′ thì thay a′ bằng x/2.
    """
    if dat_doi_xung:
        x_khong_ke_a_prime = (Rs * As) / (Rb * b)
        a_dung = a_prime
        if x_khong_ke_a_prime < 2 * a_prime:
            a_dung = x_khong_ke_a_prime / 2
        Mu = Rs * As * (h0 - a_dung) / 1e6
        return KetQuaMuDam(Mu=Mu, x=x_khong_ke_a_prime, dieu_kien_deo_thoa=True)

    x = (Rs * As - Rsc * As_prime) / (Rb * b)
    dieu_kien_deo_thoa = x <= xiR * h0
    if not dieu_kien_deo_thoa:
        # Điều kiện dẻo bắt buộc x <= xiR*h0 — khi As thực tế bố trí vượt As lý
        # thuyết, lấy thẳng x = xiR*h0 để tính lại khả năng chịu lực thực tế
        # (đúng theo hướng dẫn cuối mục 2.3).
        x = xiR * h0

    Mu = (Rb * b * x * (h0 - 0.5 * x) + Rsc * As_prime * (h0 - a_prime)) / 1e6
    return KetQuaMuDam(Mu=Mu, x=x, dieu_kien_deo_thoa=dieu_kien_deo_thoa)


# ---------------------------------------------------------------------------
# Dầm — tiết diện chữ T / chữ I, cánh nằm vùng nén (mục 2.4)
# ---------------------------------------------------------------------------


def be_rong_canh_tinh_toan(
    nhip: float,
    h_f_prime: float,
    h: float,
    khoang_cach_thong_thuy_suon: float | None = None,
    co_suon_ngang: bool = True,
    la_canh_console: bool = False,
) -> float:
    """Bề rộng cánh b'f mỗi bên đưa vào tính toán — mục 2.4.

    Trả về phần bề rộng cánh MỘT BÊN (không kể bề rộng sườn b) được phép kể
    vào tính toán; b'f tổng = b + 2 * kết quả hàm này (nếu cánh đối xứng 2 bên)
    hoặc cộng riêng từng bên nếu không đối xứng.
    """
    gioi_han = [nhip / 6]

    if la_canh_console:
        if h_f_prime >= 0.1 * h:
            gioi_han.append(6 * h_f_prime)
        elif h_f_prime >= 0.05 * h:
            gioi_han.append(3 * h_f_prime)
        else:
            return 0.0  # bỏ qua cánh console quá mỏng
    else:
        if co_suon_ngang and h_f_prime >= 0.1 * h:
            if khoang_cach_thong_thuy_suon is not None:
                gioi_han.append(khoang_cach_thong_thuy_suon / 2)
        elif h_f_prime < 0.1 * h:
            gioi_han.append(6 * h_f_prime)

    return min(gioi_han)


def tinh_Mu_dam_chu_T(
    Rb: float,
    b: float,
    b_f_prime: float,
    h_f_prime: float,
    h0: float,
    Rs: float,
    As: float,
    xiR: float,
    Rsc: float = 0.0,
    As_prime: float = 0.0,
    a_prime: float = 0.0,
) -> KetQuaMuDam:
    """Mu của dầm chữ T/chữ I (cánh nằm vùng nén) — mục 2.4.

    Kiểm tra trục trung hòa: nếu RsAs ≤ Rb·b'f·h'f + RscA's → tính như tiết
    diện chữ nhật rộng b'f (trục qua cánh). Ngược lại, trục qua sườn.
    """
    if Rs * As <= Rb * b_f_prime * h_f_prime + Rsc * As_prime:
        return tinh_Mu_dam_chu_nhat(
            Rb, b_f_prime, h0, Rs, As, xiR, Rsc, As_prime, a_prime
        )

    x = (Rs * As - Rsc * As_prime - Rb * (b_f_prime - b) * h_f_prime) / (Rb * b)
    dieu_kien_deo_thoa = x <= xiR * h0
    if not dieu_kien_deo_thoa:
        x = xiR * h0

    Mu = (
        Rb * b * x * (h0 - 0.5 * x)
        + Rb * (b_f_prime - b) * h_f_prime * (h0 - 0.5 * h_f_prime)
        + Rsc * As_prime * (h0 - a_prime)
    ) / 1e6
    return KetQuaMuDam(Mu=Mu, x=x, dieu_kien_deo_thoa=dieu_kien_deo_thoa)


# ---------------------------------------------------------------------------
# Cột — nén lệch tâm, tiết diện chữ nhật (mục 2.5)
# ---------------------------------------------------------------------------


def thu_lech_tam_lon(
    N: float, Rs: float, As: float, Rsc: float, As_prime: float, Rb: float, b: float
) -> float:
    """x theo nhánh lệch tâm lớn (thử trước, theo nguyên tắc 3 mục 10.6).

    N (kN) → quy đổi N·mm bằng ×1000 để cùng hệ N/MPa với Rb, b (mm).
    """
    return (N * 1000 + Rs * As - Rsc * As_prime) / (Rb * b)


def thu_lech_tam_be(
    N: float,
    Rs: float,
    As: float,
    Rsc: float,
    As_prime: float,
    Rb: float,
    b: float,
    h0: float,
    xiR: float,
) -> float:
    """x theo nhánh lệch tâm bé (dùng khi x của thu_lech_tam_lon > ξR·h0). Mục 2.5.

    Đây là công thức KIỂM TRA (đã biết As, A's) — không dùng để thiết kế As
    từ đầu. Muốn thiết kế As đối xứng từ (N, e) khi rơi vào lệch tâm bé, dùng
    `thiet_ke_cot_doi_xung_lech_tam_be`.
    """
    tu_so = N * 1000 + Rs * As * (1 + xiR) / (1 - xiR) - Rsc * As_prime
    mau_so = Rb * b + 2 * Rs * As / (h0 * (1 - xiR))
    return tu_so / mau_so


def tinh_Mu_cot(
    Rb: float,
    b: float,
    x: float,
    h0: float,
    Rsc: float,
    As_prime: float,
    a_prime: float,
) -> float:
    """Vế phải điều kiện Ne ≤ ... của cột — mục 2.5, trả về kN·m."""
    return (Rb * b * x * (h0 - 0.5 * x) + Rsc * As_prime * (h0 - a_prime)) / 1e6


def tinh_e(e0: float, eta: float, h0: float, a_prime: float) -> float:
    """e = e0·η + (h0−a′)/2 — cánh tay đòn dùng trong điều kiện Ne ≤ ... mục 2.5."""
    return e0 * eta + (h0 - a_prime) / 2


def thiet_ke_cot_doi_xung_lech_tam_be(
    N: float,
    e: float,
    Rb: float,
    b: float,
    h0: float,
    a_prime: float,
    Rs: float,
    Rsc: float,
    xiR: float,
    dung_sai_mm: float = 0.5,
    so_lan_lap_toi_da: int = 200,
) -> tuple[float, float]:
    """Giải đồng thời As=A's và x cho cột đối xứng, nhánh lệch tâm bé.

    Dùng khi thu_lech_tam_lon(...) cho x > ξR·h0 và cần suy As trực tiếp từ
    cặp (N, e) — đúng tình huống ví dụ "cột 22" mục 10.4. Đây KHÔNG phải một
    công thức mới: chỉ giải đồng thời 2 phương trình đã có sẵn trong mục 2.5
    bằng phương pháp chia đôi khoảng (bisection — xác định, không ngẫu nhiên):

        (a) Ne = Rb·b·x·(h0−0,5x) + Rsc·As·(h0−a′)          [điều kiện Ne]
        (b) x  = [N + Rs·As·(1+ξR)/(1−ξR) − Rsc·As] / [Rb·b + 2Rs·As/(h0(1−ξR))]

    với As=A's, Rs=Rsc (thép đối xứng dùng chung 1 nhóm — trường hợp phổ biến
    và đúng với ví dụ kiểm chứng). Trả về (x, As).

    Miền tìm x hợp lệ cho nhánh lệch tâm bé: (ξR·h0, h0). Dò nghiệm bằng cách
    tìm x sao cho As suy từ (a) khớp với As suy ngược từ (b).
    """
    Ne = N * e / 1000  # kN·mm -> kN·m để cùng đơn vị Mu ở trên (Ne tính bằng kN·m)

    def as_tu_dieu_kien_Ne(x: float) -> float:
        # (a): As = [Ne - Rb*b*x*(h0-0.5x)/1e6] / [Rsc*(h0-a')/1e6]  (kN·m cả hai vế)
        tu = Ne - (Rb * b * x * (h0 - 0.5 * x)) / 1e6
        mau = Rsc * (h0 - a_prime) / 1e6
        return tu / mau

    def x_tu_cong_thuc_2_5(As: float) -> float:
        return thu_lech_tam_be(N, Rs, As, Rsc, As, Rb, b, h0, xiR)

    def sai_so(x: float) -> float:
        As_a = as_tu_dieu_kien_Ne(x)
        x_b = x_tu_cong_thuc_2_5(As_a)
        return x_b - x

    x_lo, x_hi = xiR * h0, h0
    f_lo, f_hi = sai_so(x_lo), sai_so(x_hi)
    if f_lo * f_hi > 0:
        raise ValueError(
            "Không tìm được nghiệm x trong khoảng (xiR*h0, h0) cho nhánh lệch "
            "tâm bé — kiểm tra lại input (N, e, tiết diện) trước khi dùng hàm này."
        )

    for _ in range(so_lan_lap_toi_da):
        x_mid = (x_lo + x_hi) / 2
        f_mid = sai_so(x_mid)
        if abs(f_mid) < 1e-6 or (x_hi - x_lo) < dung_sai_mm:
            break
        if f_lo * f_mid <= 0:
            x_hi, f_hi = x_mid, f_mid
        else:
            x_lo, f_lo = x_mid, f_mid

    x_final = (x_lo + x_hi) / 2
    As_final = as_tu_dieu_kien_Ne(x_final)
    return x_final, As_final


# ---------------------------------------------------------------------------
# Hệ số uốn dọc η (mục 2.6) — chỉ cần khi L0/i > 14
# ---------------------------------------------------------------------------


def can_xet_uon_doc(L0: float, i: float) -> bool:
    """True nếu L0/i > 14 → bắt buộc xét hệ số uốn dọc η. Mục 2.6."""
    return (L0 / i) > 14


def tinh_phi_l(M_L1: float, M_L: float) -> float:
    """φl = 1 + ML1/ML (≤ 2). Mục 2.6. ML1: mô men do tải thường xuyên + tạm
    thời dài hạn; ML: mô men do toàn bộ tải trọng."""
    return min(1 + M_L1 / M_L, 2.0)


def tinh_delta_e(e0: float, h: float) -> float:
    """δe = e0/h, chặn trong [0,15 ; 1,5]. Mục 2.6."""
    return min(max(e0 / h, 0.15), 1.5)


def tinh_kb(phi_l: float, delta_e: float) -> float:
    """kb = 0,15 / [φl·(0,3+δe)]. Mục 2.6."""
    return 0.15 / (phi_l * (0.3 + delta_e))


def tinh_Ncr(D: float, L0: float) -> float:
    """Ncr = π²D / L0² (kN nếu D tính bằng kN·m² và L0 bằng m). Mục 2.6."""
    return (3.141592653589793**2) * D / (L0**2)


def tinh_D(kb: float, Eb: float, I: float, Es: float, Is: float) -> float:
    """D = kb·Eb·I + 0,7·Es·Is. Mục 2.6.

    Chú ý đơn vị: Eb, Es tính bằng MPa (N/mm²); I, Is tính bằng mm⁴ → D ra
    N·mm² ; cần tự quy đổi về kN·m² (chia 1e9) trước khi dùng cùng tinh_Ncr
    nếu L0 tính bằng m — quy đổi đơn vị là trách nhiệm của lời gọi hàm.
    """
    return kb * Eb * I + 0.7 * Es * Is


def tinh_eta(N: float, Ncr: float) -> float:
    """η = 1 / (1 − N/Ncr). Mục 2.6. N, Ncr cùng đơn vị."""
    if N >= Ncr:
        raise ValueError(
            "N >= Ncr: cột mất ổn định theo tính toán (điều kiện uốn dọc không "
            "thỏa) — cần tăng tiết diện hoặc giảm chiều dài tính toán L0."
        )
    return 1 / (1 - N / Ncr)


# ---------------------------------------------------------------------------
# Công thức đơn giản hoá cột đối xứng, e0 ≤ h/30, L0/h ≤ 20 (mục 2.7)
# ---------------------------------------------------------------------------

# Bảng 16 (trích) — chỉ 2 điểm được tài liệu cho rõ, nội suy tuyến tính giữa
# 2 điểm này theo đúng RULES_TCVN5574.md mục 2.7. KHÔNG ngoại suy ra ngoài
# [10, 20] vì tài liệu không cho thêm điểm nào khác — ngoài khoảng này phải
# tra bảng 16 đầy đủ trong TCVN 5574:2018 (chưa có trong phạm vi dữ liệu).
_BANG16_DIEM_DA_BIET_DAI_HAN = {10: 0.90, 20: 0.70}
_BANG16_DIEM_DA_BIET_NGAN_HAN = {10: 0.90, 20: 0.85}


def tra_phi_bang16(L0_h: float, tai_dai_han: bool = True) -> float:
    """φ tra Bảng 16 theo độ mảnh L0/h — mục 2.7 (chỉ nội suy trong [10,20])."""
    diem = _BANG16_DIEM_DA_BIET_DAI_HAN if tai_dai_han else _BANG16_DIEM_DA_BIET_NGAN_HAN
    if not (10 <= L0_h <= 20):
        raise ValueError(
            "RULES_TCVN5574.md mục 2.7 chỉ cho 2 điểm tra Bảng 16 tại L0/h=10 và "
            "L0/h=20 — L0/h nằm ngoài khoảng này cần tra bảng 16 đầy đủ trong "
            "TCVN 5574:2018 (chưa nằm trong dữ liệu hiện có), không tự ngoại suy."
        )
    phi_10, phi_20 = diem[10], diem[20]
    return phi_10 + (phi_20 - phi_10) * (L0_h - 10) / (20 - 10)


def kiem_tra_don_gian_hoa(
    N: float, phi: float, Rb: float, A: float, Rsc: float, As_tot: float
) -> tuple[bool, float]:
    """N ≤ φ(Rb·A + Rsc·As,tot) — mục 2.7. N (kN); trả về (đạt?, N_max theo kN)."""
    N_max = phi * (Rb * A + Rsc * As_tot) / 1000
    return N <= N_max, N_max


_HE_SO_L0_THEO_LIEN_KET: dict[str, float] = {
    "2_khop": 1.0,
    "ngam_tu_do": 2.0,  # công-xôn
    "khop-ngam": 0.7,
    "2_ngam": 0.5,
}


def chieu_dai_tinh_toan_L0(L: float, lien_ket: str) -> float:
    """L0 theo liên kết 2 đầu cấu kiện — mục 2.7 (4 trường hợp cơ bản có trong
    tài liệu; TCVN có bảng đầy đủ hơn 10 trường hợp 0,5L–2,0L, chưa đưa hết
    vào đây vì tài liệu chỉ liệt kê 4 trường hợp này)."""
    key = lien_ket.strip().lower()
    if key not in _HE_SO_L0_THEO_LIEN_KET:
        raise ValueError(
            f"Loại liên kết '{lien_ket}' chưa có trong RULES_TCVN5574.md mục 2.7 "
            f"(hỗ trợ: {sorted(_HE_SO_L0_THEO_LIEN_KET)}) — cần bổ sung tài liệu "
            "trước khi dùng, không tự đoán hệ số."
        )
    return _HE_SO_L0_THEO_LIEN_KET[key] * L


# ---------------------------------------------------------------------------
# Kéo đúng tâm / kéo lệch tâm (mục 2.8)
# ---------------------------------------------------------------------------


def keo_dung_tam_Nmax(Rs: float, As_tot: float) -> float:
    """N ≤ Rs·As,tot — mục 2.8. Trả về N_max (kN)."""
    return Rs * As_tot / 1000
