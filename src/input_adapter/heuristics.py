"""
Heuristic dò schema Excel/CSV không cố định — TONGQUAN_AI_AGENT.md mục 5
bước 2 và mục 3 nguyên tắc 1 ("Tự nhận diện cấu trúc một file Excel không
biết trước — không thể hard-code tên cột").

Chiến lược 2 tầng đúng theo mục 5 TONGQUAN: (1) heuristic từ khoá + so khớp
mờ trước — rẻ, không cần gọi LLM; (2) chỉ khi heuristic không đủ tin cậy mới
rơi xuống llm_mapping.py (LLM). Module này CHỈ làm tầng (1) — không gọi
mạng, không phụ thuộc anthropic, để test được ngay không cần API key.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass


def _tach_token(ten: str) -> list[str]:
    """Tách tên cột thành các "từ" theo ranh giới ký tự không phải chữ/số VÀ
    ranh giới camelCase — vd "As_yc(mm2)" -> ["as","yc","mm2"],
    "AsReq(mm2)" -> ["as","req","mm2"] (nhiều báo cáo kiểu ETABS đặt tên cột
    dạng camelCase không có dấu phân cách). Dùng để so khớp CHÍNH XÁC từng
    token thay vì so khớp con (substring) trên toàn bộ chuỗi đã ghép dính —
    tránh khớp nhầm kiểu keyword "b" khớp bừa vào cột "Beam" (chứa chữ "b"
    nhưng không phải cột bề rộng tiết diện)."""
    ten = unicodedata.normalize("NFD", ten)
    ten = "".join(c for c in ten if unicodedata.category(c) != "Mn")
    ten = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", ten)  # "AsReq" -> "As Req"
    ten = ten.lower()
    return [t for t in re.split(r"[^a-z0-9]+", ten) if t]


def _chuan_hoa_ten(ten: str) -> str:
    """Bỏ dấu tiếng Việt, hạ chữ thường, bỏ ký tự không phải chữ/số — để so
    khớp không phân biệt "Mô men"/"mo_men"/"MoMen"/"M (kNm)"."""
    return "".join(_tach_token(ten))


# Mỗi trường chuẩn (đúng schema mục 5 TONGQUAN) -> danh sách từ khoá tiếng
# Anh/Việt thường gặp trong báo cáo ETABS hoặc bảng tính thủ công. Danh sách
# này không thể đầy đủ tuyệt đối (input không cố định) — phần còn thiếu rơi
# xuống llm_mapping.py.
TU_KHOA_THEO_TRUONG: dict[str, list[str]] = {
    "ten_phan_tu": ["frame", "label", "uniquename", "beam", "column", "phantu", "tenphantu", "caukien", "id"],
    "tang": ["story", "tang", "floor", "level"],
    "truc": ["truc", "axis", "grid", "gridline", "nhip"],
    "loai": ["type", "loai", "designtype", "framedesigntype"],
    "vi_tri": ["station", "loc", "vitri", "position"],
    "b": ["b", "bmm", "berong", "width"],
    "h": ["h", "hmm", "chieucao", "depth"],
    "mac_be_tong": ["macbetong", "concrete", "grade", "capdoben", "matvatlieu", "material"],
    "nhom_thep": ["nhomthep", "rebargrade", "steelgrade", "matcotthep"],
    "combo": ["combo", "case", "tohop", "loadcombo", "outputcase"],
    "M": ["m3", "moment", "momen", "mknm", "m"],
    "N": ["p", "axial", "luocdoc", "luccdoc", "n"],
    "Q": ["v2", "shear", "luccat", "q"],
    "As_yc": ["asreq", "asrqd", "astoparea", "asbotarea", "reqdrebar", "dientichthep", "asyeucau", "as"],
    # Nhiều báo cáo ETABS ghi tiết diện dưới dạng 1 ô ký hiệu (vd "D250x700",
    # "C250x600") thay vì 2 cột b/h riêng — dùng làm nguồn suy ra b,h dự
    # phòng khi không có cột b/h trực tiếp (xem adapter.py: _suy_b_h_tu_ky_hieu).
    "tiet_dien_ky_hieu": ["section", "tietdien", "kyhieu"],
}


@dataclass(frozen=True)
class DeXuatAnhXa:
    truong_chuan: str
    cot_nguon: str
    do_tin_cay: float  # 0..1
    nguon: str = "heuristic"


def _diem_so_khop(ten_cot_chuan_hoa: str, cac_token_cot: list[str], tu_khoa: str) -> float:
    tu_khoa_ch = _chuan_hoa_ten(tu_khoa)
    if not ten_cot_chuan_hoa or not tu_khoa_ch:
        return 0.0

    if ten_cot_chuan_hoa == tu_khoa_ch:
        return 1.0
    if tu_khoa_ch in cac_token_cot:
        # Khớp ĐÚNG 1 token trọn vẹn (vd cột "M(kNm)" tách token ["m","knm"],
        # từ khoá "m" khớp token "m") — tin cậy rất cao, không phụ thuộc độ
        # dài từ khoá vì đây là khớp trọn từ, không phải khớp con lẫn lộn.
        return 0.95

    if len(tu_khoa_ch) <= 2:
        # Từ khoá quá ngắn (vd "b","h","n","m","q","p") CHỈ được chấp nhận
        # khi khớp trọn 1 token (đã kiểm tra ở trên) — không cho khớp con
        # (substring) trên toàn chuỗi đã ghép dính, vì dễ khớp bừa (vd "b"
        # là con của "beam", "n" là con của hầu hết mọi tên cột).
        return 0.0

    if tu_khoa_ch in ten_cot_chuan_hoa:
        # Khớp con với từ khoá đủ dài (>2 ký tự) — vẫn tin cậy khá cao.
        ty_le = len(tu_khoa_ch) / len(ten_cot_chuan_hoa)
        return 0.45 + 0.4 * ty_le

    # So khớp mờ CHỈ dùng làm phương án cuối, ngưỡng nâng lên 0,75 (thay vì
    # 0,6) sau khi phát hiện qua test thực tế: "nhomthep" (Nhóm thép) và
    # "dientichthep" (từ khoá As_yc) từng bị chấm 0,6 — đủ để khớp NHẦM cột
    # "Nhóm thép" vào trường As_yc dù không liên quan.
    diem = difflib.SequenceMatcher(None, ten_cot_chuan_hoa, tu_khoa_ch).ratio()
    return diem if diem >= 0.75 else 0.0


def du_doan_anh_xa_cot(danh_sach_cot_goc: list[str]) -> dict[str, DeXuatAnhXa]:
    """Với mỗi trường chuẩn, chọn cột gốc khớp tốt nhất (nếu có bất kỳ khớp
    nào > 0). Không tự áp đặt ngưỡng "đủ tin cậy" ở đây — trả nguyên độ tin
    cậy để lớp gọi (adapter.py) quyết định trường nào cần hỏi thêm LLM/người
    dùng (đúng tinh thần "không tự quyết định âm thầm khi có sự mơ hồ")."""
    ket_qua: dict[str, DeXuatAnhXa] = {}
    ten_chuan_hoa = {c: _chuan_hoa_ten(c) for c in danh_sach_cot_goc}
    token_theo_cot = {c: _tach_token(c) for c in danh_sach_cot_goc}

    for truong, tu_khoa_list in TU_KHOA_THEO_TRUONG.items():
        tot_nhat: DeXuatAnhXa | None = None
        for cot_goc in danh_sach_cot_goc:
            ten_ch = ten_chuan_hoa[cot_goc]
            token_cot = token_theo_cot[cot_goc]
            for tu_khoa in tu_khoa_list:
                diem = _diem_so_khop(ten_ch, token_cot, tu_khoa)
                if diem > 0 and (tot_nhat is None or diem > tot_nhat.do_tin_cay):
                    tot_nhat = DeXuatAnhXa(truong, cot_goc, diem)
        if tot_nhat is not None:
            ket_qua[truong] = tot_nhat
    return ket_qua


def truong_can_hoi_nguoi_dung(anh_xa: dict[str, DeXuatAnhXa], nguong_tin_cay: float = 0.75) -> list[str]:
    """Trường có độ tin cậy heuristic dưới ngưỡng -> cần xác nhận thêm (qua
    LLM rồi hỏi người dùng, hoặc hỏi người dùng trực tiếp) — đúng "vòng lặp
    xác nhận dữ liệu" TONGQUAN_AI_AGENT.md mục 5."""
    return [t for t, dx in anh_xa.items() if dx.do_tin_cay < nguong_tin_cay]


def truong_bat_buoc_con_thieu(anh_xa: dict[str, DeXuatAnhXa], truong_bat_buoc: list[str]) -> list[str]:
    """Trường bắt buộc hoàn toàn không tìm được cột nào khớp (kể cả tin cậy thấp)."""
    return [t for t in truong_bat_buoc if t not in anh_xa]


def doan_don_vi_luc(ten_cot: str, gia_tri_mau: list[float] | None = None) -> tuple[str, float]:
    """Đoán đơn vị lực/mô men của 1 cột dữ liệu — trả (đơn_vị, độ_tin_cậy).

    đơn_vị trả về: "kN" hoặc "N". Ưu tiên tên cột có ghi rõ đơn vị; nếu
    không, dùng độ lớn số liệu làm GỢI Ý (mục 11 RULES: input ETABS thật
    không cố định đơn vị) — CHỈ là gợi ý xác suất, không phải căn cứ chắc
    chắn; lớp gọi luôn phải coi độ tin cậy < 0.9 là cần xác nhận người dùng.
    """
    ten_ch = ten_cot.lower()
    if "kn" in ten_ch:
        return "kN", 0.9
    if re.search(r"(?<![a-z])n(?![a-z])", ten_ch):
        return "N", 0.9

    if not gia_tri_mau:
        return "kN", 0.3  # mặc định theo xác nhận của người dùng dự án — độ tin cậy thấp vì chỉ là mặc định

    gia_tri_sap_xep = sorted(abs(v) for v in gia_tri_mau)
    trung_vi = gia_tri_sap_xep[len(gia_tri_sap_xep) // 2]
    # Mô men/lực tính bằng N, N·mm thường có bậc độ lớn 1e3-1e9; tính bằng
    # kN, kN·m thường ở bậc 1e-1-1e4 — ngưỡng 10.000 chỉ là gợi ý thực hành.
    if trung_vi > 10_000:
        return "N", 0.5
    return "kN", 0.5
