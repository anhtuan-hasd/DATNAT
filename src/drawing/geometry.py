"""
Tính toán hình học độc lập backend (KHÔNG phụ thuộc pywin32) — nhận
input trực tiếp từ kết quả Input Adapter (Phase 2) + Rule Engine (Phase 1),
xuất ra một biểu diễn trung gian (IR — Intermediate Representation) gồm các
đối tượng vẽ thuần (đoạn thẳng, đa giác, vòng tròn, chữ, kích thước) kèm tên
layer. `backend_com.py` (backend DUY NHẤT, AutoCAD COM — xem
docs/CHANGE_REQUESTS.md mục 2) đọc IR này để vẽ ra AutoCAD thật — tách IR
khỏi backend để logic hình học test được thuần Python, không cần AutoCAD.

Nguyên tắc bắt buộc (RULES_TCVN5574.md mục 10.7.1): MỌI kích thước xuất hiện
ở đây phải là THAM SỐ truyền vào từ Input Adapter/Rule Engine — không hard-code
theo bản vẽ mẫu khung trục 5. Số lượng mặt cắt theo loại cấu kiện lấy đúng yêu
cầu đã xác nhận: cột → 1 mặt cắt đại diện; dầm nhịp thường (2 đầu có gối) → 3
mặt cắt (gối trái/giữa nhịp/gối phải); dầm công-xôn → 1 mặt cắt tại ngàm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..rule_engine.cot_doc import so_thanh_toi_da_1_lop
from ..rule_engine.neo_noi import duong_kinh_uon_toi_thieu
from ..rule_engine.vat_lieu import dien_tich_1_thanh
from ..input_adapter.models import LoaiCauKien
from . import layers

# ---------------------------------------------------------------------------
# Biểu diễn trung gian (IR) — đơn vị: mm, hệ toạ độ cục bộ của từng hình vẽ.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Diem:
    x: float
    y: float

    def dich(self, dx: float, dy: float) -> "Diem":
        return Diem(self.x + dx, self.y + dy)


@dataclass(frozen=True)
class VeDoanThang:
    p1: Diem
    p2: Diem
    layer: str


@dataclass(frozen=True)
class VeDaGiac:
    """Đa giác — dùng cho đường bao tiết diện, đường bao đai..."""

    diem: tuple[Diem, ...]
    layer: str
    dong: bool = True
    do_rong_net: float = 0.0  # mm, đơn vị bản vẽ (model-space thật) — > 0 ->
    # backend đặt ĐỘ RỘNG HÌNH HỌC THẬT (const_width/ConstantWidth) cho
    # polyline, KHÔNG chỉ dựa vào thuộc tính lineweight của layer. Thấy thật:
    # lineweight DXF là thuộc tính HIỂN THỊ — đa số phần mềm xem DXF (kể cả
    # AutoCAD ở Model Space) mặc định TẮT hiển thị lineweight (nút "Bật/Tắt
    # trọng lượng nét" trên thanh trạng thái phải bấm riêng), nên nét "đậm"
    # của cấu kiện trông y hệt nét mảnh khi mở file bình thường — đặt thêm độ
    # rộng hình học thật đảm bảo LUÔN thấy đậm, không phụ thuộc cấu hình xem.
    # 0.0 = giữ hành vi cũ (không đặt, chỉ dựa vào lineweight của layer).


@dataclass(frozen=True)
class VeVongTron:
    """Vòng tròn đặc — tiết diện 1 thanh thép dọc nhìn dọc trục (mục 10.7.2 ghi chú)."""

    tam: Diem
    ban_kinh: float
    layer: str


@dataclass(frozen=True)
class VeCung:
    """Cung tròn — dùng cho chỗ UỐN của cốt thép (đai/thanh dọc uốn), vì thép
    uốn từ 1 thanh tròn luôn có bán kính uốn tại góc (mục 6.4 RULES_TCVN5574.md
    "Đường kính uốn tối thiểu"), KHÔNG phải góc vuông sắc như đường bao bê
    tông (OUTLINE_CUT vẫn dùng VeDaGiac góc vuông — đúng vì đó là mặt cắt bê
    tông thật, không phải thanh thép uốn)."""

    tam: Diem
    ban_kinh: float
    goc_bat_dau_do: float  # độ (0-360), theo chiều dương lượng giác (ngược kim đồng hồ)
    goc_ket_thuc_do: float
    layer: str


@dataclass(frozen=True)
class VeChu:
    vi_tri: Diem
    noi_dung: str
    chieu_cao: float
    layer: str
    canh_giua: bool = False
    canh_phai: bool = False  # True -> chữ mọc về BÊN TRÁI điểm neo (kết thúc tại vi_tri) —
    # dùng cho chú thích cần "mọc ra ngoài" bản vẽ (vd tên tầng/cao độ bên trái
    # khung) thay vì mặc định mọc sang phải, tránh đè lên nội dung bên trong.


@dataclass(frozen=True)
class VeKichThuoc:
    """Kích thước tuyến tính đơn giản — backend tự vẽ đường dóng + đường kích
    thước + số theo p1, p2 và khoảng offset ra khỏi đoạn p1-p2."""

    p1: Diem
    p2: Diem
    khoang_offset: float
    layer: str = layers.DIM.ten
    nhan: str | None = None  # None -> backend tự hiển thị khoảng cách |p2-p1|
    co_chu: float = 15.0  # mm — cỡ chữ số kích thước; TỶ LỆ THEO QUY MÔ bản vẽ,
    # KHÔNG dùng chung 1 giá trị cho mọi loại bản vẽ. Thấy thật: 15mm (đúng cho
    # mặt cắt cỡ 250-700mm, xem ve_mat_cat_dam/cot) trở thành QUÁ NHỎ để đọc
    # được khi áp nguyên cho mặt đứng khung tổng thể cỡ 5600-14500mm (~20 lần
    # lớn hơn) — chữ số biến mất khỏi tầm nhìn dù dữ liệu hoàn toàn đúng.


@dataclass
class BanVe:
    """Toàn bộ đối tượng vẽ của 1 hình (1 mặt cắt, 1 mặt đứng, 1 bảng...)."""

    ten: str
    doan_thang: list[VeDoanThang] = field(default_factory=list)
    da_giac: list[VeDaGiac] = field(default_factory=list)
    vong_tron: list[VeVongTron] = field(default_factory=list)
    cung: list[VeCung] = field(default_factory=list)
    chu: list[VeChu] = field(default_factory=list)
    kich_thuoc: list[VeKichThuoc] = field(default_factory=list)

    def gop(self, khac: "BanVe") -> None:
        self.doan_thang.extend(khac.doan_thang)
        self.da_giac.extend(khac.da_giac)
        self.vong_tron.extend(khac.vong_tron)
        self.cung.extend(khac.cung)
        self.chu.extend(khac.chu)
        self.kich_thuoc.extend(khac.kich_thuoc)

    def dich_chuyen(self, dx: float, dy: float) -> "BanVe":
        """Trả về 1 BanVe mới, toàn bộ toạ độ đã dịch (dx,dy) — dùng để đặt
        1 hình đã vẽ ở hệ toạ độ cục bộ vào đúng vị trí trên tờ bản vẽ."""
        return BanVe(
            ten=self.ten,
            doan_thang=[VeDoanThang(dt.p1.dich(dx, dy), dt.p2.dich(dx, dy), dt.layer) for dt in self.doan_thang],
            da_giac=[VeDaGiac(tuple(d.dich(dx, dy) for d in dg.diem), dg.layer, dg.dong, dg.do_rong_net) for dg in self.da_giac],
            vong_tron=[VeVongTron(vt.tam.dich(dx, dy), vt.ban_kinh, vt.layer) for vt in self.vong_tron],
            cung=[VeCung(c.tam.dich(dx, dy), c.ban_kinh, c.goc_bat_dau_do, c.goc_ket_thuc_do, c.layer) for c in self.cung],
            chu=[VeChu(c.vi_tri.dich(dx, dy), c.noi_dung, c.chieu_cao, c.layer, c.canh_giua, c.canh_phai) for c in self.chu],
            kich_thuoc=[VeKichThuoc(kt.p1.dich(dx, dy), kt.p2.dich(dx, dy), kt.khoang_offset, kt.layer, kt.nhan, kt.co_chu) for kt in self.kich_thuoc],
        )


# ---------------------------------------------------------------------------
# Số lượng & vị trí mặt cắt ngang cần vẽ theo loại cấu kiện — yêu cầu Phase 3.
# ---------------------------------------------------------------------------


def xac_dinh_vi_tri_mat_cat_can_ve(loai: LoaiCauKien, la_console: bool = False) -> list[str]:
    """Trả về danh sách vị trí BẮT BUỘC phải có mặt cắt ngang cho 1 phần tử.

    - Cột: 1 mặt cắt đại diện ("dai_dien"), tại vị trí giữa đoạn cột.
    - Dầm nhịp thường (2 đầu đều có gối): 3 mặt cắt ("goi_trai","giua_nhip","goi_phai").
    - Dầm công-xôn (chỉ 1 đầu ngàm): 1 mặt cắt ("ngam"), tại vị trí ngàm.
    """
    if loai == LoaiCauKien.COT:
        return ["dai_dien"]
    if la_console:
        return ["ngam"]
    return ["goi_trai", "giua_nhip", "goi_phai"]


# ---------------------------------------------------------------------------
# Mặt cắt ngang — bố trí thép dọc theo hàng/lớp.
# ---------------------------------------------------------------------------

_KHOANG_HO_DUNG_TOI_THIEU = 25.0  # mm — mục 4.4 (khoảng hở đứng tối thiểu giữa 2 lớp).


def chia_lop_thep(
    danh_sach_duong_kinh: list[int], b: float, cover: float, duong_kinh_dai: float
) -> list[list[int]]:
    """Chia 1 hàng thép dọc thành nhiều lớp nếu vượt quá số thanh tối đa xếp
    được trong 1 lớp theo bề rộng b — dùng lại đúng công thức đã kiểm chứng ở
    Phase 1 (rule_engine.cot_doc.so_thanh_toi_da_1_lop, mục 4.4), không định
    nghĩa lại công thức khoảng cách ở đây."""
    if not danh_sach_duong_kinh:
        return []
    n_max = so_thanh_toi_da_1_lop(b, cover, duong_kinh_dai, max(danh_sach_duong_kinh))
    n_max = max(n_max, 1)
    return [danh_sach_duong_kinh[i : i + n_max] for i in range(0, len(danh_sach_duong_kinh), n_max)]


def toa_do_1_hang(
    b: float, cover: float, duong_kinh_dai: float, danh_sach_duong_kinh: list[int], y: float
) -> list[tuple[Diem, int]]:
    """Toạ độ tâm từng thanh trong 1 hàng, dàn đều theo bề rộng b."""
    if not danh_sach_duong_kinh:
        return []
    x_min = cover + duong_kinh_dai + danh_sach_duong_kinh[0] / 2
    x_max = b - cover - duong_kinh_dai - danh_sach_duong_kinh[-1] / 2
    n = len(danh_sach_duong_kinh)
    if n == 1:
        return [(Diem((x_min + x_max) / 2, y), danh_sach_duong_kinh[0])]
    buoc = (x_max - x_min) / (n - 1)
    return [(Diem(x_min + i * buoc, y), d) for i, d in enumerate(danh_sach_duong_kinh)]


def toa_do_nhieu_lop(
    b: float, cover: float, duong_kinh_dai: float, lop: list[list[int]], y_lop_dau: float, huong_len: bool
) -> list[tuple[Diem, int]]:
    """Toạ độ toàn bộ thanh qua nhiều lớp — huong_len=True: lớp sau cách xa
    gốc hơn theo +y (dùng cho thép TRÊN, gốc là mép dưới hình); huong_len=False:
    lớp sau theo -y (dùng cho thép DƯỚI nếu hệ trục đảo, tuỳ nơi gọi)."""
    ket_qua: list[tuple[Diem, int]] = []
    y_hien_tai = y_lop_dau
    for i, ds in enumerate(lop):
        ket_qua.extend(toa_do_1_hang(b, cover, duong_kinh_dai, ds, y_hien_tai))
        if i + 1 < len(lop):
            d_hien_tai = max(ds)
            d_ke_tiep = max(lop[i + 1])
            khoang_dich = d_hien_tai / 2 + _KHOANG_HO_DUNG_TOI_THIEU + d_ke_tiep / 2
            y_hien_tai += khoang_dich if huong_len else -khoang_dich
    return ket_qua


def ban_kinh_uon_dai(duong_kinh_dai: float) -> float:
    """Bán kính bo góc cốt đai tại chỗ uốn (mm) — mục 6.4 RULES_TCVN5574.md
    "Đường kính uốn tối thiểu" / 2. Cốt đai mặc định coi là thép TRƠN
    (co_go=False) vì thường dùng nhóm CB240-T (mục 8: "Thanh trơn"), khác với
    thép dọc thường có gờ — dùng neo_noi.duong_kinh_uon_toi_thieu đã kiểm
    chứng ở Phase 1, không định nghĩa lại công thức."""
    return duong_kinh_uon_toi_thieu(duong_kinh_dai, co_go=False) / 2


def duong_bao_chu_nhat_bo_tron(
    x0: float, y0: float, x1: float, y1: float, ban_kinh: float, layer: str
) -> tuple[list[VeDoanThang], list[VeCung]]:
    """Đường bao hình chữ nhật GÓC BO TRÒN từ (x0,y0) đến (x1,y1) — dùng cho
    CỐT ĐAI (uốn từ 1 thanh thép tròn, luôn có bán kính uốn tại góc theo mục
    6.4), KHÁC với đường bao bê tông (OUTLINE_CUT) vốn là mặt cắt thật, góc
    vuông sắc. Trả về (đoạn thẳng 4 cạnh đã rút ngắn, cung tròn 4 góc)."""
    r = max(0.0, min(ban_kinh, (x1 - x0) / 2, (y1 - y0) / 2))
    doan_thang = [
        VeDoanThang(Diem(x0 + r, y0), Diem(x1 - r, y0), layer),  # cạnh dưới
        VeDoanThang(Diem(x1, y0 + r), Diem(x1, y1 - r), layer),  # cạnh phải
        VeDoanThang(Diem(x1 - r, y1), Diem(x0 + r, y1), layer),  # cạnh trên
        VeDoanThang(Diem(x0, y1 - r), Diem(x0, y0 + r), layer),  # cạnh trái
    ]
    cung = (
        [
            VeCung(Diem(x1 - r, y0 + r), r, 270, 360, layer),  # góc dưới-phải
            VeCung(Diem(x1 - r, y1 - r), r, 0, 90, layer),  # góc trên-phải
            VeCung(Diem(x0 + r, y1 - r), r, 90, 180, layer),  # góc trên-trái
            VeCung(Diem(x0 + r, y0 + r), r, 180, 270, layer),  # góc dưới-trái
        ]
        if r > 0
        else []
    )
    return doan_thang, cung


def ve_mat_cat_dam(
    nhan: str,
    b: float,
    h: float,
    cover: float,
    duong_kinh_dai: float,
    thanh_duoi: list[int],
    thanh_tren: list[int],
) -> BanVe:
    """Vẽ 1 mặt cắt ngang dầm (chữ nhật) — RULES_TCVN5574.md mục 10.7.1/10.7.2.

    Hệ toạ độ cục bộ: gốc (0,0) tại góc dưới-trái tiết diện, x sang phải theo
    b, y lên trên theo h. thanh_duoi/thanh_tren: danh sách đường kính từng
    thanh (mm), tự động chia lớp theo chia_lop_thep nếu vượt quá 1 hàng.
    """
    bv = BanVe(ten=nhan)

    # Đường bao mặt cắt — nét liền MẢNH (bê tông coi như trong suốt, để cốt
    # thép nổi bật — KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md mục 1.2, TCVN 4612-88;
    # KHÔNG phải "rất đậm" như RULES_TCVN5574.md mục 10.7.2 từng ghi nhầm —
    # 2 tài liệu mâu thuẫn nhau, đã đối chiếu bản vẽ mẫu thật để xác nhận).
    goc = [Diem(0, 0), Diem(b, 0), Diem(b, h), Diem(0, h)]
    bv.da_giac.append(VeDaGiac(tuple(goc), layers.OUTLINE_CUT.ten))

    # Đường bao cốt đai — nét liền đậm, cách mép ngoài đúng `cover`, GÓC BO
    # TRÒN (thanh thép uốn có bán kính uốn tại góc, mục 6.4 — không phải góc
    # vuông sắc như đường bao bê tông ở trên).
    doan_thang_dai, cung_dai = duong_bao_chu_nhat_bo_tron(
        cover, cover, b - cover, h - cover, ban_kinh_uon_dai(duong_kinh_dai), layers.REBAR_STIRRUP.ten
    )
    bv.doan_thang.extend(doan_thang_dai)
    bv.cung.extend(cung_dai)

    # Thép dưới: lớp đầu tiên sát cạnh dưới, các lớp sau đi LÊN (+y).
    lop_duoi = chia_lop_thep(thanh_duoi, b, cover, duong_kinh_dai)
    if lop_duoi:
        y0 = cover + duong_kinh_dai + max(lop_duoi[0]) / 2
        for tam, d in toa_do_nhieu_lop(b, cover, duong_kinh_dai, lop_duoi, y0, huong_len=True):
            bv.vong_tron.append(VeVongTron(tam, d / 2, layers.REBAR_MAIN.ten))

    # Thép trên: lớp đầu tiên sát cạnh trên, các lớp sau đi XUỐNG (-y).
    lop_tren = chia_lop_thep(thanh_tren, b, cover, duong_kinh_dai)
    if lop_tren:
        y0 = h - cover - duong_kinh_dai - max(lop_tren[0]) / 2
        for tam, d in toa_do_nhieu_lop(b, cover, duong_kinh_dai, lop_tren, y0, huong_len=False):
            bv.vong_tron.append(VeVongTron(tam, d / 2, layers.REBAR_MAIN.ten))

    # Kích thước b, h — nét liền mảnh, đặt ra ngoài đường bao.
    bv.kich_thuoc.append(VeKichThuoc(Diem(0, -30), Diem(b, -30), khoang_offset=0, nhan=f"{b:g}"))
    bv.kich_thuoc.append(VeKichThuoc(Diem(-30, 0), Diem(-30, h), khoang_offset=0, nhan=f"{h:g}"))
    bv.chu.append(VeChu(Diem(b / 2, h + 40), nhan, chieu_cao=25, layer=layers.TEXT.ten, canh_giua=True))

    return bv


def toa_do_thep_chu_vi_hcn(
    b: float, h: float, cover: float, duong_kinh_dai: float,
    so_thanh_canh_b: int, duong_kinh_canh_b: int,
    so_thanh_canh_h: int, duong_kinh_canh_h: int,
) -> list[tuple[Diem, int]]:
    """Toạ độ thép bố trí ĐỀU CHU VI tiết diện chữ nhật (cột) — mục 4.2
    "Cột: bố trí đối xứng theo chu vi". so_thanh_canh_b: tổng số thanh trên
    MỖI cạnh song song trục b (kể cả 2 thanh góc); so_thanh_canh_h: tương tự
    cho cạnh h. 4 thanh góc dùng chung cho cả 2 cạnh (không nhân đôi)."""
    x_min = cover + duong_kinh_dai + duong_kinh_canh_b / 2
    x_max = b - cover - duong_kinh_dai - duong_kinh_canh_b / 2
    y_min = cover + duong_kinh_dai + duong_kinh_canh_h / 2
    y_max = h - cover - duong_kinh_dai - duong_kinh_canh_h / 2

    diem: dict[tuple[float, float], int] = {}

    def _rai_deu(gt_min, gt_max, n):
        if n <= 1:
            return [(gt_min + gt_max) / 2]
        buoc = (gt_max - gt_min) / (n - 1)
        return [gt_min + i * buoc for i in range(n)]

    for x in _rai_deu(x_min, x_max, so_thanh_canh_b):
        diem[(round(x, 6), round(y_min, 6))] = duong_kinh_canh_b
        diem[(round(x, 6), round(y_max, 6))] = duong_kinh_canh_b
    for y in _rai_deu(y_min, y_max, so_thanh_canh_h):
        diem.setdefault((round(x_min, 6), round(y, 6)), duong_kinh_canh_h)
        diem.setdefault((round(x_max, 6), round(y, 6)), duong_kinh_canh_h)

    return [(Diem(x, y), d) for (x, y), d in diem.items()]


def ve_mat_cat_cot(
    nhan: str,
    b: float,
    h: float,
    cover: float,
    duong_kinh_dai: float,
    so_thanh_canh_b: int,
    duong_kinh_canh_b: int,
    so_thanh_canh_h: int,
    duong_kinh_canh_h: int,
) -> BanVe:
    """Vẽ 1 mặt cắt ngang cột (chữ nhật, thép bố trí đều chu vi)."""
    bv = BanVe(ten=nhan)

    goc = [Diem(0, 0), Diem(b, 0), Diem(b, h), Diem(0, h)]
    bv.da_giac.append(VeDaGiac(tuple(goc), layers.OUTLINE_CUT.ten))

    doan_thang_dai, cung_dai = duong_bao_chu_nhat_bo_tron(
        cover, cover, b - cover, h - cover, ban_kinh_uon_dai(duong_kinh_dai), layers.REBAR_STIRRUP.ten
    )
    bv.doan_thang.extend(doan_thang_dai)
    bv.cung.extend(cung_dai)

    for tam, d in toa_do_thep_chu_vi_hcn(
        b, h, cover, duong_kinh_dai, so_thanh_canh_b, duong_kinh_canh_b, so_thanh_canh_h, duong_kinh_canh_h
    ):
        bv.vong_tron.append(VeVongTron(tam, d / 2, layers.REBAR_MAIN.ten))

    bv.kich_thuoc.append(VeKichThuoc(Diem(0, -30), Diem(b, -30), khoang_offset=0, nhan=f"{b:g}"))
    bv.kich_thuoc.append(VeKichThuoc(Diem(-30, 0), Diem(-30, h), khoang_offset=0, nhan=f"{h:g}"))
    bv.chu.append(VeChu(Diem(b / 2, h + 40), nhan, chieu_cao=25, layer=layers.TEXT.ten, canh_giua=True))

    return bv


# ---------------------------------------------------------------------------
# Bảng thống kê cốt thép — RULES_TCVN5574.md mục 10.7 (đối chiếu bản vẽ mẫu).
# ---------------------------------------------------------------------------

# Khối lượng riêng thép xây dựng — HẰNG SỐ VẬT LÝ tiêu chuẩn (7850 kg/m³),
# KHÔNG phải điều khoản của TCVN 5574:2018 (tài liệu không cho bảng kg/m) —
# cần thiết để lập cột "TRỌNG LƯỢNG" đúng như bản vẽ mẫu mục 10.7. Đối chiếu
# ngược với bảng thống kê trong data/samples/BoTriThep_KhungTruc5_mau.pdf
# (vd d=18, dài 4700mm, SL=144 -> 676,8m -> 1351,96kG) cho sai số < 0,1%.
KHOI_LUONG_RIENG_THEP_KG_M3 = 7850.0


def khoi_luong_tren_1m(duong_kinh: int) -> float:
    """kg/m — dùng đúng As (mm²) đã tra ở vat_lieu.dien_tich_1_thanh để khớp
    bảng đường kính chuẩn đã dùng xuyên suốt Rule Engine (mục 1.3)."""
    As_mm2 = dien_tich_1_thanh(duong_kinh)
    return As_mm2 * KHOI_LUONG_RIENG_THEP_KG_M3 / 1e6


@dataclass(frozen=True)
class DongThongKe:
    """1 dòng bảng thống kê cốt thép — ĐÚNG 8 cột bắt buộc theo mục 3.9
    `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md`: (1) tên cấu kiện, (2) số hiệu thanh,
    (3) hình dáng thanh, (4) đường kính, (5) chiều dài 1 thanh, (6) số lượng,
    (7) tổng chiều dài, (8) tổng trọng lượng.

    Trước đây bảng này chỉ có 7 cột (thiếu hẳn "số hiệu thanh" và "hình dáng
    thanh", có thừa 1 cột "STT" không nằm trong quy ước) — phát hiện khi viết
    bộ kiểm chứng cho Verification Agent (đối chiếu lại với
    `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md` mục 3.9 mới lộ ra thiếu 2 cột), đã sửa
    tận gốc ở đây thay vì chỉ nới lỏng điều kiện kiểm tra cho khớp cái sai.

    `so_hieu_thanh`: số hiệu tham chiếu (vd "①", "1", "N1") dùng để đối chiếu
    ngược lại ký hiệu ghi trên mặt cắt — do lớp gọi (Drawing Agent) tự đánh số
    tăng dần theo thứ tự xuất hiện, KHÔNG tính toán gì ở đây.
    `hinh_dang`: mô tả NGẮN dạng thanh (vd "Thẳng", "Đai kín", "Móc chữ L") —
    mục 3.9 gợi ý "phác thảo hình dáng", ở đây dùng MÔ TẢ CHỮ thay vì vẽ hình
    pictogram thu nhỏ trong ô (đơn giản hoá có chủ đích, đủ để tra cứu, không
    thuộc phạm vi vẽ chi tiết uốn móc thật — cùng tinh thần đơn giản hoá đã
    ghi rõ ở docstring `ve_chi_tiet_nut_khung`)."""

    ten_cau_kien: str  # vd "Dầm 32", "Cột C1"
    so_hieu_thanh: str
    hinh_dang: str
    duong_kinh: int
    chieu_dai_1_don_vi_mm: float
    so_luong: int
    tong_chieu_dai_m: float
    khoi_luong_kg: float


def tinh_dong_thong_ke(
    ten_cau_kien: str, so_hieu_thanh: str, hinh_dang: str,
    duong_kinh: int, chieu_dai_1_don_vi_mm: float, so_luong: int,
) -> DongThongKe:
    tong_chieu_dai_m = chieu_dai_1_don_vi_mm * so_luong / 1000
    khoi_luong_kg = tong_chieu_dai_m * khoi_luong_tren_1m(duong_kinh)
    return DongThongKe(
        ten_cau_kien, so_hieu_thanh, hinh_dang, duong_kinh,
        chieu_dai_1_don_vi_mm, so_luong, tong_chieu_dai_m, khoi_luong_kg,
    )


def ve_bang_thong_ke(
    ten: str,
    dong: list[DongThongKe],
    do_rong_cot: list[float],
    chieu_cao_dong: float = 30.0,
) -> BanVe:
    """Vẽ khung bảng + nội dung từng ô — layer TEXT (khung bảng là nét liền
    mảnh theo mục 10.7.2). 8 cột ĐÚNG thứ tự mục 3.9: Cấu kiện, Số hiệu, Hình
    dáng, Đường kính, Chiều dài 1 thanh, Số lượng, Tổng chiều dài, Khối
    lượng. `do_rong_cot` phải có đúng 8 phần tử (1 độ rộng cho mỗi cột)."""
    bv = BanVe(ten=ten)
    tieu_de = ["CẤU KIỆN", "SỐ HIỆU", "HÌNH DÁNG", "Ø(mm)", "DÀI 1CK(mm)", "SL", "TỔNG DÀI(m)", "K.LƯỢNG(kG)"]
    if len(do_rong_cot) != len(tieu_de):
        raise ValueError(f"do_rong_cot phải có đúng {len(tieu_de)} phần tử (1 cho mỗi cột mục 3.9), nhận {len(do_rong_cot)}.")
    tong_rong = sum(do_rong_cot)
    so_hang = len(dong) + 1  # +1 tiêu đề
    cao_bang = chieu_cao_dong * so_hang

    x_cot = [0.0]
    for w in do_rong_cot:
        x_cot.append(x_cot[-1] + w)

    for i in range(so_hang + 1):
        y = cao_bang - i * chieu_cao_dong
        bv.doan_thang.append(VeDoanThang(Diem(0, y), Diem(tong_rong, y), layers.TEXT.ten))
    for x in x_cot:
        bv.doan_thang.append(VeDoanThang(Diem(x, 0), Diem(x, cao_bang), layers.TEXT.ten))

    y_tieu_de = cao_bang - chieu_cao_dong / 2
    for i, tieu in enumerate(tieu_de):
        x_giua = (x_cot[i] + x_cot[i + 1]) / 2
        bv.chu.append(VeChu(Diem(x_giua, y_tieu_de), tieu, chieu_cao=12, layer=layers.TEXT.ten, canh_giua=True))

    for hang, d in enumerate(dong, start=1):
        y = cao_bang - (hang + 0.5) * chieu_cao_dong
        gia_tri = [
            d.ten_cau_kien, d.so_hieu_thanh, d.hinh_dang, str(d.duong_kinh),
            f"{d.chieu_dai_1_don_vi_mm:g}", str(d.so_luong),
            f"{d.tong_chieu_dai_m:.2f}", f"{d.khoi_luong_kg:.2f}",
        ]
        for i, gt in enumerate(gia_tri):
            x_giua = (x_cot[i] + x_cot[i + 1]) / 2
            bv.chu.append(VeChu(Diem(x_giua, y), gt, chieu_cao=10, layer=layers.TEXT.ten, canh_giua=True))

    return bv


# ---------------------------------------------------------------------------
# Khung tên — RULES_TCVN5574.md mục 10.7 (checklist "khung tên").
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThongTinKhungTen:
    ten_truong: str
    khoa: str
    chuyen_nganh: str
    ten_do_an: str
    gvhd: str
    svth: str
    de_so: str
    ngay_nhan: str
    ngay_hoan_thanh: str


def ve_khung_ten(rong: float, cao: float, thong_tin: ThongTinKhungTen) -> BanVe:
    bv = BanVe(ten="KHUNG_TEN")
    bv.da_giac.append(VeDaGiac((Diem(0, 0), Diem(rong, 0), Diem(rong, cao), Diem(0, cao)), layers.OUTLINE.ten))

    dong = [
        thong_tin.ten_truong, thong_tin.khoa, thong_tin.chuyen_nganh, thong_tin.ten_do_an,
        f"GVHD: {thong_tin.gvhd}", f"SVTH: {thong_tin.svth}",
        f"Đề số: {thong_tin.de_so}", f"Ngày nhận: {thong_tin.ngay_nhan}", f"Hoàn thành: {thong_tin.ngay_hoan_thanh}",
    ]
    buoc_y = cao / (len(dong) + 1)
    for i, noi_dung in enumerate(dong, start=1):
        bv.chu.append(VeChu(Diem(rong / 2, cao - i * buoc_y), noi_dung, chieu_cao=14, layer=layers.TEXT.ten, canh_giua=True))

    return bv


# ---------------------------------------------------------------------------
# Ký hiệu SỐ HIỆU thanh thép (vòng tròn + đường dẫn) — KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md
# mục 2.2 (TCVN 4612-88). Thay cho cách ghi chữ dài trực tiếp cạnh cấu kiện
# (vd "8Ø25 (đều chu vi...)") — LỖI THẬT đã gặp, sai quy cách bản vẽ kỹ thuật
# xây dựng thật (xác nhận qua đối chiếu data/samples/BoTriThep_KhungTruc5_mau.pdf).
# Dùng lại được cho CẢ mặt đứng khung (dưới đây) LẪN mặt cắt (Phase B sau này).
# ---------------------------------------------------------------------------


def ve_ky_hieu_so_hieu(
    diem_tro_toi: Diem, diem_ngang: Diem, so_hieu: int, tren: str, duoi: str | None = None,
    huong_ngang: int = 1, do_dai_ngang: float = 250.0, ban_kinh_vong_tron: float = 90.0,
    chieu_cao_chu: float = 100.0, chieu_cao_so_hieu: float = 110.0,
) -> BanVe:
    """Vẽ 1 ký hiệu "số hiệu thanh thép" hoàn chỉnh: đường dẫn (leader) từ
    `diem_tro_toi` (vị trí thanh thép thật) → `diem_ngang` (điểm gấp khúc) →
    đoạn ngang dài `do_dai_ngang` theo hướng `huong_ngang` (+1 phải, -1 trái)
    → vòng tròn Ø(2×ban_kinh_vong_tron) chứa số hiệu ở cuối đoạn ngang.
    `tren` (bắt buộc, vd "2Ø18") đặt PHÍA TRÊN đoạn ngang; `duoi` (tuỳ chọn,
    vd "L=4700" cho thép dọc hoặc "a=200" cho cốt đai) đặt PHÍA DƯỚI — đúng
    quy ước mục 2.2 nguyên văn.

    Toàn bộ đường dẫn + vòng tròn + số hiệu nằm trên layer SO_HIEU (mảnh —
    mục 2.2: "vòng tròn... nét liền mảnh", KHÁC layer REBAR_MAIN đậm nhất
    dành cho tiết diện thanh thép THẬT trên mặt cắt); chữ `tren`/`duoi` trên
    layer TEXT (cùng nhóm chú thích với nhãn/kích thước khác)."""
    bv = BanVe(ten="KY_HIEU_SO_HIEU")
    diem_vong_tron = Diem(diem_ngang.x + huong_ngang * do_dai_ngang, diem_ngang.y)

    bv.doan_thang.append(VeDoanThang(diem_tro_toi, diem_ngang, layers.SO_HIEU.ten))
    bv.doan_thang.append(VeDoanThang(diem_ngang, diem_vong_tron, layers.SO_HIEU.ten))
    bv.vong_tron.append(VeVongTron(diem_vong_tron, ban_kinh_vong_tron, layers.SO_HIEU.ten))
    bv.chu.append(VeChu(diem_vong_tron, str(so_hieu), chieu_cao=chieu_cao_so_hieu, layer=layers.SO_HIEU.ten, canh_giua=True))

    bv.chu.append(
        VeChu(
            Diem(diem_vong_tron.x, diem_vong_tron.y + ban_kinh_vong_tron + 30), tren,
            chieu_cao=chieu_cao_chu, layer=layers.TEXT.ten, canh_giua=True,
        )
    )
    if duoi:
        bv.chu.append(
            VeChu(
                Diem(diem_vong_tron.x, diem_vong_tron.y - ban_kinh_vong_tron - 30 - chieu_cao_chu), duoi,
                chieu_cao=chieu_cao_chu, layer=layers.TEXT.ten, canh_giua=True,
            )
        )
    return bv


# ---------------------------------------------------------------------------
# Mặt đứng khung (đơn giản hoá) — cột/dầm dạng hình chữ nhật đặt theo lưới
# trục (x) và cao độ (y) truyền vào tường minh, cùng đường tim trục (AXIS) và
# ghi chú cao độ. Mọi khoảng cách là THAM SỐ — không hard-code theo mẫu.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KyHieuThep:
    """1 loại thanh thép cần ghi ký hiệu (số hiệu + số lượng/đường kính +
    chiều dài) tại 1 vị trí cụ thể trên cấu kiện — xem `ve_ky_hieu_so_hieu`.
    1 vị trí (vd "goi_trai") có thể cần NHIỀU KyHieuThep nếu tổ hợp thép ở đó
    gồm nhiều đường kính khác nhau (vd "1Ø20+1Ø22" -> 2 số hiệu riêng, mỗi
    loại thanh 1 số hiệu — đúng mục 2.2, KHÔNG gộp chung 1 ký hiệu)."""

    so_hieu: int
    so_luong_duong_kinh: str  # vd "2Ø18"
    chieu_dai: str | None = None  # vd "L=4700" (thép dọc) hoặc "a=200" (cốt đai) — None nếu không có
    vi_tri_tren_cau_kien: str = "dai_dien"  # "dai_dien" | "goi_trai" | "giua_nhip" | "goi_phai"


@dataclass(frozen=True)
class DoanCotVe:
    x_truc: float  # mm — vị trí trục đứng cột trên mặt đứng
    y_duoi: float  # mm — cao độ đáy đoạn cột
    y_tren: float  # mm — cao độ đỉnh đoạn cột
    b: float  # mm — bề rộng tiết diện cột hiển thị trên mặt đứng
    nhan: str = ""  # tên cấu kiện (vd "1") — vẫn hiển thị riêng, KHÔNG kèm mô tả thép nữa
    ky_hieu: tuple[KyHieuThep, ...] = ()


@dataclass(frozen=True)
class DoanDamVe:
    x_trai: float
    x_phai: float
    y_truc: float  # mm — cao độ trục dầm (thường = cao độ sàn/tầng)
    h: float  # mm — chiều cao tiết diện dầm hiển thị
    nhan: str = ""
    ky_hieu: tuple[KyHieuThep, ...] = ()


def ve_mat_dung_khung(
    ten_truc_dung: list[str],
    x_truc_dung: list[float],
    ten_cao_do: list[str],
    y_cao_do: list[float],
    cac_cot: list[DoanCotVe],
    cac_dam: list[DoanDamVe],
    moc_tham_chieu: list[tuple[str, float]] | None = None,
    ten_mat_dat: str | None = None,
    x_truc_dung_nhan: list[float] | None = None,
    y_cao_do_nhan: list[float] | None = None,
) -> BanVe:
    """Vẽ mặt đứng khung: đường tim trục (AXIS), ghi chú cao độ (TEXT), kích
    thước nhịp/chiều cao tầng (DIM), và hình chữ nhật cột/dầm (OUTLINE) theo
    đúng toạ độ x_truc_dung/y_cao_do đã truyền vào — các toạ độ này phải đến
    từ lưới trục + cao độ đã chuẩn hoá ở Input Adapter (mục 10.7.1), KHÔNG tự
    đặt trong hàm này.

    Thấy thật: bản đầu tiên của hàm này KHÔNG vẽ kích thước (chỉ có đường tim
    trục + tên trục/cao độ) — nhìn giống sơ đồ trống, thiếu hẳn thông tin
    khoảng cách nhịp/chiều cao tầng mà 1 bản vẽ kết cấu thật LUÔN phải có
    (mục 10.7 checklist "mặt đứng khung" + đối chiếu bản vẽ mẫu). Đã bổ sung
    3 hàng kích thước: nhịp từng khoang (DIM ngang, hàng trong), tổng bề rộng
    (DIM ngang, hàng ngoài), và chiều cao từng tầng (DIM dọc, bên trái).

    Cỡ chữ/khoảng cách offset dưới đây LỚN HƠN NHIỀU so với `ve_mat_cat_dam/
    cot` (chieu_cao=15-20mm) — thấy thật: mặt đứng khung tổng thể có quy mô
    ~5600-14500mm, lớn hơn ~20 lần 1 mặt cắt (~250-700mm); dùng nguyên cỡ chữ
    của mặt cắt khiến số liệu/nhãn trở nên QUÁ NHỎ để đọc được trên bản vẽ
    (dữ liệu đúng nhưng chữ biến mất khỏi tầm nhìn thực tế) dù không phải lỗi
    hình học. Cỡ chữ chọn theo mục 10.7 (chữ ghi chú bản vẽ kết cấu ~200mm ở
    tỷ lệ model space 1:1, tương đương ~2mm trên giấy in tỷ lệ 1:100).

    Ký hiệu/bố cục theo đúng NGUỒN CÓ THỂ TRA CỨU ĐƯỢC — Giáo Trình Vẽ Kỹ
    Thuật Xây Dựng (Nguyễn Quang Cự - Nguyễn Mạnh Dũng, NXB Giáo Dục), mục
    2.2 "Các hình biểu diễn thẳng góc của ngôi nhà" (tr.161-171) và mục 1.2
    "Bản vẽ kết cấu bê tông cốt thép" (tr.154-157) — KHÔNG tự đặt tuỳ tiện
    theo trí nhớ hình ảnh nữa:
    - Tên trục đặt trong VÒNG TRÒN (bong bóng trục), đường kính 7-8mm trên
      giấy in, vẽ bằng NÉT LIỀN MẢNH, chữ viết NGANG (giáo trình mục 2.2.2.a,
      tr.164-165) — không phải chữ nổi tự do, không xoay theo trục.
    - Ghi cao độ dùng ký hiệu "▽", ĐỈNH tam giác CHẠM đường mức cần ghi,
      đơn vị mét, 2-3 chữ số lẻ (giáo trình mục 2.5.3, tr.28, ví dụ Hình
      I.24/III.5/III.7: "+8.900", "±0.000", "-0.450").
    - "Mặt đứng được vẽ bằng nét liền mảnh... RIÊNG ĐƯỜNG MẶT ĐẤT vẽ bằng
      NÉT LIỀN ĐẬM" (giáo trình mục 2.2.1, tr.168, nguyên văn) — mốc cao độ
      đại diện cho mặt đất tự nhiên (tham số `ten_mat_dat`) phải vẽ đường
      tim mốc bằng layers.OUTLINE (đậm), KHÔNG dùng chung nét chấm gạch mảnh
      (layers.AXIS) như các mốc tầng kết cấu khác — bản trước vi phạm điều
      này, vẽ mọi mốc cùng 1 kiểu nét.
    - Với bản vẽ BỐ TRÍ KẾT CẤU (khác mặt đứng kiến trúc thuần tuý): "phải
      thể hiện rõ trục định vị, khoảng cách giữa các trục và kích thước tổng
      cộng, cùng các cao độ ở những độ cao đặc trưng" (TCVN 5572:2012, Điều
      4.2, xác nhận qua tra cứu web) — nên VẪN GHI kích thước nhịp/chiều cao
      (khác quy tắc "mặt đứng kiến trúc không cần ghi kích thước" ở tr.168,
      vì đây không phải mặt đứng kiến trúc thuần tuý).
    - Mũi tên kích thước dùng gạch chéo 45° (cấu hình ở `backend_com.py`,
      `ArrowheadType=acArrowArchTick`) — đúng quy ước kiến trúc/xây dựng, khác
      mũi tên đóng kiểu cơ khí mà giáo trình mục 2.5.2 (tr.25, Hình I.17)
      dùng cho bản vẽ chi tiết máy; bản vẽ công trình "cho phép thay các mũi
      tên bằng gạch chéo" (tr.25, nguyên văn).
    - Nhãn cấu kiện chỉ ghi tiết diện "bxh" ngắn gọn (vd "220x300"), KHÔNG
      ghép thêm số hiệu phần tử — thấy thật: chuỗi dài "C17-220x300" đặt cạnh
      "C21-220x220" ở 2 trục cách nhau 1500mm bị dính liền, không có khoảng
      trắng phân tách; "bxh" ngắn hơn nhiều nên đủ chỗ.

    moc_tham_chieu: các mốc cao độ KIẾN TRÚC bổ sung (vd "Tự nhiên" -0.450,
    "Tôn nền" 0.000, "Đỉnh móng" -1.000) — thấy thật: ảnh mẫu người dùng cung
    cấp có thêm các mốc này mà dữ liệu ETABS (chỉ có Story Definitions kết
    cấu) không có. Các mốc này CHỈ vẽ ký hiệu tam giác + chữ (giống
    ten_cao_do/y_cao_do), KHÔNG tham gia chuỗi kích thước chiều cao bên trái
    — nếu gộp chung vào ten_cao_do/y_cao_do sẽ làm SAI chuỗi kích thước (vd
    "4200" giữa 2 tầng kết cấu bị chẻ nhỏ thành "550+450+3200" vì các mốc phụ
    này chen giữa), trong khi bản vẽ mẫu vẫn giữ nguyên "4200" ở kích thước
    và chỉ ghi thêm các mốc phụ như chú thích tham chiếu riêng.

    ten_mat_dat: tên (khớp đúng chuỗi trong ten_cao_do hoặc moc_tham_chieu)
    của mốc đại diện MẶT ĐẤT TỰ NHIÊN — đường tim mốc này vẽ NÉT LIỀN ĐẬM
    (layers.OUTLINE) thay vì nét chấm gạch mảnh, đúng nguyên văn giáo trình
    tr.168 "Riêng đường mặt đất vẽ bằng nét liền đậm". None -> không mốc nào
    được vẽ đậm (mọi mốc dùng chung nét chấm gạch mảnh như cũ).

    x_truc_dung_nhan/y_cao_do_nhan: giá trị THẬT (mm) dùng để GHI SỐ (kích
    thước nhịp/chiều cao tầng, số cao độ ▽) — None -> dùng luôn x_truc_dung/
    y_cao_do (hành vi cũ, vẽ đúng tỷ lệ thật). Khi khác None (từng phần tử
    khớp theo CHỈ SỐ với x_truc_dung/y_cao_do), HÌNH HỌC (vị trí trục/cột/
    dầm/mốc cao độ) vẫn vẽ theo x_truc_dung/y_cao_do (có thể là toạ độ
    SCHEMATIC đều nhau), còn CON SỐ ghi trên bản vẽ lấy từ tham số `_nhan`
    này — thấy thật: người dùng phản hồi trực tiếp khi xem bản vẽ vẽ đúng tỷ
    lệ thật ("tại sao lại phải có đoạn thì to đoạn thì nhỏ... tôi thấy trong
    bản vẽ người ta vẽ khung bằng nhau cơ mà") — nhịp/tầng ngắn bị nén sát,
    mất cân đối và không đủ chỗ cho ký hiệu số hiệu. Xác nhận qua tra cứu:
    "sơ đồ bố trí thép không cần vẽ theo đúng tỷ lệ... các kích thước cụ thể
    vẫn phải ghi rõ" — đúng cách tách biệt ở đây: hình học vẽ đều (dễ đọc),
    số liệu ghi chú vẫn TRUNG THỰC 100% với dữ liệu thật (không bịa số).
    """
    x_truc_dung_nhan = x_truc_dung_nhan if x_truc_dung_nhan is not None else x_truc_dung
    y_cao_do_nhan = y_cao_do_nhan if y_cao_do_nhan is not None else y_cao_do

    CHIEU_CAO_CHU_TRUC = 250.0
    CO_CHU_KICH_THUOC = 200.0
    BAN_KINH_BONG_BONG = 350.0

    bv = BanVe(ten="MAT_DUNG_KHUNG")

    y_min, y_max = min(y_cao_do), max(y_cao_do)
    y_bong_bong = y_min - 1600  # dưới cả 2 hàng kích thước nhịp, tránh chồng lấn
    for x, ten in zip(x_truc_dung, ten_truc_dung):
        bv.doan_thang.append(VeDoanThang(Diem(x, y_bong_bong), Diem(x, y_max + 300), layers.AXIS.ten))
        # Bong bóng trục (vòng tròn + chữ) dùng layer AXIS (cyan, màu phụ duy
        # nhất — xem giải thích ở layers.py) — cùng nhóm "chú thích" với kích
        # thước/cao độ, tách biệt với OUTLINE (trắng/đen, hình học thật).
        bv.vong_tron.append(VeVongTron(Diem(x, y_bong_bong - BAN_KINH_BONG_BONG), BAN_KINH_BONG_BONG, layers.AXIS.ten))
        bv.chu.append(VeChu(Diem(x, y_bong_bong - BAN_KINH_BONG_BONG), ten, chieu_cao=CHIEU_CAO_CHU_TRUC, layer=layers.AXIS.ten, canh_giua=True))

    # Ký hiệu mức cao độ theo đúng mục 10.7: "ghi bằng ký hiệu mức (±0.000,
    # +3.900…) KÈM MŨI TÊN TAM GIÁC" — đặt BÊN PHẢI khung (tách phía với kích
    # thước chiều cao tầng bên trái). Tam giác RỖNG, ĐỈNH CHẠM đúng đường mức
    # chỉ THẲNG XUỐNG, thân tam giác nằm PHÍA TRÊN đường mức — đúng hình dạng
    # ký hiệu cao độ "▽" chuẩn (không phải tam giác nằm ngang như bản trước,
    # đó là hướng SAI — ký hiệu cao độ luôn chỉ vuông góc xuống mặt mốc).
    KICH_THUOC_TAM_GIAC = 130.0
    x_min, x_max = min(x_truc_dung), max(x_truc_dung)

    def _ve_moc_cao_do(y: float, y_nhan: float, ten: str, ve_duong_tim: bool) -> None:
        if ve_duong_tim:
            # Đường mặt đất tự nhiên: NÉT LIỀN ĐẬM (giáo trình tr.168, nguyên
            # văn "Riêng đường mặt đất vẽ bằng nét liền đậm") — các mốc khác
            # (tầng kết cấu, tôn nền, đỉnh móng) vẫn dùng nét chấm gạch mảnh
            # như đường tim trục thông thường.
            layer_duong_tim = layers.OUTLINE.ten if ten == ten_mat_dat else layers.AXIS.ten
            bv.doan_thang.append(VeDoanThang(Diem(x_min - 300, y), Diem(x_max + 300, y), layer_duong_tim))
        x_tam_giac = x_max + 500
        # Tam giác + chữ cao độ dùng layer AXIS (magenta theo layers.py hiện
        # tại — comment cũ ghi nhầm "cyan", xem layers._MAU_TRUC) — đúng màu
        # mốc cao độ (▽ + số) thấy trong ảnh chụp bản vẽ CAD thật người dùng
        # gửi (cùng màu với đường mốc dash-dot), KHÁC màu kích thước chi tiết
        # (DIM, cyan) — bản trước đặt nhầm sang layer DIM.
        bv.da_giac.append(
            VeDaGiac(
                (
                    Diem(x_tam_giac, y),  # đỉnh, chạm đúng đường mức
                    Diem(x_tam_giac - KICH_THUOC_TAM_GIAC, y + KICH_THUOC_TAM_GIAC * 1.6),
                    Diem(x_tam_giac + KICH_THUOC_TAM_GIAC, y + KICH_THUOC_TAM_GIAC * 1.6),
                ),
                layers.AXIS.ten,
            )
        )
        # Căn TRÁI mặc định (mọc sang phải) — bên phải khung không còn nội
        # dung nào khác nên chữ mọc tự nhiên ra ngoài, không cần căn phải.
        # CHỈ ghi số cao độ, KHÔNG kèm tên mốc (ten) — thấy thật: người dùng
        # phản hồi trực tiếp "bỏ mấy chữ tầng tầng đi, không cần thiết" — vị
        # trí theo chiều dọc đã đủ cho biết đang ở mốc nào, tên lặp lại
        # ("Tang2", "Tang3"...) chỉ gây rối không cần thiết. 2 số lẻ theo
        # đúng mục 2.1/3 KY_HIEU_NET_VE_QUY_TAC_BO_TRI.pdf ("VD ▽+3,00").
        bv.chu.append(
            VeChu(
                Diem(x_tam_giac + KICH_THUOC_TAM_GIAC + 80, y),
                f"{y_nhan/1000:+.2f}", chieu_cao=CHIEU_CAO_CHU_TRUC, layer=layers.AXIS.ten,
            )
        )

    for y, y_nhan, ten in zip(y_cao_do, y_cao_do_nhan, ten_cao_do):
        _ve_moc_cao_do(y, y_nhan, ten, ve_duong_tim=True)

    # Mốc kiến trúc bổ sung (Tự nhiên/Tôn nền/Đỉnh móng...) — CHỈ ký hiệu tam
    # giác + chữ, KHÔNG vẽ lại đường tim trục ngang (đã đủ dày đặc) và KHÔNG
    # tham gia chuỗi kích thước chiều cao bên dưới. Vị trí VÀ số ghi đều lấy
    # thẳng từ `y` (không đi qua toạ độ vẽ/schematic — các mốc này do người
    # gọi truyền trực tiếp bằng mm thật, không nằm trong hệ trục schematic).
    for ten, y in moc_tham_chieu or []:
        _ve_moc_cao_do(y, y, ten, ve_duong_tim=True)

    # Kích thước nhịp — hàng trong (từng khoang giữa 2 trục liên tiếp) + hàng
    # ngoài (tổng bề rộng), đặt dưới đường tim trục thấp nhất. LUÔN truyền
    # `nhan` tường minh (tự tính |p2-p1|) thay vì để backend tự đo — thấy
    # thật: dimstyle mặc định "EZDXF" của ezdxf có dimlfac=100 (hệ số nhân
    # khi hiển thị), khiến 5600 hiển thị thành "560000" nếu để tự đo. Cùng
    # khuôn mẫu đã dùng đúng từ trước ở ve_mat_cat_dam/cot (luôn tự tính nhãn
    # kích thước, không phụ thuộc cấu hình dimstyle của backend).
    #
    # layer=AXIS (magenta theo layers.py — comment cũ ghi nhầm "cyan", xem
    # layers._MAU_TRUC): đúng màu chuỗi kích thước TỔNG THỂ (nhịp/chiều cao
    # tầng) thấy trong ảnh chụp bản vẽ CAD thật người dùng gửi — khác màu
    # (DIM, cyan, mặc định của VeKichThuoc) dành cho kích thước CHI TIẾT bên
    # trong 1 cấu kiện (vd vị trí cắt cốt thép) mà mặt đứng khung tổng thể
    # này chưa thể hiện tới mức đó.
    # Vị trí (x1/x2) lấy từ toạ độ VẼ (x_truc_dung, có thể schematic-đều);
    # NHÃN (`nhan=`) lấy từ toạ độ THẬT (x_truc_dung_nhan) — 2 trục có thể
    # khác nhau, xem giải thích ở docstring tham số x_truc_dung_nhan.
    truc_sx = sorted(zip(x_truc_dung, x_truc_dung_nhan, ten_truc_dung))
    for (x1, xt1, _), (x2, xt2, _) in zip(truc_sx, truc_sx[1:]):
        bv.kich_thuoc.append(
            VeKichThuoc(Diem(x1, y_min - 800), Diem(x2, y_min - 800), khoang_offset=0, nhan=f"{abs(xt2 - xt1):g}", co_chu=CO_CHU_KICH_THUOC, layer=layers.AXIS.ten)
        )
    if len(truc_sx) >= 2:
        tong_rong = abs(truc_sx[-1][1] - truc_sx[0][1])
        bv.kich_thuoc.append(
            VeKichThuoc(Diem(truc_sx[0][0], y_min - 1200), Diem(truc_sx[-1][0], y_min - 1200), khoang_offset=0, nhan=f"{tong_rong:g}", co_chu=CO_CHU_KICH_THUOC, layer=layers.AXIS.ten)
        )

    # Kích thước chiều cao từng tầng — đặt bên trái đường tim trục ngoài
    # cùng. Cùng nguyên tắc vị trí-vẽ/nhãn-thật tách biệt như trên.
    cao_do_sx = sorted(zip(y_cao_do, y_cao_do_nhan, ten_cao_do))
    for (y1, yt1, _), (y2, yt2, _) in zip(cao_do_sx, cao_do_sx[1:]):
        bv.kich_thuoc.append(
            VeKichThuoc(Diem(x_min - 800, y1), Diem(x_min - 800, y2), khoang_offset=0, nhan=f"{abs(yt2 - yt1):g}", co_chu=CO_CHU_KICH_THUOC, layer=layers.AXIS.ten)
        )

    # Bố cục nhãn cấu kiện — SỬA LẠI lần cuối, thay bản góc trên-trái trước
    # đó: đặt ở góc trên-trái khiến nhãn cột và nhãn dầm CÙNG CHỤM vào đúng
    # 1 dải ngang hẹp tại mỗi chỗ nút khung (đỉnh cột trùng đúng độ cao đáy
    # dầm) — chồng lấn với đường mốc tầng, kích thước, và nhãn cấu kiện lân
    # cận ngay tại đó; thấy thật: người dùng phản hồi trực tiếp "nếu bố trí
    # như này thì vẽ lên thêm sẽ bị rối". Nay tách 2 nhãn ra 2 VÙNG TRỐNG
    # riêng biệt, không cấu kiện/chú thích nào khác đi qua:
    # - Nhãn CỘT: giữa chiều cao đoạn cột (khoảng trống rộng nhất của cột,
    #   cách xa cả 2 đầu nút khung).
    # - Nhãn DẦM: ngay TRÊN đường bao dầm (khoảng trống giữa đỉnh dầm và đáy
    #   cột tầng trên, không cấu kiện nào khác chiếm chỗ ở đó), canh giữa
    #   theo chiều dài dầm.
    # Đường bao cột/dầm trên mặt đứng khung — KHÔNG đặt do_rong_net (độ rộng
    # hình học ép cứng, sẽ đè lên mọi giá trị Lineweight của layer OUTLINE dù
    # là bao nhiêu). LỖI THẬT đã gặp: bản trước ép do_rong_net=25.0mm khiến
    # đường bao bê tông LUÔN vẽ đậm bất kể layers.py cấu hình gì — vi phạm
    # đúng nguyên tắc "bê tông trong suốt, cốt thép nổi bật" (KY_HIEU mục
    # 1.2) mà layers.OUTLINE (nay đã sửa về nét mảnh) đang cố thể hiện. Bỏ
    # hẳn tham số này — đường bao chỉ còn phụ thuộc Lineweight của layer.
    LE_NHAN_TRAI = 40.0  # mm — khoảng lùi nhãn cột vào từ mép trái
    CHIEU_CAO_CHU_NHAN_GON = 130.0  # nhỏ hơn bản trước (180) — đủ đọc, đỡ chiếm chỗ

    # Khoảng cách xếp chồng khi CÙNG 1 vị trí (vd "goi_trai") có nhiều ký hiệu
    # (nhiều đường kính khác nhau trong cùng tổ hợp, vd "1Ø20+1Ø22") — mỗi
    # ký hiệu thêm lùi ra xa hơn 1 khoảng, tránh chồng lên ký hiệu trước đó.
    # 420 (không phải 260) — thấy thật: 260mm khiến chữ "L=..." của 2 ký hiệu
    # liền kề (vd 2 đường kính khác nhau cùng "goi_trai") chồng lên nhau, dù
    # vòng tròn không chồng — xác nhận qua đọc lại PDF xuất thật.
    BUOC_XEP_CHONG_KY_HIEU = 420.0

    for cot in cac_cot:
        x0, x1 = cot.x_truc - cot.b / 2, cot.x_truc + cot.b / 2
        y_giua = (cot.y_duoi + cot.y_tren) / 2
        bv.da_giac.append(
            VeDaGiac(
                (Diem(x0, cot.y_duoi), Diem(x1, cot.y_duoi), Diem(x1, cot.y_tren), Diem(x0, cot.y_tren)),
                layers.OUTLINE.ten,
            )
        )
        if cot.nhan:
            bv.chu.append(
                VeChu(Diem(x0 + LE_NHAN_TRAI, y_giua), cot.nhan, chieu_cao=CHIEU_CAO_CHU_NHAN_GON, layer=layers.TEXT.ten)
            )
        # Đường thép dọc THẬT — 2 đường (mép gần/mép xa, đơn giản hoá chuẩn
        # cho mặt đứng: số lượng/cách bố trí CHÍNH XÁC quanh chu vi chỉ mặt
        # cắt mới thể hiện đủ) chạy suốt chiều cao đoạn cột, cách mép `COVER`
        # — LỖI THẬT đã gặp: thiếu hẳn phần này khiến khung chỉ có đường bao
        # trống + ký hiệu lơ lửng, KHÔNG trông như "có thép bên trong" (đối
        # chiếu trực tiếp bản vẽ mẫu thật — người dùng phản hồi trực tiếp).
        # Layer REBAR_MAIN (đậm nhất bản vẽ, mục 1.2 KY_HIEU) — đây MỚI là
        # tiết diện/đường thép thật, khác hẳn layer SO_HIEU (mảnh) của ký
        # hiệu số hiệu.
        if cot.ky_hieu:
            COVER_COT = 40.0
            x_gan, x_xa = x0 + COVER_COT, x1 - COVER_COT
            bv.doan_thang.append(VeDoanThang(Diem(x_gan, cot.y_duoi), Diem(x_gan, cot.y_tren), layers.REBAR_MAIN.ten))
            bv.doan_thang.append(VeDoanThang(Diem(x_xa, cot.y_duoi), Diem(x_xa, cot.y_tren), layers.REBAR_MAIN.ten))
            # Vạch cốt đai MINH HOẠ — nối 2 đường thép dọc tại các khoảng cách
            # ĐỀU NHAU thuần tuý trực quan (KHÔNG phải bước đai tính toán thật
            # — dữ liệu đó (`tinh_cot_dai`) hiện CHƯA truyền tới bước lắp ráp
            # mặt đứng khung, xem Phase B). Mục đích CHỈ để không bỏ trống
            # hoàn toàn "có cốt đai ở đây" — lỗi thật đã gặp: người dùng phản
            # hồi trực tiếp "không thấy nét thép đai đâu" khi xem bản vẽ thật.
            BUOC_DAI_MINH_HOA = 450.0
            so_dai = max(2, round((cot.y_tren - cot.y_duoi) / BUOC_DAI_MINH_HOA))
            for i in range(so_dai + 1):
                y_dai = cot.y_duoi + i * (cot.y_tren - cot.y_duoi) / so_dai
                bv.doan_thang.append(VeDoanThang(Diem(x_gan, y_dai), Diem(x_xa, y_dai), layers.REBAR_STIRRUP.ten))
        # Ký hiệu số hiệu thanh — trỏ từ mép PHẢI cột ra ngoài, xếp chồng dọc
        # theo y nếu có nhiều đường kính trong cùng tổ hợp "đều chu vi".
        #
        # KHÔNG ghi chiều dài (`kh.chieu_dai`, "L=...") ở MẶT ĐỨNG KHUNG TỔNG
        # THỂ — đối chiếu trực tiếp bản vẽ mẫu chính thức
        # (`data/samples/BoTriThep_KhungTruc5_mau.pdf`, panel "BỐ TRÍ THÉP
        # KHUNG TRỤC 5"): mọi ký hiệu trên mặt đứng CHỈ ghi số lượng+đường
        # kính (vd "9 2Ø18") phía trên đường dẫn, chiều dài CHỈ xuất hiện ở
        # bảng thống kê + hình chi tiết phóng to — đúng nguyên tắc mục 2.2
        # "đầy đủ thông số chỉ ghi 1 lần trên cả bản vẽ" (không lặp lại 1
        # thông số đã có ở bảng thống kê). LỖI THẬT đã gặp: ghi "L=..." ở MỌI
        # ký hiệu trên mặt đứng (nơi có tới hàng chục ký hiệu) là nguồn chiếm
        # chỗ/rối mắt lớn nhất — người dùng phản hồi trực tiếp "chú thích thì
        # không logic".
        for i, kh in enumerate(cot.ky_hieu):
            y_kh = y_giua + i * BUOC_XEP_CHONG_KY_HIEU - (len(cot.ky_hieu) - 1) * BUOC_XEP_CHONG_KY_HIEU / 2
            bv.gop(
                ve_ky_hieu_so_hieu(
                    Diem(x1, y_kh), Diem(x1 + 150.0, y_kh), kh.so_hieu, kh.so_luong_duong_kinh,
                    huong_ngang=1,
                )
            )

    for dam in cac_dam:
        y0, y1 = dam.y_truc - dam.h / 2, dam.y_truc + dam.h / 2
        bv.da_giac.append(
            VeDaGiac(
                (Diem(dam.x_trai, y0), Diem(dam.x_phai, y0), Diem(dam.x_phai, y1), Diem(dam.x_trai, y1)),
                layers.OUTLINE.ten,
            )
        )
        if dam.nhan:
            bv.chu.append(
                VeChu(Diem((dam.x_trai + dam.x_phai) / 2, y1 + 60), dam.nhan, chieu_cao=CHIEU_CAO_CHU_NHAN_GON, layer=layers.TEXT.ten, canh_giua=True)
            )
        # Đường thép dọc THẬT (trên + dưới) — cùng lý do/layer như cột ở
        # trên. "goi" (trái/phải) -> thép TRÊN (mô men âm); "giua_nhip" ->
        # thép DƯỚI (mô men dương) — đúng quy ước dầm liên tục đã dùng nhất
        # quán từ pipeline.py (_mo_ta_yeu_cau_ve_mat_cat: o_tren = "goi" in vt.vi_tri).
        COVER_DAM = 30.0
        co_thep_tren = any("goi" in kh.vi_tri_tren_cau_kien for kh in dam.ky_hieu)
        co_thep_duoi = any(kh.vi_tri_tren_cau_kien in ("giua_nhip", "dai_dien") for kh in dam.ky_hieu)
        if co_thep_tren:
            bv.doan_thang.append(VeDoanThang(Diem(dam.x_trai, y1 - COVER_DAM), Diem(dam.x_phai, y1 - COVER_DAM), layers.REBAR_MAIN.ten))
        if co_thep_duoi:
            bv.doan_thang.append(VeDoanThang(Diem(dam.x_trai, y0 + COVER_DAM), Diem(dam.x_phai, y0 + COVER_DAM), layers.REBAR_MAIN.ten))
        # Vạch cốt đai MINH HOẠ — cùng lý do/khoảng cách trực quan như cột ở
        # trên (KHÔNG phải bước đai tính toán thật). Nối trọn chiều cao tiết
        # diện (y0->y1, không chỉ giữa 2 đường thép) vì đai dầm ôm TRỌN tiết
        # diện, không chỉ vùng có thép dọc.
        if co_thep_tren or co_thep_duoi:
            BUOC_DAI_MINH_HOA = 450.0
            nhip_dam = dam.x_phai - dam.x_trai
            so_dai = max(2, round(nhip_dam / BUOC_DAI_MINH_HOA))
            for i in range(so_dai + 1):
                x_dai = dam.x_trai + i * nhip_dam / so_dai
                bv.doan_thang.append(VeDoanThang(Diem(x_dai, y0), Diem(x_dai, y1), layers.REBAR_STIRRUP.ten))
        # Ký hiệu số hiệu thanh — vị trí X theo đúng chỗ thật trên dầm (gối
        # trái ~1/6 nhịp từ trái, giữa nhịp ở giữa, gối phải ~1/6 từ phải;
        # "dai_dien" — dầm công-xôn 1 vị trí duy nhất — đặt giữa), trỏ từ mép
        # TRÊN dầm lên trên. Nhiều ký hiệu CÙNG vị trí xếp chồng dọc theo x.
        #
        # BẬC THANG theo vị trí (TIER_THEO_VI_TRI) — LỖI THẬT đã gặp: với dầm
        # nhịp NGẮN (vd 1500mm), 3 điểm gối_trái/giữa_nhịp/gối_phải chỉ cách
        # nhau nhịp/3 (~500mm hoặc ít hơn) — khoảng cách này NHỎ HƠN bề rộng 1
        # ký hiệu (vòng tròn Ø180mm + chữ "2Ø18" ~240mm), nên 3 nhóm ký hiệu
        # chồng đè lên nhau dù mỗi nhóm tự xếp chồng đúng theo x (xác nhận qua
        # đọc lại PDF xuất thật — các số hiệu dính chùm không đọc được ở dầm
        # ngắn). Xếp mỗi VỊ TRÍ ở 1 ĐỘ CAO đường dẫn riêng (bậc thang tăng dần
        # trái->phải) đảm bảo KHÔNG BAO GIỜ chồng giữa gối_trái/giữa_nhịp/gối
        # phải bất kể nhịp dài hay ngắn, vì khi đó chúng nằm ở 3 dải ngang
        # tách biệt thay vì cùng 1 dải sát mép dầm.
        TIER_THEO_VI_TRI = {"goi_trai": 0, "giua_nhip": 1, "goi_phai": 2, "dai_dien": 1}
        BUOC_BAC_THANG = 380.0
        nhip = dam.x_phai - dam.x_trai
        X_THEO_VI_TRI = {
            "goi_trai": dam.x_trai + nhip / 6, "giua_nhip": (dam.x_trai + dam.x_phai) / 2,
            "goi_phai": dam.x_phai - nhip / 6, "dai_dien": (dam.x_trai + dam.x_phai) / 2,
        }
        dem_theo_vi_tri: dict[str, int] = {}
        nhom_theo_vi_tri: dict[str, int] = {}
        for kh in dam.ky_hieu:
            nhom_theo_vi_tri[kh.vi_tri_tren_cau_kien] = nhom_theo_vi_tri.get(kh.vi_tri_tren_cau_kien, 0) + 1
        for kh in dam.ky_hieu:
            i = dem_theo_vi_tri.get(kh.vi_tri_tren_cau_kien, 0)
            dem_theo_vi_tri[kh.vi_tri_tren_cau_kien] = i + 1
            so_luong_cung_vi_tri = nhom_theo_vi_tri[kh.vi_tri_tren_cau_kien]
            x_goc = X_THEO_VI_TRI.get(kh.vi_tri_tren_cau_kien, (dam.x_trai + dam.x_phai) / 2)
            x_kh = x_goc + i * BUOC_XEP_CHONG_KY_HIEU - (so_luong_cung_vi_tri - 1) * BUOC_XEP_CHONG_KY_HIEU / 2
            bac = TIER_THEO_VI_TRI.get(kh.vi_tri_tren_cau_kien, 0)
            y_ngang = y1 + 150.0 + bac * BUOC_BAC_THANG
            bv.gop(
                ve_ky_hieu_so_hieu(
                    Diem(x_kh, y1), Diem(x_kh, y_ngang), kh.so_hieu, kh.so_luong_duong_kinh,
                    huong_ngang=1,
                )
            )

    return bv


# ---------------------------------------------------------------------------
# Mặt bằng kết cấu sàn — RULES_TCVN5574.md mục 10.7 (checklist "mặt bằng kết
# cấu công trình"), đối chiếu bố cục data/samples/BoTriThep_KhungTruc5_mau.pdf
# (2 mặt bằng: tầng điển hình + tầng mái, lưới trục số 1 chiều/chữ 1 chiều,
# cột ký hiệu tại giao điểm trục, dầm ghi nhãn dọc theo tim dầm). Cùng triết
# lý mặt đứng khung ở trên: toạ độ lưới trục/vị trí cột-dầm là THAM SỐ tường
# minh (chưa tự suy từ BoDuLieuKhung — model Input Adapter hiện chưa lưu
# topology lưới trục, xem hạn chế đã ghi trong docs/BAOCAO_KIEMTHU.md).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ViTriCotMatBang:
    x_truc: float  # mm — toạ độ trục theo phương x
    y_truc: float  # mm — toạ độ trục theo phương y
    b: float  # mm — kích thước tiết diện cột theo phương x
    h: float  # mm — kích thước tiết diện cột theo phương y
    nhan: str = ""  # vd "C1", "C-25x60"


@dataclass(frozen=True)
class DoanDamMatBang:
    x1: float
    y1: float
    x2: float
    y2: float
    nhan: str = ""  # vd "K1", "D-22x40"


def ve_mat_bang_ket_cau(
    ten_mat_bang: str,
    ten_truc_x: list[str],
    x_truc: list[float],
    ten_truc_y: list[str],
    y_truc: list[float],
    cac_cot: list[ViTriCotMatBang],
    cac_dam: list[DoanDamMatBang],
    ban_kinh_dau_truc: float = 150.0,
) -> BanVe:
    """Vẽ 1 mặt bằng kết cấu (tầng điển hình HOẶC tầng mái — gọi hàm này 2
    lần, mỗi lần 1 `ten_mat_bang` khác nhau, đúng bố cục "2 mặt bằng" của bản
    vẽ mẫu). Lưới trục (AXIS, chấm gạch) kèm vòng tròn + số/chữ ở đầu trục
    (đúng quy ước mục 10.7: "trục định vị: số 1 phương, chữ cái 1 phương,
    đặt trong vòng tròn ở đầu trục"). Cột vẽ đúng kích thước tiết diện thật
    tại giao điểm trục; dầm vẽ đường tim kèm nhãn — KHÔNG vẽ 2 nét mép dầm
    ở tỷ lệ mặt bằng (đúng thực hành phổ biến ở tỷ lệ nhỏ 1/100, mục 10.7).
    """
    bv = BanVe(ten=f"MAT_BANG_{ten_mat_bang}")

    x_min, x_max = min(x_truc), max(x_truc)
    y_min, y_max = min(y_truc), max(y_truc)
    le_truc = 300.0  # mm — đoạn trục kéo dài ra ngoài mép mặt bằng trước khi tới vòng tròn đầu trục

    for x, ten in zip(x_truc, ten_truc_x):
        bv.doan_thang.append(VeDoanThang(Diem(x, y_min - le_truc), Diem(x, y_max + le_truc), layers.AXIS.ten))
        tam_dau_truc = Diem(x, y_max + le_truc + ban_kinh_dau_truc)
        bv.vong_tron.append(VeVongTron(tam_dau_truc, ban_kinh_dau_truc, layers.OUTLINE.ten))
        bv.chu.append(VeChu(tam_dau_truc, ten, chieu_cao=ban_kinh_dau_truc, layer=layers.TEXT.ten, canh_giua=True))

    for y, ten in zip(y_truc, ten_truc_y):
        bv.doan_thang.append(VeDoanThang(Diem(x_min - le_truc, y), Diem(x_max + le_truc, y), layers.AXIS.ten))
        tam_dau_truc = Diem(x_min - le_truc - ban_kinh_dau_truc, y)
        bv.vong_tron.append(VeVongTron(tam_dau_truc, ban_kinh_dau_truc, layers.OUTLINE.ten))
        bv.chu.append(VeChu(tam_dau_truc, ten, chieu_cao=ban_kinh_dau_truc, layer=layers.TEXT.ten, canh_giua=True))

    for dam in cac_dam:
        bv.doan_thang.append(VeDoanThang(Diem(dam.x1, dam.y1), Diem(dam.x2, dam.y2), layers.OUTLINE.ten))
        if dam.nhan:
            giua = Diem((dam.x1 + dam.x2) / 2, (dam.y1 + dam.y2) / 2)
            bv.chu.append(VeChu(giua, dam.nhan, chieu_cao=20, layer=layers.TEXT.ten, canh_giua=True))

    for cot in cac_cot:
        x0, x1 = cot.x_truc - cot.b / 2, cot.x_truc + cot.b / 2
        y0, y1 = cot.y_truc - cot.h / 2, cot.y_truc + cot.h / 2
        bv.da_giac.append(VeDaGiac((Diem(x0, y0), Diem(x1, y0), Diem(x1, y1), Diem(x0, y1)), layers.OUTLINE.ten))
        if cot.nhan:
            bv.chu.append(VeChu(Diem(cot.x_truc, y1 + 30), cot.nhan, chieu_cao=15, layer=layers.TEXT.ten, canh_giua=True))

    bv.chu.append(VeChu(Diem((x_min + x_max) / 2, y_min - le_truc - 4 * ban_kinh_dau_truc), ten_mat_bang, chieu_cao=30, layer=layers.TEXT.ten, canh_giua=True))

    return bv


# ---------------------------------------------------------------------------
# Hình chi tiết phối cảnh 3D nút khung — RULES_TCVN5574.md mục 7 (cấu tạo nút
# khung) + mục 10.7 (checklist bản vẽ mẫu: 4 hình phối cảnh). IR (geometry.py)
# vốn chỉ có toạ độ 2D (Diem.x, Diem.y) — "phối cảnh 3D" ở đây dựng bằng PHÉP
# CHIẾU TRỤC ĐO (isometric, góc chuẩn 30°): toạ độ không gian (x,y,z) được
# chiếu về 1 điểm 2D rồi vẽ bằng đúng các primitive đã có (VeDoanThang...),
# không cần thêm backend/loại thực thể 3D nào — đúng cách vẽ kỹ thuật "hình
# chiếu trục đo" vẫn dùng nét 2D thông thường.
#
# ĐÂY LÀ HÌNH MINH HOẠ SƠ ĐỒ (schematic) cấu tạo không gian tại nút — thể
# hiện đúng khối cột/dầm giao nhau, vị trí đại diện của thép dọc/đai, KHÔNG
# vẽ chi tiết uốn móc/neo thật của từng thanh (việc đó thuộc bản vẽ thi công
# chi tiết, ngoài phạm vi 4 hình phối cảnh tổng quan của bản vẽ mẫu).
# ---------------------------------------------------------------------------


def chieu_iso(x: float, y: float, z: float) -> Diem:
    """Chiếu 1 điểm không gian (x,y,z) sang mặt phẳng vẽ 2D bằng phép chiếu
    trục đo góc chuẩn 30°. Quy ước trục: x = phương dọc dầm, y = phương đứng
    (cao độ), z = phương bề rộng/chiều sâu cấu kiện (vuông góc mặt phẳng khung)."""
    goc = math.radians(30)
    return Diem((x - z) * math.cos(goc), (x + z) * math.sin(goc) + y)


def _hop_3d(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, layer: str) -> list[VeDoanThang]:
    """12 cạnh của 1 khối hộp chữ nhật 3D, đã chiếu trục đo — dùng làm khối
    cột/dầm trong hình phối cảnh nút khung."""
    d = {
        (xi, yi, zi): chieu_iso(xi, yi, zi)
        for xi in (x0, x1) for yi in (y0, y1) for zi in (z0, z1)
    }
    canh = []
    for xi in (x0, x1):
        for zi in (z0, z1):
            canh.append(VeDoanThang(d[(xi, y0, zi)], d[(xi, y1, zi)], layer))
    for yi in (y0, y1):
        for zi in (z0, z1):
            canh.append(VeDoanThang(d[(x0, yi, zi)], d[(x1, yi, zi)], layer))
    for xi in (x0, x1):
        for yi in (y0, y1):
            canh.append(VeDoanThang(d[(xi, yi, z0)], d[(xi, yi, z1)], layer))
    return canh


def _vong_dai_ngang_3d(x_tam: float, y_vi_tri: float, rong_x: float, sau_z: float, layer: str) -> list[VeDoanThang]:
    """1 vòng đai hình chữ nhật trong mặt phẳng x-z tại cao độ y_vi_tri —
    minh hoạ đai CỘT (mặt cắt ngang cột nằm NGANG trong không gian phối cảnh)."""
    x0, x1 = x_tam - rong_x / 2, x_tam + rong_x / 2
    z0, z1 = -sau_z / 2, sau_z / 2
    dinh = [chieu_iso(x0, y_vi_tri, z0), chieu_iso(x1, y_vi_tri, z0), chieu_iso(x1, y_vi_tri, z1), chieu_iso(x0, y_vi_tri, z1)]
    return [VeDoanThang(dinh[i], dinh[(i + 1) % 4], layer) for i in range(4)]


def _vong_dai_doc_3d(x_vi_tri: float, y_tam: float, cao_y: float, sau_z: float, layer: str) -> list[VeDoanThang]:
    """1 vòng đai hình chữ nhật trong mặt phẳng y-z tại vị trí x_vi_tri —
    minh hoạ đai DẦM (mặt cắt ngang dầm ĐỨNG, vuông góc trục dầm)."""
    y0, y1 = y_tam - cao_y / 2, y_tam + cao_y / 2
    z0, z1 = -sau_z / 2, sau_z / 2
    dinh = [chieu_iso(x_vi_tri, y0, z0), chieu_iso(x_vi_tri, y0, z1), chieu_iso(x_vi_tri, y1, z1), chieu_iso(x_vi_tri, y1, z0)]
    return [VeDoanThang(dinh[i], dinh[(i + 1) % 4], layer) for i in range(4)]


@dataclass(frozen=True)
class ThongSoChiTietNutKhung:
    nhan: str
    b_cot: float
    h_cot: float
    chieu_dai_cot_duoi: float
    chieu_dai_cot_tren: float
    b_dam: float
    h_dam: float
    chieu_dai_dam: float
    so_dai_minh_hoa_cot: int = 3
    so_dai_minh_hoa_dam: int = 3


def ve_chi_tiet_nut_khung(ts: ThongSoChiTietNutKhung) -> BanVe:
    """Vẽ 1 hình phối cảnh trục đo minh hoạ cấu tạo tại nút khung biên (1 cột
    đứng + 1 dầm framing vào 1 mặt cột theo phương x) — mục 7 (cấu tạo nút
    khung) + mục 10.7 (4 hình phối cảnh trong bản vẽ mẫu). Xem cảnh báo phạm
    vi ở docstring đầu khối mã phía trên: đây là hình SƠ ĐỒ, không phải chi
    tiết uốn móc/neo thật.
    """
    bv = BanVe(ten=f"CHI_TIET_{ts.nhan}")

    # Khối cột: hộp đứng theo y, tiết diện b_cot (x) x h_cot (z), tâm x=z=0.
    bv.doan_thang.extend(
        _hop_3d(-ts.b_cot / 2, ts.b_cot / 2, -ts.chieu_dai_cot_duoi, ts.chieu_dai_cot_tren, -ts.h_cot / 2, ts.h_cot / 2, layers.OUTLINE.ten)
    )
    # Khối dầm: hộp ngang theo x từ mép cột ra, tiết diện b_dam (z) x h_dam (y), tâm y=0.
    x_dau, x_cuoi = ts.b_cot / 2, ts.b_cot / 2 + ts.chieu_dai_dam
    bv.doan_thang.extend(_hop_3d(x_dau, x_cuoi, -ts.h_dam / 2, ts.h_dam / 2, -ts.b_dam / 2, ts.b_dam / 2, layers.OUTLINE.ten))

    # Thép dọc cột — 4 đường minh hoạ tại 4 góc tiết diện (lùi vào ~35% nửa cạnh).
    lui_x, lui_z = ts.b_cot * 0.35, ts.h_cot * 0.35
    for dx in (-lui_x, lui_x):
        for dz in (-lui_z, lui_z):
            bv.doan_thang.append(
                VeDoanThang(chieu_iso(dx, -ts.chieu_dai_cot_duoi, dz), chieu_iso(dx, ts.chieu_dai_cot_tren, dz), layers.REBAR_MAIN.ten)
            )

    # Thép dọc dầm — 4 đường minh hoạ tại 4 góc tiết diện.
    lui_y, lui_zd = ts.h_dam * 0.35, ts.b_dam * 0.35
    for dy in (-lui_y, lui_y):
        for dz in (-lui_zd, lui_zd):
            bv.doan_thang.append(VeDoanThang(chieu_iso(x_dau, dy, dz), chieu_iso(x_cuoi, dy, dz), layers.REBAR_MAIN.ten))

    # Đai cột — vài vòng đại diện dọc chiều cao (không vẽ dày đặc, chỉ minh hoạ vị trí).
    for i in range(ts.so_dai_minh_hoa_cot):
        ty_le = (i + 0.5) / ts.so_dai_minh_hoa_cot
        y_vi_tri = -ts.chieu_dai_cot_duoi + ty_le * (ts.chieu_dai_cot_duoi + ts.chieu_dai_cot_tren)
        bv.doan_thang.extend(_vong_dai_ngang_3d(0, y_vi_tri, ts.b_cot * 0.85, ts.h_cot * 0.85, layers.REBAR_STIRRUP.ten))

    # Đai dầm — vài vòng đại diện dọc chiều dài.
    for i in range(ts.so_dai_minh_hoa_dam):
        ty_le = (i + 0.5) / ts.so_dai_minh_hoa_dam
        x_vi_tri = x_dau + ty_le * ts.chieu_dai_dam
        bv.doan_thang.extend(_vong_dai_doc_3d(x_vi_tri, 0, ts.h_dam * 0.85, ts.b_dam * 0.85, layers.REBAR_STIRRUP.ten))

    bv.chu.append(
        VeChu(chieu_iso(0, ts.chieu_dai_cot_tren + ts.h_cot * 0.6, 0), ts.nhan, chieu_cao=ts.h_cot * 0.3, layer=layers.TEXT.ten, canh_giua=True)
    )

    return bv
