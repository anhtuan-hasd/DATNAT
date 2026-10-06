"""Điều phối cấp cao — `chay_toan_bo_khung()` ghép 4 agent (`agents/*.py`)
thành pipeline hoàn chỉnh theo đúng mục 5 `docs/TONGQUAN_AI_AGENT.md`.

QUAN TRỌNG: file này KHÔNG gọi LLM trực tiếp và KHÔNG chứa công thức kỹ
thuật nào — nó chỉ là "dây dẫn": gọi 4 hàm `chay_<ten>_agent()` theo đúng
thứ tự, và chuyển tiếp dữ liệu giữa chúng qua các dataclass ở
`shared/hop_dong_du_lieu.py`. Đây là điểm khác biệt LỚN NHẤT so với
`pipeline.py` bản cũ (1 system prompt cho cả 7 bước, 1 phiên LLM duy nhất).

Chiến lược truyền dữ liệu lớn (toạ độ trục, danh sách phần tử+thép) sang
Drawing/Verification Agent: thay vì yêu cầu LLM TỰ GÕ LẠI dữ liệu từ trí nhớ
(rủi ro sai số/thiếu trường đã biết của LLM với dữ liệu lớn), pipeline.py
NHÚNG SẴN đúng khối JSON cần truyền vào tin nhắn yêu cầu, và system prompt
của agent đó (xem `agents/drawing_agent.py`) chỉ dẫn "SAO CHÉP NGUYÊN VĂN"
khối JSON đó vào tham số tool — LLM chỉ quyết định GỌI TOOL NÀO, không phải
tự nhớ lại số liệu.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from ..drawing import backend_com
from . import agent
from .agents import drawing_agent, input_adapter_agent, rule_engine_agent, verification_agent
from .loops import BoDemVongLap
from .shared.hop_dong_du_lieu import BoDuLieuKhungChuanHoa, KetQuaKhung, KetQuaPhanTu, PhuongAnThepPhanTu
from .shared.phien_cad import PhienCAD

HamHoiNguoiDung = Callable[[str, list[str] | None], str]
# Observer tuỳ chọn — gọi mỗi khi 1 agent con thực thi xong (KHÔNG BẮT BUỘC,
# webapp (Giai đoạn 2) dùng để log tiến trình thời gian thực lên trang web;
# script CLI có thể bỏ qua hoặc dùng để in log).
HamQuanSat = Callable[[str, str, agent.KetQuaVongLapAgent], None]


def _bao(quan_sat: HamQuanSat | None, giai_doan: str, ten: str, kq: agent.KetQuaVongLapAgent) -> None:
    if quan_sat is not None:
        quan_sat(giai_doan, ten, kq)


# ---------------------------------------------------------------------------
# Bước 1 — Input Adapter Agent (chạy 1 lần cho cả file).
# ---------------------------------------------------------------------------


def _chay_buoc_input_adapter(
    nha_cung_cap: agent.NhaCungCapChat, duong_dan_file: str, hoi_nguoi_dung: HamHoiNguoiDung,
    quan_sat: HamQuanSat | None,
) -> BoDuLieuKhungChuanHoa | None:
    ket_qua, nc = input_adapter_agent.chay_input_adapter_agent(nha_cung_cap, duong_dan_file, hoi_nguoi_dung)
    _bao(quan_sat, "input_adapter", "file", ket_qua)
    return input_adapter_agent.trich_bo_du_lieu_chuan_hoa(nc)


# ---------------------------------------------------------------------------
# Bước 2 — Rule Engine Agent (lặp qua từng phần tử).
# ---------------------------------------------------------------------------


def _mo_ta_yeu_cau_rule_engine(ten_khung: str, p) -> str:  # p: PhanTuChuanHoa
    dong = [
        f"Chọn thép cho {'CỘT' if p.loai == 'cot' else 'dầm'} '{p.ten}' (khung '{ten_khung}'), "
        f"tiết diện b={p.b}mm, h={p.h}mm, mác bê tông {p.mac_be_tong}, nhóm thép dọc {p.nhom_thep_doc}.",
        "Xử lý LẦN LƯỢT từng vị trí sau, ĐÚNG THỨ TỰ liệt kê:",
    ]
    for v in p.vi_tri:
        # Ghi RÕ "KHÔNG CÓ" thay vì in thẳng "Q=None" — chuỗi "None" trông
        # giống 1 giá trị số bất thường hơn là 1 tín hiệu rõ ràng "trường
        # này thật sự không tồn tại", dễ khiến LLM tự hiểu nhầm/tự bịa số
        # thay thế. Khớp đúng câu chữ HE_THONG_PROMPT của rule_engine_agent
        # đang tìm ("Q: KHÔNG CÓ") để agent nhận diện đúng tình huống.
        Q_hien_thi = "KHÔNG CÓ (nguồn ETABS design summary không xuất raw force cho dầm)" if v.Q is None else v.Q
        dong.append(
            f"- Vị trí '{v.vi_tri}': As_yc={v.As_yc}mm², M={v.M}, N={v.N}, Q: {Q_hien_thi} (kN/kN·m), "
            f"tổ hợp chi phối '{v.to_hop}'."
        )
    return "\n".join(dong)


def _chay_buoc_rule_engine(
    nha_cung_cap: agent.NhaCungCapChat, ten_khung: str, p, hoi_nguoi_dung: HamHoiNguoiDung,
    gioi_han_vong_lap: dict[str, int] | None, quan_sat: HamQuanSat | None,
) -> PhuongAnThepPhanTu:
    mo_ta = _mo_ta_yeu_cau_rule_engine(ten_khung, p)
    # Dầm nguồn ETABS thật: TOÀN BỘ vị trí luôn cùng thiếu Q (hạn chế của
    # nguồn dữ liệu, không phải của riêng 1 vị trí — xem etabs_reader.py) —
    # chỉ cần 1 vị trí thiếu Q đã đủ suy ra CẢ phần tử thiếu Q.
    khong_co_Q = p.loai == "dam" and any(v.Q is None for v in p.vi_tri)
    ket_qua, _nc = rule_engine_agent.chay_rule_engine_agent(
        nha_cung_cap, mo_ta, hoi_nguoi_dung, gioi_han_vong_lap=gioi_han_vong_lap, khong_co_Q=khong_co_Q,
    )
    _bao(quan_sat, "rule_engine", p.ten, ket_qua)
    phuong_an = rule_engine_agent.trich_phuong_an_thep(ket_qua, ten_phan_tu=p.ten, loai=p.loai, b=p.b, h=p.h)
    # Gán lại TÊN VỊ TRÍ THẬT (rule_engine_agent chỉ biết thứ tự, không biết
    # tên) — khớp đúng thứ tự p.vi_tri vì system prompt buộc xử lý tuần tự.
    for i, vt in enumerate(phuong_an.vi_tri):
        if i < len(p.vi_tri):
            vt.vi_tri = p.vi_tri[i].vi_tri
    return phuong_an


# ---------------------------------------------------------------------------
# Bước 3 — Drawing Agent vẽ từng mặt cắt + Verification Agent kiểm chứng
# NGAY (vòng lặp riêng cho mỗi mặt cắt, BoDemVongLap RIÊNG mỗi mặt cắt).
# ---------------------------------------------------------------------------


def _mo_ta_yeu_cau_ve_mat_cat(p, vt, cover: float, duong_kinh_dai: float) -> tuple[str, dict]:
    if p.loai == "cot":
        # thep_doc của cột là kết quả chon_thep_doc(loai='cot') — đã có sẵn
        # đúng field so_thanh_canh_b/h, duong_kinh_canh_b/h.
        du_lieu_tool = {
            "loai": "cot", "nhan": f"{p.ten}/{vt.vi_tri}", "b": p.b, "h": p.h, "cover": cover,
            "duong_kinh_dai": duong_kinh_dai,
            "so_thanh_canh_b": vt.thep_doc.get("so_thanh_canh_b"), "duong_kinh_canh_b": vt.thep_doc.get("duong_kinh"),
            "so_thanh_canh_h": vt.thep_doc.get("so_thanh_canh_h"), "duong_kinh_canh_h": vt.thep_doc.get("duong_kinh"),
        }
    else:
        thanh = vt.thep_doc.get("thanh", [])
        # Dầm: KHÔNG phân biệt thép trên/dưới trong PhuongAnThepPhanTu hiện
        # tại (Rule Engine Agent chọn 1 tổ hợp chung cho vị trí, chưa tách
        # lớp trên/dưới theo mô men dương/âm — đơn giản hoá có chủ đích, xem
        # ghi chú dưới) — đặt TOÀN BỘ vào thanh_duoi cho vị trí "giua_nhip"
        # (mô men dương, thép chịu kéo ở dưới) và thanh_tren cho "goi_trai"/
        # "goi_phai" (mô men âm, thép chịu kéo ở trên) — đúng quy ước dầm
        # liên tục thông thường (mục 10.6 RULES_TCVN5574.md).
        danh_sach_duong_kinh = [th["duong_kinh"] for th in thanh for _ in range(th["so_luong"])]
        o_tren = "goi" in vt.vi_tri
        du_lieu_tool = {
            "loai": "dam", "nhan": f"{p.ten}/{vt.vi_tri}", "b": p.b, "h": p.h, "cover": cover,
            "duong_kinh_dai": duong_kinh_dai,
            "thanh_tren": danh_sach_duong_kinh if o_tren else [],
            "thanh_duoi": [] if o_tren else danh_sach_duong_kinh,
        }
    yeu_cau = (
        f"Vẽ 1 mặt cắt ngang cho '{p.ten}/{vt.vi_tri}'. Gọi tool ve_mat_cat với ĐÚNG các tham số sau "
        f"(SAO CHÉP NGUYÊN VĂN, không tự đổi số liệu):\n```json\n{json.dumps(du_lieu_tool, ensure_ascii=False)}\n```"
    )
    return yeu_cau, du_lieu_tool


def _ve_va_kiem_chung_1_mat_cat(
    nha_cung_cap: agent.NhaCungCapChat, phien_cad: PhienCAD, p, vt,
    hoi_nguoi_dung: HamHoiNguoiDung, bo_dem_kiem_chung: BoDemVongLap, quan_sat: HamQuanSat | None,
) -> bool:
    """Vẽ 1 mặt cắt rồi kiểm chứng, TỰ SỬA nếu lệch (đến khi hết
    `bo_dem_kiem_chung`). Trả True nếu cuối cùng đạt."""
    yeu_cau_ve, du_lieu_ve = _mo_ta_yeu_cau_ve_mat_cat(p, vt, cover=25.0 if p.loai == "dam" else 40.0, duong_kinh_dai=8.0)
    ket_qua_ve = drawing_agent.chay_drawing_agent(nha_cung_cap, yeu_cau_ve, phien_cad, hoi_nguoi_dung)
    _bao(quan_sat, "drawing", f"{p.ten}/{vt.vi_tri}", ket_qua_ve)

    nhan_ky_vong = ["I-I"] if p.loai == "cot" else ["I-I"]  # 1 mặt cắt/lần gọi — luôn đúng 1 nhãn tiêu chuẩn
    while True:
        yeu_cau_kc = (
            f"Kiểm chứng mặt cắt vừa vẽ cho '{p.ten}/{vt.vi_tri}'. Gọi kiem_chung_ban_ve với "
            f"loai_kiem_tra='mat_cat', b_ky_vong={du_lieu_ve['b']}, h_ky_vong={du_lieu_ve['h']}."
        )
        ket_qua_kc = verification_agent.chay_verification_agent(
            nha_cung_cap, yeu_cau_kc, phien_cad, bo_dem_kiem_chung, hoi_nguoi_dung,
        )
        _bao(quan_sat, "verification", f"{p.ten}/{vt.vi_tri}", ket_qua_kc)

        goi_kiem_chung = [t for t in ket_qua_kc.nhat_ky_tool if t["ten"] == "kiem_chung_ban_ve"]
        if not goi_kiem_chung:
            return False  # agent không gọi tool (bất thường) — coi như chưa xác nhận đạt
        kq = goi_kiem_chung[-1]["ket_qua"]
        if kq.get("dat"):
            return True
        if kq.get("het_luot_kiem_chung"):
            return False
        if "vi_pham" not in kq:
            # kiem_chung_ban_ve TỰ LỖI (khác "chưa đạt" hợp lệ — vd lỗi COM
            # thoáng qua khi đọc `.Coordinates` không tự phục hồi được dù đã
            # có _thu_lai_khi_com_ban ở verify_drawing.py) — dict trả về chỉ
            # có "loi", KHÔNG có "vi_pham"/"dat", nên hàm kiem_chung_ban_ve
            # (verification_agent.py) chưa kịp chạy tới đoạn tăng bộ đếm
            # "kiem_chung_ve" (nó crash TRƯỚC đoạn đó). LỖI THẬT đã gặp: nếu
            # không tự tăng bộ đếm ở đây, vòng lặp `while True` phía trên có
            # thể lặp VÔ HẠN khi lỗi COM cứ lặp lại y hệt mỗi lần — không bao
            # giờ tới nhánh "het_luot_kiem_chung" để dừng đúng cách.
            con_duoc = bo_dem_kiem_chung.ghi_nhan_1_lan_thu("kiem_chung_ve")
            if not con_duoc:
                return False
            continue  # thử đọc lại bản vẽ (KHÔNG yêu cầu vẽ lại — không biết sai chỗ nào, chỉ là lỗi đọc thoáng qua)
        # Còn lượt — yêu cầu Drawing Agent sửa đúng vi_pham rồi vẽ lại.
        yeu_cau_sua = (
            f"Verification Agent báo mặt cắt '{p.ten}/{vt.vi_tri}' CHƯA ĐẠT, vi phạm: {kq.get('vi_pham')}. "
            f"Sửa đúng chỗ sai rồi gọi lại ve_mat_cat với tham số đã điều chỉnh (tham số gốc:\n"
            f"```json\n{json.dumps(du_lieu_ve, ensure_ascii=False)}\n```)."
        )
        ket_qua_ve = drawing_agent.chay_drawing_agent(nha_cung_cap, yeu_cau_sua, phien_cad, hoi_nguoi_dung)
        _bao(quan_sat, "drawing", f"{p.ten}/{vt.vi_tri} (sửa)", ket_qua_ve)


# ---------------------------------------------------------------------------
# Bước 4 — lắp ráp mặt đứng khung + xuất bản vẽ + kiểm chứng tổng thể.
# ---------------------------------------------------------------------------


def _chieu_dai_co_neo_noi(chieu_dai_goc: float, loai: str, vi_tri: list) -> float:
    """Cộng thêm đoạn neo/nối chồng vào chiều dài CẮT THÉP thật — LỖI THẬT đã
    gặp: `tinh_neo_noi` ĐÃ tính đúng L_an/L_lap theo mục 6 RULES_TCVN5574.md
    (Rule Engine Agent ĐÃ gọi tool này, kết quả ĐÃ lưu ở `KetQuaViTriDaThietKe
    .neo_noi`), nhưng `chieu_dai` dùng cho bảng thống kê/mặt đứng khung trước
    đây lấy THẲNG `goc.chieu_dai` (= khoảng cách trục/hiệu cao độ thuần hình
    học), BỎ QUA hoàn toàn kết quả neo_noi đã tính — không phải thiếu công
    thức (công thức đã có sẵn, đã tính), mà là dữ liệu tính ra rồi KHÔNG được
    dùng tới. Xác nhận qua đối chiếu trực tiếp bản vẽ mẫu: cột tầng cao
    3200mm thật nhưng bản mẫu ghi L=4700mm (dài hơn ~1500mm — đúng tầm 1 đoạn
    nối chồng Ø16-18) vì thép phải kéo dài qua sàn chờm lên đoạn cột tầng
    trên, không cắt đúng bằng chiều cao tầng.

    Giả định cách cộng (CẦN XÁC NHẬN LẠI khi có tài liệu chuẩn mới — đây là
    lựa chọn hợp lý nhất rút ra từ mục 6/7 RULES_TCVN5574.md, không phải suy
    đoán tuỳ tiện): CỘT cộng 1×L_lap (thép đoạn dưới vuốt lên chờm vào đoạn
    trên, mục 7 "Cốt dọc cột dưới vuốt liên tục lên chờ nối cột trên"); DẦM
    cộng 2×L_an (neo vào CẢ 2 đầu gối, mục 6.2). Lấy GIÁ TRỊ LỚN NHẤT trong
    các vị trí của phần tử (nhiều vị trí có thể có L_an/L_lap khác nhau do
    khác đường kính — dùng giá trị lớn nhất để AN TOÀN, cùng tinh thần "thiết
    kế chung theo giá trị lớn hơn" đã áp dụng ở mục 10.6 nguyên tắc 1)."""
    if not vi_tri:
        return chieu_dai_goc
    if loai == "cot":
        gia_tri = [vt.neo_noi.get("L_lap") for vt in vi_tri if vt.neo_noi.get("L_lap")]
        if not gia_tri:
            return chieu_dai_goc
        return chieu_dai_goc + max(gia_tri)
    if loai == "dam":
        gia_tri = [vt.neo_noi.get("L_an") for vt in vi_tri if vt.neo_noi.get("L_an")]
        if not gia_tri:
            return chieu_dai_goc
        return chieu_dai_goc + 2 * max(gia_tri)
    return chieu_dai_goc


def _du_lieu_lap_rap(bo_du_lieu: BoDuLieuKhungChuanHoa, ket_qua_phan_tu: list[KetQuaPhanTu]) -> dict:
    # Lọc theo rule_engine_dat (KHÔNG phải trang_thai == "dat"): tại thời
    # điểm gọi hàm này, mặt cắt CHƯA được vẽ (xem chay_toan_bo_khung) — bản
    # vẽ bố trí khung chỉ cần phương án thép đã chọn xong, không phụ thuộc
    # việc từng mặt cắt đã qua kiểm chứng hay chưa.
    phan_tu_dat = {kq.ten_phan_tu: kq.phuong_an_thep for kq in ket_qua_phan_tu if kq.rule_engine_dat}
    phan_tu_goc = {p.ten: p for p in bo_du_lieu.phan_tu}

    phan_tu_json = []
    for ten, phuong_an in phan_tu_dat.items():
        goc = phan_tu_goc.get(ten)
        if goc is None:
            continue
        phan_tu_json.append(
            {
                "ten": ten, "loai": phuong_an.loai, "b": phuong_an.b, "h": phuong_an.h,
                "truc": goc.truc, "tang": goc.tang, "mac_be_tong": goc.mac_be_tong, "nhom_thep_doc": goc.nhom_thep_doc,
                # chieu_dai (nhịp dầm/chiều cao đoạn cột) — LỖI THẬT đã gặp: bị
                # rớt mất hoàn toàn ở khâu trích BoDuLieuKhungChuanHoa
                # (input_adapter_agent.trich_bo_du_lieu_chuan_hoa không truyền
                # field này dù dữ liệu ETABS/generic đã có sẵn) khiến bảng
                # thống kê thép (_xay_dong_thong_ke ở drawing_agent.py, vốn bỏ
                # qua mọi phần tử KHÔNG có 'chieu_dai') luôn rỗng — xác nhận
                # qua đọc lại PDF xuất ra thật, bảng trống hoàn toàn.
                #
                # Cộng thêm đoạn neo/nối chồng đã tính sẵn (mục 6 RULES_
                # TCVN5574.md, xem _chieu_dai_co_neo_noi) — KHÔNG dùng
                # goc.chieu_dai trần trụi nữa.
                "chieu_dai": _chieu_dai_co_neo_noi(goc.chieu_dai, phuong_an.loai, phuong_an.vi_tri) if goc.chieu_dai else goc.chieu_dai,
                "vi_tri": [
                    {
                        "vi_tri": vt.vi_tri, "mo_ta_thep": vt.thep_doc.get("mo_ta", "?"),
                        "As_yc": next((v.As_yc for v in goc.vi_tri if v.vi_tri == vt.vi_tri), None),
                        # "thanh" — chuẩn hoá format cho MỌI loại phần tử.
                        # chon_thep_doc(loai='cot') trả {"duong_kinh",
                        # "tong_so_thanh",...} (KHÔNG có key "thanh" như dầm) —
                        # LỖI THẬT đã gặp: nếu chỉ đọc thẳng
                        # vt.thep_doc.get("thanh", []) thì cột LUÔN ra [] rỗng,
                        # khiến cột biến mất khỏi bảng thống kê (chỉ dầm có
                        # dòng) — tự tổng hợp lại 1 dòng "thanh" tương đương
                        # cho cột khi thiếu key này.
                        "thanh": vt.thep_doc.get("thanh") or (
                            [{"duong_kinh": vt.thep_doc["duong_kinh"], "so_luong": vt.thep_doc["tong_so_thanh"]}]
                            if "tong_so_thanh" in vt.thep_doc else []
                        ),
                    }
                    for vt in phuong_an.vi_tri
                ],
            }
        )
    return {"toa_do_truc": bo_du_lieu.toa_do_truc, "cao_do_moc": bo_du_lieu.cao_do_moc, "phan_tu": phan_tu_json}


def _lap_rap_va_xuat_ban_ve(
    nha_cung_cap: agent.NhaCungCapChat, phien_cad: PhienCAD, bo_du_lieu: BoDuLieuKhungChuanHoa,
    ket_qua_phan_tu: list[KetQuaPhanTu], ten_khung: str, hoi_nguoi_dung: HamHoiNguoiDung,
    bo_dem_kiem_chung: BoDemVongLap, quan_sat: HamQuanSat | None,
) -> tuple[dict | None, Any]:
    du_lieu = _du_lieu_lap_rap(bo_du_lieu, ket_qua_phan_tu)
    if not du_lieu["phan_tu"]:
        return None, None  # không có phần tử nào đạt — không có gì để lắp ráp

    yeu_cau = (
        f"Lắp ráp mặt đứng khung tổng thể cho khung '{ten_khung}'. Gọi tool lap_rap_mat_dung_khung với "
        f"ĐÚNG các tham số sau (SAO CHÉP NGUYÊN VĂN toa_do_truc/cao_do_moc/phan_tu, không tự gõ lại từ "
        f"trí nhớ — dữ liệu này CHÍNH XÁC, đã qua Rule Engine Agent):\n"
        f"```json\n{json.dumps(du_lieu, ensure_ascii=False)}\n```\n"
        f"Sau đó gọi xuat_ban_ve với ten_file='{ten_khung.upper()}'."
    )
    ket_qua = drawing_agent.chay_drawing_agent(nha_cung_cap, yeu_cau, phien_cad, hoi_nguoi_dung, so_lan_goi_toi_da=6)
    _bao(quan_sat, "drawing", "lap_rap_mat_dung_khung", ket_qua)

    goi_lap_rap = [t for t in ket_qua.nhat_ky_tool if t["ten"] == "lap_rap_mat_dung_khung" and "loi" not in t["ket_qua"]]
    goi_xuat = [t for t in ket_qua.nhat_ky_tool if t["ten"] == "xuat_ban_ve" and "loi" not in t["ket_qua"]]
    ket_qua_lap_rap = goi_lap_rap[-1]["ket_qua"] if goi_lap_rap else None
    ket_qua_xuat = goi_xuat[-1]["ket_qua"] if goi_xuat else None

    if ket_qua_lap_rap is None:
        return None, ket_qua_xuat

    # Kiểm chứng tổng thể.
    ten_truc = sorted(bo_du_lieu.toa_do_truc, key=lambda t: bo_du_lieu.toa_do_truc[t])
    yeu_cau_kc = (
        f"Kiểm chứng bản vẽ tổng thể khung '{ten_khung}' vừa lắp ráp. Gọi kiem_chung_ban_ve với "
        f"loai_kiem_tra='mat_dung_khung', so_cot_ky_vong={ket_qua_lap_rap.get('so_cot')}, "
        f"so_dam_ky_vong={ket_qua_lap_rap.get('so_dam')}, "
        f"so_ky_hieu_ky_vong={ket_qua_lap_rap.get('so_ky_hieu_ky_vong', 0)}, "
        f"ten_truc_ky_vong={json.dumps(ten_truc, ensure_ascii=False)}."
    )
    ket_qua_kc = verification_agent.chay_verification_agent(
        nha_cung_cap, yeu_cau_kc, phien_cad, bo_dem_kiem_chung, hoi_nguoi_dung,
    )
    _bao(quan_sat, "verification", "mat_dung_khung", ket_qua_kc)
    goi_kc = [t for t in ket_qua_kc.nhat_ky_tool if t["ten"] == "kiem_chung_ban_ve"]
    ket_qua_kiem_chung = goi_kc[-1]["ket_qua"] if goi_kc else {"dat": False, "vi_pham": ["Verification Agent không gọi tool."]}

    return ket_qua_kiem_chung, ket_qua_xuat


_KHOANG_CACH_AN_TOAN_MAT_CAT_MM = 2000.0


def _tinh_y_mat_cat_an_toan(
    hop_gioi_han: tuple[float, float, float, float] | None,
    khoang_cach_an_toan: float = _KHOANG_CACH_AN_TOAN_MAT_CAT_MM,
) -> float | None:
    """Cao độ Y an toàn để bắt đầu vẽ hàng mặt cắt — HẲN DƯỚI mọi thứ đã vẽ
    (mặt đứng khung + bảng thống kê + khung tên), tránh chồng đè như lỗi thật
    đã gặp (xem PhienCAD.y_mat_cat). `hop_gioi_han` là bounding box THẬT của
    ModelSpace (min_x, min_y, max_x, max_y) — None nếu ModelSpace rỗng (chưa
    vẽ gì, hàm trả None, gọi nơi KHÔNG đổi y_mat_cat, giữ mặc định 0.0)."""
    if hop_gioi_han is None:
        return None
    _, min_y, _, _ = hop_gioi_han
    return min_y - khoang_cach_an_toan


def _xuat_ban_ve_lai(
    nha_cung_cap: agent.NhaCungCapChat, phien_cad: PhienCAD, ten_khung: str,
    hoi_nguoi_dung: HamHoiNguoiDung, quan_sat: HamQuanSat | None,
) -> Any:
    """Xuất lại PDF/DWG (CÙNG tên file, ghi đè) sau khi đã vẽ thêm mặt cắt
    chi tiết vào Document — để file cuối cùng có ĐỦ cả bản vẽ bố trí khung
    (đã xuất sớm ở `_lap_rap_va_xuat_ban_ve`) LẪN mặt cắt, trên CÙNG 1 tờ.
    Gọi lại Drawing Agent (không tự ghi PDF/DWG trực tiếp ở tầng pipeline)
    để giữ đúng nguyên tắc "pipeline.py không tự vẽ" của file này."""
    yeu_cau = f"Xuất lại bản vẽ hiện tại (đã có đủ mặt cắt chi tiết). Gọi tool xuat_ban_ve với ten_file='{ten_khung.upper()}'."
    ket_qua = drawing_agent.chay_drawing_agent(nha_cung_cap, yeu_cau, phien_cad, hoi_nguoi_dung, so_lan_goi_toi_da=3)
    _bao(quan_sat, "drawing", "xuat_ban_ve (cuối)", ket_qua)
    goi_xuat = [t for t in ket_qua.nhat_ky_tool if t["ten"] == "xuat_ban_ve" and "loi" not in t["ket_qua"]]
    return goi_xuat[-1]["ket_qua"] if goi_xuat else None


# ---------------------------------------------------------------------------
# Hàm điều phối cấp cao DUY NHẤT — vòng lặp ngoài cùng (per phần tử).
# ---------------------------------------------------------------------------


def chay_toan_bo_khung(
    nha_cung_cap: agent.NhaCungCapChat,
    duong_dan_file: str,
    hoi_nguoi_dung: HamHoiNguoiDung,
    thu_muc_xuat_ban_ve: str,
    ten_khung: str = "khung",
    gioi_han_vong_lap: dict[str, int] | None = None,
    quan_sat: HamQuanSat | None = None,
) -> KetQuaKhung:
    """Chạy TOÀN BỘ pipeline cho 1 file dữ liệu — Input Adapter Agent (1 lần)
    → Rule Engine Agent cho MỌI phần tử → lắp ráp + xuất bản vẽ BỐ TRÍ KHUNG
    NGAY (bản vẽ chính, người dùng cần xem trước) → rồi mới vẽ + kiểm chứng
    TỪNG MẶT CẮT chi tiết (bản vẽ bổ sung, vẽ sau) → xuất lại bản vẽ lần cuối
    để file có đủ cả hai. Thứ tự này KHÁC với mục 5 `docs/TONGQUAN_AI_AGENT.md`
    (vốn vẽ mặt cắt trước rồi mới lắp ráp) — đổi theo yêu cầu thực tế người
    dùng: bản vẽ bố trí khung phải có SỚM, không phải chờ hết ~36 mặt cắt
    (mỗi mặt cắt có thể tự sửa tới 3 lần) mới thấy được bản vẽ chính.

    1 phần tử lỗi/leo thang KHÔNG làm dừng toàn bộ batch — các phần tử khác
    vẫn được xử lý tiếp, kết quả giữ trong `KetQuaKhung.ket_qua_phan_tu`."""
    ket_qua_khung = KetQuaKhung(ten_khung=ten_khung)

    bo_du_lieu = _chay_buoc_input_adapter(nha_cung_cap, duong_dan_file, hoi_nguoi_dung, quan_sat)
    if bo_du_lieu is None:
        ket_qua_khung.ghi("Input Adapter Agent KHÔNG hoàn tất (thiếu dữ liệu hoặc chưa suy luận xong hình học) — dừng pipeline.")
        return ket_qua_khung
    ket_qua_khung.du_lieu_dau_vao = bo_du_lieu
    ket_qua_khung.ghi(f"Input Adapter Agent: {len(bo_du_lieu.phan_tu)} phần tử, toa_do_truc={bo_du_lieu.toa_do_truc}, cao_do_moc={bo_du_lieu.cao_do_moc}")

    app = backend_com.ket_noi_autocad()
    doc = backend_com.tao_ban_ve_moi(app)
    phien_cad = PhienCAD(app=app, doc=doc, thu_muc_xuat=thu_muc_xuat_ban_ve)

    # Bước A — Rule Engine Agent cho MỌI phần tử trước (chưa vẽ gì cả). Đây
    # là bước duy nhất bản vẽ bố trí khung phụ thuộc vào (chọn xong thép),
    # không cần chờ mặt cắt.
    for p in bo_du_lieu.phan_tu:
        phuong_an = _chay_buoc_rule_engine(
            nha_cung_cap, ten_khung, p, hoi_nguoi_dung, gioi_han_vong_lap, quan_sat,
        )
        if not phuong_an.moi_vi_tri_dat:
            ket_qua_khung.ket_qua_phan_tu.append(
                KetQuaPhanTu(ten_phan_tu=p.ten, loai=p.loai, trang_thai="leo_thang", phuong_an_thep=phuong_an,
                             ghi_chu="Chưa đạt tự kiểm tra cho mọi vị trí — xem vi_pham từng vị trí.")
            )
            ket_qua_khung.ghi(f"Phần tử '{p.ten}': LEO THANG (chưa đạt tự kiểm tra) — KHÔNG đưa vào bản vẽ bố trí khung.")
            continue
        ket_qua_khung.ket_qua_phan_tu.append(
            KetQuaPhanTu(ten_phan_tu=p.ten, loai=p.loai, trang_thai="cho_ve_mat_cat", phuong_an_thep=phuong_an, rule_engine_dat=True)
        )
        ket_qua_khung.ghi(f"Phần tử '{p.ten}': Rule Engine ĐẠT ({len(phuong_an.vi_tri)} vị trí) — chờ vẽ mặt cắt.")

    # Bước B — lắp ráp + xuất BẢN VẼ BỐ TRÍ KHUNG ngay (ưu tiên số 1 theo yêu
    # cầu người dùng), dùng mọi phần tử đã có rule_engine_dat=True — KHÔNG
    # chờ mặt cắt.
    bo_dem_khung = BoDemVongLap(gioi_han=dict(gioi_han_vong_lap) if gioi_han_vong_lap else BoDemVongLap().gioi_han)
    ket_qua_kiem_chung, ket_qua_xuat = _lap_rap_va_xuat_ban_ve(
        nha_cung_cap, phien_cad, bo_du_lieu, ket_qua_khung.ket_qua_phan_tu, ten_khung, hoi_nguoi_dung, bo_dem_khung, quan_sat,
    )
    if ket_qua_kiem_chung is not None:
        from .shared.hop_dong_du_lieu import KetQuaKiemChung

        ket_qua_khung.kiem_chung_tong_the = KetQuaKiemChung(
            dat=bool(ket_qua_kiem_chung.get("dat")), vi_pham=ket_qua_kiem_chung.get("vi_pham", []),
        )
        ket_qua_khung.ghi(f"Kiểm chứng bản vẽ bố trí khung: {'ĐẠT' if ket_qua_kiem_chung.get('dat') else 'CHƯA ĐẠT'} — {ket_qua_kiem_chung.get('vi_pham')}")
    else:
        ket_qua_khung.ghi("KHÔNG có phần tử nào đạt Rule Engine — không lắp ráp được bản vẽ bố trí khung.")
    if ket_qua_xuat is not None:
        ket_qua_khung.duong_dan_pdf = ket_qua_xuat.get("duong_dan_pdf")
        ket_qua_khung.duong_dan_dwg = ket_qua_xuat.get("duong_dan_dwg")
        ket_qua_khung.ghi(f"Đã xuất bản vẽ bố trí khung: {ket_qua_khung.duong_dan_pdf}, {ket_qua_khung.duong_dan_dwg}")

    # Đặt hàng mặt cắt hẳn xuống DƯỚI toàn bộ những gì vừa vẽ ở Bước B (mặt
    # đứng khung + bảng thống kê + khung tên) — LỖI THẬT đã gặp: PhienCAD.
    # y_mat_cat mặc định 0.0 TRÙNG đúng vùng y=0 (cao độ Mong) của mặt đứng
    # khung, khiến mặt cắt chồng đè lên góc dưới-trái mặt đứng khung (xem
    # giải thích đầy đủ ở docstring PhienCAD.y_mat_cat). Tính lại bằng bounding
    # box THẬT của ModelSpace ngay sau khi Bước B vẽ xong — không hard-code
    # theo 1 giá trị cao độ cụ thể nào (mỗi công trình cao độ khác nhau).
    y_mat_cat_moi = _tinh_y_mat_cat_an_toan(backend_com.hop_gioi_han_modelspace(phien_cad.doc))
    if y_mat_cat_moi is not None:
        phien_cad.y_mat_cat = y_mat_cat_moi

    # Bước C — SAU KHI đã có bản vẽ bố trí khung, mới vẽ + kiểm chứng từng
    # mặt cắt chi tiết cho các phần tử đã đạt Rule Engine (vẽ thêm vào CÙNG
    # Document, không đè lên bản vẽ bố trí khung — xem PhienCAD/lap_rap_mat_dung_khung).
    phan_tu_goc_theo_ten = {p.ten: p for p in bo_du_lieu.phan_tu}
    co_mat_cat_moi = False
    for kq_pt in ket_qua_khung.ket_qua_phan_tu:
        if not kq_pt.rule_engine_dat:
            continue
        phuong_an = kq_pt.phuong_an_thep
        p = phan_tu_goc_theo_ten[kq_pt.ten_phan_tu]
        dat_het_mat_cat = True
        for vt in phuong_an.vi_tri:
            bo_dem = BoDemVongLap(gioi_han=dict(gioi_han_vong_lap) if gioi_han_vong_lap else BoDemVongLap().gioi_han)
            dat = _ve_va_kiem_chung_1_mat_cat(nha_cung_cap, phien_cad, p, vt, hoi_nguoi_dung, bo_dem, quan_sat)
            dat_het_mat_cat = dat_het_mat_cat and dat
        co_mat_cat_moi = True
        kq_pt.trang_thai = "dat" if dat_het_mat_cat else "leo_thang"
        if not dat_het_mat_cat:
            kq_pt.ghi_chu = "Rule Engine đạt nhưng ít nhất 1 mặt cắt chưa qua kiểm chứng — xem log 'drawing'/'verification'."
        ket_qua_khung.ghi(f"Phần tử '{kq_pt.ten_phan_tu}': mặt cắt {kq_pt.trang_thai.upper()} ({len(phuong_an.vi_tri)} mặt cắt).")

    # Bước D — xuất lại bản vẽ lần cuối (ghi đè CÙNG file) để có đủ cả bản vẽ
    # bố trí khung LẪN mặt cắt chi tiết trên cùng 1 tờ.
    if co_mat_cat_moi:
        ket_qua_xuat_cuoi = _xuat_ban_ve_lai(nha_cung_cap, phien_cad, ten_khung, hoi_nguoi_dung, quan_sat)
        if ket_qua_xuat_cuoi is not None:
            ket_qua_khung.duong_dan_pdf = ket_qua_xuat_cuoi.get("duong_dan_pdf")
            ket_qua_khung.duong_dan_dwg = ket_qua_xuat_cuoi.get("duong_dan_dwg")
            ket_qua_khung.ghi(f"Đã xuất lại bản vẽ đầy đủ (bố trí khung + mặt cắt): {ket_qua_khung.duong_dan_pdf}, {ket_qua_khung.duong_dan_dwg}")

    return ket_qua_khung
