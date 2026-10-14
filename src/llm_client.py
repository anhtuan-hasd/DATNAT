"""Khởi tạo client LLM dùng chung cho toàn hệ thống.

OpenRouter có endpoint TƯƠNG THÍCH OpenAI (cùng Chat Completions + tool-calling)
nên vẫn dùng gói `openai`, chỉ đổi `base_url` + API key. Quy tắc chọn nhà cung cấp:

1. `api_key` truyền tường minh  -> OpenAI chính hãng (hành vi cũ, dùng cho test).
2. Có biến môi trường `OPENROUTER_API_KEY` -> OpenRouter (ưu tiên, có model miễn phí).
3. Còn lại -> OpenAI chính hãng với `OPENAI_API_KEY` như trước.

Model mặc định trên OpenRouter là 1 model miễn phí (hậu tố `:free`) có hỗ trợ tool-calling
và context đủ lớn cho bộ skill ~36k token/lượt; đổi bằng biến môi trường `OPENROUTER_MODEL`.
"""

from __future__ import annotations

import os

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_OPENROUTER_MAC_DINH = "nvidia/nemotron-3-super-120b-a12b:free"
MODEL_OPENAI_MAC_DINH = "gpt-5.6-luna"


def dung_openrouter(api_key: str | None = None) -> bool:
    """True nếu lần gọi này sẽ đi qua OpenRouter."""
    return api_key is None and bool(os.environ.get("OPENROUTER_API_KEY"))


def tao_client_openai(api_key: str | None = None):
    """Trả về `openai.OpenAI` trỏ tới OpenRouter hoặc OpenAI theo quy tắc ở đầu file."""
    import openai

    if dung_openrouter(api_key):
        return openai.OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url=OPENROUTER_BASE_URL,
            # 2 header tuỳ chọn để lượt gọi hiện tên ứng dụng trên dashboard OpenRouter.
            default_headers={"X-Title": "DA - Ban ve khung BTCT"},
        )
    return openai.OpenAI(api_key=api_key)


def chon_model(model: str | None, api_key: str | None = None) -> str:
    """`model` truyền vào thì dùng nguyên; không thì lấy mặc định theo nhà cung cấp đang dùng."""
    if model:
        return model
    if dung_openrouter(api_key):
        return os.environ.get("OPENROUTER_MODEL") or MODEL_OPENROUTER_MAC_DINH
    return MODEL_OPENAI_MAC_DINH
