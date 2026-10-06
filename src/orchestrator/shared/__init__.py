"""Thành phần DÙNG CHUNG cho cả 4 agent (Input Adapter/Rule Engine/Drawing/
Verification) — chỉ chứa 2 thứ thật sự không thuộc về riêng agent nào:

- `hop_dong_du_lieu.py`: các dataclass mô tả đúng cấu trúc JSON "hợp đồng đầu
  ra" mà mỗi agent bàn giao cho agent kế tiếp, khớp 1-1 với mục "Hợp đồng đầu
  ra" trong từng file docs/agents/*.md. `pipeline.py` dùng các dataclass này
  để truyền dữ liệu giữa 4 lần gọi chay_<ten>_agent() — đây là lớp Python
  thuần, KHÔNG phải nội dung gửi cho LLM (nội dung gửi/nhận với LLM vẫn là
  dict JSON thô qua agent.chay_vong_lap_tool, giống hệt cách tools.py cũ làm).
- `hoi_nguoi_dung_tool.py`: tool `hoi_nguoi_dung` — MỘT định nghĩa DUY NHẤT,
  4 agent cùng dùng lại thay vì khai báo lặp lại 4 lần.

Cố ý KHÔNG có 1 "NguCanhChung" (ngữ cảnh dùng chung kiểu god-object) ở đây —
mỗi agent tự định nghĩa dataclass ngữ cảnh RIÊNG trong file của mình (vd
`NguCanhInputAdapter`, `NguCanhRuleEngine`...), chỉ giữ đúng state agent đó
cần. Đây là quyết định thiết kế có chủ đích: 1 agent chỉ nên "nhìn thấy" state
thuộc phạm vi trách nhiệm của nó, không chia sẻ 1 object state khổng lồ giữa
cả 4 agent (tránh agent này vô tình đọc/ghi nhầm state của agent khác).
"""

from __future__ import annotations
