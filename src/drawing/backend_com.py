"""
Backend DUY NHẤT — vẽ trực tiếp lên AutoCAD đang chạy, qua COM Automation
(pywin32). TONGQUAN_AI_AGENT.md mục 4/7: "vẽ AutoCAD 100% qua backend_com.py
(COM Automation)". Nhận `BanVe` (IR, từ `geometry.py`) — tách biệt hoàn toàn
khỏi logic hình học, chỉ lo phần "vẽ ra đâu" (gọi AutoCAD thật qua COM).

Yêu cầu môi trường: máy đã cài AutoCAD (đã xác nhận trên máy này: AutoCAD
2024, ProgID COM "AutoCAD.Application.24"). `ket_noi_autocad()` sẽ thử gắn
vào tiến trình AutoCAD ĐANG MỞ trước; nếu không có, COM tự khởi động 1 tiến
trình mới (mất vài giây, và có thể bị chặn bởi hộp thoại lần đầu chạy —
nên MỞ SẴN AutoCAD và đóng hết hộp thoại trước khi gọi module này).

Module này chỉ import `win32com.client`/`pythoncom` BÊN TRONG từng hàm (không
ở đầu file) để vẫn import được trên môi trường chưa cài pywin32 hoặc không
phải Windows — khớp cách làm đã dùng cho `anthropic` ở llm_mapping.py.
"""

from __future__ import annotations

import math
import time
from typing import Any, Callable, TypeVar

from . import layers
from .geometry import BanVe

_T = TypeVar("_T")
_RPC_E_CALL_REJECTED = -2147418111  # "Call was rejected by callee." — AutoCAD bận, lỗi TẠM THỜI.


def _thu_lai_khi_com_ban(ham: Callable[[], _T], so_lan_toi_da: int = 15, cho_giay: float = 0.3) -> _T:
    """Gọi 1 hàm COM AutoCAD, tự thử lại khi gặp lỗi thoáng qua "Call was
    rejected by callee" (RPC_E_CALL_REJECTED) — lỗi COM RẤT PHỔ BIẾN ngay sau
    khi tạo Document mới hoặc khi AutoCAD còn đang bận vẽ/refresh UI, KHÔNG
    phải lỗi logic của code. Lỗi COM khác (thật sự sai) vẫn raise ngay, không
    nuốt lỗi mù quáng — đã xác nhận qua smoke test thật trên máy này."""
    import pywintypes

    loi_cuoi: Exception | None = None
    for _ in range(so_lan_toi_da):
        try:
            return ham()
        except pywintypes.com_error as e:
            if e.args[0] != _RPC_E_CALL_REJECTED:
                raise
            loi_cuoi = e
            time.sleep(cho_giay)
    assert loi_cuoi is not None
    raise loi_cuoi

# AutoCAD COM không nhận số thực mm tuỳ ý cho Lineweight như ezdxf — chỉ có 1
# tập giá trị enum rời rạc (AcLineWeight, đơn vị 1/100mm theo đúng bội số cố
# định của AutoCAD). Ánh xạ về giá trị enum gần nhất với do_day_net_mm khai
# báo trong layers.py.
_ACAD_LINEWEIGHT_ENUM_MM = {0.00: 0, 0.13: 13, 0.18: 18, 0.25: 25, 0.35: 35, 0.50: 50, 0.70: 70, 1.00: 100}


def _lineweight_gan_nhat(mm: float) -> int:
    gia_tri_mm = min(_ACAD_LINEWEIGHT_ENUM_MM, key=lambda k: abs(k - mm))
    return _ACAD_LINEWEIGHT_ENUM_MM[gia_tri_mm]


def _nang_cap_early_bound(doi_tuong: Any) -> Any:
    """Bọc lại 1 đối tượng COM (Application, hoặc kết quả `GetActiveObject`)
    qua `win32com.client.gencache.EnsureDispatch` — chuyển từ DYNAMIC dispatch
    (late-bound thuần, tự dò tên thuộc tính lúc chạy) sang EARLY-bound (build/
    cache sẵn wrapper Python từ type library thật của AutoCAD, qua makepy).

    LÝ DO BẮT BUỘC (lỗi thật đã gặp khi chạy `scripts/chay_pipeline_day_du.py`
    trên máy người dùng): dùng thẳng `win32com.client.Dispatch(...)`/
    `GetActiveObject(...)` (dynamic dispatch), các đối tượng CON trả về từ 1
    lệnh gọi (vd `app.Documents.Add()`) đôi khi không tự có đủ thông tin kiểu
    (`ITypeInfo`) để pywin32 dò đúng tên thuộc tính — `doc.Layers` bị báo
    `AttributeError: Add.Layers` dù `Layers` là thuộc tính CÓ THẬT của
    Document (tên "Add" ở đây chỉ là pywin32 tự đặt theo tên lệnh gọi ra nó
    khi không dò được kiểu thật, không phải dấu hiệu gọi sai lệnh). Bọc qua
    `EnsureDispatch` khiến MỌI đối tượng con trả về sau đó (Documents, Layers,
    Linetypes, ModelSpace...) đều được wrap bằng đúng lớp Python sinh từ type
    library AutoCAD thật — hết lỗi dò thuộc tính kiểu này. Đây là kỹ thuật
    tiêu chuẩn cho lớp lỗi này (KHÔNG suy đoán, đã đọc trực tiếp mã nguồn
    `win32com.client.gencache.EnsureDispatch`/`win32com.client.Dispatch` cài
    trên máy để xác nhận đối số đầu vào chấp nhận CẢ chuỗi ProgID lẫn 1 đối
    tượng COM đã kết nối sẵn — dùng được cho cả 2 nhánh của `ket_noi_autocad`).

    Có fallback về nguyên `doi_tuong` (dynamic) nếu `EnsureDispatch` lỗi (vd
    môi trường không ghi được cache `gen_py`) — vẫn CÓ THỂ chạy được (dynamic
    dispatch vẫn đúng với đa số thuộc tính/lệnh, chỉ 1 số đối tượng con hiếm
    gặp mới lộ lỗi như trên), không để 1 lỗi phụ chặn đứng toàn bộ kết nối."""
    import win32com.client.gencache

    try:
        return win32com.client.gencache.EnsureDispatch(doi_tuong)
    except Exception:
        return doi_tuong


def ket_noi_autocad(khoi_dong_moi: bool = False) -> Any:
    """Kết nối AutoCAD đang chạy (GetActiveObject) hoặc khởi động tiến trình
    mới (Dispatch) nếu chưa có/khoi_dong_moi=True. Trả về đối tượng
    Application đã nâng cấp EARLY-bound (xem `_nang_cap_early_bound`)."""
    import win32com.client

    if not khoi_dong_moi:
        try:
            return _nang_cap_early_bound(win32com.client.GetActiveObject("AutoCAD.Application"))
        except Exception:
            pass
    app = _nang_cap_early_bound(win32com.client.Dispatch("AutoCAD.Application"))
    app.Visible = True
    return app


def tao_ban_ve_moi(app: Any) -> Any:
    """Mở 1 Document mới trong AutoCAD, khai báo đủ layer theo layers.py + cấu
    hình font chữ hỗ trợ tiếng Việt có dấu TRƯỚC khi vẽ bất kỳ chữ nào."""
    doc = app.Documents.Add()
    time.sleep(0.5)  # AutoCAD còn đang bận khởi tạo UI cho document mới — giảm số lần phải thử lại bên dưới
    khai_bao_layer(doc)
    _cau_hinh_font_tieng_viet(doc)
    return doc


def _cau_hinh_font_tieng_viet(doc: Any) -> None:
    """Chuyển text style 'Standard' (mặc định MỌI AcDbText/AddText tạo ra
    dùng, trừ khi chỉ định khác) sang font TrueType hỗ trợ dấu tiếng Việt.

    LỖI THẬT đã gặp: font mặc định của style 'Standard' là 'txt.shx' (SHX
    shape font đời cũ) — CHỈ có glyph ASCII, không có glyph cho ký tự có dấu
    tiếng Việt (đ, ă, ơ, ư, các dấu thanh...). Text vẫn LƯU ĐÚNG chuỗi Unicode
    (đọc lại `.TextString` ra đúng "đều", "cạnh"...) nhưng khi VẼ/XUẤT PDF,
    AutoCAD không tìm được glyph tương ứng trong txt.shx nên hiển thị "?" —
    đây là lỗi HIỂN THỊ/FONT, không phải lỗi lưu trữ chuỗi.

    QUAN TRỌNG: phải gọi hàm này TRƯỚC khi vẽ chữ nào (ngay sau tạo Document)
    — thử đổi font style SAU KHI đã vẽ xong (trên Document đã có sẵn text)
    KHÔNG có tác dụng lên PDF xuất ra (đã xác nhận qua debug trực tiếp: đổi
    font rồi export lại, PDF vẫn hiển thị "?" y hệt) — khả năng cao do
    AutoCAD dùng bảng ánh xạ font riêng lúc Plot (font substitution), không
    re-render theo style mới một cách đáng tin cậy qua COM sau khi đã vẽ.

    163 = VIETNAMESE_CHARSET (Windows GDI LOGFONT.lfCharSet, tra cứu
    learn.microsoft.com/windows/win32/api/wingdi/ns-wingdi-logfonta — KHÔNG
    đoán số). 34 = PitchAndFamily (DEFAULT_PITCH=0 OR FF_SWISS=32 -> 0|32=32,
    +2 cho TRUETYPE_FONTTYPE theo mẫu SetFont chuẩn của AutoCAD ActiveX)."""
    try:
        kieu = doc.TextStyles.Item("Standard")
        kieu.SetFont("Arial", False, False, 163, 34)
        doc.ActiveTextStyle = kieu
    except Exception:
        pass  # không chặn cả pipeline chỉ vì lỗi font — vẽ vẫn tiếp tục, chỉ mất dấu tiếng Việt


def _cau_hinh_1_layer(doc: Any, lp: layers.DinhNghiaLayer) -> None:
    try:
        layer = doc.Layers.Item(lp.ten)
    except Exception:
        layer = doc.Layers.Add(lp.ten)
    layer.color = lp.mau_acad
    layer.Lineweight = _lineweight_gan_nhat(lp.do_day_net_mm)
    if lp.kieu_net != "Continuous":
        try:
            doc.Linetypes.Load(lp.kieu_net, "acadiso.lin")
        except Exception:
            pass  # linetype có thể đã nạp sẵn từ template — bỏ qua lỗi trùng
        try:
            layer.Linetype = lp.kieu_net
        except Exception:
            pass


def khai_bao_layer(doc: Any) -> None:
    for lp in layers.TAT_CA_LAYER:
        _thu_lai_khi_com_ban(lambda lp=lp: _cau_hinh_1_layer(doc, lp))


def _mang_diem(*toa_do: float):
    """Bọc 1 danh sách toạ độ phẳng (x1,y1,z1,x2,y2,z2,...) thành SAFEARRAY
    kiểu VT_R8 mà COM AutoCAD yêu cầu cho các tham số điểm/mảng điểm."""
    import pythoncom
    from win32com.client import VARIANT

    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(toa_do))


def _mang_diem_2d(x: float, y: float):
    """Điểm 2D (x,y) — KHÁC `_mang_diem` (luôn 3D x,y,z): 1 số phương thức
    COM của AutoCAD (vd `Layout.SetWindowToPlot`) đòi hỏi ĐÚNG 2 phần tử,
    truyền mảng 3 phần tử (kể cả z=0.0) sẽ báo lỗi COM "Incorrect number of
    elements in SafeArray" — lỗi thật đã gặp khi viết `xuat_pdf`."""
    import pythoncom
    from win32com.client import VARIANT

    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y])


def _ve_1_doan_thang(msp: Any, dt) -> None:
    e = msp.AddLine(_mang_diem(dt.p1.x, dt.p1.y, 0.0), _mang_diem(dt.p2.x, dt.p2.y, 0.0))
    e.Layer = dt.layer


def _ve_1_da_giac(msp: Any, dg) -> None:
    toa_do: list[float] = []
    for d in dg.diem:
        toa_do += [d.x, d.y]
    e = msp.AddLightWeightPolyline(_mang_diem(*toa_do))
    e.Closed = dg.dong
    e.Layer = dg.layer
    # Độ rộng hình học thật — cùng lý do với backend_dxf.py (const_width):
    # lineweight của layer thường bị tắt hiển thị mặc định ở Model Space.
    if getattr(dg, "do_rong_net", 0) > 0:
        e.ConstantWidth = dg.do_rong_net


def _ve_1_vong_tron(msp: Any, vt) -> None:
    e = msp.AddCircle(_mang_diem(vt.tam.x, vt.tam.y, 0.0), vt.ban_kinh)
    e.Layer = vt.layer


def _ve_1_cung(msp: Any, cg) -> None:
    # AutoCAD COM AddArc nhận góc bằng RADIAN (khác ezdxf dùng độ), đo ngược
    # kim đồng hồ từ trục X dương — cùng quy ước chiều với goc_bat_dau_do/
    # goc_ket_thuc_do của VeCung nên chỉ cần đổi đơn vị, không đổi chiều.
    goc_dau_rad = math.radians(cg.goc_bat_dau_do)
    goc_cuoi_rad = math.radians(cg.goc_ket_thuc_do)
    e = msp.AddArc(_mang_diem(cg.tam.x, cg.tam.y, 0.0), cg.ban_kinh, goc_dau_rad, goc_cuoi_rad)
    e.Layer = cg.layer


def _ve_1_chu(msp: Any, c) -> None:
    e = msp.AddText(c.noi_dung, _mang_diem(c.vi_tri.x, c.vi_tri.y, 0.0), c.chieu_cao)
    e.Layer = c.layer
    if c.canh_giua:
        e.Alignment = 4  # acAlignmentMiddleCenter (AcAlignment enum COM)
        e.TextAlignmentPoint = _mang_diem(c.vi_tri.x, c.vi_tri.y, 0.0)
    elif getattr(c, "canh_phai", False):
        e.Alignment = 2  # acAlignmentRight (AcAlignment enum COM)
        e.TextAlignmentPoint = _mang_diem(c.vi_tri.x, c.vi_tri.y, 0.0)


def _ve_1_kich_thuoc(msp: Any, kt) -> None:
    la_ngang = kt.p1.y == kt.p2.y
    if la_ngang:
        diem_dim = _mang_diem(kt.p1.x, kt.p1.y - kt.khoang_offset - 15, 0.0)
    else:
        diem_dim = _mang_diem(kt.p1.x - kt.khoang_offset - 15, kt.p1.y, 0.0)
    e = msp.AddDimAligned(_mang_diem(kt.p1.x, kt.p1.y, 0.0), _mang_diem(kt.p2.x, kt.p2.y, 0.0), diem_dim)
    e.Layer = kt.layer
    # Dimstyle mặc định của template AutoCAD thường có cỡ chữ/mũi tên quá nhỏ
    # so với tỷ lệ bản vẽ tính bằng mm của cấu kiện (250-700mm) — ghi đè trực
    # tiếp trên từng đối tượng để khớp cỡ chữ ghi chú khác trong cùng bản vẽ
    # (mục 10.7), tương tự override đã áp ở backend_dxf.py.
    try:
        e.TextHeight = kt.co_chu
        e.ArrowheadSize = kt.co_chu * 8 / 15
        e.ExtensionLineExtend = kt.co_chu * 5 / 15
        e.ExtensionLineOffset = kt.co_chu * 3 / 15
        # Ép HIỆN đường dóng (extension line) cả 2 đầu — LỖI THẬT đã gặp:
        # người dùng phản hồi trực tiếp "nét dóng đâu rồi" khi xem bản vẽ
        # thật. Trước đây chỉ chỉnh ĐỘ DÀI đường dóng (ExtensionLineExtend/
        # Offset), không ép rõ trạng thái BẬT — nếu DIMSTYLE mặc định của
        # template AutoCAD đang dùng có sẵn cờ ẩn đường dóng (SuppressExtLine1/2
        # = True, khá phổ biến ở 1 số dimstyle kiến trúc có sẵn), mọi chỉnh
        # độ dài phía trên vô nghĩa vì đường dóng không hiện ra ngay từ đầu.
        e.SuppressExtLine1 = False
        e.SuppressExtLine2 = False
        # Mũi tên kích thước GẠCH CHÉO 45° kiểu kiến trúc/xây dựng (đúng quy
        # ước mục 10.7 + KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md, cùng hiệu ứng
        # "_ARCHTICK" của backend DXF trước đây) thay vì mũi tên đóng kiểu cơ
        # khí mặc định — enum AcDimArrowheadType.acArrowArchTick=4, TRA CỨU
        # trực tiếp AutoCAD ActiveX Reference chính thức (không đoán số, cùng
        # nguyên tắc đã áp dụng cho AcSaveAsType ở luu_file_dwg()). Đặt qua
        # ArrowheadType (gán CẢ 2 đầu mũi tên cùng lúc) — không dùng được
        # win32com.client.constants ở đây vì kết nối COM late-bound qua
        # ProgID, không có cache type-library sinh sẵn tên hằng số.
        e.ArrowheadType = 4
    except Exception:
        pass
    if kt.nhan is not None:
        e.TextOverride = kt.nhan


def ve_vao_doc(doc: Any, ban_ve: BanVe, dx: float = 0.0, dy: float = 0.0) -> None:
    """Vẽ 1 BanVe (IR) vào ModelSpace của Document AutoCAD đang mở.

    Mọi lệnh vẽ đều bọc qua `_thu_lai_khi_com_ban` — AutoCAD hay trả lỗi COM
    thoáng qua "Call was rejected by callee" khi đang bận vẽ/refresh, không
    phải lỗi hình học (đã xác nhận qua smoke test thật trên máy này)."""
    msp = doc.ModelSpace
    bv = ban_ve.dich_chuyen(dx, dy) if (dx or dy) else ban_ve

    for dt in bv.doan_thang:
        _thu_lai_khi_com_ban(lambda dt=dt: _ve_1_doan_thang(msp, dt))
    for dg in bv.da_giac:
        _thu_lai_khi_com_ban(lambda dg=dg: _ve_1_da_giac(msp, dg))
    for vt in bv.vong_tron:
        _thu_lai_khi_com_ban(lambda vt=vt: _ve_1_vong_tron(msp, vt))
    for cg in bv.cung:
        _thu_lai_khi_com_ban(lambda cg=cg: _ve_1_cung(msp, cg))
    for c in bv.chu:
        _thu_lai_khi_com_ban(lambda c=c: _ve_1_chu(msp, c))
    for kt in bv.kich_thuoc:
        _thu_lai_khi_com_ban(lambda kt=kt: _ve_1_kich_thuoc(msp, kt))


# AcActiveSpace/AcPlotType/AcPlotScale — TRA CỨU trực tiếp (không đoán số,
# cùng nguyên tắc "DWG_VERSION" ở dưới): đối chiếu tài liệu AutoCAD ActiveX
# Reference chính thức (help.autodesk.com, trang "PlotType Property"/
# "StandardScale Property") VÀ mã nguồn IDL gốc của ObjectARX
# (axtypes.idl — enum AcActiveSpace/AcPlotType/AcPlotScale) để lấy đúng giá
# trị nguyên (late-bound COM không có win32com.client.constants).
_AC_MODEL_SPACE = 1  # AcActiveSpace.acModelSpace (acPaperSpace=0, acModelSpace=1)
_AC_PLOT_TYPE_WINDOW = 4  # AcPlotType.acWindow — dùng SetWindowToPlot (xem lý do dưới, KHÔNG dùng acExtents=1)
_AC_PLOT_SCALE_TO_FIT = 0  # AcPlotScale.acScaleToFit — tự co giãn vừa khổ giấy, không cần biết trước toạ độ


def _hop_gioi_han_modelspace(doc: Any) -> tuple[float, float, float, float] | None:
    """Tự tính bounding box (min_x, min_y, max_x, max_y) của MỌI thực thể
    trong ModelSpace bằng `GetBoundingBox()` từng đối tượng — trả None nếu
    ModelSpace rỗng/không lấy được bbox từ bất kỳ đối tượng nào.

    Bỏ qua (không raise) đối tượng lỗi KHÔNG PHẢI do COM bận thoáng qua (vd
    1 số loại Dimension/Text thật sự không hỗ trợ GetBoundingBox) — nhưng lỗi
    "Call was rejected by callee" (COM bận) được TỰ THỬ LẠI qua
    `_thu_lai_khi_com_ban` trước khi bỏ qua. LỖI THẬT đã gặp (chạy thật, phiên
    vẽ dài ~hàng trăm thực thể + liên tục bị "Call was rejected by callee"
    xuyên suốt log): KHÔNG retry ở đây khiến PHẦN LỚN thực thể (gồm cả toàn
    bộ mặt đứng khung) bị bỏ qua do COM bận đúng lúc đọc bbox, bounding box
    tính ra chỉ còn dựa trên vài thực thể may mắn đọc được (vài mặt cắt mới
    vẽ gần cuối) — PDF xuất ra CẮT MẤT hẳn mặt đứng khung dù đã vẽ đúng, chỉ
    còn sót vài mặt cắt lọt vào khung nhìn sai."""
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    so_lay_duoc = 0
    for thuc_the in doc.ModelSpace:
        try:
            diem_duoi, diem_tren = _thu_lai_khi_com_ban(thuc_the.GetBoundingBox)
        except Exception:
            continue
        min_x, min_y = min(min_x, diem_duoi[0]), min(min_y, diem_duoi[1])
        max_x, max_y = max(max_x, diem_tren[0]), max(max_y, diem_tren[1])
        so_lay_duoc += 1
    if so_lay_duoc == 0:
        return None
    return min_x, min_y, max_x, max_y


def hop_gioi_han_modelspace(doc: Any) -> tuple[float, float, float, float] | None:
    """Wrapper CÔNG KHAI của `_hop_gioi_han_modelspace` — dùng ở nơi khác
    ngoài module này (vd `pipeline.py` cần biết vùng đã vẽ của mặt đứng khung
    để đặt mặt cắt an toàn bên dưới, xem `PhienCAD.y_mat_cat`)."""
    return _hop_gioi_han_modelspace(doc)


def xuat_pdf(doc: Any, duong_dan_pdf: str) -> None:
    """Xuất bản vẽ hiện tại ra PDF bằng AcadPlot.PlotToFile.

    LỖI THẬT #1 đã gặp (lần chạy live đầu tiên trên máy người dùng): bản đầu
    tiên chỉ gọi thẳng `doc.Plot.PlotToFile(...)` mà KHÔNG tự cấu hình layout
    — Document mới (`Documents.Add()`) mặc định active layout là 1 tờ PAPER
    SPACE (vd "Layout2") với khung nhìn (viewport) chưa trỏ tới vùng đã vẽ
    (mọi thực thể đều nằm trong ModelSpace) — PDF xuất ra chỉ có khung viền
    trang giấy, HOÀN TOÀN TRỐNG.

    LỖI THẬT #2 đã gặp (NGAY SAU khi sửa lỗi #1): chuyển sang Model Space +
    đặt `PlotType=acExtents` (kỳ vọng AutoCAD tự tính lại vùng bao hết mọi
    thực thể) — vẫn ra PDF TRỐNG. Xác nhận qua debug trực tiếp: gọi
    `layout.GetWindowToPlot()` sau khi plot vẫn trả về `((0,0),(0,0))` — tức
    `acExtents` KHÔNG tự trigger tính lại vùng bao khi gọi qua COM
    `PlotToFile` (khác hành vi UI tương tác "Plot > Extents" — đây LÀ vấn đề
    đã biết rộng rãi trong cộng đồng AutoCAD ActiveX, không phải lỗi logic ở
    đây). Sửa triệt để: TỰ tính bounding box thật bằng
    `_hop_gioi_han_modelspace()` (duyệt GetBoundingBox từng thực thể) rồi gọi
    `SetWindowToPlot(min, max)` + `PlotType=acWindow` — đã xác nhận bằng cách
    đọc lại PDF xuất ra THẤY ĐÚNG hình vẽ (không còn trống)."""

    def _xuat() -> None:
        # BACKGROUNDPLOT != 0 (mặc định AutoCAD hiện đại = 2, "bật cho cả
        # Plot lẫn Publish") khiến PlotToFile CHẠY NGẦM (bất đồng bộ) — COM
        # trả về NGAY LẬP TỨC dù file PDF CHƯA được ghi xong, gây race
        # condition: đọc lại file ngay sau PlotToFile có thể thấy CHƯA TỒN
        # TẠI dù không có lỗi nào được báo. LỖI THẬT đã gặp: script gọi
        # xuat_pdf() rồi kết thúc ngay (không có thao tác nào khác xen giữa
        # để "vô tình" chờ đủ lâu) -> file PDF không xuất hiện dù không có
        # exception. Ép về 0 (đồng bộ) TRƯỚC khi plot đảm bảo PlotToFile chỉ
        # trả về SAU KHI file đã ghi xong hẳn.
        doc.SetVariable("BACKGROUNDPLOT", 0)
        doc.ActiveSpace = _AC_MODEL_SPACE
        layout = doc.ActiveLayout
        layout.ConfigName = "DWG To PDF.pc3"
        # RefreshPlotDeviceInfo BẮT BUỘC sau khi đổi ConfigName — nếu không,
        # GetCanonicalMediaNames()/CanonicalMediaName vẫn trả về danh sách
        # của driver CŨ (gotcha đã biết rộng rãi trong cộng đồng AutoCAD
        # ActiveX, không riêng đồ án này).
        layout.RefreshPlotDeviceInfo()
        # Chọn khổ giấy TỪ danh sách driver THẬT SỰ hỗ trợ (không hardcode 1
        # chuỗi tên khổ giấy cố định — tên chính xác có thể khác nhau giữa
        # các máy/phiên bản AutoCAD) — ưu tiên khổ A3 (đủ lớn cho khung nhiều
        # cấu kiện), nếu không có thì lấy khổ đầu tiên driver hỗ trợ.
        ten_khay_giay = list(layout.GetCanonicalMediaNames())
        khay_a3 = next((t for t in ten_khay_giay if "A3" in t), None)
        layout.CanonicalMediaName = khay_a3 or ten_khay_giay[0]

        hop = _hop_gioi_han_modelspace(doc)
        if hop is not None:
            min_x, min_y, max_x, max_y = hop
            LE_AN_TOAN = 500.0  # mm — chừa lề quanh vùng vẽ, tránh cắt sát mép chữ/kích thước ngoài cùng
            # SetWindowToPlot nhận ĐIỂM 2D (x,y) — KHÁC `_mang_diem()` dùng
            # cho lệnh vẽ (3D x,y,z); truyền nhầm mảng 3 phần tử ở đây từng
            # gây lỗi COM "Incorrect number of elements in SafeArray".
            layout.SetWindowToPlot(
                _mang_diem_2d(min_x - LE_AN_TOAN, min_y - LE_AN_TOAN),
                _mang_diem_2d(max_x + LE_AN_TOAN, max_y + LE_AN_TOAN),
            )
            layout.PlotType = _AC_PLOT_TYPE_WINDOW
        # else: ModelSpace rỗng (không có gì để vẽ vùng in) — giữ nguyên
        # PlotType mặc định của layout, PlotToFile vẫn chạy nhưng có thể trống.
        layout.StandardScale = _AC_PLOT_SCALE_TO_FIT
        layout.CenterPlot = True
        doc.Plot.PlotToFile(duong_dan_pdf)

    _thu_lai_khi_com_ban(_xuat)


# AutoCAD COM SaveAs(FileName, SaveAsType) nhận SaveAsType là 1 SỐ NGUYÊN
# (enum AcSaveAsType của AutoCAD ActiveX), KHÔNG phải chuỗi — vì kết nối COM ở
# đây dùng late-binding qua ProgID (win32com.client.Dispatch, không chạy
# makepy/EnsureDispatch để sinh cache type-library), nên KHÔNG có sẵn
# win32com.client.constants.ac2018_dwg như khi lập trình VBA — phải tự khai
# đúng giá trị số nguyên. KHÔNG đoán số này — đã tra cứu trực tiếp tài liệu
# AutoCAD ActiveX Reference chính thức của Autodesk (help.autodesk.com,
# trang "SaveAs Method"/"SaveAsType Property") để lấy đúng giá trị, tránh lặp
# lại đúng lớp lỗi "tự bịa số liệu" đã từng xảy ra ở nơi khác trong đồ án (vd
# Rbt=1,22 sai cho B30 — xem docs/agents/RULE_ENGINE_AGENT.md).
#
# "2018" là mặc định vì đây là định dạng DWG hiện hành từ AutoCAD 2018 trở đi
# (chưa có định dạng DWG mới hơn tính đến các bản AutoCAD gần đây, bao gồm
# AutoCAD 2024 đã xác nhận cài trên máy này) — mở được ở hầu hết máy khác mà
# không cần lo phiên bản quá mới/quá cũ.
_ACAD_DWG_VERSION = {
    "2018": 64,  # ac2018_dwg
    "2013": 60,  # ac2013_dwg
    "2010": 48,  # ac2010_dwg
    "2007": 36,  # ac2007_dwg
    "2004": 24,  # ac2004_dwg
}


def luu_file_dwg(doc: Any, duong_dan_dwg: str, phien_ban: str = "2018") -> None:
    """Lưu Document đang mở thành file .dwg thật qua COM `SaveAs` —
    CHANGE_REQUESTS.md mục 2b (trước đây `backend_com.py` chỉ có `xuat_pdf`,
    chưa có cách xuất DWG). `phien_ban` là 1 khoá trong `_ACAD_DWG_VERSION`
    (mặc định "2018" — xem lý do chọn ở trên).

    Bọc qua `_thu_lai_khi_com_ban` như mọi lệnh COM khác trong module này —
    SaveAs cũng có thể gặp lỗi "Call was rejected by callee" thoáng qua nếu
    AutoCAD còn đang bận xử lý các lệnh vẽ vừa gọi trước đó."""
    if phien_ban not in _ACAD_DWG_VERSION:
        raise ValueError(f"phien_ban '{phien_ban}' không hợp lệ — chỉ chấp nhận: {sorted(_ACAD_DWG_VERSION)}")
    ma_phien_ban = _ACAD_DWG_VERSION[phien_ban]
    _thu_lai_khi_com_ban(lambda: doc.SaveAs(duong_dan_dwg, ma_phien_ban))
