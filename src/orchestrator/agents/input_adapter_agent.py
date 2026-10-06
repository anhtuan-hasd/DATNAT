"""Input Adapter Agent — 1 trong 4 agent LLM riêng biệt (CHANGE_REQUESTS.md
mục 1). Xem đầy đủ vai trò, quy trình, hợp đồng dữ liệu tại
`docs/agents/INPUT_ADAPTER_AGENT.md` — file đó là NGUỒN SỰ THẬT cho hành vi
mong muốn của agent này; `HE_THONG_PROMPT` dưới đây chỉ là bản rút gọn dịch
sang lời nhắc cho LLM, không lặp lại toàn bộ chi tiết.

Cấu trúc file (áp dụng THỐNG NHẤT cho cả 4 file agent — xem thêm
`docs/agents/*.md`):
1. `NguCanhInputAdapter` — state RIÊNG của agent này (không dùng chung với 3
   agent kia, theo đúng nguyên tắc "phạm vi trách nhiệm rõ ràng" đã bàn khi
   thiết kế kiến trúc).
2. 1 hàm Python THUẦN cho mỗi tool (nhận `NguCanhInputAdapter` + `dict` đầu
   vào từ LLM, trả `dict` — KHÔNG tính bất kỳ con số kỹ thuật nào, chỉ gọi lại
   đúng hàm đã có sẵn ở `src/input_adapter/`).
3. `DINH_NGHIA_TOOL`/`_HAM_THEO_TEN`/`tao_dispatch` — đúng khuôn Anthropic
   tool-use, y hệt cách `tools.py` cũ làm (không đổi format, chỉ thu hẹp
   phạm vi xuống đúng 6 tool của riêng agent này).
4. `HE_THONG_PROMPT` + `chay_input_adapter_agent()` — lắp ráp lại thành 1
   phiên `agent.chay_vong_lap_tool()` độc lập.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import pandas as pd

from ...input_adapter import adapter, heuristics, hinh_hoc, readers
from ...input_adapter.models import DonViLucGoc, LoaiCauKien
from .. import agent
from ..shared.hoi_nguoi_dung_tool import DINH_NGHIA_HOI_NGUOI_DUNG, hoi_nguoi_dung
from ..shared.hop_dong_du_lieu import BoDuLieuKhungChuanHoa, PhanTuChuanHoa, ViTriChuanHoa

HamHoiNguoiDung = Callable[[str, list[str] | None], str]


@dataclass
class NguCanhInputAdapter:
    """State riêng cho 1 lượt chạy Input Adapter Agent (1 file đầu vào).
    `sheets_da_doc` giữ DataFrame thô giữa các lượt gọi tool trong CÙNG 1
    phiên hội thoại — không lưu ở module-level để nhiều lượt chạy song song
    (nhiều người dùng khác nhau) không giẫm lên nhau, giống hệt lý do
    `NguCanhPipeline` cũ đã ghi."""

    hoi_nguoi_dung: HamHoiNguoiDung
    sheets_da_doc: dict[str, pd.DataFrame] | None = None
    phan_tu_da_chuan_hoa: list[dict[str, Any]] = field(default_factory=list)  # gom dần qua nhiều lần gọi chuan_hoa_du_lieu
    # Kết quả suy_luan_hinh_hoc LẦN GỌI THÀNH CÔNG GẦN NHẤT — lưu lại ở đây
    # (không chỉ trả cho LLM) để pipeline.py đọc lại CHẮC CHẮN qua
    # trich_bo_du_lieu_chuan_hoa(), không phải tự bóc tách từ log tự do.
    toa_do_truc: dict[str, float] = field(default_factory=dict)
    cao_do_moc: dict[str, float] = field(default_factory=dict)
    hinh_hoc_hoan_tat: bool = False


def _loi(thong_diep: str) -> dict[str, Any]:
    return {"loi": thong_diep}


# ---------------------------------------------------------------------------
# Tool 1-4: đọc file, dò schema, ánh xạ, xác nhận, chuẩn hoá — logic chuyển
# nguyên từ orchestrator/tools.py cũ (đã kiểm chứng chạy thật với OpenAI
# nhiều lần, xem lịch sử trong docs/agents/INPUT_ADAPTER_AGENT.md).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Tool 0 (thử TRƯỚC bước 1): nhận diện + đọc báo cáo ETABS THẬT (đa bảng quan
# hệ Grid Lines/Story Definitions/Joint Coordinates/Connectivity - Frame...)
# — KHÁC hẳn model "1 sheet phẳng" mà doc_va_do_schema/de_xuat_anh_xa/
# chuan_hoa_du_lieu xử lý. MỚI so với bản tools.py cũ: trước đây (xem lịch sử
# webapp/jobs.py) chỉ webapp Python tự rẽ nhánh, KHÔNG có tool nào cho agent
# tự làm việc này — nay đưa hẳn vào agent để CLI/webapp dùng chung 1 đường.
# ---------------------------------------------------------------------------


def doc_etabs_that(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    from pathlib import Path

    from ...input_adapter import etabs_reader

    duong_dan = Path(dau_vao["duong_dan"])
    if not etabs_reader.nhan_dien_file_etabs_that(duong_dan):
        return {
            "la_etabs_that": False,
            "huong_dan": (
                "File này KHÔNG phải báo cáo ETABS thật (thiếu các sheet đặc trưng Grid Lines/Joint "
                "Coordinates/Connectivity - Frame...). Tiếp tục theo đường thông thường: gọi "
                "doc_va_do_schema."
            ),
        }

    bo_du_lieu, toa_do_truc, cao_do_moc = etabs_reader.doc_etabs_thuc(duong_dan)
    phan_tu_tra_ve = [
        {
            "ten": p.ten, "loai": p.loai.value, "b": p.tiet_dien.b, "h": p.tiet_dien.h,
            "mac_be_tong": p.mac_be_tong, "nhom_thep_doc": p.nhom_thep_doc,
            "truc": p.truc, "tang": p.tang, "chieu_dai": p.chieu_dai,
            "vi_tri": [
                {
                    "vi_tri": v.vi_tri, "As_yc": v.As_yc,
                    "M": v.noi_luc.M, "N": v.noi_luc.N, "Q": v.noi_luc.Q,
                    "to_hop": v.noi_luc.to_hop_chi_phoi,
                }
                for v in p.du_lieu_vi_tri
            ],
        }
        for p in bo_du_lieu.phan_tu
    ]
    nc.phan_tu_da_chuan_hoa = phan_tu_tra_ve  # ghi ĐÈ (không extend) — 1 file ETABS thật cho ĐỦ mọi phần tử trong 1 lần đọc
    # toa_do_truc/cao_do_moc lấy TRỰC TIẾP từ bảng Grid Lines/Story
    # Definitions thật — CHÍNH XÁC hơn suy luận gián tiếp, KHÔNG cần gọi
    # suy_luan_hinh_hoc nữa (xem docstring etabs_reader.doc_etabs_thuc).
    nc.toa_do_truc = toa_do_truc
    nc.cao_do_moc = cao_do_moc
    nc.hinh_hoc_hoan_tat = True

    canh_bao = None
    if any(v.get("Q") is None for p in phan_tu_tra_ve for v in p["vi_tri"]):
        canh_bao = (
            "1 số vị trí không có lực cắt Q thô (báo cáo ETABS Concrete Design Summary không xuất "
            "raw force cho dầm) — Rule Engine Agent sẽ tự xử lý (bỏ qua tinh_cot_dai cho các vị trí "
            "đó), KHÔNG được tự bịa Q."
        )
    ket_qua: dict[str, Any] = {
        "la_etabs_that": True, "phan_tu": phan_tu_tra_ve, "toa_do_truc": toa_do_truc, "cao_do_moc": cao_do_moc,
    }
    if canh_bao:
        ket_qua["canh_bao"] = canh_bao
    return ket_qua


def doc_va_do_schema(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    duong_dan = dau_vao["duong_dan"]
    if duong_dan.lower().endswith(".csv"):
        sheets = {"data": readers.doc_csv(duong_dan)}
    else:
        sheets = readers.doc_excel(duong_dan)
    nc.sheets_da_doc = sheets

    sheet_hop_le = readers.tim_sheet_co_du_lieu_khung(sheets)
    return {
        "sheet_hop_le": sheet_hop_le,
        "tat_ca_sheet": {
            ten: {"cot": [str(c) for c in df.columns], "so_dong": len(df)} for ten, df in sheets.items()
        },
    }


def de_xuat_anh_xa(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    if nc.sheets_da_doc is None:
        return _loi("Chưa gọi doc_va_do_schema — không có sheet nào được đọc.")
    ten_sheet = dau_vao["ten_sheet"]
    if ten_sheet not in nc.sheets_da_doc:
        return _loi(f"Sheet '{ten_sheet}' không tồn tại (đã đọc: {list(nc.sheets_da_doc)}).")
    df = nc.sheets_da_doc[ten_sheet]

    truong_bat_buoc = dau_vao.get("truong_bat_buoc") or adapter.TRUONG_BAT_BUOC
    canh_bao: str | None = None
    truong_hop_le = set(heuristics.TU_KHOA_THEO_TRUONG)
    if truong_bat_buoc and not set(truong_bat_buoc) & truong_hop_le:
        # Bảo vệ ở tầng CODE (xem docs/agents/INPUT_ADAPTER_AGENT.md "Lỗi thật
        # đã từng gặp" mục 1) — nếu KHÔNG có phần tử nào trong truong_bat_buoc
        # trùng tên trường chuẩn hợp lệ, gần như chắc chắn LLM đã truyền nhầm
        # TÊN CỘT GỐC của file thay vì tên trường chuẩn nội bộ.
        canh_bao = (
            f"Đã BỎ QUA truong_bat_buoc={truong_bat_buoc!r} vì không khớp bất kỳ tên trường "
            f"chuẩn nào (hợp lệ: {sorted(truong_hop_le)}) — có vẻ bạn đã truyền tên CỘT GỐC "
            "trong file thay vì tên trường chuẩn. Đã dùng danh sách mặc định thay thế."
        )
        truong_bat_buoc = adapter.TRUONG_BAT_BUOC

    ket_qua = adapter.xac_dinh_anh_xa(df, nha_cung_cap_llm=None, truong_bat_buoc=truong_bat_buoc)
    ket_qua_tra_ve: dict[str, Any] = {
        "anh_xa": {t: {"cot_nguon": dx.cot_nguon, "do_tin_cay": dx.do_tin_cay} for t, dx in ket_qua.anh_xa.items()},
        "can_xac_nhan": ket_qua.can_xac_nhan,
        "thieu_bat_buoc": ket_qua.thieu_bat_buoc,
    }
    if canh_bao:
        ket_qua_tra_ve["canh_bao"] = canh_bao
    return ket_qua_tra_ve


def xac_nhan_anh_xa_voi_nguoi_dung(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    truong = dau_vao["truong"]
    cot_de_xuat = dau_vao["cot_de_xuat"]
    ly_do = dau_vao.get("ly_do", "")
    cau_hoi = (
        f"Cột '{cot_de_xuat}' có phải là dữ liệu cho trường '{truong}' không? "
        f"({ly_do}) Trả lời tên cột đúng nếu khác, hoặc 'đồng ý'."
    )
    tra_loi = nc.hoi_nguoi_dung(cau_hoi, None)
    dong_y = tra_loi.strip().lower() in {"đồng ý", "dong y", "yes", "ok", "co", "có"}
    return {"dong_y": dong_y, "cot_nguoi_dung_chi_dinh": None if dong_y else tra_loi.strip()}


def chuan_hoa_du_lieu(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    if nc.sheets_da_doc is None:
        return _loi("Chưa gọi doc_va_do_schema.")
    ten_sheet = dau_vao["ten_sheet"]
    df = nc.sheets_da_doc[ten_sheet]
    anh_xa: dict[str, str] = dau_vao["anh_xa"]
    don_vi = DonViLucGoc(dau_vao.get("don_vi_luc_goc", DonViLucGoc.KN_KNM.value))
    loai_raw = dau_vao.get("loai_mac_dinh")
    loai_mac_dinh = LoaiCauKien(loai_raw) if loai_raw else None

    canh_bao: str | None = None
    if loai_mac_dinh is not None and "loai" in anh_xa:
        # Bảo vệ ở tầng CODE — xem docs/agents/INPUT_ADAPTER_AGENT.md "Lỗi
        # thật đã từng gặp" mục 2.
        canh_bao = (
            f"Đã BỎ QUA loai_mac_dinh='{loai_mac_dinh.value}' vì ánh xạ đã có cột 'loai' "
            "đáng tin cậy cho từng dòng — dùng loai_mac_dinh sẽ ghi đè sai loại của các dòng "
            "khác loại trong cùng sheet. Đã chuẩn hoá theo đúng giá trị 'loai' của từng dòng."
        )
        loai_mac_dinh = None

    try:
        bo_du_lieu = adapter.chuan_hoa_bang(ten_sheet, df, anh_xa, don_vi, loai_mac_dinh)
    except Exception as e:  # dữ liệu vào không hợp lệ theo ánh xạ đã cho — trả lỗi để LLM xử lý, không sập tiến trình
        return _loi(f"Chuẩn hoá thất bại: {e}")

    phan_tu_tra_ve = [
        {
            "ten": p.ten, "loai": p.loai.value, "b": p.tiet_dien.b, "h": p.tiet_dien.h,
            "mac_be_tong": p.mac_be_tong, "nhom_thep_doc": p.nhom_thep_doc,
            "truc": p.truc, "tang": p.tang, "chieu_dai": p.chieu_dai,
            "vi_tri": [
                {
                    "vi_tri": v.vi_tri, "As_yc": v.As_yc,
                    "M": v.noi_luc.M, "N": v.noi_luc.N, "Q": v.noi_luc.Q,
                    "to_hop": v.noi_luc.to_hop_chi_phoi,
                }
                for v in p.du_lieu_vi_tri
            ],
        }
        for p in bo_du_lieu.phan_tu
    ]
    # Gom dần vào ngữ cảnh — suy_luan_hinh_hoc (gọi sau) cần TOÀN BỘ phần tử
    # đã chuẩn hoá từ MỌI sheet, không chỉ sheet vừa xử lý (1 file có thể có
    # nhiều sheet hợp lệ, mỗi sheet 1 lần gọi chuan_hoa_du_lieu).
    nc.phan_tu_da_chuan_hoa.extend(phan_tu_tra_ve)

    ket_qua: dict[str, Any] = {"phan_tu": phan_tu_tra_ve}
    if canh_bao:
        ket_qua["canh_bao"] = canh_bao
    return ket_qua


# ---------------------------------------------------------------------------
# Tool 5: suy luận hình học công trình — MỚI (CHANGE_REQUESTS.md mục 5), bọc
# src/input_adapter/hinh_hoc.py. Đây là điểm khác biệt lớn nhất so với
# tools.py cũ: trước đây KHÔNG có tool nào làm việc này, toạ_độ_trục/cao_độ
# bị hard-code thủ công trong từng script demo.
# ---------------------------------------------------------------------------


def suy_luan_hinh_hoc(nc: NguCanhInputAdapter, dau_vao: dict) -> dict:
    from ...input_adapter.models import PhanTuKhung, TietDien

    # Dựng lại PhanTuKhung tối giản (chỉ cần đúng 4 trường hinh_hoc.py dùng:
    # loai, truc, tang, chieu_dai) từ dict phan_tu agent đã tích luỹ được qua
    # các lần gọi chuan_hoa_du_lieu trước đó — KHÔNG yêu cầu LLM tự truyền lại
    # toàn bộ dữ liệu phần tử (dễ sai/thiếu), agent chỉ cần gọi tool này
    # KHÔNG tham số (hoặc kèm gia_tri_da_biet khi trả lời câu hỏi treo).
    phan_tu_nguon = dau_vao.get("phan_tu") or nc.phan_tu_da_chuan_hoa
    if not phan_tu_nguon:
        return _loi("Chưa có phần tử nào đã chuẩn hoá — gọi chuan_hoa_du_lieu trước.")

    phan_tu_model = [
        PhanTuKhung(
            ten=p["ten"], loai=LoaiCauKien(p["loai"]), tiet_dien=TietDien(p["b"], p["h"]),
            mac_be_tong=p["mac_be_tong"], nhom_thep_doc=p["nhom_thep_doc"],
            truc=p.get("truc"), tang=p.get("tang"), chieu_dai=p.get("chieu_dai"),
        )
        for p in phan_tu_nguon
    ]

    da_biet_truc = dau_vao.get("gia_tri_da_biet_truc")
    da_biet_tang = dau_vao.get("gia_tri_da_biet_tang")

    kq_truc = hinh_hoc.suy_luan_toa_do_truc(phan_tu_model, da_biet=da_biet_truc)
    kq_tang = hinh_hoc.suy_luan_cao_do_moc(phan_tu_model, da_biet=da_biet_tang)

    # Lưu lại kết quả vào ngữ cảnh — xem ghi chú field toa_do_truc/cao_do_moc/
    # hinh_hoc_hoan_tat ở NguCanhInputAdapter. Ghi ĐÈ mỗi lần gọi (lần gọi sau
    # luôn đáng tin hơn lần trước vì có thêm gia_tri_da_biet mới).
    nc.toa_do_truc = kq_truc.gia_tri
    nc.cao_do_moc = kq_tang.gia_tri
    nc.hinh_hoc_hoan_tat = kq_truc.hoan_tat and kq_tang.hoan_tat

    return {
        "hoan_tat": nc.hinh_hoc_hoan_tat,
        "toa_do_truc": kq_truc.gia_tri,
        "cao_do_moc": kq_tang.gia_tri,
        "thieu": kq_truc.thieu + kq_tang.thieu,
    }


# ---------------------------------------------------------------------------
# Đăng ký tool.
# ---------------------------------------------------------------------------

DINH_NGHIA_TOOL: list[dict] = [
    {
        "name": "doc_etabs_that",
        "description": (
            "THỬ GỌI TRƯỚC TIÊN, trước doc_va_do_schema. Nhận diện + đọc THẲNG báo cáo ETABS THẬT (đa "
            "bảng quan hệ: Grid Lines, Joint Coordinates, Connectivity - Frame...). Nếu 'la_etabs_that'"
            "=true, kết quả đã ĐỦ VÀ CHÍNH XÁC (phan_tu, toa_do_truc, cao_do_moc) — DỪNG NGAY, không "
            "gọi doc_va_do_schema/de_xuat_anh_xa/chuan_hoa_du_lieu/suy_luan_hinh_hoc nữa (gọi các tool "
            "đó trên file này sẽ LỖI vì không đúng định dạng heuristic xử lý được). Nếu "
            "'la_etabs_that'=false, tiếp tục bình thường từ doc_va_do_schema."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"duong_dan": {"type": "string"}},
            "required": ["duong_dan"],
        },
    },
    {
        "name": "doc_va_do_schema",
        "description": "Đọc file Excel/CSV và liệt kê sheet + tên cột (KHÔNG suy đoán ý nghĩa cột).",
        "input_schema": {
            "type": "object",
            "properties": {"duong_dan": {"type": "string"}},
            "required": ["duong_dan"],
        },
    },
    {
        "name": "de_xuat_anh_xa",
        "description": "Chạy heuristic dò ánh xạ cột cho 1 sheet đã đọc, trả về độ tin cậy từng trường.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ten_sheet": {"type": "string"},
                "truong_bat_buoc": {
                    "type": "array", "items": {"type": "string"},
                    "description": (
                        "THƯỜNG NÊN BỎ TRỐNG (dùng mặc định hợp lý sẵn có). Nếu truyền, PHẢI là "
                        "TÊN TRƯỜNG CHUẨN NỘI BỘ — CHỈ được chọn trong tập: ten_phan_tu, loai, "
                        "vi_tri, b, h, mac_be_tong, nhom_thep, combo, M, N, Q, As_yc. TUYỆT ĐỐI "
                        "KHÔNG truyền tên cột gốc trong file (vd 'Phan_tu', 'b(mm)') — sẽ khiến "
                        "'thieu_bat_buoc' báo sai dù ánh xạ thực tế đã đủ."
                    ),
                },
            },
            "required": ["ten_sheet"],
        },
    },
    {
        "name": "xac_nhan_anh_xa_voi_nguoi_dung",
        "description": "Hỏi người dùng xác nhận 1 ánh xạ cột có độ tin cậy thấp trước khi dùng để tính toán.",
        "input_schema": {
            "type": "object",
            "properties": {
                "truong": {"type": "string"},
                "cot_de_xuat": {"type": "string"},
                "ly_do": {"type": "string"},
            },
            "required": ["truong", "cot_de_xuat"],
        },
    },
    {
        "name": "chuan_hoa_du_lieu",
        "description": "Chuẩn hoá 1 sheet thành danh sách phần tử khung theo ánh xạ ĐÃ ĐƯỢC XÁC NHẬN.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ten_sheet": {"type": "string"},
                "anh_xa": {"type": "object"},
                "don_vi_luc_goc": {"type": "string", "enum": ["kN_kNm", "N_Nmm"]},
                "loai_mac_dinh": {
                    "type": "string", "enum": ["dam", "cot"],
                    "description": (
                        "CHỈ dùng khi anh_xa KHÔNG có trường 'loai'. Nếu anh_xa ĐÃ CÓ 'loai', "
                        "BỎ TRỐNG tham số này — ép loai_mac_dinh sẽ ghi đè SAI loại của các dòng "
                        "khác loại trong cùng sheet."
                    ),
                },
            },
            "required": ["ten_sheet", "anh_xa"],
        },
    },
    {
        "name": "suy_luan_hinh_hoc",
        "description": (
            "Suy luận toa_do_truc/cao_do_moc của công trình từ toàn bộ phần tử ĐÃ chuẩn hoá (tự động "
            "dùng lại phan_tu đã tích luỹ qua các lần gọi chuan_hoa_du_lieu trước đó — KHÔNG cần "
            "truyền lại). Gọi ĐÚNG 1 LẦN sau khi đã chuan_hoa_du_lieu xong MỌI sheet cần dùng. Nếu "
            "kết quả trả 'hoan_tat'=false, đọc 'thieu' và hỏi người dùng từng giá trị còn thiếu, rồi "
            "gọi LẠI tool này với 'gia_tri_da_biet_truc'/'gia_tri_da_biet_tang' đã bổ sung — KHÔNG tự "
            "bịa số, KHÔNG dùng lại toạ độ của công trình khác."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "gia_tri_da_biet_truc": {
                    "type": "object",
                    "description": "vd {\"D\": 12000} — toạ độ (mm) của các trục người dùng vừa xác nhận, nếu có.",
                },
                "gia_tri_da_biet_tang": {
                    "type": "object",
                    "description": "vd {\"tangmai\": 15200} — cao độ (mm) của các mốc tầng người dùng vừa xác nhận, nếu có.",
                },
            },
        },
    },
    DINH_NGHIA_HOI_NGUOI_DUNG,
]

_HAM_THEO_TEN: dict[str, Callable[[NguCanhInputAdapter, dict], dict]] = {
    "doc_etabs_that": doc_etabs_that,
    "doc_va_do_schema": doc_va_do_schema,
    "de_xuat_anh_xa": de_xuat_anh_xa,
    "xac_nhan_anh_xa_voi_nguoi_dung": xac_nhan_anh_xa_voi_nguoi_dung,
    "chuan_hoa_du_lieu": chuan_hoa_du_lieu,
    "suy_luan_hinh_hoc": suy_luan_hinh_hoc,
    "hoi_nguoi_dung": hoi_nguoi_dung,
}


def tao_dispatch(nc: NguCanhInputAdapter) -> dict[str, Callable[[dict], dict]]:
    return {ten: (lambda dau_vao, _ham=ham: _ham(nc, dau_vao)) for ten, ham in _HAM_THEO_TEN.items()}


# ---------------------------------------------------------------------------
# System prompt + hàm chạy 1 phiên độc lập.
# ---------------------------------------------------------------------------

HE_THONG_PROMPT = """\
Bạn là Input Adapter Agent trong hệ thống thiết kế khung BTCT theo TCVN \
5574:2018 (đọc chi tiết: docs/agents/INPUT_ADAPTER_AGENT.md). Nhiệm vụ DUY \
NHẤT: đọc 1 file Excel/CSV có schema BẤT KỲ (không biết trước tên cột) và \
biến nó thành dữ liệu chuẩn hoá kèm hình học công trình. Bạn KHÔNG tính bất \
kỳ con số kỹ thuật nào (As, M, N...) và KHÔNG quyết định thép/bản vẽ.

Quy trình:
0. LUÔN thử gọi doc_etabs_that TRƯỚC TIÊN. Nếu "la_etabs_that"=true, dữ liệu \
đã đủ và chính xác — DỪNG NGAY, tóm tắt kết quả, không làm bước 1-4 dưới đây.
1. Nếu "la_etabs_that"=false: gọi doc_va_do_schema đúng 1 lần. Lấy sheet_hop_le.
2. Với từng sheet hợp lệ, gọi de_xuat_anh_xa. Với MỌI trường trong \
"can_xac_nhan" hoặc "thieu_bat_buoc", BẮT BUỘC gọi \
xac_nhan_anh_xa_voi_nguoi_dung trước khi dùng ánh xạ đó — không tự ý dùng \
ánh xạ độ tin cậy thấp.
3. Khi mọi trường bắt buộc đã có ánh xạ đã xác nhận, gọi chuan_hoa_du_lieu.
4. Sau khi đã chuan_hoa_du_lieu cho MỌI sheet cần dùng, gọi suy_luan_hinh_hoc \
đúng 1 lần (không cần tự truyền lại phan_tu). Nếu "hoan_tat"=false, đọc \
"thieu", hỏi người dùng (qua hoi_nguoi_dung) từng giá trị còn thiếu, rồi \
gọi LẠI suy_luan_hinh_hoc kèm gia_tri_da_biet_truc/gia_tri_da_biet_tang.

Khi đã có đủ phan_tu[] (từ các lần gọi chuan_hoa_du_lieu) VÀ toa_do_truc/ \
cao_do_moc đã hoan_tat, dừng lại và tóm tắt kết quả bằng văn bản — không gọi \
thêm tool nào nữa. Đây là kết quả cuối cùng bạn bàn giao, không cần lo về \
các bước sau (chọn thép, vẽ) — đó là việc của agent khác.
"""


def chay_input_adapter_agent(
    nha_cung_cap: agent.NhaCungCapChat,
    duong_dan_file: str,
    hoi_nguoi_dung: HamHoiNguoiDung,
    so_lan_goi_toi_da: int = 20,
) -> tuple[agent.KetQuaVongLapAgent, NguCanhInputAdapter]:
    """Chạy 1 phiên độc lập của Input Adapter Agent cho 1 file. Trả về cả kết
    quả vòng lặp (log, lý do dừng) LẪN `NguCanhInputAdapter` (để lớp gọi —
    `pipeline.py` — đọc lại `phan_tu_da_chuan_hoa` một cách chắc chắn, không
    phải tự bóc tách từ `nhat_ky_tool` dạng log tự do)."""
    nc = NguCanhInputAdapter(hoi_nguoi_dung=hoi_nguoi_dung)
    dispatch = tao_dispatch(nc)
    tin_nhan_dau = f"Đọc và chuẩn hoá file dữ liệu khung tại đường dẫn: {duong_dan_file}"
    ket_qua = agent.chay_vong_lap_tool(
        nha_cung_cap=nha_cung_cap, he_thong=HE_THONG_PROMPT, tin_nhan_dau=tin_nhan_dau,
        tools=DINH_NGHIA_TOOL, dispatch=dispatch, so_lan_goi_toi_da=so_lan_goi_toi_da,
    )
    return ket_qua, nc


def trich_bo_du_lieu_chuan_hoa(nc: NguCanhInputAdapter) -> BoDuLieuKhungChuanHoa | None:
    """Chuyển state cuối cùng của `NguCanhInputAdapter` (sau khi
    `chay_input_adapter_agent` chạy xong) sang `BoDuLieuKhungChuanHoa` — dữ
    liệu kiểu Python có cấu trúc mà `pipeline.py` dùng để bàn giao cho Rule
    Engine Agent + Drawing Agent. Trả None nếu chưa có phần tử nào ĐÃ chuẩn
    hoá, HOẶC agent chưa suy luận xong hình học (`hinh_hoc_hoan_tat=False`) —
    trường hợp này `pipeline.py` phải coi là chưa sẵn sàng/lỗi, không được
    âm thầm dùng `toa_do_truc`/`cao_do_moc` còn thiếu để vẽ tiếp."""
    if not nc.phan_tu_da_chuan_hoa or not nc.hinh_hoc_hoan_tat:
        return None
    phan_tu = [
        PhanTuChuanHoa(
            ten=p["ten"], loai=p["loai"], b=p["b"], h=p["h"], mac_be_tong=p["mac_be_tong"],
            nhom_thep_doc=p["nhom_thep_doc"], truc=p.get("truc"), tang=p.get("tang"),
            chieu_dai=p.get("chieu_dai"),
            vi_tri=[ViTriChuanHoa(**v) for v in p["vi_tri"]],
        )
        for p in nc.phan_tu_da_chuan_hoa
    ]
    return BoDuLieuKhungChuanHoa(phan_tu=phan_tu, toa_do_truc=nc.toa_do_truc, cao_do_moc=nc.cao_do_moc)
