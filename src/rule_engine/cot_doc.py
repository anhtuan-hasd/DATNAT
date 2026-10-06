"""
Điều kiện & lựa chọn cốt thép dọc — RULES_TCVN5574.md mục 4 (TCVN 5574:2018
mục 10.3.3, 5.4.1-5.4.2).

Ghi chú quan trọng về `chon_to_hop_thep_doc`: RULES_TCVN5574.md không cho một
quy tắc ưu tiên DUY NHẤT khi nhiều tổ hợp đường kính×số thanh đều hợp lệ (bản
thân tài liệu mục 4.1 ghi rõ μ_max "là ngưỡng cảnh báo thực hành... không phải
trị số tuyệt đối duy nhất"). Quy tắc ưu tiên dùng ở đây (ít thừa diện tích nhất
→ ít loại đường kính nhất → ít lớp nhất) là quy tắc xác định (deterministic),
không ngẫu nhiên — nhưng vì lựa chọn thép của kỹ sư thật (trong ví dụ mục 10)
còn chịu ảnh hưởng bởi các yếu tố thi công không định lượng được trong tài
liệu (thói quen, tính liên tục giữa các nhịp...), tổ hợp mà hàm này chọn có
thể KHÔNG trùng 100% với tổ hợp trong ví dụ sách — điều bắt buộc kiểm tra là
As_thực ≥ As_yêu_cầu và mọi ràng buộc cấu tạo, không phải trùng khớp tuyệt đối
số thanh với sách.

LỖI THẬT đã gặp (đối chiếu trực tiếp thuyết minh gốc inputvanban2.pdf, Bảng
26/27): chỉ tối ưu "ít thừa diện tích nhất" khiến hệ thống dùng Ø12-Ø22 rải
rác, có dầm 4 loại đường kính, và chọn 2Ø22 thay 3Ø18 chỉ vì thừa ít hơn vài
mm². Đã THỬ ép dùng chung 1 đường kính toàn công trình -> SAI (dầm cần 57mm²
bị gán 2Ø22=760mm²), đã gỡ. Quy tắc đúng là theo YÊU CẦU CẤU TẠO của từng vị
trí: (1) ưu tiên Ø >= 16 (cột cạnh > 200mm mục 54.1, dầm chính mục 53.1), (2)
ưu tiên cùng 1 đường kính trong 1 vị trí, (3) khi thừa diện tích tương đương
(<= 5% As_target) chọn đường kính NHỎ hơn, (4) mỗi phần tử không quá 3 loại
đường kính (mục 16.1). Kiểm chứng offline trên 12 cột + 16 vị trí dầm của
thuyết minh gốc: khớp tuyệt đối 25/28 (trước 6/28), 28/28 đủ As.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import vat_lieu

MU_MAX_PHAN_TRAM = 3.0  # mục 4.1 — ngưỡng cảnh báo thực hành cho cấu kiện chịu uốn (dầm).
# mục 4.1 — cột đặt đối xứng (As=A's, mô hình 2 mặt b), mỗi phía ≤ 3% (tổng
# ≤ 6%), chuẩn hoá theo As_thuc_moi_phia/(b·h0).
#
# CẦN ĐỐI CHIẾU LẠI (chưa sửa — xem docs/agents/huongdanchonthep/
# RULE_BASE_CHON_THEP_KHUNG_BTCT.md mục 54.2): tài liệu rule base mới (trích
# trực tiếp điều khoản GỐC TCVN 5574:2018 mục 6.2.1) ghi μmax=4% cho As,tot
# (TỔNG mọi thanh dọc quanh chu vi, chuẩn hoá theo A=b·h GỘP, không phải
# As_thuc_moi_phia/h0 như hằng số này) — 8% tại vùng nối chồng. CHƯA đổi
# trực tiếp hằng số này thành 4.0 vì đó là 2 chuẩn hoá KHÁC NHAU (mỗi mặt
# b/h0 vs tổng chu vi/A gộp, gồm cả thanh cấu tạo 2 cạnh h mà mô hình 2 mặt
# đối xứng ở đây bỏ qua) — quy đổi trực tiếp 3%→4% là SAI nếu không quy đổi
# đúng cơ sở chuẩn hoá trước. Cần phân tích kỹ (hoặc đổi hẳn verify.py sang
# kiểm tra As,tot/A thay vì As_thuc_moi_phia/h0) trước khi sửa số này — tránh
# lặp lại lớp lỗi "sửa ẩu rồi phải revert" đã gặp với bug chia đôi As cột.
MU_MAX_COT_MOI_PHIA_PHAN_TRAM = 3.0

# CHANGE_REQUESTS.md mục 6 — ràng buộc đường kính thép dọc TỐI THIỂU thực tế
# thi công. RULES_TCVN5574.md mục 5.4.2 chỉ nêu rõ khoảng "φ12–φ40" cho THÉP
# CỘT; tài liệu không nói tường minh cho dầm, nhưng thực hành cấu tạo phổ
# biến (và chính hàm lượng μ_min mục 4.1 đã ngầm định 1 tiết diện đủ lớn) coi
# φ<12mm là bất thường cho cấu kiện chịu lực chính — ĐÂY LÀ RÀNG BUỘC ĐỒ ÁN TỰ
# THÊM (cùng tinh thần với MU_MAX_PHAN_TRAM ở trên: "ngưỡng cảnh báo thực
# hành", không phải trị số TCVN tuyệt đối), áp dụng CHUNG cho cả dầm và cột
# để nhất quán 1 quy tắc duy nhất, dễ kiểm chứng.
#
# Root cause đã xác nhận (không còn nghi vấn — xem lịch sử ở CHANGE_REQUESTS
# mục 6): sinh_va_loc_to_hop/chon_to_hop_thep_chu_vi_cot TRƯỚC ĐÂY vét cạn vô
# điều kiện mọi giá trị trong duong_kinh_cho_phep do người gọi truyền, kể cả
# khi Rule Engine Agent tự "nới đường kính cho phép" xuống 8/10mm lúc tự sửa
# lỗi (đúng hướng dẫn trong docs/agents/RULE_ENGINE_AGENT.md bước 5 — "nới
# đường kính cho phép" là gợi ý hợp lý, nhưng không có giới hạn dưới sẽ tạo
# ra cấu hình phi thực tế như 3Ø8/2Ø10). Lọc ngay tại nguồn (2 hàm sinh tổ
# hợp bên dưới) thay vì chỉ cảnh báo sau khi đã chọn xong.
DUONG_KINH_DOC_TOI_THIEU_MM = 12.0

_KHOANG_HO_TOI_THIEU_DUOI_1_2_LOP = 25.0  # mm, mục 4.4.
_KHOANG_HO_TOI_THIEU_TREN = 30.0  # mm, mục 4.4.
_KHOANG_HO_TOI_THIEU_TU_LOP_3 = 50.0  # mm, mục 4.4.


# ---------------------------------------------------------------------------
# 4.1 — Hàm lượng tối thiểu / tối đa
# ---------------------------------------------------------------------------


def tra_mu_min(
    do_manh: float,
    theo_L0_i: bool = False,
    bo_tri_deu_chu_vi_hoac_keo_dung_tam: bool = False,
) -> float:
    """μ_min (%) theo độ mảnh — mục 4.1.

    do_manh: L0/h (mặc định, tiết diện chữ nhật) hoặc L0/i nếu theo_L0_i=True.
    Ngưỡng chữ nhật: ≤5 → 0,10%; ≥25 → 0,25%; giữa → nội suy tuyến tính.
    Ngưỡng L0/i: ≤17 → 0,10%; ≥87 → 0,25%; giữa → nội suy tuyến tính.
    bo_tri_deu_chu_vi_hoac_keo_dung_tam=True: nhân đôi kết quả.
    """
    if theo_L0_i:
        nguong_min, nguong_max = 17.0, 87.0
    else:
        nguong_min, nguong_max = 5.0, 25.0

    if do_manh <= nguong_min:
        mu = 0.10
    elif do_manh >= nguong_max:
        mu = 0.25
    else:
        mu = 0.10 + (0.25 - 0.10) * (do_manh - nguong_min) / (nguong_max - nguong_min)

    return mu * 2 if bo_tri_deu_chu_vi_hoac_keo_dung_tam else mu


def canh_bao_vuot_mu_max(As: float, b: float, h0: float, mu_max: float = MU_MAX_PHAN_TRAM) -> bool:
    """True nếu hàm lượng As/(b·h0) vượt mu_max (%) — cảnh báo thực hành, mục 4.1."""
    mu = 100 * As / (b * h0)
    return mu > mu_max


# ---------------------------------------------------------------------------
# 4.4 — Khoảng cách giữa các thanh thép dọc & số thanh tối đa 1 lớp
# ---------------------------------------------------------------------------


def so_thanh_toi_da_1_lop(
    b: float,
    cover: float,
    duong_kinh_dai: float,
    duong_kinh_doc: float,
    la_lop_duoi: bool = True,
    la_lop_thu_3_tro_len: bool = False,
) -> int:
    """Số thanh dọc tối đa xếp được trong 1 lớp theo bề rộng b — mục 4.4.

    Khoảng hở thông thủy tối thiểu giữa 2 thanh cùng lớp: 25mm (lớp dưới,
    1-2 lớp) / 30mm (lớp trên) / 50mm (từ lớp 3), và không nhỏ hơn đường kính
    thanh. Bề rộng khả dụng = b − 2·cover − 2·d_đai.
    """
    if la_lop_thu_3_tro_len:
        khoang_ho_toi_thieu = _KHOANG_HO_TOI_THIEU_TU_LOP_3
    elif la_lop_duoi:
        khoang_ho_toi_thieu = _KHOANG_HO_TOI_THIEU_DUOI_1_2_LOP
    else:
        khoang_ho_toi_thieu = _KHOANG_HO_TOI_THIEU_TREN
    khoang_ho = max(khoang_ho_toi_thieu, duong_kinh_doc)

    be_rong_kha_dung = b - 2 * cover - 2 * duong_kinh_dai
    if be_rong_kha_dung < duong_kinh_doc:
        return 0
    # n thanh chiếm n*d + (n-1)*khoang_ho <= be_rong_kha_dung
    n = math.floor((be_rong_kha_dung + khoang_ho) / (duong_kinh_doc + khoang_ho))
    return max(n, 0)


def khoang_cach_toi_da_giua_thanh(h: float, la_cot: bool = False, theo_phuong_uon: bool = False) -> float:
    """Khoảng cách tối đa giữa các thanh — mục 4.4.

    Dầm/bản: h≤150 → 200mm; h>150 → min(1,5h; 400mm).
    Cột: 400mm (vuông góc mặt uốn) / 500mm (theo mặt uốn).
    """
    if la_cot:
        return 500.0 if theo_phuong_uon else 400.0
    return 200.0 if h <= 150 else min(1.5 * h, 400.0)


# ---------------------------------------------------------------------------
# Chọn tổ hợp thép dọc — vét cạn có điều kiện dừng rõ ràng (KHÔNG ngẫu nhiên)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToHopThep:
    thanh: tuple[tuple[int, int], ...]  # ((duong_kinh, so_luong), ...) đã sort giảm dần đường kính
    As_thuc: float  # mm²
    so_loai_duong_kinh: int
    so_lop: int

    def mo_ta(self) -> str:
        return "+".join(f"{n}Ø{d}" for d, n in self.thanh)


def _As_cua_to_hop(thanh: tuple[tuple[int, int], ...]) -> float:
    return sum(vat_lieu.dien_tich_1_thanh(d) * n for d, n in thanh)


def _chenh_lech_duong_kinh_hop_le(danh_sach_d: list[int]) -> bool:
    """Không quá 3 loại đường kính/dầm; không chênh lệch đúng 1mm; trong cùng
    miền chịu lực không chênh quá 6mm giữa loại lớn nhất và nhỏ nhất. Mục 4.2."""
    if len(danh_sach_d) > 3:
        return False
    if len(danh_sach_d) < 2:
        return True
    for i, d1 in enumerate(danh_sach_d):
        for d2 in danh_sach_d[i + 1 :]:
            if abs(d1 - d2) == 1:
                return False
    if max(danh_sach_d) - min(danh_sach_d) > 6:
        return False
    return True


def _so_lop_can(so_thanh: int, so_thanh_toi_da_1_lop: int) -> int:
    if so_thanh_toi_da_1_lop <= 0:
        return 999  # không xếp được — loại ứng viên này ở bước lọc
    return math.ceil(so_thanh / so_thanh_toi_da_1_lop)


def sinh_va_loc_to_hop(
    As_target: float,
    duong_kinh_cho_phep: list[int],
    b: float,
    cover: float,
    duong_kinh_dai_du_kien: float = 8.0,
    so_thanh_toi_thieu: int = 2,
    so_thanh_toi_da_1_loai: int = 10,
    so_loai_duong_kinh_toi_da: int = 2,
) -> list[ToHopThep]:
    """Vét cạn tổ hợp 1 hoặc 2 loại đường kính thoả As_thực ≥ As_target.

    Vòng lặp có điều kiện dừng rõ ràng: số thanh mỗi loại chạy từ
    so_thanh_toi_thieu đến so_thanh_toi_da_1_loai (hữu hạn, không tìm kiếm mù/
    không ngẫu nhiên) — KHÔNG dùng giải thuật di truyền hay metaheuristic nào.
    Trả về danh sách ứng viên đã lọc qua điều kiện khoảng cách (mục 4.4) và số
    loại đường kính/chênh lệch đường kính (mục 4.2); chưa sắp xếp ưu tiên.
    """
    ung_vien: list[ToHopThep] = []

    # Lọc bỏ NGAY từ đầu mọi đường kính < DUONG_KINH_DOC_TOI_THIEU_MM (xem
    # ghi chú hằng số ở đầu module) — không sinh ra ứng viên có đường kính phi
    # thực tế dù người gọi (Rule Engine Agent lúc tự sửa lỗi) có nới
    # duong_kinh_cho_phep xuống thấp tới đâu. Không lọc lại sau khi đã sinh
    # (lọc ở nguồn rẻ hơn và không thể lọt sót).
    duong_kinh_cho_phep = [d for d in duong_kinh_cho_phep if d >= DUONG_KINH_DOC_TOI_THIEU_MM]

    # --- 1 loại đường kính ---
    for d in duong_kinh_cho_phep:
        as1 = vat_lieu.dien_tich_1_thanh(d)
        for n in range(so_thanh_toi_thieu, so_thanh_toi_da_1_loai + 1):
            As_thuc = as1 * n
            if As_thuc < As_target:
                continue
            n_max_1_lop = so_thanh_toi_da_1_lop(b, cover, duong_kinh_dai_du_kien, d)
            so_lop = _so_lop_can(n, n_max_1_lop)
            if so_lop >= 999:
                continue
            ung_vien.append(ToHopThep(thanh=((d, n),), As_thuc=As_thuc, so_loai_duong_kinh=1, so_lop=so_lop))
            break  # đủ số thanh nhỏ nhất cho đường kính này là đủ, không cần n lớn hơn

    if so_loai_duong_kinh_toi_da < 2:
        return ung_vien

    # --- 2 loại đường kính ---
    for i, d1 in enumerate(duong_kinh_cho_phep):
        as1 = vat_lieu.dien_tich_1_thanh(d1)
        for d2 in duong_kinh_cho_phep[i + 1 :]:
            if not _chenh_lech_duong_kinh_hop_le([d1, d2]):
                continue
            as2 = vat_lieu.dien_tich_1_thanh(d2)
            tim_thay_cho_cap_nay = False
            for n1 in range(1, so_thanh_toi_da_1_loai + 1):
                if tim_thay_cho_cap_nay:
                    break
                for n2 in range(1, so_thanh_toi_da_1_loai + 1):
                    As_thuc = as1 * n1 + as2 * n2
                    if As_thuc < As_target:
                        continue
                    n_max_1_lop_d1 = so_thanh_toi_da_1_lop(b, cover, duong_kinh_dai_du_kien, d1)
                    so_lop = _so_lop_can(n1 + n2, n_max_1_lop_d1)
                    if so_lop >= 999:
                        continue
                    ung_vien.append(
                        ToHopThep(
                            thanh=((d1, n1), (d2, n2)),
                            As_thuc=As_thuc,
                            so_loai_duong_kinh=2,
                            so_lop=so_lop,
                        )
                    )
                    tim_thay_cho_cap_nay = True
                    break

    return ung_vien


# Yêu cầu cấu tạo về đường kính (RULE_BASE_CHON_THEP_KHUNG_BTCT.md): cột cạnh
# tiết diện > 200mm "nên chọn Ø ≥ 16" (mục 54.1); dầm chính "nên chọn Ø > 16"
# (mục 53.1; thuyết minh gốc Khung Trục 5 dùng Ø16 làm nhỏ nhất cho cả dầm lẫn
# cột). Là "nên", không phải "bắt buộc" -> dùng làm TẦNG ƯU TIÊN, chỉ hạ xuống
# Ø12-14 khi không có tổ hợp khả thi nào với Ø >= 16.
DUONG_KINH_DOC_NEN_TOI_THIEU_MM = 16
# Hai tổ hợp có diện tích thừa chênh nhau không quá tỷ lệ này (so với As_target)
# coi là "tương đương về tiết kiệm thép" -> chọn theo yêu cầu cấu tạo: ít loại
# đường kính hơn, rồi đường kính NHỎ hơn (L_an, L_lap tỷ lệ theo d, dễ uốn,
# khống chế vết nứt tốt hơn — mục 11.5, 11.6). Ví dụ As=752mm²: 2Ø22 (760) và
# 3Ø18 (763) tương đương -> chọn 3Ø18 như thuyết minh gốc, không chọn 2Ø22 chỉ
# vì thừa ít hơn 3mm².
DUNG_SAI_THUA_TUONG_DUONG = 0.05
DUNG_SAI_UU_TIEN_CUNG_DUONG_KINH = 0.15


def _chon_theo_yeu_cau_cau_tao(ung_vien, As_target, thua, so_loai, d_max, phu):
    """Trong các ứng viên có thừa diện tích <= thừa_min + 5%·As_target (tương
    đương), chọn: ít loại đường kính nhất -> đường kính lớn nhất nhỏ nhất ->
    ít thừa nhất -> `phu` (khoá phụ: số lớp / tổng số thanh)."""
    thua_min = min(thua(u) for u in ung_vien)
    # Trong 1 vị trí ưu tiên thép CÙNG đường kính (dễ thi công, tránh nhầm lẫn —
    # mục 16.1) khi phương án như vậy chỉ thừa hơn phương án trộn <= 15% As_target.
    it_loai_nhat = min(so_loai(u) for u in ung_vien)
    cung_loai = [u for u in ung_vien if so_loai(u) == it_loai_nhat]
    if min(thua(u) for u in cung_loai) <= thua_min + DUNG_SAI_UU_TIEN_CUNG_DUONG_KINH * As_target:
        ung_vien = cung_loai
    nguong = min(thua(u) for u in ung_vien) + DUNG_SAI_THUA_TUONG_DUONG * As_target
    nhom = [u for u in ung_vien if thua(u) <= nguong]
    return min(nhom, key=lambda u: (so_loai(u), d_max(u), thua(u), phu(u)))


def _cac_tang_duong_kinh(duong_kinh_cho_phep: list[int], duong_kinh_uu_tien: list[int] | None) -> list[list[int]]:
    """Thứ tự thử: (0) tập ưu tiên của chính phần tử (nếu có), (1) Ø >= 16 theo
    yêu cầu cấu tạo, (2) toàn bộ — dừng ở tầng đầu tiên có tổ hợp khả thi."""
    tang: list[list[int]] = []
    if duong_kinh_uu_tien:
        giao = sorted(set(duong_kinh_cho_phep) & set(duong_kinh_uu_tien))
        if giao:
            tang.append(giao)
    nen = [d for d in duong_kinh_cho_phep if d >= DUONG_KINH_DOC_NEN_TOI_THIEU_MM]
    if nen:
        tang.append(nen)
    tang.append(list(duong_kinh_cho_phep))
    return tang


def chon_to_hop_thep_doc(
    As_target: float,
    duong_kinh_cho_phep: list[int],
    b: float,
    cover: float,
    duong_kinh_dai_du_kien: float = 8.0,
    so_thanh_toi_thieu: int = 2,
    duong_kinh_uu_tien: list[int] | None = None,
) -> ToHopThep:
    """Chọn tổ hợp thép dọc tốt nhất theo quy tắc ưu tiên xác định:
    (1) ít thừa diện tích nhất → (2) ít loại đường kính nhất → (3) ít lớp nhất.

    Xem ghi chú đầu module: đây là quy tắc do đồ án tự đặt (được nêu rõ trong
    yêu cầu triển khai), không phải một trị số bắt buộc duy nhất của TCVN.

    `duong_kinh_uu_tien`: nếu có (khác rỗng), THỬ TRƯỚC với giao của tập này
    và `duong_kinh_cho_phep` — chỉ mở rộng ra toàn bộ `duong_kinh_cho_phep`
    (tìm "tối ưu tuyệt đối") khi KHÔNG tổ hợp nào khả thi trong tập ưu tiên.
    Mục đích: ưu tiên TÁI DÙNG đường kính đã dùng ở phần tử khác trong cùng
    công trình thay vì luôn tối ưu độc lập từng lần gọi — xem LỖI THẬT ở đầu
    module.
    """
    for tang in _cac_tang_duong_kinh(duong_kinh_cho_phep, duong_kinh_uu_tien):
        ung_vien = sinh_va_loc_to_hop(As_target, tang, b, cover, duong_kinh_dai_du_kien, so_thanh_toi_thieu)
        if ung_vien:
            return _chon_theo_yeu_cau_cau_tao(
                ung_vien, As_target,
                thua=lambda t: t.As_thuc - As_target, so_loai=lambda t: t.so_loai_duong_kinh,
                d_max=lambda t: max(d for d, _n in t.thanh), phu=lambda t: t.so_lop,
            )
    raise ValueError(
        f"Không tìm được tổ hợp thép hợp lệ cho As_target={As_target}mm² với "
        f"b={b}mm, cover={cover}mm và bộ đường kính {duong_kinh_cho_phep} — "
        "cần tăng tiết diện, mở rộng bộ đường kính, hoặc tăng số lớp cho phép."
    )


# ---------------------------------------------------------------------------
# Chọn tổ hợp thép dọc CHO CỘT — bố trí đều chu vi (mục 4.2: "Cột: bố trí đối
# xứng theo chu vi"). KHÔNG dùng chon_to_hop_thep_doc ở trên cho cột: hàm đó
# xếp thanh thành 1 hàng ngang rồi chia LỚP chồng lên nhau (đúng cho dầm, có
# 1 vùng chịu kéo + 1 vùng chịu nén), còn cột cần thanh chạy dọc theo CẢ 4
# CẠNH tiết diện, không phải xếp lớp — phát hiện qua chạy thật Phase 4: dùng
# nhầm chon_to_hop_thep_doc cho cột ra "9Ø14 xếp 3 lớp" (đúng công thức dầm)
# nhưng khi vẽ theo chu vi (geometry.ve_mat_cat_cot) chỉ dựng được 8 điểm cho
# cấu hình 3 thanh/cạnh — lệch giữa As đã chọn và hình học thực vẽ.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ToHopThepChuViCot:
    duong_kinh: int
    so_thanh_canh_b: int  # số thanh trên MỖI cạnh song song trục b (kể cả 2 góc)
    so_thanh_canh_h: int  # số thanh trên MỖI cạnh song song trục h (kể cả 2 góc)
    tong_so_thanh: int  # đã trừ 4 thanh góc dùng chung, không đếm 2 lần
    As_thuc_moi_phia: float  # mm² — diện tích 1 cạnh chịu lực chính (As = A's dùng ở mục 2.5)
    As_thuc_tong: float  # mm² — tổng toàn bộ thanh quanh chu vi

    def mo_ta(self) -> str:
        return f"{self.tong_so_thanh}Ø{self.duong_kinh} (đều chu vi, {self.so_thanh_canh_b}/cạnh b, {self.so_thanh_canh_h}/cạnh h)"


def so_thanh_toi_thieu_theo_khoang_cach_cot(
    chieu_dai_canh: float, cover: float, duong_kinh_dai: float, duong_kinh_doc: float, theo_phuong_uon: bool = False
) -> int:
    """Số thanh tối thiểu trên 1 cạnh để khoảng cách giữa 2 thanh liền kề
    không vượt quá khoảng cách tối đa cho cột (mục 4.4, qua khoang_cach_toi_da_giua_thanh)."""
    khoang_cach_toi_da = khoang_cach_toi_da_giua_thanh(0, la_cot=True, theo_phuong_uon=theo_phuong_uon)
    chieu_dai_kha_dung = chieu_dai_canh - 2 * cover - 2 * duong_kinh_dai - duong_kinh_doc
    if chieu_dai_kha_dung <= 0:
        return 2
    so_khoang = math.ceil(chieu_dai_kha_dung / khoang_cach_toi_da)
    return max(2, so_khoang + 1)


def _sinh_ung_vien_chu_vi_cot(
    As_target_moi_phia: float, b: float, h: float, cover: float, duong_kinh_cho_phep: list[int],
    duong_kinh_dai_du_kien: float,
) -> list[ToHopThepChuViCot]:
    """Sinh mọi ứng viên hợp lệ cho 1 bộ `duong_kinh_cho_phep` — tách khỏi
    `chon_to_hop_thep_chu_vi_cot` để hàm đó có thể gọi lại 2 lần (ưu tiên rồi
    fallback) mà không lặp logic."""
    ung_vien: list[ToHopThepChuViCot] = []
    for d in sorted(duong_kinh_cho_phep):
        as1 = vat_lieu.dien_tich_1_thanh(d)
        so_thanh_toi_thieu_b = so_thanh_toi_thieu_theo_khoang_cach_cot(b, cover, duong_kinh_dai_du_kien, d)
        so_thanh_toi_thieu_h = so_thanh_toi_thieu_theo_khoang_cach_cot(h, cover, duong_kinh_dai_du_kien, d)
        so_thanh_can_theo_As = max(2, math.ceil(As_target_moi_phia / as1))
        so_thanh_canh_b = max(so_thanh_can_theo_As, so_thanh_toi_thieu_b)
        so_thanh_canh_h = max(2, so_thanh_toi_thieu_h)

        # Kiểm tra khả thi vật lý: số thanh cần có thực sự xếp vừa trong bề
        # rộng b không (dùng lại so_thanh_toi_da_1_lop, mục 4.4) — thiếu bước
        # này sẽ không bao giờ raise ValueError khi As_target quá lớn so với
        # tiết diện, vì math.ceil() không tự biết giới hạn vật lý.
        so_thanh_toi_da_kha_thi = so_thanh_toi_da_1_lop(b, cover, duong_kinh_dai_du_kien, d)
        if so_thanh_canh_b > so_thanh_toi_da_kha_thi:
            continue

        As_thuc_moi_phia = so_thanh_canh_b * as1
        if As_thuc_moi_phia < As_target_moi_phia:
            continue

        tong_so_thanh = 2 * so_thanh_canh_b + 2 * (so_thanh_canh_h - 2)
        As_thuc_tong = tong_so_thanh * as1
        ung_vien.append(ToHopThepChuViCot(d, so_thanh_canh_b, so_thanh_canh_h, tong_so_thanh, As_thuc_moi_phia, As_thuc_tong))
    return ung_vien


def chon_to_hop_thep_chu_vi_cot(
    As_target_moi_phia: float,
    b: float,
    h: float,
    cover: float,
    duong_kinh_cho_phep: list[int],
    duong_kinh_dai_du_kien: float = 8.0,
    duong_kinh_uu_tien: list[int] | None = None,
) -> ToHopThepChuViCot:
    """Chọn đường kính + số thanh/cạnh cho cột đối xứng, bố trí đều chu vi —
    mục 4.2, dùng CHUNG 1 đường kính (giữ đơn giản, đúng thực hành phổ biến
    "cột đặt đối xứng, mỗi phía As=A's" của mục 2.5/10.4). Vét cạn theo đường
    kính cho phép (vòng lặp có điều kiện dừng rõ ràng, không ngẫu nhiên):
    với mỗi d, số thanh/cạnh b lấy max(đủ As_target_moi_phia, đủ khoảng cách
    mục 4.4); số thanh/cạnh h chỉ cần đủ khoảng cách (2 cạnh này là "cạnh
    bên", không phải mặt chịu lực chính trong mô hình As=A's 2 mặt).

    `duong_kinh_uu_tien`: xem docstring `chon_to_hop_thep_doc` — cùng cơ chế:
    thử trước với giao của tập ưu tiên, chỉ mở rộng ra toàn bộ
    `duong_kinh_cho_phep` khi không có ứng viên nào khả thi.
    """
    # Cùng ràng buộc đường kính tối thiểu áp dụng cho dầm ở sinh_va_loc_to_hop
    # — xem ghi chú DUONG_KINH_DOC_TOI_THIEU_MM đầu module (CHANGE_REQUESTS
    # mục 6): lọc ngay tại nguồn, không sinh ứng viên đường kính phi thực tế.
    duong_kinh_cho_phep = [d for d in duong_kinh_cho_phep if d >= DUONG_KINH_DOC_TOI_THIEU_MM]

    for tang in _cac_tang_duong_kinh(duong_kinh_cho_phep, duong_kinh_uu_tien):
        ung_vien = _sinh_ung_vien_chu_vi_cot(As_target_moi_phia, b, h, cover, tang, duong_kinh_dai_du_kien)
        if ung_vien:
            return _chon_theo_yeu_cau_cau_tao(
                ung_vien, As_target_moi_phia,
                thua=lambda t: t.As_thuc_moi_phia - As_target_moi_phia, so_loai=lambda t: 1,
                d_max=lambda t: t.duong_kinh, phu=lambda t: t.tong_so_thanh,
            )
    raise ValueError(
        f"Không tìm được tổ hợp thép chu vi hợp lệ cho As_target_moi_phia={As_target_moi_phia}mm² "
        f"với b={b}mm, h={h}mm, cover={cover}mm và bộ đường kính {duong_kinh_cho_phep}."
    )
