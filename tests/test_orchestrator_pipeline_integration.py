"""Test src/orchestrator/pipeline.py.

`chay_toan_bo_khung()` (hàm điều phối cấp cao) tự nó gọi TUẦN TỰ 4 phiên LLM
riêng (Input Adapter → Rule Engine × N phần tử → (Drawing+Verification) × M
mặt cắt → Drawing+Verification lần cuối) VÀ mở AutoCAD COM thật ngay từ đầu
(`backend_com.ket_noi_autocad()`) — dựng kịch bản FakeChatProvider chính xác
cho TOÀN BỘ chuỗi đó, cộng với việc cần máy có AutoCAD mở sẵn, không phù hợp
làm 1 unit test tự động chạy mọi nơi. Việc đó thuộc về
`scripts/chay_pipeline_day_du.py` (script canonical, người dùng tự chạy trên
máy có AutoCAD — xem docs/HUONG_DAN_CHAY.md).

File này tập trung test các HÀM THUẦN không đụng LLM/COM bên trong
pipeline.py — nơi lỗi thật dễ xảy ra nhất (ghép JSON sai trường, gán nhầm
tên vị trí, gộp nhãn sai...), test được đầy đủ và nhanh mà không cần AutoCAD.
"""

from __future__ import annotations

from src.orchestrator import pipeline
from src.orchestrator.shared.hop_dong_du_lieu import (
    BoDuLieuKhungChuanHoa,
    KetQuaPhanTu,
    KetQuaViTriDaThietKe,
    PhanTuChuanHoa,
    PhuongAnThepPhanTu,
    ViTriChuanHoa,
)


def test_tinh_y_mat_cat_an_toan_dat_han_duoi_vung_da_ve():
    """Hồi quy — LỖI THẬT đã gặp khi chạy thật: mặt cắt luôn vẽ ở
    PhienCAD.y_mat_cat mặc định 0.0, TRÙNG đúng vùng y=0 (cao độ Mong) của
    mặt đứng khung — 32 mặt cắt chồng đè lên góc dưới-trái mặt đứng khung,
    hiện thành 1 khối đặc màu đen khi xuất PDF (không phải "bị nén nhỏ do
    chung tỷ lệ" như chẩn đoán ban đầu). Khoá lại: y mới phải THẤP HƠN hẳn
    min_y của vùng đã vẽ (có khoảng cách an toàn), không chỉ bằng/gần nó."""
    hop = (-500.0, -1600.0, 11200.0, 15000.0)  # (min_x, min_y, max_x, max_y) điển hình của 1 mặt đứng khung
    y = pipeline._tinh_y_mat_cat_an_toan(hop, khoang_cach_an_toan=2000.0)
    assert y == -1600.0 - 2000.0
    assert y < hop[1]  # thấp hơn hẳn min_y đã vẽ, không trùng/gần


def test_tinh_y_mat_cat_an_toan_tra_none_khi_modelspace_rong():
    assert pipeline._tinh_y_mat_cat_an_toan(None) is None


def test_chieu_dai_co_neo_noi_cot_cong_1_lan_L_lap():
    """Hồi quy — LỖI THẬT đã gặp: `tinh_neo_noi` ĐÃ tính đúng L_an/L_lap
    (mục 6 RULES_TCVN5574.md), Rule Engine Agent ĐÃ gọi tool này và lưu kết
    quả vào `KetQuaViTriDaThietKe.neo_noi`, nhưng chiều dài dùng cho bảng
    thống kê/mặt đứng khung trước đây lấy THẲNG `goc.chieu_dai` (thuần hình
    học), bỏ qua hoàn toàn kết quả đã tính — xác nhận qua đối chiếu bản vẽ
    mẫu: cột tầng cao 3200mm thật nhưng bản mẫu ghi L=4700mm (dài hơn ~1 đoạn
    nối chồng) vì thép kéo dài qua sàn chờm lên đoạn cột tầng trên."""
    vi_tri = [
        KetQuaViTriDaThietKe(vi_tri="dai_dien", thep_doc={}, neo_noi={"L_an": 500.0, "L_lap": 1500.0}, dat=True),
    ]
    assert pipeline._chieu_dai_co_neo_noi(3200.0, "cot", vi_tri) == 3200.0 + 1500.0


def test_chieu_dai_co_neo_noi_dam_cong_2_lan_L_an_lon_nhat():
    vi_tri = [
        KetQuaViTriDaThietKe(vi_tri="goi_trai", thep_doc={}, neo_noi={"L_an": 400.0}, dat=True),
        KetQuaViTriDaThietKe(vi_tri="giua_nhip", thep_doc={}, neo_noi={}, dat=True),
        KetQuaViTriDaThietKe(vi_tri="goi_phai", thep_doc={}, neo_noi={"L_an": 600.0}, dat=True),
    ]
    assert pipeline._chieu_dai_co_neo_noi(5600.0, "dam", vi_tri) == 5600.0 + 2 * 600.0


def test_chieu_dai_co_neo_noi_giu_nguyen_khi_thieu_du_lieu_neo_noi():
    """Agent chưa gọi tinh_neo_noi (neo_noi rỗng) -> KHÔNG được tự bịa, giữ
    nguyên chieu_dai gốc thay vì cộng thêm giá trị không có thật."""
    vi_tri = [KetQuaViTriDaThietKe(vi_tri="dai_dien", thep_doc={}, neo_noi={}, dat=True)]
    assert pipeline._chieu_dai_co_neo_noi(3200.0, "cot", vi_tri) == 3200.0
    assert pipeline._chieu_dai_co_neo_noi(3200.0, "cot", []) == 3200.0


def test_mo_ta_yeu_cau_rule_engine_liet_ke_du_moi_vi_tri_dung_thu_tu():
    p = PhanTuChuanHoa(
        ten="32", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB400-V",
        vi_tri=[
            ViTriChuanHoa(vi_tri="goi_trai", As_yc=686.0, M=-95.0, N=0, Q=120.0, to_hop="COMB1"),
            ViTriChuanHoa(vi_tri="giua_nhip", As_yc=473.0, M=60.0, N=0, Q=80.0, to_hop="COMB2"),
            ViTriChuanHoa(vi_tri="goi_phai", As_yc=654.0, M=-90.0, N=0, Q=118.0, to_hop="COMB1"),
        ],
    )
    mo_ta = pipeline._mo_ta_yeu_cau_rule_engine("khung_5", p)
    # Cả 3 vị trí phải xuất hiện, ĐÚNG THỨ TỰ (Rule Engine Agent xử lý tuần
    # tự theo thứ tự trong mô tả — pipeline.py sau đó gán tên vị trí thật
    # theo đúng thứ tự này, nên thứ tự sai ở đây sẽ làm SAI TÊN vị trí).
    vi_tri_trai = mo_ta.find("goi_trai")
    vi_tri_giua = mo_ta.find("giua_nhip")
    vi_tri_phai = mo_ta.find("goi_phai")
    assert -1 not in (vi_tri_trai, vi_tri_giua, vi_tri_phai)
    assert vi_tri_trai < vi_tri_giua < vi_tri_phai
    assert "686.0" in mo_ta and "B25" in mo_ta and "CB400-V" in mo_ta


def test_gan_ten_vi_tri_that_theo_dung_thu_tu():
    # Mô phỏng đúng việc _chay_buoc_rule_engine làm sau khi trich_phuong_an_thep:
    # rule_engine_agent chỉ biết THỨ TỰ ("vi_tri_1", "vi_tri_2"...), pipeline.py
    # phải gán lại TÊN THẬT theo đúng danh sách p.vi_tri.
    p_vi_tri = [
        ViTriChuanHoa(vi_tri="goi_trai"), ViTriChuanHoa(vi_tri="giua_nhip"), ViTriChuanHoa(vi_tri="goi_phai"),
    ]
    phuong_an = PhuongAnThepPhanTu(
        ten_phan_tu="32", loai="dam", b=220, h=500,
        vi_tri=[
            KetQuaViTriDaThietKe(vi_tri="vi_tri_1", thep_doc={}, dat=True),
            KetQuaViTriDaThietKe(vi_tri="vi_tri_2", thep_doc={}, dat=True),
            KetQuaViTriDaThietKe(vi_tri="vi_tri_3", thep_doc={}, dat=True),
        ],
    )
    for i, vt in enumerate(phuong_an.vi_tri):
        if i < len(p_vi_tri):
            vt.vi_tri = p_vi_tri[i].vi_tri
    assert [vt.vi_tri for vt in phuong_an.vi_tri] == ["goi_trai", "giua_nhip", "goi_phai"]


def test_mo_ta_yeu_cau_ve_mat_cat_dam_dat_dung_thep_tren_duoi_theo_vi_tri():
    p = PhanTuChuanHoa(ten="32", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB400-V")
    thanh = [{"duong_kinh": 18, "so_luong": 2}, {"duong_kinh": 16, "so_luong": 1}]

    vt_goi = KetQuaViTriDaThietKe(vi_tri="goi_trai", thep_doc={"thanh": thanh, "As_thuc": 710.6, "mo_ta": "2Ø18+1Ø16"})
    _, du_lieu_goi = pipeline._mo_ta_yeu_cau_ve_mat_cat(p, vt_goi, cover=25.0, duong_kinh_dai=8.0)
    assert du_lieu_goi["thanh_tren"] == [18, 18, 16]  # lặp lại từng thanh, KHÔNG phải số lượng
    assert du_lieu_goi["thanh_duoi"] == []

    vt_nhip = KetQuaViTriDaThietKe(vi_tri="giua_nhip", thep_doc={"thanh": thanh, "As_thuc": 710.6, "mo_ta": "2Ø18+1Ø16"})
    _, du_lieu_nhip = pipeline._mo_ta_yeu_cau_ve_mat_cat(p, vt_nhip, cover=25.0, duong_kinh_dai=8.0)
    assert du_lieu_nhip["thanh_duoi"] == [18, 18, 16]
    assert du_lieu_nhip["thanh_tren"] == []


def test_mo_ta_yeu_cau_ve_mat_cat_cot_dung_thang_tu_ket_qua_chon_thep():
    p = PhanTuChuanHoa(ten="C1", loai="cot", b=250, h=600, mac_be_tong="B25", nhom_thep_doc="CB400-V")
    vt = KetQuaViTriDaThietKe(
        vi_tri="dai_dien",
        thep_doc={"duong_kinh": 20, "so_thanh_canh_b": 3, "so_thanh_canh_h": 4, "tong_so_thanh": 10, "As_thuc_moi_phia": 942, "mo_ta": "..."},
    )
    _, du_lieu = pipeline._mo_ta_yeu_cau_ve_mat_cat(p, vt, cover=40.0, duong_kinh_dai=8.0)
    assert du_lieu["so_thanh_canh_b"] == 3
    assert du_lieu["so_thanh_canh_h"] == 4
    assert du_lieu["duong_kinh_canh_b"] == du_lieu["duong_kinh_canh_h"] == 20


def test_du_lieu_lap_rap_chi_gom_phan_tu_da_dat_khong_gom_leo_thang():
    bo_du_lieu = BoDuLieuKhungChuanHoa(
        phan_tu=[
            PhanTuChuanHoa(ten="32", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB400-V", truc="A-B", tang="tang3",
                           vi_tri=[ViTriChuanHoa(vi_tri="goi_trai", As_yc=686.0)]),
            PhanTuChuanHoa(ten="33", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB400-V", truc="B-C", tang="tang3",
                           vi_tri=[ViTriChuanHoa(vi_tri="goi_trai", As_yc=400.0)]),
        ],
        toa_do_truc={"A": 0.0, "B": 5600.0, "C": 7100.0}, cao_do_moc={"tang3": 3200.0},
    )
    ket_qua_phan_tu = [
        KetQuaPhanTu(
            ten_phan_tu="32", loai="dam", trang_thai="dat", rule_engine_dat=True,
            phuong_an_thep=PhuongAnThepPhanTu(
                ten_phan_tu="32", loai="dam", b=220, h=500,
                vi_tri=[KetQuaViTriDaThietKe(vi_tri="goi_trai", thep_doc={"mo_ta": "2Ø18", "thanh": [{"duong_kinh": 18, "so_luong": 2}]}, dat=True)],
            ),
        ),
        # rule_engine_dat=False (mặc định) — KHÔNG được xuất hiện trong kết
        # quả, dù trang_thai đặt "leo_thang" hay bất kỳ giá trị nào khác:
        # _du_lieu_lap_rap lọc theo rule_engine_dat (được lắp ráp SỚM, trước
        # khi mặt cắt vẽ xong nên trang_thai lúc đó chưa thể là "dat" đầy đủ).
        KetQuaPhanTu(ten_phan_tu="33", loai="dam", trang_thai="leo_thang"),
    ]

    du_lieu = pipeline._du_lieu_lap_rap(bo_du_lieu, ket_qua_phan_tu)
    ten_cac_phan_tu = [p["ten"] for p in du_lieu["phan_tu"]]
    assert ten_cac_phan_tu == ["32"]
    assert du_lieu["toa_do_truc"] == {"A": 0.0, "B": 5600.0, "C": 7100.0}
    assert du_lieu["phan_tu"][0]["vi_tri"][0]["mo_ta_thep"] == "2Ø18"
    assert du_lieu["phan_tu"][0]["vi_tri"][0]["As_yc"] == 686.0  # ghép lại đúng As_yc gốc theo tên vị trí
