"""Script CANONICAL — chạy TOÀN BỘ pipeline 4-agent (Input Adapter → Rule
Engine → Drawing → Verification, `src/orchestrator/pipeline.chay_toan_bo_khung`)
trên file ETABS THẬT `data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx`, từ đầu đến
cuối: đọc Excel → chọn thép cho 12 cột + 8 dầm → vẽ mặt cắt + mặt đứng khung
tổng thể + bảng thống kê + khung tên → xuất PDF/DWG — 100% qua AutoCAD COM
thật.

ĐÂY LÀ "ĐẦU RA CHUẨN BẢN VẼ KHUNG BTCT" của đồ án — thay thế mọi script demo
cũ (`chay_lien_mach_khung.py`, `ve_khung_truc5_day_du.py`, `demo_ve_phase3.py`,
`demo_ve_mat_bang_va_chi_tiet.py` — đã xoá, xem docs/CHANGE_REQUESTS.md mục 2).

YÊU CẦU trước khi chạy:
1. Mở sẵn AutoCAD (Windows Start -> AutoCAD), đóng hết hộp thoại lần đầu chạy.
2. Đặt OPENAI_API_KEY — script TỰ NẠP từ file `.env` ở gốc dự án nếu có
   (giống webapp/app.py, dùng python-dotenv); nếu chưa có `.env`, đặt trực
   tiếp bằng biến môi trường trước khi chạy: $env:OPENAI_API_KEY = "sk-...".

Chạy: python scripts/chay_pipeline_day_du.py
Kết quả: output/khung_truc5_day_du/KHUNG_TRUC5.pdf + .dwg, kèm báo cáo in ra
màn hình (trạng thái từng phần tử, kiểm chứng tổng thể).
"""

from __future__ import annotations

import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).parent.parent
sys.path.insert(0, str(THU_MUC_GOC))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(THU_MUC_GOC / ".env")  # nạp OPENAI_API_KEY từ .env nếu có, không báo lỗi nếu thiếu file

from src.orchestrator import agent, pipeline  # noqa: E402

FILE_DU_LIEU = THU_MUC_GOC / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"
THU_MUC_XUAT = Path(__file__).parent.parent / "output" / "khung_truc5_day_du"


def hoi_nguoi_dung_tu_dong(cau_hoi: str, lua_chon: list[str] | None) -> str:
    """Với dữ liệu ETABS thật, Input Adapter Agent hầu như KHÔNG cần hỏi gì
    (dữ liệu đủ và chính xác qua doc_etabs_that) — hàm này chỉ là lưới an
    toàn cho trường hợp bất ngờ agent vẫn hỏi (vd hết lượt tự sửa/kiểm chứng
    ở 1 vị trí cụ thể). Tự động trả lời "đồng ý" và LUÔN IN RÕ câu hỏi ra màn
    hình để người chạy script biết agent đang gặp vướng mắc gì — không âm
    thầm bỏ qua."""
    print(f"\n  [AGENT HỎI] {cau_hoi}")
    if lua_chon:
        print(f"  (lựa chọn gợi ý: {lua_chon})")
    print("  -> Tự động trả lời: 'đồng ý' (script chạy không giám sát).")
    return "đồng ý"


def quan_sat_tien_do(giai_doan: str, ten: str, ket_qua_agent) -> None:
    so_luot = ket_qua_agent.so_lan_goi_model
    print(f"  [{giai_doan}] {ten} — {so_luot} lượt gọi model, dừng vì: {ket_qua_agent.dung_vi}")


def main() -> None:
    if not FILE_DU_LIEU.exists():
        print(f"LỖI: không tìm thấy file dữ liệu mẫu: {FILE_DU_LIEU}")
        sys.exit(1)

    print("=" * 78)
    print("CHẠY TOÀN TRÌNH — 4 AGENT, 100% AUTOCAD COM")
    print(f"Dữ liệu vào : {FILE_DU_LIEU.name}")
    print(f"Xuất ra     : {THU_MUC_XUAT}")
    print("=" * 78)

    # max_completion_tokens=8192 (KHÔNG phải 800) — xem giải thích chi tiết
    # tại webapp/jobs.py (cùng lỗi thật đã gặp: tool lap_rap_mat_dung_khung
    # cần "SAO CHÉP NGUYÊN VĂN" 1 khối JSON lớn cho toàn bộ phần tử, 800
    # token không đủ, JSON bị cắt cụt -> tool báo thiếu khóa toa_do_truc).
    provider = agent.OpenAIChatProvider(max_completion_tokens=8192)

    ket_qua = pipeline.chay_toan_bo_khung(
        nha_cung_cap=provider,
        duong_dan_file=str(FILE_DU_LIEU),
        hoi_nguoi_dung=hoi_nguoi_dung_tu_dong,
        thu_muc_xuat_ban_ve=str(THU_MUC_XUAT),
        ten_khung="KHUNG_TRUC5",
        quan_sat=quan_sat_tien_do,
    )

    print("\n" + "=" * 78)
    print("NHẬT KÝ PIPELINE")
    print("=" * 78)
    for dong in ket_qua.nhat_ky:
        print(f"  {dong}")

    print("\n" + "=" * 78)
    print("KẾT QUẢ TỪNG PHẦN TỬ")
    print("=" * 78)
    so_dat = ket_qua.so_phan_tu_dat
    tong = len(ket_qua.ket_qua_phan_tu)
    for kq_pt in ket_qua.ket_qua_phan_tu:
        ky_hieu = "✓" if kq_pt.trang_thai == "dat" else "✗"
        print(f"  [{ky_hieu}] {kq_pt.ten_phan_tu} ({kq_pt.loai}): {kq_pt.trang_thai}" + (f" — {kq_pt.ghi_chu}" if kq_pt.ghi_chu else ""))

    print("\n" + "=" * 78)
    print(f"TỔNG KẾT: {so_dat}/{tong} phần tử đạt tự kiểm tra + kiểm chứng bản vẽ.")
    if ket_qua.kiem_chung_tong_the is not None:
        trang_thai = "ĐẠT" if ket_qua.kiem_chung_tong_the.dat else "CHƯA ĐẠT"
        print(f"Kiểm chứng bản vẽ tổng thể: {trang_thai}")
        if ket_qua.kiem_chung_tong_the.vi_pham:
            for vp in ket_qua.kiem_chung_tong_the.vi_pham:
                print(f"  - {vp}")
    if ket_qua.duong_dan_pdf:
        print(f"Bản vẽ PDF: {ket_qua.duong_dan_pdf}")
    if ket_qua.duong_dan_dwg:
        print(f"Bản vẽ DWG: {ket_qua.duong_dan_dwg}")
    print("=" * 78)


if __name__ == "__main__":
    main()
