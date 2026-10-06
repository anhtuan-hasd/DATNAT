"""
Đọc trực tiếp báo cáo XUẤT ETABS THẬT — khác hẳn model "1 sheet phẳng, mỗi
dòng là 1 vị trí" mà `adapter.py`/`heuristics.py` xử lý. Một báo cáo ETABS
thật xuất ra NHIỀU BẢNG QUAN HỆ (Grid Lines, Story Definitions, Joint
Coordinates, Connectivity - Frame, Frame Section Assignments, Frame Props,
Material Props, và các bảng "Concrete Design Summary" theo TCVN/SP)
— phải JOIN theo "Frame" ID mới dựng lại được 1 phần tử hoàn chỉnh.

Mỗi bảng ETABS thật có đúng 3 dòng đầu cố định trước khi tới dữ liệu:
dòng 0 = "TABLE:  <tên bảng>", dòng 1 = tên cột thật, dòng 2 = đơn vị.
`readers.doc_excel` (đọc kiểu sheet phẳng) lấy nhầm dòng 0 làm tên cột, ra
toàn "Unnamed: N" — đây là lý do file ETABS thật KHÔNG đọc được qua đường
`adapter.xac_dinh_anh_xa` thông thường (phát hiện qua chạy thật với
`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx`).

HẠN CHẾ ĐÃ BIẾT: bảng "Concrete Design Summary" cho DẦM (vd
"Conc Sum2 - SP 63-13330-2012") chỉ xuất "VRebar" — diện tích cốt đai
ĐÃ THIẾT KẾ trên 1m dài (Asw/s, ETABS tự tính) — KHÔNG xuất lực cắt Q thô
(bảng "Element Forces" không có trong bộ báo cáo Concrete Design). Vì vậy
với dữ liệu đọc qua module này, `NoiLuc.Q` của dầm luôn là None — pipeline
KHÔNG tự chạy lại `tinh_cot_dai` (mục 3, cần Q thô) cho dầm nguồn ETABS
thật, chỉ chọn cốt đai đạt đúng As_yc/vrebar_yc đã ETABS tính sẵn (đúng vai
trò "ETABS đã tính, agent chỉ nhận kết quả" — TONGQUAN_AI_AGENT.md mục 3).
Cột thì có đủ N/M thật (bảng PMM Summary) nên vẫn chạy đầy đủ `tu_kiem_tra`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import BoDuLieuKhung, DonViLucGoc, DuLieuViTri, LoaiCauKien, NoiLuc, PhanTuKhung, TietDien

# Tên sheet cố định theo báo cáo ETABS chuẩn — 1 vài bảng có thể đổi tên theo
# phiên bản/tuỳ chỉnh xuất báo cáo nên dò theo TIỀN TỐ cho các bảng dễ đổi tên.
_SHEET_GRID = "Grid Lines"
_SHEET_STORY = "Story Definitions"
_SHEET_JOINT = "Joint Coordinates"
_SHEET_CONN = "Connectivity - Frame"
_SHEET_SECTION_ASSIGN = "Frame Section Assignments"
_SHEET_PROPS_GENERAL = "Frame Props 01 - General"
_SHEET_MAT_CONCRETE = "MatProp 03b - Concrete Data"
_SHEET_MAT_STEEL = "MatProp 03a - Steel Data"
_TIEN_TO_PROPS_BEAM = "Frame Props 03 - Concrete Beam"
_TIEN_TO_PROPS_COL = "FrameProps06-ConcCol"
_TIEN_TO_SUM_DAM = "Conc Sum2"  # bảng tổng hợp thiết kế DẦM (uốn/cắt theo mặt cắt)
_TIEN_TO_SUM_COT = "ConcSum1"  # bảng tổng hợp thiết kế CỘT (PMM — nén lệch tâm)

_CAC_SHEET_NHAN_DIEN = {_SHEET_GRID, _SHEET_JOINT, _SHEET_CONN, _SHEET_SECTION_ASSIGN}


def nhan_dien_file_etabs_that(duong_dan: Path) -> bool:
    """True nếu file có đủ các sheet đặc trưng của báo cáo ETABS thật (đa
    bảng quan hệ) — dùng để lớp gọi (webapp) quyết định rẽ sang
    `doc_etabs_thuc` thay vì đường ánh xạ 1-sheet-phẳng thông thường."""
    try:
        ten_sheet = set(pd.ExcelFile(duong_dan).sheet_names)
    except Exception:
        return False
    return _CAC_SHEET_NHAN_DIEN.issubset(ten_sheet)


def _doc_bang(duong_dan: Path, ten_sheet: str) -> pd.DataFrame:
    """Đọc 1 bảng ETABS thật — bỏ dòng 0 ("TABLE: ...") và dòng 2 (đơn vị),
    dùng dòng 1 (tên cột thật) làm header."""
    return pd.read_excel(duong_dan, sheet_name=ten_sheet, skiprows=[0, 2], header=0)


def _tim_sheet_theo_tien_to(ten_cac_sheet: list[str], tien_to: str) -> str | None:
    return next((s for s in ten_cac_sheet if s.startswith(tien_to)), None)


def _tim_ten_gan_nhat(gia_tri: float, bang_gia_tri: dict[str, float], dung_sai: float = 1.0) -> str | None:
    """So khớp toạ độ (mm) với tên trục/tầng đã khai báo — dùng dung sai nhỏ
    để tránh lệch do sai số làm tròn float khi đổi đơn vị m -> mm."""
    for ten, gt in bang_gia_tri.items():
        if abs(gt - gia_tri) < dung_sai:
            return ten
    return None


def doc_etabs_thuc(duong_dan: Path) -> tuple[BoDuLieuKhung, dict[str, float], dict[str, float]]:
    """Đọc + JOIN toàn bộ báo cáo ETABS thật thành `BoDuLieuKhung` — cùng
    model nội bộ mà `adapter.chuan_hoa_bang` tạo ra, nên MỌI code phía sau
    (Rule Engine, Agent, khung_ve, webapp) dùng lại y nguyên, không cần biết
    dữ liệu đến từ đường nào.

    Trả về THÊM `toa_do_truc`/`cao_do_moc` (mm) — 2 giá trị này vốn ĐÃ được
    tính CHÍNH XÁC ở đây từ bảng "Grid Lines"/"Story Definitions" thật của
    ETABS (không phải suy luận gián tiếp như `input_adapter/hinh_hoc.py`,
    vốn chỉ cần khi nguồn dữ liệu KHÔNG có sẵn lưới trục/tầng tường minh) —
    trước đây hàm này TÍNH RỒI BỎ (chỉ dùng nội bộ để gán tên truc/tang cho
    từng phần tử qua `_tim_ten_gan_nhat`), không trả ra ngoài, nên
    Input Adapter Agent không có cách nào lấy lại 2 giá trị này cho ETABS
    nguồn thật — phát hiện khi nối `agents/input_adapter_agent.py` vào
    module này (CHANGE_REQUESTS.md mục 5: không hard-code toạ độ, nhưng cũng
    không được suy luận LẠI những gì ETABS đã cho biết chính xác)."""
    xl = pd.ExcelFile(duong_dan)
    ten_cac_sheet = xl.sheet_names

    grid = _doc_bang(duong_dan, _SHEET_GRID)
    story = _doc_bang(duong_dan, _SHEET_STORY)
    joint = _doc_bang(duong_dan, _SHEET_JOINT)
    conn = _doc_bang(duong_dan, _SHEET_CONN)
    section_assign = _doc_bang(duong_dan, _SHEET_SECTION_ASSIGN)
    props_general = _doc_bang(duong_dan, _SHEET_PROPS_GENERAL)

    ten_beam = _tim_sheet_theo_tien_to(ten_cac_sheet, _TIEN_TO_PROPS_BEAM)
    ten_col = _tim_sheet_theo_tien_to(ten_cac_sheet, _TIEN_TO_PROPS_COL)
    ten_sum_dam = _tim_sheet_theo_tien_to(ten_cac_sheet, _TIEN_TO_SUM_DAM)
    ten_sum_cot = _tim_sheet_theo_tien_to(ten_cac_sheet, _TIEN_TO_SUM_COT)

    props_beam = _doc_bang(duong_dan, ten_beam) if ten_beam else None
    props_col = _doc_bang(duong_dan, ten_col) if ten_col else None
    sum_dam = _doc_bang(duong_dan, ten_sum_dam) if ten_sum_dam else None
    sum_cot = _doc_bang(duong_dan, ten_sum_cot) if ten_sum_cot else None

    # 1) Lưới trục theo phương X (khung phẳng chỉ quan tâm 1 phương) -> mm
    grid_x = grid[grid["AxisDir"] == "X"]
    toa_do_truc = {str(r["GridID"]): float(r["XRYZCoord"]) * 1000 for _, r in grid_x.iterrows()}

    # 2) Cao độ mốc tầng -> mm
    cao_do_tang = {str(r["Name"]): float(r["Elevation"]) * 1000 for _, r in story.iterrows()}

    # 3) Toạ độ joint (X, Z) -> mm
    toa_do_joint = {int(r["Joint"]): (float(r["GlobalX"]) * 1000, float(r["GlobalZ"]) * 1000) for _, r in joint.iterrows()}

    # 4) Tiết diện: SectionName -> (mác bê tông, b=t2, h=t3) — t3 là phương
    # uốn chính (mặt phẳng khung), khớp đúng quy ước "h chịu uốn" đã dùng ở
    # src/orchestrator/khung_ve.py.
    tiet_dien_theo_section: dict[str, tuple[str, float, float]] = {
        str(r["SectionName"]): (str(r["Material"]), float(r["t2"]) * 1000, float(r["t3"]) * 1000)
        for _, r in props_general.iterrows()
    }

    # 5) Nhóm thép dọc/đai theo section (bảng riêng cho dầm/cột)
    nhom_thep_theo_section: dict[str, tuple[str, str]] = {}
    for bang_props in (props_beam, props_col):
        if bang_props is None:
            continue
        for _, r in bang_props.iterrows():
            nhom_thep_theo_section[str(r["SectionName"])] = (str(r["RebarMatL"]), str(r["RebarMatC"]))

    # 6) Kết nối: Frame -> (JointI, JointJ, chiều dài mm)
    ket_noi_theo_frame = {
        int(r["Frame"]): (int(r["JointI"]), int(r["JointJ"]), float(r["Length"]) * 1000) for _, r in conn.iterrows()
    }

    # 8) Frame -> tên tiết diện đã gán (DesignSect)
    section_theo_frame = {int(r["Frame"]): str(r["DesignSect"]) for _, r in section_assign.iterrows()}

    phan_tu: list[PhanTuKhung] = []

    if sum_cot is not None:
        for frame_id, nhom in sum_cot.groupby("Frame"):
            frame_id = int(frame_id)
            if frame_id not in ket_noi_theo_frame or frame_id not in section_theo_frame:
                continue
            section = section_theo_frame[frame_id]
            mac_be_tong, b, h = tiet_dien_theo_section.get(section, (None, None, None))
            nhom_doc, nhom_dai = nhom_thep_theo_section.get(section, (None, None))
            j1, j2, chieu_dai_cot = ket_noi_theo_frame[frame_id]
            x1, z1 = toa_do_joint[j1]
            x2, z2 = toa_do_joint[j2]
            truc = _tim_ten_gan_nhat(x1, toa_do_truc)
            tang1 = _tim_ten_gan_nhat(min(z1, z2), cao_do_tang)
            tang2 = _tim_ten_gan_nhat(max(z1, z2), cao_do_tang)

            hang = nhom.iloc[0]  # 1 dòng PMM đại diện (đã chọn nguy hiểm nhất)/cột
            N = abs(float(hang["PMMDemandN"]))  # ETABS: âm=nén — quy ước nội bộ N>0=nén
            M = float(hang["PMMDemandM"])
            As_yc = float(hang["PMMArea"]) * 1e6  # m² -> mm²

            phan_tu.append(
                PhanTuKhung(
                    ten=str(frame_id), loai=LoaiCauKien.COT,
                    tiet_dien=TietDien(b=b, h=h), mac_be_tong=mac_be_tong,
                    nhom_thep_doc=nhom_doc, nhom_thep_dai=nhom_dai,
                    tang=f"{tang1}_{tang2}" if tang1 and tang2 else None, truc=truc,
                    chieu_dai=chieu_dai_cot,  # mm — chiều cao đoạn cột, dùng cho hinh_hoc.py + bảng thống kê
                    du_lieu_vi_tri=[
                        DuLieuViTri(
                            vi_tri="dai_dien", As_yc=As_yc,
                            noi_luc=NoiLuc(M=abs(M), N=N, Q=None, to_hop_chi_phoi=str(hang["PMMCombo"])),
                        )
                    ],
                )
            )

    if sum_dam is not None:
        for frame_id, nhom in sum_dam.groupby("Frame"):
            frame_id = int(frame_id)
            if frame_id not in ket_noi_theo_frame or frame_id not in section_theo_frame:
                continue
            section = section_theo_frame[frame_id]
            mac_be_tong, b, h = tiet_dien_theo_section.get(section, (None, None, None))
            nhom_doc, nhom_dai = nhom_thep_theo_section.get(section, (None, None))
            j1, j2, L = ket_noi_theo_frame[frame_id]
            x1, z1 = toa_do_joint[j1]
            x2, _ = toa_do_joint[j2]
            truc1 = _tim_ten_gan_nhat(min(x1, x2), toa_do_truc)
            truc2 = _tim_ten_gan_nhat(max(x1, x2), toa_do_truc)
            tang = _tim_ten_gan_nhat(z1, cao_do_tang)

            du_lieu_vi_tri: list[DuLieuViTri] = []
            for _, hang in nhom.sort_values("Location").iterrows():
                loc = float(hang["Location"]) * 1000  # m -> mm, so với L (đã mm)
                as_top = float(hang["FTopArea"]) * 1e6
                as_bot = float(hang["FBotArea"]) * 1e6
                as_yc = max(as_top, as_bot)
                to_hop = hang["FTopCombo"] if as_top >= as_bot else hang["FBotCombo"]
                # Phân loại theo MẶT THÉP CHI PHỐI (trên=mô men âm=gối, dưới=mô
                # men dương=nhịp), KHÔNG chỉ theo vị trí — với nhịp ngắn (vd
                # nhịp B-C 1,5m) 2 mặt cắt "giữa nhịp"/"gối phải" có thể nằm ở
                # CÙNG toạ độ Location (ETABS chỉ báo 1 vị trí đại diện gần
                # cuối dầm cho cả 2 kiểm tra) — phải phân biệt bằng mặt chi
                # phối, nếu chỉ dùng ngưỡng vị trí sẽ gộp nhầm cả 2 thành 1 nhãn.
                if as_top >= as_bot:
                    vt = "goi_trai" if loc < L / 2 else "goi_phai"
                else:
                    vt = "giua_nhip"
                du_lieu_vi_tri.append(
                    DuLieuViTri(
                        vi_tri=vt, As_yc=as_yc,
                        # Q=None: bảng ETABS design summary không xuất Q thô cho
                        # dầm (chỉ có VRebar — Asw/s đã thiết kế sẵn) — xem
                        # docstring module. Không được LLM tự bịa Q để lấp chỗ
                        # trống này (đúng nguyên tắc đã thiết lập trong tools.py).
                        noi_luc=NoiLuc(M=None, N=0.0, Q=None, to_hop_chi_phoi=str(to_hop)),
                    )
                )

            phan_tu.append(
                PhanTuKhung(
                    ten=str(frame_id), loai=LoaiCauKien.DAM,
                    tiet_dien=TietDien(b=b, h=h), mac_be_tong=mac_be_tong,
                    nhom_thep_doc=nhom_doc, nhom_thep_dai=nhom_dai,
                    tang=tang, truc=f"{truc1}-{truc2}" if truc1 and truc2 else None,
                    chieu_dai=L,  # mm — nhịp dầm, dùng cho hinh_hoc.py + bảng thống kê
                    du_lieu_vi_tri=du_lieu_vi_tri,
                )
            )

    bo_du_lieu = BoDuLieuKhung(ten_khung=duong_dan.stem, don_vi_luc_goc=DonViLucGoc.KN_KNM, phan_tu=phan_tu)
    return bo_du_lieu, toa_do_truc, cao_do_tang
