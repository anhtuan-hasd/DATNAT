# Báo cáo GAP-tool — việc skill mô tả nhưng agent chưa có tool

Nhiệm vụ cấm thêm tool mới; báo cáo này chỉ **đặc tả** để sau này triển khai. Nguyên tắc: LLM không tự tính; mỗi công thức phải nằm trong `src/rule_engine/`. Khi chưa có tool, skill buộc agent **ghi cờ `can_xac_nhan`, không in "ĐẠT"** (R45/R46).

| Mã | Tool đề xuất | Đầu vào | Đầu ra | Cơ sở (module skill) | Hiện trạng code | Ưu tiên |
|:-:|:--|:--|:--|:--|:--|:-:|
| G1 | `tinh_cot_treo` | Q dầm phụ, b, h, h_s, Rsw, đường kính đai | số đai treo, vùng bố trí (b+2h_s hay b+2h — mâu thuẫn nguồn) | 02 Bước 13 | hàm `cot_dai.tinh_cot_treo` (cot_dai.py:222) chưa vào bảng tool | Cao |
| G2 | `tinh_eta_cot` | l0, h, N, M1, M2, Ncr, độ cứng | η và cờ cột mảnh | 03 Bước 5 | Không (đang η=1) | Cao |
| G3 | `chon_nut_khung` / `chi_tiet_nut` | loại nút (NK-01…20), d, b, h, As | quy tắc neo/uốn/đai cho nút + cổng hình học 14.2/14.3 | 05 | `nut_khung.py` (13 loại) chưa nối; thiếu "2·L_an", "≤ 2 thanh", "30d" ở `goc_mai_dong_e0_h_gt_05` | Cao |
| G4 | `bo_tri_theo_chieu_dai` | M(x), Q(x), phương án thép, qsw | điểm cắt/uốn, đoạn W = Q/2qsw+5d ≥ 20d, hình bao vật liệu | 06 (B4, B8) | Không | Cao |
| G5 | `kiem_tra_gioi_han_neo` | L_an thực, d, vùng nén/kéo | cờ khi L_an < 0,3·L0,an | 01 | `neo_noi.py:53` thiếu sàn 0,3·L0,an | Trung bình |
| G6 | `tinh_xoan_dam_cao_lo_mo` | nội lực, hình học | kiểm xoắn/dầm cao/lỗ mở | 09 | Không | Trung bình |
| G7 | `kiem_tra_khang_chan` | cấp dẻo, nội lực, cấu tạo | các kiểm tra Chương 13 (EN 1998-1) | 07 | Không; **mọi số có ⚠** | Thấp (cần xác nhận nguồn) |
| G8 | `chon_thep_doc` hỗn hợp đường kính | As yêu cầu, b, lớp | tổ hợp như 2Ø25+1Ø22 | 03 | Chỉ 1 đường kính ⇒ 1275 mm² → 8Ø25 | Trung bình |
| G9 | Mở rộng bảng đường kính | — | thêm Ø36/Ø40 | 01 | `vat_lieu.py:69-81` dừng Ø32 | Thấp |
| G10 | Tool đọc thép dọc/đai từ bản vẽ (Verification) | bản vẽ | KC-08/KC-09 (mã dành sẵn) | Verification | `kiem_chung_ban_ve` chỉ có `mat_cat`, `mat_dung_khung` | Trung bình |

Mọi hàng trên chưa triển khai; không có hàng nào được thêm trong đợt này.

## Cập nhật sau khi mở khoá vùng Vẽ (nhánh `feat/ban-ve-theo-mau-khung-truc5`)

Đã làm **ở lớp Vẽ** (không thêm tool cho agent): bố trí sơ bộ theo skill 06 nằm trong `src/drawing/to_ve/ke_hoach.py` và
`src/rule_engine/bo_tri_dai.py` (hàm thuần Python, có test):

| Mã | Trạng thái |
|:-:|:--|
| G4 (bố trí theo chiều dài) | **Một phần, ở lớp Vẽ**: thanh trên suốt + gia cường cắt L/4, thanh dưới chạy suốt, đai theo vùng (B8/C4). Chưa có: hình bao vật liệu, điểm cắt theo Mu, nối thép, cắt thép dưới. Chưa là tool của Rule Engine. |
| G3 (chi tiết nút) | **Một phần, ở lớp Vẽ**: móc thanh trên/dưới vào cột đầu biên, đai cột qua nút, hình 3D nút. Chưa có: tool sinh cấu tạo 20 loại nút (NK-01…20), cổng hình học 14.2/14.3. |
| G1 (cốt treo) | Chưa vẽ (dầm phụ gác dầm chính chưa có trong dữ liệu mẫu). |
| G2 (η cột) | Không đổi. |
| Mới | Móng/COS/sàn dày là **giả định** (`CauHinhToVe`) — dữ liệu ETABS không có; cần đưa vào Input Adapter nếu muốn thật. Mặt bằng sàn cần dữ liệu toàn nhà. |

Lưu ý: bảng băm 36 file Vẽ ở `_nguon_tai_lieu_chon_thep/_bang_bam_ve_truoc.txt` **không còn là điều kiện** (người dùng đã cho phép sửa vùng Vẽ); bảng giữ nguyên làm tư liệu lịch sử.

