# 08 — BẢNG LUẬT QUYẾT ĐỊNH R1–R52, CHECKLIST VÀ PHẦN Q (ĐIỀU KIỆN → XỬ LÝ)

> Module này là **nơi tra cứu khi gặp tình huống biên**: tra đúng mã (R#, hoặc A1, B3, D2, F2c…) rồi làm theo cột "Xử lý/Hành động". Không tự suy luận cách xử lý khác khi đã có quy tắc.
> Hợp nhất: (a) luật R1–R13 và checklist của tài liệu nguồn (Chương 10); (b) **Phần Q** của rule base cũ (bảng ~70 trường hợp A–I) **đã đối chiếu và cập nhật** theo tài liệu nguồn mới; (c) chỉ mục toàn bộ R1–R52. Các dòng có ⚠ là chỗ cũ/mới khác nhau (đã chọn giá trị an toàn hơn).

# CHƯƠNG 10. CHECKLIST QUY TRÌNH CHỌN THÉP

## 10.1. Sơ đồ quy trình tổng thể

Xem lưu đồ ở module 01 (`flow_process.png`). **Ba "cổng" bắt buộc:** (1) **Cổng ETABS** (cuối Chương 6): $\sum N$ chân cột = tổng tải đứng; $\sum Q$ chân cột = tổng gió; chuyển vị, chu kỳ hợp lý — Input Adapter chịu trách nhiệm, agent này nhận dữ liệu đã qua cổng; (2) **Cổng khả năng chịu lực** (cuối từng cấu kiện): $M_u\ge M$, $x\le\xi_Rh_0$, $\mu$ trong giới hạn (dầm); mọi $(\eta M,N)$ trong BĐTT (cột); (3) **Cổng cấu tạo** (module 04–06): lớp bảo vệ, khoảng hở, neo, nối, đai, nút khung.

## 10.2. Bảng checklist theo từng bước

### 10.2.1. Giai đoạn chuẩn bị (Chương 1–6)

Thuộc Input Adapter (`SKILL_NHAP_DU_LIEU_ETABS.md`): điền đủ nhóm A–G; chọn sơ bộ tiết diện; sơ đồ tính; tải; tổ hợp; nội lực và kiểm ETABS. Lỗi thường gặp ở đó ảnh hưởng trực tiếp tới agent này: thiếu cấp bền/nhóm thép; nhầm điểm giữa nhịp (vị trí dầm phụ) là cột; quên đoạn từ mặt ngàm (ảnh hưởng $l_0$); ghép $M$ tổ hợp này với $N$ tổ hợp khác; bỏ mô men giữa nhịp; đọc nén là dương.

### 10.2.2. Dầm — 16 bước (Chương 7)

Chi tiết module 02. Các lỗi thường gặp theo bước: B1 bỏ sót dầm, lấy $Q$ giữa nhịp; B3 dùng $a$ một hàng cho gối hai hàng; B4 dùng chữ T cho mô men âm, $b_f'$ sai; B5 quên đổi kN·m→N·mm; B6 dùng $R_s$ cho $R_{sw}$, không kiểm $x\ge2a'$; B7 dùng 0,05%; B8 không đủ khoảng hở, vượt >10%, >3 loại Ø, chênh Ø >6 mm; B9 cố "cứu" bằng đai; B10 bỏ qua $Q_{b,min}$; B11 quên số nhánh, đoạn $L/4$ đai dày; B12 dùng cốt xiên khi tăng đai đã đủ; B13 **quên cốt treo**; B14 cắt sát điểm lý thuyết, dùng quy tắc ACI cho khung chịu gió; B15 $R_{bond}$ thiếu $R_{bt}$; B16 chỉ kiểm nứt/võng khi nhịp lớn.

### 10.2.3. Cột — 14 bước (Chương 8)

Chi tiết module 03. Bước 0 chọn phương pháp (chỉ kiểm một cặp là lỗi); B3 $l_0=H$/quên đoạn ngàm; B4 $e_a$ theo $l_0$; B5 quên nhân $\eta$, $\eta<0$ khi $N>N_{cr}$; B7 dùng công thức lệch tâm lớn cho lệch tâm bé; B8 dùng một $\mu_{min}$ cho mọi độ mảnh; B9 bỏ cốt cấu tạo, $a$ thực lệch >5 mm; B10 quên phương ngoài mặt phẳng; B11 không nhân $\eta$ vào điểm kiểm; B12 lấy $15d$ theo thanh lớn; B13 nối ở vùng nút/mô men lớn; B14 cột góc tính một phương.

### 10.2.4. Cấu tạo và hoàn thiện hồ sơ (Chương 9, 12, 13, 14, 15)

Lớp bảo vệ (module 04: 20/25/30/40; không dùng 15 mm bản cũ); khoảng hở ($\max(d;25)$ đáy, $\max(d;30)$ trên, $\max(d;50)$ cột; không nhồi 5Ø25 vào $b=250$); neo–nối–uốn (module 04); nút khung (module 05; lỗi: cắt thép dầm ngay mép cột, neo thiếu); cột–móng (thiếu đai trong đoạn neo); bố trí dọc (module 06; lỗi: cắt thép không có $W$, quên mô men dương ở gối); kháng chấn (module 07; lỗi: dùng $N$ tổ hợp thường, nối thép trong vùng tới hạn); bản vẽ và thống kê (mặt cắt không khớp thống kê).

## 10.3. Checklist kiểm tra cuối cùng trước khi phát hành hồ sơ

**A. Số liệu và mô hình:** tiêu chuẩn, vật liệu, lớp bảo vệ ghi đúng trên bản vẽ và khớp ETABS; tải khớp bảng Chương 4 ($\sum N$ chân cột); tổ hợp đúng TCVN 2737:2023, có tổ hợp dài hạn cho cột; nội lực từ **bao** các tổ hợp, đúng dấu, đơn vị.
**B. Dầm:** mỗi tiết diện nguy hiểm $M_u\ge M$, $x\le\xi_Rh_0$, $\mu_{min}\le\mu\le\mu_{max}$; đai $Q\le0{,}3R_bbh_0$, $Q_u\ge Q$, bước đầu $\le\min(h/2;300)$, giữa $\le\min(3h/4;500)$; **cốt treo** ở mọi chỗ dầm phụ; $W\ge\max(Q/2q_{sw}+5d;20d)$, ≥2 thanh và ≥$A_s/2$ vào gối; $L_{an}\ge\max(15d;200;0{,}3L_{0,an})$.
**C. Cột:** $\lambda_b\le31$; $\eta$ theo $\mu_t$ thực, $N<N_{cr}$; mọi $(\eta M,N)$ trong BĐTT, $k_{max}\le1$; ngoài mặt phẳng $N\le N_u$; $\mu_{min}\le\mu\le3\%$, $\mu_t\le4\%$ (8% nối); tim thép $\le400/\le500$, cốt cấu tạo khi $h>500$; đai $\ge\max(d_{max}/4;6)$, $s\le15d_{min}$ ($10d_{min}$ nối); nối ngoài nút, $L_{ov}$ đủ.
**D. Nút và cấu tạo:** từng loại nút có sơ đồ cốt thép và neo kiểm bằng số; thép chờ cột–móng, đai trong móng; bố trí dọc (module 06), phiếu 12.8; nhà chịu động đất: cấp dẻo đã xác nhận, kiểm Chương 13 và đối chiếu 13.9; mọi bán kính uốn, móc, khoảng hở ghi trên bản vẽ.
**E. Hồ sơ:** bảng thống kê khớp mặt cắt; ghi chú rõ phần tiêu chuẩn cũ/giả thiết (Phụ lục B); **thép dầm lọt qua thép cột ở mọi nút; dầm đặt thấp đã tính lại $h_0$; cấu kiện ngoài phạm vi (14.1) đã xử lý riêng; dầm có $T\ne0$ đã tính theo 15.1.**

## 10.4. Cấu trúc dữ liệu và luật quyết định cho AI Agent (tóm tắt từ chương 1–9; luật bố trí R14–R30 ở mục 12.7; luật kháng chấn R31–R40 ở mục 13.10; cổng chặn R41–R46 ở mục 14.6; xoắn, dầm cao, lỗ mở R47–R52 ở mục 15.4)

**Đầu vào tối thiểu của một cấu kiện:** loại (dầm/cột/console), $b$, $h$, $L$ hoặc $l$, cấp bền bê tông, nhóm thép dọc và đai, $c$, danh sách cặp nội lực (tổ hợp, vị trí, $M$, $N$, $Q$), $M_{dh}$, $N_{dh}$ (cột), điều kiện liên kết ($l_0$).

| # | Luật quyết định | Hành động của Agent |
|:--|:--|:--|
| R1 | $\alpha_m>0{,}5$ hoặc $\xi>\xi_R$ với cốt đơn đã thử cốt kép | Báo **"tăng tiết diện"**, không tự tăng thép |
| R2 | Mô men dương dầm | Tính tiết diện chữ T với $b_f'$ nhỏ nhất của các điều kiện; kiểm $M_f$ |
| R3 | $A_{s,tt}<A_{s,min}$ | Lấy $A_s=A_{s,min}$ |
| R4 | Không có tổ hợp thép nào chọn được trong bề rộng $b$ (khoảng hở) | Thử 2 hàng, tăng Ø (≤ 32 dầm / ≤ 40 cột); nếu vẫn không được → báo tăng $b$ |
| R5 | $Q\le Q_{b,min}$ | Đai cấu tạo |
| R6 | $Q>0{,}3R_bbh_0$ | Báo tăng tiết diện |
| R7 | Cột: $l_0/h\le4$ | $\eta=1$ |
| R8 | Cột: $N\ge N_{cr}$ | Báo tăng tiết diện |
| R9 | Cột: $x_1\le\xi_Rh_0$ | Công thức lệch tâm lớn, ngược lại lệch tâm bé |
| R10 | Cột: sau khi chọn thép, một cặp $(\eta M,N)$ nằm ngoài BĐTT | Tăng thép → kiểm lại; nếu $\mu_t>4\%$ → tăng tiết diện |
| R11 | Cột: khoảng cách tim thép trên cạnh $>500$ mm | Thêm thanh cấu tạo |
| R12 | Cột có $N<0$ (kéo) | Chuyển sang quy trình cột kéo (Bước 14a) |
| R13 | Tiết diện cột/dầm thay đổi giữa các tầng | Kiểm tra lại neo/nối tại nút |

**Đầu ra của Agent:** (i) bảng thép dọc và đai, (ii) $L_{an}$, $L_{ov}$, vị trí cắt, (iii) hệ số sử dụng $k=\text{yêu cầu}/\text{khả năng}$ cho mọi tiết diện, (iv) danh sách cảnh báo (tiêu chuẩn cũ, giả thiết chưa kiểm).
**Đối chiếu tool cho R1–R13:** R3 `tu_kiem_tra` (μ<μmin) • R4 `chon_thep_doc` báo lỗi "không tìm được tổ hợp" (nhưng tool dừng Ø≤32: không có Ø36/Ø40) • R5, R6 `tinh_cot_dai` (`can_dat_dai_theo_tinh_toan`, `dat_dieu_kien_ep_vo_bung`) • R7–R9 `tinh_lech_tam_cot` (η=1 cố định ⇒ **R7 chỉ đúng khi $l_0/h\le4$; R8 không có tool**) • R10 (một cặp, không BĐTT) • R11 `chon_thep_doc(loai="cot")` đã đặt thanh giữa cạnh dài theo khoảng ≤400 • R12 `tu_kiem_tra` trả lỗi khi $N\le0$ • R1, R2, R13 **không có tool**.

# PHẦN Q — DANH MỤC TRƯỜNG HỢP ĐẶC BIỆT KHI CHỌN THÉP (bảng quy tắc ĐIỀU KIỆN → XỬ LÝ)

Khai thác lại theo góc nhìn **ngược lại**: theo từng **điểm rẽ nhánh** Rule Engine thực sự gặp. Mỗi dòng: **Điều kiện** (IF) → **Xử lý** → **Nguồn/mã mới**. Bảng gốc của rule base cũ đã đối chiếu với tài liệu nguồn; chỗ khác ghi ⚠ và mã R/NK/DM/CT.

### 57. Thứ tự xử lý tổng thể cho một phần tử

1. Phân loại cấu kiện: dầm hay cột? (DesignType).
2. Công trình có yêu cầu **kháng chấn**? (cờ do người dùng khai báo, **không suy từ ETABS**). CÓ ⇒ đối chiếu thêm Bảng H và module 07 (R31) trước khi chốt.
3. Dầm: THÉP DỌC (Bảng A) độc lập từng vị trí → CỐT ĐAI (Bảng B) → CỐT TREO/GIẬT ĐỨT nếu có dầm phụ (Bảng C).
4. Cột: THÉP DỌC (Bảng D) → CỐT ĐAI (Bảng E).
5. **MỌI nút giao dầm–cột:** cấu tạo nút (Bảng F; module 05) — bước hay bị bỏ sót. **Kiểm hình học 14.2/14.3 (Bảng K).**
6. Vị trí có lực cục bộ/neo/nối (chân cột, đổi tiết diện, mối nối): Bảng G.
7. **Kiểm phạm vi (Bảng K, R42) trước khi bắt đầu; quy tắc vận hành/toàn vẹn dữ liệu (Bảng I) chạy sau cùng, trước khi xuất bản vẽ.**

### 58. Dầm — thép dọc chịu uốn: trường hợp đặc biệt (Bảng A)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
|:--|:--|:--|:--|
| A1 | Chuẩn: $A_{s,min}\le A_{s,yc}\le A_{s,max}$ | $A_{s,tk}=\max(A_{s,yc},A_{s,min})$; chọn tổ hợp theo Ø chuẩn dự án (số thanh = ROUNDUP($A_{s,tk}/A_{s,1\,thanh}$)) | 02 Bước 7–8 |
| A2 | $A_{s,yc}<A_{s,min}$ ($\mu<0{,}1\%$) | $A_{s,tk}=A_{s,min}=\mu_{min}bh_0$. **KHÔNG** dùng $A_{s,yc}$ trực tiếp | R3 |
| A3 | $A_{s,yc}>A_{s,max}$ ($\alpha_m>\alpha_R$) | **KHÔNG** tăng $A_s$ đơn thuần (giòn). (a) tăng tiết diện; (b) cốt kép (Bài toán 2); (c) tăng $R_b$ (ít hiệu quả) | R1 |
| A3a | Cốt kép, ĐÃ có $A_s'$ sẵn | Bài toán 3 (6c): $\alpha_m$ với $A_s'$ cho trước; 3 nhánh theo $\xi$ vs $\xi_R$ và $2a'/h_0$ | 02 Bước 6c |
| A4 | Chữ T/I: so $M$ với $M_f$ | $M\le M_f$ ⇒ qua **cánh** (chữ nhật $b_f'$); $M>M_f$ ⇒ qua **sườn** | R2 |
| A5 | Dầm có $N$ đáng kể: $\|N\|>0{,}1R_bbh_0$ | **KHÔNG** tính như uốn thuần tuý ⇒ nén lệch tâm (Bảng D) hoặc kéo lệch tâm (14a) | 02 Bước 16a |
| A6 | $A_s$ âm/rất nhỏ | Cấu tạo tối thiểu $A_s=A_{s,min}$; ≥2 thanh ($b\ge150$) | A2 + 02 Bước 8b |
| A7 | Số thanh vượt ngưỡng thực hành | Chuyển Ø **lớn hơn** kế tiếp, tính lại; hoặc thêm lớp thứ 2. ⚠ Ngưỡng theo $b$ **bảng 8b** (không phải "6/lớp" cố định) | R4 |
| A8 | Nhiều vị trí liền kề $A_s$ chênh không đáng kể | Có thể đồng bộ dùng tổ hợp lớn hơn — **kinh tế, không bắt buộc** | thực hành |
| A9 | Dầm cao bất thường/công-xôn ngắn | **NGOÀI phạm vi Bài toán 1–4: DỪNG (R51)**: mô hình thanh–giằng | module 09, 15.2 |

### 59. Dầm — cốt đai chịu cắt: trường hợp đặc biệt (Bảng B)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
|:--|:--|:--|:--|
| B1 | $Q\le0{,}5R_{bt}bh_0$ | KHÔNG cần tính đai theo cắt. Đai cấu tạo $s_{ct}\le\min(3h/4;500)$ | R5 |
| B2 | $Q>0{,}3R_bbh_0$ | **Tiết diện KHÔNG ĐỦ** dù bao nhiêu đai: tăng tiết diện/cấp bê tông | R6 |
| B3 | $0{,}5R_{bt}bh_0<Q\le0{,}3R_bbh_0$ (chuẩn) | $q_{sw}=\max[Q^2/(4{,}5R_{bt}bh_0^2);0{,}25R_{bt}b]$; $s=\min(R_{sw}A_{sw}/q_{sw};s_{max}\text{ cấu tạo})$. ⚠ **Số nhánh:** cũ ($b\le150$: 1; $>150$: 2; $\ge400$: ≥3) ⟷ mới (2 nhánh $b\le350/400$; 3–4 nhánh khi lớn hơn) — lấy **chặt hơn** | 02 Bước 11 |
| B4 | $C_0=\sqrt{2R_{bt}bh_0^2/q_{sw}}$ ngoài $[h_0;2h_0]$ | $C_0<h_0\to C=h_0$; $C_0>2h_0\to C=2h_0$; tính lại $Q_{u,min}$ | 02 Bước 11a |
| B5 | Không có dữ liệu $Q$ riêng từ ETABS | KHÔNG bỏ qua kiểm cắt. Phải lấy $Q$ thật; **với nguồn ETABS design summary: `tinh_cot_dai` bị chặn, chỉ đề xuất Ø8 cấu tạo kèm cờ** (module 00, điều 4) | Bảng I |
| B6 | Dầm chịu **đồng thời cắt + xoắn** | Không cộng đơn giản; kiểm riêng 7.36–7.38; đai xoắn **kín**, nối ≥$30d_{sw}$ | R47–R50 |
| B7 | Vị trí: $L/4$ gần gối vs giữa nhịp | $s_1=\min(h/2;300)$ [A: $h_0/2$] gần gối; $s_2=\min(3h/4;500)$ giữa. ⚠ cũ ghi $\min(0{,}5h_0;300)$/$\min(0{,}75h_0;500)$; mới thêm $\min(h/3;500)$ khi $h>450$ — lấy **chặt hơn** | 02 Bước 11d; 06 B8 |

### 60. Dầm — cốt treo và giật đứt: trường hợp đặc biệt (Bảng C)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
|:--|:--|:--|:--|
| C1 | Dầm phụ gác lên dầm chính ($F$ tập trung) | **BẮT BUỘC cốt treo** dù đã đủ đai: $F(1-h_s/h_{dc})\le\sum R_{sw}A_{sw}$ | R23; DM-03 |
| C2 | Hai dầm giao nhau **cùng cao độ** | $F\le\sum R_{sw}A_{sw}$, đoạn dài $3b$ | DM-04 |
| C3 | Phân bổ cốt treo | ≥2/3 $A_{sw}$ trong $(b+2h)$ dầm CHÍNH; còn lại trong $h/3$ dầm PHỤ. ⚠ chính văn mới: $S=b_{dp}+2h_s$ — dùng vùng **rộng hơn** | DM-03 |

### 61. Cột — thép dọc chịu nén/kéo lệch tâm: trường hợp đặc biệt (Bảng D)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
|:--|:--|:--|:--|
| D1 | $N$ là lực **NÉN** (phổ biến) | Tiếp tục D2–D6 | — |
| D2 | $N$ là lực **KÉO** | **KHÔNG** áp dụng công thức nén lệch tâm. **CHUYỂN HẲN** sang **KÉO LỆCH TÂM** (03, 14a). Lỗi hay gặp nhất nếu chỉ đọc $\|N\|$; **tool `tu_kiem_tra` báo lỗi khi $N\le0$ ⇒ dừng, báo kỹ sư** | R12 |
| D3 | $l_0/h\le20$ **VÀ** $e_0\le h/30$ | Công thức nén đúng tâm (6.3–6.4) | 03 14c |
| D4 | Lệch tâm LỚN: $2a'\le x\le\xi_Rh_0$ | $A_s=A_s'=[Ne-R_bbx(h_0-0{,}5x)]/[R_{sc}(h_0-a')]$ (5.30) | 03 Bước 7a |
| D5 | $x<2a'$ | **KHÔNG** dùng (5.30); dùng $A_s=A_s'=Ne'/[R_s(h_0-a')]$ (5.31) | 03 Bước 7a |
| D6 | Lệch tâm BÉ: $x>\xi_Rh_0$ | Xác định LẠI $x$ (7b, **ưu tiên Cách 2**), rồi thế vào (5.30) | R9 |
| D7 | $l_0/h>4$ (⚠ cũ: ≥4) | **PHẢI** nhân $e_0$ với $\eta$ TRƯỚC khi tính $A_s$. $4<l_0/h\le7$: $\eta\approx1{,}03$–$1{,}08$ | R7; ⚠ tool $\eta=1$ |
| D8 | $e_a$ chi phối ($e_1<e_a$) | $e_0=e_a=\max(l/600,h/30,10)$ — **không để $e_0\to0$**. ($l$ không phải $l_0$) | 03 Bước 4 |
| D9 | $A_s$ âm | Cấu tạo tối thiểu $A_s=A_s'=\mu_{min}bh_0$; ≥402 ($b\le400$)/603 ($b>400$) | 03 Bước 8 |
| D10 | $\mu_t$ vượt 4% (hoặc 8% tại nối) | **KHÔNG** tăng thép tiếp. **TĂNG TIẾT DIỆN/cấp bê tông**, tính lại | R10 |
| D11 | $l_0/i>120$ (hoặc $\lambda_b>31$) | **KHÔNG ĐẠT ổn định** — không xử lý bằng thép: tăng tiết diện/giảm $l_0$ | 03 Bước 3 |
| D12 | Nén lệch tâm **XIÊN** (2 phương) | Ngoài phạm vi (lệch tâm phẳng): **dừng và hỏi** (14b) | R42 |
| D13 | Cột tròn/vành khuyên | **KHÔNG** dùng Bảng D (chỉ chữ nhật); Phụ lục F TCVN 5574:2018 — **chưa trích**; dừng | R42 |

### 62. Cột — cốt đai: trường hợp đặc biệt (Bảng E)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
|:--|:--|:--|:--|
| E1 | $\mu_t\le1{,}5\%$ ⚠ (D: thép **nén** $\le1{,}5\%$; A: $\mu_t\le3\%$) | $s\le\min(15d_{min};500)$; $d_{sw}\ge\max(0{,}25d_{max};6)$. ⚠ cũ ghi $d_{min}$ hay $d_{dọc,min}$: lấy thanh **nhỏ nhất kể cả cốt cấu tạo** | 03 Bước 12b |
| E2 | $\mu_t>1{,}5\%$ | $s\le\min(10d_{min};300)$ | CT-03 |
| E3 | Bề rộng mặt bên $>400$ **HOẶC** $>4$ thanh/mặt | Cần **đai phụ**; chỗ uốn cách nhau ≤400 | CT-02 |
| E4 | Có $Q$ cột từ ETABS | Tính đai như Bảng B, lấy **nhỏ hơn** giữa cấu tạo và tính toán | 03 Bước 12a |
| E5 | Kháng chấn (DCM) | E1–E4 **bị THAY THẾ** bởi Bảng H dòng H2 (vùng tới hạn): $s=\min(b_0/2;175;8d_{bL})$ | module 07; R36 |

### 63. Nút khung: trường hợp đặc biệt lựa chọn kiểu cấu tạo (Bảng F)

Agent **tự xác định loại nút** từ vị trí hình học và dấu nội lực (không có trong bảng $A_s$ ETABS ⇒ **dễ bị bỏ sót nhất**). Chi tiết hình, số liệu và mã NK: module 05.

| # | Điều kiện | Xử lý | Nguồn |
|:--|:--|:--|:--|
| F1 | Xác định: góc/giữa? mái/trung gian? | → F2–F3 (góc+mái), F4 (giữa+mái), F5–F6 (trung gian) | 05 quy trình |
| F2 | Góc, mái, nút **ĐÓNG** | Tra $e_0/h$ (F2a–c) | NK-01…03 |
| F2a | $e_0/h\le0{,}25$ | Cốt kéo dầm ra sát mép ngoài cột, uốn xuống $L_{an}$; đai cột đến dưới mặt sàn | NK-01 |
| F2b | $0{,}25<e_0/h\le0{,}5$ | + ≥2 thanh kéo xuống quá đáy dầm $L_{an}$ | NK-02 |
| F2c | $e_0/h>0{,}5$ | Thép cột lên mép trên dầm; thép dầm neo sâu ($2L_{an}$ ⚠); không cắt quá 2 thanh/tiết diện | NK-03 |
| F3 | Góc, mái, nút **MỞ** | $\mu\le2\%$ ⇒ chữ U; $\mu>2\%$ ⇒ + chéo gia cường ~20% | NK-06/07 |
| F3a | Dầm cao >1,5× cao cột tại nút góc | **BẮT BUỘC** thêm đai kín/chữ U (không phụ thuộc $e_0/h$, $\mu$) | NK-05 |
| F4 | Giữa, mái | Thép cột kéo lên mặt dầm $L_{an}$ | NK-08 |
| F5 | Biên, trung gian: $\tan\beta=(h_2-h_1)/h_d$ | Không đổi ⇒ thường (đai $\le\min(300;10d_{min})$ trong $L_{an}$); $\le1/6$ ⇒ chạy thẳng/bẻ nghiêng nối chồng; $>1/6$ ⇒ kéo lên mặt dầm + neo $L_{an}$ | NK-09…11 |
| F6 | Giữa, trung gian | Không đổi/cùng cao ⇒ liên tục qua nút; đổi nhiều ⇒ như F5; khác cao độ ⇒ neo sâu | NK-12/13 |
| F7 | Nút cột–móng | Thép chờ tương đương thép cột; nối so le, ≤50%/lần | NK-16 |
| F8 | Gãy khúc, góc lõm $\alpha$ (⚠ cũ ghi $\beta$) | $\ge160°$ ⇒ liên tục + cốt ngang; $<160°$ ⇒ tách rời, neo riêng, cốt ngang ôm trên đoạn $S$ | NK-14/15 |
| F9 | Kháng chấn — MỌI nút | F1–F8 là nền, CỘNG Bảng H dòng H3 (đai nút ≥ vùng tới hạn cột) | NK-20 |

### 64. Chịu lực cục bộ, neo và nối thép: trường hợp đặc biệt (Bảng G)

| # | Điều kiện | Xử lý | Nguồn |
|:--|:--|:--|:--|
| G1 | $L_{an}$ tính ra $<15d$ hoặc $<200$ | $L_{an}=\max(\text{tính được};15d;200;0{,}3L_{0,an})$ — **bốn** giá trị sàn (tool thiếu $0{,}3L_{0,an}$) | 02 Bước 15 |
| G2 | Thép TRƠN chịu kéo, không đủ $L_{an}$ thẳng | Bắt buộc **móc** uốn (U/L); thép gờ có thể bỏ móc nếu đủ $L_{an}$ | 04 9.5.1 |
| G3 | Cần nối — chọn phương pháp | $\le40$ đủ không gian ⇒ **nối chồng**; tốc độ/nhà máy ⇒ **hàn**; lực đảo dấu/Ø lớn ⇒ **ống ren** | 04 9.5.2 |
| G4 | >4 thanh/cạnh — vị trí nối | **KHÔNG** nối cùng mặt cắt; so le, ≤50%/lần, cách $\ge1{,}5L_{an}$ | CT-06 |
| G5 | Nén cục bộ, diện chịu tải GẦN BIÊN | $A_{b,max}$ giới hạn bởi biên — dùng đúng 1 trong 6 sơ đồ hình học | ngoài phạm vi — tra TCVN |
| G6 | $\varphi_b=0{,}8\sqrt{A_{b,max}/A_{b,loc}}$ | $>2{,}5$ ⇒ chặn 2,5; $<1{,}0$ ⇒ chặn 1,0 | ngoài phạm vi |
| G7 | Chọc thủng — ĐỒNG THỜI $F$ và $M$ | Tương tác $F/F_{b,u}+M/M_{b,u}\le1$; $M/M_{b,u}$ chặn $\le0{,}5F/F_{b,u}$ | ngoài phạm vi (sàn/móng) |
| G8 | Chọc thủng — chưa có cốt ngang | Bổ sung cốt ngang (bước $\le h_0/3$, $\le300$); chỉ tính khi $F_{sw,u}\ge0{,}25F_{b,u}$ | ngoài phạm vi |

### 65. Công trình kháng chấn: rẽ nhánh toàn bộ luồng xử lý (Bảng H)

Cờ cấp cao nhất — BẬT thì gần như mọi bảng A–G có phiên bản thay thế/bổ sung. Cờ **do người dùng khai tường minh** (R31).

| # | Điều kiện | Xử lý | Nguồn |
|:--|:--|:--|:--|
| H1 | Cờ = TẮT (mặc định) | Dùng nguyên Bảng A–G | — |
| H2 | Cờ = BẬT — CỘT đầu/chân | $l_{cl}/h_c\ge3$: $l_{cr}=\max(h_c;l_{cl}/6;450)$; $<3$: toàn bộ. Trong $l_{cr}$: Ø≥6, $s=\min(b_0/2;175;8d_{bL,min})$ — Bảng E KHÔNG áp dụng | R36; module 07 |
| H3 | Cờ = BẬT — DẦM gần nút | ⚠ cũ: $l_{cr}=1{,}5h_w$ (DCM); **mới: DCM $h_w$, DCH $1{,}5h_w$** — chưa rõ cấp dẻo ⇒ lấy $1{,}5h_w$. Đai dày hơn Bảng B; $\rho_{max}$ riêng (**tra TCVN 9386**) | R32 |
| H4 | Cờ = BẬT — NÚT dầm–cột | Đai ngang nút KHÔNG nhỏ hơn vùng tới hạn cột liền kề (chồng lên Bảng F) | R38 |
| H5 | Cờ = BẬT — vị trí NỐI thép cột | CẤM hàn chồng trong vùng tới hạn; nối thường $s=\min(h/4;100)$; $A_{st}=s(d_{bL}/50)(f_{yld}/f_{ywd})$; móc 135°, đoạn sau ≥$10d_{sw}$ | R40 |
| H6 | Cờ = BẬT — $N$ chuyển KÉO | $L_{an}$ **tăng 50%** | CT-10 ⚠ |
| H7 | Cờ = BẬT — kiểm tổng thể | "Cột khỏe–dầm yếu" $\sum M_{Rc}\ge1{,}3\sum M_{Rb}$ (⚠ cũ: hệ số thiếu; **mới 1,3**) | R39 |

### 66. Vận hành Rule Engine: trường hợp dữ liệu/quy trình đặc biệt (Bảng I)

| # | Điều kiện | Xử lý | Nguồn |
|:--|:--|:--|:--|
| I1 | $A_{s,yc}=0$ hoặc "N.A." | KHÔNG hiểu là "không cần thép": luôn $A_{s,tk}=A_{s,min}$ | A2 |
| I2 | Cột không có $Q$ (thiếu, không phải $Q=0$) | Phân biệt rõ; thiếu ⇒ cấu tạo TẠM + cờ, KHÔNG dùng làm kết quả cuối | E4 |
| I3 | Quy ước As cột trong ETABS chưa rõ | Đối chiếu ≥1 ví dụ tay trước khi áp dụng hàng loạt — **ĐÃ đối chiếu: As = MỘT PHÍA** (Khung Trục 5, mục 71–72, module 09) | module 00 |
| I4 | Tiết diện không phải bội số 50/100 | Cảnh báo "không đúng mô-đun ván khuôn" — không tự sửa | 02, Ch.2 |
| I5 | 2 vị trí liền kề $A_s$ chênh ĐỘT NGỘT dù tải gần như không đổi | Dấu hiệu LỖI MÔ HÌNH ETABS — cờ "kiểm tra lại mô hình" | kinh nghiệm |
| I6 | Khoảng hở thông thủy tính ra vi phạm (<25 dầm, <50 cột) | KHÔNG xuất bản vẽ vi phạm: (a) tăng Ø giảm số thanh → (b) thêm lớp → (c) tăng bề rộng | R4 |
| I7 | ETABS dùng mã nước ngoài (SP 63.13330.2012…) thay TCVN | CHẤP NHẬN — chỉ cần đối chiếu ký hiệu vật liệu khớp | thực hành VN |

### Bảng K — Cổng hình học nút và phạm vi áp dụng (mới, theo Chương 14–15; chi tiết module 09)

| # | Điều kiện | Xử lý | Luật |
|:--|:--|:--|:--|
| K1 | **Trước khi xuất bản vẽ nút:** số thanh dầm một lớp > số khe lọt giữa thép cột (14.2), cho thép trên, dưới và dầm vuông góc | **KHÔNG vẽ**; trả phương án 1–4 để kỹ sư chọn | R41 |
| K2 | Công trình/cấu kiện thuộc dòng "Không", "Chưa đủ", "Chỉ sàng lọc" ở 14.1 (xoắn đã có quy trình R47–R50) | **DỪNG**, ghi lý do và danh sách việc cần làm; không điền số | R42 |
| K3 | Hai dầm cắt nhau cùng cao độ mặt trên | Tính lại $h_0$ dầm thấp ($a'=a+d_{kia}$); chọn lại thép nếu $M_u<M$ | R43 |
| K4 | Tiền lượng hoặc $\mu$ ngoài khoảng 14.4 | **Cảnh báo** (không chặn) kèm số và khoảng tham chiếu | R44 |
| K5 | Mọi con số đưa vào dữ liệu bản vẽ | Gắn `basis` ∈ {TCVN, thuc_hanh, uoc_luong, can_xac_nhan}; có `uoc_luong`/`can_xac_nhan` ⇒ cờ "chưa đủ để phát hành" | R45 |
| K6 | Hoàn tất | **Không in "ĐẠT"** khi còn cờ R41–R45 hoặc ⚠ ở Chương 13 | R46 |
| L1 | Dầm có $\|T\|>0$ trong bất kỳ tổ hợp nào | Phân loại cân bằng/tương thích; không xác định ⇒ coi cân bằng và **hỏi kỹ sư**; không tự giảm $T$ | R47 |
| L2 | Có xoắn cần tính | Kiểm 7.21; không đạt ⇒ tăng tiết diện | R48 |
| L3 | Có xoắn cần tính | Chọn đai theo 15.1.3 bước 3; thép dọc từng biên bước 4; kiểm bốn cạnh bước 5 | R49 |
| L4 | Đồng thời có $M$ hoặc $Q$ | Kiểm riêng 7.36, 7.37, 7.38; bước đai nhỏ nhất thoả cả ba; cờ `can_xac_nhan` | R50 |
| L5 | $L_{ef}/h<3$ | **DỪNG**: dầm cao ⇒ mô hình thanh–giằng | R51 |
| L6 | Có lỗ mở xuyên dầm | **DỪNG**: không chọn vị trí, kích thước, thép quanh lỗ | R52 |

### 67. Tóm tắt: sơ đồ ra quyết định tổng thể (dạng mã giả — đã cập nhật)

```
KIỂM phạm vi [R42]: dầm cao? lỗ mở? xoắn? cột xiên/tròn? kháng chấn? → DỪNG/HỎI nếu thuộc diện
CHO MỖI phần tử (dầm hoặc cột):
  XÁC ĐỊNH loại, tiết diện (b,h), vật liệu → GỌI tra_vat_lieu (không bao giờ tự nhớ)
  NẾU DẦM:
    CHO MỖI vị trí (gối trái, giữa nhịp, gối phải):
      LẤY As_yc, N (nếu có) TỪ ETABS
      NẾU |N| > 0,1·Rb·b·h0: CHUYỂN nén/kéo lệch tâm [A5]
      NẾU As_yc = 0 HOẶC N.A.: As_yc = 0 [I1]
      As_tk = MAX(As_yc, As_min=0,1%·b·h0) [A2]
      NẾU αm > αR (ETABS báo): CẢNH BÁO "cần cốt kép/tăng tiết diện" [A3, R1]
      GỌI chon_thep_doc → KIỂM khoảng hở theo bảng 8b [I6]
    NẾU Q có: GỌI tinh_cot_dai; NẾU Q: KHÔNG CÓ: bỏ, đề xuất Ø8 cấu tạo [B5]
    NẾU có dầm phụ gác lên: ghi cốt treo (DM-03) — chưa có tool [C1]
    GỌI tinh_neo_noi (so tay 0,3·L0,an)
    GỌI tu_kiem_tra; dat=false & còn lượt ⇒ chọn lại; hết lượt ⇒ hoi_nguoi_dung
  NẾU CỘT:
    LẤY N, M TỪ ETABS; NẾU N là lực KÉO: DỪNG/kéo lệch tâm [D2, R12]
    l0 = 0,7·H (khung nhiều tầng toàn khối; tầng 1 từ mặt ngàm) ⚠ không dùng 0,8L [03 Bước 3]
    NẾU l0/h > 4: η cần tính — tool đặt η=1 ⇒ CỜ (l0/h>7 ⇒ HỎI)
    GỌI chon_thep_doc(loai="cot", As_target=As_yc [mỗi phía], h) → tinh_cot_dai → tinh_neo_noi → tu_kiem_tra
    KIỂM μ_t ≤ 4% (8% nối) [D10]; ĐỘ MẢNH [D11]
CHO MỖI nút dầm–cột: TRA Bảng F (module 05) → ghi cấu tạo nút + KIỂM hình học 14.2/14.3 [K1, K3]
CHO MỖI vị trí neo/nối/lực cục bộ: ÁP DỤNG Bảng G
NẾU cờ kháng chấn = BẬT: ÁP DỤNG Bảng H + module 07 [R31–R40] (⚠, không phát hành)
GHI kết quả + basis + cờ [R45]; KHÔNG in "ĐẠT" khi còn cờ [R46]
```

## Chỉ mục R1–R52 — nơi định nghĩa và trạng thái tool

| Nhóm | Luật | Nơi định nghĩa | Trạng thái tool |
|:--|:--|:--|:--|
| Chọn thép dầm/cột | R1–R13 | module 08 (bảng 10.4 ở trên) | R3, R5, R6, R7(chỉ ≤4), R9, R11, R12 có tool; R1, R2, R8, R10, R13 không/ một phần |
| Bố trí thép | R14–R30 | module 06, mục 12.7 | **không có tool** |
| Kháng chấn | R31–R40 | module 07, mục 13.10 | **không có tool, không có cờ** |
| Cổng chặn | R41–R46 | module 09, mục 14.6 | **không có tool** (R45: chưa có trường `basis` trong hợp đồng dữ liệu) |
| Xoắn, dầm cao, lỗ mở | R47–R52 | module 09, mục 15.4 | **không có tool**; R51, R52 là luật dừng |

**Danh sách đầy đủ để tra nhanh:** R1 • R2 • R3 • R4 • R5 • R6 • R7 • R8 • R9 • R10 • R11 • R12 • R13 • R14 • R15 • R16 • R17 • R18 • R19 • R20 • R21 • R22 • R23 • R24 • R25 • R26 • R27 • R28 • R29 • R30 • R31 • R32 • R33 • R34 • R35 • R36 • R37 • R38 • R39 • R40 • R41 • R42 • R43 • R44 • R45 • R46 • R47 • R48 • R49 • R50 • R51 • R52.
