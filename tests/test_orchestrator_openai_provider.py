"""
Test lớp chuyển đổi định dạng nội bộ <-> OpenAI Chat Completions —
src/orchestrator/agent.py (OpenAIChatProvider + các hàm _*_sang_*).

Không gọi mạng: OpenAIChatProvider được khởi tạo bình thường (api_key giả,
`openai.OpenAI(...)` không tự gọi mạng lúc khởi tạo) rồi thay `._client` bằng
1 client giả lập để kiểm tra đúng luồng chuyển đổi.
"""

from types import SimpleNamespace

from src.orchestrator import agent


def _tool_call_gia(id_, ten, arguments_json_str):
    return SimpleNamespace(id=id_, function=SimpleNamespace(name=ten, arguments=arguments_json_str))


def _message_gia(content=None, tool_calls=None):
    return SimpleNamespace(content=content, tool_calls=tool_calls)


class FakeOpenAIClient:
    """Giả lập client.chat.completions.create — trả về response đã script sẵn."""

    def __init__(self, message_tra_ve):
        self._message = message_tra_ve
        self.cuoc_goi_gan_nhat: dict | None = None
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages, tools=None, max_completion_tokens=None, reasoning_effort=None):
        self.cuoc_goi_gan_nhat = {"model": model, "messages": messages, "tools": tools}
        return SimpleNamespace(choices=[SimpleNamespace(message=self._message)])


def _tao_provider(message_tra_ve) -> tuple[agent.OpenAIChatProvider, FakeOpenAIClient]:
    provider = agent.OpenAIChatProvider(api_key="fake-key-khong-can-that")
    fake_client = FakeOpenAIClient(message_tra_ve)
    provider._client = fake_client
    return provider, fake_client


def test_tools_noi_bo_sang_openai():
    tools = [{"name": "cong", "description": "Cộng 2 số", "input_schema": {"type": "object", "properties": {"a": {"type": "number"}}}}]
    ket_qua = agent._tools_noi_bo_sang_openai(tools)
    assert ket_qua == [
        {
            "type": "function",
            "function": {
                "name": "cong", "description": "Cộng 2 số",
                "parameters": {"type": "object", "properties": {"a": {"type": "number"}}},
            },
        }
    ]


def test_messages_noi_bo_sang_openai_tin_nhan_dau_la_string():
    ket_qua = agent._messages_noi_bo_sang_openai("he thong", [{"role": "user", "content": "xin chao"}])
    assert ket_qua == [{"role": "system", "content": "he thong"}, {"role": "user", "content": "xin chao"}]


def test_messages_noi_bo_sang_openai_assistant_tool_use():
    messages = [
        {"role": "user", "content": "yeu cau"},
        {"role": "assistant", "content": [
            {"type": "text", "text": "de tinh"},
            {"type": "tool_use", "id": "call_1", "name": "cong", "input": {"a": 1, "b": 2}},
        ]},
    ]
    ket_qua = agent._messages_noi_bo_sang_openai("he thong", messages)
    assistant_msg = ket_qua[2]
    assert assistant_msg["role"] == "assistant"
    assert assistant_msg["content"] == "de tinh"
    assert assistant_msg["tool_calls"] == [
        {"id": "call_1", "type": "function", "function": {"name": "cong", "arguments": '{"a": 1, "b": 2}'}}
    ]


def test_messages_noi_bo_sang_openai_tool_result():
    messages = [{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": '{"tong": 3}'}]}]
    ket_qua = agent._messages_noi_bo_sang_openai("he thong", messages)
    assert ket_qua[1] == {"role": "tool", "tool_call_id": "call_1", "content": '{"tong": 3}'}


def test_response_openai_sang_noi_bo_chi_co_text():
    ket_qua = agent._response_openai_sang_noi_bo(_message_gia(content="xong roi"))
    assert ket_qua == {"content": [{"type": "text", "text": "xong roi"}]}


def test_response_openai_sang_noi_bo_co_tool_call():
    msg = _message_gia(content=None, tool_calls=[_tool_call_gia("call_1", "cong", '{"a": 1, "b": 2}')])
    ket_qua = agent._response_openai_sang_noi_bo(msg)
    assert ket_qua == {"content": [{"type": "tool_use", "id": "call_1", "name": "cong", "input": {"a": 1, "b": 2}}]}


def test_response_openai_sang_noi_bo_json_hong_khong_sap():
    msg = _message_gia(content=None, tool_calls=[_tool_call_gia("call_1", "cong", "khong phai json")])
    ket_qua = agent._response_openai_sang_noi_bo(msg)
    assert ket_qua["content"][0]["input"] == {}


def test_openai_chat_provider_goi_dung_dinh_dang():
    provider, fake_client = _tao_provider(_message_gia(content="ok"))
    ket_qua = provider.goi("he thong", [{"role": "user", "content": "hoi"}], tools=[])
    assert ket_qua == {"content": [{"type": "text", "text": "ok"}]}
    assert fake_client.cuoc_goi_gan_nhat["messages"][0] == {"role": "system", "content": "he thong"}


def test_openai_chat_provider_qua_agent_loop_toan_trinh():
    """Chạy OpenAIChatProvider (đã giả lập client) qua đúng chay_vong_lap_tool
    dùng chung với ClaudeChatProvider — xác nhận lớp chuyển đổi không làm hỏng
    cơ chế vòng lặp tool-calling đã kiểm chứng ở test_orchestrator_agent.py."""
    tool_call_msg = _message_gia(content=None, tool_calls=[_tool_call_gia("call_1", "cong", '{"a": 2, "b": 3}')])
    final_msg = _message_gia(content="Kết quả là 5.")

    provider = agent.OpenAIChatProvider(api_key="fake")
    fake_client = FakeOpenAIClient(tool_call_msg)
    lan_goi = {"n": 0}

    def create_lan_luot(model, messages, tools=None, max_completion_tokens=None, reasoning_effort=None):
        lan_goi["n"] += 1
        msg = tool_call_msg if lan_goi["n"] == 1 else final_msg
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    fake_client.chat.completions.create = create_lan_luot
    provider._client = fake_client

    dispatch = {"cong": lambda dau_vao: {"tong": dau_vao["a"] + dau_vao["b"]}}
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "cong 2+3", tools=[], dispatch=dispatch)

    assert ket_qua.dung_vi == "end_turn"
    assert ket_qua.nhat_ky_tool == [{"ten": "cong", "dau_vao": {"a": 2, "b": 3}, "ket_qua": {"tong": 5}}]
