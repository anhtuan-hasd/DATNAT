"""Test các hàm đọc-lại-qua-COM trong src/drawing/verify_drawing.py — dùng
"thực thể COM giả" (duck-typing, chỉ cần đúng thuộc tính `.ObjectName`/
`.Layer`/`.TextString`/`.Coordinates` mà code thật đọc) THAY VÌ AutoCAD thật.

Đây KHÔNG phải cách né việc cần AutoCAD thật — mục đích của các hàm này là
DUYỆT DỮ LIỆU đã có sẵn trong `doc.ModelSpace` (COM collection, chỉ cần hỗ
trợ lặp `for e in doc.ModelSpace`) và so sánh, hoàn toàn KHÔNG gọi ngược lại
bất kỳ phương thức COM nào khác — nên test được đầy đủ logic so sánh bằng
input giả, nhanh, không cần máy có AutoCAD. Việc "AutoCAD có thực sự trả về
đúng .ObjectName/.Coordinates như tài liệu ActiveX Reference mô tả không" là
phạm vi của `scripts/smoke_test_com.py` (chạy thật, cần AutoCAD mở sẵn), tách
biệt khỏi các test logic thuần ở đây.
"""

from __future__ import annotations

from src.drawing import layers, verify_drawing as vd


class _ThucTheGia:
    def __init__(self, object_name: str, layer: str, **kw):
        self.ObjectName = object_name
        self.Layer = layer
        for k, v in kw.items():
            setattr(self, k, v)


class _DocGia:
    """Document COM giả — chỉ cần `.ModelSpace` hỗ trợ lặp `for e in ...`."""

    def __init__(self, thuc_the: list[_ThucTheGia]):
        self.ModelSpace = thuc_the


def _text(noi_dung: str, layer: str = layers.TEXT.ten) -> _ThucTheGia:
    return _ThucTheGia("AcDbText", layer, TextString=noi_dung)


def _da_giac(xs: list[float], ys: list[float], layer: str) -> _ThucTheGia:
    toa_do = [c for x, y in zip(xs, ys) for c in (x, y)]
    return _ThucTheGia("AcDbPolyline", layer, Coordinates=toa_do)


def _vong_tron(layer: str) -> _ThucTheGia:
    return _ThucTheGia("AcDbCircle", layer)


# ---------------------------------------------------------------------------
# lop_khong_hop_le_com / doc_lop_su_dung_com
# ---------------------------------------------------------------------------


def test_doc_lop_su_dung_com_gom_dung_moi_layer_dang_dung():
    doc = _DocGia([_text("a", layers.TEXT.ten), _da_giac([0, 10], [0, 10], layers.OUTLINE_CUT.ten)])
    assert vd.doc_lop_su_dung_com(doc) == {layers.TEXT.ten, layers.OUTLINE_CUT.ten}


def test_lop_khong_hop_le_com_phat_hien_layer_la():
    doc = _DocGia([_text("a", "LAYER_LA_KHONG_TON_TAI")])
    assert vd.lop_khong_hop_le_com(doc) == ["LAYER_LA_KHONG_TON_TAI"]


def test_lop_khong_hop_le_com_rong_khi_dung_quy_uoc():
    doc = _DocGia([_text("a", layers.TEXT.ten), _vong_tron(layers.AXIS.ten)])
    assert vd.lop_khong_hop_le_com(doc) == []


# ---------------------------------------------------------------------------
# doc_noi_dung_text_com / kiem_tra_nhan_mat_cat_day_du_com
# ---------------------------------------------------------------------------


def test_doc_noi_dung_text_com_loc_dung_layer():
    doc = _DocGia([_text("I-I", layers.TEXT.ten), _text("khong_lien_quan", layers.AXIS.ten)])
    assert vd.doc_noi_dung_text_com(doc, layer=layers.TEXT.ten) == ["I-I"]


def test_kiem_tra_nhan_mat_cat_day_du_com_bao_thieu():
    doc = _DocGia([_text("I-I")])
    assert vd.kiem_tra_nhan_mat_cat_day_du_com(doc, ["I-I", "II-II"]) == ["II-II"]


def test_kiem_tra_nhan_mat_cat_day_du_com_du_thi_rong():
    doc = _DocGia([_text("I-I"), _text("II-II")])
    assert vd.kiem_tra_nhan_mat_cat_day_du_com(doc, ["I-I", "II-II"]) == []


# ---------------------------------------------------------------------------
# hop_gioi_han_da_giac_com / khop_kich_thuoc_nao_do
# ---------------------------------------------------------------------------


def test_hop_gioi_han_da_giac_com_tinh_dung_kich_thuoc():
    doc = _DocGia([_da_giac([0, 250, 250, 0], [0, 0, 500, 500], layers.OUTLINE_CUT.ten)])
    hop = vd.hop_gioi_han_da_giac_com(doc, layers.OUTLINE_CUT.ten)
    assert len(hop) == 1
    assert hop[0].rong == 250
    assert hop[0].cao == 500
    assert vd.khop_kich_thuoc_nao_do(hop, 250, 500)
    assert not vd.khop_kich_thuoc_nao_do(hop, 300, 500)


def test_hop_gioi_han_da_giac_com_bo_qua_layer_khac():
    doc = _DocGia([_da_giac([0, 250], [0, 500], layers.OUTLINE.ten)])
    assert vd.hop_gioi_han_da_giac_com(doc, layers.OUTLINE_CUT.ten) == []


def test_ep_kieu_fallback_ve_nguyen_thuc_the_khi_khong_cast_duoc():
    """Hồi quy — LỖI THẬT đã gặp khi chạy thật: `doc.ModelSpace` (early-bound)
    trả về thực thể ở giao diện CHUNG IAcadEntity (dù ObjectName đúng là
    "AcDbPolyline"/"AcDbText"), thiếu hẳn `.Coordinates`/`.TextString` gây
    "IAcadEntity không có thuộc tính ...". `_ep_kieu` phải CastTo khi có thể,
    và fallback về nguyên thực thể khi không (vd thực thể giả này — không
    phải con trỏ COM thật nên CastTo chắc chắn lỗi/không áp dụng được) — vẫn
    phải trả về đúng thực thể gốc để logic đọc `.Coordinates` phía sau không
    vỡ (thực thể giả trong test này đã có sẵn thuộc tính, không qua CastTo)."""
    thuc_the = _da_giac([0, 250], [0, 500], layers.OUTLINE.ten)
    assert vd._ep_kieu(thuc_the, "IAcadLWPolyline") is thuc_the


# ---------------------------------------------------------------------------
# dem_da_giac_theo_layer_com / dem_vong_tron_theo_layer_com — mở rộng cho
# Verification Agent kiểm tra bản vẽ tổng thể (CHANGE_REQUESTS.md mục 2).
# ---------------------------------------------------------------------------


def test_dem_da_giac_theo_layer_com():
    doc = _DocGia(
        [
            _da_giac([0, 1], [0, 1], layers.OUTLINE.ten),
            _da_giac([0, 1], [0, 1], layers.OUTLINE.ten),
            _da_giac([0, 1], [0, 1], layers.OUTLINE_CUT.ten),  # layer khác — không đếm
        ]
    )
    assert vd.dem_da_giac_theo_layer_com(doc, layers.OUTLINE.ten) == 2


def test_dem_vong_tron_theo_layer_com():
    doc = _DocGia([_vong_tron(layers.AXIS.ten), _vong_tron(layers.AXIS.ten), _vong_tron(layers.OUTLINE.ten)])
    assert vd.dem_vong_tron_theo_layer_com(doc, layers.AXIS.ten) == 2


# ---------------------------------------------------------------------------
# kiem_tra_nhan_thep_du_vi_tri_com — hồi quy trực tiếp cho lỗi ghi đè nhãn
# thép (CHANGE_REQUESTS.md mục 3): nhãn gộp PHẢI chứa cả 3 vị trí.
# ---------------------------------------------------------------------------


def test_kiem_tra_nhan_thep_du_vi_tri_com_du_ca_3_vi_tri():
    nhan_gop = "32: goi_trai: 2Ø18+1Ø16 | giua_nhip: 3Ø16 | goi_phai: 2Ø18"
    doc = _DocGia([_text(nhan_gop)])
    thieu = vd.kiem_tra_nhan_thep_du_vi_tri_com(doc, "32", ["goi_trai", "giua_nhip", "goi_phai"])
    assert thieu == []


def test_kiem_tra_nhan_thep_du_vi_tri_com_phat_hien_bi_ghi_de():
    # Mô phỏng ĐÚNG lỗi thật đã gặp: nhãn chỉ còn giữ "goi_phai", mất 2 vị trí kia.
    doc = _DocGia([_text("32: goi_phai: 2Ø18")])
    thieu = vd.kiem_tra_nhan_thep_du_vi_tri_com(doc, "32", ["goi_trai", "giua_nhip", "goi_phai"])
    assert thieu == ["goi_trai", "giua_nhip"]


# ---------------------------------------------------------------------------
# kiem_tra_bang_thong_ke_du_cot_com — 8 cột mục 3.9.
# ---------------------------------------------------------------------------


def test_kiem_tra_bang_thong_ke_du_cot_com_du_8_cot():
    doc = _DocGia([_text(t) for t in vd._TIEU_DE_BANG_THONG_KE_8_COT])
    assert vd.kiem_tra_bang_thong_ke_du_cot_com(doc) == []


def test_kiem_tra_bang_thong_ke_du_cot_com_thieu_cot():
    doc = _DocGia([_text(t) for t in vd._TIEU_DE_BANG_THONG_KE_8_COT[:6]])  # thiếu 2 cột cuối
    thieu = vd.kiem_tra_bang_thong_ke_du_cot_com(doc)
    assert thieu == vd._TIEU_DE_BANG_THONG_KE_8_COT[6:]
