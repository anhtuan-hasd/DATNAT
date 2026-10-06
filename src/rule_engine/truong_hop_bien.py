"""
Bảy nguyên tắc xử lý trường hợp biên — RULES_TCVN5574.md mục 10.6, rút ra từ
ví dụ thực hành "Khung trục 3, trường học" (mục 10) và đưa thẳng vào Rule
Engine như yêu cầu của mục 12 (pseudocode `xu_ly_truong_hop_bien`).

Mỗi hàm ở đây tương ứng với đúng 1 trong 7 nguyên tắc; các nguyên tắc mà số
liệu/ngưỡng cụ thể KHÔNG được tài liệu nêu rõ (vd "gần bằng nhau" là bao
nhiêu %) đòi hỏi lời gọi truyền tường minh ngưỡng đó — module này không tự
đặt ngưỡng mặc định để tránh suy diễn ngoài tài liệu.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from . import cot_dai

# ---------------------------------------------------------------------------
# Nguyên tắc 1 — hai gối liền kề |M| gần bằng nhau → thiết kế chung theo giá
# trị lớn hơn.
# ---------------------------------------------------------------------------


def la_gan_bang_nhau(M1: float, M2: float, ty_le_chenh_lech_toi_da: float) -> bool:
    """So sánh |M1|, |M2| theo tỷ lệ chênh lệch tương đối.

    ty_le_chenh_lech_toi_da PHẢI truyền tường minh (vd 0,10 = 10%) — tài liệu
    (mục 10.6) không cho một ngưỡng % cụ thể để coi là "gần bằng nhau", nên
    không đặt giá trị mặc định ở đây; ngưỡng dùng thực tế phải do người dùng/
    kỹ sư xác nhận trước (đúng tinh thần "vòng lặp xác nhận dữ liệu").
    """
    lon, nho = sorted((abs(M1), abs(M2)), reverse=True)
    if lon == 0:
        return True
    return (lon - nho) / lon <= ty_le_chenh_lech_toi_da


def gia_tri_thiet_ke_chung(M1: float, M2: float) -> float:
    """Giá trị mô men dùng thiết kế chung cho 2 gối liền kề — mục 10.6 nguyên tắc 1."""
    return max(abs(M1), abs(M2))


# ---------------------------------------------------------------------------
# Nguyên tắc 2 — cấu kiện phụ/console M nhỏ hơn nhiều so với cấu kiện chính
# liền kề → dùng thép cấu kiện chính kéo dài qua.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuyetDinhKeoDaiThepChinh:
    dung_thep_cau_kien_chinh: bool
    ghi_chu: str


def xu_ly_cau_kien_phu(
    M_phu: float, M_chinh: float, ty_le_nho_hon_toi_thieu: float
) -> QuyetDinhKeoDaiThepChinh:
    """Quyết định có dùng thép cấu kiện chính kéo dài qua cấu kiện phụ/console
    hay không — mục 10.6 nguyên tắc 2.

    ty_le_nho_hon_toi_thieu: |M_phu|/|M_chinh| phải nhỏ hơn ngưỡng này để coi
    là "nhỏ hơn nhiều" — cũng như nguyên tắc 1, tài liệu không cho số cụ thể
    nên bắt buộc truyền tường minh. Khi áp dụng: chỉ kiểm tra lại h0/khoảng hở
    của cấu kiện phụ với thép đã kéo dài, KHÔNG tính As riêng cho cấu kiện phụ.
    """
    if M_chinh == 0:
        ty_le = float("inf")
    else:
        ty_le = abs(M_phu) / abs(M_chinh)
    if ty_le < ty_le_nho_hon_toi_thieu:
        return QuyetDinhKeoDaiThepChinh(
            True, "Dùng thép cấu kiện chính kéo dài qua; chỉ kiểm tra lại h0/khoảng hở."
        )
    return QuyetDinhKeoDaiThepChinh(False, "M_phu không đủ nhỏ so với M_chinh — tính As riêng bình thường.")


# ---------------------------------------------------------------------------
# Nguyên tắc 3 — cột: luôn thử lệch tâm lớn trước.
# ---------------------------------------------------------------------------


def chon_nhanh_lech_tam(x_thu_lech_tam_lon: float, xiR: float, h0: float) -> str:
    """Trả về "lon" nếu x (từ nhánh lệch tâm lớn) ≤ ξR·h0, ngược lại "be" —
    mục 10.6 nguyên tắc 3 (áp dụng cùng uon_nen.thu_lech_tam_lon)."""
    return "lon" if x_thu_lech_tam_lon <= xiR * h0 else "be"


# ---------------------------------------------------------------------------
# Nguyên tắc 4 — sau khi chọn thép cột, kiểm tra TOÀN BỘ tổ hợp tải trọng
# (không chỉ cặp M,N nguy hiểm nhất) nằm trong khả năng chịu lực.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KetQuaKiemTraToHop:
    chi_so_to_hop: int
    dat: bool
    chi_tiet: object = None


def kiem_tra_toan_bo_to_hop_tai_trong(
    danh_sach_to_hop: Sequence[object],
    ham_kiem_tra_1_to_hop: Callable[[object], bool],
) -> list[KetQuaKiemTraToHop]:
    """Chạy `ham_kiem_tra_1_to_hop` (thường là so Ne với Mu qua uon_nen) cho
    TỪNG tổ hợp tải trọng — mục 10.6 nguyên tắc 4. Trả về danh sách kết quả;
    lớp gọi (verify.py) sẽ coi cấu kiện KHÔNG đạt nếu có bất kỳ tổ hợp nào sai.

    Đây là vòng lặp có điều kiện dừng rõ ràng (hết danh sách tổ hợp), không
    phải dựng biểu đồ tương tác đầy đủ 5 điểm A-E — việc dựng biểu đồ tương
    tác hình học là phần mở rộng chưa triển khai ở Phase 1 (chưa có yêu cầu
    số liệu cụ thể nào trong RULES_TCVN5574.md để kiểm chứng bằng test).
    """
    ket_qua = []
    for i, to_hop in enumerate(danh_sach_to_hop):
        dat = ham_kiem_tra_1_to_hop(to_hop)
        ket_qua.append(KetQuaKiemTraToHop(chi_so_to_hop=i, dat=dat, chi_tiet=to_hop))
    return ket_qua


# ---------------------------------------------------------------------------
# Nguyên tắc 5 — μmin < μ < μmax=3% (uốn) hoặc 2μmin<μt<6% (cột đối xứng).
# Dùng trực tiếp cot_doc.tra_mu_min / canh_bao_vuot_mu_max (không lặp lại ở đây).
# ---------------------------------------------------------------------------

# Nguyên tắc 6 — cốt treo (giật đứt): xem cot_dai.tinh_cot_treo (đã làm tròn lên).

# ---------------------------------------------------------------------------
# Nguyên tắc 7 — bước đai thiết kế = min(s_max chống ép vỡ bụng theo Q,
# s_tt theo tính toán, s_ct cấu tạo theo vị trí đầu/giữa dầm).
# ---------------------------------------------------------------------------


def buoc_dai_thiet_ke_day_du(
    sw_max_theo_kha_nang_chiu_cat: float, s_tt: float, s_ct_cau_tao: float
) -> float:
    """min(sw,max theo mục 3.2, s_tt = Rsw·Asw/qsw, s_ct cấu tạo mục 5.2/5.3) —
    mục 10.6 nguyên tắc 7. Ba giá trị đầu vào tính từ
    `cot_dai.buoc_dai_toi_da_theo_kha_nang_chiu_cat`, `cot_dai.tinh_qsw` (suy
    ngược s_tt), và `cot_dai.buoc_dai_max_dam`/`buoc_dai_max_cot`.
    """
    return min(sw_max_theo_kha_nang_chiu_cat, s_tt, s_ct_cau_tao)
