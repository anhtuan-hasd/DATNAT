"""Verification Agent — 1 trong 4 agent LLM riêng biệt (CHANGE_REQUESTS.md
mục 1). Xem đầy đủ vai trò, quy trình, hợp đồng dữ liệu tại
`docs/agents/VERIFICATION_AGENT.md`. Đọc lại bản vẽ AutoCAD TRỰC TIẾP qua COM
(`src/drawing/verify_drawing.py`, các hàm hậu tố `_com`) — không còn `ezdxf`
làm trung gian. Agent này CHỈ đọc và so sánh, KHÔNG BAO GIỜ tự sửa bản vẽ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ...drawing import layers, verify_drawing
from .. import agent
from ..loops import BoDemVongLap
from ..shared import doc_skill
from ..shared.hoi_nguoi_dung_tool import DINH_NGHIA_HOI_NGUOI_DUNG, hoi_nguoi_dung
from ..shared.phien_cad import PhienCAD

HamHoiNguoiDung = Callable[[str, list[str] | None], str]


@dataclass
class NguCanhVerification:
    hoi_nguoi_dung: HamHoiNguoiDung
    phien_cad: PhienCAD
    # BoDemVongLap TRUYỀN VÀO TỪ NGOÀI (pipeline.py), KHÔNG tự tạo mới ở đây
    # — khác với Rule Engine Agent (tự sửa xảy ra TRONG 1 phiên LLM duy
    # nhất). Ở đây mỗi lần kiểm chứng lại là 1 PHIÊN LLM RIÊNG (Verification
    # Agent chạy xong thì kết thúc, Drawing Agent sửa xong lại gọi
    # Verification Agent MỚI) — bộ đếm phải sống XUYÊN SUỐT nhiều phiên, nên
    # phải do pipeline.py giữ và truyền vào, đúng như CHANGE_REQUESTS.md mục
    # 1 đã ghi rõ.
    bo_dem: BoDemVongLap


def kiem_chung_ban_ve(nc: NguCanhVerification, dau_vao: dict) -> dict:
    loai_kiem_tra = dau_vao.get("loai_kiem_tra", "mat_cat")
    doc = nc.phien_cad.doc
    vi_pham: list[str] = []

    lop_la = verify_drawing.lop_khong_hop_le_com(doc)
    if lop_la:
        vi_pham.append(f"Layer không thuộc quy ước mục 10.7.2: {lop_la}")

    if loai_kiem_tra == "mat_cat":
        vi_pham.extend(_kiem_tra_mat_cat(doc, dau_vao))
    elif loai_kiem_tra == "mat_dung_khung":
        vi_pham.extend(_kiem_tra_mat_dung_khung(doc, dau_vao))
    else:
        return {"loi": f"loai_kiem_tra phải là 'mat_cat' hoặc 'mat_dung_khung', nhận '{loai_kiem_tra}'."}

    ket_qua: dict[str, Any] = {"dat": not vi_pham, "vi_pham": vi_pham}
    if vi_pham:
        con_duoc = nc.bo_dem.ghi_nhan_1_lan_thu("kiem_chung_ve")
        ket_qua["so_lan_con_lai"] = nc.bo_dem.so_lan_con_lai("kiem_chung_ve")
        if not con_duoc:
            ket_qua["het_luot_kiem_chung"] = True
            ket_qua["huong_dan"] = (
                "Đã hết số lần thử vẽ lại cho phép — KHÔNG gọi kiem_chung_ban_ve/yêu cầu vẽ lại nữa, "
                "phải gọi hoi_nguoi_dung để báo cáo bản vẽ chưa đạt."
            )
    return ket_qua


def _kiem_tra_mat_cat(doc: Any, dau_vao: dict) -> list[str]:
    vi_pham: list[str] = []
    b_ky_vong, h_ky_vong = dau_vao.get("b_ky_vong"), dau_vao.get("h_ky_vong")
    if b_ky_vong and h_ky_vong:
        hop = verify_drawing.hop_gioi_han_da_giac_com(doc, layers.OUTLINE_CUT.ten)
        if not verify_drawing.khop_kich_thuoc_nao_do(hop, b_ky_vong, h_ky_vong):
            vi_pham.append(f"Không tìm thấy mặt cắt nào có kích thước {b_ky_vong}x{h_ky_vong}mm trong bản vẽ.")

    nhan_ky_vong = dau_vao.get("nhan_ky_vong")
    if nhan_ky_vong:
        thieu = verify_drawing.kiem_tra_nhan_mat_cat_day_du_com(doc, nhan_ky_vong)
        if thieu:
            vi_pham.append(f"Thiếu nhãn mặt cắt: {thieu}")
    return vi_pham


def _kiem_tra_mat_dung_khung(doc: Any, dau_vao: dict) -> list[str]:
    """Kiểm tra MỞ RỘNG cho bản vẽ tổng thể — docs/agents/VERIFICATION_AGENT.md
    mục 2 (trước đây CHƯA có, CHANGE_REQUESTS.md mục 2)."""
    vi_pham: list[str] = []

    so_cot_ky_vong, so_dam_ky_vong = dau_vao.get("so_cot_ky_vong"), dau_vao.get("so_dam_ky_vong")
    if so_cot_ky_vong is not None and so_dam_ky_vong is not None:
        so_thuc = verify_drawing.dem_da_giac_theo_layer_com(doc, layers.OUTLINE.ten)
        # >= chứ không phải == : khung tên (ve_khung_ten) cũng vẽ 1 đường bao
        # trên layer OUTLINE (+1), nên tổng thực tế luôn >= so_cot+so_dam.
        # Quan trọng nhất là bắt được đúng lớp lỗi đã biết ("chỉ có 1 cấu
        # kiện trong khi dữ liệu có nhiều hơn") — dùng >= vẫn chặn được lỗi
        # đó chắc chắn, không cần biết chính xác +1 hay +N khung tên phụ.
        if so_thuc < so_cot_ky_vong + so_dam_ky_vong:
            vi_pham.append(
                f"Số cấu kiện vẽ ra ({so_thuc}, kể cả khung tên) ít hơn kỳ vọng "
                f"({so_cot_ky_vong} cột + {so_dam_ky_vong} dầm = {so_cot_ky_vong + so_dam_ky_vong}) "
                "— nghi thiếu cấu kiện trong bản vẽ tổng thể."
            )

    # Đếm số VÒNG TRÒN SỐ HIỆU (layer SO_HIEU) đã vẽ — thay cho dò TEXT chứa
    # tên vị trí "goi_trai"/"giua_nhip"/"goi_phai" (hệ ký hiệu số hiệu MỚI,
    # mục 2.2 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md, không còn ghi các tên vị trí
    # này thành chữ tìm được nữa — chỉ còn số hiệu trong vòng tròn).
    so_ky_hieu_ky_vong = dau_vao.get("so_ky_hieu_ky_vong")
    if so_ky_hieu_ky_vong is not None:
        so_ky_hieu_thuc = verify_drawing.dem_vong_tron_theo_layer_com(doc, layers.SO_HIEU.ten)
        if so_ky_hieu_thuc < so_ky_hieu_ky_vong:
            vi_pham.append(
                f"Số vòng tròn ký hiệu số hiệu thanh thép vẽ ra ({so_ky_hieu_thuc}) ít hơn kỳ vọng "
                f"({so_ky_hieu_ky_vong}) — nghi thiếu ký hiệu thép ở 1 số vị trí."
            )

    ten_truc_ky_vong = dau_vao.get("ten_truc_ky_vong")
    if ten_truc_ky_vong:
        so_vong_tron = verify_drawing.dem_vong_tron_theo_layer_com(doc, layers.AXIS.ten)
        if so_vong_tron < len(ten_truc_ky_vong):
            vi_pham.append(
                f"Chỉ có {so_vong_tron} vòng tròn ký hiệu trục, kỳ vọng ít nhất {len(ten_truc_ky_vong)} "
                f"(1 mỗi trục: {ten_truc_ky_vong})."
            )

    if dau_vao.get("can_co_bang_thong_ke", True):
        thieu_cot = verify_drawing.kiem_tra_bang_thong_ke_du_cot_com(doc)
        if thieu_cot:
            vi_pham.append(f"Bảng thống kê thép thiếu cột (mục 3.9, 8 cột bắt buộc): {thieu_cot}")

    return vi_pham


# ---------------------------------------------------------------------------
# Đăng ký tool.
# ---------------------------------------------------------------------------

DINH_NGHIA_TOOL: list[dict] = [
    {
        "name": "kiem_chung_ban_ve",
        "description": (
            "Đọc lại bản vẽ AutoCAD hiện tại (qua COM) để đối chiếu layer/kích thước/nhãn. "
            "loai_kiem_tra='mat_cat' (mặc định): kiểm tra 1 mặt cắt vừa vẽ. loai_kiem_tra="
            "'mat_dung_khung': kiểm tra MỞ RỘNG cho bản vẽ tổng thể đã lắp ráp — số cấu kiện, nhãn "
            "thép đủ vị trí, vòng tròn ký hiệu trục, bảng thống kê đủ cột."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loai_kiem_tra": {"type": "string", "enum": ["mat_cat", "mat_dung_khung"]},
                "b_ky_vong": {"type": "number"}, "h_ky_vong": {"type": "number"},
                "nhan_ky_vong": {"type": "array", "items": {"type": "string"}},
                "so_cot_ky_vong": {"type": "integer"}, "so_dam_ky_vong": {"type": "integer"},
                "so_ky_hieu_ky_vong": {
                    "type": "integer",
                    "description": "Tổng số vòng tròn ký hiệu số hiệu thanh thép kỳ vọng — lấy nguyên từ kết quả lap_rap_mat_dung_khung.",
                },
                "ten_truc_ky_vong": {"type": "array", "items": {"type": "string"}},
                "can_co_bang_thong_ke": {"type": "boolean", "description": "Mặc định true."},
            },
        },
    },
    DINH_NGHIA_HOI_NGUOI_DUNG,
]

_HAM_THEO_TEN: dict[str, Callable[[NguCanhVerification, dict], dict]] = {
    "kiem_chung_ban_ve": kiem_chung_ban_ve,
    "hoi_nguoi_dung": hoi_nguoi_dung,
}


def tao_dispatch(nc: NguCanhVerification) -> dict[str, Callable[[dict], dict]]:
    return {ten: (lambda dau_vao, _ham=ham: _ham(nc, dau_vao)) for ten, ham in _HAM_THEO_TEN.items()}


# ---------------------------------------------------------------------------
# System prompt + hàm chạy 1 phiên độc lập.
# ---------------------------------------------------------------------------

_HE_THONG_PROMPT_GOC = """\
Bạn là Verification Agent trong hệ thống thiết kế khung BTCT theo TCVN \
5574:2018 (đọc chi tiết: docs/agents/VERIFICATION_AGENT.md). Bạn CHỈ đọc lại \
bản vẽ AutoCAD hiện tại và so sánh với dữ liệu/quy ước — KHÔNG BAO GIỜ tự \
sửa bản vẽ, không gọi bất kỳ tool vẽ nào.

Đọc kỹ tin nhắn đầu để biết đang kiểm tra 1 mặt cắt hay bản vẽ tổng thể, rồi \
gọi kiem_chung_ban_ve với đúng loai_kiem_tra và tham số kỳ vọng được cho.

Nếu "dat"=false: đọc "so_lan_con_lai". Nếu còn > 0, tóm tắt "vi_pham" thật \
CỤ THỂ (không chỉ nói "sai", nói rõ thiếu gì/lệch bao nhiêu) trong câu trả \
lời cuối cùng để Drawing Agent sửa đúng chỗ. Nếu "het_luot_kiem_chung"=true, \
BẮT BUỘC gọi hoi_nguoi_dung báo cáo toàn bộ vi_pham còn lại — KHÔNG gọi lại \
kiem_chung_ban_ve.

Khi đã có kết quả (đạt hoặc đã báo cáo người dùng), dừng lại và tóm tắt bằng \
văn bản — không gọi thêm tool nào nữa.
"""

# Skill kiểm chứng của kỹ sư: tool kiểm được gì, việc nào chỉ báo cáo/dừng, các mâu thuẫn đã biết (không báo lỗi giả).
_DUONG_DAN_SKILL_KIEM_CHUNG = doc_skill.THU_MUC_AGENTS / "huongdankiemchung" / "SKILL_KIEM_CHUNG_KY_SU.md"


def _xay_dung_he_thong_prompt() -> str:
    return doc_skill.ghep_skill_vao_prompt(
        _HE_THONG_PROMPT_GOC, doc_skill.doc_file_skill(_DUONG_DAN_SKILL_KIEM_CHUNG),
        "TÀI LIỆU THAM KHẢO BẮT BUỘC — skill kiểm chứng của kỹ sư",
        "Dưới đây là skill kiểm chứng: ranh giới giữa việc tool đọc được và việc chỉ kiểm bằng dữ liệu/báo cáo, "
        "cách viết vi_pham cụ thể, và các mâu thuẫn tài liệu đã biết. KHÔNG in 'ĐẠT' khi còn hạng mục chưa kiểm được.",
    )


HE_THONG_PROMPT = _xay_dung_he_thong_prompt()


def chay_verification_agent(
    nha_cung_cap: agent.NhaCungCapChat,
    yeu_cau: str,
    phien_cad: PhienCAD,
    bo_dem: BoDemVongLap,
    hoi_nguoi_dung: HamHoiNguoiDung,
    so_lan_goi_toi_da: int = 5,
) -> agent.KetQuaVongLapAgent:
    nc = NguCanhVerification(hoi_nguoi_dung=hoi_nguoi_dung, phien_cad=phien_cad, bo_dem=bo_dem)
    dispatch = tao_dispatch(nc)
    return agent.chay_vong_lap_tool(
        nha_cung_cap=nha_cung_cap, he_thong=HE_THONG_PROMPT, tin_nhan_dau=yeu_cau,
        tools=DINH_NGHIA_TOOL, dispatch=dispatch, so_lan_goi_toi_da=so_lan_goi_toi_da,
    )
