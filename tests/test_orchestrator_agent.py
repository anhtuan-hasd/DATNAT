"""Test vòng lặp tool-calling tổng quát — src/orchestrator/agent.py, dùng
FakeChatProvider (kịch bản hội thoại dựng sẵn, KHÔNG gọi Anthropic thật)."""

from src.orchestrator import agent


class FakeChatProvider:
    """Trả về lần lượt các response đã script sẵn, bỏ qua nội dung gửi vào."""

    def __init__(self, kich_ban: list[dict]):
        self._kich_ban = kich_ban
        self._lan_goi = 0
        self.lich_su_goi: list[list[dict]] = []  # lưu lại messages mỗi lần gọi để test kiểm tra

    def goi(self, he_thong, messages, tools):
        self.lich_su_goi.append(messages)
        resp = self._kich_ban[self._lan_goi]
        self._lan_goi += 1
        return resp


def _tool_use(id_, name, input_):
    return {"type": "tool_use", "id": id_, "name": name, "input": input_}


def _text(noi_dung):
    return {"type": "text", "text": noi_dung}


def test_thu_lai_khi_mang_loi_thu_lai_roi_thanh_cong():
    """Hồi quy — LỖI THẬT đã gặp khi chạy thật: pipeline dài ~15-20 phút sập
    HOÀN TOÀN giữa chừng (mất hết tiến độ) chỉ vì 1 lần mạng chập gọi OpenAI
    API (APIConnectionError), dù client `openai` đã tự retry nội bộ nhưng
    không đủ. Khoá lại: `_thu_lai_khi_mang_loi` phải thử lại khi gặp lỗi
    mạng và trả về kết quả ngay khi 1 lần thử thành công, không cần hết
    `so_lan_toi_da`."""
    import httpx2 as httpx
    import openai

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    so_lan_goi = 0

    def _ham():
        nonlocal so_lan_goi
        so_lan_goi += 1
        if so_lan_goi < 3:
            raise openai.APIConnectionError(request=req)
        return "ket_qua_that"

    ket_qua = agent._thu_lai_khi_mang_loi(_ham, so_lan_toi_da=5, cho_giay=0.0)
    assert ket_qua == "ket_qua_that"
    assert so_lan_goi == 3


def test_thu_lai_khi_mang_loi_het_luot_van_raise():
    import httpx2 as httpx
    import openai
    import pytest

    req = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")

    def _luon_loi():
        raise openai.APIConnectionError(request=req)

    with pytest.raises(openai.APIConnectionError):
        agent._thu_lai_khi_mang_loi(_luon_loi, so_lan_toi_da=2, cho_giay=0.0)


def test_thu_lai_khi_mang_loi_khong_nuot_loi_khac():
    """Lỗi KHÔNG PHẢI về mạng (vd sai tham số/logic) phải raise NGAY, không
    bị thử lại vô ích."""
    import pytest

    def _loi_khac():
        raise ValueError("loi logic khong lien quan mang")

    with pytest.raises(ValueError):
        agent._thu_lai_khi_mang_loi(_loi_khac, so_lan_toi_da=3, cho_giay=0.0)


def test_ket_thuc_ngay_khi_khong_goi_tool():
    provider = FakeChatProvider([{"content": [_text("Xin chào, không cần làm gì.")]}])
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "yeu cau", tools=[], dispatch={})
    assert ket_qua.dung_vi == "end_turn"
    assert ket_qua.so_lan_goi_model == 1
    assert ket_qua.nhat_ky_tool == []


def test_goi_1_tool_roi_ket_thuc():
    provider = FakeChatProvider([
        {"content": [_tool_use("t1", "cong", {"a": 1, "b": 2})]},
        {"content": [_text("Kết quả là 3.")]},
    ])
    dispatch = {"cong": lambda dau_vao: {"tong": dau_vao["a"] + dau_vao["b"]}}
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "cong 1+2", tools=[], dispatch=dispatch)

    assert ket_qua.dung_vi == "end_turn"
    assert ket_qua.so_lan_goi_model == 2
    assert ket_qua.nhat_ky_tool == [{"ten": "cong", "dau_vao": {"a": 1, "b": 2}, "ket_qua": {"tong": 3}}]
    # messages: [user(yc), assistant(tool_use), user(tool_result), assistant(text cuối)].
    assert ket_qua.messages[1]["role"] == "assistant"
    assert ket_qua.messages[2]["role"] == "user"
    assert ket_qua.messages[2]["content"][0]["tool_use_id"] == "t1"
    assert ket_qua.messages[-1]["role"] == "assistant"


def test_tool_khong_ton_tai_tra_loi_khong_sap():
    provider = FakeChatProvider([
        {"content": [_tool_use("t1", "khong_ton_tai", {})]},
        {"content": [_text("xong")]},
    ])
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "yc", tools=[], dispatch={})
    assert ket_qua.nhat_ky_tool[0]["ket_qua"] == {"loi": "Tool 'khong_ton_tai' không tồn tại trong dispatch."}
    assert ket_qua.dung_vi == "end_turn"


def test_tool_nem_exception_khong_sap_pipeline():
    def _loi(_dau_vao):
        raise ValueError("hỏng rồi")

    provider = FakeChatProvider([
        {"content": [_tool_use("t1", "loi_tool", {})]},
        {"content": [_text("xong")]},
    ])
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "yc", tools=[], dispatch={"loi_tool": _loi})
    assert "hỏng rồi" in ket_qua.nhat_ky_tool[0]["ket_qua"]["loi"]
    assert ket_qua.dung_vi == "end_turn"


def test_dat_gioi_han_cung_so_lan_goi_toi_da():
    # Kịch bản CỐ TÌNH gọi tool vô hạn (không bao giờ end_turn) — bộ đếm
    # so_lan_goi_toi_da phải chặn lại, không để vòng lặp chạy mãi.
    kich_ban_lap_vo_han = [{"content": [_tool_use(f"t{i}", "lap", {})]} for i in range(100)]
    provider = FakeChatProvider(kich_ban_lap_vo_han)
    ket_qua = agent.chay_vong_lap_tool(
        provider, "he thong", "yc", tools=[], dispatch={"lap": lambda _: {"ok": True}}, so_lan_goi_toi_da=5,
    )
    assert ket_qua.dung_vi == "het_luot_toi_da"
    assert ket_qua.so_lan_goi_model == 5
    assert len(ket_qua.nhat_ky_tool) == 5


def test_nhieu_tool_use_trong_1_response():
    provider = FakeChatProvider([
        {"content": [_tool_use("t1", "cong", {"a": 1, "b": 1}), _tool_use("t2", "cong", {"a": 2, "b": 2})]},
        {"content": [_text("xong")]},
    ])
    dispatch = {"cong": lambda dau_vao: {"tong": dau_vao["a"] + dau_vao["b"]}}
    ket_qua = agent.chay_vong_lap_tool(provider, "he thong", "yc", tools=[], dispatch=dispatch)
    assert len(ket_qua.nhat_ky_tool) == 2
    # messages[2] là message user chứa cả 2 tool_result (sau assistant gọi 2 tool cùng lúc ở messages[1]).
    assert ket_qua.messages[2]["content"][0]["tool_use_id"] == "t1"
    assert ket_qua.messages[2]["content"][1]["tool_use_id"] == "t2"
