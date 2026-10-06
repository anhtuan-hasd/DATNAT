"""Sổ đăng ký SỐ HIỆU THANH THÉP — TCVN 4612-88, KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md
mục 2.2: mỗi loại thanh RIÊNG BIỆT (cùng đường kính + cùng chiều dài) được gán
1 số hiệu DUY NHẤT, dùng CHUNG số hiệu đó ở MỌI nơi thanh đó xuất hiện trên cả
bản vẽ (mặt đứng khung, mọi mặt cắt, bảng thống kê) — KHÔNG đánh số lại từ đầu
cho mỗi cấu kiện. Xác nhận qua đối chiếu `data/samples/BoTriThep_KhungTruc5_mau.pdf`:
số hiệu "5" (4Ø16) lặp lại ở nhiều đoạn cột khác tầng vì cùng đường kính+chiều dài.

Module thuần Python, không phụ thuộc AutoCAD/LLM — đây là NƠI DUY NHẤT trong
toàn hệ thống cấp số hiệu, để `_xay_dong_thong_ke` (bảng thống kê) và
`lap_rap_mat_dung_khung` (vẽ ký hiệu trên hình) LUÔN dùng chung đúng 1 số cho
cùng 1 loại thanh — tách riêng khỏi `drawing_agent.py` để dùng lại được ở
Phase B (mặt cắt) sau này mà không phải sao chép logy.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThanhThep:
    """Khoá nhận diện 1 LOẠI thanh thép — 2 thanh cùng (duong_kinh,
    chieu_dai_mm) được coi là CÙNG LOẠI, nhận chung 1 số hiệu. chieu_dai_mm
    làm tròn về số nguyên gần nhất TRƯỚC KHI tạo ThanhThep (ở nơi gọi) — chiều
    dài tính từ dữ liệu thực tế (vd nhịp dầm) hiếm khi trùng khớp tuyệt đối
    đến phần thập phân, làm tròn tránh tạo số hiệu MỚI không cần thiết chỉ vì
    sai số 0,001mm."""

    duong_kinh: int
    chieu_dai_mm: int


@dataclass
class SoDangKySoHieu:
    """1 instance DÙNG CHUNG cho toàn bộ 1 lần lắp ráp bản vẽ (1 lần gọi
    `lap_rap_mat_dung_khung`) — KHÔNG tạo mới giữa chừng, để số hiệu nhất
    quán giữa bảng thống kê và ký hiệu vẽ trên hình trong CÙNG 1 lần chạy."""

    _so_hieu_theo_thanh: dict[ThanhThep, int] = field(default_factory=dict)

    def lay_so_hieu(self, thanh: ThanhThep) -> int:
        """Trả về số hiệu ĐÃ CÓ nếu đúng loại thanh này đã gặp trước đó,
        hoặc cấp số hiệu MỚI (tăng dần từ 1, theo đúng thứ tự lần đầu gặp)
        nếu chưa — ĐIỂM DUY NHẤT cấp số hiệu trong toàn hệ thống."""
        if thanh not in self._so_hieu_theo_thanh:
            self._so_hieu_theo_thanh[thanh] = len(self._so_hieu_theo_thanh) + 1
        return self._so_hieu_theo_thanh[thanh]
