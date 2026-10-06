"""
Vòng lặp tool-calling tổng quát với LLM điều phối — nơi DUY NHẤT trong toàn
hệ thống gọi LLM để RA QUYẾT ĐỊNH (gọi tool nào tiếp theo, có cần hỏi người
dùng không, diễn giải kết quả/lỗi) — KHÔNG BAO GIỜ dùng để tính số
(TONGQUAN_AI_AGENT.md mục 3, mục 4). Theo quyết định hiện tại của đồ án
(docs/TONGQUAN_AI_AGENT.md mục 4/7), LLM DUY NHẤT dùng trong toàn hệ thống là
**OpenAI GPT** (qua OpenAI API, Chat Completions tool-calling) — không dùng
LLM/nhà cung cấp khác ở bất kỳ đâu trong pipeline.

Toàn bộ logic vòng lặp (chay_vong_lap_tool) được viết theo 1 định dạng nội bộ
CỐ ĐỊNH cho messages/response — cùng hình dạng "content block" mà Anthropic
Messages API dùng (đã chọn làm chuẩn nội bộ vì rõ ràng, có type tường minh
cho từng khối "text"/"tool_use"/"tool_result"). `OpenAIChatProvider` chuyển
đổi qua lại giữa định dạng OpenAI Chat Completions và định dạng nội bộ này ở
đúng 1 lớp biên (`_messages_noi_bo_sang_openai`/`_response_openai_sang_noi_bo`)
— nhờ vậy `chay_vong_lap_tool`, `tools.py`, `pipeline.py` không cần biết/quan
tâm nhà cung cấp LLM thực sự là ai.

Tách khỏi SDK cụ thể qua Protocol `NhaCungCapChat` để test được bằng giả lập
(FakeChatProvider script sẵn kịch bản hội thoại), không cần API key thật —
cùng cách làm đã dùng ở input_adapter/llm_mapping.py.

An toàn vòng lặp: `so_lan_goi_toi_da` là giới hạn CỨNG tổng số lượt gọi model
cho 1 lần chạy — đây là lớp bảo vệ ngoài cùng (phòng trường hợp model kẹt
vòng lặp gọi tool không lối thoát); các giới hạn CHI TIẾT hơn cho từng loại
vòng lặp (tự sửa, kiểm chứng vẽ) nằm ở loops.BoDemVongLap và được tools.py
báo cáo lại cho model qua chính nội dung tool_result.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, TypeVar

_T = TypeVar("_T")


def _thu_lai_khi_mang_loi(ham: Callable[[], _T], so_lan_toi_da: int = 5, cho_giay: float = 2.0) -> _T:
    """Gọi 1 hàm gọi OpenAI API, tự thử lại (backoff tuyến tính) khi gặp lỗi
    MẠNG thoáng qua (mất kết nối/timeout khi bắt tay TLS...) — LỖI THẬT đã
    gặp khi chạy thật (pipeline dài ~15-20 phút, hàng trăm lượt gọi model):
    dù `openai.OpenAI` client đã tự retry nội bộ (mặc định 2 lần), 1 lần mất
    mạng đủ dài (vd Wi-Fi chập chờn) vẫn vượt quá số lần retry nội bộ đó,
    làm SẬP TOÀN BỘ pipeline giữa chừng (mất hết tiến độ ~20 phút đã chạy,
    kể cả các phần tử đã xong) chỉ vì 1 lần mạng chập — không phải lỗi logic
    ở đâu trong code. Lỗi KHÔNG PHẢI về mạng (400 sai tham số, 401 sai API
    key...) vẫn raise ngay, không nuốt lỗi mù quáng."""
    import openai

    loi_cuoi: Exception | None = None
    for lan in range(so_lan_toi_da):
        try:
            return ham()
        except (openai.APIConnectionError, openai.APITimeoutError) as e:
            loi_cuoi = e
            time.sleep(cho_giay * (lan + 1))
    assert loi_cuoi is not None
    raise loi_cuoi


class NhaCungCapChat(Protocol):
    def goi(self, he_thong: str, messages: list[dict], tools: list[dict]) -> dict:
        """Trả về 1 message response thô theo ĐÚNG định dạng nội bộ (dạng
        content-block kiểu Anthropic Messages API): {"content": [...]}, mỗi
        phần tử content là {"type": "text", "text": ...} hoặc {"type":
        "tool_use", "id": ..., "name": ..., "input": {...}}."""
        ...


class OpenAIChatProvider:
    """Cài đặt CHÍNH THỨC của đồ án — dùng OpenAI API (Chat Completions +
    function calling). Import `openai` BÊN TRONG __init__ (không phải đầu
    file) để agent.py vẫn import được trên môi trường chưa cài `openai`,
    cùng cách làm đã dùng cho `anthropic` trước đây ở llm_mapping.py.

    Mặc định dùng `gpt-5.6-luna` — model rẻ nhất trong dòng GPT-5.6 (GA
    07/2026) vẫn hỗ trợ đầy đủ function calling, phù hợp cho việc test pipeline
    lặp nhiều vòng tool-calling mà không tốn kém. Đổi `model` nếu cần model
    mạnh hơn (vd "gpt-5.6-sol", "gpt-5.6-terra").

    `max_completion_tokens` (KHÔNG phải `max_tokens` — model này từ chối tham
    số cũ, đã xác nhận qua lỗi 400 thật khi test) mặc định 1024, đủ cho 1 lượt
    quyết định + gọi tool mà không để model "nói dài" tốn phí ngoài ý muốn.

    `reasoning_effort="none"` là BẮT BUỘC mặc định cho gpt-5.6-luna khi dùng
    kèm `tools` trên endpoint Chat Completions — đã xác nhận qua lỗi 400 thật
    khi test ("Function tools with reasoning_effort are not supported for
    gpt-5.6-luna in /v1/chat/completions... set reasoning_effort to 'none'").
    Đổi thành None (không gửi tham số) nếu dùng model không hỗ trợ tham số
    này (vd các model đời cũ hơn GPT-5.6).
    """

    def __init__(
        self,
        model: str = "gpt-5.6-luna",
        api_key: str | None = None,
        max_completion_tokens: int = 1024,
        reasoning_effort: str | None = "none",
    ):
        import openai

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._max_completion_tokens = max_completion_tokens
        self._reasoning_effort = reasoning_effort

    def goi(self, he_thong: str, messages: list[dict], tools: list[dict]) -> dict:
        openai_messages = _messages_noi_bo_sang_openai(he_thong, messages)
        openai_tools = _tools_noi_bo_sang_openai(tools) if tools else None
        tham_so_them = {"reasoning_effort": self._reasoning_effort} if self._reasoning_effort else {}

        def _goi_1_lan():
            return self._client.chat.completions.create(
                model=self._model,
                messages=openai_messages,
                tools=openai_tools,
                max_completion_tokens=self._max_completion_tokens,
                **tham_so_them,
            )

        resp = _thu_lai_khi_mang_loi(_goi_1_lan)
        return _response_openai_sang_noi_bo(resp.choices[0].message)


class ClaudeChatProvider:
    """Cài đặt THAY THẾ (không phải lựa chọn chính thức hiện tại — xem
    docstring đầu file) dùng Anthropic SDK, giữ lại vì cùng Protocol
    `NhaCungCapChat` nên không tốn thêm chi phí bảo trì. Định dạng nội bộ ở
    đây trùng khớp gần như nguyên vẹn với Anthropic Messages API nên KHÔNG
    cần lớp chuyển đổi như OpenAIChatProvider."""

    def __init__(self, model: str = "claude-sonnet-5", api_key: str | None = None, max_tokens: int = 4096):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def goi(self, he_thong: str, messages: list[dict], tools: list[dict]) -> dict:
        resp = self._client.messages.create(
            model=self._model, max_tokens=self._max_tokens, system=he_thong, messages=messages, tools=tools,
        )
        return resp.model_dump()


# ---------------------------------------------------------------------------
# Lớp chuyển đổi định dạng nội bộ (dạng content-block) <-> OpenAI Chat
# Completions — CHỈ dùng bởi OpenAIChatProvider, không rò rỉ ra chỗ khác.
# ---------------------------------------------------------------------------


def _tools_noi_bo_sang_openai(tools: list[dict]) -> list[dict]:
    """tools.DINH_NGHIA_TOOL (dạng {name, description, input_schema}, đúng
    khuôn Anthropic tool-use) -> dạng OpenAI ({"type":"function","function":
    {name, description, parameters}})."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in tools
    ]


def _messages_noi_bo_sang_openai(he_thong: str, messages: list[dict]) -> list[dict]:
    """Toàn bộ lịch sử hội thoại dạng nội bộ (content-block) -> dạng OpenAI
    Chat Completions (mỗi tool_result thành 1 message role="tool" riêng)."""
    ket_qua: list[dict] = [{"role": "system", "content": he_thong}]

    for m in messages:
        vai_tro = m["role"]
        noi_dung = m["content"]

        if isinstance(noi_dung, str):
            ket_qua.append({"role": vai_tro, "content": noi_dung})
            continue

        if vai_tro == "assistant":
            doan_text = [b["text"] for b in noi_dung if b.get("type") == "text"]
            cac_tool_use = [b for b in noi_dung if b.get("type") == "tool_use"]
            tin_nhan: dict[str, Any] = {"role": "assistant", "content": "\n".join(doan_text) or None}
            if cac_tool_use:
                tin_nhan["tool_calls"] = [
                    {
                        "id": b["id"],
                        "type": "function",
                        "function": {
                            "name": b["name"],
                            "arguments": json.dumps(b.get("input", {}), ensure_ascii=False),
                        },
                    }
                    for b in cac_tool_use
                ]
            ket_qua.append(tin_nhan)
        else:  # role == "user" — có thể chứa tool_result (kết quả gọi tool) hoặc text thường
            cac_tool_result = [b for b in noi_dung if b.get("type") == "tool_result"]
            if cac_tool_result:
                for b in cac_tool_result:
                    ket_qua.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": b["content"]})
            else:
                doan_text = [b.get("text", "") for b in noi_dung if b.get("type") == "text"]
                ket_qua.append({"role": "user", "content": "\n".join(doan_text)})

    return ket_qua


def _response_openai_sang_noi_bo(message: Any) -> dict:
    """1 message trả về từ OpenAI (choices[0].message) -> dạng nội bộ
    {"content": [...]} (danh sách block "text"/"tool_use")."""
    content: list[dict] = []
    if message.content:
        content.append({"type": "text", "text": message.content})
    for tc in (message.tool_calls or []):
        try:
            du_lieu_vao = json.loads(tc.function.arguments) if tc.function.arguments else {}
        except json.JSONDecodeError:
            du_lieu_vao = {}
        content.append({"type": "tool_use", "id": tc.id, "name": tc.function.name, "input": du_lieu_vao})
    return {"content": content}


def _noi_dung_thanh_text(gia_tri: Any) -> str:
    return json.dumps(gia_tri, ensure_ascii=False, default=str)


@dataclass
class KetQuaVongLapAgent:
    messages: list[dict] = field(default_factory=list)
    so_lan_goi_model: int = 0
    dung_vi: str = "chua_chay"  # "end_turn" | "het_luot_toi_da" | "loi"
    nhat_ky_tool: list[dict] = field(default_factory=list)  # [{ten, dau_vao, ket_qua}, ...] — phục vụ log/audit


def chay_vong_lap_tool(
    nha_cung_cap: NhaCungCapChat,
    he_thong: str,
    tin_nhan_dau: str,
    tools: list[dict],
    dispatch: dict[str, Callable[[dict], dict]],
    so_lan_goi_toi_da: int = 20,
) -> KetQuaVongLapAgent:
    """Chạy vòng lặp: gửi tin nhắn + tools cho model → nếu model trả
    tool_use, thực thi qua dispatch rồi gửi tool_result quay lại → lặp đến
    khi model không còn gọi tool nào nữa (end_turn) hoặc hết so_lan_goi_toi_da.
    """
    ket_qua = KetQuaVongLapAgent(messages=[{"role": "user", "content": tin_nhan_dau}])

    for lan in range(1, so_lan_goi_toi_da + 1):
        resp = nha_cung_cap.goi(he_thong, ket_qua.messages, tools)
        ket_qua.so_lan_goi_model = lan
        noi_dung = resp.get("content", [])
        ket_qua.messages.append({"role": "assistant", "content": noi_dung})

        tool_use_blocks = [b for b in noi_dung if b.get("type") == "tool_use"]
        if not tool_use_blocks:
            ket_qua.dung_vi = "end_turn"
            return ket_qua

        tool_results = []
        for block in tool_use_blocks:
            ten_tool = block["name"]
            dau_vao = block.get("input", {})
            ham = dispatch.get(ten_tool)
            if ham is None:
                ket_qua_tool = {"loi": f"Tool '{ten_tool}' không tồn tại trong dispatch."}
            else:
                try:
                    ket_qua_tool = ham(dau_vao)
                except Exception as e:
                    ket_qua_tool = {"loi": f"Lỗi khi chạy tool '{ten_tool}': {e}"}

            ket_qua.nhat_ky_tool.append({"ten": ten_tool, "dau_vao": dau_vao, "ket_qua": ket_qua_tool})
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block["id"], "content": _noi_dung_thanh_text(ket_qua_tool)}
            )
        ket_qua.messages.append({"role": "user", "content": tool_results})

    ket_qua.dung_vi = "het_luot_toi_da"
    return ket_qua
