"""Tool `hoi_nguoi_dung` — DÙNG CHUNG cho cả 4 agent (mọi vòng lặp cần xác
nhận/leo thang cho người dùng thật đều gọi qua đây). Trước đây (kiến trúc 1
agent) tool này chỉ khai báo 1 lần trong `tools.py`; nay tách 4 agent thành 4
file riêng, nếu mỗi file tự khai báo lại `hoi_nguoi_dung` sẽ trùng lặp định
nghĩa 4 lần — module này tồn tại CHỈ để tránh lặp đó (1 nguồn sự thật duy
nhất cho tool này, sửa 1 chỗ là đủ cho cả 4 agent).

Cách dùng trong 1 file agent (vd `agents/rule_engine_agent.py`):

    from ..shared.hoi_nguoi_dung_tool import DINH_NGHIA_HOI_NGUOI_DUNG, hoi_nguoi_dung

    DINH_NGHIA_TOOL = [..., DINH_NGHIA_HOI_NGUOI_DUNG]
    _HAM_THEO_TEN = {..., "hoi_nguoi_dung": hoi_nguoi_dung}
"""

from __future__ import annotations

from typing import Any, Callable, Protocol


class CoTheHoiNguoiDung(Protocol):
    """Bất kỳ ngữ cảnh agent nào MUỐN dùng tool này đều phải có field
    `hoi_nguoi_dung` kiểu `Callable[[str, list[str] | None], str]` — hàm này
    do lớp gọi pipeline truyền vào lúc khởi tạo ngữ cảnh (terminal: input();
    webapp: chặn thread nền chờ người dùng trả lời qua trang web — xem
    webapp/jobs.py). Bản thân module này không quan tâm cài đặt cụ thể là gì,
    chỉ cần đúng chữ ký hàm."""

    hoi_nguoi_dung: Callable[[str, list[str] | None], str]


DINH_NGHIA_HOI_NGUOI_DUNG: dict = {
    "name": "hoi_nguoi_dung",
    "description": (
        "Hỏi người dùng THẬT khi gặp mơ hồ hoặc đã hết số lần thử lại cho phép của 1 vòng lặp tự sửa/"
        "kiểm chứng — dùng cho MỌI vòng lặp cần xác nhận, không riêng agent nào. Luôn ưu tiên gọi tool "
        "chuyên biệt hơn (vd xac_nhan_anh_xa_voi_nguoi_dung ở Input Adapter Agent) nếu có, chỉ dùng tool "
        "này khi không có tool chuyên biệt phù hợp hoặc khi cần báo cáo kết quả cuối cùng (vi phạm còn "
        "lại, hết lượt thử...)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "cau_hoi": {"type": "string"},
            "lua_chon": {
                "type": "array", "items": {"type": "string"},
                "description": "Danh sách lựa chọn gợi ý cho người dùng, nếu có — để trống nếu câu hỏi tự do.",
            },
        },
        "required": ["cau_hoi"],
    },
}


def hoi_nguoi_dung(nc: CoTheHoiNguoiDung, dau_vao: dict) -> dict[str, Any]:
    """Cài đặt THUẦN của tool — chỉ chuyển tiếp câu hỏi/lựa chọn tới hàm
    `nc.hoi_nguoi_dung` thật (input() dòng lệnh, hoặc callback web) rồi trả
    câu trả lời lại cho LLM dưới dạng tool_result. Không có logic nghiệp vụ
    nào ở đây — nghiệp vụ (khi nào NÊN gọi tool này) nằm trong system prompt
    của từng agent (docs/agents/*.md)."""
    cau_hoi = dau_vao["cau_hoi"]
    lua_chon = dau_vao.get("lua_chon")
    tra_loi = nc.hoi_nguoi_dung(cau_hoi, lua_chon)
    return {"tra_loi": tra_loi}
