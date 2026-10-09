"""Lắp ráp TỜ VẼ BỐ TRÍ THÉP KHUNG (mặt đứng + mặt cắt + bảng thống kê + ghi chú + khung tên) theo bố cục của bản vẽ
mẫu `data/samples/BoTriThep_KhungTruc5_mau.pdf`, từ dữ liệu đã qua Input Adapter + Rule Engine.

Thuần Python (xuất biểu diễn trung gian `geometry.BanVe`), không phụ thuộc AutoCAD/LLM — test được không cần CAD.

Quy ước toạ độ: mô hình theo mm THẬT của MẶT ĐỨNG, tờ A1 in tỷ lệ 1:`ty_le` (mặc định 1:50) ⇒ tờ giấy 841×594 mm
tương ứng 42 050 × 29 700 mm trong model. Mặt cắt vẽ PHÓNG `he_so_mat_cat` lần so với mặt đứng (mặc định ×5, tương
đương 1:10). Chữ có chiều cao GIẤY cố định (nhân `ty_le`), không đổi theo tỷ lệ hình.

Các quy tắc hình học rút từ bản vẽ mẫu (đã đối chiếu từng vùng):
- Mặt trên MỌI dầm bằng cốt sàn (dầm cao/thấp đều treo xuống) — dầm không đối xứng qua cốt sàn.
- Thép trên chạy liền qua nút và uốn móc xuống cột ở đầu biên; thép gia cường gối cắt ở L/4 thông thuỷ.
- Cốt đai theo vùng (gối/giữa nhịp; hai đầu/giữa cột) lấy từ `rule_engine.bo_tri_dai`.
- Cột đi xuống móng (thép chờ bẻ L), có COS đỉnh móng / tôn nền / tự nhiên; số hiệu thanh dùng chung toàn tờ.
Các số CHƯA có trong dữ liệu (móng, bề dày sàn, COS) lấy từ `CauHinhToVe` (mặc định theo bản mẫu) và được ghi chú
rõ trên tờ vẽ là giả định — KHÔNG phải kết quả tính toán.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .. import geometry as g
from .. import layers
from ..geometry import BanVe, Diem, VeChu, VeCung, VeDaGiac, VeDoanThang, VeKichThuoc, VeVongTron

# ---------------------------------------------------------------------------
# Cấu hình
# ---------------------------------------------------------------------------


@dataclass
class CauHinhToVe:
    ty_le: float = 50.0  # in 1:ty_le
    he_so_mat_cat: float = 5.0  # phóng mặt cắt so với mặt đứng (5 ⇒ 1:10)
    chu_giay_mm: float = 3.0  # chiều cao chữ trên giấy
    chu_nho_giay_mm: float = 2.5
    rong_to_giay_mm: float = 841.0  # A1
    cao_to_giay_mm: float = 594.0
    ten_khung_truc: str = ""  # tên trục khung (vd "5") — ghi trên mặt cắt/mặt đứng
    # --- Giả định (CHƯA có trong dữ liệu ETABS) — mặc định theo bản mẫu, ghi chú trên tờ vẽ ---
    day_san: float = 100.0
    cao_do_ton_nen_tren_dinh_mong: float = 1000.0  # COS ±0.000 cao hơn đỉnh móng (Mong) bao nhiêu
    cao_do_tu_nhien_duoi_ton_nen: float = 450.0
    day_dai_mong: float = 450.0
    day_lot: float = 100.0
    rong_dai_them_moi_ben: float = 400.0  # đài rộng hơn cột mỗi bên
    lop_bao_ve_dam: float = 25.0
    lop_bao_ve_cot: float = 25.0
    canh_ban_cua_t: float = 150.0  # cánh sàn mỗi bên trên mặt cắt chữ T
    chieu_dai_nen_noi_mac_dinh: float = 45.0  # hệ số × d khi không có L_lap từ tool [thực hành]
    thong_tin_khung_ten: dict = field(default_factory=dict)
    ghi_chu_vat_lieu: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Kết quả
# ---------------------------------------------------------------------------


@dataclass
class KetQuaToVe:
    ban_ve: BanVe
    thong_ke: list[g.DongThongKe]
    so_cot: int
    so_dam: int
    so_ky_hieu_ky_vong: int  # số vòng tròn số hiệu (layer SO_HIEU) kỳ vọng — gồm cả vòng tròn trong mặt cắt
    mat_cat: list[dict]  # [{"nhan","loai","b","h","rong_ve","cao_ve"}]: kích thước TRÊN BẢN VẼ (đã nhân hệ số)
    he_so_mat_cat: float
    canh_bao: list[str]
    kho_giay: str = "A1"
    so_da_giac_outline: int = 0


# ---------------------------------------------------------------------------
# Tiện ích vẽ
# ---------------------------------------------------------------------------

_MAU_TEN_TANG = {}


def _ten_tang(ten: str) -> str:
    """'Tang3' → 'TẦNG 3'; 'TangMai' → 'TẦNG MÁI'; 'Mong' → 'MÓNG'."""
    if ten.lower().startswith("tangmai"):
        return "TẦNG MÁI"
    if ten.lower().startswith("tang"):
        return "TẦNG " + ten[4:]
    if ten.lower().startswith("mong"):
        return "MÓNG"
    return ten.upper()


class _Ve:
    """Bộ gom đối tượng vẽ + hàm tiện ích theo kích cỡ chữ GIẤY."""

    def __init__(self, cfg: CauHinhToVe, ten: str = "HINH"):
        self.cfg = cfg
        self.bv = BanVe(ten=ten)
        s = cfg.ty_le
        self.h_chu = cfg.chu_giay_mm * s
        self.h_chu_nho = cfg.chu_nho_giay_mm * s
        self.r_the = 3.2 * s  # bán kính vòng tròn số hiệu (giấy 3,2 mm)

    # --- nguyên thuỷ ---
    def doan(self, x1, y1, x2, y2, layer):
        self.bv.doan_thang.append(VeDoanThang(Diem(x1, y1), Diem(x2, y2), layer))

    def duong(self, pts, layer, dong=False, rong=0.0):
        self.bv.da_giac.append(VeDaGiac(tuple(Diem(x, y) for x, y in pts), layer, dong, rong))

    def hcn(self, x0, y0, x1, y1, layer, rong=0.0):
        self.duong([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, True, rong)

    def tron(self, x, y, r, layer):
        self.bv.vong_tron.append(VeVongTron(Diem(x, y), r, layer))

    def cung(self, x, y, r, a0, a1, layer):
        self.bv.cung.append(VeCung(Diem(x, y), r, a0, a1, layer))

    def chu(self, x, y, noi_dung, cao=None, layer=layers.TEXT.ten, giua=False, phai=False):
        self.bv.chu.append(VeChu(Diem(x, y), noi_dung, cao or self.h_chu, layer, giua, phai))

    def kt(self, p1, p2, nhan, layer=layers.DIM.ten, co=None):
        self.bv.kich_thuoc.append(VeKichThuoc(Diem(*p1), Diem(*p2), 0.0, layer, nhan, co or self.h_chu_nho))

    # --- ký hiệu ---
    def the_so_hieu(self, x_tro, y_tro, x_the, y_the, so_hieu, noi_dung, huong=1):
        """Đường dẫn từ (x_tro,y_tro) tới vòng tròn số hiệu tại (x_the,y_the); chữ `noi_dung` ở cạnh vòng tròn,
        mọc ra phía `huong` (+1 phải, −1 trái). Dạng bản mẫu: ⓝ Ø6a150."""
        r = self.r_the
        self.doan(x_tro, y_tro, x_the, y_the, layers.SO_HIEU.ten)
        self.tron(x_the, y_the, r, layers.SO_HIEU.ten)
        self.chu(x_the, y_the, str(so_hieu), self.h_chu, layers.SO_HIEU.ten, giua=True)
        if noi_dung:
            if huong >= 0:
                self.chu(x_the + r + 0.5 * self.h_chu_nho, y_the, noi_dung, self.h_chu)
            else:
                self.chu(x_the - r - 0.5 * self.h_chu_nho, y_the, noi_dung, self.h_chu, phai=True)

    def doan_net_dam(self, x, y0, y1, rong):
        """Vạch đậm đứng (ký hiệu mặt cắt trên mặt đứng): polyline có độ rộng hình học."""
        self.duong([(x, y0), (x, y1)], layers.REBAR_MAIN.ten, False, rong)

    def tam_giac_cao_do(self, x, y, layer=layers.AXIS.ten):
        k = 1.6 * self.cfg.ty_le
        self.bv.da_giac.append(VeDaGiac((Diem(x, y), Diem(x - k * 0.5, y + k * 0.8), Diem(x + k * 0.5, y + k * 0.8)), layer, True))

    def bong_bong_truc(self, x, y, ten):
        r = 4.0 * self.cfg.ty_le
        self.tron(x, y, r, layers.AXIS.ten)
        self.chu(x, y, ten, self.h_chu * 1.3, layers.AXIS.ten, giua=True)


# ---------------------------------------------------------------------------
# Dữ liệu
# ---------------------------------------------------------------------------


def _doi_mo_ta_thep(vi_tri: dict) -> list[int]:
    """Danh sách đường kính từng thanh của 1 vị trí: [{duong_kinh,so_luong}] → [18,18,16]."""
    ds: list[int] = []
    for th in vi_tri.get("thanh", []) or []:
        ds.extend([int(th["duong_kinh"])] * int(th["so_luong"]))
    return sorted(ds, reverse=True)


@dataclass
class _Cot:
    ten: str
    truc: str
    y0: float
    y1: float
    b: float  # bề rộng vuông góc mặt phẳng khung
    h: float  # bề rộng TRONG mặt phẳng khung — hiển thị trên mặt đứng
    d: int
    n_b: int  # số thanh trên cạnh song song b
    n_h: int
    n_tong: int
    l_lap: float
    tang: str
    raw: dict
    so_hieu_thep: int = 0
    vung: list = field(default_factory=list)
    nhan_dai: list = field(default_factory=list)  # số hiệu đai theo vùng


@dataclass
class _Dam:
    ten: str
    x1: float
    x2: float
    y: float  # cao độ MẶT TRÊN dầm = cốt sàn
    b: float
    h: float
    tang: str
    truc1: str
    truc2: str
    top_l: list[int]
    top_r: list[int]
    bot: list[int]
    raw: dict
    l_tt: float = 0.0  # thông thuỷ
    hc1: float = 0.0
    hc2: float = 0.0
    vung: list = field(default_factory=list)


def _doc_cot(p: dict, truc: dict[str, float], moc: dict[str, float]) -> _Cot | None:
    t = p.get("tang") or ""
    ten_moc = t.split("_")
    if p.get("truc") not in truc or len(ten_moc) != 2 or ten_moc[0] not in moc or ten_moc[1] not in moc:
        return None
    y0, y1 = sorted((moc[ten_moc[0]], moc[ten_moc[1]]))
    vt = (p.get("vi_tri") or [{}])[0]
    td = vt.get("thep_doc") or {}
    n_tong = int(td.get("tong_so_thanh") or sum(th.get("so_luong", 0) for th in vt.get("thanh", [])) or 4)
    d = int(td.get("duong_kinh") or (vt.get("thanh") or [{"duong_kinh": 16}])[0]["duong_kinh"])
    n_b = int(td.get("so_thanh_canh_b") or 2)
    n_h = int(td.get("so_thanh_canh_h") or 2)
    neo = vt.get("neo_noi") or {}
    return _Cot(p["ten"], p["truc"], y0, y1, float(p["b"]), float(p["h"]), d, n_b, n_h, n_tong,
                float(neo.get("L_lap") or 0.0), t, p)


def _doc_dam(p: dict, truc: dict[str, float], moc: dict[str, float]) -> _Dam | None:
    hai = (p.get("truc") or "").split("-")
    if len(hai) != 2 or hai[0] not in truc or hai[1] not in truc or p.get("tang") not in moc:
        return None
    x1, x2 = sorted((truc[hai[0]], truc[hai[1]]))
    sets: dict[str, list[int]] = {}
    for v in p.get("vi_tri", []):
        sets[v["vi_tri"]] = _doi_mo_ta_thep(v)
    bot = sets.get("giua_nhip") or sets.get("dai_dien") or []
    top_l = sets.get("goi_trai") or sets.get("ngam") or []
    top_r = sets.get("goi_phai") or sets.get("ngam") or []
    return _Dam(p["ten"], x1, x2, moc[p["tang"]], float(p["b"]), float(p["h"]), p["tang"], hai[0], hai[1],
                top_l, top_r, bot, p)


# ---------------------------------------------------------------------------
# Lược đồ thanh dọc dầm (theo skill 06 B2–B8; số hiệu cấp qua SoDangKySoHieu)
# ---------------------------------------------------------------------------


@dataclass
class _ThanhDocVe:
    vai_tro: str  # "tren_suot" | "tren_cat_trai" | "tren_cat_phai" | "tren_cat_nut" | "duoi"
    duong_kinh: int
    so_luong: int
    chieu_dai: float
    so_hieu: int = 0


def _tru_da_tap(ds: list[int], d: int, n: int) -> list[int]:
    ds = list(ds)
    for _ in range(n):
        if d in ds:
            ds.remove(d)
    return ds


def _dem_theo_d(ds: list[int]) -> dict[int, int]:
    r: dict[int, int] = defaultdict(int)
    for d in ds:
        r[d] += 1
    return dict(sorted(r.items(), reverse=True))
