# TÀI LIỆU HỢP NHẤT — Rule Base chọn thép khung BTCT (Phiên bản Cập nhật)

Đây là tài liệu tinh gọn dành cho **Rule Engine Agent**, tập trung vào các **quy tắc ra quyết định (R1-R52)**. Mọi công thức tính toán và hằng số đã được **mã hóa cứng (hardcode)** trong thư mục `src/rule_engine/` (Phương án C).

## 1. Nguyên tắc hoạt động
- **Agent không bao giờ tự tính số.** Bạn chỉ làm nhiệm vụ ra quyết định gọi Tool dựa trên các điều kiện dưới đây.
- Các hằng số (như $\xi_R$, $R_b$, độ mảnh, hàm lượng $\mu_{min}, \mu_{max}$) đều được lấy từ tiêu chuẩn (TCVN 5574:2018, TCVN 2737:2023) qua module `vat_lieu.py` và `uon_nen.py`.
- **Cổng chặn an toàn:** Khi gặp các yếu tố phức tạp (Kháng chấn, Xoắn, Dầm cao, Lỗ mở, Khe lọt nút), Agent phải dừng lại hoặc gắn cờ cảnh báo (theo bảng bên dưới).

## 2. Quy trình thiết kế cơ bản

### 2.1. Dầm (16 Bước - tóm tắt)
1. **Dữ liệu:** Chốt nội lực $M^+, M^-$ từng gối, nhịp; $Q_{max}$; $b \times h$.
2. **Chọn thép dọc:** Gọi `chon_thep_doc`. Nếu $\alpha_m > 0,5$ hoặc $\xi > \xi_R$, Tool sẽ báo lỗi; Agent cần báo **"tăng tiết diện"** (Không tự ý tăng thép). (R1, R2, R3)
3. **Kiểm tra hàm lượng:** $\mu_{min} \le \mu \le \mu_{max}$. (R4)
4. **Cốt đai:** Gọi `tinh_cot_dai`. Nếu $Q > 0,3 R_b b h_0$, báo **"tăng tiết diện"**. Nếu $Q \le 0,5 R_{bt} b h_0$, chỉ cần đai cấu tạo. (R5, R6)
5. **Cốt treo (Dầm phụ):** Tại vị trí dầm phụ gác lên, thêm cốt treo trong khoảng $S = b_{dp} + 2h_s$. (R23)
6. **Cắt/Uốn:** Cắt thép theo hình bao nội lực, đoạn kéo dài $W \ge \max(Q/2q_{sw} + 5d; 20d)$. (R16-R18)
7. **Neo:** $L_{an} \ge \max(15d; 200; 0,3L_{0,an})$.

### 2.2. Cột (14 Bước - tóm tắt)
1. **Dữ liệu:** Chốt các cặp nội lực nguy hiểm $(M, N)$ cho mỗi đầu cột.
2. **Lệch tâm:** Tính $e_0 = \max(e_1; e_a)$. $l_0/h \le 4 \Rightarrow \eta=1$. (R7)
3. **Phân loại lệch tâm:** Lệch tâm lớn ($x_1 \le \xi_R h_0$) hoặc bé ($x_1 > \xi_R h_0$). (R9)
4. **Chọn thép dọc:** Hàm lượng $\mu_t \in [1\%, 4\%]$. (R8)
5. **BĐTT (Biểu đồ tương tác):** Mọi cặp $(M, N)$ phải nằm trong biểu đồ tương tác ($\eta M, N$). Nếu không đạt, tăng thép; nếu $\mu_t > 4\%$, báo **tăng tiết diện**. (R10)
6. **Đai cột:** Bước đai $\le \min(15d_{min}, 500)$ (ngoài nối), $\le \min(10d_{min}, 300)$ (trong nối). Cột $N < 0$ (kéo) $\Rightarrow$ chuyển sang quy trình cột kéo. (R12, R26)

## 3. Các cổng chặn (Dừng và hỏi kỹ sư)

Agent **không tự giải quyết** mà phải dừng/báo cáo kỹ sư khi gặp các trường hợp sau (R41-R52):

| # | Điều kiện (Phát hiện từ mô hình) | Hành động của Agent |
|---|---|---|
| **R41** | Trước khi xuất bản vẽ nút (kiểm tra hình học nút 14.2) | Gọi tool kiểm tra lọt khe. Nếu số thanh một lớp > số khe lọt được $\rightarrow$ **không vẽ**, yêu cầu kỹ sư chọn phương án (tăng $b_c$, giảm thanh...). |
| **R42** | Cấu kiện thuộc dòng "Không/Chưa đủ" (Xoắn, vách, sàn, móng, nhịp lớn, chống cháy...) | **Dừng**, ghi lý do và danh sách việc cần làm; không điền số/vẽ. |
| **R43** | Hai dầm cắt nhau ở cùng cao độ mặt trên | Tính lại $h_0$ của dầm đặt thấp ($a' = a + d_{kia}$); chọn lại thép, nếu $M_u < M$ báo kỹ sư. |
| **R44** | Tiền lượng hoặc $\mu$ ngoài khoảng ($1 \div 3\%$ cột, $0,5 \div 2\%$ dầm) | **Cảnh báo** kèm con số và khoảng tham chiếu. |
| **R45** | Dữ liệu thuộc loại "ước lượng", "cần xác nhận", tiêu chuẩn cũ | Gắn cờ **"chưa đủ để phát hành"** lên dữ liệu. |
| **R46** | Cấu kiện hoàn tất | Không in nhãn "ĐẠT" khi còn bất kỳ cờ R41-R45 hoặc cờ kháng chấn. |

## 4. Xoắn, Dầm cao, Lỗ mở (Trường hợp đặc biệt)

| # | Điều kiện | Hành động của Agent |
|---|---|---|
| **R47** | Dầm có xoắn (T > 0) | Cân bằng/Tương thích không rõ ràng $\rightarrow$ Coi là xoắn cân bằng và **hỏi kỹ sư**; không tự giảm T. |
| **R48** | Có xoắn cần tính | Kiểm tra $T \le 0,1R_b b^2 h$. Không đạt $\rightarrow$ **Báo tăng tiết diện**. |
| **R49** | Có xoắn cần tính | Đai chọn theo Bước 3 (Chương 15); dọc tính từng biên (Bước 4); kiểm tra đủ 4 cạnh. |
| **R50** | Đồng thời M hoặc Q | Kiểm tra riêng lẻ (7.36, 7.37, 7.38); chọn bước đai nhỏ nhất thỏa mãn. Gắn cờ `can_xac_nhan`. |
| **R51** | $L_{ef}/h < 3$ (Dầm cao) | **Dừng:** chuyển sang mô hình thanh-giằng (báo kỹ sư). |
| **R52** | Lỗ mở xuyên dầm | **Dừng:** không tự chọn vị trí, thép quanh lỗ; yêu cầu kỹ sư. |

## 5. Kháng chấn (TCVN 9386:2012 / Eurocode 8)
*Chỉ kích hoạt nếu dự án có yêu cầu động đất.*

| # | Điều kiện | Hành động của Agent |
|---|---|---|
| **R31** | Công trình có động đất | Yêu cầu kỹ sư xác nhận **cấp dẻo (DCM/DCH)**. Không tự chọn. |
| **R32** | Dầm trong vùng tới hạn ($l_{cr} = 1,5h_w$ DCH hoặc $h_w$ DCM) | Đai $s \le \min(h_w/4; 24d_{bw}; 225; 8d_{bL})$ (DCM). Đầu dầm khoảng đai dày này. |
| **R33** | Dầm thép dọc | $\rho' \ge 0,5\rho$ ở gối; $\ge 2\phi 14$ chạy suốt; thép trên giữa nhịp $\ge 1/4$ gối. |
| **R34** | Cột (Lực dọc chuẩn hóa) | $\nu_d \le 0,65$ (DCM) / $0,55$ (DCH). Vượt ngưỡng $\rightarrow$ **báo tăng tiết diện**. |
| **R35** | Cột (Khoảng cách thép) | Các thanh giằng nhau $\le 200$ (DCM) / $150$ (DCH). Thêm thanh dọc nếu cần. |
| **R36** | Đầu cột (Vùng tới hạn) | $l_{cr} = \max(h_c; l_{cl}/6; 450)$ (DCM). Đai $s \le \min(b_0/2; 175; 8d_{bL})$. |
| **R37** | Cột (Bó lõi) | Tính $\alpha \omega_{wd}$; nếu không đạt bằng đai khả thi $\rightarrow$ **báo tăng tiết diện**. |
| **R38** | Nút khung | Đai nút $\ge$ vùng tới hạn cột; không cắt. Thanh dọc dầm ở trung gian bắt buộc. |
| **R39** | Mọi nút khung | $\sum M_{Rc} \ge 1,3 \sum M_{Rb}$ (Cột mạnh - dầm yếu). Không đạt $\rightarrow$ **báo tăng cột/giảm thép dầm**, không tự tăng thép cột. |
| **R40** | Nối thép cột | Rời mối nối khỏi vùng tới hạn; kiểm tra kỹ $L_{ov}$. |
