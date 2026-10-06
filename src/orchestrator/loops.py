"""
Bộ đếm cho 4 vòng lặp GIỚI HẠN PHẠM VI của TONGQUAN_AI_AGENT.md mục 5
("Vòng lặp của Agent nằm ở đâu"):

1. Vòng lặp ngoài cùng (per phần tử) — lặp bước 2→7 cho từng phần tử khung.
   Điều kiện dừng: hết danh sách phần tử (không cần bộ đếm, dùng vòng for
   thường trong pipeline.py).
2. Vòng lặp tự sửa (self-correction) — bước 5→3. Điều kiện dừng: qua được
   self-check, HOẶC đạt số lần thử tối đa.
3. Vòng lặp xác nhận dữ liệu — bước 2 (Input Adapter không chắc mapping) →
   hỏi người dùng → tiếp tục bước 2. Điều kiện dừng: người dùng xác nhận.
4. Vòng lặp kiểm chứng bản vẽ — bước 6 → đọc lại → so sánh → sửa nếu lệch →
   bước 7. Điều kiện dừng: bản vẽ khớp, HOẶC hết số lần thử.

QUAN TRỌNG: bộ đếm ở đây là NƠI DUY NHẤT ép các vòng lặp 2 và 4 có giới hạn
cứng bằng code — không giao phó việc "biết dừng lại" cho LLM. LLM (OpenAI GPT,
trong agent.py/pipeline.py) chỉ quyết định NÊN LÀM GÌ TIẾP THEO trong phạm vi
còn được phép thử; khi bộ đếm báo hết lượt, tool tương ứng (tools.py) trả về
cờ báo hiệu và LLM BẮT BUỘC chuyển hướng (thường là gọi hoi_nguoi_dung)
thay vì tiếp tục thử — đúng tinh thần "Vòng lặp dừng khi... hoặc hết số lần
thử tối đa rồi báo người dùng".
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Số lần thử mặc định cho từng loại vòng lặp — có thể ghi đè khi khởi tạo
# BoDemVongLap tuỳ ngữ cảnh (vd đồ án có thể muốn nới lỏng khi debug).
GIOI_HAN_MAC_DINH: dict[str, int] = {
    "tu_sua": 3,  # vòng lặp 2
    "kiem_chung_ve": 3,  # vòng lặp 4
}


@dataclass
class BoDemVongLap:
    """Theo dõi số lần đã thử cho từng (loại vòng lặp, phần tử) — 1 instance
    dùng riêng cho mỗi phần tử đang chạy qua pipeline (không chia sẻ giữa các
    phần tử khác nhau, để phần tử A hết lượt không ảnh hưởng phần tử B)."""

    gioi_han: dict[str, int] = field(default_factory=lambda: dict(GIOI_HAN_MAC_DINH))
    da_dung: dict[str, int] = field(default_factory=dict)
    ly_do_dung: dict[str, str] = field(default_factory=dict)

    def con_duoc_thu(self, loai: str) -> bool:
        return self.da_dung.get(loai, 0) < self.gioi_han.get(loai, 10**9)

    def ghi_nhan_1_lan_thu(self, loai: str) -> bool:
        """Tăng bộ đếm cho 1 lần thử MỚI, trả về True nếu lần thử này còn hợp
        lệ (chưa vượt giới hạn tại thời điểm ghi nhận)."""
        n = self.da_dung.get(loai, 0) + 1
        self.da_dung[loai] = n
        con_duoc = n <= self.gioi_han.get(loai, 10**9)
        if not con_duoc and loai not in self.ly_do_dung:
            self.ly_do_dung[loai] = f"Đã thử {n} lần, vượt giới hạn {self.gioi_han.get(loai)} lần cho phép."
        return con_duoc

    def so_lan_con_lai(self, loai: str) -> int:
        return max(0, self.gioi_han.get(loai, 10**9) - self.da_dung.get(loai, 0))
