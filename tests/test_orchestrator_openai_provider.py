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


# ---------------------------------------------------------------- 429 rate limit (TPM) — lỗi thật khi chạy bộ skill lớn


def _loi_429(thong_diep):
    import httpx
    import openai

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    return openai.RateLimitError(thong_diep, response=httpx.Response(429, request=req), body=None)


def test_thoi_gian_cho_doc_tu_thong_diep():
    from src.orchestrator import agent

    assert agent._thoi_gian_cho_rate_limit("Please try again in 1.073s. Visit", 1) == pytest_approx(2.073)
    assert agent._thoi_gian_cho_rate_limit("Please try again in 250ms.", 1) == 2.0  # chặn dưới
    assert agent._thoi_gian_cho_rate_limit("try again in 2m3.5s", 1) == 70.0  # chặn trên
    assert agent._thoi_gian_cho_rate_limit("không có gợi ý", 2) == 15.0


def pytest_approx(x):
    import pytest

    return pytest.approx(x)


def test_rate_limit_duoc_thu_lai_roi_thanh_cong(monkeypatch):
    from src.orchestrator import agent

    ngu = []
    monkeypatch.setattr(agent.time, "sleep", lambda s: ngu.append(s))
    lan = {"n": 0}

    def goi():
        lan["n"] += 1
        if lan["n"] < 3:
            raise _loi_429("Rate limit reached ... Please try again in 1.0s.")
        return "ok"

    assert agent._thu_lai_khi_mang_loi(goi) == "ok"
    assert lan["n"] == 3 and len(ngu) == 2


def test_het_tien_khong_thu_lai(monkeypatch):
    import pytest

    from src.orchestrator import agent

    monkeypatch.setattr(agent.time, "sleep", lambda s: None)

    def goi():
        raise _loi_429("You exceeded your current quota: insufficient_quota")

    with pytest.raises(Exception):
        agent._thu_lai_khi_mang_loi(goi)


def test_rate_limit_qua_nhieu_lan_van_raise(monkeypatch):
    import pytest

    from src.orchestrator import agent

    monkeypatch.setattr(agent.time, "sleep", lambda s: None)
    monkeypatch.setattr(agent, "SO_LAN_RATE_LIMIT", 3)
    dem = {"n": 0}

    def goi():
        dem["n"] += 1
        raise _loi_429("try again in 1s")

    with pytest.raises(Exception):
        agent._thu_lai_khi_mang_loi(goi)
    assert dem["n"] == 4  # 1 lần đầu + 3 lần thử lại
