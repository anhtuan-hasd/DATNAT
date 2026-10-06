"""Test hình học độc lập backend — src/drawing/geometry.py."""

import pytest

from src.drawing import geometry, layers
from src.input_adapter.models import LoaiCauKien


def test_vi_tri_mat_cat_theo_loai():
    assert geometry.xac_dinh_vi_tri_mat_cat_can_ve(LoaiCauKien.COT) == ["dai_dien"]
    assert geometry.xac_dinh_vi_tri_mat_cat_can_ve(LoaiCauKien.DAM) == ["goi_trai", "giua_nhip", "goi_phai"]
    assert geometry.xac_dinh_vi_tri_mat_cat_can_ve(LoaiCauKien.DAM, la_console=True) == ["ngam"]


def test_chia_lop_thep_vua_1_lop():
    lop = geometry.chia_lop_thep([18, 18, 18], b=250, cover=25, duong_kinh_dai=8)
    assert lop == [[18, 18, 18]]


def test_chia_lop_thep_can_2_lop():
    # so_thanh_toi_da_1_lop(250,25,8,18) = 4 (đã kiểm chứng ở test_cot_doc.py)
    lop = geometry.chia_lop_thep([18, 18, 18, 18, 18], b=250, cover=25, duong_kinh_dai=8)
    assert lop == [[18, 18, 18, 18], [18]]


def test_toa_do_1_hang_doi_xung():
    toa_do = geometry.toa_do_1_hang(b=250, cover=25, duong_kinh_dai=8, danh_sach_duong_kinh=[18, 18], y=50)
    assert len(toa_do) == 2
    x0, x1 = toa_do[0][0].x, toa_do[1][0].x
    assert x0 < x1
    # Đối xứng qua tâm b/2.
    assert (x0 + x1) / 2 == pytest.approx(125, abs=1e-6)


def test_ban_kinh_uon_dai():
    # phi8 trơn (co_go=False): duong_kinh_uon_toi_thieu(8, False) = 2,5*8 = 20mm -> bán kính 10mm.
    assert geometry.ban_kinh_uon_dai(8) == pytest.approx(10.0)
    # phi22 trơn, d>=20 -> hệ số 4d -> bán kính 2d = 44mm.
    assert geometry.ban_kinh_uon_dai(22) == pytest.approx(44.0)


def test_duong_bao_chu_nhat_bo_tron_khep_kin_va_dung_ban_kinh():
    doan_thang, cung = geometry.duong_bao_chu_nhat_bo_tron(0, 0, 100, 50, ban_kinh=10, layer="TEST")
    assert len(doan_thang) == 4
    assert len(cung) == 4
    assert all(c.ban_kinh == pytest.approx(10.0) for c in cung)
    # Cạnh dưới đã rút ngắn đúng bán kính ở 2 đầu (từ x=10 đến x=90, không phải 0-100).
    canh_duoi = next(dt for dt in doan_thang if dt.p1.y == 0 and dt.p2.y == 0)
    assert canh_duoi.p1.x == pytest.approx(10.0)
    assert canh_duoi.p2.x == pytest.approx(90.0)


def test_duong_bao_chu_nhat_bo_tron_ban_kinh_qua_lon_tu_dong_gioi_han():
    # bán kính lớn hơn nửa cạnh ngắn -> tự giới hạn lại, không được âm/lỗi hình học.
    doan_thang, cung = geometry.duong_bao_chu_nhat_bo_tron(0, 0, 40, 20, ban_kinh=100, layer="TEST")
    assert all(c.ban_kinh <= 10.0 for c in cung)  # nửa cạnh ngắn nhất (20/2=10)


def test_ve_mat_cat_dam_so_luong_doi_tuong():
    bv = geometry.ve_mat_cat_dam(
        nhan="1-1", b=250, h=700, cover=25, duong_kinh_dai=8,
        thanh_duoi=[18, 18, 18], thanh_tren=[16, 16],
    )
    # Đường bao bê tông (OUTLINE_CUT, góc vuông) + đường bao đai GÓC BO TRÒN
    # (4 đoạn thẳng + 4 cung, mục 6.4 — thanh thép uốn không phải góc vuông sắc).
    assert len(bv.da_giac) == 1
    assert bv.da_giac[0].layer == layers.OUTLINE_CUT.ten
    dai_doan_thang = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_STIRRUP.ten]
    dai_cung = [c for c in bv.cung if c.layer == layers.REBAR_STIRRUP.ten]
    assert len(dai_doan_thang) == 4
    assert len(dai_cung) == 4
    assert len(bv.vong_tron) == 5  # 3 dưới + 2 trên
    assert all(vt.layer == layers.REBAR_MAIN.ten for vt in bv.vong_tron)
    assert len(bv.kich_thuoc) == 2  # b và h


def test_ve_mat_cat_dam_kiem_chung_bang_verify_ir():
    bv = geometry.ve_mat_cat_dam(
        nhan="2-2", b=250, h=700, cover=25, duong_kinh_dai=8, thanh_duoi=[18, 18], thanh_tren=[16, 16],
    )
    from src.drawing import verify_drawing

    assert verify_drawing.kiem_tra_mat_cat_ir(bv, b_ky_vong=250, h_ky_vong=700) == []
    assert verify_drawing.dem_thanh_thep_ir(bv) == 4


def test_toa_do_thep_chu_vi_hcn_dem_dung():
    toa_do = geometry.toa_do_thep_chu_vi_hcn(
        b=250, h=600, cover=25, duong_kinh_dai=8,
        so_thanh_canh_b=3, duong_kinh_canh_b=20,
        so_thanh_canh_h=3, duong_kinh_canh_h=20,
    )
    # 2*3 (cạnh b, trên+dưới) + 2*(3-2) (cạnh h, trừ 2 góc đã tính) = 8.
    assert len(toa_do) == 8


def test_ve_mat_cat_cot():
    bv = geometry.ve_mat_cat_cot(
        nhan="dai_dien", b=250, h=600, cover=25, duong_kinh_dai=8,
        so_thanh_canh_b=2, duong_kinh_canh_b=25,
        so_thanh_canh_h=2, duong_kinh_canh_h=22,
    )
    assert len(bv.vong_tron) == 4  # chỉ 4 góc khi mỗi cạnh 2 thanh
    assert len(bv.da_giac) == 1  # chỉ đường bao bê tông — đai nay là đoạn thẳng+cung bo tròn
    assert len([c for c in bv.cung if c.layer == layers.REBAR_STIRRUP.ten]) == 4


def test_khoi_luong_tren_1m_khop_ban_ve_mau():
    # d=18, dài 4700mm, SL=144 -> tổng dài 676,8m -> 1351,96kG (bảng thống kê
    # thép trong data/samples/BoTriThep_KhungTruc5_mau.pdf).
    dong = geometry.tinh_dong_thong_ke(
        "Dầm 32", "1", "Thẳng", duong_kinh=18, chieu_dai_1_don_vi_mm=4700, so_luong=144
    )
    assert dong.tong_chieu_dai_m == pytest.approx(676.8, abs=0.01)
    assert dong.khoi_luong_kg == pytest.approx(1351.96, rel=0.002)


def test_ve_bang_thong_ke_khong_loi():
    # 8 cột ĐÚNG mục 3.9 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md (không còn 7 cột
    # như bản trước — xem ghi chú docstring DongThongKe).
    dong = [
        geometry.tinh_dong_thong_ke("Dầm 32", "1", "Thẳng", 18, 4700, 144),
        geometry.tinh_dong_thong_ke("Dầm 32", "2", "Có móc", 16, 3700, 192),
    ]
    bv = geometry.ve_bang_thong_ke("BANG_THONG_KE", dong, do_rong_cot=[60, 25, 40, 30, 60, 30, 60, 60])
    assert len(bv.chu) == 8 * 3  # 8 cột x (1 tiêu đề + 2 dòng dữ liệu)


def test_ve_bang_thong_ke_bao_loi_khi_sai_so_luong_cot():
    dong = [geometry.tinh_dong_thong_ke("Dầm 32", "1", "Thẳng", 18, 4700, 144)]
    with pytest.raises(ValueError):
        geometry.ve_bang_thong_ke("BANG_THONG_KE", dong, do_rong_cot=[30, 80, 40])  # thiếu, không đủ 8


def test_ve_khung_ten():
    tt = geometry.ThongTinKhungTen(
        ten_truong="ĐH Kiến Trúc Hà Nội", khoa="Xây dựng", chuyen_nganh="XD DD&CN",
        ten_do_an="Đồ án KCBTCT 2", gvhd="X", svth="Y", de_so="1",
        ngay_nhan="01/01/2026", ngay_hoan_thanh="01/02/2026",
    )
    bv = geometry.ve_khung_ten(rong=300, cao=150, thong_tin=tt)
    assert len(bv.da_giac) == 1
    assert len(bv.chu) == 9


def test_ve_mat_dung_khung_co_du_truc_va_cao_do():
    cac_cot = [geometry.DoanCotVe(x_truc=0, y_duoi=0, y_tren=3200, b=300, nhan="C1")]
    cac_dam = [geometry.DoanDamVe(x_trai=0, x_phai=3200, y_truc=3200, h=500, nhan="D1")]
    bv = geometry.ve_mat_dung_khung(
        ten_truc_dung=["A", "B"], x_truc_dung=[0, 3200],
        ten_cao_do=["MONG", "TANG2"], y_cao_do=[0, 3200],
        cac_cot=cac_cot, cac_dam=cac_dam,
    )
    # 1 cột + 1 dầm (OUTLINE) + 2 tam giác ký hiệu cao độ (layer AXIS — cùng
    # màu cyan với đường mốc cao độ, đúng ảnh chụp bản vẽ CAD thật) — lọc
    # theo layer để không lẫn ký hiệu trang trí.
    cau_kien = [dg for dg in bv.da_giac if dg.layer == layers.OUTLINE.ten]
    assert len(cau_kien) == 2
    tam_giac_cao_do = [dg for dg in bv.da_giac if dg.layer == layers.AXIS.ten]
    assert len(tam_giac_cao_do) == 2
    ten_chu = {c.noi_dung for c in bv.chu}
    assert "A" in ten_chu and "B" in ten_chu
    assert "C1" in ten_chu and "D1" in ten_chu


def test_ve_mat_bang_ket_cau_co_du_truc_cot_dam():
    cac_cot = [
        geometry.ViTriCotMatBang(x_truc=0, y_truc=0, b=250, h=600, nhan="C1"),
        geometry.ViTriCotMatBang(x_truc=3200, y_truc=0, b=250, h=600, nhan="C1"),
    ]
    cac_dam = [geometry.DoanDamMatBang(x1=0, y1=0, x2=3200, y2=0, nhan="K1")]
    bv = geometry.ve_mat_bang_ket_cau(
        ten_mat_bang="MAT BANG TANG 2",
        ten_truc_x=["1", "2"], x_truc=[0, 3200],
        ten_truc_y=["A"], y_truc=[0],
        cac_cot=cac_cot, cac_dam=cac_dam,
    )
    assert len(bv.da_giac) == 2  # 2 cột
    assert len(bv.vong_tron) == 3  # 2 đầu trục "1"/"2" + 1 đầu trục "A"
    ten_chu = [c.noi_dung for c in bv.chu]
    assert ten_chu.count("1") == 1 and ten_chu.count("2") == 1 and ten_chu.count("A") == 1
    assert ten_chu.count("K1") == 1
    assert ten_chu.count("C1") == 2
    assert "MAT BANG TANG 2" in ten_chu


def test_ve_mat_bang_ket_cau_khong_ve_2_net_mep_dam():
    # Ở tỷ lệ mặt bằng, dầm chỉ vẽ 1 đường tim (đoạn thẳng), không phải đa
    # giác 2 mép — khác hẳn mặt cắt ngang chi tiết.
    cac_dam = [geometry.DoanDamMatBang(x1=0, y1=0, x2=3200, y2=0, nhan="K1")]
    bv = geometry.ve_mat_bang_ket_cau(
        ten_mat_bang="TEST", ten_truc_x=["1"], x_truc=[0], ten_truc_y=["A"], y_truc=[0],
        cac_cot=[], cac_dam=cac_dam,
    )
    dam_doan_thang = [dt for dt in bv.doan_thang if dt.layer == layers.OUTLINE.ten]
    assert len(dam_doan_thang) == 1


def test_chieu_iso_khong_suy_bien():
    # 3 điểm không thẳng hàng trong không gian phải chiếu ra 3 điểm không thẳng hàng.
    p0 = geometry.chieu_iso(0, 0, 0)
    p1 = geometry.chieu_iso(100, 0, 0)
    p2 = geometry.chieu_iso(0, 100, 0)
    p3 = geometry.chieu_iso(0, 0, 100)
    dien_tich = abs((p1.x - p0.x) * (p2.y - p0.y) - (p2.x - p0.x) * (p1.y - p0.y))
    assert dien_tich > 0  # p0,p1,p2 không suy biến thành 1 đường thẳng
    assert p3 != p0  # trục z cũng phải tạo ra khác biệt trên mặt phẳng chiếu


def test_ve_chi_tiet_nut_khung_du_thanh_phan():
    ts = geometry.ThongSoChiTietNutKhung(
        nhan="CHI TIET 1", b_cot=250, h_cot=600, chieu_dai_cot_duoi=800, chieu_dai_cot_tren=800,
        b_dam=250, h_dam=700, chieu_dai_dam=1500, so_dai_minh_hoa_cot=3, so_dai_minh_hoa_dam=3,
    )
    bv = geometry.ve_chi_tiet_nut_khung(ts)

    outline = [dt for dt in bv.doan_thang if dt.layer == layers.OUTLINE.ten]
    assert len(outline) == 24  # 12 cạnh khối cột + 12 cạnh khối dầm

    thep_doc = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_MAIN.ten]
    assert len(thep_doc) == 8  # 4 thanh cột + 4 thanh dầm

    dai = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_STIRRUP.ten]
    assert len(dai) == 4 * (ts.so_dai_minh_hoa_cot + ts.so_dai_minh_hoa_dam)  # mỗi vòng đai 4 cạnh

    assert any(c.noi_dung == "CHI TIET 1" for c in bv.chu)


# Trước đây có thêm 1 test ở đây xuất `ve_chi_tiet_nut_khung` ra DXF bằng
# `backend_dxf` (ezdxf) để xác nhận "không lỗi khi vẽ ra file thật" — module
# đó đã bị xoá hẳn khỏi repo (CHANGE_REQUESTS.md mục 2, ezdxf không còn là
# backend nào của đồ án). Việc "vẽ ra file thật không lỗi" cho hình phối cảnh
# nút khung giờ được xác nhận gián tiếp qua `tests/test_agents_drawing.py`
# (đường COM thật, đánh dấu skip khi máy không có AutoCAD) — bài test IR ở
# đây (phía trên) vẫn đủ để xác nhận ĐÚNG HÌNH HỌC (số đoạn thẳng, số đai...)
# mà không cần phụ thuộc bất kỳ backend vẽ nào.
