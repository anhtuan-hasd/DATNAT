"""
Test lớp fallback gọi LLM khi heuristic không chắc — dùng giả lập (FakeLLM)
để KHÔNG cần API key thật, đúng tinh thần "test được ngay".
"""

import json
from types import SimpleNamespace

import pytest

from src.input_adapter.llm_mapping import OpenAIMappingProvider, de_xuat_anh_xa_bang_llm


class FakeLLM:
    def __init__(self, phan_hoi: str):
        self._phan_hoi = phan_hoi

    def hoi(self, prompt: str) -> str:
        return self._phan_hoi


def test_de_xuat_anh_xa_bang_llm_hop_le():
    phan_hoi = json.dumps(
        {
            "As_yc": {"cot_nguon": "RebarNeeded", "do_tin_cay": 0.8},
            "mac_be_tong": {"cot_nguon": "ConcGrade", "do_tin_cay": 0.7},
        }
    )
    llm = FakeLLM(phan_hoi)
    ket_qua = de_xuat_anh_xa_bang_llm(
        llm, danh_sach_cot_goc=["RebarNeeded", "ConcGrade", "Other"], truong_con_thieu=["As_yc", "mac_be_tong"]
    )
    assert ket_qua["As_yc"].cot_nguon == "RebarNeeded"
    assert ket_qua["As_yc"].nguon == "llm"
    assert ket_qua["mac_be_tong"].do_tin_cay == pytest.approx(0.7)


def test_de_xuat_anh_xa_bang_llm_loai_bo_cot_bia_dat():
    # LLM "bịa" ra cột không tồn tại trong file gốc -> phải bị loại bỏ.
    phan_hoi = json.dumps({"As_yc": {"cot_nguon": "CotKhongTonTai", "do_tin_cay": 0.9}})
    llm = FakeLLM(phan_hoi)
    ket_qua = de_xuat_anh_xa_bang_llm(llm, danh_sach_cot_goc=["A", "B"], truong_con_thieu=["As_yc"])
    assert ket_qua == {}


def test_de_xuat_anh_xa_bang_llm_json_hong():
    llm = FakeLLM("không phải JSON hợp lệ")
    with pytest.raises(ValueError):
        de_xuat_anh_xa_bang_llm(llm, danh_sach_cot_goc=["A"], truong_con_thieu=["As_yc"])


def test_de_xuat_anh_xa_bang_llm_rong_khi_khong_thieu_truong():
    class LLMKhongDuocGoi:
        def hoi(self, prompt: str) -> str:
            raise AssertionError("Không được gọi LLM khi không có trường nào thiếu")

    ket_qua = de_xuat_anh_xa_bang_llm(LLMKhongDuocGoi(), danh_sach_cot_goc=["A"], truong_con_thieu=[])
    assert ket_qua == {}


def test_openai_mapping_provider_hoi():
    provider = OpenAIMappingProvider(api_key="fake-key-khong-can-that")

    def create_gia(model, messages):
        assert messages[0]["content"] == "hoi thu"
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))])

    provider._client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create_gia)))
    assert provider.hoi("hoi thu") == '{"ok": true}'
