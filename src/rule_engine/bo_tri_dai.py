"""Bố trí cốt đai theo VÙNG dọc cấu kiện (dầm: gối/giữa nhịp/gối; cột: hai đầu/giữa) — quy tắc cấu tạo của skill
`docs/agents/huongdanchonthep/06_BO_TRI_THEO_CHIEU_DAI.md` (B8 cho dầm, C4 cho cột) và `04_CAU_TAO_CHUNG.md`.

Đây là bố trí CẤU TẠO (tối đa bước đai cho phép). Khi có kết quả `tinh_cot_dai` (đai theo tính toán) thì lấy bước
NHỎ HƠN giữa tính toán và cấu tạo — việc đó do nơi gọi truyền `buoc_tinh_toan` (mm) vào. Hàm thuần Python, không LLM,
không AutoCAD. Mọi số có nhãn nguồn trong docstring:
  - [D] TCVN 5574:2018, [A] tài liệu hướng dẫn chọn thép (Phụ lục A/D), [thực hành] thông lệ thiết kế (skill ghi nhãn).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

DUONG_KINH_DAI_CHUAN = (6, 8, 10, 12)  # mm — đường kính đai thông dụng
KHOANG_DAI_DAU_TIEN_MM = 50.0  # đai đầu tiên cách mép gối/cột 50 mm (B8, C4 — nguồn A, B / [thực hành])


@dataclass(frozen=True)
class VungDai:
    """Một vùng đai: từ `tu_mm` đến `den_mm` (toạ độ dọc cấu kiện, mm, tính từ mép trái/dưới), bước `buoc_mm`."""

    tu_mm: float
    den_mm: float
    buoc_mm: float
    duong_kinh: int

    @property
    def chieu_dai(self) -> float:
        return self.den_mm - self.tu_mm

    @property
    def so_dai(self) -> int:
        """n = ⌊(l − 50)/s⌋ + 1 (B8). Vùng quá ngắn (l < 50) ⇒ 0."""
        if self.chieu_dai < KHOANG_DAI_DAU_TIEN_MM:
            return 0
        return int((self.chieu_dai - KHOANG_DAI_DAU_TIEN_MM) // self.buoc_mm) + 1

    def nhan(self) -> str:
        """Nhãn bản vẽ: 'Ø6a150'."""
        return f"Ø{self.duong_kinh}a{self.buoc_mm:g}"


def lam_tron_xuong(gia_tri: float, buoc: float = 50.0, toi_thieu: float | None = None) -> float:
    """Làm tròn XUỐNG bội của `buoc` (bước đai chỉ được nhỏ đi, không to lên). `toi_thieu` chặn dưới."""
    ket_qua = math.floor(gia_tri / buoc) * buoc
    if toi_thieu is not None:
        ket_qua = max(ket_qua, toi_thieu)
    return ket_qua


def chon_duong_kinh_dai(duong_kinh_doc_max: float) -> int:
    """d_sw ≥ max(d/4; 6) [D, 04_CAU_TAO_CHUNG.md]; chọn cỡ chuẩn nhỏ nhất thoả."""
    can = max(duong_kinh_doc_max / 4.0, 6.0)
    for d in DUONG_KINH_DAI_CHUAN:
        if d >= can:
            return d
    return DUONG_KINH_DAI_CHUAN[-1]


def buoc_dai_goi_dam(h: float) -> float:
    """Bước đai vùng GỐI dầm: s ≤ min(h/2; 300) nếu h ≤ 450; min(h/3; 500) nếu h > 450 [D; A — B8].
    Làm tròn xuống bội 50 (tối thiểu 100)."""
    s = min(h / 2.0, 300.0) if h <= 450 else min(h / 3.0, 500.0)
    return lam_tron_xuong(s, 50.0, 100.0)


def buoc_dai_giua_dam(h: float, duong_kinh_doc_min: float, co_thep_nen: bool = True) -> float:
    """Bước đai vùng GIỮA NHỊP: s ≤ min(3h/4; 500) [D; A — B8]; khi có cốt dọc chịu nén thì thêm s ≤ 15·d_min
    (mục "đai" cột/dầm có thép nén, 04_CAU_TAO_CHUNG.md — D, A). Làm tròn xuống bội 50 (tối thiểu 100)."""
    s = min(0.75 * h, 500.0)
    if co_thep_nen:
        s = min(s, 15.0 * duong_kinh_doc_min)
    return lam_tron_xuong(s, 50.0, 100.0)


def bo_tri_dai_dam(
    h: float, l_thong_thuy: float, duong_kinh_doc_max: float, duong_kinh_doc_min: float,
    co_thep_nen: bool = True, buoc_tinh_toan_goi: float | None = None,
) -> list[VungDai]:
    """Các vùng đai dầm theo toạ độ x từ MÉP gối trái (0) đến mép gối phải (`l_thong_thuy`).

    - Vùng gối: dài l1 = L/4 (B8 khi đai giữa nhịp đã chịu Q_max; làm tròn xuống bội 50), bước `buoc_dai_goi_dam`;
      nếu có `buoc_tinh_toan_goi` thì lấy bước nhỏ hơn.
    - Vùng giữa: phần còn lại, bước `buoc_dai_giua_dam`.
    - Nhịp ngắn (L/4 < 3 bước gối): chỉ 1 vùng, dùng bước gối (an toàn hơn; vùng gối không đủ chỗ cho ≥3 đai).
    """
    d_w = chon_duong_kinh_dai(duong_kinh_doc_max)
    s_goi = buoc_dai_goi_dam(h)
    if buoc_tinh_toan_goi is not None:
        s_goi = min(s_goi, lam_tron_xuong(buoc_tinh_toan_goi, 50.0, 50.0))
    s_giua = max(s_goi, buoc_dai_giua_dam(h, duong_kinh_doc_min, co_thep_nen))
    l1 = lam_tron_xuong(l_thong_thuy / 4.0, 50.0)
    if l1 < 3 * s_goi or l_thong_thuy - 2 * l1 <= 0:
        return [VungDai(0.0, l_thong_thuy, s_goi, d_w)]
    return [
        VungDai(0.0, l1, s_goi, d_w),
        VungDai(l1, l_thong_thuy - l1, s_giua, d_w),
        VungDai(l_thong_thuy - l1, l_thong_thuy, s_goi, d_w),
    ]


def bo_tri_dai_cot(
    h_cot: float, h_thong_thuy: float, duong_kinh_doc_max: float, duong_kinh_doc_min: float,
    chieu_dai_noi: float = 0.0, buoc_tinh_toan: float | None = None,
) -> list[VungDai]:
    """Các vùng đai cột theo toạ độ y từ ĐÁY đoạn cột (0) đến đỉnh (`h_thong_thuy`) — C4.

    - Hai đầu: s ≤ 10·d_min, dài l_d = max(h_c; H_n/6; 450) [s: A; l_d: thực hành]. Ở tầng có mối nối chồng
      (`chieu_dai_noi` > 0) vùng chân kéo dài đến hết đoạn nối nếu dài hơn l_d (s ≤ min(10d; 300) trong đoạn nối).
    - Giữa: s ≤ min(15·d_min; 500) [D 6.2.1; A].
    Làm tròn xuống bội 50 (tối thiểu 100). Cột quá thấp để chia 3 vùng ⇒ 1 vùng bước hai đầu.
    """
    d_w = chon_duong_kinh_dai(duong_kinh_doc_max)
    s_dau = lam_tron_xuong(min(10.0 * duong_kinh_doc_min, 300.0), 50.0, 100.0)
    if buoc_tinh_toan is not None:
        s_dau = min(s_dau, lam_tron_xuong(buoc_tinh_toan, 50.0, 50.0))
    s_giua = max(s_dau, lam_tron_xuong(min(15.0 * duong_kinh_doc_min, 500.0), 50.0, 100.0))
    l_d = max(h_cot, h_thong_thuy / 6.0, 450.0)
    l_chan = max(l_d, chieu_dai_noi)
    l_dau = l_d
    if l_chan + l_dau >= h_thong_thuy:
        return [VungDai(0.0, h_thong_thuy, s_dau, d_w)]
    return [
        VungDai(0.0, l_chan, s_dau, d_w),
        VungDai(l_chan, h_thong_thuy - l_dau, s_giua, d_w),
        VungDai(h_thong_thuy - l_dau, h_thong_thuy, s_dau, d_w),
    ]


def vi_tri_dai(vung: list[VungDai]) -> list[float]:
    """Toạ độ (dọc cấu kiện, mm) của từng cốt đai: đai đầu mỗi vùng cách mép vùng 50 mm, rồi theo bước vùng.
    Vùng liền kề không trùng toạ độ (loại đai cách nhau < 1 mm)."""
    ket_qua: list[float] = []
    for v in vung:
        for i in range(v.so_dai):
            x = v.tu_mm + KHOANG_DAI_DAU_TIEN_MM + i * v.buoc_mm
            if x <= v.den_mm + 1e-6 and (not ket_qua or x - ket_qua[-1] > 1.0):
                ket_qua.append(x)
    return ket_qua
