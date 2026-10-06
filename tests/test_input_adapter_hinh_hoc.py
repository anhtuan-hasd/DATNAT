"""Test src/input_adapter/hinh_hoc.py — suy luận toa_do_truc/cao_do_moc từ
PhanTuKhung.truc/tang/chieu_dai (CHANGE_REQUESTS.md mục 5). Thuần Python,
không cần AutoCAD/API key."""

from __future__ import annotations

from src.input_adapter import hinh_hoc
from src.input_adapter.models import LoaiCauKien, PhanTuKhung, TietDien


def _dam(ten: str, truc: str, chieu_dai: float | None, tang: str = "tang3") -> PhanTuKhung:
    return PhanTuKhung(
        ten=ten, loai=LoaiCauKien.DAM, tiet_dien=TietDien(220, 500),
        mac_be_tong="B25", nhom_thep_doc="CB400-V", truc=truc, tang=tang, chieu_dai=chieu_dai,
    )


def _cot(ten: str, truc: str, tang: str, chieu_dai: float | None) -> PhanTuKhung:
    return PhanTuKhung(
        ten=ten, loai=LoaiCauKien.COT, tiet_dien=TietDien(220, 300),
        mac_be_tong="B25", nhom_thep_doc="CB400-V", truc=truc, tang=tang, chieu_dai=chieu_dai,
    )


# ---------------------------------------------------------------------------
# toa_do_truc — suy từ nhịp dầm (A-B, B-C...)
# ---------------------------------------------------------------------------


def test_toa_do_truc_day_du_2_nhip():
    phan_tu = [_dam("32", "A-B", 5600.0), _dam("33", "B-C", 1500.0)]
    kq = hinh_hoc.suy_luan_toa_do_truc(phan_tu)
    assert kq.hoan_tat is True
    assert kq.gia_tri == {"A": 0.0, "B": 5600.0, "C": 7100.0}


def test_toa_do_truc_thieu_chieu_dai_bao_cao_ro():
    phan_tu = [_dam("32", "A-B", None)]
    kq = hinh_hoc.suy_luan_toa_do_truc(phan_tu)
    assert kq.hoan_tat is False
    assert any("A" in d and "B" in d for d in kq.thieu)


def test_toa_do_truc_cot_don_le_khong_noi_duoc():
    # Cột đứng tại trục "D" nhưng KHÔNG có dầm nào bắc tới D -> D rơi vào thieu.
    phan_tu = [_dam("32", "A-B", 5600.0), _cot("D1", "D", "tang2_tang3", 3200.0)]
    kq = hinh_hoc.suy_luan_toa_do_truc(phan_tu)
    assert kq.hoan_tat is False
    assert any("D" in d for d in kq.thieu)
    # Nhưng A/B vẫn suy ra đúng dù D thiếu (không bị "sập" toàn bộ vì 1 trục lẻ).
    assert kq.gia_tri.get("A") == 0.0
    assert kq.gia_tri.get("B") == 5600.0


def test_toa_do_truc_da_biet_giup_hoan_tat_truc_don_le():
    phan_tu = [_dam("32", "A-B", 5600.0), _cot("D1", "D", "tang2_tang3", 3200.0)]
    kq = hinh_hoc.suy_luan_toa_do_truc(phan_tu, da_biet={"D": 12000.0})
    assert kq.hoan_tat is True
    assert kq.gia_tri["D"] == 12000.0
    assert kq.gia_tri["A"] == 0.0


def test_toa_do_truc_chi_1_truc_duy_nhat():
    # Công trình chỉ có 1 trục duy nhất (không có dầm nối 2 trục) -> mặc nhiên gốc 0.
    phan_tu = [_cot("A1", "A", "tang2_tang3", 3200.0)]
    kq = hinh_hoc.suy_luan_toa_do_truc(phan_tu)
    assert kq.hoan_tat is True
    assert kq.gia_tri == {"A": 0.0}


# ---------------------------------------------------------------------------
# cao_do_moc — suy từ chiều cao đoạn cột (tang2_tang3, tang3_tang4...)
# ---------------------------------------------------------------------------


def test_cao_do_moc_day_du_nhieu_tang():
    phan_tu = [
        _cot("C1", "A", "mong_tang2", 4200.0),
        _cot("C2", "A", "tang2_tang3", 3200.0),
        _dam("D1", "A-B", 5600.0, tang="tang3"),  # dầm chỉ nằm ngang tại "tang3", không tạo cạnh mới
    ]
    kq = hinh_hoc.suy_luan_cao_do_moc(phan_tu)
    assert kq.hoan_tat is True
    assert kq.gia_tri == {"mong": 0.0, "tang2": 4200.0, "tang3": 7400.0}


def test_cao_do_moc_dam_tai_moc_khong_ton_tai_bao_thieu():
    # Dầm nằm tại "tangmai" nhưng KHÔNG có đoạn cột nào tới tangmai -> thiếu.
    phan_tu = [_cot("C1", "A", "mong_tang2", 4200.0), _dam("D1", "A-B", 5600.0, tang="tangmai")]
    kq = hinh_hoc.suy_luan_cao_do_moc(phan_tu)
    assert kq.hoan_tat is False
    assert any("tangmai" in d for d in kq.thieu)
