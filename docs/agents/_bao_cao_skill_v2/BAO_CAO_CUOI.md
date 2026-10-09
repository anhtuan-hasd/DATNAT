# Báo cáo cuối — bộ skill cho Input Adapter, Rule Engine, Verification

Nhánh `feat/skill-chon-thep-v2`. Nguồn: "Huong_dan_chon_thep_khung_BTCT12.pdf" (115 trang, 15 chương, R1–R52, 32 hình) dưới dạng gói `_nguon_tai_lieu_chon_thep/`.

## 1. Việc đã làm
| Hạng mục | Kết quả |
|:--|:--|
| Skill Input Adapter | `huongdannhapdulieu/SKILL_NHAP_DU_LIEU_ETABS.md` (+ hình bs_12) |
| Skill Rule Engine | `huongdanchonthep/00…09_*.md`: nguyên tắc/ưu tiên nguồn; vật liệu; dầm 16 bước; cột 14 bước; cấu tạo chung; **nút khung (NK-01…20, DM-01…13, CT-01…12)**; bố trí theo chiều dài; kháng chấn (⚠); bảng R1–R52 + Phần Q; rà soát phạm vi/xoắn/ví dụ/sai khác |
| Skill Kiểm chứng | `huongdankiemchung/SKILL_KIEM_CHUNG_KY_SU.md` (KC-01…07 tool đọc được; KC-10…24 việc kỹ sư; KC-08/09 để trống có chủ đích) |
| Hình | 32 hình nguồn + 14 hình bổ sung vẽ bằng script (`scripts_ve_hinh_bo_sung/`), đã xem lại bằng mắt; **mọi ảnh đều có khối "Mô tả bằng chữ"** (agent không xem được ảnh) — test kiểm tự động |
| Loader | `src/orchestrator/shared/doc_skill.py`; 3 agent nạp skill; Rule Engine theo loại (`loai=`) bỏ module không liên quan; thiếu file ⇒ prompt gốc, không lỗi |
| Bản đồ phủ | `BAN_DO_PHU_NGUON_SANG_SKILL.md` (242 mục, 32 hình, R1–R52 → module) sinh bằng `lap_ban_do_phu.py` |
| Hợp đồng | Cập nhật `RULE_ENGINE_AGENT.md`, `INPUT_ADAPTER_AGENT.md`, `VERIFICATION_AGENT.md` (không đụng `DRAWING_AGENT.md`) |
| Báo cáo | đối chiếu code–tài liệu; mâu thuẫn skill–Vẽ; GAP-tool; nhật ký dọn dẹp |

## 2. Kiểm chứng
- `kiem_tra_do_phu.py`: **ĐẠT** các kiểm tra cứng (R1–R52, hình, B1–B10/C1–C8, bước 1–16/1–14, 9.7.x & Chương 12–15, 31 hàng Phụ lục B, mọi mục có trong bản đồ phủ; số liệu có đơn vị thiếu: 0).
- Nhãn (nguồn → skill): ⚠ 36 → 91; [thực hành] 22 → 25; [ước lượng] 4 → 6; [kinh nghiệm] 5 → 9; [suy ra từ D] 3 → 4; [hình học] 2 → 3. Skill chỉ **thêm** nhãn, không mất nhãn nào.
- `pytest`: **276 đạt** (214 cũ không sửa + 62 mới: `test_skill_files.py`, `test_skill_loaders.py`). Test mới tính lại độc lập các số ví dụ (As 1949,5/1108,5; Mu 492,5/260,2; W=1165; F=28,035; ξR 0,493 vs 0,481; 1362 mm²; 198 kg/m³; 0,0061654 kg/(m·mm²)…).
- Bảng băm 36 file Vẽ bị khoá: **không đổi** (`sha256sum -c`, 0 dòng lỗi) sau mỗi pha.
- Đã rà độc lập bằng cách chạy lại checker, test và đối chiếu code (không dùng subagent, theo yêu cầu "làm inline"). Một lỗi do rà phát hiện và đã sửa: test Phụ lục B ban đầu quá lỏng (qua được nhờ điều kiện `or`) → thay bằng test kiểm đúng 31 hàng nguồn + B1–B17.

## 3. Phát hiện quan trọng (chi tiết ở các báo cáo kèm)
1. Code dùng **η = 1** cho cột (không tính uốn dọc) → skill buộc hỏi người dùng khi l0/h > 7.
2. `tu_kiem_tra` dầm dùng tiêu chí Qb1+Qsw1 **chặt hơn** mục 11a (CB Ø8a150: 165,4 vs 249,3 kN).
3. Thiếu tool cho: cốt treo (hàm có nhưng chưa là tool), chi tiết nút khung (`nut_khung.py` chưa nối), bố trí theo chiều dài/điểm cắt, cổng hình học nút, kháng chấn, xoắn/dầm cao/lỗ mở → skill buộc ghi cờ, **không in "ĐẠT"** (R45/R46).
4. Chương 13 (kháng chấn) dựa EN 1998-1: mọi số mang ⚠, **không đủ để phát hành bản vẽ**.
5. Nhiều mâu thuẫn nội bộ nguồn được ghi lại (Phụ lục B-bổ sung, B1–B17); mặc định lấy giá trị an toàn hơn.

## 4. Chi phí ngữ cảnh (cần quyết định)
Prompt Rule Engine chế độ gọn: dầm ≈ 138k ký tự, cột ≈ 140k (gốc cũ 74,6k ≈ gấp 1,9 lần); Input Adapter ≈ 27k; Verification ≈ 9,5k. Đã giảm bằng dấu PROMPT, bỏ khối mô tả ảnh (trừ module 05), loại module theo loại cấu kiện. Test chặn trần 165k ký tự. Nếu cần nhỏ hơn: thêm dấu BO cho Chương 12/14 hoặc chuyển bảng NK/DM/CT sang tra cứu theo yêu cầu.

## 5. Điều chưa làm / cần lưu ý (nói rõ, không giấu)
- **Đề bài bị cắt ngang**: văn bản yêu cầu nhận được dừng sau mục 12.3 điểm 8; phần còn lại của 12.3 và toàn bộ **Phần 13 (mẫu báo cáo cuối) chưa bao giờ nhận được**. Báo cáo này theo cấu trúc hợp lý, **không phải mẫu gốc**; nếu mẫu khác, cần bổ sung.
- `kiem_tra_do_phu.py` có lỗi nhỏ `m[0]` khi `findall` chỉ có 1 nhóm (vô hại, tôi **không sửa** vì là tệp nguồn).
- Không chạy AutoCAD/COM; không `git push`; không thêm tool; không sửa `src/rule_engine/**`, `src/drawing/**`, test cũ.
- Đối chiếu code–tài liệu: một phần dựa trên các phiên trước (xem lưu ý trong báo cáo đối chiếu); khoảng hở thanh cột 50 mm chưa đối chiếu với `src/drawing`.
- Mâu thuẫn skill–Vẽ (uốn móc, đai trong móng, 7 vs 8 cột thống kê) **chưa được giải quyết** vì skill Vẽ bị khoá — cần người quyết.
- Các ⚠ còn lại đều chờ kỹ sư xác nhận; **tài liệu này hỗ trợ tra cứu, không phải hồ sơ thiết kế**.
- Loader không bắt `IsADirectoryError`/`PermissionError` khi đường dẫn là thư mục (chỉ bắt file không tồn tại) — hiện không xảy ra vì đường dẫn cố định.

## 6. Commit (tiếng Việt, theo pha)
`c9226b5` Pha 0 nạp gói nguồn · `a98ba72` bộ skill + 14 hình · `03e281e` loader + 3 agent + bản đồ phủ · `9dc27cc` test · `5fedd3d` hợp đồng · (commit báo cáo ngay sau).
File của người dùng có từ trước **không** bị `git add`.
