"""Test src/input_adapter/etabs_reader.py — đọc trực tiếp báo cáo ETABS THẬT
(đa bảng quan hệ), dùng chính file mẫu chính thức của đồ án
(`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx`, xem TONGQUAN_AI_AGENT.md mục 3)
làm fixture — không tự tạo fixture giả cho module này vì mục đích của module
CHÍNH LÀ đọc đúng định dạng xuất thật, phải test bằng file thật."""

from pathlib import Path

import pytest

from src.input_adapter import etabs_reader
from src.input_adapter.models import LoaiCauKien

FILE_ETABS_THAT = Path(__file__).parent.parent / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"

pytestmark = pytest.mark.skipif(not FILE_ETABS_THAT.exists(), reason="Thiếu file mẫu ETABS thật")


def test_nhan_dien_file_etabs_that():
    assert etabs_reader.nhan_dien_file_etabs_that(FILE_ETABS_THAT) is True


def test_nhan_dien_tu_choi_file_khong_phai_etabs(thu_muc_tam: Path):
    file_thuong = thu_muc_tam / "khong_phai_etabs.xlsx"
    import pandas as pd

    pd.DataFrame({"A": [1, 2]}).to_excel(file_thuong, index=False)
    assert etabs_reader.nhan_dien_file_etabs_that(file_thuong) is False


def test_doc_etabs_thuc_du_20_phan_tu():
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    assert len(bo.phan_tu) == 20
    so_cot = sum(1 for p in bo.phan_tu if p.loai == LoaiCauKien.COT)
    so_dam = sum(1 for p in bo.phan_tu if p.loai == LoaiCauKien.DAM)
    assert so_cot == 12
    assert so_dam == 8


def test_doc_etabs_thuc_cot_14_khop_thuyet_minh():
    """Đối chiếu với đúng số liệu mục 5.3.2 thuyết minh gốc (cột 14,
    N=483,237kN, M=91,4069kNm, As lý thuyết=752,65mm² — số liệu này đã được
    dùng làm test hồi quy khác trong test_orchestrator_tools.py)."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    cot_14 = next(p for p in bo.phan_tu if p.ten == "14")
    assert cot_14.loai == LoaiCauKien.COT
    assert cot_14.truc == "B"
    assert cot_14.tang == "Mong_Tang2"
    assert cot_14.tiet_dien.b == pytest.approx(220.0)
    assert cot_14.tiet_dien.h == pytest.approx(300.0)
    assert cot_14.mac_be_tong == "B25"
    assert cot_14.nhom_thep_doc == "CB500-V"
    assert cot_14.nhom_thep_dai == "CB240-T"

    vt = cot_14.du_lieu_vi_tri[0]
    assert vt.vi_tri == "dai_dien"
    assert vt.noi_luc.N == pytest.approx(483.237, abs=0.01)
    assert vt.noi_luc.M == pytest.approx(91.4069, abs=0.01)
    assert vt.As_yc == pytest.approx(752.65, abs=1.0)  # PMMArea 0.000753 m² -> làm tròn ~753


def test_doc_etabs_thuc_cot_N_luon_duong_bat_ke_dau_etabs():
    """ETABS quy ước N âm = nén; hệ thống nội bộ dùng N>0 = nén (mục 2.5) —
    module phải TỰ CHUẨN HOÁ dấu, không để giá trị âm lọt xuống Rule Engine."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    for p in bo.phan_tu:
        if p.loai == LoaiCauKien.COT:
            assert p.du_lieu_vi_tri[0].noi_luc.N >= 0


def test_doc_etabs_thuc_dam_32_khop_bang_27():
    """Đối chiếu với Bảng 27 thuyết minh: dầm 32 (nhịp AB, tầng 2), As lý
    thuyết gối trái=686,02; giữa nhịp=473,67; gối phải=654,53 mm²."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    dam_32 = next(p for p in bo.phan_tu if p.ten == "32")
    assert dam_32.loai == LoaiCauKien.DAM
    assert dam_32.truc == "A-B"
    assert dam_32.tang == "Tang2"
    assert dam_32.tiet_dien.b == pytest.approx(220.0)
    assert dam_32.tiet_dien.h == pytest.approx(500.0)

    as_theo_vi_tri = {v.vi_tri: v.As_yc for v in dam_32.du_lieu_vi_tri}
    assert set(as_theo_vi_tri) == {"goi_trai", "giua_nhip", "goi_phai"}
    assert as_theo_vi_tri["goi_trai"] == pytest.approx(686.02, abs=1.0)
    assert as_theo_vi_tri["giua_nhip"] == pytest.approx(473.67, abs=1.0)
    assert as_theo_vi_tri["goi_phai"] == pytest.approx(654.53, abs=1.0)


def test_doc_etabs_thuc_dam_nhip_ngan_van_phan_biet_3_vi_tri():
    """Hồi quy — lỗi thật phát hiện khi đọc file thật lần đầu: dầm nhịp B-C
    (1,5m, rất ngắn) có 2 mặt cắt CÙNG toạ độ Location (~1,39m, ETABS chỉ báo
    1 vị trí đại diện gần cuối dầm cho cả kiểm tra giữa nhịp lẫn gối phải) —
    nếu phân loại vị trí chỉ dựa theo ngưỡng toạ độ (không theo mặt thép chi
    phối) sẽ gộp nhầm CẢ HAI thành cùng 1 nhãn 'goi_phai', làm mất hẳn 1 vị
    trí (giữa nhịp)."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    for ten_dam_ngan in ("39", "41", "43", "45"):
        dam = next(p for p in bo.phan_tu if p.ten == ten_dam_ngan)
        cac_vi_tri = [v.vi_tri for v in dam.du_lieu_vi_tri]
        assert sorted(cac_vi_tri) == ["giua_nhip", "goi_phai", "goi_trai"], f"dầm {ten_dam_ngan}: {cac_vi_tri}"


def test_doc_etabs_thuc_dam_khong_co_Q_tho():
    """Bảng Concrete Design Summary của ETABS không xuất Q thô cho dầm (chỉ
    có VRebar đã thiết kế sẵn) — Q phải là None, KHÔNG được bịa/suy diễn."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    for p in bo.phan_tu:
        if p.loai == LoaiCauKien.DAM:
            for v in p.du_lieu_vi_tri:
                assert v.noi_luc.Q is None


def test_doc_etabs_thuc_tra_ve_toa_do_truc_cao_do_moc_chinh_xac_tu_grid_story():
    """CHANGE_REQUESTS.md mục 5 — trước đây 2 giá trị này bị TÍNH RỒI BỎ
    (chỉ dùng nội bộ), Input Adapter Agent không lấy lại được. Giờ trả ra
    ngoài, và PHẢI khớp đúng tên trục 'A'/'B'/'C' thật đã dùng để gán
    'truc'/'tang' cho từng phần tử ở các test phía trên (cot_14.truc=='B',
    dam_32.truc=='A-B', dam_32.tang=='Tang2')."""
    bo, toa_do_truc, cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    assert {"A", "B"}.issubset(toa_do_truc.keys())
    assert "Tang2" in cao_do_moc
    # Trục thật sự phải cách nhau > 0 (không phải toàn bộ = 0, tức đọc nhầm cột).
    assert len(set(toa_do_truc.values())) > 1


def test_doc_etabs_thuc_phan_tu_co_chieu_dai():
    """Trước đây PhanTuKhung sinh ra từ đường này KHÔNG có 'chieu_dai' (bị bỏ
    qua khi unpack ket_noi_theo_frame) — khiến mọi phần tử nguồn ETABS thật
    bị BỎ QUA hoàn toàn khỏi bảng thống kê thép (drawing_agent._xay_dong_thong_ke
    chỉ nhận phần tử CÓ chieu_dai). Nay phải có, > 0, cho MỌI phần tử."""
    bo, _toa_do_truc, _cao_do_moc = etabs_reader.doc_etabs_thuc(FILE_ETABS_THAT)
    for p in bo.phan_tu:
        assert p.chieu_dai is not None and p.chieu_dai > 0, f"phần tử '{p.ten}' thiếu chieu_dai"
