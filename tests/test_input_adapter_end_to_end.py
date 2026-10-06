"""
Test toàn trình Input Adapter (đọc -> ánh xạ heuristic -> xác nhận -> chuẩn
hoá) trên 2 fixture tự tạo (tests/fixtures/) — mô phỏng cả file "đơn giản"
lẫn file "đầy đủ nhiều sheet kiểu ETABS" như mục tiêu Phase 2 đề ra.
"""

from pathlib import Path

from src.input_adapter import adapter, readers
from src.input_adapter.models import DonViLucGoc, LoaiCauKien

FIXTURES = Path(__file__).parent / "fixtures"


def test_file_don_gian_toan_trinh():
    df = readers.doc_csv(FIXTURES / "dam_don_gian.csv")
    ket_qua_anh_xa = adapter.xac_dinh_anh_xa(df)

    # Không cần LLM cho file này — header tiếng Việt đã đủ rõ ràng.
    assert not ket_qua_anh_xa.thieu_bat_buoc

    anh_xa_da_xac_nhan = {t: dx.cot_nguon for t, dx in ket_qua_anh_xa.anh_xa.items()}
    bo_du_lieu = adapter.chuan_hoa_bang("Khung mẫu đơn giản", df, anh_xa_da_xac_nhan, DonViLucGoc.KN_KNM)

    assert len(bo_du_lieu.phan_tu) == 2  # "44-45" (dầm) và "22" (cột)
    dam = next(p for p in bo_du_lieu.phan_tu if p.ten == "44-45")
    assert dam.loai == LoaiCauKien.DAM
    assert dam.tiet_dien.b == 250.0 and dam.tiet_dien.h == 700.0
    assert {vt.vi_tri for vt in dam.du_lieu_vi_tri} == {"goi_trai", "goi_phai", "giua_nhip"}
    goi_trai = next(vt for vt in dam.du_lieu_vi_tri if vt.vi_tri == "goi_trai")
    assert goi_trai.As_yc == 1212.0
    assert goi_trai.noi_luc.M == 346.5
    assert goi_trai.noi_luc.Q == 180.2

    cot = next(p for p in bo_du_lieu.phan_tu if p.ten == "22")
    assert cot.loai == LoaiCauKien.COT
    assert cot.du_lieu_vi_tri[0].noi_luc.N == 1514.38


def test_file_day_du_etabs_toan_trinh_2_sheet_rieng():
    sheets = readers.doc_excel(FIXTURES / "bao_cao_etabs_day_du.xlsx")
    sheet_hop_le = readers.tim_sheet_co_du_lieu_khung(sheets, so_cot_toi_thieu=5)
    assert set(sheet_hop_le) == {"Concrete Beam Envelope", "Concrete Column Envelope"}

    # --- Sheet dầm: sheet này không có cột "loại" (loại biết từ TÊN SHEET,
    # không phải từ dữ liệu) -> loại trừ "loai" khỏi danh sách bắt buộc khi
    # gọi xac_dinh_anh_xa cho riêng sheet này, và truyền loai_mac_dinh=DAM
    # khi chuẩn hoá — đúng cách Agent điều phối (Phase 4) sẽ dùng thực tế.
    truong_bat_buoc_theo_sheet = [t for t in adapter.TRUONG_BAT_BUOC if t != "loai"]
    df_dam = sheets["Concrete Beam Envelope"]
    ket_qua_dam = adapter.xac_dinh_anh_xa(df_dam, truong_bat_buoc=truong_bat_buoc_theo_sheet)
    assert not ket_qua_dam.thieu_bat_buoc, ket_qua_dam.thieu_bat_buoc
    anh_xa_dam = {t: dx.cot_nguon for t, dx in ket_qua_dam.anh_xa.items()}
    phan_tu_dam = adapter.chuan_hoa_thanh_phan_tu(df_dam, anh_xa_dam, DonViLucGoc.KN_KNM, LoaiCauKien.DAM)

    assert len(phan_tu_dam) == 1
    b12 = phan_tu_dam[0]
    assert b12.loai == LoaiCauKien.DAM
    # b,h suy ra từ cột "Section"="D250x700" (không có cột b/h riêng trong sheet này).
    assert b12.tiet_dien.b == 250.0 and b12.tiet_dien.h == 700.0
    # 3 station (0, 3200, 1600) -> 3 vị trí riêng biệt (mỗi station 1 tổ hợp -> giữ nguyên).
    assert len(b12.du_lieu_vi_tri) == 3
    vt_0 = next(vt for vt in b12.du_lieu_vi_tri if vt.vi_tri == "0")
    assert vt_0.As_yc == 1212.0
    assert vt_0.noi_luc.M == 346.5
    assert vt_0.noi_luc.to_hop_chi_phoi == "COMBO3"

    # --- Sheet cột: cùng lý do, loại trừ "loai" khỏi bắt buộc ---
    df_cot = sheets["Concrete Column Envelope"]
    ket_qua_cot = adapter.xac_dinh_anh_xa(df_cot, truong_bat_buoc=truong_bat_buoc_theo_sheet)
    assert not ket_qua_cot.thieu_bat_buoc, ket_qua_cot.thieu_bat_buoc
    anh_xa_cot = {t: dx.cot_nguon for t, dx in ket_qua_cot.anh_xa.items()}
    phan_tu_cot = adapter.chuan_hoa_thanh_phan_tu(df_cot, anh_xa_cot, DonViLucGoc.KN_KNM, LoaiCauKien.COT)

    assert len(phan_tu_cot) == 1
    c22 = phan_tu_cot[0]
    assert c22.loai == LoaiCauKien.COT
    assert c22.tiet_dien.b == 250.0 and c22.tiet_dien.h == 600.0
    assert c22.du_lieu_vi_tri[0].As_yc == 1362.0
    assert c22.du_lieu_vi_tri[0].noi_luc.N == 1514.38
