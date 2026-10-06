"""Test các hàm THUẦN (không đụng COM) trong src/orchestrator/agents/
drawing_agent.py — đặc biệt `_ky_hieu_thep_theo_vi_tri` (hệ số hiệu vòng
tròn, thay cho `_mo_ta_thep_gop` ghi chữ dài cũ — KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md
mục 2.2) và `_xay_dong_thong_ke` (bảng thống kê 8 cột, mục 3.9), cả 2 giờ
dùng CHUNG `SoDangKySoHieu`. Phần đụng COM thật (ve_mat_cat/lap_rap_mat_dung_khung/
xuat_ban_ve gọi backend_com) thuộc phạm vi scripts/smoke_test_com.py và
scripts/chay_pipeline_day_du.py (người dùng tự chạy trên máy có AutoCAD)."""

from __future__ import annotations

from src.drawing.so_hieu_thanh import SoDangKySoHieu
from src.orchestrator.agents import drawing_agent as da


def test_he_thong_prompt_nap_du_cam_nang_ve_ky_thuat():
    """Hồi quy — người dùng yêu cầu tường minh "viết code để agent đọc được
    tài liệu này" (docs/agents/huongdanvebanve/SKILL_VE_KY_THUAT_BTCT.md).
    Khoá lại: HE_THONG_PROMPT phải chứa nội dung cẩm nang (không chỉ trích
    dẫn đường dẫn), và không còn cú pháp ảnh markdown thô (agent nhận văn bản
    thuần, không xem được ảnh img/*.png)."""
    assert "Phần E.4" in da.HE_THONG_PROMPT  # 1 phần đặc trưng của tài liệu, không có trong prompt gốc
    assert "Bảng thống kê cốt thép (8 cột" in da.HE_THONG_PROMPT
    assert "![" not in da.HE_THONG_PROMPT  # cú pháp ảnh markdown đã bị thay bằng chú thích
    assert "hình minh hoạ" in da.HE_THONG_PROMPT


def test_ky_hieu_thep_1_vi_tri_1_duong_kinh():
    # Cột chỉ có 1 vị trí "dai_dien", 1 loại thanh -> ra đúng 1 KyHieuThep.
    ket_qua = da._ky_hieu_thep_theo_vi_tri(
        [{"vi_tri": "dai_dien", "thanh": [{"duong_kinh": 25, "so_luong": 8}]}], chieu_dai=3200.0,
        so_dang_ky=SoDangKySoHieu(),
    )
    assert len(ket_qua) == 1
    assert ket_qua[0].so_hieu == 1
    assert ket_qua[0].so_luong_duong_kinh == "8Ø25"
    assert ket_qua[0].chieu_dai == "L=3200"
    assert ket_qua[0].vi_tri_tren_cau_kien == "dai_dien"


def test_ky_hieu_thep_3_vi_tri_khong_ghi_de_giu_du_ca_3():
    # Hồi quy cho lỗi thật đã biết (script cũ GÁN ĐÈ dict, chỉ giữ vị trí
    # cuối) — ở đây phải giữ ĐỦ CẢ 3 vị trí, mỗi vị trí 1 KyHieuThep riêng.
    vi_tri = [
        {"vi_tri": "goi_trai", "thanh": [{"duong_kinh": 18, "so_luong": 2}]},
        {"vi_tri": "giua_nhip", "thanh": [{"duong_kinh": 16, "so_luong": 3}]},
        {"vi_tri": "goi_phai", "thanh": [{"duong_kinh": 18, "so_luong": 2}]},
    ]
    ket_qua = da._ky_hieu_thep_theo_vi_tri(vi_tri, chieu_dai=5600.0, so_dang_ky=SoDangKySoHieu())
    vi_tri_co_mat = {kh.vi_tri_tren_cau_kien for kh in ket_qua}
    assert vi_tri_co_mat == {"goi_trai", "giua_nhip", "goi_phai"}
    # goi_trai và goi_phai CÙNG (duong_kinh=18, chieu_dai=5600) -> CÙNG 1 số hiệu.
    so_hieu_goi_trai = next(kh.so_hieu for kh in ket_qua if kh.vi_tri_tren_cau_kien == "goi_trai")
    so_hieu_goi_phai = next(kh.so_hieu for kh in ket_qua if kh.vi_tri_tren_cau_kien == "goi_phai")
    assert so_hieu_goi_trai == so_hieu_goi_phai


def test_ky_hieu_thep_2_duong_kinh_cung_vi_tri_ra_2_ky_hieu_rieng():
    # "1Ø20+1Ø22" tại 1 vị trí -> 2 KyHieuThep riêng (KHÔNG gộp 1 ký hiệu
    # cho cả tổ hợp) — đúng mục 2.2 "1 loại thanh = 1 số hiệu".
    ket_qua = da._ky_hieu_thep_theo_vi_tri(
        [{"vi_tri": "goi_trai", "thanh": [{"duong_kinh": 20, "so_luong": 1}, {"duong_kinh": 22, "so_luong": 1}]}],
        chieu_dai=5600.0, so_dang_ky=SoDangKySoHieu(),
    )
    assert len(ket_qua) == 2
    assert {kh.so_hieu for kh in ket_qua} == {1, 2}


def test_phan_tu_khung_tu_dict_giu_dung_truc_tang_chieu_dai():
    p = da._phan_tu_khung_tu_dict(
        {"ten": "32", "loai": "dam", "b": 220, "h": 500, "truc": "A-B", "tang": "tang3", "chieu_dai": 5600.0,
         "mac_be_tong": "B25", "nhom_thep_doc": "CB400-V", "vi_tri": [{"vi_tri": "goi_trai"}]}
    )
    assert p.ten == "32"
    assert p.truc == "A-B" and p.tang == "tang3"
    assert p.tiet_dien.b == 220 and p.tiet_dien.h == 500
    assert len(p.du_lieu_vi_tri) == 1


def test_xay_dung_thong_ke_bo_qua_phan_tu_thieu_chieu_dai():
    phan_tu = [
        {
            "ten": "32", "chieu_dai": 5600.0,
            "vi_tri": [{"vi_tri": "goi_trai", "thanh": [{"duong_kinh": 18, "so_luong": 2}, {"duong_kinh": 16, "so_luong": 1}]}],
        },
        {"ten": "33", "chieu_dai": None, "vi_tri": [{"vi_tri": "goi_trai", "thanh": [{"duong_kinh": 16, "so_luong": 2}]}]},
    ]
    dong = da._xay_dong_thong_ke(phan_tu, SoDangKySoHieu())
    # Phần tử "33" thiếu chieu_dai -> KHÔNG được xuất hiện (không tự bịa chiều dài).
    assert all(d.ten_cau_kien != "33" for d in dong)
    ten_va_duong_kinh = {(d.ten_cau_kien, d.duong_kinh) for d in dong}
    assert ("32", 18) in ten_va_duong_kinh and ("32", 16) in ten_va_duong_kinh


def test_xay_dung_thong_ke_gop_dung_so_luong_theo_duong_kinh():
    phan_tu = [
        {
            "ten": "32", "chieu_dai": 5600.0,
            "vi_tri": [
                {"vi_tri": "goi_trai", "thanh": [{"duong_kinh": 18, "so_luong": 2}]},
                {"vi_tri": "goi_phai", "thanh": [{"duong_kinh": 18, "so_luong": 3}]},
            ],
        },
    ]
    dong = da._xay_dong_thong_ke(phan_tu, SoDangKySoHieu())
    assert len(dong) == 1  # cùng đường kính 18, gộp thành 1 dòng
    assert dong[0].so_luong == 5  # 2 + 3


def test_so_dang_ky_dung_chung_giua_bang_thong_ke_va_ky_hieu_khac_cau_kien():
    # 2 cấu kiện KHÁC nhau, CÙNG (đường kính=16, chiều dài=3200) -> phải nhận
    # ĐÚNG 1 số hiệu giống nhau ở CẢ bảng thống kê LẪN ký hiệu vẽ trên hình
    # (mục 2.2 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md — xác nhận qua bản mẫu thật,
    # số hiệu "5" (4Ø16) lặp lại ở nhiều đoạn cột khác tầng).
    phan_tu = [
        {"ten": "1", "chieu_dai": 3200.0, "vi_tri": [{"vi_tri": "dai_dien", "thanh": [{"duong_kinh": 16, "so_luong": 4}]}]},
        {"ten": "14", "chieu_dai": 3200.0, "vi_tri": [{"vi_tri": "dai_dien", "thanh": [{"duong_kinh": 16, "so_luong": 4}]}]},
    ]
    so_dang_ky = SoDangKySoHieu()
    dong = da._xay_dong_thong_ke(phan_tu, so_dang_ky)
    assert len(dong) == 2  # 2 dòng riêng (1 cho mỗi cấu kiện) nhưng...
    assert dong[0].so_hieu_thanh == dong[1].so_hieu_thanh == "1"  # ...CÙNG 1 số hiệu

    ky_hieu_1 = da._ky_hieu_thep_theo_vi_tri(phan_tu[0]["vi_tri"], phan_tu[0]["chieu_dai"], so_dang_ky)
    ky_hieu_14 = da._ky_hieu_thep_theo_vi_tri(phan_tu[1]["vi_tri"], phan_tu[1]["chieu_dai"], so_dang_ky)
    assert ky_hieu_1[0].so_hieu == ky_hieu_14[0].so_hieu == 1  # khớp đúng số hiệu bảng thống kê đã dùng
    assert dong[0].so_hieu_thanh == "1"  # tự đánh số tăng dần, tất định
