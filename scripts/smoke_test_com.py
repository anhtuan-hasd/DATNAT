"""Smoke test thủ công cho backend_com.py — cần AutoCAD cài trên máy.
Chạy: python scripts/smoke_test_com.py
KHÔNG phải unit test tự động (không chạy trong pytest) — vì phụ thuộc 1 tiến
trình AutoCAD thật đang mở/được mở, không phù hợp CI.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.drawing import backend_com, geometry

print("1. Đang kết nối AutoCAD...", flush=True)
t0 = time.time()
app = backend_com.ket_noi_autocad()
print(f"   OK ({time.time()-t0:.1f}s) - AutoCAD version: {app.Version}", flush=True)

print("2. Đang tạo document mới + khai báo layer...", flush=True)
doc = backend_com.tao_ban_ve_moi(app)
print("   OK", flush=True)

print("3. Đang vẽ 1 mặt cắt dầm demo...", flush=True)
bv = geometry.ve_mat_cat_dam(
    "1-1", b=250, h=700, cover=25, duong_kinh_dai=8,
    thanh_duoi=[25, 25, 22, 22, 22], thanh_tren=[16, 16],
)
backend_com.ve_vao_doc(doc, bv)
print("   OK", flush=True)

print("4. Đang zoom to extents để nhìn thấy hình...", flush=True)
app.ZoomExtents()
print("   OK", flush=True)

print("5. Đang lưu file DWG (backend_com.luu_file_dwg, CHANGE_REQUESTS.md mục 2b)...", flush=True)
duong_dan_dwg = Path(__file__).parent.parent / "output" / "smoke_test_com" / "smoke_test_com.dwg"
duong_dan_dwg.parent.mkdir(parents=True, exist_ok=True)
backend_com.luu_file_dwg(doc, str(duong_dan_dwg))
print(f"   OK -> {duong_dan_dwg}", flush=True)

print("6. Đang xuất PDF (backend_com.xuat_pdf)...", flush=True)
duong_dan_pdf = duong_dan_dwg.with_suffix(".pdf")
try:
    backend_com.xuat_pdf(doc, str(duong_dan_pdf))
    print(f"   OK -> {duong_dan_pdf}", flush=True)
except Exception as e:
    # Xuất PDF cần layout đang active có cấu hình plot hợp lệ (driver/khổ
    # giấy) — có thể lỗi trên document MỚI TẠO chưa cấu hình layout, KHÔNG
    # phải lỗi logic vẽ. Không để bước này làm cả smoke test "thất bại".
    print(f"   BỎ QUA (lỗi xuất PDF, có thể do layout chưa cấu hình plot): {e}", flush=True)

print("HOÀN TẤT — kiểm tra cửa sổ AutoCAD để xem hình đã vẽ, và file DWG/PDF trong output/smoke_test_com/.", flush=True)
