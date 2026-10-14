"""Gom nhóm thép giữa các phần tử/vị trí — luật R53 (cột) và R54 (dầm) của skill Rule Engine.

Rút ra từ số liệu thuyết minh Khung Trục 5 (Bảng 26–27) và nhãn thép trên bản vẽ mẫu — KHÔNG phải điều khoản TCVN,
kiểm trên một công trình (xem `docs/agents/huongdanchonthep/02_DAM_16_BUOC.md` Bước 8d, `03_COT_14_BUOC.md` Bước 9d):

  * R53 — cột CÙNG tầng, CÙNG tiết diện, CÙNG vật liệu lấy chung bố trí thép của cột bất lợi nhất (lớn nhất theo As thực mỗi
    phía). Thuyết minh KT5: tầng 3, cột A cần 382,13 mm² (2Ø16 = 402 đủ) vẫn lấy 2Ø18 vì cột B cùng tầng cần 503,59.
  * R54 — thép trên dầm chạy suốt nhịp ⇒ hai gối cùng bố trí theo gối lớn hơn. Dầm 45: gối phải cần 388,69 mm² (2Ø16 đủ)
    vẫn lấy 2Ø18 như gối trái (439,35). Thép dưới (giữa nhịp) giữ riêng.

Chỉ NÂNG thép (không bao giờ hạ dưới As yêu cầu của chính phần tử/vị trí): bố trí được chọn lại bằng bố trí của phần tử/vị trí
bất lợi hơn, nên As thực chỉ tăng. Hàm thuần Python, tất định, không LLM/AutoCAD; việc áp dụng lên dữ liệu pipeline nằm ở
`src/orchestrator/gom_nhom_khung.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

DUNG_SAI_AS = 1e-6  # mm² — hai As coi là bằng nhau


@dataclass(frozen=True)
class MucGom:
    """Một phần tử (cột) hoặc một vị trí (gối dầm) tham gia gom nhóm."""

    ten: str
    nhom: tuple  # khoá nhóm: các mục cùng khoá được gom với nhau
    as_thuc: float  # mm² — As thực đã chọn (mỗi phía với cột; cả mặt thép trên với gối dầm)
    mo_ta: str = ""


@dataclass(frozen=True)
class NangCap:
    """Một lần nâng thép: `ten` được đổi sang bố trí của `nguon`."""

    quy_tac: str  # "R53" | "R54"
    ten: str
    nguon: str
    as_truoc: float
    as_sau: float
    mo_ta_truoc: str
    mo_ta_sau: str


def khoa_nhom_cot(ten: str, tang: str | None, b: float, h: float, mac_be_tong: str, nhom_thep_doc: str) -> tuple:
    """Khoá nhóm cột: cùng tầng + cùng tiết diện (b×h) + cùng vật liệu. Thiếu `tang` ⇒ không biết cột nào cùng tầng nên
    KHÔNG gom (khoá riêng theo tên cột)."""
    if not tang:
        return ("khong_gom", ten)
    return (tang, round(float(b), 1), round(float(h), 1), mac_be_tong, nhom_thep_doc)


def tim_nang_cap(cac_muc: list[MucGom], quy_tac: str) -> list[NangCap]:
    """Trong mỗi nhóm (≥2 mục), mục có As thực lớn nhất là chuẩn; mọi mục có As nhỏ hơn được nâng theo chuẩn.

    Hai mục bằng As nhưng khác bố trí không bị đổi (không có cơ sở để chọn bên nào). Nhiều mục cùng As lớn nhất ⇒ lấy
    mục đứng trước (thứ tự đầu vào) làm chuẩn — kết quả tất định."""
    theo_nhom: dict[tuple, list[MucGom]] = {}
    for m in cac_muc:
        theo_nhom.setdefault(m.nhom, []).append(m)
    ket_qua: list[NangCap] = []
    for nhom in theo_nhom.values():
        if len(nhom) < 2:
            continue
        chuan = max(nhom, key=lambda m: m.as_thuc)  # max giữ phần tử đầu tiên khi bằng nhau
        for m in nhom:
            if m.as_thuc < chuan.as_thuc - DUNG_SAI_AS:
                ket_qua.append(NangCap(quy_tac, m.ten, chuan.ten, m.as_thuc, chuan.as_thuc, m.mo_ta, chuan.mo_ta))
    return ket_qua
