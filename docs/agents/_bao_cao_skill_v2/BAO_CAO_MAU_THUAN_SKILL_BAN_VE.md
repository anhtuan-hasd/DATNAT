# Báo cáo mâu thuẫn giữa skill chọn thép v2 và skill/code Vẽ (Drawing Agent)

Skill Vẽ (`docs/agents/huongdanvebanve/**`, `DRAWING_AGENT.md`, `drawing_agent.py`, `src/drawing/**`) **bị khoá, không sửa**. Báo cáo này chỉ ghi chỗ lệch để người có thẩm quyền quyết định. Hash 36 file Vẽ được kiểm lại cuối mỗi pha (`_bang_bam_ve_truoc.txt`): không đổi.

| # | Chủ đề | Skill chọn thép v2 | Skill / code Vẽ | Giá trị mặc định đang áp dụng | Cần ai quyết |
|:-:|:--|:--|:--|:--|:--|
| 1 | Uốn móc | Bán kính r ≥ 5d/8d (Phụ lục A); code Rule Engine dùng 5d/8d làm **đường kính** | D ≥ 5d / 8d / 10d | Giá trị lớn hơn (D ≥ …) | Kỹ sư + chủ đề tài |
| 2 | Số mặt cắt mỗi dầm | Chương 7/12: gối trái, giữa nhịp, gối phải (3) khi đổi thép | Drawing yêu cầu 3 mặt cắt/dầm | Trùng nhau (3); Verification kiểm theo 3 | — |
| 3 | Đai cột trong móng | Tài liệu 12.6 / module 05 (NK-16): 2–3 đai trong chiều cao móng ở đoạn thép chờ (module 09, B16) | Skill Vẽ (M.6): đai cột kéo xuống tới sát đáy đài | Phương án của Vẽ (đầy đủ hơn, an toàn hơn); ghi cờ | Kỹ sư |
| 4 | Trọng lượng riêng thép | 0,0061654 kg/(m·mm²) (chính xác) | 0,00617 (làm tròn) | Chênh ≈ 0,07 % ⇒ chấp nhận; ghi cả hai trong module 01 | — |
| 5 | Bảng thống kê thép | 7 cột (module 06/09) | 8 cột (KC-07 của Verification kiểm "đủ 8 cột") | Theo Vẽ khi vẽ; Verification kiểm 8 cột | Chủ đề tài |

## Ghi chú
- Mục 5: cần xác nhận cột thứ 8 là cột nào; skill chọn thép không xuất bảng ⇒ lệch này không làm sai số liệu thép, chỉ ảnh hưởng định dạng.
- Khoảng hở thanh cột (50 mm trong skill chọn thép) **chưa được đối chiếu** với hằng số trong `src/drawing`; không khẳng định lệch hay khớp — để mở.
- Không có mục nào thay đổi số liệu thép của Rule Engine; Drawing vẫn nhận `PhuongAnThepPhanTu` như cũ (hợp đồng dữ liệu không đổi).
