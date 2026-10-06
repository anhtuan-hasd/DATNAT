"""Test src/orchestrator/khung_ve.py — lắp ráp mặt đứng khung tổng thể từ
PhanTuKhung (truc/tang) + nhãn thép đã chọn."""

from src.drawing.geometry import KyHieuThep
from src.input_adapter.models import LoaiCauKien, PhanTuKhung, TietDien
from src.orchestrator import khung_ve


def _pt_cot(ten: str, truc: str, tang: str, b: float = 220, h: float = 300) -> PhanTuKhung:
    return PhanTuKhung(
        ten=ten, loai=LoaiCauKien.COT, tiet_dien=TietDien(b=b, h=h),
        mac_be_tong="B25", nhom_thep_doc="CB500-V", tang=tang, truc=truc,
    )


def _pt_dam(ten: str, truc: str, tang: str, b: float = 220, h: float = 500) -> PhanTuKhung:
    return PhanTuKhung(
        ten=ten, loai=LoaiCauKien.DAM, tiet_dien=TietDien(b=b, h=h),
        mac_be_tong="B25", nhom_thep_doc="CB500-V", tang=tang, truc=truc,
    )


def test_lap_rap_tra_ve_none_khi_thieu_topology():
    pt = PhanTuKhung(
        ten="1", loai=LoaiCauKien.COT, tiet_dien=TietDien(b=220, h=300),
        mac_be_tong="B25", nhom_thep_doc="CB500-V",
    )  # không có truc/tang
    assert khung_ve.lap_rap_mat_dung_khung([pt]) is None


def test_lap_rap_toa_do_that_khung_truc5():
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_cot("2", "A", "tang2_tang3"),
        _pt_cot("14", "B", "mong_tang2"),
        _pt_dam("32", "A-B", "tang2"),
    ]
    toa_do_truc = {"A": 0.0, "B": 5600.0, "C": 7100.0}
    cao_do_moc = {"mong": -1000.0, "tang2": 3200.0, "tang3": 6400.0}
    ky_hieu = {
        "1": [KyHieuThep(so_hieu=1, so_luong_duong_kinh="3Ø18", chieu_dai="L=4200")],
        "32": [KyHieuThep(so_hieu=2, so_luong_duong_kinh="3Ø18", chieu_dai="L=5600", vi_tri_tren_cau_kien="dai_dien")],
    }

    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, ky_hieu_theo_ten=ky_hieu, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc)
    assert bv is not None

    # 3 trục dọc (AXIS) + 2 mốc ngang (AXIS) = 5 đường tim trục
    duong_tim = [d for d in bv.doan_thang if d.layer == "AXIS" or d.layer == geometry_axis_layer()]
    assert len(duong_tim) >= 5

    # 3 cột (khối OUTLINE hình chữ nhật) + 1 dầm = 4 đa giác OUTLINE — lọc
    # theo layer để không lẫn tam giác ký hiệu cao độ (mục 10.7, layer TEXT).
    cau_kien = [dg for dg in bv.da_giac if dg.layer == geometry_outline_layer()]
    assert len(cau_kien) == 4

    # Cột 1 (trục A, mong->tang2): x_truc=0, hiển thị theo h=300 (không phải
    # b=220). Vị trí y KHÔNG còn đúng mm thật (-1000/3200) — hình học nay vẽ
    # theo toạ độ SCHEMATIC đều nhau (khung_ve._toa_do_deu_giu_thu_tu), bước
    # đều = khoảng cách lớn nhất giữa 2 mốc thật liên tiếp (max(4200, 3200)
    # = 4200) -> mong=0, tang2=4200, tang3=8400 (xem test riêng cho việc ghi
    # NHÃN kích thước vẫn đúng số thật, bên dưới).
    diem_cot1 = cau_kien[0].diem
    xs = [p.x for p in diem_cot1]
    ys = [p.y for p in diem_cot1]
    assert min(xs) == -150 and max(xs) == 150  # b hiển thị = h cột = 300 -> nửa bề rộng 150
    assert min(ys) == 0 and max(ys) == 4200

    # Tên cấu kiện ("1", "32") VÀ ký hiệu số hiệu thật ("3Ø18", "1", "2")
    # phải xuất hiện trên bản vẽ — không còn ghi chữ mô tả dài "1: 3d18" nữa.
    noi_dung_chu = [c.noi_dung for c in bv.chu]
    assert "1" in noi_dung_chu and "32" in noi_dung_chu
    assert "3Ø18" in noi_dung_chu


def test_lap_rap_ve_deu_nhau_bat_ke_nhip_that_khac_nhau():
    """Hồi quy — người dùng phản hồi trực tiếp khi xem bản vẽ vẽ ĐÚNG TỶ LỆ
    THẬT (ảnh chụp bản vẽ, nhịp 5600mm cạnh nhịp 1500mm): "tại sao lại phải
    có đoạn thì to đoạn thì nhỏ... tôi thấy trong bản vẽ người ta vẽ khung
    bằng nhau cơ mà". Xác nhận qua tra cứu: sơ đồ bố trí thép không cần vẽ
    theo đúng tỷ lệ, miễn kích thước vẫn ghi rõ (xem test_lap_rap_ve_du_kich_
    thuoc_nhip_va_tang — nhãn "5600"/"1500" vẫn đúng số thật). Khoá lại: vị
    trí VẼ (x_truc) của 2 trục B/C phải cách đều B/A (schematic), KHÔNG còn tỷ
    lệ 5600:1500 như dữ liệu thật."""
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_cot("14", "B", "mong_tang2"),
        _pt_cot("18", "C", "mong_tang2"),
    ]
    toa_do_truc = {"A": 0.0, "B": 5600.0, "C": 7100.0}  # A-B=5600 (rộng), B-C=1500 (hẹp)
    cao_do_moc = {"mong": -1000.0, "tang2": 3200.0}

    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc)
    assert bv is not None

    from src.drawing import layers

    x_cot = sorted(
        round((min(p.x for p in dg.diem) + max(p.x for p in dg.diem)) / 2)
        for dg in bv.da_giac if dg.layer == layers.OUTLINE.ten
    )
    assert len(x_cot) == 3
    khoang_ab = x_cot[1] - x_cot[0]
    khoang_bc = x_cot[2] - x_cot[1]
    # Thật: khoang_ab=5600, khoang_bc=1500 (tỷ lệ ~3.7:1) — SAU khi vẽ đều,
    # phải bằng nhau tuyệt đối, không còn tỷ lệ chênh lệch đó.
    assert khoang_ab == khoang_bc


def test_lap_rap_ve_du_kich_thuoc_nhip_va_tang():
    """Hồi quy — lỗi thật phát hiện qua xem trực tiếp bản vẽ: bản đầu tiên
    của `ve_mat_dung_khung` KHÔNG vẽ kích thước nhịp/chiều cao tầng nào cả
    (chỉ có đường tim trục + tên trục/cao độ) — trông như sơ đồ trống, thiếu
    hẳn thông tin bắt buộc phải có trên 1 bản vẽ kết cấu thật. Test này khoá
    lại: phải có đủ kích thước nhịp từng khoang + tổng bề rộng + chiều cao
    từng tầng, với NHÃN SỐ ĐÚNG (không lấy tự động qua dimstyle — thấy thật:
    dimstyle mặc định có dimlfac=100 khiến số bị nhân sai lệch 100 lần)."""
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_cot("2", "A", "tang2_tang3"),
        _pt_cot("14", "B", "mong_tang2"),
        _pt_cot("18", "C", "mong_tang2"),
        _pt_dam("32", "A-B", "tang2"),
        _pt_dam("45", "B-C", "tang2"),
    ]
    toa_do_truc = {"A": 0.0, "B": 5600.0, "C": 7100.0}
    cao_do_moc = {"mong": -1000.0, "tang2": 3200.0, "tang3": 6400.0}

    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc)
    assert bv is not None

    nhan_kich_thuoc = {kt.nhan for kt in bv.kich_thuoc}
    # 2 nhịp (A-B=5600, B-C=1500) + tổng bề rộng (7100) + 2 chiều cao tầng
    # (mong->tang2=4200, tang2->tang3=3200)
    assert nhan_kich_thuoc == {"5600", "1500", "7100", "4200", "3200"}

    # Mọi kích thước phải tự tính nhãn tường minh (không để None cho backend
    # tự đo — tránh lỗi dimlfac nhân sai lệch).
    assert all(kt.nhan is not None for kt in bv.kich_thuoc)

    # Cỡ chữ kích thước phải LỚN HƠN mức mặc định 15mm (đúng cho mặt cắt,
    # quá nhỏ cho mặt đứng khung tổng thể quy mô hàng nghìn mm).
    assert all(kt.co_chu > 15.0 for kt in bv.kich_thuoc)


def test_lap_rap_moc_tham_chieu_khong_lam_sai_chuoi_kich_thuoc():
    """Hồi quy — lỗi thật phát hiện qua phản hồi trực tiếp: ảnh mẫu người
    dùng cung cấp có thêm 3 mốc cao độ KIẾN TRÚC (Tự nhiên -0.450, Tôn nền
    0.000, Đỉnh móng -1.000) mà Story Definitions của ETABS không có. Nếu gộp
    chung các mốc này vào cao_do_moc (tham gia luôn chuỗi kích thước), chuỗi
    "4200" giữa 2 tầng kết cấu sẽ bị CHẺ NHỎ SAI thành "550+450+3200" — phải
    truyền riêng qua moc_tham_chieu (chỉ vẽ ký hiệu, không ảnh hưởng kích
    thước)."""
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_cot("14", "B", "mong_tang2"),
    ]
    toa_do_truc = {"A": 0.0, "B": 5600.0}
    cao_do_moc = {"mong": -1000.0, "tang2": 3200.0}
    moc_tham_chieu = {"Tu nhien": -450.0, "Ton nen": 0.0}

    bv = khung_ve.lap_rap_mat_dung_khung(
        phan_tu, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc, moc_tham_chieu=moc_tham_chieu,
    )
    assert bv is not None

    # Chuỗi kích thước CHIỀU CAO không bị ảnh hưởng — vẫn đúng 1 đoạn "4200"
    # duy nhất, không bị chẻ theo 2 mốc tham chiếu chen giữa ("5600" là kích
    # thước nhịp A-B, không liên quan, vẫn đúng như bình thường).
    nhan_kich_thuoc = {kt.nhan for kt in bv.kich_thuoc}
    assert nhan_kich_thuoc == {"4200", "5600"}

    # Vẫn phải có đủ ký hiệu (tam giác) cho cả mốc kết cấu lẫn mốc tham
    # chiếu — tổng 4 mốc (mong, tang2, Tu nhien, Ton nen) — CHỈ ghi số cao
    # độ, KHÔNG kèm tên mốc trong chữ nữa (thấy thật: người dùng yêu cầu "bỏ
    # mấy chữ tầng tầng đi, không cần thiết").
    from src.drawing import layers

    tam_giac_cao_do = [dg for dg in bv.da_giac if dg.layer == layers.AXIS.ten]
    assert len(tam_giac_cao_do) == 4

    noi_dung_chu = [c.noi_dung for c in bv.chu]
    assert "-0.45" in noi_dung_chu  # Tu nhien
    assert "+0.00" in noi_dung_chu  # Ton nen
    assert "-1.00" in noi_dung_chu  # mong
    assert "+3.20" in noi_dung_chu  # tang2
    assert not any("Tu nhien" in c or "Ton nen" in c for c in noi_dung_chu)


def test_lap_rap_khung_bao_dam_va_nhan_gon_o_goc():
    """Hồi quy — SỬA LẠI LẦN NỮA, LẦN NÀY THEO BẰNG CHỨNG MẠNH HƠN: đối chiếu
    trực tiếp bản vẽ mẫu CHÍNH THỨC của ĐÚNG bài tập này
    (`data/samples/BoTriThep_KhungTruc5_mau.pdf`, không phải 1 ảnh chụp CAD
    không rõ nguồn gốc/loại bản vẽ như lần sửa trước) + tiêu chuẩn TCVN
    4612-88 trích dẫn rõ ràng (`KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md` mục 1.2):
    bê tông trên bản vẽ RIÊNG cho bố trí cốt thép phải coi như TRONG SUỐT
    (nét MẢNH), để cốt thép (đậm) nổi bật — NGƯỢC nhận định "đậm — đúng ảnh
    thật" của lần sửa trước. `do_rong_net` (ép độ rộng hình học cứng, đè lên
    mọi Lineweight của layer) đã BỎ HẲN khỏi `ve_mat_dung_khung` — đường bao
    giờ chỉ phụ thuộc `layers.OUTLINE.do_day_net_mm` (đã sửa về nét mảnh)."""
    phan_tu = [_pt_cot("1", "A", "mong_tang2"), _pt_cot("14", "B", "mong_tang2"), _pt_dam("32", "A-B", "tang2")]
    ky_hieu = {
        "1": [KyHieuThep(so_hieu=1, so_luong_duong_kinh="4Ø22", chieu_dai="L=4200")],
        "14": [KyHieuThep(so_hieu=1, so_luong_duong_kinh="4Ø22", chieu_dai="L=4200")],
        "32": [KyHieuThep(so_hieu=2, so_luong_duong_kinh="2Ø20", chieu_dai="L=5600", vi_tri_tren_cau_kien="dai_dien")],
    }
    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, ky_hieu_theo_ten=ky_hieu)
    assert bv is not None

    from src.drawing import layers

    be_tong = [dg for dg in bv.da_giac if dg.layer == layers.OUTLINE.ten]
    assert len(be_tong) == 3  # 2 cột + 1 dầm
    assert all(dg.do_rong_net == 0 for dg in be_tong)  # mảnh — không ép độ rộng hình học

    # KHÔNG vẽ tiết diện thanh dạng ĐA GIÁC/HÌNH giả trên layer REBAR_MAIN —
    # nhưng PHẢI có đường thép dọc THẬT (VeDoanThang) chạy dọc cấu kiện, xem
    # test riêng test_lap_rap_ve_duong_thep_doc_that bên dưới.
    thep_da_giac = [dg for dg in bv.da_giac if dg.layer == layers.REBAR_MAIN.ten]
    assert len(thep_da_giac) == 0

    # Vòng tròn ký hiệu số hiệu (layer SO_HIEU) phải xuất hiện — 1 cho mỗi
    # cấu kiện trong ky_hieu ở trên (3 cấu kiện, mỗi cấu kiện 1 KyHieuThep).
    vong_tron_so_hieu = [vt for vt in bv.vong_tron if vt.layer == layers.SO_HIEU.ten]
    assert len(vong_tron_so_hieu) == 3

    # Nhãn cấu kiện (chỉ còn TÊN, vd "1" — KHÔNG kèm mô tả thép nữa) đặt
    # lệch về góc trên-trái — với cột 1 (x_truc=0, b=220 hiển thị theo h=300
    # -> nửa bề rộng 150, y_tren=3200): x phải > x0=-150, y phải < y_tren=3200.
    # Lọc thêm layer=TEXT — tránh nhầm với text "1" bên trong vòng tròn số
    # hiệu (layer SO_HIEU, cùng nội dung "1" vì so_hieu=1 cũng được gán).
    nhan_cot1 = next(c for c in bv.chu if c.noi_dung == "1" and c.layer == layers.TEXT.ten)
    assert nhan_cot1.vi_tri.x > -150.0
    assert nhan_cot1.vi_tri.y < 3200.0
    assert not nhan_cot1.canh_giua  # căn trái mặc định, không còn canh_giua như bản centered cũ


def test_lap_rap_ve_duong_thep_doc_that():
    """Hồi quy — người dùng phản hồi trực tiếp qua ảnh so sánh với bản vẽ mẫu
    thật: chỉ có ký hiệu số hiệu (vòng tròn lơ lửng) mà KHÔNG có đường thép
    dọc thật chạy dọc cấu kiện khiến khung "trông rất xấu, không có thép bên
    trong" — bản mẫu thật LUÔN có đường thép dọc chạy suốt chiều dài cấu
    kiện. Thêm 2 đường (mép gần/xa cho cột; trên/dưới cho dầm) trên layer
    REBAR_MAIN (đậm nhất, mục 1.2 KY_HIEU) — độc lập với ký hiệu số hiệu."""
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_dam("32", "A-B", "tang2"),  # có cả "goi" (trên) và "giua_nhip" (dưới)
    ]
    ky_hieu = {
        "1": [KyHieuThep(so_hieu=1, so_luong_duong_kinh="4Ø22", chieu_dai="L=3200")],
        "32": [
            KyHieuThep(so_hieu=2, so_luong_duong_kinh="2Ø18", chieu_dai="L=5600", vi_tri_tren_cau_kien="goi_trai"),
            KyHieuThep(so_hieu=3, so_luong_duong_kinh="3Ø16", chieu_dai="L=5600", vi_tri_tren_cau_kien="giua_nhip"),
        ],
    }
    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, ky_hieu_theo_ten=ky_hieu, toa_do_truc={"A": 0.0, "B": 5600.0}, cao_do_moc={"mong": -1000.0, "tang2": 3200.0})
    assert bv is not None

    from src.drawing import layers

    duong_thep = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_MAIN.ten]
    # Cột: 2 đường (mép gần/xa). Dầm: 2 đường (trên VÌ có "goi_trai" + dưới VÌ có "giua_nhip").
    assert len(duong_thep) == 4

    # Đường thép cột phải chạy SUỐT chiều cao đoạn cột — vị trí hình học nay
    # theo toạ độ SCHEMATIC (khung_ve._toa_do_deu_giu_thu_tu): mong/tang2 chỉ
    # cách nhau 4200mm thật (>=3000 sàn) -> bước đều = 4200 -> mong=0,
    # tang2=4200 (KHÔNG còn -1000/3200 thật — số thật vẫn đúng ở NHÃN kích
    # thước, xem test_lap_rap_toa_do_that_khung_truc5).
    duong_cot = [dt for dt in duong_thep if dt.p1.x == dt.p2.x]  # đường dọc (x không đổi)
    assert len(duong_cot) == 2
    for dt in duong_cot:
        assert {dt.p1.y, dt.p2.y} == {0.0, 4200.0}

    # Vạch cốt đai MINH HOẠ (layer REBAR_STIRRUP) — hồi quy: người dùng phản
    # hồi trực tiếp "không thấy nét thép đai đâu" khi xem bản vẽ thật, mặt
    # đứng khung trước đó hoàn toàn không có đại diện nào cho cốt đai.
    dai = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_STIRRUP.ten]
    assert len(dai) > 0
    # Vạch đai cột phải NGANG (nối 2 đường thép dọc), không phải dọc.
    dai_cot = [dt for dt in dai if dt.p1.y == dt.p2.y and 0.0 <= dt.p1.y <= 4200.0]
    assert len(dai_cot) > 0


def test_lap_rap_khong_ve_duong_thep_khi_khong_co_ky_hieu():
    # Cấu kiện KHÔNG có ky_hieu (vd Rule Engine chưa đạt/chưa có dữ liệu) ->
    # KHÔNG tự vẽ đường thép nào (không bịa thép khi chưa xác nhận đã chọn).
    phan_tu = [_pt_cot("1", "A", "mong_tang2")]
    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu, ky_hieu_theo_ten={})
    assert bv is not None

    from src.drawing import layers

    duong_thep = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_MAIN.ten]
    assert duong_thep == []
    dai = [dt for dt in bv.doan_thang if dt.layer == layers.REBAR_STIRRUP.ten]
    assert dai == []


def test_lap_rap_duong_mat_dat_ve_net_dam():
    """Hồi quy — đúng nguyên văn Giáo Trình Vẽ Kỹ Thuật Xây Dựng (Nguyễn
    Quang Cự - Nguyễn Mạnh Dũng, NXB Giáo Dục), tr.168: 'Mặt đứng được vẽ
    bằng nét liền mảnh... Riêng đường mặt đất vẽ bằng nét liền đậm.' Đường
    tim của mốc mặt đất tự nhiên (ten_mat_dat) phải dùng layers.OUTLINE (đậm)
    — KHÁC các mốc khác (dùng layers.AXIS, nét chấm gạch mảnh như đường tim
    trục thông thường)."""
    from src.drawing import layers

    phan_tu = [_pt_cot("1", "A", "mong_tang2")]
    toa_do_truc = {"A": 0.0}
    cao_do_moc = {"mong": -1000.0, "tang2": 3200.0}
    moc_tham_chieu = {"Tu nhien": -450.0, "Ton nen": 0.0}

    bv = khung_ve.lap_rap_mat_dung_khung(
        phan_tu, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc,
        moc_tham_chieu=moc_tham_chieu, ten_mat_dat="Tu nhien",
    )
    assert bv is not None

    # Đường tim ngang tại y=-450 (mốc "Tu nhien") phải là OUTLINE (đậm).
    duong_tim_ngang = [d for d in bv.doan_thang if d.p1.y == d.p2.y]
    duong_mat_dat = [d for d in duong_tim_ngang if d.p1.y == -450.0]
    assert len(duong_mat_dat) == 1
    assert duong_mat_dat[0].layer == layers.OUTLINE.ten

    # Các đường tim ngang khác (mốc kết cấu, Ton nen) vẫn AXIS (mảnh) như cũ.
    duong_khac = [d for d in duong_tim_ngang if d.p1.y != -450.0]
    assert all(d.layer == layers.AXIS.ten for d in duong_khac)
    assert len(duong_khac) >= 2  # ít nhất mong, tang2 (có thể cả Ton nen)


def geometry_axis_layer() -> str:
    from src.drawing import layers

    return layers.AXIS.ten


def geometry_outline_layer() -> str:
    from src.drawing import layers

    return layers.OUTLINE.ten


def _loc_cau_kien(bv):
    """Lọc da_giac chỉ lấy khối cấu kiện (OUTLINE) — loại bỏ tam giác ký hiệu
    cao độ (mục 10.7, layer TEXT) khi đếm số cột/dầm đã vẽ."""
    return [dg for dg in bv.da_giac if dg.layer == geometry_outline_layer()]


def test_lap_rap_fallback_toa_do_deu_khi_khong_truyen():
    phan_tu = [
        _pt_cot("1", "A", "mong_tang2"),
        _pt_cot("14", "B", "mong_tang2"),
    ]
    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu)
    assert bv is not None
    cau_kien = _loc_cau_kien(bv)
    assert len(cau_kien) == 2
    # 2 trục khác nhau -> toạ độ x khác nhau dù không truyền toa_do_truc
    x_truc_cac_cot = {round((min(p.x for p in dg.diem) + max(p.x for p in dg.diem)) / 2) for dg in cau_kien}
    assert len(x_truc_cac_cot) == 2


def test_lap_rap_bo_qua_dam_thieu_dinh_dang_truc():
    # dầm "truc" không đúng định dạng "X-Y" (thiếu dấu gạch nối) -> bị bỏ qua
    # thay vì lỗi, vì đây là dữ liệu không xác định được topology.
    phan_tu = [_pt_cot("1", "A", "mong_tang2"), _pt_dam("32", "AB", "tang2")]
    bv = khung_ve.lap_rap_mat_dung_khung(phan_tu)
    assert bv is not None
    assert len(_loc_cau_kien(bv)) == 1  # chỉ có cột, dầm bị bỏ qua
