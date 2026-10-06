"""
Sinh 2 file dữ liệu THỬ NGHIỆM tự tạo cho Input Adapter (Phase 2) — KHÔNG
phải dữ liệu thật của ETABS, KHÔNG phải code tham khảo — chỉ là input mẫu để
test khả năng dò schema không cố định. Chạy 1 lần để tạo file, không phải
import trong pipeline chính.

- dam_don_gian.csv: 1 bảng đơn giản, header tiếng Việt rõ ràng.
- bao_cao_etabs_day_du.xlsx: nhiều sheet, header kiểu ETABS (tiếng Anh), có
  cả sheet "nhiễu" (Cover/Materials) để test lọc sheet không liên quan.
"""

import pandas as pd

FIXTURES_DIR = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0]


def sinh_file_don_gian():
    df = pd.DataFrame(
        [
            # Phan_tu, Loai, Vi_tri, b, h, As_yc, M, N, Q, To_hop, Mac_be_tong, Nhom_thep
            ["44-45", "dam", "goi_trai", 250, 700, 1212, 346.5, 0, 180.2, "COMBO3", "B30", "CB500-V"],
            ["44-45", "dam", "goi_phai", 250, 700, 1103, 316.0, 0, 175.4, "COMBO3", "B30", "CB500-V"],
            ["44-45", "dam", "giua_nhip", 250, 700, 569, 162.8, 0, 90.1, "COMBO5", "B30", "CB500-V"],
            ["22", "cot", "dai_dien", 250, 600, 1362, 417.74, 1514.38, 95.6, "TH12", "B30", "CB500-V"],
        ],
        columns=[
            "Phan_tu", "Loai", "Vi_tri", "b(mm)", "h(mm)", "As_yc(mm2)",
            "M(kNm)", "N(kN)", "Q(kN)", "To_hop", "Mac_be_tong", "Nhom_thep",
        ],
    )
    df.to_csv(f"{FIXTURES_DIR}/dam_don_gian.csv", index=False, encoding="utf-8-sig")


def sinh_file_day_du():
    sheet_cover = pd.DataFrame({"Field": ["Project", "Units"], "Value": ["Khung mau", "kN, mm"]})

    sheet_dam = pd.DataFrame(
        [
            ["Story2", "B12", "B12-1", "D250x700", "COMBO3", 0, 0.0, 180.2, 346.5, 1212],
            ["Story2", "B12", "B12-1", "D250x700", "COMBO3", 3200, 0.0, 175.4, 316.0, 1103],
            ["Story2", "B12", "B12-1", "D250x700", "COMBO5", 1600, 0.0, 90.1, 162.8, 569],
        ],
        columns=["Story", "Beam", "Unique Name", "Section", "Combo", "Station(mm)", "P(kN)", "V2(kN)", "M3(kN-m)", "AsReq(mm2)"],
    )

    sheet_cot = pd.DataFrame(
        [
            ["Story1", "C22", "C22-1", "C250x600", "TH12", 0, 1514.38, 95.6, 417.74, 1362],
        ],
        columns=["Story", "Column", "Unique Name", "Section", "Combo", "Station(mm)", "P(kN)", "V2(kN)", "M3(kN-m)", "AsCol(mm2)"],
    )

    sheet_vat_lieu = pd.DataFrame({"Material": ["B30", "CB500-V"], "fc_MPa": [17.0, None], "fy_MPa": [None, 435.0]})

    with pd.ExcelWriter(f"{FIXTURES_DIR}/bao_cao_etabs_day_du.xlsx", engine="openpyxl") as writer:
        sheet_cover.to_excel(writer, sheet_name="Cover", index=False)
        sheet_dam.to_excel(writer, sheet_name="Concrete Beam Envelope", index=False)
        sheet_cot.to_excel(writer, sheet_name="Concrete Column Envelope", index=False)
        sheet_vat_lieu.to_excel(writer, sheet_name="Materials", index=False)


if __name__ == "__main__":
    sinh_file_don_gian()
    sinh_file_day_du()
    print("Đã sinh xong 2 file fixture trong", FIXTURES_DIR)
