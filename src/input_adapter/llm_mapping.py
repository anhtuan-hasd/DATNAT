"""
Suy đoán ánh xạ cột bằng LLM — CHỈ dùng khi heuristics.py không đủ tin cậy
(TONGQUAN_AI_AGENT.md mục 5 bước 2, mục 3 nguyên tắc 1). Theo quyết định hiện
tại của đồ án (docs/TONGQUAN_AI_AGENT.md mục 4/7), LLM DUY NHẤT dùng trong
toàn hệ thống là **OpenAI GPT** — không dùng LLM/nhà cung cấp khác ở bất kỳ
đâu trong pipeline.

Ranh giới bắt buộc: LLM ở đây CHỈ đề xuất TÊN CỘT tương ứng — không tính bất
kỳ con số kỹ thuật nào (As, M, N, Q...). Kết quả đề xuất LUÔN phải qua bước
xác nhận người dùng ở lớp gọi (adapter.py) trước khi dùng để tính toán —
module này không bao giờ tự động áp dụng ánh xạ do LLM đề xuất.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from .heuristics import TU_KHOA_THEO_TRUONG, DeXuatAnhXa


class NhaCungCapLLM(Protocol):
    """Giao diện tối thiểu để gọi LLM — tách khỏi SDK cụ thể để test được
    bằng giả lập (fake), không cần API key thật khi chạy unit test."""

    def hoi(self, prompt: str) -> str: ...


class OpenAIMappingProvider:
    """Cài đặt CHÍNH THỨC của đồ án — dùng OpenAI API (Chat Completions).

    Import `openai` được đặt TRONG __init__ (không ở đầu module) để
    llm_mapping.py vẫn import/test được trong môi trường chưa cài gói
    `openai` — chỉ cần cài khi thực sự khởi tạo lớp này để gọi API thật.
    Mặc định dùng `gpt-5.6-luna` (rẻ nhất dòng GPT-5.6, GA 07/2026) — tác vụ
    này chỉ hỏi 1 câu, không cần model mạnh.
    """

    def __init__(self, model: str = "gpt-5.6-luna", api_key: str | None = None):
        import openai

        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def hoi(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


class ClaudeMappingProvider:
    """Cài đặt THAY THẾ (không phải lựa chọn chính thức hiện tại — xem
    docstring đầu file) dùng Anthropic SDK, giữ lại vì cùng Protocol
    `NhaCungCapLLM` nên không tốn thêm chi phí bảo trì.

    Import `anthropic` được đặt TRONG __init__ (không ở đầu module) để
    llm_mapping.py vẫn import/test được trong môi trường chưa cài gói
    `anthropic` — chỉ cần cài khi thực sự khởi tạo lớp này để gọi API thật.
    """

    def __init__(self, model: str = "claude-sonnet-5", api_key: str | None = None):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def hoi(self, prompt: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")


def _tao_prompt(
    danh_sach_cot_goc: list[str],
    truong_con_thieu: list[str],
    mau_du_lieu: dict[str, list] | None,
) -> str:
    goi_y_tu_khoa = {t: TU_KHOA_THEO_TRUONG.get(t, []) for t in truong_con_thieu}
    mau = mau_du_lieu or {}
    return (
        "Bạn đang giúp ánh xạ tên cột của một file Excel/CSV xuất ra từ ETABS "
        "(kết quả tính khung bê tông cốt thép) về một schema chuẩn nội bộ. "
        "TUYỆT ĐỐI KHÔNG tính bất kỳ con số nào, CHỈ đề xuất cột gốc nào (nếu "
        "có) tương ứng với mỗi trường chuẩn dưới đây, dựa trên tên cột và vài "
        "giá trị mẫu.\n\n"
        f"Danh sách cột gốc trong file: {json.dumps(danh_sach_cot_goc, ensure_ascii=False)}\n\n"
        f"Vài dòng dữ liệu mẫu theo từng cột (nếu có): {json.dumps(mau, ensure_ascii=False)}\n\n"
        f"Các trường chuẩn cần tìm cột tương ứng (kèm gợi ý từ khoá tiếng "
        f"Anh/Việt thường gặp): {json.dumps(goi_y_tu_khoa, ensure_ascii=False)}\n\n"
        "Trả lời DUY NHẤT bằng JSON hợp lệ (không kèm giải thích, không kèm "
        'markdown), dạng {"ten_truong_chuan": {"cot_nguon": "<tên cột gốc '
        'chính xác trong danh sách trên>", "do_tin_cay": <số 0..1>}, ...}. '
        "Nếu không tìm được cột phù hợp cho một trường, bỏ qua hẳn trường đó "
        "trong JSON — KHÔNG được bịa ra tên cột không có trong danh sách gốc."
    )


def de_xuat_anh_xa_bang_llm(
    nha_cung_cap: NhaCungCapLLM,
    danh_sach_cot_goc: list[str],
    truong_con_thieu: list[str],
    mau_du_lieu: dict[str, list] | None = None,
) -> dict[str, DeXuatAnhXa]:
    """Gọi LLM để đề xuất ánh xạ cho các trường heuristic chưa chắc chắn.

    Trả về dict cùng dạng heuristics.du_doan_anh_xa_cot nhưng nguon="llm".
    Mọi cột LLM đề xuất mà KHÔNG có trong danh_sach_cot_goc bị loại bỏ
    ngay (không tin tưởng mù quáng) — đề xuất còn lại vẫn bắt buộc đi qua xác
    nhận người dùng ở adapter.py, hàm này không tự quyết định gì thêm.
    """
    if not truong_con_thieu:
        return {}

    prompt = _tao_prompt(danh_sach_cot_goc, truong_con_thieu, mau_du_lieu)
    phan_hoi = nha_cung_cap.hoi(prompt)
    try:
        du_lieu = json.loads(phan_hoi)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM không trả về JSON hợp lệ cho ánh xạ cột: {phan_hoi!r}") from e

    ket_qua: dict[str, DeXuatAnhXa] = {}
    for truong, thong_tin in du_lieu.items():
        if not isinstance(thong_tin, dict):
            continue
        cot_nguon = thong_tin.get("cot_nguon")
        if cot_nguon not in danh_sach_cot_goc:
            continue  # LLM bịa cột không tồn tại — loại bỏ ngay
        try:
            do_tin_cay = float(thong_tin.get("do_tin_cay", 0.5))
        except (TypeError, ValueError):
            do_tin_cay = 0.5
        ket_qua[truong] = DeXuatAnhXa(truong, cot_nguon, do_tin_cay, nguon="llm")
    return ket_qua
