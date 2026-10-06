"""Đọc lại hình học đã vẽ để đối chiếu — nền tảng cho "vòng lặp kiểm chứng
bản vẽ" (`docs/TONGQUAN_AI_AGENT.md` mục 5, thực hiện bởi Verification Agent
— `src/orchestrator/agents/verification_agent.py`). Module này CHỈ cung cấp
các hàm đọc/so sánh THUẦN (không tự quyết định "vẽ lại hay không" — đó là
việc của Verification Agent, dựa trên kết quả các hàm ở đây).

2 mức kiểm tra tách biệt:
1. Kiểm tra trên chính IR (`geometry.BanVe`) TRƯỚC KHI vẽ — xác nhận LOGIC
   hình học đúng (vd mặt cắt đúng kích thước b×h khai báo). Không phụ thuộc
   backend nào — dùng cho cả test tự động không cần AutoCAD.
2. Đọc lại TRỰC TIẾP qua AutoCAD COM (`doc.ModelSpace`) sau khi đã vẽ thật —
   xác nhận AutoCAD vẽ ra đúng như IR, không có sai lệch khi chuyển sang COM
   (vd layer, toạ độ, nhãn).

CHANGE_REQUESTS.md mục 2: trước đây mức 2 đọc qua file DXF bằng `ezdxf`
(`import ezdxf` đầu file) — nay đọc THẲNG qua Document COM đang mở, không
qua file trung gian nào, và KHÔNG còn phụ thuộc `ezdxf`/`backend_dxf.py`
(đã xoá khỏi repo). Mọi hàm mức 2 nhận tham số `doc` (Document COM), không
còn nhận `duong_dan: str` như bản cũ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from . import layers as layers_module
from .backend_com import _thu_lai_khi_com_ban
from .geometry import BanVe


@dataclass(frozen=True)
class HopGioiHan:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def rong(self) -> float:
        return self.max_x - self.min_x

    @property
    def cao(self) -> float:
        return self.max_y - self.min_y


# ---------------------------------------------------------------------------
# Mức 1 — kiểm tra trực tiếp trên IR (geometry.BanVe), chưa cần vẽ ra AutoCAD.
# Không đổi so với bản trước — các hàm này KHÔNG phụ thuộc backend nào.
# ---------------------------------------------------------------------------


def hop_gioi_han_da_giac_ir(ban_ve: BanVe, layer: str) -> list[HopGioiHan]:
    ket_qua = []
    for dg in ban_ve.da_giac:
        if dg.layer != layer or not dg.diem:
            continue
        xs = [d.x for d in dg.diem]
        ys = [d.y for d in dg.diem]
        ket_qua.append(HopGioiHan(min(xs), min(ys), max(xs), max(ys)))
    return ket_qua


def kiem_tra_mat_cat_ir(ban_ve: BanVe, b_ky_vong: float, h_ky_vong: float, dung_sai_mm: float = 1.0) -> list[str]:
    """Đối chiếu đường bao OUTLINE_CUT của 1 mặt cắt (IR, trước khi vẽ ra
    AutoCAD) với kích thước b,h ĐÃ TÍNH TỪ Rule Engine/Input Adapter. Trả về
    danh sách vi phạm (rỗng = đạt)."""
    vi_pham: list[str] = []
    hop = hop_gioi_han_da_giac_ir(ban_ve, layers_module.OUTLINE_CUT.ten)
    if not hop:
        return [f"Mặt cắt '{ban_ve.ten}' không có đường bao trên layer {layers_module.OUTLINE_CUT.ten}."]
    h0 = hop[0]
    if abs(h0.rong - b_ky_vong) > dung_sai_mm:
        vi_pham.append(f"Bề rộng vẽ ra {h0.rong:g}mm khác kích thước khai báo b={b_ky_vong:g}mm.")
    if abs(h0.cao - h_ky_vong) > dung_sai_mm:
        vi_pham.append(f"Chiều cao vẽ ra {h0.cao:g}mm khác kích thước khai báo h={h_ky_vong:g}mm.")
    return vi_pham


def dem_thanh_thep_ir(ban_ve: BanVe) -> int:
    """Đếm số vòng tròn trên layer REBAR_MAIN — phải khớp tổng số thanh thép
    dọc đã chọn ở Rule Engine cho mặt cắt này."""
    return sum(1 for vt in ban_ve.vong_tron if vt.layer == layers_module.REBAR_MAIN.ten)


# ---------------------------------------------------------------------------
# Mức 2 — đọc lại TRỰC TIẾP qua AutoCAD COM (doc.ModelSpace đang mở).
#
# Tên lớp COM (ObjectName) dùng để lọc theo loại thực thể — đã TRA CỨU tài
# liệu AutoCAD ActiveX Reference chính thức (help.autodesk.com), KHÔNG đoán
# theo trí nhớ (cùng nguyên tắc "không tự bịa số liệu/tên gọi" đã áp dụng
# xuyên suốt đồ án): AddLightWeightPolyline (dùng cho MỌI VeDaGiac trong
# backend_com.py) tạo ra đối tượng có ObjectName = "AcDbPolyline" — KHÔNG
# PHẢI "AcDbLWPolyline" như tên hàm dễ khiến lầm tưởng.
# ---------------------------------------------------------------------------

_OBJECTNAME_POLYLINE = "AcDbPolyline"
_OBJECTNAME_TEXT = "AcDbText"
_OBJECTNAME_CIRCLE = "AcDbCircle"


def _duyet_modelspace(doc: Any) -> Iterator[Any]:
    """Duyệt qua từng thực thể trong ModelSpace của Document COM đang mở.
    `doc.ModelSpace` là 1 COM collection hỗ trợ sẵn giao thức lặp tiêu chuẩn
    của win32com (dynamic dispatch tự ánh xạ `_NewEnum` sang Python
    iterator) — không cần chỉ số/Count thủ công."""
    for thuc_the in doc.ModelSpace:
        yield thuc_the


def doc_lop_su_dung_com(doc: Any) -> set[str]:
    """Tập hợp TÊN LAYER đang có ít nhất 1 thực thể sử dụng trong ModelSpace.

    Bọc qua `_thu_lai_khi_com_ban` (tái dùng nguyên hàm của backend_com.py) —
    lỗi thật đã gặp: duyệt `doc.ModelSpace` sau khi đã vẽ nhiều thực thể
    (~20 mặt cắt + mặt đứng khung) có thể gặp "Call was rejected by callee"
    thoáng qua GIỐNG HỆT khi VẼ, không chỉ riêng lúc vẽ — trước đây các hàm
    đọc lại ở module này KHÔNG tự thử lại, khiến 1 lần đọc lỗi thoáng qua làm
    cả `kiem_chung_ban_ve` báo lỗi (không phải "chưa đạt" hợp lệ), và vì lỗi
    đó không đi qua nhánh tăng bộ đếm tự sửa trong `verification_agent.py`,
    pipeline.py có thể lặp lại vô hạn (không bao giờ hết lượt thử)."""
    return _thu_lai_khi_com_ban(lambda: {thuc_the.Layer for thuc_the in _duyet_modelspace(doc)})


def lop_khong_hop_le_com(doc: Any) -> list[str]:
    """Layer nào trong bản vẽ KHÔNG nằm trong quy ước mục 10.7.2 — phải rỗng
    khi bản vẽ đạt. (Ngược lại — layer hợp lệ mà KHÔNG có thực thể nào dùng
    tới, vd HATCH/HIDDEN/BREAK ở 1 mặt cắt đơn giản không cần gạch mặt cắt —
    KHÔNG phải lỗi, layer đó chỉ đơn giản chưa cần dùng tới.)"""
    hop_le = {lp.ten for lp in layers_module.TAT_CA_LAYER}
    return sorted(l for l in doc_lop_su_dung_com(doc) if l not in hop_le)


def doc_noi_dung_text_com(doc: Any, layer: str | None = None) -> list[str]:
    """Nội dung mọi text đơn dòng (AcDbText, do `backend_com._ve_1_chu` tạo
    qua `AddText`) trong ModelSpace, lọc theo layer nếu có truyền. Bọc qua
    `_thu_lai_khi_com_ban` — xem lý do ở `doc_lop_su_dung_com`."""
    return _thu_lai_khi_com_ban(lambda: [
        _ep_kieu(thuc_the, "IAcadText").TextString
        for thuc_the in _duyet_modelspace(doc)
        if thuc_the.ObjectName == _OBJECTNAME_TEXT and (layer is None or thuc_the.Layer == layer)
    ])


def kiem_tra_nhan_mat_cat_day_du_com(doc: Any, nhan_ky_vong: list[str]) -> list[str]:
    """Trả về danh sách nhãn mặt cắt (vd "I-I", "II-II") CÒN THIẾU trong bản
    vẽ — dùng để kiểm tra đúng SỐ LƯỢNG mặt cắt bắt buộc theo loại cấu kiện
    (mục 3.8 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md: cột 1 mặt cắt, dầm thường 3,
    dầm công-xôn 1)."""
    text_hien_co = set(doc_noi_dung_text_com(doc, layer=layers_module.TEXT.ten))
    return [n for n in nhan_ky_vong if n not in text_hien_co]


def _ep_kieu(thuc_the: Any, ten_interface: str) -> Any:
    """CastTo sang `ten_interface` nếu khả dụng — LỖI THẬT đã gặp khi chạy
    thật: `doc.ModelSpace` (early-bound qua `_nang_cap_early_bound`) là 1
    collection DỊ KIỂU (nhiều loại thực thể khác nhau), nên win32com trả về
    mỗi phần tử ở giao diện CHUNG `IAcadEntity` (dù `ObjectName` đã đúng là
    loại cụ thể, vd "AcDbPolyline") — `IAcadEntity` không khai báo các thuộc
    tính riêng của từng loại (`.Coordinates` chỉ có ở `IAcadLWPolyline`,
    `.TextString` chỉ có ở `IAcadText`), gây lỗi "IAcadEntity không có thuộc
    tính ..." ngay khi đọc, KHÔNG PHẢI lỗi COM bận thoáng qua (retry vô ích).
    Fallback về nguyên thực thể nếu CastTo lỗi/không có (vd thực thể giả
    trong test, hoặc môi trường dynamic dispatch vốn không cần CastTo) — vẫn
    hoạt động đúng như trước vì đối tượng giả/dynamic đã có sẵn thuộc tính đó."""
    try:
        import win32com.client

        da_ep = win32com.client.CastTo(thuc_the, ten_interface)
        return da_ep if da_ep is not None else thuc_the
    except Exception:
        return thuc_the


def hop_gioi_han_da_giac_com(doc: Any, layer: str) -> list[HopGioiHan]:
    """Hộp giới hạn của mọi đa giác (AcDbPolyline) trên 1 layer — đọc
    `.Coordinates` (mảng phẳng x0,y0,x1,y1,... do COM trả về, ghép cặp lại ở
    đây) để tính min/max, tương đương `hop_gioi_han_da_giac_ir` nhưng đọc từ
    bản vẽ THẬT thay vì IR."""
    def _doc() -> list[HopGioiHan]:
        ket_qua: list[HopGioiHan] = []
        for thuc_the in _duyet_modelspace(doc):
            if thuc_the.ObjectName != _OBJECTNAME_POLYLINE or thuc_the.Layer != layer:
                continue
            toa_do_phang = list(_ep_kieu(thuc_the, "IAcadLWPolyline").Coordinates)
            if len(toa_do_phang) < 2:
                continue
            xs = toa_do_phang[0::2]
            ys = toa_do_phang[1::2]
            ket_qua.append(HopGioiHan(min(xs), min(ys), max(xs), max(ys)))
        return ket_qua

    return _thu_lai_khi_com_ban(_doc)


def khop_kich_thuoc_nao_do(
    danh_sach_hop: list[HopGioiHan], rong_ky_vong: float, cao_ky_vong: float, dung_sai_mm: float = 1.0
) -> bool:
    """Backend-agnostic — nhận sẵn `list[HopGioiHan]` (từ mức IR hoặc mức COM
    đều gọi hàm này được), không tự đọc bất kỳ đâu."""
    return any(
        abs(h.rong - rong_ky_vong) <= dung_sai_mm and abs(h.cao - cao_ky_vong) <= dung_sai_mm
        for h in danh_sach_hop
    )


# ---------------------------------------------------------------------------
# Kiểm tra MỞ RỘNG cho bản vẽ TỔNG THỂ (mặt đứng khung đã lắp ráp) — trước
# đây CHƯA có (docs/agents/VERIFICATION_AGENT.md mục 2, CHANGE_REQUESTS mục
# 2): số cấu kiện, vòng tròn ký hiệu trục, nhãn thép đủ mọi vị trí/dầm, bảng
# thống kê đủ 8 cột.
# ---------------------------------------------------------------------------


def dem_da_giac_theo_layer_com(doc: Any, layer: str) -> int:
    """Đếm số đa giác (AcDbPolyline) trên 1 layer — dùng đếm số cấu kiện
    (cột/dầm) đã vẽ trên layer OUTLINE ở mặt đứng khung, so với số phần tử
    Rule Engine Agent đã xử lý (không thiếu, không thừa)."""
    return _thu_lai_khi_com_ban(lambda: sum(
        1 for t in _duyet_modelspace(doc) if t.ObjectName == _OBJECTNAME_POLYLINE and t.Layer == layer
    ))


def dem_vong_tron_theo_layer_com(doc: Any, layer: str) -> int:
    """Đếm số vòng tròn (AcDbCircle) trên 1 layer — dùng đếm số "bong bóng
    ký hiệu trục" (layer AXIS) ở mặt đứng khung, mục 2.4
    KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md — phải khớp đúng số trục."""
    return _thu_lai_khi_com_ban(lambda: sum(1 for t in _duyet_modelspace(doc) if t.ObjectName == _OBJECTNAME_CIRCLE and t.Layer == layer))


def kiem_tra_nhan_thep_du_vi_tri_com(doc: Any, ten_phan_tu: str, vi_tri_ky_vong: list[str]) -> list[str]:
    """Với 1 dầm cụ thể, kiểm tra nhãn thép gộp trên mặt đứng khung (layer
    TEXT, do `khung_ve.lap_rap_mat_dung_khung` gộp) có nhắc tới CẢ 3 vị trí
    kỳ vọng hay không — đúng hồi quy cho lỗi thật đã gặp: nhãn từng bị GHI ĐÈ
    chỉ còn giữ 1 vị trí cuối cùng (xem docs/CHANGE_REQUESTS.md mục 3). Tìm
    trong TOÀN BỘ text trên layer TEXT có chứa `ten_phan_tu` (không chỉ đúng
    1 dòng — nhãn cấu kiện có thể tách thành nhiều dòng/nhiều đối tượng text
    tuỳ cách Drawing Agent bố trí), rồi kiểm tra từng vi_tri kỳ vọng có xuất
    hiện ở ĐÂU ĐÓ trong các dòng đó không.

    Trả về danh sách vi_tri CÒN THIẾU (rỗng = đạt)."""
    cac_dong_lien_quan = [
        dong for dong in doc_noi_dung_text_com(doc, layer=layers_module.TEXT.ten) if ten_phan_tu in dong
    ]
    noi_dung_gop = " ".join(cac_dong_lien_quan)
    return [vt for vt in vi_tri_ky_vong if vt not in noi_dung_gop]


_TIEU_DE_BANG_THONG_KE_8_COT = ["CẤU KIỆN", "SỐ HIỆU", "HÌNH DÁNG", "Ø(mm)", "DÀI 1CK(mm)", "SL", "TỔNG DÀI(m)", "K.LƯỢNG(kG)"]


def kiem_tra_bang_thong_ke_du_cot_com(doc: Any) -> list[str]:
    """Kiểm tra bảng thống kê thép (layer TEXT) có đủ 8 tiêu đề cột đúng mục
    3.9 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md hay không (`geometry.ve_bang_thong_ke`
    luôn vẽ đúng 8 tiêu đề này — hàm ở đây xác nhận lại trên bản vẽ THẬT,
    phòng trường hợp Drawing Agent gọi sai tham số/dùng phiên bản cũ)."""
    text_hien_co = set(doc_noi_dung_text_com(doc, layer=layers_module.TEXT.ten))
    return [t for t in _TIEU_DE_BANG_THONG_KE_8_COT if t not in text_hien_co]
