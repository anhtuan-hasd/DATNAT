"""Cấu trúc dữ liệu "hợp đồng đầu ra" giữa 4 agent — khớp 1-1 với mục "Hợp
đồng đầu ra" trong từng file `docs/agents/*.md`. `pipeline.py` (điều phối
cấp cao, KHÔNG gọi LLM) dùng các dataclass này để cầm dữ liệu giữa 4 lần gọi
`chay_<ten>_agent()`.

Phân biệt quan trọng: đây là dữ liệu Ở TẦNG PYTHON, khác với dữ liệu trao đổi
QUA LLM (tool input/output) — kênh đó vẫn là dict JSON thô, đi qua
`agent.chay_vong_lap_tool`, giống hệt cách `tools.py` cũ làm (mỗi hàm tool
nhận/trả `dict`). Sở dĩ cần tách riêng 1 lớp dataclass ở đây vì `pipeline.py`
cần ĐỌC LẠI kết quả cuối cùng mà 1 agent để lại (vd Input Adapter Agent đã
suy luận xong `toa_do_truc` gì, Rule Engine Agent đã chọn thép gì cho phần tử
nào) để XÂY DỰNG tin nhắn mở đầu cho agent kế tiếp — không thể chỉ dựa vào
`nhat_ky_tool` dạng log tự do, cần 1 kiểu dữ liệu có cấu trúc rõ ràng.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Input Adapter Agent -> (Rule Engine Agent, Drawing Agent)
# ---------------------------------------------------------------------------


@dataclass
class ViTriChuanHoa:
    vi_tri: str
    As_yc: float | None = None
    M: float | None = None
    N: float | None = None
    Q: float | None = None
    to_hop: str | None = None


@dataclass
class PhanTuChuanHoa:
    ten: str
    loai: str  # "dam" | "cot"
    b: float
    h: float
    mac_be_tong: str
    nhom_thep_doc: str
    nhom_thep_dai: str | None = None
    truc: str | None = None  # vd "A" (cột) hoặc "A-B" (dầm) — dùng cho mặt đứng khung
    tang: str | None = None  # vd "tang2_tang3" (cột) hoặc "tang3" (dầm)
    chieu_dai: float | None = None  # mm — nhịp dầm/chiều cao đoạn cột, dùng cho bảng thống kê thép
    vi_tri: list[ViTriChuanHoa] = field(default_factory=list)


@dataclass
class BoDuLieuKhungChuanHoa:
    """Đầu ra CUỐI CÙNG của Input Adapter Agent — xem
    docs/agents/INPUT_ADAPTER_AGENT.md mục "Hợp đồng đầu ra"."""

    phan_tu: list[PhanTuChuanHoa] = field(default_factory=list)
    toa_do_truc: dict[str, float] = field(default_factory=dict)
    cao_do_moc: dict[str, float] = field(default_factory=dict)
    canh_bao: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rule Engine Agent -> Drawing Agent
# ---------------------------------------------------------------------------


@dataclass
class KetQuaViTriDaThietKe:
    """Kết quả Rule Engine Agent đã chọn xong cho 1 vị trí — chỉ tồn tại khi
    `tu_kiem_tra` đã trả `dat=true` (hoặc người dùng đã xác nhận chấp nhận vi
    phạm còn lại sau khi hết lượt tự sửa)."""

    vi_tri: str
    thep_doc: dict[str, Any]  # {"thanh": [{"duong_kinh", "so_luong"}, ...], "As_thuc": ...} (dầm)
    # hoặc {"so_thanh_canh_b", "duong_kinh_canh_b", "so_thanh_canh_h", "duong_kinh_canh_h", ...} (cột)
    cot_dai: dict[str, Any] = field(default_factory=dict)
    neo_noi: dict[str, Any] = field(default_factory=dict)
    dat: bool = False
    vi_pham: list[str] = field(default_factory=list)


@dataclass
class PhuongAnThepPhanTu:
    """Đầu ra của Rule Engine Agent cho 1 phần tử — xem
    docs/agents/RULE_ENGINE_AGENT.md mục "Hợp đồng đầu ra". Chỉ được coi là
    SẴN SÀNG bàn giao cho Drawing Agent khi mọi phần tử trong `vi_tri` đều có
    `dat=True`."""

    ten_phan_tu: str
    loai: str
    b: float
    h: float
    vi_tri: list[KetQuaViTriDaThietKe] = field(default_factory=list)

    @property
    def moi_vi_tri_dat(self) -> bool:
        return bool(self.vi_tri) and all(v.dat for v in self.vi_tri)


# ---------------------------------------------------------------------------
# Drawing Agent -> Verification Agent (và ngược lại khi lệch)
# ---------------------------------------------------------------------------


@dataclass
class KetQuaVeBanVe:
    """Xem docs/agents/DRAWING_AGENT.md mục "Hợp đồng đầu ra". `loai_ban_ve`
    phân biệt 2 dạng kiểm chứng Verification Agent cần làm khác nhau: kiểm
    tra 1 mặt cắt đơn lẻ, hay kiểm tra toàn bộ bản vẽ tổng thể đã lắp ráp."""

    loai_ban_ve: str  # "mat_cat" | "mat_dung_khung"
    nhan: str | None = None
    b_ky_vong: float | None = None
    h_ky_vong: float | None = None
    nhan_ky_vong: list[str] = field(default_factory=list)
    duong_dan_pdf: str | None = None
    duong_dan_dwg: str | None = None
    so_cot: int | None = None
    so_dam: int | None = None
    nhan_ky_vong_theo_cau_kien: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class KetQuaKiemChung:
    """Xem docs/agents/VERIFICATION_AGENT.md mục "Hợp đồng đầu ra"."""

    dat: bool
    vi_pham: list[str] = field(default_factory=list)
    so_lan_con_lai: int | None = None
    het_luot_kiem_chung: bool = False


# ---------------------------------------------------------------------------
# Báo cáo cuối cùng cho 1 khung — không phải "hợp đồng giữa 2 agent" nào cụ
# thể, mà là kết quả TỔNG HỢP pipeline.py trả về cho người gọi ngoài cùng
# (script CLI hoặc webapp) — chính là phần "đầu ra chuẩn" người dùng cần đọc.
# ---------------------------------------------------------------------------


@dataclass
class KetQuaPhanTu:
    ten_phan_tu: str
    loai: str
    trang_thai: str  # "cho_ve_mat_cat" (Rule Engine đạt, chưa vẽ mặt cắt) | "dat" | "leo_thang" | "loi"
    phuong_an_thep: PhuongAnThepPhanTu | None = None
    ghi_chu: str = ""
    # True ngay khi Rule Engine Agent đạt cho MỌI vị trí — ĐỘC LẬP với việc
    # mặt cắt đã vẽ/kiểm chứng xong hay chưa. pipeline.py dùng cờ này (thay vì
    # trang_thai == "dat") để quyết định phần tử nào được đưa vào bản vẽ bố
    # trí khung — vì bản vẽ bố trí khung nay được lắp ráp NGAY sau khi có đủ
    # thép, TRƯỚC khi vẽ từng mặt cắt chi tiết (người dùng cần xem bản vẽ bố
    # trí khung trước, mặt cắt là bản vẽ chi tiết bổ sung vẽ sau).
    rule_engine_dat: bool = False


@dataclass
class KetQuaKhung:
    ten_khung: str
    du_lieu_dau_vao: BoDuLieuKhungChuanHoa | None = None
    ket_qua_phan_tu: list[KetQuaPhanTu] = field(default_factory=list)
    duong_dan_pdf: str | None = None
    duong_dan_dwg: str | None = None
    kiem_chung_tong_the: KetQuaKiemChung | None = None
    nhat_ky: list[str] = field(default_factory=list)  # log 1 dòng/sự kiện, phục vụ báo cáo đọc được

    def ghi(self, dong: str) -> None:
        self.nhat_ky.append(dong)

    @property
    def so_phan_tu_dat(self) -> int:
        return sum(1 for kq in self.ket_qua_phan_tu if kq.trang_thai == "dat")
