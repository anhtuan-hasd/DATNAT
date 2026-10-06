"""4 agent LLM độc lập — mỗi agent 1 file, đúng ranh giới trách nhiệm mô tả
trong `docs/agents/*.md` và `docs/TONGQUAN_AI_AGENT.md` mục 4:

- `input_adapter_agent.py` — đọc & chuẩn hoá Excel/CSV, suy luận hình học.
- `rule_engine_agent.py` — chọn thép, tính cấu tạo, tự kiểm tra.
- `drawing_agent.py` — vẽ mặt cắt + lắp ráp mặt đứng khung, 100% AutoCAD COM.
- `verification_agent.py` — đọc lại bản vẽ qua COM để đối chiếu.

Mỗi file tự khai báo system prompt + tool + dispatch RIÊNG của agent đó —
không có tool nào bị chia sẻ ngầm giữa các file (trừ `hoi_nguoi_dung`, nằm ở
`../shared/hoi_nguoi_dung_tool.py`, dùng chung có chủ đích). `pipeline.py`
(thư mục cha) là nơi DUY NHẤT gọi cả 4 agent theo đúng thứ tự.
"""

from __future__ import annotations
