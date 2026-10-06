"""Test bộ đếm vòng lặp giới hạn — src/orchestrator/loops.py."""

from src.orchestrator.loops import BoDemVongLap


def test_con_duoc_thu_ban_dau():
    bo = BoDemVongLap(gioi_han={"tu_sua": 2})
    assert bo.con_duoc_thu("tu_sua")
    assert bo.so_lan_con_lai("tu_sua") == 2


def test_het_luot_sau_khi_vuot_gioi_han():
    bo = BoDemVongLap(gioi_han={"tu_sua": 2})
    assert bo.ghi_nhan_1_lan_thu("tu_sua") is True
    assert bo.ghi_nhan_1_lan_thu("tu_sua") is True
    assert bo.ghi_nhan_1_lan_thu("tu_sua") is False  # lần thứ 3 vượt giới hạn 2
    assert not bo.con_duoc_thu("tu_sua")
    assert bo.so_lan_con_lai("tu_sua") == 0
    assert "tu_sua" in bo.ly_do_dung


def test_cac_loai_vong_lap_doc_lap_nhau():
    bo = BoDemVongLap(gioi_han={"tu_sua": 1, "kiem_chung_ve": 1})
    bo.ghi_nhan_1_lan_thu("tu_sua")
    assert bo.con_duoc_thu("kiem_chung_ve")  # chưa dùng lần nào


def test_loai_khong_khai_bao_gioi_han_mac_dinh_lon():
    bo = BoDemVongLap(gioi_han={})
    for _ in range(100):
        assert bo.ghi_nhan_1_lan_thu("loai_la") is True
