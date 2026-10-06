"""`PhienCAD` — tham chiếu tới 1 phiên làm việc AutoCAD COM (Application +
Document đang mở) DÙNG CHUNG xuyên suốt việc vẽ 1 khung. Đặt riêng module này
(không nằm trong `hop_dong_du_lieu.py`) vì đây KHÔNG phải dữ liệu JSON tuần
tự hoá được — nó cầm tham chiếu COM sống (live object), chỉ tồn tại trong bộ
nhớ của 1 lần chạy.

Vì sao cần dùng CHUNG 1 Document cho cả khung (không mở Document mới cho mỗi
mặt cắt): `docs/agents/DRAWING_AGENT.md` yêu cầu tất cả mặt cắt + mặt đứng
khung của 1 khung nằm trên CÙNG 1 tờ bản vẽ — mở nhiều Document rồi mới gộp
lại sẽ phức tạp và không cần thiết khi AutoCAD COM cho phép vẽ trực tiếp vào
nhiều vị trí (dx, dy) khác nhau trên CÙNG 1 ModelSpace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PhienCAD:
    app: Any  # AutoCAD.Application (COM) — trả về bởi backend_com.ket_noi_autocad()
    doc: Any  # Document (COM) đang mở — trả về bởi backend_com.tao_ban_ve_moi(app)
    thu_muc_xuat: str  # nơi lưu PDF/DWG khi Drawing Agent gọi xuat_ban_ve
    # Vị trí X tiếp theo còn TRỐNG trên ModelSpace để đặt mặt cắt kế tiếp —
    # Drawing Agent tự cộng dồn mỗi lần vẽ xong 1 mặt cắt (giống cách
    # scripts/chay_lien_mach_khung.py cũ làm thủ công, nay chuyển vào đây để
    # tool ve_mat_cat tự quản lý, LLM không cần tự tính toạ độ đặt hình).
    x_tiep_theo: float = 0.0
    khoang_cach_giua_mat_cat: float = 300.0  # mm — đủ chỗ cho kích thước/nhãn 2 mặt cắt liền kề không đè lên nhau
    # Cao độ Y CỐ ĐỊNH đặt cả hàng mặt cắt — LỖI THẬT đã gặp: mặt cắt trước
    # đây luôn vẽ ở dy=0, TRÙNG đúng vùng y=0 (cao độ Mong/tầng trệt) của mặt
    # đứng khung (vốn cũng bắt đầu từ y=0) — 32 mặt cắt chồng đè LÊN TRÊN góc
    # dưới-trái mặt đứng khung (không chỉ "bị nén nhỏ do chung tỷ lệ" như
    # chẩn đoán trước đó), khiến vùng đó hiện thành 1 khối đặc màu đen khi
    # xuất PDF (hàng chục đường/hatch chồng khít nhau). pipeline.py tự tính
    # lại giá trị này SAU KHI mặt đứng khung đã vẽ xong (Bước B), dựa trên
    # bounding box THẬT của ModelSpace lúc đó (backend_com.hop_gioi_han_
    # modelspace) — đặt mặt cắt hẳn xuống DƯỚI toàn bộ mặt đứng khung, không
    # còn chồng lấn dù giá trị thật của dự án là bao nhiêu.
    y_mat_cat: float = 0.0
