"""Test src/orchestrator/agents/verification_agent.py — dùng "Document COM
giả" (cùng kỹ thuật `tests/test_drawing_verify_com.py`) để test logic tổng
hợp (`_kiem_tra_mat_cat`/`_kiem_tra_mat_dung_khung`) mà KHÔNG cần AutoCAD
thật. `kiem_chung_ban_ve` (tool đầy đủ, gồm cả bo_dem) test riêng bằng
NguCanhVerification + BoDemVongLap thật."""

from __future__ import annotations

from src.drawing import layers
from src.drawing.verify_drawing import _TIEU_DE_BANG_THONG_KE_8_COT
from src.orchestrator.agents import verification_agent as va
from src.orchestrator.loops import BoDemVongLap
from src.orchestrator.shared.phien_cad import PhienCAD


class _ThucTheGia:
    def __init__(self, object_name: str, layer: str, **kw):
        self.ObjectName = object_name
        self.Layer = layer
        for k, v in kw.items():
            setattr(self, k, v)


class _DocGia:
    def __init__(self, thuc_the):
        self.ModelSpace = thuc_the


def _text(nd, layer=layers.TEXT.ten):
    return _ThucTheGia("AcDbText", layer, TextString=nd)


def _da_giac(xs, ys, layer):
    return _ThucTheGia("AcDbPolyline", layer, Coordinates=[c for x, y in zip(xs, ys) for c in (x, y)])


def _vong_tron(layer):
    return _ThucTheGia("AcDbCircle", layer)


# ---------------------------------------------------------------------------
# _kiem_tra_mat_cat
# ---------------------------------------------------------------------------


def test_kiem_tra_mat_cat_dat_khi_du_kich_thuoc_va_nhan():
    doc = _DocGia([_da_giac([0, 220, 220, 0], [0, 0, 500, 500], layers.OUTLINE_CUT.ten), _text("I-I")])
    vi_pham = va._kiem_tra_mat_cat(doc, {"b_ky_vong": 220, "h_ky_vong": 500, "nhan_ky_vong": ["I-I"]})
    assert vi_pham == []


def test_kiem_tra_mat_cat_bao_sai_kich_thuoc():
    doc = _DocGia([_da_giac([0, 999], [0, 500], layers.OUTLINE_CUT.ten)])
    vi_pham = va._kiem_tra_mat_cat(doc, {"b_ky_vong": 220, "h_ky_vong": 500})
    assert len(vi_pham) == 1 and "220" in vi_pham[0]


# ---------------------------------------------------------------------------
# _kiem_tra_mat_dung_khung
# ---------------------------------------------------------------------------


def test_kiem_tra_mat_dung_khung_dat_du_dieu_kien():
    doc = _DocGia(
        [
            _da_giac([0, 1], [0, 1], layers.OUTLINE.ten),  # cột 1
            _da_giac([0, 1], [0, 1], layers.OUTLINE.ten),  # dầm 1
            _da_giac([0, 1], [0, 1], layers.OUTLINE.ten),  # khung tên (+1, không tính vào so_cot/so_dam)
            _vong_tron(layers.AXIS.ten), _vong_tron(layers.AXIS.ten),  # 2 trục
            # 3 vòng tròn ký hiệu số hiệu (goi_trai/giua_nhip/goi_phai của dầm 32) — thay
            # cho TEXT mô tả dài cũ, đúng hệ ký hiệu số hiệu mục 2.2.
            _vong_tron(layers.SO_HIEU.ten), _vong_tron(layers.SO_HIEU.ten), _vong_tron(layers.SO_HIEU.ten),
            *[_text(t) for t in _TIEU_DE_BANG_THONG_KE_8_COT],
        ]
    )
    vi_pham = va._kiem_tra_mat_dung_khung(
        doc,
        {
            "so_cot_ky_vong": 1, "so_dam_ky_vong": 1,
            "so_ky_hieu_ky_vong": 3,
            "ten_truc_ky_vong": ["A", "B"],
        },
    )
    assert vi_pham == []


def test_kiem_tra_mat_dung_khung_phat_hien_thieu_cau_kien():
    # Chỉ vẽ 1 cấu kiện dù dữ liệu có 12 cột + 8 dầm -> đúng lớp lỗi VERIFICATION_AGENT.md cảnh báo.
    doc = _DocGia([_da_giac([0, 1], [0, 1], layers.OUTLINE.ten)])
    vi_pham = va._kiem_tra_mat_dung_khung(
        doc, {"so_cot_ky_vong": 12, "so_dam_ky_vong": 8, "can_co_bang_thong_ke": False},
    )
    assert len(vi_pham) == 1 and "ít hơn kỳ vọng" in vi_pham[0]


def test_kiem_tra_mat_dung_khung_phat_hien_thieu_vong_tron_truc():
    doc = _DocGia([_vong_tron(layers.AXIS.ten)])
    vi_pham = va._kiem_tra_mat_dung_khung(doc, {"ten_truc_ky_vong": ["A", "B", "C"]})
    assert any("vòng tròn" in v for v in vi_pham)


def test_kiem_tra_mat_dung_khung_bo_qua_khi_khong_truyen_so_ky_hieu():
    # Không truyền so_ky_hieu_ky_vong -> KHÔNG kiểm tra số ký hiệu (tool khác
    # có thể gọi loai_kiem_tra='mat_dung_khung' mà chưa cần kiểm phần này).
    doc = _DocGia([])
    vi_pham = va._kiem_tra_mat_dung_khung(doc, {"can_co_bang_thong_ke": False})
    assert vi_pham == []


def test_kiem_tra_mat_dung_khung_phat_hien_thieu_vong_tron_so_hieu():
    doc = _DocGia([_vong_tron(layers.SO_HIEU.ten)])  # chỉ có 1, kỳ vọng 3
    vi_pham = va._kiem_tra_mat_dung_khung(doc, {"so_ky_hieu_ky_vong": 3, "can_co_bang_thong_ke": False})
    assert len(vi_pham) == 1 and "ký hiệu số hiệu" in vi_pham[0]


# ---------------------------------------------------------------------------
# kiem_chung_ban_ve (tool đầy đủ) — bo_dem tăng đúng khi vi_pham.
# ---------------------------------------------------------------------------


def test_kiem_chung_ban_ve_bo_dem_tang_khi_chua_dat():
    doc = _DocGia([])  # rỗng -> chắc chắn thiếu, luôn vi phạm
    # gioi_han=1 -> lần gọi 1 vẫn còn được (con_duoc: 1<=1), lần gọi 2 mới hết lượt (2<=1=False).
    bo_dem = BoDemVongLap(gioi_han={"kiem_chung_ve": 1})
    nc = va.NguCanhVerification(
        hoi_nguoi_dung=lambda c, l: "đồng ý",
        phien_cad=PhienCAD(app=None, doc=doc, thu_muc_xuat="."),
        bo_dem=bo_dem,
    )
    kq1 = va.kiem_chung_ban_ve(nc, {"nhan_ky_vong": ["I-I"]})
    assert kq1["dat"] is False and kq1["so_lan_con_lai"] == 0
    kq2 = va.kiem_chung_ban_ve(nc, {"nhan_ky_vong": ["I-I"]})
    assert kq2["dat"] is False and kq2.get("het_luot_kiem_chung") is True
