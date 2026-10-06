"""Test heuristic dò cột — src/input_adapter/heuristics.py."""

from src.input_adapter import heuristics


def test_du_doan_anh_xa_cot_header_tieng_viet():
    cot = ["Phan_tu", "Loai", "Vi_tri", "b(mm)", "h(mm)", "As_yc(mm2)", "M(kNm)", "N(kN)", "Q(kN)", "To_hop", "Mac_be_tong", "Nhom_thep"]
    anh_xa = heuristics.du_doan_anh_xa_cot(cot)

    assert anh_xa["ten_phan_tu"].cot_nguon == "Phan_tu"
    assert anh_xa["b"].cot_nguon == "b(mm)"
    assert anh_xa["h"].cot_nguon == "h(mm)"
    assert anh_xa["M"].cot_nguon == "M(kNm)"
    assert anh_xa["N"].cot_nguon == "N(kN)"
    assert anh_xa["Q"].cot_nguon == "Q(kN)"
    assert anh_xa["As_yc"].cot_nguon == "As_yc(mm2)"
    for truong in ["ten_phan_tu", "b", "h", "M", "N", "Q", "As_yc"]:
        assert anh_xa[truong].do_tin_cay >= 0.75


def test_du_doan_anh_xa_cot_header_etabs_tieng_anh():
    cot = ["Story", "Beam", "Unique Name", "Section", "Combo", "Station(mm)", "P(kN)", "V2(kN)", "M3(kN-m)", "AsReq(mm2)"]
    anh_xa = heuristics.du_doan_anh_xa_cot(cot)

    assert anh_xa["ten_phan_tu"].cot_nguon == "Beam"
    assert anh_xa["tang"].cot_nguon == "Story"
    assert anh_xa["combo"].cot_nguon == "Combo"
    assert anh_xa["N"].cot_nguon == "P(kN)"
    assert anh_xa["Q"].cot_nguon == "V2(kN)"
    assert anh_xa["M"].cot_nguon == "M3(kN-m)"
    assert anh_xa["As_yc"].cot_nguon == "AsReq(mm2)"
    assert anh_xa["vi_tri"].cot_nguon == "Station(mm)"
    assert anh_xa["tiet_dien_ky_hieu"].cot_nguon == "Section"


def test_truong_can_hoi_nguoi_dung_va_thieu_bat_buoc():
    cot = ["Story", "Column", "Section", "P(kN)"]  # thiếu hẳn cột b, h, M, Q
    anh_xa = heuristics.du_doan_anh_xa_cot(cot)
    thieu = heuristics.truong_bat_buoc_con_thieu(anh_xa, ["ten_phan_tu", "b", "h", "M", "Q"])
    assert set(thieu) == {"b", "h", "M", "Q"}


def test_doan_don_vi_luc_tu_ten_cot():
    assert heuristics.doan_don_vi_luc("M(kNm)") == ("kN", 0.9)
    assert heuristics.doan_don_vi_luc("M3(kN-m)") == ("kN", 0.9)
    assert heuristics.doan_don_vi_luc("M (N.mm)")[0] == "N"


def test_doan_don_vi_luc_tu_do_lon_so_lieu():
    # Tên cột không rõ đơn vị -> dùng độ lớn số liệu làm gợi ý.
    don_vi, tin_cay = heuristics.doan_don_vi_luc("Mo_men", gia_tri_mau=[346.5, 417.74, 462.0])
    assert don_vi == "kN"
    don_vi2, _ = heuristics.doan_don_vi_luc("Mo_men", gia_tri_mau=[3.465e8, 4.177e8])
    assert don_vi2 == "N"
