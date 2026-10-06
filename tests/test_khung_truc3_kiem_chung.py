"""
Đối chiếu Rule Engine với 2 bộ dữ liệu kiểm chứng bắt buộc trong
RULES_TCVN5574.md mục 10 (Khung trục 3, trường học): CỘT 22 (mục 10.4) và
DẦM 40-41 (mục 10.5). Vật liệu: bê tông B30, cốt dọc CB500-V, cốt đai CB240-T
(mục 10.1).

Ghi chú về dung sai: các số liệu trong tài liệu (e0, η, e, x, As...) đã được
LÀM TRÒN qua nhiều bước tính tay trung gian, nên khi tính lại bằng code, sai
số vài % giữa kết quả code và số liệu sách là bình thường — đúng theo yêu cầu
"khớp trong sai số làm tròn hợp lý", KHÔNG yêu cầu khớp tuyệt đối từng chữ số.

Ghi chú riêng cho cột 22: tài liệu nói ví dụ dùng "công thức thực nghiệm bậc 2
(n, ε, γa)" để ra x=326mm, As≈1250mm² — nhưng KHÔNG cho đầy đủ công thức đó
(chỉ nêu tên 3 biến không thứ nguyên). Vì vậy Rule Engine ở đây KHÔNG cài công
thức đó (đúng nguyên tắc "không tự suy diễn công thức khi tài liệu không nói
rõ"), mà dùng cách giải đồng thời 2 phương trình ĐÃ CÓ trong mục 2.5 (điều
kiện Ne và công thức x lệch tâm bé) bằng phương pháp số xác định (bisection).
Bài kiểm tra chính (đáng tin cậy nhất) vì vậy là bài VERIFY: lấy đúng thép
CUỐI CÙNG sách đã chọn (2ϕ25+1ϕ22 mỗi phía) và xác nhận nó thoả Ne ≤ Mu theo
đúng công thức mục 2.5 — đây mới là mục đích đã công bố của mục 2 (tự kiểm
tra chéo), không phải suy As từ đầu.
"""

import pytest

from src.rule_engine import cot_dai, cot_doc, uon_nen, vat_lieu, verify

# --- Vật liệu dùng chung (mục 10.1) ---
BE_TONG = vat_lieu.lay_be_tong("B30")
THEP_DOC = vat_lieu.lay_thep("CB500-V")
THEP_DAI = vat_lieu.lay_thep("CB240-T")
XI_R = uon_nen.tinh_xiR(THEP_DOC.Rs, THEP_DOC.Es)
ALPHA_R = uon_nen.tinh_alpha_R(XI_R)


def test_xiR_va_alphaR_muc_10_1():
    # "ξR = 0,8/(1+(435/200000)/0,0035) = 0,493; αR = ξR(1−ξR/2) = 0,371" — mục 10.1.
    assert XI_R == pytest.approx(0.493, abs=0.001)
    assert ALPHA_R == pytest.approx(0.371, abs=0.001)


# ---------------------------------------------------------------------------
# CỘT 22, tầng 1 (250×600mm) — mục 10.4
# TH12: M=417,74 kNm, N=1514,38 kN.
# ---------------------------------------------------------------------------

COT_b = 250.0
COT_h = 600.0
COT_a_prime = 40.0  # suy từ e=550mm cho trong tài liệu (xem giải trình bên dưới test)
COT_h0 = COT_h - COT_a_prime  # 560mm
COT_N = 1514.38
COT_M = 417.74


def test_cot22_do_lech_tam_ngau_nhien_va_e0():
    # ea = max(h/600; hc/30; 10) = 20mm; e0 = max(M/N; ea) = 275,85mm — mục 10.4.
    ea = uon_nen.tinh_ea(L=COT_h, h=COT_h)
    assert ea == pytest.approx(20.0, abs=1.0)
    e1 = COT_M / COT_N * 1000  # kN·m / kN -> m -> mm
    e0 = uon_nen.tinh_e0(e1, ea, sieu_tinh=True)
    assert e0 == pytest.approx(275.85, rel=0.01)


def test_cot22_he_so_uon_doc_eta():
    # phiL=1,42; delta_e=0,46; kb=0,139; eta=1,05 — mục 10.4.
    e0 = 275.85
    phi_l = uon_nen.tinh_phi_l(M_L1=0.42, M_L=1.0)  # phi_l = 1 + ML1/ML = 1,42
    assert phi_l == pytest.approx(1.42, abs=0.01)
    delta_e = uon_nen.tinh_delta_e(e0, COT_h)
    assert delta_e == pytest.approx(0.46, abs=0.01)
    kb = uon_nen.tinh_kb(phi_l, delta_e)
    assert kb == pytest.approx(0.139, abs=0.002)

    # D=46828 kNm² (cho sẵn), N=1514,38kN -> Ncr, eta — kiểm tra công thức eta
    # tự nhất quán (không phụ thuộc cách tính D, vì D lấy thẳng từ tài liệu).
    D = 46_828.0  # kNm² — lấy thẳng từ mục 10.4 (không tính lại I, Is ở đây).
    L0 = COT_h / 1000 * 6.07  # l0/h = 6,07 -> l0 (m)
    Ncr = uon_nen.tinh_Ncr(D, L0)
    eta = uon_nen.tinh_eta(COT_N, Ncr)
    assert eta == pytest.approx(1.05, abs=0.02)


def test_cot22_e_va_nhanh_lech_tam():
    # e = eta*e0 + (h0-a')/2 = 550mm — mục 10.4.
    e = uon_nen.tinh_e(e0=275.85, eta=1.05, h0=COT_h0, a_prime=COT_a_prime)
    assert e == pytest.approx(550.0, rel=0.02)

    # Thử lệch tâm lớn: x = N/(Rb*b) = 356mm (As, A's cùng nhóm cùng giá trị
    # nên các số hạng RsAs, RscA's triệt tiêu nhau trong công thức 2.5) — mục 10.4.
    x_lon = uon_nen.thu_lech_tam_lon(
        N=COT_N, Rs=THEP_DOC.Rs, As=1000.0, Rsc=THEP_DOC.Rsc, As_prime=1000.0,
        Rb=BE_TONG.Rb, b=COT_b,
    )
    assert x_lon == pytest.approx(356.0, rel=0.01)

    # x_lon > xiR*h0 = 276mm -> chuyển lệch tâm bé — mục 10.4, mục 10.6 nguyên tắc 3.
    xiR_h0 = XI_R * COT_h0
    assert xiR_h0 == pytest.approx(276.0, abs=1.0)
    assert x_lon > xiR_h0


def test_cot22_verify_thep_da_chon_2phi25_1phi22():
    """Bài test chính: xác nhận thép CUỐI CÙNG sách chọn (2ϕ25+1ϕ22 mỗi phía,
    As=A's=1362mm²) thoả Ne ≤ Mu theo đúng công thức lệch tâm bé mục 2.5 —
    đúng công dụng "tự kiểm tra chéo" mà mục 2 công bố."""
    As = vat_lieu.dien_tich_nhieu_thanh(25, 2) + vat_lieu.dien_tich_nhieu_thanh(22, 1)
    assert As == pytest.approx(1361.9, abs=0.1)

    e = 550.0
    x = uon_nen.thu_lech_tam_be(
        N=COT_N, Rs=THEP_DOC.Rs, As=As, Rsc=THEP_DOC.Rsc, As_prime=As,
        Rb=BE_TONG.Rb, b=COT_b, h0=COT_h0, xiR=XI_R,
    )
    assert XI_R * COT_h0 < x < COT_h0  # nghiệm phải nằm trong miền lệch tâm bé hợp lệ

    Mu = uon_nen.tinh_Mu_cot(BE_TONG.Rb, COT_b, x, COT_h0, THEP_DOC.Rsc, As, COT_a_prime)
    Ne = COT_N * e / 1000
    assert Mu >= Ne  # điều kiện an toàn Ne <= Mu phải thoả

    ket_qua = verify.kiem_tra_tong_hop_cot(
        verify.DauVaoVerifyCot(
            As_thuc=As, b=COT_b, h0=COT_h0, do_manh_L0_h=6.07,
            N=COT_N, e=e, Rb=BE_TONG.Rb, Rsc=THEP_DOC.Rsc, x=x, a_prime=COT_a_prime,
        )
    )
    assert ket_qua.dat, ket_qua.vi_pham


def test_cot22_giai_dong_thoi_lech_tam_be_hop_le():
    """Bộ giải đồng thời (bisection) phải hội tụ và tự nhất quán — không kỳ
    vọng khớp tuyệt đối x=326mm/As=1250mm² của sách vì sách dùng phương pháp
    khác ("công thức thực nghiệm bậc 2") không có đủ công thức trong tài liệu
    để cài lại (xem docstring đầu file)."""
    x, As = uon_nen.thiet_ke_cot_doi_xung_lech_tam_be(
        N=COT_N, e=550.0, Rb=BE_TONG.Rb, b=COT_b, h0=COT_h0, a_prime=COT_a_prime,
        Rs=THEP_DOC.Rs, Rsc=THEP_DOC.Rsc, xiR=XI_R,
    )
    assert XI_R * COT_h0 < x < COT_h0
    assert As > 0
    # Sai số lớn hơn giữa 2 phương pháp là dự kiến — chỉ kiểm tra cùng bậc độ lớn.
    assert x == pytest.approx(326.0, rel=0.15)
    assert As == pytest.approx(1250.0, rel=0.25)


# ---------------------------------------------------------------------------
# DẦM 40-41, tầng 1 (250×700mm, nhịp CB) — mục 10.5
# h0 = 643,53mm suy ngược từ ξ=0,31 cho sẵn trong tài liệu ứng với As=1954mm²
# (tài liệu không nêu trực tiếp a/h0 của dầm này) — cùng h0 này tái lập khớp
# cả Qb,min≈92,7kN, Mu nhịp chữ T≈315,5kNm và cốt treo ΣAsw≈69mm², nên đây là
# giá trị suy ngược nhất quán, không phải số tự đặt tuỳ tiện.
# ---------------------------------------------------------------------------

DAM_b = 250.0
DAM_h = 700.0
DAM_h0 = 643.53


def test_dam_goi_C_as_yeu_cau_va_xi():
    # αm=0,262<αR=0,371 -> ξ=0,31 -> As=1954mm² (μ=1,21%) — mục 10.5.
    As_yc = 1954.0
    ket_qua = uon_nen.tinh_Mu_dam_chu_nhat(
        Rb=BE_TONG.Rb, b=DAM_b, h0=DAM_h0, Rs=THEP_DOC.Rs, As=As_yc, xiR=XI_R
    )
    xi = ket_qua.x / DAM_h0
    assert xi == pytest.approx(0.31, abs=0.01)
    assert ket_qua.dieu_kien_deo_thoa  # xi < xiR=0,493, đúng "thoả điều kiện dẻo"
    assert ket_qua.Mu == pytest.approx(462.0, rel=0.02)  # thiết kế theo gối C (462kNm)

    mu = 100 * As_yc / (DAM_b * DAM_h0)
    assert mu == pytest.approx(1.21, abs=0.02)


def test_dam_goi_thep_da_chon_2phi25_3phi22_du_kha_nang():
    # Thép chọn: 2ϕ25+3ϕ22 (2122mm²), 2 hàng — mục 10.5.
    As_thuc = vat_lieu.dien_tich_nhieu_thanh(25, 2) + vat_lieu.dien_tich_nhieu_thanh(22, 3)
    assert As_thuc == pytest.approx(2122.1, abs=0.5)

    ket_qua = uon_nen.tinh_Mu_dam_chu_nhat(
        Rb=BE_TONG.Rb, b=DAM_b, h0=DAM_h0, Rs=THEP_DOC.Rs, As=As_thuc, xiR=XI_R
    )
    assert ket_qua.Mu >= 462.0  # phải đủ khả năng chịu mô men thiết kế


def test_dam_nhip_chu_T_truc_qua_canh_va_Mu():
    # hf'=100mm, bf'=2450mm (mỗi bên (2450-250)/2=1100mm). Mmax=315,47kNm.
    # Chọn 3ϕ22 (1140mm²) — mục 10.5.
    As_thuc = vat_lieu.dien_tich_nhieu_thanh(22, 3)
    assert As_thuc == pytest.approx(1140.3, abs=0.1)

    bf_prime = 2450.0
    hf_prime = 100.0
    # Kiểm tra trục trung hoà qua cánh: RsAs <= Rb*bf'*hf' — mục 2.4.
    assert THEP_DOC.Rs * As_thuc <= BE_TONG.Rb * bf_prime * hf_prime

    ket_qua = uon_nen.tinh_Mu_dam_chu_T(
        Rb=BE_TONG.Rb, b=DAM_b, b_f_prime=bf_prime, h_f_prime=hf_prime, h0=DAM_h0,
        Rs=THEP_DOC.Rs, As=As_thuc, xiR=XI_R,
    )
    assert ket_qua.Mu == pytest.approx(315.47, rel=0.02)


def test_dam_qb_min_gan_khop_muc_10_5():
    # Qb,min = 0,5*Rbt*b*h0 ≈ 92,7kN — mục 10.5 (công thức đơn giản hoá mục 3.2).
    Qb1 = cot_dai.tinh_Qb1(BE_TONG.Rbt, DAM_b, DAM_h0)
    assert Qb1 == pytest.approx(92.7, rel=0.02)


def test_dam_cot_treo_giat_dut():
    # F=28,035kN, hs=375mm -> ΣAsw≥69,03mm² — mục 10.5.
    ket_qua = cot_dai.tinh_cot_treo(
        F=28.035, h=DAM_h, hs=375.0, h0=DAM_h0, Rsw=THEP_DAI.Rsw, Asw_1_dai=2 * vat_lieu.dien_tich_1_thanh(8)
    )
    assert ket_qua.tong_Asw_yeu_cau == pytest.approx(69.03, rel=0.03)
