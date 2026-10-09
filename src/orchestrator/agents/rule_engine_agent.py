"""Rule Engine Agent — 1 trong 4 agent LLM riêng biệt (CHANGE_REQUESTS.md
mục 1). Xem đầy đủ vai trò, quy trình, hợp đồng dữ liệu tại
`docs/agents/RULE_ENGINE_AGENT.md`. Cấu trúc file theo đúng khuôn chung mô tả
ở đầu `input_adapter_agent.py` (state riêng, 1 hàm/tool, đăng ký, system
prompt + hàm chạy).

LLM KHÔNG BAO GIỜ tính số — mọi con số trong kết quả trả về đều đến từ
`src/rule_engine/`; agent chỉ đọc kết quả và quyết định gọi tool nào tiếp
theo (`docs/TONGQUAN_AI_AGENT.md` mục 3). Toàn bộ các "chặn ở tầng code" (x/e
tự tính lại, mu_max cố định, A=b*h tự tính...) GIỮ NGUYÊN không đổi so với
`tools.py` cũ — đây là kết quả của nhiều lỗi thật đã gặp và sửa, xem chi tiết
từng lỗi trong `docs/agents/RULE_ENGINE_AGENT.md` mục "Lỗi thật đã từng gặp".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ...rule_engine import cot_dai, cot_doc, neo_noi, verify
from .. import agent
from ..loops import BoDemVongLap
from ..shared import doc_skill
from ..shared.hoi_nguoi_dung_tool import DINH_NGHIA_HOI_NGUOI_DUNG, hoi_nguoi_dung
from ..shared.hop_dong_du_lieu import KetQuaViTriDaThietKe, PhuongAnThepPhanTu

HamHoiNguoiDung = Callable[[str, list[str] | None], str]


@dataclass
class NguCanhRuleEngine:
    """State riêng cho 1 lượt chạy Rule Engine Agent — ĐÚNG 1 PHẦN TỬ (dầm
    hoặc cột), lặp qua từng vị trí của phần tử đó trong CÙNG 1 phiên hội
    thoại. `bo_dem` (BoDemVongLap) RIÊNG cho phần tử này — không chia sẻ giữa
    các phần tử khác nhau (CHANGE_REQUESTS.md mục 1: "1 instance RIÊNG cho
    mỗi agent có vòng lặp nội bộ").

    `khong_co_Q`: True khi TOÀN BỘ vị trí của phần tử này KHÔNG có lực cắt Q
    thô — xảy ra khi dữ liệu đến từ báo cáo ETABS thật qua `etabs_reader.py`
    (bảng "Concrete Design Summary" cho dầm chỉ xuất VRebar đã thiết kế sẵn,
    KHÔNG xuất raw force, xem docstring `etabs_reader.doc_etabs_thuc`). Ban
    đầu cờ này CHỈ tồn tại ở tầng webapp cũ (`webapp/jobs.py::
    _chay_1_yeu_cau_co_log`, tự bọc dispatch để chặn) — chuyển hẳn vào đây
    để CẢ webapp lẫn `scripts/chay_pipeline_day_du.py` (CLI) đều được bảo vệ
    như nhau, không chỉ webapp. Lý do PHẢI chặn ở tầng code, không chỉ DẶN
    LLM qua mô tả yêu cầu: đã xác nhận qua chạy thật — LLM có thể tuân thủ
    đúng ở vị trí này nhưng bỏ qua hướng dẫn ở vị trí khác trong CÙNG 1 phiên
    hội thoại."""

    hoi_nguoi_dung: HamHoiNguoiDung
    bo_dem: BoDemVongLap
    khong_co_Q: bool = False
    # Đường kính đã dùng trong CHÍNH phần tử này (mọi vị trí của nó) — phục vụ
    # yêu cầu cấu tạo mục 16.1 "không quá 3 loại đường kính cho cốt chịu lực
    # trong mỗi dầm". KHÔNG chia sẻ giữa các phần tử: mỗi vị trí phải chọn thép
    # theo yêu cầu riêng của nó (As, cấu tạo), không bị ép dùng chung một loại
    # toàn công trình (đã thử và sai: dầm cần 57mm² bị gán 2Ø22 = 760mm²).
    duong_kinh_da_dung: set[int] = field(default_factory=set)


def _loi(thong_diep: str) -> dict[str, Any]:
    return {"loi": thong_diep}


# ---------------------------------------------------------------------------
# Tra bảng vật liệu — BẮT BUỘC gọi trước chon_thep_doc/tinh_cot_dai để lấy
# Rb/Rbt/Rs/Rsc/Rsw thật, KHÔNG để LLM tự đoán/nhớ.
# ---------------------------------------------------------------------------


def tra_vat_lieu(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    from ...rule_engine import vat_lieu

    ket_qua: dict[str, Any] = {}
    if dau_vao.get("mac_be_tong"):
        try:
            bt = vat_lieu.lay_be_tong(dau_vao["mac_be_tong"])
            ket_qua["be_tong"] = {"Rb": bt.Rb, "Rbt": bt.Rbt, "Eb": bt.Eb}
        except ValueError as e:
            return _loi(str(e))
    if dau_vao.get("nhom_thep_doc"):
        try:
            th = vat_lieu.lay_thep(dau_vao["nhom_thep_doc"])
            ket_qua["thep_doc"] = {"Rs": th.Rs, "Rsc": th.Rsc, "Es": th.Es}
        except ValueError as e:
            return _loi(str(e))
    if dau_vao.get("nhom_thep_dai"):
        try:
            th = vat_lieu.lay_thep(dau_vao["nhom_thep_dai"])
            ket_qua["thep_dai"] = {"Rsw": th.Rsw}
        except ValueError as e:
            return _loi(str(e))
    if not ket_qua:
        return _loi("Cần ít nhất 1 trong: mac_be_tong, nhom_thep_doc, nhom_thep_dai.")
    return ket_qua


# ---------------------------------------------------------------------------
# Nén lệch tâm CHO CỘT — dùng chung nội bộ bởi tinh_lech_tam_cot (tham khảo)
# VÀ tu_kiem_tra (bắt buộc) — xem docstring tu_kiem_tra để rõ lý do tách hàm
# nội bộ này thay vì để LLM tự truyền x/e.
# ---------------------------------------------------------------------------


def _tinh_lech_tam_cot_noi_bo(
    N: float, M: float, b: float, h: float, a_prime: float, Rb: float, Rs: float, Rsc: float,
    As_gia_dinh: float, Es: float = 2.0e5, L: float | None = None,
) -> dict:
    from ...rule_engine import truong_hop_bien, uon_nen

    h0 = h - a_prime
    xiR = uon_nen.tinh_xiR(Rs, Es)
    ea = uon_nen.tinh_ea(L, h) if L else max(h / 30, 10.0)
    e1 = M * 1000 / N
    e0 = uon_nen.tinh_e0(e1, ea, sieu_tinh=True)
    eta = 1.0  # chưa đủ dữ liệu (Is, ML, ML1...) để tính chính xác hệ số uốn dọc mục 2.6 — chỉ an toàn khi cột không mảnh
    e = uon_nen.tinh_e(e0, eta, h0, a_prime)

    x_lon = uon_nen.thu_lech_tam_lon(N, Rs, As_gia_dinh, Rsc, As_gia_dinh, Rb, b)
    nhanh = truong_hop_bien.chon_nhanh_lech_tam(x_lon, xiR, h0)
    x = uon_nen.thu_lech_tam_be(N, Rs, As_gia_dinh, Rsc, As_gia_dinh, Rb, b, h0, xiR) if nhanh == "be" else x_lon

    Mu = uon_nen.tinh_Mu_cot(Rb, b, x, h0, Rsc, As_gia_dinh, a_prime)
    Ne = N * e / 1000

    return {
        "xiR": xiR, "ea": ea, "e0": e0, "eta": eta,
        "eta_ghi_chu": "Mặc định η=1 (bỏ qua uốn dọc) — thiếu dữ liệu Is/ML/ML1 để tính chính xác mục 2.6; chỉ dùng an toàn khi cột không mảnh.",
        "e": e, "nhanh_lech_tam": nhanh, "x": x, "Mu": Mu, "Ne": Ne,
        "dat_dieu_kien": Ne <= Mu * 1.02,
    }


def tinh_lech_tam_cot(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    """Tool THAM KHẢO — cho LLM XEM trước các giá trị trung gian để giải
    thích/báo cáo. KHÔNG BẮT BUỘC gọi — tu_kiem_tra tự gọi lại đúng hàm này
    NỘI BỘ, không nhận x/e từ LLM."""
    N, M = dau_vao["N"], dau_vao["M"]
    if N <= 0:
        return _loi("Hàm này chỉ áp dụng khi N > 0 (nén lệch tâm) — mục 2.5. N=0/kéo nằm ngoài phạm vi.")
    return _tinh_lech_tam_cot_noi_bo(
        N=N, M=M, b=dau_vao["b"], h=dau_vao["h"], a_prime=dau_vao.get("a_prime", 40.0),
        Rb=dau_vao["Rb"], Rs=dau_vao["Rs"], Rsc=dau_vao["Rsc"],
        As_gia_dinh=dau_vao["As_gia_dinh"], Es=dau_vao.get("Es", 2.0e5), L=dau_vao.get("L"),
    )


# ---------------------------------------------------------------------------
# Chọn thép dọc + cấu tạo đai/neo/nối.
# ---------------------------------------------------------------------------


SO_LOAI_DUONG_KINH_TOI_DA_MOI_PHAN_TU = 3  # mục 16.1


def _duong_kinh_bat_buoc_dung_lai(nc: NguCanhRuleEngine) -> list[int] | None:
    """Phần tử đã dùng đủ 3 loại đường kính -> các vị trí còn lại ưu tiên chỉ
    trong 3 loại đó (chỉ mở rộng nếu không khả thi, xem _cac_tang_duong_kinh)."""
    if len(nc.duong_kinh_da_dung) >= SO_LOAI_DUONG_KINH_TOI_DA_MOI_PHAN_TU:
        return sorted(nc.duong_kinh_da_dung)
    return None


def chon_thep_doc(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    loai = dau_vao.get("loai", "dam")
    duong_kinh_cho_phep = dau_vao.get("duong_kinh_cho_phep", [12, 14, 16, 18, 20, 22, 25])
    duong_kinh_dai_du_kien = dau_vao.get("duong_kinh_dai_du_kien", 8.0)

    if loai == "cot":
        if "h" not in dau_vao:
            return _loi("loai='cot' cần thêm tham số 'h' (chiều cao tiết diện) để bố trí đều chu vi.")
        # As_target ở đây là As MỖI PHÍA (As=A's, mục 2.5/10.4) — TRUYỀN
        # THẲNG As_yc của Input Adapter, KHÔNG chia đôi.
        #
        # ĐÃ THỬ chia đôi (coi As_yc là tổng, theo quy ước CSI PMMArea=tổng
        # tiết diện) rồi REVERT NGAY sau khi phát hiện qua chạy thật: tự kiểm
        # tra (tu_kiem_tra) bắt đầu báo hàng loạt cột KHÔNG ĐẠT (N·e > Mu) mà
        # trước đó vẫn đạt — dấu hiệu As bị thiếu, không phải thừa. Xác nhận
        # độc lập bằng chính công thức TCVN 5574 mục 2.5 (đã cài ở uon_nen.
        # thiet_ke_cot_doi_xung_lech_tam_be, không liên quan gì đến As_yc từ
        # ETABS): với đúng N,M,b,h,vật liệu của phần tử '14' (N=483.24kN,
        # M=91.41kNm, 220x300mm, B25/CB500-V), công thức cho As MỖI PHÍA =
        # 630.2mm² và phần tử '1' (N=546.43kN, M=87.02kNm) cho 623.8mm² —
        # CẢ HAI đều XẤP XỈ (thấp hơn ~15-20%, hợp lý vì SP 63-13330-2012 mà
        # ETABS dùng có hệ số an toàn khác TCVN) giá trị As_yc GỐC (752.76mm²
        # và 743.19mm²) — KHÔNG PHẢI xấp xỉ 1 nửa As_yc (376/372mm², sai lệch
        # ~40%, đúng khoảng thiếu hụt gây tu_kiem_tra hỏng hàng loạt). Kết
        # luận: As_yc (PMMArea) tuy đặt tên "tổng" theo quy ước CSI, nhưng vì
        # thuyết minh gốc dùng SP 63-13330-2012 (kết cấu As=A's tương tự TCVN
        # mục 2.5) nên trị số này XẤP XỈ ĐÚNG As MỖI PHÍA theo TCVN, không
        # phải tổng 2 phía cộng lại — dùng trực tiếp là đúng, không chia đôi.
        try:
            to_hop_cot = cot_doc.chon_to_hop_thep_chu_vi_cot(
                As_target_moi_phia=dau_vao["As_target"], b=dau_vao["b"], h=dau_vao["h"],
                cover=dau_vao.get("cover", 40.0), duong_kinh_cho_phep=duong_kinh_cho_phep,
                duong_kinh_dai_du_kien=duong_kinh_dai_du_kien,
                duong_kinh_uu_tien=_duong_kinh_bat_buoc_dung_lai(nc),
            )
        except ValueError as e:
            return _loi(str(e))
        nc.duong_kinh_da_dung.add(to_hop_cot.duong_kinh)
        return {
            "duong_kinh": to_hop_cot.duong_kinh,
            "so_thanh_canh_b": to_hop_cot.so_thanh_canh_b, "so_thanh_canh_h": to_hop_cot.so_thanh_canh_h,
            "tong_so_thanh": to_hop_cot.tong_so_thanh,
            "As_thuc_moi_phia": to_hop_cot.As_thuc_moi_phia, "As_thuc_tong": to_hop_cot.As_thuc_tong,
            "mo_ta": to_hop_cot.mo_ta(),
        }

    try:
        to_hop = cot_doc.chon_to_hop_thep_doc(
            As_target=dau_vao["As_target"], duong_kinh_cho_phep=duong_kinh_cho_phep, b=dau_vao["b"],
            cover=dau_vao.get("cover", 25.0), duong_kinh_dai_du_kien=duong_kinh_dai_du_kien,
            duong_kinh_uu_tien=_duong_kinh_bat_buoc_dung_lai(nc),
        )
    except ValueError as e:
        return _loi(str(e))
    nc.duong_kinh_da_dung.update(d for d, _n in to_hop.thanh)
    return {
        "thanh": [{"duong_kinh": d, "so_luong": n} for d, n in to_hop.thanh],
        "As_thuc": to_hop.As_thuc, "so_loai_duong_kinh": to_hop.so_loai_duong_kinh, "so_lop": to_hop.so_lop,
        "mo_ta": to_hop.mo_ta(),
    }


def tinh_cot_dai(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    """Với cột có N: diện tích tiết diện 'A' LUÔN được tool TỰ TÍNH = b*h nội
    bộ khi có 'h' — KHÔNG dùng giá trị 'A' do LLM tự nhân/tự đặt."""
    if nc.khong_co_Q:
        return _loi(
            "Không có Q thô cho phần tử này (nguồn ETABS design summary chỉ xuất kết quả đã thiết kế, "
            "không xuất raw force) — tool tinh_cot_dai BỊ CHẶN, KHÔNG được gọi. Đề xuất Ø8 bước cấu tạo "
            "hợp lý (150mm gần gối/nút, 200-250mm giữa nhịp) mà không kiểm tra lại bằng Q."
        )
    Q, Rb, Rbt, b, h0, Rsw = dau_vao["Q"], dau_vao["Rb"], dau_vao["Rbt"], dau_vao["b"], dau_vao["h0"], dau_vao["Rsw"]
    N = dau_vao.get("N")
    h_day_du = dau_vao.get("h")
    A = b * h_day_du if h_day_du else dau_vao.get("A")

    phi_n = 1.0
    if N is not None and A:
        try:
            phi_n = cot_dai.tinh_phi_n_nen(N, A, Rb) if N >= 0 else cot_dai.tinh_phi_n_keo(-N, A, Rbt)
        except ValueError as e:
            return _loi(str(e))

    dat_ep_vo_bung, Q_gioi_han = cot_dai.kiem_tra_ep_vo_bung(Q, Rb, b, h0, phi_n)
    Qb1 = cot_dai.tinh_Qb1(Rbt, b, h0, phi_n)
    can_tinh_toan = Q > Qb1

    ket_qua: dict[str, Any] = {
        "phi_n": phi_n, "dat_dieu_kien_ep_vo_bung": dat_ep_vo_bung, "Q_gioi_han_ep_vo_bung": Q_gioi_han,
        "Qb1": Qb1, "can_dat_dai_theo_tinh_toan": can_tinh_toan,
    }
    if not dat_ep_vo_bung:
        ket_qua["canh_bao"] = "Q vượt điều kiện chống ép vỡ bụng — PHẢI tăng b/h/cấp bê tông, không chỉ tăng cốt đai (mục 3.1)."
        return ket_qua

    Asw = dau_vao.get("Asw")
    if Asw:
        qsw = cot_dai.tinh_qsw(Rsw, Asw, dau_vao.get("sw_thu", 150.0))
        Qsw1 = cot_dai.tinh_Qsw1(qsw, h0)
        ket_qua["qsw"] = qsw
        ket_qua["dat_dieu_kien_co_ban"] = cot_dai.dieu_kien_co_ban_chiu_cat(Q, Qb1, Qsw1)
        if can_tinh_toan:
            ket_qua["buoc_dai_toi_da_theo_kha_nang_chiu_cat"] = cot_dai.buoc_dai_toi_da_theo_kha_nang_chiu_cat(Rbt, b, h0, Q)

    d_doc_min = dau_vao.get("d_doc_min")
    loai = dau_vao.get("loai", "dam")
    if loai == "cot" and d_doc_min:
        ket_qua["buoc_dai_max_cau_tao"] = cot_dai.buoc_dai_max_cot(d_doc_min, dau_vao.get("dieu_kien_dac_biet", False))
    elif d_doc_min or dau_vao.get("h0"):
        ket_qua["buoc_dai_max_cau_tao"] = cot_dai.buoc_dai_max_dam(h0, can_tinh_toan)

    return ket_qua


def tinh_neo_noi(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    from ...rule_engine import vat_lieu

    d = dau_vao["duong_kinh"]
    Rs = dau_vao["Rs"]
    Rbt = dau_vao["Rbt"]
    co_go = dau_vao.get("co_go", True)
    As_cal = dau_vao.get("As_cal", vat_lieu.dien_tich_1_thanh(d))
    As_ef = dau_vao.get("As_ef", As_cal)
    keo = dau_vao.get("keo", True)

    eta1 = neo_noi.tinh_eta1(co_go)
    eta2 = neo_noi.tinh_eta2(d)
    R_bond = neo_noi.tinh_R_bond(eta1, eta2, Rbt)
    us = neo_noi.chu_vi_thanh(d)
    L0_an = neo_noi.tinh_L0_an(Rs, vat_lieu.dien_tich_1_thanh(d), R_bond, us)

    return {
        "L0_an": L0_an,
        "L_an": neo_noi.tinh_L_an(L0_an, As_cal, As_ef, d, keo),
        "L_lap": neo_noi.tinh_L_lap(L0_an, As_cal, As_ef, d, keo),
        "duong_kinh_uon_toi_thieu": neo_noi.duong_kinh_uon_toi_thieu(d, co_go),
    }


# ---------------------------------------------------------------------------
# Tự kiểm tra (vòng lặp tự sửa lỗi).
# ---------------------------------------------------------------------------


def tu_kiem_tra(nc: NguCanhRuleEngine, dau_vao: dict) -> dict:
    """loai='cot': KHÔNG nhận 'x'/'e' từ LLM — LUÔN được tool TỰ TÍNH nội bộ
    qua `_tinh_lech_tam_cot_noi_bo`. 'mu_max'/'mu_max_moi_phia' CŨNG KHÔNG
    được nhận từ LLM, luôn dùng đúng hằng số TCVN. Xem
    docs/agents/RULE_ENGINE_AGENT.md mục "Lỗi thật đã từng gặp" cho lý do đầy
    đủ (2 lỗi nghiêm trọng thật đã gặp khi không chặn 2 điều này ở tầng code)."""
    loai = dau_vao["loai"]
    if loai == "dam" and nc.khong_co_Q:
        # Không có Q thô (nguồn ETABS) -> KHÔNG gọi verify.kiem_tra_tong_hop_dam
        # (đòi hỏi Q để kiểm tra chịu cắt mục 3) — trả kết quả TRUNG THỰC:
        # chỉ kiểm tra được As dọc, có canh_bao rõ ràng, KHÔNG bịa Q dù LLM
        # có truyền giá trị nào trong thong_so["Q"] (bị NGÓ LƠ hoàn toàn, kể
        # cả khi LLM tự đặt để "cho đủ field"). Xem docstring NguCanhRuleEngine.
        ts = dau_vao["thong_so"]
        as_thuc, as_yc = ts.get("As_thuc"), ts.get("As_yc")
        dat_as_doc = as_thuc is not None and as_yc is not None and as_thuc >= as_yc
        return {
            "dat": dat_as_doc,
            "vi_pham": [] if dat_as_doc else [f"As_thuc={as_thuc} < As_yc={as_yc} (thép dọc chưa đủ)"],
            "canh_bao": (
                "Không có Q thô cho phần tử này (nguồn ETABS) nên KHÔNG kiểm tra được điều kiện chịu cắt "
                "mục 3 — 'dat' ở đây CHỈ phản ánh As dọc đã đạt/chưa đạt so với As yêu cầu. KHÔNG được "
                "diễn giải đây là đã tự kiểm tra đầy đủ; không gọi lại tu_kiem_tra hay hoi_nguoi_dung "
                "thêm cho việc này, tiếp tục sang bước vẽ."
            ),
        }
    if loai == "dam":
        ts = dict(dau_vao["thong_so"])
        ts.pop("mu_max", None)
        ket_qua = verify.kiem_tra_tong_hop_dam(verify.DauVaoVerifyDam(**ts))
    elif loai == "cot":
        ts = dict(dau_vao["thong_so"])
        try:
            N, M = ts.pop("N"), ts.pop("M")
        except KeyError as e:
            return _loi(f"thong_so cho loai='cot' thiếu trường bắt buộc: {e}")
        if N <= 0:
            return _loi("tu_kiem_tra cho cột chỉ áp dụng khi N > 0 (nén lệch tâm) — mục 2.5.")
        b, h = ts["b"], ts["h"]
        a_prime = ts.get("a_prime", 40.0)
        Rb, Rs, Rsc = ts["Rb"], ts.get("Rs", ts["Rsc"]), ts["Rsc"]
        As_thuc = ts["As_thuc"]
        lech_tam = _tinh_lech_tam_cot_noi_bo(
            N=N, M=M, b=b, h=h, a_prime=a_prime, Rb=Rb, Rs=Rs, Rsc=Rsc,
            As_gia_dinh=As_thuc, Es=ts.get("Es", 2.0e5), L=ts.get("L"),
        )
        ts_cho_verify = {
            "As_thuc": As_thuc, "b": b, "h0": h - a_prime, "do_manh_L0_h": ts.get("do_manh_L0_h", 0.0),
            "N": N, "e": lech_tam["e"], "Rb": Rb, "Rsc": Rsc, "x": lech_tam["x"], "a_prime": a_prime,
        }
        ket_qua = verify.kiem_tra_tong_hop_cot(verify.DauVaoVerifyCot(**ts_cho_verify))
    else:
        return _loi(f"loai phải là 'dam' hoặc 'cot', nhận '{loai}'.")

    ket_qua_tra_ve: dict[str, Any] = {"dat": ket_qua.dat, "vi_pham": ket_qua.vi_pham}
    if not ket_qua.dat:
        con_duoc = nc.bo_dem.ghi_nhan_1_lan_thu("tu_sua")
        ket_qua_tra_ve["so_lan_tu_sua_con_lai"] = nc.bo_dem.so_lan_con_lai("tu_sua")
        if not con_duoc:
            ket_qua_tra_ve["het_luot_tu_sua"] = True
            ket_qua_tra_ve["huong_dan"] = (
                "Đã hết số lần thử tự sửa cho phép — KHÔNG thử lại chon_thep_doc nữa, "
                "phải gọi hoi_nguoi_dung để báo cáo vi phạm còn lại."
            )
    return ket_qua_tra_ve


# ---------------------------------------------------------------------------
# Đăng ký tool.
# ---------------------------------------------------------------------------

DINH_NGHIA_TOOL: list[dict] = [
    {
        "name": "tra_vat_lieu",
        "description": (
            "Tra Rb/Rbt (bê tông), Rs/Rsc (thép dọc), Rsw (thép đai) từ bảng chuẩn mục 1 "
            "RULES_TCVN5574.md theo mác bê tông/nhóm thép. BẮT BUỘC gọi tool này trước "
            "chon_thep_doc/tinh_cot_dai/tinh_neo_noi — KHÔNG được tự nhớ/đoán các giá trị này."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "mac_be_tong": {"type": "string", "description": "vd \"B25\", \"B30\""},
                "nhom_thep_doc": {"type": "string", "description": "vd \"CB400-V\", \"CB500-V\""},
                "nhom_thep_dai": {"type": "string", "description": "vd \"CB240-T\""},
            },
        },
    },
    {
        "name": "tinh_lech_tam_cot",
        "description": (
            "TUỲ CHỌN (không bắt buộc) — tính trước ξR, e0, cánh tay đòn e, nhánh lệch tâm lớn/bé, "
            "chiều cao vùng nén x, và Mu cho CỘT nén lệch tâm (mục 2.5), để bạn XEM/GIẢI THÍCH kết "
            "quả cho người dùng. tu_kiem_tra đã TỰ tính lại đúng các giá trị này nội bộ nên không "
            "cần gọi tool này trước — chỉ dùng khi muốn trình bày chi tiết trung gian. Chỉ áp dụng "
            "khi N>0 (nén); CHƯA tính hệ số uốn dọc η (mặc định η=1, chỉ an toàn cho cột không mảnh)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "N": {"type": "number", "description": "Lực dọc (kN), phải > 0"},
                "M": {"type": "number", "description": "Mô men (kN·m) tại tiết diện đang xét"},
                "b": {"type": "number"}, "h": {"type": "number"},
                "a_prime": {"type": "number", "description": "Khoảng cách mép chịu nén đến trọng tâm As' (mm), mặc định 40"},
                "Rb": {"type": "number"}, "Rs": {"type": "number"}, "Rsc": {"type": "number"},
                "Es": {"type": "number", "description": "Mặc định 2e5 MPa nếu bỏ trống"},
                "As_gia_dinh": {"type": "number", "description": "As=A's dùng để thử nhánh lệch tâm (dùng As_thuc_moi_phia từ chon_thep_doc)"},
                "L": {"type": "number", "description": "Chiều dài đoạn cột (mm), tuỳ chọn — dùng tính ea theo L/600"},
            },
            "required": ["N", "M", "b", "h", "Rb", "Rs", "Rsc", "As_gia_dinh"],
        },
    },
    {
        "name": "chon_thep_doc",
        "description": (
            "Chọn tổ hợp thép dọc thật thoả As_target — mục 4 RULES_TCVN5574.md. "
            "loai='dam': xếp thanh thành hàng trên/dưới, trả về 'thanh' (mảng {duong_kinh,so_luong}). "
            "loai='cot': BẮT BUỘC truyền thêm 'h', bố trí ĐỀU CHU VI (khác hẳn dầm), As_target là As "
            "MỖI PHÍA (As=A's theo mục 2.5/10.4, KHÔNG phải tổng 2 phía cộng lại) — TRUYỀN THẲNG As_yc "
            "nhận được từ Input Adapter cho vị trí này (dù As_yc đến từ PMMArea của ETABS, đã xác nhận "
            "qua chạy thật giá trị này xấp xỉ đúng As MỖI PHÍA theo TCVN, KHÔNG phải tổng — chia đôi sẽ "
            "làm thép thiếu, gây hàng loạt cột không đạt tu_kiem_tra N·e>Mu). Kết quả trả về "
            "(so_thanh_canh_b/h, duong_kinh) dùng THẲNG cho Drawing Agent, không tự suy đổi. Tool tự "
            "lọc bỏ mọi đường kính < 12mm dù truyền trong duong_kinh_cho_phep — không cần tự lọc lại."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loai": {"type": "string", "enum": ["dam", "cot"], "description": "Mặc định 'dam' nếu bỏ trống."},
                "As_target": {"type": "number"},
                "duong_kinh_cho_phep": {"type": "array", "items": {"type": "integer"}},
                "b": {"type": "number"},
                "h": {"type": "number", "description": "CHỈ bắt buộc khi loai='cot'."},
                "cover": {"type": "number"},
                "duong_kinh_dai_du_kien": {"type": "number"},
            },
            "required": ["As_target", "b"],
        },
    },
    {
        "name": "tinh_cot_dai",
        "description": (
            "Kiểm tra ép vỡ bụng + tính điều kiện chịu cắt cơ bản — mục 3 RULES_TCVN5574.md. "
            "Nếu có N (cột): truyền 'h' (chiều cao tiết diện ĐẦY ĐỦ, không phải h0) để tool TỰ "
            "TÍNH diện tích tiết diện A=b*h nội bộ — KHÔNG tự nhân b*h rồi truyền 'A'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "Q": {"type": "number"}, "N": {"type": "number"}, "h": {"type": "number"},
                "Rb": {"type": "number"}, "Rbt": {"type": "number"}, "Rsw": {"type": "number"},
                "b": {"type": "number"}, "h0": {"type": "number"}, "Asw": {"type": "number"},
                "sw_thu": {"type": "number"}, "loai": {"type": "string", "enum": ["dam", "cot"]},
                "d_doc_min": {"type": "number"}, "dieu_kien_dac_biet": {"type": "boolean"},
            },
            "required": ["Q", "Rb", "Rbt", "Rsw", "b", "h0"],
        },
    },
    {
        "name": "tinh_neo_noi",
        "description": "Tính chiều dài neo cơ sở/tính toán, nối chồng, đường kính uốn — mục 6 RULES_TCVN5574.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "duong_kinh": {"type": "integer"}, "Rs": {"type": "number"}, "Rbt": {"type": "number"},
                "co_go": {"type": "boolean"}, "keo": {"type": "boolean"},
                "As_cal": {"type": "number"}, "As_ef": {"type": "number"},
            },
            "required": ["duong_kinh", "Rs", "Rbt"],
        },
    },
    {
        "name": "tu_kiem_tra",
        "description": (
            "Chạy toàn bộ điều kiện cấu tạo liên quan cho 1 tiết diện đã chọn thép (vòng lặp tự "
            "sửa lỗi). 'thong_so' phải là object PHẲNG, CHỈ chứa đúng field liệt kê dưới đây theo "
            "'loai' — thừa/thiếu field sẽ báo lỗi."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "loai": {"type": "string", "enum": ["dam", "cot"]},
                "thong_so": {
                    "type": "object",
                    "description": (
                        "loai=dam (bắt buộc đủ): As_yc, As_thuc, danh_sach_duong_kinh (mảng số "
                        "nguyên đường kính từng thanh), b, h0, do_manh_L0_h, so_lop, "
                        "so_lop_toi_da_cho_phep, Q, Rb, Rbt, Rsw, Asw, sw. "
                        "loai=cot (bắt buộc đủ): As_thuc, b, h (chiều cao TIẾT DIỆN, KHÔNG phải "
                        "h0), N, M (mô men kN·m — KHÔNG truyền 'e'/'x', tool TỰ TÍNH nội bộ), "
                        "Rb, Rsc, a_prime, do_manh_L0_h (tuỳ chọn: Rs, Es mặc định 2e5, L). "
                        "KHÔNG truyền 'mu_max'/'mu_max_moi_phia' — ngưỡng CỐ ĐỊNH theo TCVN, mọi "
                        "giá trị LLM tự đặt cho 2 trường này sẽ BỊ BỎ QUA."
                    ),
                    "properties": {
                        "As_yc": {"type": "number"}, "As_thuc": {"type": "number"},
                        "danh_sach_duong_kinh": {"type": "array", "items": {"type": "integer"}},
                        "b": {"type": "number"}, "h0": {"type": "number"}, "h": {"type": "number"},
                        "do_manh_L0_h": {"type": "number"},
                        "so_lop": {"type": "integer"}, "so_lop_toi_da_cho_phep": {"type": "integer"},
                        "Q": {"type": "number"}, "Rb": {"type": "number"}, "Rbt": {"type": "number"},
                        "Rsw": {"type": "number"}, "Asw": {"type": "number"}, "sw": {"type": "number"},
                        "N": {"type": "number"}, "M": {"type": "number"}, "Rsc": {"type": "number"},
                        "Rs": {"type": "number"}, "Es": {"type": "number"}, "L": {"type": "number"},
                        "a_prime": {"type": "number"},
                    },
                },
            },
            "required": ["loai", "thong_so"],
        },
    },
    DINH_NGHIA_HOI_NGUOI_DUNG,
]

_HAM_THEO_TEN: dict[str, Callable[[NguCanhRuleEngine, dict], dict]] = {
    "tra_vat_lieu": tra_vat_lieu,
    "tinh_lech_tam_cot": tinh_lech_tam_cot,
    "chon_thep_doc": chon_thep_doc,
    "tinh_cot_dai": tinh_cot_dai,
    "tinh_neo_noi": tinh_neo_noi,
    "tu_kiem_tra": tu_kiem_tra,
    "hoi_nguoi_dung": hoi_nguoi_dung,
}


def tao_dispatch(nc: NguCanhRuleEngine) -> dict[str, Callable[[dict], dict]]:
    return {ten: (lambda dau_vao, _ham=ham: _ham(nc, dau_vao)) for ten, ham in _HAM_THEO_TEN.items()}


# ---------------------------------------------------------------------------
# System prompt + hàm chạy 1 phiên độc lập cho 1 PHẦN TỬ.
# ---------------------------------------------------------------------------

# Bộ skill chọn thép (10 module `NN_*.md` trong docs/agents/huongdanchonthep/,
# biên soạn từ "Hướng dẫn thực hành chọn thép khung phẳng BTCT toàn khối" —
# xem docs/agents/BAN_DO_PHU_NGUON_SANG_SKILL.md) — thay rule base 76 trang cũ
# (đã lưu trữ ở _luu_tru/). Phần Q (bảng Điều kiện→Xử lý) và Phần R (ví dụ
# Khung Trục 5 thật) của rule base cũ được hợp nhất vào module 08 và 09 nên
# các test hồi quy "PHẦN Q", "D2", "Khung Trục 5" vẫn đúng.
#
# Ngân sách ngữ cảnh: nạp ở chế độ "gon" (module dài chỉ nạp phần thiết yếu,
# bỏ khối mô tả ảnh trừ hình nút khung) và theo LOẠI cấu kiện (dầm không cần
# module cột 03 và ngược lại). Chạy thật truyền `loai` (xem chay_rule_engine_agent).
_THU_MUC_SKILL_CHON_THEP = doc_skill.THU_MUC_AGENTS / "huongdanchonthep"
_RULE_BASE_CU_DA_LUU_TRU = _THU_MUC_SKILL_CHON_THEP / "_luu_tru" / "RULE_BASE_CHON_THEP_KHUNG_BTCT.md"
# Module loại trừ theo loại cấu kiện: chọn thép dầm bỏ 03 (cột); chọn thép cột bỏ 02 (dầm).
_MODULE_LOAI_TRU_THEO_LOAI = {"dam": ("03",), "cot": ("02",)}


def _doc_skill_chon_thep(loai: str | None = None) -> str:
    """Nạp bộ skill chọn thép. Trả "" (không raise) nếu thiếu thư mục và cả file lưu trữ — vẫn chạy được với
    prompt rút gọn, nhưng thiếu skill là bất thường cần sửa ngay."""
    return doc_skill.doc_bo_skill(
        _THU_MUC_SKILL_CHON_THEP, du_phong=_RULE_BASE_CU_DA_LUU_TRU, che_do=doc_skill.CHE_DO_GON,
        loai_tru=_MODULE_LOAI_TRU_THEO_LOAI.get(loai or "", ()),
    )


def _xay_dung_he_thong_prompt(loai: str | None = None) -> str:
    prompt = """\
Bạn là Rule Engine Agent trong hệ thống thiết kế khung BTCT theo TCVN \
5574:2018 (đọc chi tiết: docs/agents/RULE_ENGINE_AGENT.md). Bạn nhận 1 phần \
tử (dầm hoặc cột) đã chuẩn hoá, gồm nhiều VỊ TRÍ cần chọn thép. Vai trò CHỈ \
là điều phối gọi Rule Engine thuần và tự kiểm tra — bạn KHÔNG BAO GIỜ tự \
tính bất kỳ con số kỹ thuật nào (As, x, ξ, Qsw, chiều dài neo...) bằng suy \
luận của chính bạn. Mọi con số phải đến từ kết quả gọi tool.

Với MỖI vị trí, lặp lại đúng trình tự:
1. Gọi tra_vat_lieu TRƯỚC KHI tính bất cứ gì khác — không tự nhớ/đoán \
Rb/Rbt/Rs/Rsc/Rsw dù có vẻ quen thuộc.
2. Gọi chon_thep_doc — LUÔN truyền đúng loai='dam'/'cot' của phần tử (cột \
cần thêm 'h' và As_target là As MỖI PHÍA, khác hẳn cách bố trí của dầm).
3. Gọi tinh_cot_dai và tinh_neo_noi, dùng đúng Rb/Rbt/Rs/Rsc/Rsw đã lấy ở \
bước 1. Với CỘT có N: truyền 'h' cho tinh_cot_dai để tool tự tính A=b*h — \
KHÔNG tự nhân b*h rồi truyền 'A'.
4. Gọi tu_kiem_tra. Với CỘT: truyền N, M — KHÔNG truyền "e"/"x", tool tự \
tính nội bộ. Nếu "dat"=false: xem "so_lan_tu_sua_con_lai" — nếu còn > 0, \
quay lại bước 2 với điều kiện đã điều chỉnh dựa trên "vi_pham" (vd nới \
đường kính cho phép, tăng cover — không nới xuống dưới 12mm, tool tự chặn \
việc đó); nếu "het_luot_tu_sua"=true, BẮT BUỘC gọi hoi_nguoi_dung báo cáo vi \
phạm còn lại, KHÔNG được gọi chon_thep_doc thêm nữa cho vị trí này.
5. Khi "dat"=true, chuyển sang vị trí tiếp theo của phần tử (quay lại bước 1 \
— vật liệu thường giống nhau trong cùng phần tử nên có thể tái dùng kết quả \
đã tra nếu chưa đổi mác bê tông/nhóm thép).

Khi TẤT CẢ vị trí của phần tử đã đạt tự kiểm tra (hoặc đã báo cáo người dùng \
cho vị trí hết lượt tự sửa), dừng lại và tóm tắt kết quả cuối cùng bằng văn \
bản (thép đã chọn cho từng vị trí) — không gọi thêm tool nào nữa.

Nếu mô tả 1 vị trí ghi rõ "Q: KHÔNG CÓ" (nguồn ETABS design summary không \
xuất raw force cho dầm): BỎ QUA bước gọi tinh_cot_dai cho phần tử này (tool \
sẽ tự chặn nếu bạn vẫn gọi), chỉ đề xuất Ø8 bước cấu tạo hợp lý (150mm gần \
gối, 200-250mm giữa nhịp). Vẫn GỌI tu_kiem_tra bình thường — tool tự trả về \
kết quả chỉ kiểm tra As dọc kèm "canh_bao" rõ ràng, đây là hành vi ĐÃ THIẾT \
KẾ, không cần hỏi người dùng thêm cho việc này.
"""
    prompt += """
Ngoài các tool, hệ thống CHƯA có tool cho: cấu tạo nút khung, bố trí dọc (điểm \
cắt, chiều dài thanh, vùng đai), kiểm hình học nút, kháng chấn, xoắn/dầm \
cao/lỗ mở. Với các việc đó bạn KHÔNG tự tính con số: áp dụng luật định tính \
trong bộ skill bên dưới (ví dụ BẢNG ĐIỀU KIỆN THÊM THÉP ở module 05), ghi rõ \
nguồn và nhãn basis (TCVN/thuc_hanh/uoc_luong/can_xac_nhan), gắn cờ cho mọi \
con số do suy luận, và gọi hoi_nguoi_dung khi quyết định thuộc về kỹ sư (cấp \
dẻo kháng chấn, loại nút khi thiếu dữ liệu, dầm cao, lỗ mở, xoắn). Tuyệt đối \
KHÔNG in chữ "ĐẠT" trong tóm tắt cuối khi còn cờ chưa xử lý (R45, R46).
"""
    skill = _doc_skill_chon_thep(loai)
    if skill:
        prompt += (
            "\n\n# TÀI LIỆU THAM KHẢO BẮT BUỘC — Bộ skill chọn thép khung BTCT (10 module 00–09)\n"
            "Dưới đây là bộ skill (TCVN 5574:2018; kháng chấn theo EN 1998-1 ở mức sơ bộ ⚠). Các tool "
            "(chon_thep_doc, tinh_cot_dai, tinh_neo_noi, tu_kiem_tra) ĐÃ CÀI ĐẶT các công thức tương ứng: "
            "bạn KHÔNG tự tính lại, chỉ dùng skill để hiểu/giải thích kết quả tool, biết giới hạn của tool và "
            "biết việc nào chưa có tool. Module 00 là thứ tự ưu tiên nguồn và bản đồ tool; module 05 là cấu "
            "tạo nút khung và bảng điều kiện thêm thép; module 08 chứa PHẦN Q (danh mục ~70 trường hợp "
            "Điều kiện→Xử lý — TRA CỨU TRỰC TIẾP khi gặp tình huống biên: As âm, N là lực kéo, lệch tâm bé, "
            "vượt μmax, thiếu Q… tra đúng mã như D2, A3, I1 rồi làm theo cột 'Xử lý') và chỉ mục luật R1–R52; "
            "module 09 có cổng chặn R41–R46, xoắn/dầm cao/lỗ mở R47–R52 và ví dụ đối chiếu Khung Trục 5 "
            "(As_yc của cột là MỖI PHÍA, không phải tổng — mục 71–72). Khi nguồn tài liệu mâu thuẫn nhau "
            "(ghi ⚠), dùng giá trị an toàn hơn và ghi cờ.\n\n"
            f"{skill}"
        )
    return prompt


HE_THONG_PROMPT = _xay_dung_he_thong_prompt()
# Prompt theo loại cấu kiện (nhỏ hơn): chay_rule_engine_agent(loai=...) dùng bản tương ứng.
HE_THONG_PROMPT_THEO_LOAI = {"dam": _xay_dung_he_thong_prompt("dam"), "cot": _xay_dung_he_thong_prompt("cot")}


def chay_rule_engine_agent(
    nha_cung_cap: agent.NhaCungCapChat,
    mo_ta_phan_tu: str,
    hoi_nguoi_dung: HamHoiNguoiDung,
    gioi_han_vong_lap: dict[str, int] | None = None,
    so_lan_goi_toi_da: int = 30,
    khong_co_Q: bool = False,
    loai: str | None = None,
) -> tuple[agent.KetQuaVongLapAgent, NguCanhRuleEngine]:
    """Chạy 1 phiên độc lập của Rule Engine Agent cho 1 phần tử (mô tả bằng
    văn bản, gồm mọi vị trí cần xử lý — do pipeline.py soạn từ
    BoDuLieuKhungChuanHoa). `so_lan_goi_toi_da` cao hơn 3 agent kia vì agent
    này lặp qua NHIỀU vị trí trong cùng 1 phiên (dầm: 3 vị trí × ~5 lượt gọi
    tool/vị trí).

    `khong_co_Q`: True khi phần tử này (thường: dầm nguồn ETABS thật) không
    có Q thô cho bất kỳ vị trí nào — chặn `tinh_cot_dai` và làm nhẹ
    `tu_kiem_tra` ở tầng code (xem docstring `NguCanhRuleEngine`).

    `loai`: "dam" | "cot" | None — chọn system prompt theo loại cấu kiện (bộ skill bỏ module không liên
    quan để giữ ngân sách ngữ cảnh); None ⇒ prompt đầy đủ cả hai loại (hành vi cũ).
"""
    bo_dem = BoDemVongLap(gioi_han=dict(gioi_han_vong_lap) if gioi_han_vong_lap else BoDemVongLap().gioi_han)
    nc = NguCanhRuleEngine(
        hoi_nguoi_dung=hoi_nguoi_dung, bo_dem=bo_dem, khong_co_Q=khong_co_Q
    )
    dispatch = tao_dispatch(nc)
    ket_qua = agent.chay_vong_lap_tool(
        nha_cung_cap=nha_cung_cap, he_thong=HE_THONG_PROMPT_THEO_LOAI.get(loai or "", HE_THONG_PROMPT),
        tin_nhan_dau=mo_ta_phan_tu,
        tools=DINH_NGHIA_TOOL, dispatch=dispatch, so_lan_goi_toi_da=so_lan_goi_toi_da,
    )
    return ket_qua, nc


def trich_phuong_an_thep(
    ket_qua: agent.KetQuaVongLapAgent, ten_phan_tu: str, loai: str, b: float, h: float,
) -> PhuongAnThepPhanTu:
    """Bóc tách `PhuongAnThepPhanTu` (dữ liệu kiểu Python có cấu trúc, bàn
    giao cho Drawing Agent) từ `nhat_ky_tool` của 1 phiên Rule Engine Agent.

    QUAN TRỌNG — không thể chỉ đếm số lần gọi `chon_thep_doc` rồi ghép 1-1
    theo chỉ số: khi 1 vị trí phải TỰ SỬA (`tu_kiem_tra` trả `dat=false`, còn
    lượt), model sẽ gọi lại `chon_thep_doc` NHIỀU LẦN cho CÙNG 1 vị trí —
    đếm thẳng số lần gọi sẽ ra nhiều "vị trí ảo" hơn thực tế. Thuật toán đúng
    là duyệt `nhat_ky_tool` THEO ĐÚNG THỨ TỰ THỜI GIAN, tích luỹ lần gọi GẦN
    NHẤT của từng loại tool, và chỉ "chốt" 1 vị trí khi gặp `tu_kiem_tra` trả
    về trạng thái KẾT THÚC (`dat=true`, hoặc `het_luot_tu_sua=true` — hết
    lượt tự sửa, không thử thêm nữa dù chưa đạt) — đúng khớp với
    `so_lan_tu_sua_con_lai`/`het_luot_tu_sua` mà `BoDemVongLap` (`loops.py`)
    đã tính, không suy đoán lại.

    Tên vị trí ("vi_tri_1", "vi_tri_2"...) chỉ là CHỈ SỐ THỨ TỰ — tên THẬT do
    `pipeline.py` gán lại theo đúng danh sách vị trí Input Adapter Agent đã
    cho (agent này gọi tool tuần tự đúng thứ tự system prompt yêu cầu, nên
    thứ tự chốt vị trí ở đây LUÔN khớp thứ tự vị trí trong dữ liệu đầu vào).
    """
    vi_tri: list[KetQuaViTriDaThietKe] = []
    thep_hien_tai: dict[str, Any] | None = None
    cot_dai_hien_tai: dict[str, Any] = {}
    neo_noi_hien_tai: dict[str, Any] = {}

    for muc in ket_qua.nhat_ky_tool:
        ten_tool, kq = muc["ten"], muc["ket_qua"]
        if ten_tool == "chon_thep_doc" and "loi" not in kq:
            thep_hien_tai = kq  # ghi đè — luôn giữ lần gọi GẦN NHẤT cho vị trí đang xử lý
        elif ten_tool == "tinh_cot_dai" and "loi" not in kq:
            cot_dai_hien_tai = kq
        elif ten_tool == "tinh_neo_noi" and "loi" not in kq:
            neo_noi_hien_tai = kq
        elif ten_tool == "tu_kiem_tra":
            dat = bool(kq.get("dat"))
            het_luot = bool(kq.get("het_luot_tu_sua"))
            if not (dat or het_luot):
                continue  # chưa kết thúc vị trí này — model sẽ gọi lại chon_thep_doc, chưa chốt
            vi_tri.append(
                KetQuaViTriDaThietKe(
                    vi_tri=f"vi_tri_{len(vi_tri) + 1}",
                    thep_doc=thep_hien_tai or {}, cot_dai=cot_dai_hien_tai, neo_noi=neo_noi_hien_tai,
                    dat=dat, vi_pham=kq.get("vi_pham", []),
                )
            )
            thep_hien_tai, cot_dai_hien_tai, neo_noi_hien_tai = None, {}, {}  # reset cho vị trí kế tiếp

    return PhuongAnThepPhanTu(ten_phan_tu=ten_phan_tu, loai=loai, b=b, h=h, vi_tri=vi_tri)
