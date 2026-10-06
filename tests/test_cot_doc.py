"""Test lựa chọn cốt thép dọc — RULES_TCVN5574.md mục 4."""

import pytest

from src.rule_engine import cot_doc


def test_mu_min_do_manh_thap():
    assert cot_doc.tra_mu_min(do_manh=5.0) == pytest.approx(0.10)
    assert cot_doc.tra_mu_min(do_manh=3.0) == pytest.approx(0.10)


def test_mu_min_do_manh_cao():
    assert cot_doc.tra_mu_min(do_manh=25.0) == pytest.approx(0.25)
    assert cot_doc.tra_mu_min(do_manh=30.0) == pytest.approx(0.25)


def test_mu_min_noi_suy_giua():
    # Giữa 5 và 25, tuyến tính: tại 15 -> giữa 0,10 và 0,25 -> 0,175.
    assert cot_doc.tra_mu_min(do_manh=15.0) == pytest.approx(0.175)


def test_mu_min_gap_doi_keo_dung_tam():
    assert cot_doc.tra_mu_min(do_manh=5.0, bo_tri_deu_chu_vi_hoac_keo_dung_tam=True) == pytest.approx(0.20)


def test_canh_bao_vuot_mu_max():
    # As=8000mm², b=250, h0=560 -> mu=5,71% > 3%.
    assert cot_doc.canh_bao_vuot_mu_max(As=8000, b=250, h0=560)
    assert not cot_doc.canh_bao_vuot_mu_max(As=1000, b=250, h0=560)


def test_so_thanh_toi_da_1_lop():
    # b=250mm, cover=25mm, đai 8mm, thép dọc 18mm.
    # bề rộng khả dụng = 250 - 2*25 - 2*8 = 184mm; khoảng hở >= max(25,18)=25mm.
    # n*18 + (n-1)*25 <= 184 -> n<=(184+25)/(18+25)=4,86 -> n=4.
    n = cot_doc.so_thanh_toi_da_1_lop(b=250, cover=25, duong_kinh_dai=8, duong_kinh_doc=18)
    assert n == 4


def test_chon_to_hop_thep_doc_don_gian():
    # As_target nhỏ, chỉ cần 1 loại đường kính, dư diện tích ít nhất.
    to_hop = cot_doc.chon_to_hop_thep_doc(
        As_target=600.0, duong_kinh_cho_phep=[12, 14, 16, 18, 20], b=250, cover=25
    )
    assert to_hop.As_thuc >= 600.0
    assert to_hop.so_loai_duong_kinh in (1, 2)


def test_chon_to_hop_thep_doc_khong_kha_thi():
    with pytest.raises(ValueError):
        cot_doc.chon_to_hop_thep_doc(
            As_target=1_000_000.0, duong_kinh_cho_phep=[12], b=250, cover=25
        )


def test_chon_to_hop_thep_doc_uu_tien_duong_kinh_da_dung():
    """Hồi quy — LỖI THẬT đã gặp: đối chiếu trực tiếp thuyết minh gốc
    inputvanban2.pdf của Khung Trục 5, kỹ sư thật chỉ dùng 2 loại đường kính
    (Ø16, Ø18) cho TOÀN BỘ 12 cột + 8 dầm; hệ thống trước khi có tham số này
    (mỗi lần gọi tự tìm "ít thừa diện tích nhất" độc lập, không nhớ đường
    kính đã dùng ở vị trí/phần tử khác) dùng rải rác 6 loại (Ø12-Ø22), có
    dầm dùng tới 4 loại CHỈ TRONG 1 cấu kiện — vi phạm thẳng mục 4.1 "không
    quá BA loại đường kính/dầm". Khoá lại: khi Ø18 (đã dùng ở vị trí trước)
    ĐỦ để thoả As_target, PHẢI chọn Ø18 dù Ø20 có thể "thừa ít hơn"."""
    # As_target cố ý chọn sao cho Ø20 (2 thanh) thừa diện tích ÍT HƠN Ø18
    # (2 thanh) nếu tìm "tối ưu tuyệt đối" không ràng buộc gì — xác nhận quy
    # tắc ưu tiên THỰC SỰ ghi đè quy tắc "ít thừa nhất" mặc định.
    as_18 = cot_doc.vat_lieu.dien_tich_1_thanh(18) * 2  # 2Ø18
    as_20 = cot_doc.vat_lieu.dien_tich_1_thanh(20) * 2  # 2Ø20
    assert as_20 - as_18 > 0  # Ø20 thừa nhiều hơn Ø18 cho cùng As_target dưới đây
    as_target = as_18 - 1.0  # vừa đủ để 2Ø18 thoả, nhưng 1Ø18 thì không

    to_hop_khong_uu_tien = cot_doc.chon_to_hop_thep_doc(
        As_target=as_target, duong_kinh_cho_phep=[16, 18, 20], b=250, cover=25,
    )
    # Không truyền ưu tiên: thuật toán có thể chọn đường kính khác Ø18 nếu nó
    # "thừa ít hơn" — chỉ xác nhận tiền đề bài test đúng (không phải chủ đích
    # kiểm tra nhánh này).
    assert to_hop_khong_uu_tien.As_thuc >= as_target

    to_hop_uu_tien = cot_doc.chon_to_hop_thep_doc(
        As_target=as_target, duong_kinh_cho_phep=[16, 18, 20], b=250, cover=25,
        duong_kinh_uu_tien=[18],
    )
    assert all(d == 18 for d, _n in to_hop_uu_tien.thanh)
    assert to_hop_uu_tien.As_thuc >= as_target


def test_chon_to_hop_thep_doc_uu_tien_khong_kha_thi_thi_fallback():
    """Ưu tiên Ø12 (không đủ As dù dùng rất nhiều thanh, vượt so_thanh_toi_da)
    — PHẢI tự rơi về tìm kiếm đầy đủ, không được raise ValueError oan."""
    to_hop = cot_doc.chon_to_hop_thep_doc(
        As_target=3000.0, duong_kinh_cho_phep=[12, 25], b=250, cover=25,
        duong_kinh_uu_tien=[12],
    )
    assert to_hop.As_thuc >= 3000.0
    assert 25 in {d for d, _n in to_hop.thanh}


def test_chon_to_hop_thep_chu_vi_cot_du_as_va_khop_hinh_hoc():
    """Hồi quy — lỗi thật phát hiện qua chạy Phase 4: dùng nhầm
    chon_to_hop_thep_doc (logic dầm) cho cột ra tổ hợp không khớp khi vẽ theo
    chu vi. Hàm chuyên cho cột phải cho ra đúng tổng số thanh sẽ được vẽ."""
    to_hop = cot_doc.chon_to_hop_thep_chu_vi_cot(
        As_target_moi_phia=1250.0, b=250, h=600, cover=40, duong_kinh_cho_phep=[16, 18, 20, 22, 25, 28, 32],
    )
    assert to_hop.As_thuc_moi_phia >= 1250.0
    # tổng_so_thanh phải khớp ĐÚNG công thức đếm điểm chu vi đã dùng ở geometry.py
    # (2*canh_b + 2*(canh_h-2)) — không được lệch như lỗi cũ (9 chọn vs 8 vẽ).
    assert to_hop.tong_so_thanh == 2 * to_hop.so_thanh_canh_b + 2 * (to_hop.so_thanh_canh_h - 2)


def test_chon_to_hop_thep_chu_vi_cot_toi_thieu_2_thanh_moi_canh():
    to_hop = cot_doc.chon_to_hop_thep_chu_vi_cot(
        As_target_moi_phia=50.0, b=250, h=600, cover=40, duong_kinh_cho_phep=[12],
    )
    assert to_hop.so_thanh_canh_b >= 2
    assert to_hop.so_thanh_canh_h >= 2


def test_chon_to_hop_thep_chu_vi_cot_khong_kha_thi():
    with pytest.raises(ValueError):
        cot_doc.chon_to_hop_thep_chu_vi_cot(
            As_target_moi_phia=1_000_000.0, b=250, h=600, cover=40, duong_kinh_cho_phep=[12],
        )


def test_chon_to_hop_thep_chu_vi_cot_uu_tien_duong_kinh_da_dung():
    """Cùng lớp lỗi với test_chon_to_hop_thep_doc_uu_tien_duong_kinh_da_dung
    nhưng cho CỘT (bố trí chu vi) — ví dụ thật từ thuyết minh gốc: cột 1/14
    cùng dùng 3Ø18/phía, không phải mỗi cột 1 đường kính khác nhau."""
    to_hop = cot_doc.chon_to_hop_thep_chu_vi_cot(
        As_target_moi_phia=700.0, b=220, h=300, cover=40, duong_kinh_cho_phep=[16, 18, 20, 22],
        duong_kinh_uu_tien=[18],
    )
    assert to_hop.duong_kinh == 18
    assert to_hop.As_thuc_moi_phia >= 700.0


def test_chon_to_hop_thep_chu_vi_cot_uu_tien_khong_kha_thi_thi_fallback():
    """Ưu tiên Ø12 không khả thi về mặt hình học (cần quá nhiều thanh, không
    xếp vừa 1 lớp trong bề rộng 220mm) cho As_target lớn — PHẢI tự rơi về tìm
    kiếm đầy đủ trong duong_kinh_cho_phep, không raise ValueError oan."""
    to_hop = cot_doc.chon_to_hop_thep_chu_vi_cot(
        As_target_moi_phia=1500.0, b=220, h=300, cover=40, duong_kinh_cho_phep=[12, 32],
        duong_kinh_uu_tien=[12],
    )
    assert to_hop.As_thuc_moi_phia >= 1500.0
    assert to_hop.duong_kinh == 32


def test_to_hop_thep_dam_bao_du_dien_tich_gan_book_case():
    # As_tt=1212mm² (mục 10.2, tầng 3, 44-45 gối trái) — chỉ kiểm tra As đủ và
    # ràng buộc hợp lệ, KHÔNG kỳ vọng khớp đúng tổ hợp 5ϕ18 sách chọn (xem
    # ghi chú đầu module cot_doc.py về quy tắc ưu tiên không phải duy nhất).
    to_hop = cot_doc.chon_to_hop_thep_doc(
        As_target=1212.0, duong_kinh_cho_phep=[16, 18, 20, 22, 25], b=250, cover=25
    )
    assert to_hop.As_thuc >= 1212.0
    assert to_hop.so_loai_duong_kinh <= 3


# ---------------------------------------------------------------------------
# CHANGE_REQUESTS.md mục 6 — ràng buộc đường kính thép dọc tối thiểu 12mm.
# Hồi quy cho lỗi thật đã gặp: Rule Engine Agent tự nới duong_kinh_cho_phep
# xuống thấp lúc tự sửa lỗi (tu_kiem_tra không đạt), trước đây không có gì
# chặn nên có thể ra 3Ø8/2Ø10 — nay phải bị LỌC NGAY TẠI NGUỒN, không sinh ra
# ứng viên đường kính < 12mm dù As_target rất nhỏ (chấp nhận báo lỗi "không
# tìm được tổ hợp" thay vì âm thầm trả về đường kính phi thực tế).
# ---------------------------------------------------------------------------


def test_chon_to_hop_thep_doc_khong_dung_duong_kinh_duoi_12mm_du_as_nho():
    to_hop = cot_doc.chon_to_hop_thep_doc(
        As_target=100.0, duong_kinh_cho_phep=[8, 10, 12, 14], b=250, cover=25
    )
    assert min(d for d, _ in to_hop.thanh) >= cot_doc.DUONG_KINH_DOC_TOI_THIEU_MM


def test_chon_to_hop_thep_doc_bao_loi_ro_rang_khi_chi_co_duong_kinh_duoi_12mm():
    # Toàn bộ duong_kinh_cho_phep đều < 12mm -> bị lọc hết -> raise ValueError
    # rõ ràng thay vì âm thầm trả về 1 tổ hợp đường kính nhỏ.
    with pytest.raises(ValueError):
        cot_doc.chon_to_hop_thep_doc(As_target=100.0, duong_kinh_cho_phep=[6, 8, 10], b=250, cover=25)


def test_chon_to_hop_thep_chu_vi_cot_khong_dung_duong_kinh_duoi_12mm():
    to_hop = cot_doc.chon_to_hop_thep_chu_vi_cot(
        As_target_moi_phia=50.0, b=250, h=600, cover=40, duong_kinh_cho_phep=[8, 10, 12, 14],
    )
    assert to_hop.duong_kinh >= cot_doc.DUONG_KINH_DOC_TOI_THIEU_MM
