"""
Khai báo layer/nét theo RULES_TCVN5574.md mục 10.7.2 — bảng quy ước đường nét
theo chức năng thể hiện. MỖI layer ứng với ĐÚNG 1 chức năng thể hiện trong
bảng đó — không gộp chung nhiều chức năng vào 1 layer/1 kiểu nét (yêu cầu bắt
buộc của đồ án).

Module này KHÔNG phụ thuộc pywin32 — chỉ định nghĩa dữ liệu thuần, để
`backend_com.py` và `verify_drawing.py` cùng dùng chung 1 nguồn quy ước (vẽ
và kiểm chứng luôn khớp đúng cùng 1 danh sách layer hợp lệ).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DinhNghiaLayer:
    ten: str
    mo_ta: str  # đúng tên trong bảng mục 10.7.2
    mau_acad: int  # chỉ số màu ACI (AutoCAD Color Index) — dùng cho cả DXF và COM
    kieu_net: str  # tên kiểu nét chuẩn AutoCAD (Continuous/Dashed/Center/...)
    do_day_net_mm: float  # lineweight (mm) — 0 = mặc định theo layer


# Bề dày nét — SỬA theo KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md mục 1.2 (TCVN
# 4612-88, nguồn RIÊNG cho bản vẽ bố trí cốt thép — override quy ước nét
# CHUNG của RULES_TCVN5574.md mục 10.7.2, vốn xếp OUTLINE_CUT "rất đậm" nhất
# — 2 tài liệu MÂU THUẪN NHAU, đã đối chiếu trực tiếp với bản vẽ mẫu thật
# `data/samples/BoTriThep_KhungTruc5_mau.pdf` để xác nhận TCVN 4612-88 đúng).
#
# Nguyên tắc gốc (nguyên văn KY_HIEU mục 1.2): "bê tông trên hình chiếu chính
# và trên mặt cắt được coi là TRONG SUỐT, để cốt thép bên trong nổi bật lên
# — NGƯỢC LẠI với cảm giác thông thường". Vì vậy: đường bao BÊ TÔNG (cả mặt
# đứng lẫn mặt cắt) phải MẢNH NHẤT, còn CỐT THÉP DỌC mới là nét ĐẬM NHẤT.
_DAM_THEP_DOC = 0.50  # s (hoặc 2s) — cốt thép chịu lực (dọc chính), ĐẬM NHẤT bản vẽ
_DAM_THEP_DAI = 0.35  # s/2 (hoặc s) — cốt đai/cốt phân bố/cấu tạo, đậm nhưng nhẹ hơn thép dọc
_MANH_BETONG = 0.18  # s/3 — đường bao cấu kiện bê tông (hình chiếu chính LẪN mặt cắt), MẢNH NHẤT
_MANH = 0.18  # nét mảnh dùng chung cho kích thước/hatch/text/trục (không đổi)

# Màu ACI (AutoCAD Color Index) — SỬA theo phản hồi trực tiếp người dùng +
# đối chiếu ảnh chụp thật `KC.HIEP.dwg` (bản vẽ kết cấu thật, thấy rõ đỏ/
# vàng/xanh lá/trắng tách biệt từng loại nét): "nét vẽ thì mỗi cái một màu
# cho dễ nhìn" — ĐẢO LẠI quyết định trước đó (gộp về 2-3 màu vì "đỡ rối") —
# TCVN không quy định màu (chỉ quy định LOẠI NÉT, mục 1.1 KY_HIEU), nhưng
# thực hành CAD thật rõ ràng phân biệt màu theo TỪNG Ý NGHĨA layer, không
# gộp chung. Mỗi Ý NGHĨA (không phải mỗi layer) 1 màu riêng — OUTLINE và
# OUTLINE_CUT CÙNG màu vì cùng là "đường bao bê tông", chỉ khác mặt đứng/mặt
# cắt.
_MAU_BETONG = 7  # trắng/đen tự đảo theo nền — OUTLINE, OUTLINE_CUT, TEXT
_MAU_THEP_DOC = 1  # đỏ — cốt thép dọc chịu lực (REBAR_MAIN), quy ước phổ biến thép chính = đỏ
_MAU_THEP_DAI = 2  # vàng — cốt đai (REBAR_STIRRUP), khớp ảnh KC.HIEP.dwg
_MAU_SO_HIEU = 3  # xanh lá — vòng tròn số hiệu + đường dẫn (SO_HIEU), khớp ảnh KC.HIEP.dwg
_MAU_KICH_THUOC = 4  # cyan — đường kích thước (DIM)
_MAU_TRUC = 6  # magenta — trục lưới (AXIS), tách khỏi DIM (trước đây gộp chung cyan)
_MAU_HATCH = 8  # xám đậm — gạch mặt cắt bê tông (HATCH)
_MAU_KHUAT = 9  # xám nhạt — nét khuất (HIDDEN), tách khỏi HATCH
_MAU_CAT_ROI = 5  # xanh dương — nét cắt rời khi vẽ rút ngắn (BREAK)

OUTLINE_CUT = DinhNghiaLayer(
    "OUTLINE_CUT",
    "Đường bao mặt cắt bê tông tại đúng vị trí bị cắt qua (contour tiết diện dầm/cột trên mặt cắt ngang)",
    mau_acad=_MAU_BETONG, kieu_net="Continuous", do_day_net_mm=_MANH_BETONG,
)
OUTLINE = DinhNghiaLayer(
    "OUTLINE",
    "Đường bao cấu kiện nhìn thấy được (mép ngoài dầm/cột trên mặt đứng khung, mặt bằng)",
    mau_acad=_MAU_BETONG, kieu_net="Continuous", do_day_net_mm=_MANH_BETONG,
)
REBAR_MAIN = DinhNghiaLayer(
    "REBAR_MAIN",
    "Tiết diện thật cốt thép dọc (vòng tròn đặc, nhìn dọc trục) trên mặt cắt ngang — mục 1.2 KY_HIEU (đậm nhất bản vẽ)",
    mau_acad=_MAU_THEP_DOC, kieu_net="Continuous", do_day_net_mm=_DAM_THEP_DOC,
)
SO_HIEU = DinhNghiaLayer(
    "SO_HIEU",
    "Ký hiệu SỐ HIỆU thanh thép (vòng tròn Ø7-10mm + đường dẫn) — mục 2.2 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.pdf",
    # TÁCH RIÊNG khỏi REBAR_MAIN — LỖI THẬT đã gặp: REBAR_MAIN trước đây
    # kiêm 2 vai trò mâu thuẫn nhau — (a) vòng tròn tiết diện thanh thép
    # THẬT trên mặt cắt (mục 1.2: "cốt thép dọc = đậm NHẤT"), (b) vòng tròn
    # SỐ HIỆU chú thích (mục 2.2 ghi rõ NGUYÊN VĂN: "đánh số hiệu trong một
    # vòng tròn... nét liền MẢNH" — ngược hẳn (a)). Dùng chung 1 layer/1 độ
    # đậm cho 2 vai trò khác nhau này là sai — tách SO_HIEU (mảnh, cùng
    # nhóm TEXT/DIM) riêng khỏi REBAR_MAIN (đậm nhất, chỉ còn nghĩa (a)).
    mau_acad=_MAU_SO_HIEU, kieu_net="Continuous", do_day_net_mm=_MANH,
)
REBAR_STIRRUP = DinhNghiaLayer(
    "REBAR_STIRRUP",
    "Cốt đai — nổi bật hơn nét kích thước",
    mau_acad=_MAU_THEP_DAI, kieu_net="Continuous", do_day_net_mm=_DAM_THEP_DAI,
)
DIM = DinhNghiaLayer(
    "DIM",
    "Đường kích thước (dimension)",
    mau_acad=_MAU_KICH_THUOC, kieu_net="Continuous", do_day_net_mm=_MANH,
)
HATCH = DinhNghiaLayer(
    "HATCH",
    "Đường gạch mặt cắt bê tông (hatch)",
    mau_acad=_MAU_HATCH, kieu_net="Continuous", do_day_net_mm=_MANH,
)
TEXT = DinhNghiaLayer(
    "TEXT",
    "Đường dẫn/ghi chú (leader), khung bảng thống kê, chữ",
    mau_acad=_MAU_BETONG, kieu_net="Continuous", do_day_net_mm=_MANH,
)
HIDDEN = DinhNghiaLayer(
    "HIDDEN",
    "Cấu kiện/chi tiết bị khuất — nằm phía sau hoặc ẩn trong cấu kiện khác",
    mau_acad=_MAU_KHUAT, kieu_net="Dashed", do_day_net_mm=_MANH,
)
AXIS = DinhNghiaLayer(
    "AXIS",
    "Đường tim trục lưới (cột, dầm), đường tâm đối xứng của tiết diện",
    mau_acad=_MAU_TRUC, kieu_net="Center", do_day_net_mm=_MANH,
)
BREAK = DinhNghiaLayer(
    "BREAK",
    "Giới hạn chỗ cắt rời một cấu kiện dài (dầm/cột) khi vẽ rút ngắn",
    mau_acad=_MAU_CAT_ROI, kieu_net="Continuous", do_day_net_mm=_MANH,  # lượn sóng vẽ bằng polyline, không phải linetype riêng
)

TAT_CA_LAYER: tuple[DinhNghiaLayer, ...] = (
    OUTLINE_CUT, OUTLINE, REBAR_MAIN, REBAR_STIRRUP, SO_HIEU, DIM, HATCH, TEXT, HIDDEN, AXIS, BREAK,
)

_THEO_TEN: dict[str, DinhNghiaLayer] = {lp.ten: lp for lp in TAT_CA_LAYER}


def tra_layer(ten: str) -> DinhNghiaLayer:
    if ten not in _THEO_TEN:
        raise ValueError(f"Layer '{ten}' không nằm trong quy ước mục 10.7.2 (hỗ trợ: {sorted(_THEO_TEN)}).")
    return _THEO_TEN[ten]
