# Báo cáo đối chiếu CODE ↔ TÀI LIỆU nguồn (bộ skill chọn thép v2)

Phạm vi: `src/rule_engine/**` và tool của Rule Engine Agent so với tài liệu nguồn (`NOI_DUNG_GOC.md`, PDF 115 trang, TCVN 5574:2018 ở Phụ lục A/D).
**Không sửa code** (ràng buộc của nhiệm vụ). Quy ước xử lý trong skill: khi hai nguồn lệch, **lấy giá trị an toàn hơn** làm mặc định và ghi rõ chỗ lệch ở module 09 (Phụ lục B bổ sung) / module 08 (Phần Q).

Cách kiểm: đọc code tại dòng nêu dưới đây; các dòng có dấu (*) được đọc lại ở phiên cuối, các dòng còn lại do đối chiếu ở các phiên trước (cần rà lại nếu code đã đổi).

| # | Nội dung | Code | Tài liệu | Mức | Xử lý trong skill |
|:-:|:--|:--|:--|:-:|:--|
| 1 | Hệ số uốn dọc η của cột | `rule_engine_agent.py:116` (*) `eta = 1.0` — chú thích tự nhận chỉ an toàn khi cột không mảnh | Bước 5 mục 8: η = 1/(1−N/Ncr); ví dụ cột 22 η = 1,045 | **CAO** | Module 03: l0/h > 7 ⇒ `hoi_nguoi_dung`, không để tool chạy η=1; cột 22 ghi η=1,045 tính tay, ghi rõ tool không ra số này |
| 2 | Tiêu chí cắt của `tu_kiem_tra` (dầm) | `verify.py:95-99` (*) yêu cầu Q ≤ Qb1+Qsw1 | Mục 11a: chỉ cần Qu(C) theo tiết diện nghiêng; CB Ø8a150 đạt 249,3 kN ≥ 240,3 | **CAO** | Tool chặt hơn: CB Ø8a150 báo 165,4 kN < 240,3 (đạt khi Ø8a≈70). Module 02 ghi cả hai, mặc định theo tool (an toàn) và báo mâu thuẫn |
| 3 | Chiều dài neo | `neo_noi.py:53` (*) `max(L_an, 15d, 200)` | Phụ lục A: L_an ≥ max(0,3·L0,an; 15d; 200) | TB | Thiếu sàn 0,3·L0,an. Module 01 ghi công thức đủ; ghi cờ khi L_an do tool trả nhỏ hơn 0,3·L0,an |
| 4 | Đường kính uốn móc | `neo_noi.py:87-88` (*) 5d (d<20) / 8d (d≥20) dạng **đường kính** | Phụ lục A: **bán kính** r ≥ 5d/8d; skill Vẽ: D ≥ 5d/8d/10d | TB | Module 04 ghi mâu thuẫn; mặc định giá trị lớn hơn (D≥…). Xem thêm báo cáo mâu thuẫn skill–Vẽ |
| 5 | Khoảng hở thép dọc cột | `cot_doc.py:72-74` (*) 25 mm (lớp 1–2) / 30 / 50 mm (từ lớp 3) | Chương 9: 50 mm giữa thanh cột theo bố trí chung; ví dụ nút dùng 61/52 mm | TB | Module 05: dùng 50 mm cho cột khi vẽ; 25 mm chỉ là cận dưới thi công |
| 6 | Lớp bảo vệ cột mặc định | `rule_engine_agent.py:195` (*) `cover=…get("cover", 40.0)` | Lớp bảo vệ theo cấp môi trường (module 04) | THẤP | Skill yêu cầu truyền `cover` rõ ràng, không dựa vào mặc định |
| 7 | Dải đường kính | `vat_lieu.py:69-81` (*) bảng dừng ở Ø32 | Tài liệu dùng thép tới Ø40 trong thực tế (Ø36/Ø40 hợp lệ ở TCVN) | THẤP | Skill nêu giới hạn; nếu cần Ø36/Ø40 ⇒ báo, không tự thêm |
| 8 | Hàm lượng cột | `cot_doc` kiểm μ mỗi phía ≤ 3 % | Chương 8/9: μt ≤ 4 % (8 % tại chỗ nối) | TB | Module 03 ghi cả hai; mặc định 3 % (chặt hơn) |
| 9 | ξR | Code dùng công thức (0,493 với Rs=435) | Bảng A cho 0,481 | THẤP | Module 01 ghi cả hai (có test `test_xi_r_cong_thuc_va_bang_lech_nhau`); chọn 0,481 khi tra bảng |
| 10 | `tinh_cot_treo` chưa là tool | `cot_dai.py:222` (*) có hàm | Bước 13 dầm cần cốt treo | **CAO** | Chỉ là hàm thư viện, agent không gọi được ⇒ GAP-tool (xem `BAO_CAO_GAP_TOOL.md`); module 02 yêu cầu ghi cờ `can_xac_nhan` |
| 11 | `nut_khung.py` chưa nối | 13 loại nút, không có tool | Chương 9.7: 20 loại NK + DM + CT | **CAO** | GAP-tool. `goc_mai_dong_e0_h_gt_05` thiếu "2·L_an", "≤ 2 thanh", "30d" — module 05 ghi phần thiếu |
| 12 | `chon_thep_doc` chỉ 1 đường kính | tổ hợp đơn đường kính | Ví dụ cột 22: 2Ø25+1Ø22 = 1362 mm² | TB | Với As = 1275, tool chọn 8Ø25; module 03 ghi: phương án hỗn hợp chỉ đưa vào báo cáo kèm cờ |

## Điều không nằm trong code (không có công thức để đối chiếu)
Bố trí theo chiều dài / điểm cắt (Chương 12), cổng hình học nút 14.2/14.3, kháng chấn (Chương 13, dựa EN 1998-1 ⇒ mọi số có ⚠), xoắn, dầm cao, lỗ mở: không có tool ⇒ skill chỉ **mô tả và yêu cầu ghi cờ**, tuyệt đối không để LLM tự tính.

## Lưu ý trung thực
- Một số hàng (3, 4, 5, 8, 12) dựa trên đối chiếu từ các phiên trước; hàng (*) được đọc lại ở phiên cuối. Trước khi dùng làm căn cứ thiết kế, cần kỹ sư rà lại.
- Báo cáo này ghi **sai khác**, không đánh giá bên nào đúng về mặt pháp lý; TCVN 5574:2018 (D, A) là nguồn ưu tiên cao nhất.
