#!/usr/bin/env python3
"""Sinh docs/agents/BAN_DO_PHU_NGUON_SANG_SKILL.md từ MUC_LUC_NGUON.md + NOI_DUNG_GOC.md.

Chạy từ thư mục gốc repo:
    python docs/agents/_nguon_tai_lieu_chon_thep/lap_ban_do_phu.py

Mỗi tiêu đề nguồn được gán một "nơi đi" theo quy tắc theo chương; mức phủ ("đầy đủ", "tóm tắt", "tham chiếu")
và lý do ghi rõ ở cột cuối. Không có mục nào bị bỏ im lặng: mục không có chỗ trong skill phải có dòng giải thích.
"""
import pathlib
import re
import sys

GOC = pathlib.Path(__file__).resolve().parents[3]
NGUON = GOC / "docs/agents/_nguon_tai_lieu_chon_thep"
RA = GOC / "docs/agents/BAN_DO_PHU_NGUON_SANG_SKILL.md"

CT = "huongdanchonthep"
M = {
    "00": f"{CT}/00_NGUYEN_TAC_VA_THU_TU_UU_TIEN.md",
    "01": f"{CT}/01_VAT_LIEU_HE_SO_DON_VI.md",
    "02": f"{CT}/02_DAM_16_BUOC.md",
    "03": f"{CT}/03_COT_14_BUOC.md",
    "04": f"{CT}/04_CAU_TAO_CHUNG.md",
    "05": f"{CT}/05_NUT_KHUNG.md",
    "06": f"{CT}/06_BO_TRI_THEO_CHIEU_DAI.md",
    "07": f"{CT}/07_KHANG_CHAN.md",
    "08": f"{CT}/08_BANG_QUYET_DINH_R1_R52_VA_PHAN_Q.md",
    "09": f"{CT}/09_RA_SOAT_PHAM_VI_XOAN_VI_DU_VA_SAI_KHAC.md",
    "ND": "huongdannhapdulieu/SKILL_NHAP_DU_LIEU_ETABS.md",
    "KC": "huongdankiemchung/SKILL_KIEM_CHUNG_KY_SU.md",
}
LY_DO_ND = ("Agent không chọn kích thước/không tính tải–tổ hợp (LLM không tính); giữ nguyên tắc, số liệu ví dụ và "
            "bảng quy ước để Input Adapter nhận ra dữ liệu bất thường và biết ETABS đã làm gì.")


def noi_di(so, tieu_de, chuong):
    """Trả (nơi đi, mức phủ, lý do) cho một tiêu đề."""
    t = tieu_de
    if chuong in (None, "0"):
        if so.startswith("0.4"):
            return M["00"] + "; " + M["ND"], "đầy đủ", "đơn vị và dấu dùng ở cả hai agent"
        return M["00"], "đầy đủ", "nguyên tắc tổng hợp, thứ tự ưu tiên nguồn, nhãn tin cậy"
    if chuong == "1":
        return M["ND"], "đầy đủ", "dữ liệu đầu vào = trách nhiệm Input Adapter"
    if chuong in ("2", "3", "4", "5"):
        return M["ND"], "tóm tắt", LY_DO_ND
    if chuong == "6":
        return M["ND"], "đầy đủ", "đọc/kiểm nội lực ETABS = trách nhiệm Input Adapter (agent không tự kiểm cổng ETABS)"
    if chuong == "7":
        return M["02"], "đầy đủ", "16 bước dầm; bước chưa có tool đánh dấu rõ"
    if chuong == "8":
        return M["03"], "đầy đủ", "14 bước cột; giới hạn tool (η=1, một cặp) ghi rõ"
    if chuong == "9":
        if so.startswith("9.7"):
            return M["05"], "đầy đủ", "trọng tâm: nút khung + bảng điều kiện thêm thép"
        if so.startswith("9.8"):
            return M["07"], "đầy đủ", "số liệu B (EC8 cũ) chỉ để đối chiếu; Chương 13 thay thế"
        return M["04"], "đầy đủ", "cấu tạo chung"
    if chuong == "10":
        if so.startswith("10.4"):
            return M["08"], "đầy đủ", "luật R1–R13 + chỉ mục R1–R52"
        if so.startswith("10.2.1"):
            return M["08"] + "; " + M["ND"], "tóm tắt", "giai đoạn chuẩn bị thuộc Input Adapter"
        return M["08"], "đầy đủ", "checklist quy trình"
    if chuong == "11":
        return M["09"] + " (chi tiết: " + M["02"] + ", " + M["03"] + ")", "tóm tắt", "ví dụ dùng để đối chiếu; số liệu chi tiết nằm ở module dầm/cột"
    if chuong == "12":
        return M["06"], "đầy đủ", "bố trí dọc + dữ liệu cho bản vẽ; chưa có tool"
    if chuong == "13":
        return M["07"], "đầy đủ", "kháng chấn — ⚠ sơ bộ, EN 1998-1"
    if chuong in ("14", "15"):
        return M["09"], "đầy đủ", "cổng chặn, phạm vi, xoắn, dầm cao, lỗ mở"
    if chuong == "A":
        return M["01"] + ("; " + M["ND"] if so.startswith("A.5") else ""), "đầy đủ", "bảng tra vật liệu/neo"
    if chuong == "B":
        return M["09"], "đầy đủ", "31 dòng sai khác + bổ sung của biên soạn skill"
    if chuong == "C":
        return M["09"], "đầy đủ", "biểu mẫu"
    if chuong == "D":
        return M["01"], "đầy đủ", "bảng công thức tra nhanh"
    if chuong == "E":
        return M["09"], "đầy đủ", "tài liệu tham khảo và điểm cần xác nhận"
    return "?", "?", "?"


def main():
    muc_luc = (NGUON / "MUC_LUC_NGUON.md").read_text(encoding="utf-8")
    sec1 = muc_luc.split("## 1. Tiêu đề (chương, mục, bước)")[1].split("## 2. Hình")[0]
    dong = []
    chuong = None
    for m in re.finditer(r"^(\s*)- L(\d+): (.+)$", sec1, flags=re.M):
        thut, ln, tieu = len(m.group(1)) // 2, int(m.group(2)), m.group(3).strip()
        mc = re.match(r"CHƯƠNG (\d+)\.", tieu)
        mp = re.match(r"PHỤ LỤC ([A-E])\.", tieu)
        if mc:
            chuong = mc.group(1)
        elif mp:
            chuong = mp.group(1)
        elif tieu.startswith("Phần mở đầu"):
            chuong = "0"
        so = re.match(r"(\d+(?:\.\d+)*|[A-E]\.\d+)", tieu)
        so = so.group(1) if so else ""
        # tiêu đề "Bước n." nằm trong chương 7/8 hiện hành
        nd, muc, ly = noi_di(so or tieu, tieu, chuong)
        dong.append((ln, tieu, nd, muc, ly))

    out = []
    out.append("# BẢN ĐỒ PHỦ — TỪ TÀI LIỆU NGUỒN SANG BỘ SKILL\n")
    out.append("> Sinh bởi `docs/agents/_nguon_tai_lieu_chon_thep/lap_ban_do_phu.py` từ `MUC_LUC_NGUON.md` (dòng L = dòng trong "
               "`NOI_DUNG_GOC.md`). Mỗi tiêu đề nguồn có một dòng: **nơi đi** (đường dẫn tương đối `docs/agents/`), **mức phủ** "
               "(đầy đủ / tóm tắt / tham chiếu) và **lý do** khi không phải \"đầy đủ\". Kiểm tra bằng "
               "`python docs/agents/_nguon_tai_lieu_chon_thep/kiem_tra_do_phu.py ...` (xem `BAO_CAO_CUOI.md`).\n")
    out.append("## A. Tiêu đề (chương, mục, bước) → nơi đi\n")
    out.append("| Dòng nguồn | Tiêu đề nguồn | Nơi đi trong skill | Mức phủ | Lý do / ghi chú |")
    out.append("|:--|:--|:--|:--|:--|")
    for ln, tieu, nd, muc, ly in dong:
        out.append(f"| L{ln} | {tieu.replace('|', '/')} | {nd} | {muc} | {ly} |")

    out.append("\n## B. Hình (32) → vị trí và khối \"Mô tả bằng chữ\"\n")
    out.append("| Dòng nguồn | Hình | File | Nơi đi | Mô tả bằng chữ |")
    out.append("|:--|:--|:--|:--|:--|")
    sec2 = muc_luc.split("## 2. Hình (ảnh trong nguồn → file trong figs/)")[1].split("## 3.")[0]
    vi_tri_hinh = {
        "f_51": "02", "f_52": "02", "col22_section": "03", "interaction_c22": "03", "f_54_section": "04", "f_510_col": "04",
        "f_511a": "04", "f_511b": "04", "f_513a": "05", "f_513b": "05", "f_513c": "05", "f_513d": "05", "f_513e": "05",
        "f_515a": "05", "f_515b": "05", "f_516": "05", "f_517a": "05", "f_517b": "05", "f_517c": "05", "f_518": "05",
        "f_520a": "05", "f_520b": "05", "f_520c": "05", "f_519": "05", "flow_process": "01", "beam_cb_layout": "09",
        "joint_corner_roof": "05", "lay_beam": "06", "lay_col": "06", "lay_crit": "07", "joint_check": "09", "tor_section": "09",
    }
    da = set()
    for m in re.finditer(r"^- L(\d+): `figs/([^`]+)\.png` — (.{0,70})", sec2, flags=re.M):
        ln, ten, cap = int(m.group(1)), m.group(2), m.group(3)
        mm = re.match(r"(Hình \d+\.\d+[a-e]?)\.", cap)
        nhan = mm.group(1) if mm else "(không đánh số hình trong nguồn)"
        if ten in da:
            nhan += " (lần 2: tham chiếu bằng văn bản)"
        da.add(ten)
        out.append(f"| L{ln} | {nhan} | `figs/{ten}.png` → `img/{ten}.png` | {M[vi_tri_hinh[ten]]} | có |")
    out.append("\nHình bổ sung (14, sinh bằng `huongdanchonthep/scripts_ve_hinh_bo_sung/ve_hinh_bo_sung.py`): bs_01…bs_11, bs_14 "
               "(Rule Engine), bs_12 (Input Adapter), bs_13 (Kiểm chứng) — mỗi hình có khối \"Mô tả bằng chữ\" ngay sau.\n")

    out.append("## C. Luật R1–R52 → nơi định nghĩa\n")
    out.append("| Luật | Nơi định nghĩa |")
    out.append("|:--|:--|")
    for n in range(1, 53):
        if n <= 13:
            f = M["08"]
        elif n <= 30:
            f = M["06"]
        elif n <= 40:
            f = M["07"]
        else:
            f = M["09"]
        out.append(f"| R{n} | {f} |")

    out.append("\n## D. Phụ lục B (31 dòng sai khác) → nơi đi\n")
    out.append(f"Toàn bộ 31 dòng chép nguyên vào `{M['09']}` (mục \"PHỤ LỤC B\"), cộng 17 dòng bổ sung B1–B17 do biên soạn skill "
               "phát hiện (xung đột nội bộ và lệch tài liệu–code–skill Vẽ).\n")

    out.append("## E. Mục gộp, rút gọn hoặc không đưa vào — kèm lý do\n")
    out.append("| Nội dung nguồn | Xử lý | Lý do |")
    out.append("|:--|:--|:--|")
    out.append("| Chương 2–5 (chọn sơ bộ, sơ đồ tính, tải, tổ hợp) | tóm tắt trong `SKILL_NHAP_DU_LIEU_ETABS.md` | " + LY_DO_ND + " |")
    out.append("| Bảng 4.1–4.6 chi tiết (từng lớp sàn, tải tập trung) | giữ kết quả chính, bỏ chi tiết từng phép nhân | số liệu ETABS đã có; chi tiết nằm ở `NOI_DUNG_GOC.md` |")
    out.append("| Chương 11 (ví dụ) | tóm tắt kết quả + số liệu then chốt | số liệu chi tiết ở module 02/03/06 để tránh lặp |")
    out.append("| Phần Q, R của rule base cũ | hợp nhất vào module 08 (Q) và 09 (R) | giữ test hiện có (PHẦN Q, D2, Khung Trục 5); cập nhật dòng cũ/mới khác nhau |")
    out.append("| Bản vẽ sàn, móng, chọc thủng, nén cục bộ (Phần Q, G5–G8) | giữ dòng \"ngoài phạm vi\" | ngoài phạm vi khung phẳng (R42) |")
    RA.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("ghi", RA.relative_to(GOC), "—", len(dong), "tiêu đề")


if __name__ == "__main__":
    sys.exit(main())
