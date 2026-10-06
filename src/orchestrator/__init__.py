"""Agent điều phối (Phase 4) — dùng OpenAI GPT (OpenAI API) qua tool-calling.

- loops.py: bộ đếm cho vòng lặp tự sửa lỗi + vòng lặp kiểm chứng bản vẽ.
- tools.py: các tool LLM được phép gọi (bọc mỏng quanh input_adapter/rule_engine/drawing).
- agent.py: vòng lặp tool-calling tổng quát với LLM.
- pipeline.py: system prompt + lắp ráp toàn bộ pipeline 7 bước.
"""
