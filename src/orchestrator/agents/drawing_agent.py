"""Drawing Agent — 1 trong 4 agent LLM riêng biệt (CHANGE_REQUESTS.md mục
1). Xem đầy đủ vai trò, quy trình, hợp đồng dữ liệu tại
`docs/agents/DRAWING_AGENT.md`. Vẽ **100% qua AutoCAD COM**
(`src/drawing/backend_com.py`) — không còn `ezdxf`/`backend_dxf.py` nào
trong repo (đã xoá, CHANGE_REQUESTS.md mục 2).

3 tool: `ve_mat_cat` (từng mặt cắt), `lap_rap_mat_dung_khung` (mặt đứng khung
tổng thể + bảng thống kê + khung tên, gộp làm 1 bước — xem docstring tool
bên dưới để biết vì sao gộp), `xuat_ban_ve` (PDF + DWG).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ...drawing import backend_com, geometry, verify_drawing
from ...drawing.so_hieu_thanh import SoDangKySoHieu, ThanhThep
from ...input_adapter.models import DuLieuViTri, LoaiCauKien, NoiLuc, PhanTuKhung, TietDien
from .. import agent, khung_ve
from ..shared.hoi_nguoi_dung_tool import DINH_NGHIA_HOI_NGUOI_DUNG, hoi_nguoi_dung
from ..shared.phien_cad import PhienCAD

HamHoiNguoiDung = Callable[[str, list[str] | None], str]


@dataclass
class NguCanhDrawing:
    hoi_nguoi_dung: HamHoiNguoiDung
    phien_cad: PhienCAD


def _loi(thong_diep: str) -> dict[str, Any]:
    return {"loi": thong_diep}


# ---------------------------------------------------------------------------
# Tool 1: vẽ 1 mặt cắt ngang — chuyển từ backend_dxf (bản cũ) sang backend_com.
# ---------------------------------------------------------------------------


def ve_mat_cat(nc: NguCanhDrawing, dau_vao: dict) -> dict:
    loai = dau_vao["loai"]
    nhan = dau_vao["nhan"]
    if loai == "dam":
        bv = geometry.ve_mat_cat_dam(
            nhan, b=dau_vao["b"], h=dau_vao["h"], cover=dau_vao.get("cover", 25.0),
            duong_kinh_dai=dau_vao.get("duong_kinh_dai", 8.0),
            thanh_duoi=dau_vao["thanh_duoi"], thanh_tren=dau_vao["thanh_tren"],
        )
    elif loai == "cot":
        bv = geometry.ve_mat_cat_cot(
            nhan, b=dau_vao["b"], h=dau_vao["h"], cover=dau_vao.get("cover", 40.0),
            duong_kinh_dai=dau_vao.get("duong_kinh_dai", 8.0),
            so_thanh_canh_b=dau_vao["so_thanh_canh_b"], duong_kinh_canh_b=dau_vao["duong_kinh_canh_b"],
            so_thanh_canh_h=dau_vao["so_thanh_canh_h"], duong_kinh_canh_h=dau_vao["duong_kinh_canh_h"],
        )
    else:
        return _loi(f"loai phải là 'dam' hoặc 'cot', nhận '{loai}'.")

    vi_pham_ir = verify_drawing.kiem_tra_mat_cat_ir(bv, dau_vao["b"], dau_vao["h"])
    if vi_pham_ir:
        return {"loi": "Hình học không khớp kích thước khai báo (lỗi logic geometry.py)", "chi_tiet": vi_pham_ir}

    # Vẽ vào ĐÚNG 1 Document COM dùng chung cho cả khung (nc.phien_cad.doc),
    # đặt cạnh nhau theo x_tiep_theo đang giữ trong PhienCAD — KHÔNG mở
    # Document mới cho mỗi mặt cắt (docs/agents/DRAWING_AGENT.md).
    x_dat = nc.phien_cad.x_tiep_theo
    backend_com.ve_vao_doc(nc.phien_cad.doc, bv, dx=x_dat, dy=nc.phien_cad.y_mat_cat)
    nc.phien_cad.x_tiep_theo = x_dat + dau_vao["b"] + nc.phien_cad.khoang_cach_giua_mat_cat

    return {"nhan": nhan, "x_da_dat": x_dat, "so_thanh_thep": verify_drawing.dem_thanh_thep_ir(bv)}


# ---------------------------------------------------------------------------
# Tool 2: lắp ráp mặt đứng khung + bảng thống kê + khung tên — MỚI
# (CHANGE_REQUESTS.md mục 3). Gộp cả 3 phần vào 1 tool (thay vì 3 tool riêng)
# vì cả 3 đều cần đặt lên CÙNG 1 vùng trống bên dưới hàng mặt cắt và dùng
# CHUNG dữ liệu `phan_tu` — tách 3 tool sẽ buộc LLM tự nhớ lại toàn bộ dữ
# liệu phan_tu 3 lần, dễ truyền sai/thiếu ở lần thứ 2-3.
# ---------------------------------------------------------------------------


def _ky_hieu_thep_theo_vi_tri(
    vi_tri_list: list[dict], chieu_dai: float | None, so_dang_ky: SoDangKySoHieu,
) -> list[geometry.KyHieuThep]:
    """Thay `_mo_ta_thep_gop` (ghi chữ dài trực tiếp, vd "8Ø25 (đều chu vi...)")
    — SAI quy cách bản vẽ kỹ thuật xây dựng thật, xác nhận qua đối chiếu
    KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md mục 2.2 (TCVN 4612-88) VÀ bản vẽ mẫu
    chính thức `data/samples/BoTriThep_KhungTruc5_mau.pdf`: thép phải ghi
    bằng SỐ HIỆU trong vòng tròn (dùng chung số hiệu cho MỌI nơi cùng loại
    thanh — đường kính + chiều dài giống nhau — xuất hiện), KHÔNG ghi chữ mô
    tả dài lặp lại ở từng cấu kiện.

    Mỗi thanh RIÊNG trong 1 vị trí (vd "1Ø20+1Ø22" có 2 đường kính khác
    nhau) ra 1 KyHieuThep RIÊNG — KHÔNG gộp chung 1 ký hiệu cho cả tổ hợp,
    đúng nguyên tắc "1 loại thanh = 1 số hiệu" của mục 2.2."""
    chieu_dai_str = f"L={round(chieu_dai)}" if chieu_dai else None
    chieu_dai_lam_tron = round(chieu_dai) if chieu_dai else 0
    ket_qua: list[geometry.KyHieuThep] = []
    for v in vi_tri_list:
        vi_tri = v.get("vi_tri", "dai_dien")
        for th in v.get("thanh", []):
            so_hieu = so_dang_ky.lay_so_hieu(ThanhThep(duong_kinh=th["duong_kinh"], chieu_dai_mm=chieu_dai_lam_tron))
            ket_qua.append(
                geometry.KyHieuThep(
                    so_hieu=so_hieu, so_luong_duong_kinh=f"{th['so_luong']}Ø{th['duong_kinh']}",
                    chieu_dai=chieu_dai_str, vi_tri_tren_cau_kien=vi_tri,
                )
            )
    return ket_qua


def _phan_tu_khung_tu_dict(p: dict) -> PhanTuKhung:
    return PhanTuKhung(
        ten=p["ten"], loai=LoaiCauKien(p["loai"]), tiet_dien=TietDien(p["b"], p["h"]),
        mac_be_tong=p.get("mac_be_tong", ""), nhom_thep_doc=p.get("nhom_thep_doc", ""),
        truc=p.get("truc"), tang=p.get("tang"), chieu_dai=p.get("chieu_dai"),
        du_lieu_vi_tri=[
            DuLieuViTri(vi_tri=v["vi_tri"], As_yc=v.get("As_yc"), noi_luc=NoiLuc())
            for v in p.get("vi_tri", [])
        ],
    )


def _xay_dong_thong_ke(phan_tu: list[dict], so_dang_ky: SoDangKySoHieu) -> list[geometry.DongThongKe]:
    """Gộp số liệu thép từ TOÀN BỘ phần tử thành các dòng bảng thống kê (mục
    3.9, 8 cột — xem geometry.DongThongKe). Mỗi (đường kính, phần tử) ra 1
    dòng riêng (không gộp chung mọi phần tử cùng đường kính thành 1 dòng —
    giữ được cột "Tên cấu kiện" có ý nghĩa, đúng ví dụ bản vẽ mẫu).

    'chieu_dai_1_don_vi_mm' dùng ĐÚNG 'chieu_dai' (nhịp dầm/chiều cao đoạn
    cột) của phần tử — đây là XẤP XỈ đơn giản hoá có chủ đích (nguyên trạng
    chưa tính lại chiều dài cắt thép thật gồm đoạn neo/nối/uốn móc — công
    thức đó KHÔNG có sẵn trong src/rule_engine/, ngoài phạm vi As/cấu tạo
    hiện tại). Nếu phần tử không có 'chieu_dai' (Input Adapter không suy ra
    được), BỎ QUA dòng đó — không tự bịa chiều dài.

    'so_hieu_thanh' giờ lấy từ `so_dang_ky` (SỔ ĐĂNG KÝ DÙNG CHUNG với ký
    hiệu vẽ trên mặt đứng khung — xem `_ky_hieu_thep_theo_vi_tri`) thay vì tự
    đánh số cục bộ tăng dần như trước — LỖI THẬT đã gặp: bảng thống kê trước
    đây đánh số hiệu RIÊNG không liên quan gì tới số ghi trên hình vẽ (thực
    ra trước đây hình vẽ còn chưa CÓ số hiệu nào, chỉ ghi chữ) — nay 2 nơi
    PHẢI khớp nhau (mục 2.2: đối chiếu số hiệu bảng thống kê với hình vẽ)."""
    dong: list[geometry.DongThongKe] = []
    for p in phan_tu:
        chieu_dai = p.get("chieu_dai")
        if not chieu_dai:
            continue
        dem_theo_duong_kinh: dict[int, int] = {}
        for v in p.get("vi_tri", []):
            for th in v.get("thanh", []):
                dem_theo_duong_kinh[th["duong_kinh"]] = dem_theo_duong_kinh.get(th["duong_kinh"], 0) + th["so_luong"]
        for d, so_luong in sorted(dem_theo_duong_kinh.items()):
            so_hieu = so_dang_ky.lay_so_hieu(ThanhThep(duong_kinh=d, chieu_dai_mm=round(chieu_dai)))
            dong.append(
                geometry.tinh_dong_thong_ke(
                    ten_cau_kien=p["ten"], so_hieu_thanh=str(so_hieu), hinh_dang="Thẳng",
                    duong_kinh=d, chieu_dai_1_don_vi_mm=chieu_dai, so_luong=so_luong,
                )
            )
    return dong


def lap_rap_mat_dung_khung(nc: NguCanhDrawing, dau_vao: dict) -> dict:
    toa_do_truc: dict[str, float] = dau_vao["toa_do_truc"]
    cao_do_moc: dict[str, float] = dau_vao["cao_do_moc"]
    phan_tu_raw: list[dict] = dau_vao["phan_tu"]

    danh_sach_phan_tu = [_phan_tu_khung_tu_dict(p) for p in phan_tu_raw]
    # 1 SỔ ĐĂNG KÝ SỐ HIỆU DÙNG CHUNG cho cả bảng thống kê lẫn ký hiệu vẽ
    # trên mặt đứng khung — bắt buộc dùng CHUNG 1 instance (không tạo 2 sổ
    # riêng) để cùng 1 loại thanh (đường kính+chiều dài) LUÔN nhận đúng 1 số
    # hiệu giống nhau ở cả 2 chỗ (mục 2.2 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md).
    so_dang_ky = SoDangKySoHieu()
    # Xây bảng thống kê TRƯỚC (cấp số hiệu theo đúng thứ tự phan_tu_raw xuất
    # hiện — cột trước, dầm sau) rồi mới xây ký hiệu mặt đứng khung, để 2 nơi
    # nhất quán thứ tự đánh số thay vì phụ thuộc thứ tự gọi hàm ngẫu nhiên.
    dong_thong_ke = _xay_dong_thong_ke(phan_tu_raw, so_dang_ky)
    ky_hieu_theo_ten = {
        p["ten"]: _ky_hieu_thep_theo_vi_tri(p.get("vi_tri", []), p.get("chieu_dai"), so_dang_ky)
        for p in phan_tu_raw
    }

    ban_ve_khung = khung_ve.lap_rap_mat_dung_khung(
        danh_sach_phan_tu, ky_hieu_theo_ten=ky_hieu_theo_ten, toa_do_truc=toa_do_truc, cao_do_moc=cao_do_moc,
    )
    if ban_ve_khung is None:
        return _loi(
            "Không đủ dữ liệu truc/tang để lắp ráp mặt đứng khung (phần tử thiếu 'truc'/'tang') — "
            "kiểm tra lại dữ liệu Input Adapter Agent đã bàn giao."
        )

    ban_ve_tong = geometry.BanVe(ten="TONG_HOP")
    ban_ve_tong.gop(ban_ve_khung)

    y_dat_bang = -6000.0  # đặt hẳn bên dưới mặt đứng khung, đủ xa để không đè lên chuỗi kích thước/mốc cao độ
    if dong_thong_ke:
        bang = geometry.ve_bang_thong_ke(
            "BANG_THONG_KE", dong_thong_ke, do_rong_cot=[900, 300, 500, 300, 700, 300, 700, 700],
        )
        ban_ve_tong.gop(bang.dich_chuyen(0, y_dat_bang))

    tt = geometry.ThongTinKhungTen(
        ten_truong=dau_vao.get("ten_truong", "TRƯỜNG ĐẠI HỌC KIẾN TRÚC HÀ NỘI"),
        khoa=dau_vao.get("khoa", "KHOA XÂY DỰNG"),
        chuyen_nganh=dau_vao.get("chuyen_nganh", "XÂY DỰNG DD&CN"),
        ten_do_an=dau_vao.get("ten_do_an", "ĐỒ ÁN AI AGENT THIẾT KẾ KHUNG BTCT"),
        gvhd=dau_vao.get("gvhd", "—"), svth=dau_vao.get("svth", "—"),
        de_so=dau_vao.get("de_so", "—"), ngay_nhan=dau_vao.get("ngay_nhan", "—"),
        ngay_hoan_thanh=dau_vao.get("ngay_hoan_thanh", "—"),
    )
    khung_ten = geometry.ve_khung_ten(rong=6000, cao=1800, thong_tin=tt)
    ban_ve_tong.gop(khung_ten.dich_chuyen(0, y_dat_bang - 6500))

    backend_com.ve_vao_doc(nc.phien_cad.doc, ban_ve_tong, dx=0, dy=6000)  # dy: tách khỏi hàng mặt cắt phía trên (y=0)

    so_cot = sum(1 for p in phan_tu_raw if p["loai"] == "cot")
    so_dam = sum(1 for p in phan_tu_raw if p["loai"] == "dam")
    return {
        "so_cot": so_cot, "so_dam": so_dam,
        # Thay "nhan_ky_vong_theo_cau_kien" (danh sách tên vị trí, dùng để dò
        # TEXT chứa "goi_trai"/"giua_nhip"/"goi_phai") — hệ ký hiệu số hiệu
        # MỚI không còn ghi các tên vị trí này thành text tìm được nữa (chỉ
        # còn số hiệu trong vòng tròn + "2Ø18"/"L=..."), nên đổi cách kiểm
        # chứng sang ĐẾM SỐ VÒNG TRÒN SO_HIEU đã vẽ so với số ký hiệu dự kiến.
        "so_ky_hieu_ky_vong": sum(len(kh) for kh in ky_hieu_theo_ten.values()),
        "co_bang_thong_ke": bool(dong_thong_ke),
    }


# ---------------------------------------------------------------------------
# Tool 3: xuất PDF + DWG.
# ---------------------------------------------------------------------------


def xuat_ban_ve(nc: NguCanhDrawing, dau_vao: dict) -> dict:
    ten_file = dau_vao.get("ten_file", "BAN_VE_KHUNG")
    os.makedirs(nc.phien_cad.thu_muc_xuat, exist_ok=True)
    duong_dan_pdf = os.path.join(nc.phien_cad.thu_muc_xuat, f"{ten_file}.pdf")
    duong_dan_dwg = os.path.join(nc.phien_cad.thu_muc_xuat, f"{ten_file}.dwg")

    backend_com.xuat_pdf(nc.phien_cad.doc, duong_dan_pdf)
    backend_com.luu_file_dwg(nc.phien_cad.doc, duong_dan_dwg)

    return {"duong_dan_pdf": duong_dan_pdf, "duong_dan_dwg": duong_dan_dwg}


# ---------------------------------------------------------------------------
# Đăng ký tool.
# ---------------------------------------------------------------------------

DINH_NGHIA_TOOL: list[dict] = [
    {
        "name": "ve_mat_cat",
        "description": "Vẽ 1 mặt cắt ngang dầm/cột vào bản vẽ AutoCAD đang mở (qua COM), đặt cạnh mặt cắt trước đó.",
        "input_schema": {
            "type": "object",
            "properties": {
                "loai": {"type": "string", "enum": ["dam", "cot"]},
                "nhan": {"type": "string"},
                "b": {"type": "number"}, "h": {"type": "number"}, "cover": {"type": "number"},
                "duong_kinh_dai": {"type": "number"},
                "thanh_duoi": {
                    "type": "array", "items": {"type": "integer"},
                    "description": (
                        "CHỈ dùng cho loai=dam. Danh sách ĐƯỜNG KÍNH (mm) từng thanh thép dưới, "
                        "LẶP LẠI 1 phần tử cho mỗi thanh — KHÔNG phải số lượng. Vd tổ hợp "
                        "'1Ø16+4Ø18' -> [16, 18, 18, 18, 18], không phải [1, 4]."
                    ),
                },
                "thanh_tren": {"type": "array", "items": {"type": "integer"}, "description": "CHỈ dùng cho loai=dam. Cùng quy tắc như thanh_duoi nhưng cho thép trên."},
                "so_thanh_canh_b": {"type": "integer", "description": "CHỈ dùng cho loai=cot."},
                "duong_kinh_canh_b": {"type": "integer", "description": "CHỈ dùng cho loai=cot."},
                "so_thanh_canh_h": {"type": "integer", "description": "CHỈ dùng cho loai=cot."},
                "duong_kinh_canh_h": {"type": "integer", "description": "CHỈ dùng cho loai=cot."},
            },
            "required": ["loai", "nhan", "b", "h"],
        },
    },
    {
        "name": "lap_rap_mat_dung_khung",
        "description": (
            "Lắp ráp mặt đứng khung tổng thể + bảng thống kê thép + khung tên, vẽ vào CÙNG Document "
            "đang mở (bên dưới hàng mặt cắt). Gọi ĐÚNG 1 LẦN, sau khi MỌI phần tử đã ve_mat_cat và qua "
            "Verification Agent. 'phan_tu' PHẢI liệt kê ĐỦ mọi vị trí của MỖI dầm (gối trái/giữa nhịp/"
            "gối phải) kèm 'mo_ta_thep' của từng vị trí — tool tự gộp thành 1 nhãn duy nhất/dầm, "
            "KHÔNG được chỉ truyền 1 vị trí rồi bỏ sót 2 vị trí còn lại."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "toa_do_truc": {"type": "object", "description": "vd {\"A\": 0, \"B\": 5600} — lấy nguyên từ Input Adapter Agent."},
                "cao_do_moc": {"type": "object", "description": "vd {\"tang2\": 3200} — lấy nguyên từ Input Adapter Agent."},
                "phan_tu": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ten": {"type": "string"}, "loai": {"type": "string", "enum": ["dam", "cot"]},
                            "b": {"type": "number"}, "h": {"type": "number"},
                            "truc": {"type": "string"}, "tang": {"type": "string"},
                            "chieu_dai": {"type": "number", "description": "Nhịp dầm/chiều cao đoạn cột (mm), nếu có — dùng lập bảng thống kê."},
                            "mac_be_tong": {"type": "string"}, "nhom_thep_doc": {"type": "string"},
                            "vi_tri": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "vi_tri": {"type": "string"},
                                        "mo_ta_thep": {"type": "string", "description": "vd '2Ø18+1Ø16' — lấy từ 'mo_ta' của chon_thep_doc (Rule Engine Agent)."},
                                        "As_yc": {"type": "number"},
                                        "thanh": {
                                            "type": "array", "items": {"type": "object", "properties": {"duong_kinh": {"type": "integer"}, "so_luong": {"type": "integer"}}},
                                            "description": "Danh sách {duong_kinh, so_luong} — lấy nguyên từ 'thanh' của chon_thep_doc, dùng lập bảng thống kê.",
                                        },
                                    },
                                    "required": ["vi_tri", "mo_ta_thep"],
                                },
                            },
                        },
                        "required": ["ten", "loai", "b", "h", "vi_tri"],
                    },
                },
                "ten_truong": {"type": "string"}, "khoa": {"type": "string"}, "chuyen_nganh": {"type": "string"},
                "ten_do_an": {"type": "string"}, "gvhd": {"type": "string"}, "svth": {"type": "string"},
                "de_so": {"type": "string"}, "ngay_nhan": {"type": "string"}, "ngay_hoan_thanh": {"type": "string"},
            },
            "required": ["toa_do_truc", "cao_do_moc", "phan_tu"],
        },
    },
    {
        "name": "xuat_ban_ve",
        "description": "Xuất bản vẽ hiện tại (đã có mặt cắt + mặt đứng khung) ra file PDF và DWG.",
        "input_schema": {
            "type": "object",
            "properties": {"ten_file": {"type": "string", "description": "Tên file không kèm đuôi, vd 'KHUNG_TRUC5'."}},
        },
    },
    DINH_NGHIA_HOI_NGUOI_DUNG,
]

_HAM_THEO_TEN: dict[str, Callable[[NguCanhDrawing, dict], dict]] = {
    "ve_mat_cat": ve_mat_cat,
    "lap_rap_mat_dung_khung": lap_rap_mat_dung_khung,
    "xuat_ban_ve": xuat_ban_ve,
    "hoi_nguoi_dung": hoi_nguoi_dung,
}


def tao_dispatch(nc: NguCanhDrawing) -> dict[str, Callable[[dict], dict]]:
    return {ten: (lambda dau_vao, _ham=ham: _ham(nc, dau_vao)) for ten, ham in _HAM_THEO_TEN.items()}


# ---------------------------------------------------------------------------
# System prompt + hàm chạy 1 phiên độc lập.
# ---------------------------------------------------------------------------

# Cẩm nang thao tác vẽ chi tiết (khổ giấy, hệ nét, mặt cắt, ký hiệu số hiệu,
# bảng thống kê...) — biên soạn riêng, không phải TCVN/RULES_TCVN5574.md.
# Đọc NGUYÊN VĂN vào system prompt (xem _doc_skill_ve_ky_thuat) thay vì chỉ
# trích dẫn qua comment như các tài liệu khác trong repo — người dùng yêu cầu
# tường minh "viết code để agent đọc được tài liệu này". Đường hình học/layer/
# lineweight thật vẫn do code (geometry.py/layers.py) quyết định, KHÔNG phải
# LLM tự vẽ tay — tài liệu này chỉ giúp agent biết NÊN yêu cầu vẽ gì/ở đâu
# (vị trí mặt cắt, số hiệu, bố cục) khi gọi tool, đúng vai trò điều phối.
_DUONG_DAN_SKILL_VE_KY_THUAT = (
    Path(__file__).resolve().parents[3] / "docs" / "agents" / "huongdanvebanve" / "SKILL_VE_KY_THUAT_BTCT.md"
)
_MAU_ANH_MARKDOWN = re.compile(r"!\[([^\]]*)\]\([^)]*\)")


def _doc_skill_ve_ky_thuat() -> str:
    """Đọc SKILL_VE_KY_THUAT_BTCT.md, bỏ cú pháp ảnh markdown (agent nhận văn
    bản thuần qua tool-calling, không xem được ảnh img/*.png) — thay bằng chú
    thích ngắn để mạch văn bản không đứt quãng. Trả về "" (không raise) nếu
    file bị xoá/di chuyển — pipeline vẫn chạy được với prompt rút gọn thay vì
    sập hẳn, nhưng đây là tài liệu BẮT BUỘC nên thiếu file cần được coi là
    bất thường cần sửa ngay, không phải hành vi bình thường."""
    try:
        van_ban = _DUONG_DAN_SKILL_VE_KY_THUAT.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    return _MAU_ANH_MARKDOWN.sub(r"[hình minh hoạ: \1 — chỉ có trong file gốc, không kèm được qua tool-calling văn bản]", van_ban)


def _xay_dung_he_thong_prompt() -> str:
    prompt = """\
Bạn là Drawing Agent trong hệ thống thiết kế khung BTCT theo TCVN 5574:2018 \
(đọc chi tiết: docs/agents/DRAWING_AGENT.md). Bạn vẽ bản vẽ kỹ thuật 100% \
qua AutoCAD thật (COM) từ phương án thép Rule Engine Agent ĐÃ CHỌN — bạn \
KHÔNG được tự đổi số thanh/đường kính thép, chỉ vẽ đúng số liệu đã cho.

Nhiệm vụ của bạn (do pipeline gọi lại nhiều lần, mỗi lần 1 việc cụ thể — đọc \
kỹ yêu cầu trong tin nhắn đầu để biết đang ở bước nào):
- Nếu được yêu cầu vẽ 1/nhiều mặt cắt: gọi ve_mat_cat cho MỖI mặt cắt được \
liệt kê, đúng loai='dam'/'cot', dùng ĐÚNG số liệu thép đã cho (thanh_duoi/ \
thanh_tren là mảng ĐƯỜNG KÍNH lặp lại từng thanh, không phải số lượng).
- Nếu được yêu cầu lắp ráp mặt đứng khung: gọi lap_rap_mat_dung_khung ĐÚNG 1 \
LẦN, liệt kê ĐỦ mọi phần tử và ĐỦ mọi vị trí của mỗi dầm (không được bỏ sót \
gối trái/giữa nhịp/gối phải).
- Nếu được yêu cầu xuất bản vẽ: gọi xuat_ban_ve.

Nếu thiếu thông tin để vẽ (vd thiếu vị trí nào đó của 1 phần tử), gọi \
hoi_nguoi_dung — không tự suy đoán, không vẽ thiếu rồi báo "xong". Khi đã \
hoàn tất đúng nhiệm vụ được giao trong tin nhắn đầu, dừng lại và tóm tắt kết \
quả bằng văn bản — không gọi thêm tool nào nữa.
"""
    skill = _doc_skill_ve_ky_thuat()
    if skill:
        prompt += (
            "\n\n# TÀI LIỆU THAM KHẢO BẮT BUỘC — cẩm nang thao tác vẽ chi tiết\n"
            "Dưới đây là toàn văn cẩm nang trình bày bản vẽ bố trí thép BTCT (khổ giấy, hệ nét, "
            "mặt cắt, cách ghi số hiệu, bảng thống kê...). Đây là QUY TẮC TRÌNH BÀY ĐÃ ĐƯỢC DUYỆT — "
            "dùng làm căn cứ khi quyết định NÊN yêu cầu vẽ gì/ở đâu (vd vị trí đặt mặt cắt theo Phần "
            "E.1, quy tắc ghi số hiệu ở Phần E.4/G). Phần HÌNH HỌC/LAYER/NÉT VẼ THẬT do code "
            "(geometry.py/layers.py) tự quyết định khi bạn gọi tool — bạn KHÔNG tự vẽ tay từng nét, "
            "chỉ dùng tài liệu này để gọi tool đúng, đủ, đúng thứ tự.\n\n"
            f"{skill}"
        )
    return prompt


HE_THONG_PROMPT = _xay_dung_he_thong_prompt()


def chay_drawing_agent(
    nha_cung_cap: agent.NhaCungCapChat,
    yeu_cau: str,
    phien_cad: PhienCAD,
    hoi_nguoi_dung: HamHoiNguoiDung,
    so_lan_goi_toi_da: int = 15,
) -> agent.KetQuaVongLapAgent:
    nc = NguCanhDrawing(hoi_nguoi_dung=hoi_nguoi_dung, phien_cad=phien_cad)
    dispatch = tao_dispatch(nc)
    return agent.chay_vong_lap_tool(
        nha_cung_cap=nha_cung_cap, he_thong=HE_THONG_PROMPT, tin_nhan_dau=yeu_cau,
        tools=DINH_NGHIA_TOOL, dispatch=dispatch, so_lan_goi_toi_da=so_lan_goi_toi_da,
    )
