"""Chọn nhà cung cấp LLM: OpenRouter khi có OPENROUTER_API_KEY, ngược lại OpenAI (không gọi mạng)."""

from src import llm_client
from src.orchestrator import agent


def test_co_openrouter_key_thi_dung_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-gia")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    p = agent.OpenAIChatProvider()
    assert "openrouter.ai" in str(p._client.base_url)
    assert p._model == llm_client.MODEL_OPENROUTER_MAC_DINH
    assert p._reasoning_effort is None  # tham số riêng của gpt-5.6-luna, không gửi sang OpenRouter


def test_doi_model_openrouter_bang_bien_moi_truong(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-gia")
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free")
    assert agent.OpenAIChatProvider()._model == "google/gemma-4-31b-it:free"


def test_khong_co_openrouter_key_thi_dung_openai(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-gia")
    p = agent.OpenAIChatProvider()
    assert "openrouter" not in str(p._client.base_url)
    assert p._model == llm_client.MODEL_OPENAI_MAC_DINH
    assert p._reasoning_effort == "none"


def test_api_key_truyen_tuong_minh_luon_la_openai(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-gia")
    p = agent.OpenAIChatProvider(api_key="sk-gia")
    assert "openrouter" not in str(p._client.base_url)
    assert p._model == llm_client.MODEL_OPENAI_MAC_DINH
