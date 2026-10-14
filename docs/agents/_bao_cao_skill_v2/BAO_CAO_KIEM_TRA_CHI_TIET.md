# BÁO CÁO KIỂM TRA CHI TIẾT — bản vẽ do hệ thống sinh ra so với bản mẫu Khung trục 5

Phạm vi: so `BoTriThep_KhungTruc5_mau.pdf` (bản mẫu) với `KHUNG_TRUC5_GIA_*.pdf` (bản hệ thống vừa vẽ, mock-LLM trên AutoCAD).
Nguồn đối chiếu số liệu: thuyết minh `inputvanban2.pdf` (trang 34–50, bảng 26–28), file ETABS mẫu.
**Trạng thái: chỉ kiểm tra và chẩn đoán. Chưa sửa code, chưa sửa skill. Chờ chỉ đạo.**

Nhãn: [đo] = đo/nhìn trực tiếp trên PDF phóng to; [mã] = đọc từ mã nguồn; [suy luận] = suy ra từ hai mục trên, chưa kiểm chứng riêng.

---

## A. LỖI VỀ CHI TIẾT UỐN THÉP / NÉT VẼ (mặt đứng khung)

| # | Vị trí | Bản mẫu [đo] | Bản hệ thống | Nguyên nhân [mã] |
|---|---|---|---|---|
| A1 | Mọi thanh thép dọc | Thanh là **hai nét song song** (thân thanh có bề dày đúng Ø theo tỉ lệ), góc uốn **bo cung tròn** | Một nét đơn, dày REBAR_MAIN, **góc nhọn** | `mat_dung.py` dùng `v.doan` / `v.duong` (polyline thẳng, đỉnh gấp). Chưa có hàm vẽ cung uốn, dù skill 04/05 đã có `duong_kinh_uon_toi_thieu` (từ `tinh_neo_noi`) |
| A2 | Chân cột tầng 1 trong đài | Thép chờ **uốn chữ L nằm trên lưới thép đáy**, thấy rõ hai nét + chấm lưới thép bên dưới | Chân L vẽ tại `y_dai+75`, còn lưới thép tại `y_dai+70` → **gần như trùng nhau**, không đọc được | `mat_dung.py` dòng ~71–76 và ~88–91: cùng cao độ, chiều dài chân cố định 200 |
| A3 | Nút mái biên (cột + dầm) | Thép cột tầng trên cùng **uốn vào dầm** 500 mm (thanh số 5 "500\|3200"); thép trên dầm **móc xuống cột**; hai lớp cung lồng nhau | Thép cột chạy thẳng đến đỉnh cột rồi cụt; thép dầm có móc thẳng 15d, không lồng nhau | `mat_dung.py` không có nhánh "cột tầng trên cùng uốn vào dầm"; chiều dài neo `L_an` (500 cột / 600 dầm trong thuyết minh Bảng 28) chưa đi vào hình vẽ |
| A4 | Nút mái giữa | Thép cột uốn vào dầm hai phía; thép dầm gối xuyên suốt | Chỉ có thanh trên chạy suốt | như A3 |
| A5 | Cốt đai | Đai nét **dày**, có **móc 135°** (vạch chéo nhỏ ở góc) | Đai là đoạn thẳng nét mảnh, không có móc | `mat_dung.py` dòng ~99, ~132: `v.doan(...L_DAI)` |
| A6 | Phân cấp nét | Đai dày hơn thép dọc; thép dọc mảnh hai nét | **Đảo ngược**: thép dọc dày (0,5), đai mảnh (0,35) | Cấu hình layer ở `co_so.py`/`backend_com.py` |
| A7 | Thép dầm qua nút | Thép dưới dầm đi vào cột, neo thẳng đúng `L_an`; thép gia cường gối **dừng đúng điểm cắt** có kích thước | Dừng đúng vị trí nhưng ghi chiều dài bằng quy tắc chung `_x_cat`, không lấy từ tính toán | `ke_hoach.py` dùng `_lam_tron_50`, chưa đối chiếu `neo_noi` của agent |
| A8 | Cạnh móng, lớp bê tông lót | Đài, lót, lưới thép đáy đủ, đai trong đài | Có, nhưng lưới đáy chỉ 1 nét + chấm, không có thép đáy theo hai phương | `mat_dung.py` dòng ~66–69 |

## B. THIẾU HẲN (bản mẫu có, bản hệ thống không có)

1. **Mặt bằng kết cấu**: dầm sàn tầng 2–3–4 và mái (bản mẫu có), cùng bảng K / phân loại ô sàn. Không có dữ liệu mặt bằng trong đầu vào ETABS mẫu, và không có module vẽ.
2. **Bảng thống kê**: tiêu đề cột đã đủ 8 tên, nhưng thiếu: ô gộp tiêu đề, **hình dạng thanh có ghi kích thước từng đoạn**, dòng **T.BỘ = 1CK × 12 khung** (hệ thống không có khái niệm "số khung tương tự").
3. **Chi tiết nút 3D** (isometric): bản hệ thống có nhưng thô; thiếu đai nút, thiếu thép uốn đúng hình.
4. **Ghi chú chung / yêu cầu thi công** theo đúng khối chữ bản mẫu: đã có nhưng chưa khớp từng dòng (lớp bảo vệ, mác bê tông, nhóm thép, chiều dài nối).
5. **Khổ giấy**: hệ thống tự chọn A0 tỷ lệ 1:50 cho khung này, bản mẫu là A1. Do bề rộng khối phải `RONG_KHOI_PHAI=7900` và thứ tự ưu tiên `UU_TIEN`.

## C. SẮP XẾP / VỊ TRÍ CHỮ (lộn xộn)

- Còn khoảng 13 chỗ nhãn chồng/cắt vạch dầm [đo từ lần chạy trước]. Nguyên nhân: bản mẫu bố trí **theo từng tiết diện cụ thể**, còn bộ quy tắc D1–D6/C1–C3 là bình quân đo từ bản mẫu; khi dầm ngắn (nhịp 1500 B–C) khoảng trống không đủ → `Cho` đẩy nhãn lệch.
- Nhãn kích thước mặt cắt dầm bị đè lên nét đai (mặt cắt 1–1, 2–2): `mat_cat.py` đặt nhãn cố định, chưa dùng bộ tránh va chạm `Cho`.

## D. CHỌN THÉP — chưa giống kỹ sư

Đối chiếu số liệu thật:

| Phần tử | Thuyết minh/ bản mẫu | Bản hệ thống (mock) | Nhận xét |
|---|---|---|---|
| Cột trục A, tầng 2 (PT 1) | 3Ø18 mỗi phía = 6Ø18 (As_yc 752,65 → 763,41) | Ø18 (đúng) | Đúng Ø; số thanh phụ thuộc As_yc từng mặt |
| Cột A tầng 3 (PT 2) | Thuyết minh Bảng 26: 2Ø18 mỗi phía; nhãn trên bản mẫu: 4Ø18 | Ø16 | **SAI, đã xác nhận**. As 382,13 mm² đủ với 2Ø16 (402), nhưng thuyết minh chọn 2Ø18 vì **cột A và B cùng tiết diện, cùng tầng thì lấy chung theo cột bất lợi hơn** (B/PT 15 cần 503,59 → 2Ø18). Quy tắc này khớp cả 4 tầng (xem mục G) |
| Cột B tầng 3 (PT 15) | 2Ø18 mỗi phía (503,59 → 508,94) | Ø18 | Đúng |
| Dầm 32 (tầng 2) | Gối 3Ø18 (686/654), nhịp 2Ø18 (474) | Gối Ø18, nhịp Ø18 | Đúng |
| Dầm 45 (tầng 2) | Gối trái 2Ø18 (439,35), nhịp 2Ø16 (292,01), gối phải 2Ø18 (388,69) | gối trái Ø18, nhịp Ø16, gối phải Ø16 | **Không khớp ở gối phải**: 388,69 mm² vẫn đạt với 2Ø16 (402 mm²), nhưng thuyết minh chọn 2Ø18 để hai gối **đối xứng/cùng Ø** (thanh trên chạy suốt). Đây đúng là lỗi "chọn độc lập từng vị trí" (D1) |
| Dầm 34, 43, 36… | Toàn 2Ø16 / 3Ø16 | Ø16 | Đúng |

**Điểm yếu thật sự (không phải Ø từng phần tử mà là cách "gom thép")** [suy luận từ so sánh bản mẫu]:

D1. Rule Engine chọn **từng vị trí độc lập, Ø nhỏ nhất đạt**. Kỹ sư thực tế **gom nhóm**: giữ ≤2–3 loại Ø trong một khung; thanh dọc cột và thanh trên dầm liên tục dùng cùng Ø; không để Ø dầm suốt = max(min) giữa các gối (hiện `ke_hoach.py` dùng "max của min Ø các gối", dễ ra Ø trộn).
D2. **Cột: liên tục theo tầng.** Bản mẫu đặt 6Ø18 → 4Ø18 → 4Ø16 → 4Ø16 (thép tầng dưới nối lên tầng trên bằng nối chồng `L_lap`). Hệ thống chọn từng cột độc lập nên tầng 2 của cột A/B có thể khác chuỗi mẫu; chưa có quy tắc "không giảm Ø quá 2 mm giữa 2 tầng" / "nối chồng chỉ ở 1/3 giữa cao tầng".
D3. **Dữ liệu ETABS**: dầm không có Q (`khong_co_Q`) nên cốt đai chỉ theo cấu tạo, trong khi thuyết minh kiểm tra cắt (Q_max = 107,92 kN > Q_b,min → đai d6a150 hai đầu). Đây là **thiếu dữ liệu đầu vào**, không phải lỗi thuật toán; cần cảnh báo rõ trong bản vẽ.
D4. (ĐÃ SỬA sau khi đọc thuyết minh đầy đủ) Thuyết minh thiết kế cột **đối xứng, tính mỗi phía** (phía bề rộng b); "2d16" là 2 thanh mỗi phía = 4 thanh góc, kể cả cột C 220×220. Không có thanh giữa cạnh. Nhận định trước đây "cột vuông phải 4 phía" là **sai**.
D5. **Neo/nối**: thuyết minh làm tròn L_an lên bội 100 (500 cột / 600 dầm) kèm giá trị tối thiểu 15d, 200; hệ thống dùng giá trị tính toán thô.

## G. LOGIC CHỌN THÉP CỦA THUYẾT MINH (đọc đủ 50 trang `Thuyet minh tam khao.pdf`)

Nhãn: [thuyết minh] = ghi rõ trong văn bản; [suy ra] = rút từ số liệu các bảng 26–28, thuyết minh không viết ra.

**G1. Nguồn As cần thiết**
- Cột: lấy **lớn nhất trong 3 cặp nội lực** (Mmax–Ntư, Nmax–Mtư, emax) của mỗi phần tử [thuyết minh, Bảng 24/26]. Thiết kế **đối xứng** (As = A's), Rs = Rsc = 435 MPa (CB500-V) [thuyết minh].
- Dầm: tính **tại mép cột (mặt cắt 0,15 m)**, không tại trục; nhịp tính tiết diện chữ T (cánh chịu nén), gối tính chữ nhật b×h [thuyết minh]. Cánh: Sf' = min(½ khoảng thông thủy giữa sườn, L/6) [thuyết minh].
- Giả thiết a = 30 mm, h0 = h − a; **sau khi chọn thép phải kiểm lại h0 thực** (a thực theo trọng tâm các hàng) và **khoảng hở thông thủy** giữa các thanh (c1 = (b − 2c0 − nφ)/(n−1) ≥ 50 mm, c0 = 20) [thuyết minh].
- Kiểm tra μmin ≤ μ ≤ μmax = 3 % (μmin nội suy theo độ mảnh λh); cột kiểm tra thêm bằng biểu đồ tương tác, mọi cặp nội lực phải nằm trong [thuyết minh].

**G2. Quy tắc chọn số thanh/đường kính** (toàn bộ do [suy ra] từ Bảng 26–27)
1. Toàn khung chỉ dùng **Ø16 và Ø18** cho thép dọc, **Ø6** cho đai: hạn chế số loại đường kính.
2. Tối thiểu cấu tạo **2Ø16** mỗi phía/mỗi lớp, kể cả khi As cần chỉ 18–120 mm² (dầm 39: 18,33 → 2Ø16; cột 21: 71,61 → 2Ø16).
3. Chọn tổ hợp (n, Ø) với n ≥ 2, **một hàng** (n ≤ 3), As chọn ≥ As cần, và **nhẹ nhất**: dầm 32 nhịp cần 473,67 → chọn 2Ø18 (509; ≈4,0 kg/m) thay vì 3Ø16 (603; ≈4,7 kg/m); dầm 34 gối cần 546,78 → 3Ø16 vì 2Ø18 (509) không đủ.
4. **Thép trên dầm chạy suốt ⇒ hai gối cùng bố trí theo gối lớn hơn**: dầm 45 gối trái cần 439,35 → 2Ø18, gối phải chỉ cần 388,69 (2Ø16 đã đủ) nhưng vẫn chọn 2Ø18. Ngược lại thép dưới nhịp chọn riêng (292,01 → 2Ø16).
5. **Cột cùng tiết diện, cùng tầng ⇒ lấy chung theo cột bất lợi hơn** (A và B): tầng 2: 3Ø18/phía (cả hai), tầng 3: 2Ø18 (cả hai, dù A chỉ cần 382), tầng 4 và mái: 2Ø16. Khớp 4/4 tầng. Cột C (220×220) tính riêng: 2Ø18 ở tầng 2 (As 420,11 > 402), còn lại 2Ø16.
6. Giảm thép lên cao: **giảm số thanh trước, giảm Ø sau** (A: 3Ø18 → 2Ø18 → 2Ø16 → 2Ø16 mỗi phía; trên bản mẫu 6Ø18 → 4Ø18 → 4Ø16 → 4Ø16).
Lưu ý trung thực: thuyết minh có chỗ chưa nhất quán (ví dụ μ dầm 34 gối ghi 0,74 là của 3Ø18, không khớp 3Ø16 đã chọn; Lan chọn nhỏ hơn Lan tính toán ở một số nút, mục G4). Bản mẫu là **tham chiếu**, không phải chân lý tuyệt đối.

**G3. Cốt đai**
- Cột [thuyết minh]: d ≥ max(0,25φmax; 5) → Ø6; trong đoạn nối chồng a ≤ min(10φ; 500) → chọn 150; ngoài đoạn nối chồng a ≤ min(15φ; 500) → chọn 250 (làm tròn xuống bội 50). Vùng nút (Hình 33, 34): ≤ 300 và ≤ 10φmin trên đoạn Lan; còn lại ≤ 500 và ≤ 15φmin.
- Dầm [thuyết minh, chỉ làm cho dầm 32]: kiểm tra Q ≤ 0,3·Rb·b·h0; so Q với Qb,min = 0,75·Rbt·b·h0 (81,43 kN); nếu Q lớn hơn thì tính đai: q_sw = Rsw·n·asw/s ≥ 0,25·Rbt·b ⇒ s ≤ 166 mm → chọn **150** ở hai đầu; giữa dầm theo cấu tạo s ≤ min(3h0/4; 500) = 352 → chọn **200**. Các dầm tầng 3, 4, mái trong Bảng 27 đều ghi a200 (dầm 34 có Q = 99,37 kN > Qb,min mà vẫn a200: thuyết minh không nhất quán chỗ này).
- Trên bản mẫu: 150 chỉ ở dầm tầng 2, vùng gối dài ≈ L/4 (1300 = 5220/4 làm tròn 50), giữa 2620.
- **Nguyên nhân hệ thống ra 48 nhãn Ø6a150 (mẫu 23)**: file ETABS mẫu không có Q của dầm, nên `bo_tri_dai` lấy luật cấu tạo cho mọi dầm → mọi dầm cao 300–500 đều ra 150 ở gối. Thuyết minh có Q (Bảng 25). Đây là thiếu dữ liệu đầu vào, không phải lỗi thuật toán.

**G4. Neo và nút khung (Bảng 28, Hình 31–34)**
- L0,an = Rs·As/(Rbond·us) với Rbond = η1·η2·Rbt = 2,5·1·1,05 MPa ⇒ Ø16: 662,8 mm; Ø18: 745,7 mm [thuyết minh; kiểm lại bằng tay đúng].
- Lan = α·L0,an·As,cal/As,ef, **sàn dưới 15d** (240 mm cho Ø16; 270 mm cho Ø18) [thuyết minh].
- **Lan chọn trên bản vẽ cố định: cột 500, dầm 600** (Bảng 28), kể cả khi Lan tính toán lớn hơn (cột 1: 645,93 → 500; dầm 45 nút 12: 720,81 → 600). Thuyết minh không giải thích; bản mẫu dùng đúng 500/600. [suy ra]
- Loại nút: **nút đóng** (mô men đầu dầm căng thớ trên mọi tổ hợp); phụ thuộc e0/h đầu cột: e0/h > 0,5 → cấu tạo Hình 31 (nút biên mái); nút giữa mái Hình 32 (r ≥ 5φ); nút biên tầng giữa Hình 33; nút giữa tầng giữa Hình 34 [thuyết minh].
- Nút mái biên: thép cột **uốn vào dầm**, thép trên dầm **uốn xuống cột**; ít nhất 2 thanh; đai nút ≤ 500 và ≤ 15φmin; thép dưới dầm vào cột 15φ; đai kết thúc dưới mặt dưới sàn (Hình 31, 33, 34).

---

## E. ĐỀ XUẤT BỔ SUNG SKILL (tổng quát, chưa thực hiện)

Bổ sung từ mục G (ưu tiên cao): quy tắc G2.3–G2.6 vào skill 02/03; G3 vào skill 06; G4 vào skill 05 và Phần Q của skill Vẽ. Lưu ý: các sai khác về chọn thép ở mục D quan sát được trên **mock-LLM do tôi viết** ("Ø nhỏ nhất đạt"); agent thật làm theo skill, nên sửa skill (và nếu cần thêm công cụ gom nhóm) là cách đúng, không phải sửa mock.

| Skill | Nội dung cần thêm |
|---|---|
| Rule Engine 02 (dầm) | Quy tắc **gom nhóm Ø** theo khung (≤3 loại); thanh trên liên tục Ø chung; điều kiện đủ As cho cả gối trái–phải. Cho phép nâng Ø thay vì thêm thanh khi vượt 3 thanh/hàng |
| Rule Engine 03 (cột) | Tính liên tục theo tầng; thép đối xứng; tiết diện vuông 4 phía; bội 2 thanh |
| Rule Engine 05 (nút) | Hai loại: nút **biên/giữa × mái/trung gian** — bảng chiều dài neo làm tròn bội 100; hình thái uốn (cột vào dầm / dầm xuống cột) theo tỉ số e0/h > 0,5 |
| Rule Engine 06 (đai) | Bắt buộc ghi nguồn Q; thiếu Q → cảnh báo đỏ trong bản vẽ |
| Vẽ — Phần Q | Quy cách nét: thép hai nét song song; cung uốn bán kính theo `duong_kinh_uon_toi_thieu`; móc đai 135°; thứ tự lớp nét (đai dày hơn); chân thép chờ trên lưới thép đáy; **mặt bằng + bảng K**; khái niệm "số khung tương tự / T.BỘ" |
| Verification | Kiểm tra: có cung uốn tại mọi nút; thép cột tầng trên cùng có đoạn uốn ≥ L_an; số loại Ø ≤ 3; bảng thống kê có hình dạng và T.BỘ |

## F. ĐIỀU TÔI CHƯA XÁC MINH ĐƯỢC

- Mục 13 của đề gốc (đặc tả báo cáo) chưa bao giờ được gửi; báo cáo này không thể đối chiếu với nó.
- Bản vẽ mẫu là một khung; các quy tắc "gom nhóm" ở D1–D2 rút ra từ **một** mẫu, cần thêm bản mẫu khung khác để chắc.
- Số liệu thuyết minh ở mục D về dầm 45 cần mở lại bảng ETABS gốc trước khi kết luận; tôi chỉ đọc qua thuyết minh.

---

## H. TRẠNG THÁI SAU KHI THỰC HIỆN (đã viết skill + code + test; chưa commit)

Kiểm chứng: 353 test đạt; chạy lại toàn pipeline với LLM giả (không tốn API) trên AutoCAD: kiểm chứng tổng thể ĐẠT, 20/20 phần tử.

| Hạng mục | Việc đã làm | Bằng chứng |
|:--|:--|:--|
| Skill | Rule Engine 02 (Bước 8d), 03 (Bước 9d), 05 (9.7.8), 06 (B8: đai theo Q), 08 (R53–R58), 00 (bản đồ tool); skill Vẽ Phần Q (hình thái nét); skill Kiểm chứng KC-25…27; `DRAWING_AGENT.md`, `RULE_ENGINE_AGENT.md`, `VERIFICATION_AGENT.md` | `tests/test_skill_files.py`, `test_skill_loaders.py` |
| Gom nhóm thép (D1, D2, G2.4–G2.5) | `src/rule_engine/gom_nhom.py` + `src/orchestrator/gom_nhom_khung.py`, gắn vào `pipeline.py` sau Bước A; chỉ nâng thép; tính lại `neo_noi` và `dai` | `tests/test_gom_nhom.py` (7); chạy pipeline giả ra đúng 3 lần gom, **cả ba trùng thuyết minh**: cột 2 → 4Ø18 theo cột 15; dầm 34 gối phải → 3Ø16; dầm 45 gối phải → 2Ø18 |
| Nét thép (A1, A6) | Thanh dọc = hai nét mảnh song song (layer mới `REBAR_BAR`, 0,13 mm); đai đậm hơn (0,35); chấm tiết diện ở hai đầu đai; vạch móc đai | `test_ban_ve_khung.py`, ảnh phóng to PDF |
| Cung uốn (A1, A3, A4) | `src/drawing/to_ve/chi_tiet_thep.py`: đường tim có cung, bán kính theo `duong_kinh_uon_toi_thieu`; nút mái biên/giữa; thanh trên dầm uốn xuống = $h+100$ | `tests/test_chi_tiet_thep.py` (7) |
| Chân cột trong móng (A2) | Chân L cao hơn lưới đáy, lưới vẽ hai nét + hàng chấm; đai trong đài không chạm chân L | ảnh PDF |
| Thanh dưới dầm (A7) | Thẳng, không móc; cảnh báo khi vào cột biên $<15d$ | test |
| Bảng thống kê (B2) | Chiều dài từng đoạn cạnh hình dáng thanh; `so_khung_tuong_tu` (T. BỘ) | test |
| Thiếu Q (D3, G3) | Ghi chú `⚠ THIẾU Q` trên bản vẽ; nhật ký pipeline; Verification KC-27 | test |
| Kiểm chứng cung | `so_cung_uon_ky_vong` → KC-25 (đếm cung layer `REBAR_BAR` trong AutoCAD) | chạy pipeline giả: đạt |
| Prompt Rule Engine | Dặn truyền `As_cal`, `As_ef` cho `tinh_neo_noi` (để $L_{an}$ như thuyết minh) | — |

**Chưa làm / còn hạn chế (trung thực):**
1. **Chưa chạy lại bằng LLM thật** (OpenAI): prompt/skill mới chưa được thử với model thật; kết quả ở trên là LLM giả mô phỏng quy trình. Cần chạy khi webapp không tranh AutoCAD.
2. **Mặt bằng kết cấu sàn, bảng K**: không có dữ liệu đầu vào — chưa vẽ.
3. **Chi tiết nút 3D** (isometric) vẫn thô: thanh một nét, chưa bo cung.
4. **Khổ giấy**: khung này vẫn tự chọn A0 1:50 (bản mẫu A1); chưa thu gọn bố cục.
5. **Nhãn chồng**: còn ~8 chỗ (báo trong `canh_bao`); chưa xử lý thêm.
6. **T. BỘ** không có trong dữ liệu ETABS — người dùng phải nêu (`so_khung_tuong_tu`); mặc định 1.
7. **Chiều dài thanh cột tầng 1** trong bảng gồm đoạn xuống đài + chân L (bản mẫu bỏ phần này): đã chọn cách đầy đủ hơn, nên số liệu **khác** bản mẫu ở nhóm thanh này.
8. **Chân uốn nút** lấy $\max(500;\lceil L_{an}\rceil_{50})$ và $\max(h+100;\lceil L_{an}\rceil_{50})$: **an toàn hơn** thuyết minh ở nút tầng giữa (thuyết minh lấy nhỏ hơn $L_{an}$ tính toán không giải thích); ghi ⚠ khi vượt.
9. Hình thái nút rút từ **một** bản mẫu và Hình 31–34; hướng uốn của thanh cột phía trong ở nút biên mái (cùng chiều dầm, bẻ thấp hơn) là **suy luận từ ảnh**, chưa có số liệu xác nhận.
10. Quy tắc gom nhóm kiểm trên **một** công trình; nên thử thêm khung khác.

---

## I. MẶT CẮT: ĐÃ SỬA THEO BẢN MẪU (đo phóng to 1-1, 2-2, 3-3, 10-10, 13-13)

| Điểm khác biệt | Đã làm | Nơi sửa |
|:--|:--|:--|
| Thanh = vòng rỗng | Chấm **đặc** (đa giác có độ rộng nét) | `co_so._Ve.cham`, `mat_cat.py` |
| Đai không móc | Móc 135° (hai vạch chéo) góc trên phải (dầm) / trên trái (cột) | `mat_cat._moc_dai` |
| Đường bao mặt cắt mảnh | `OUTLINE_CUT` 0,35 (đậm); mặt sàn đậm hơn | `layers.py`, `mat_cat.py` |
| Cánh sàn dài, vạch xiên | Cánh lộ ≈0,3·b, đầu cánh **nét gãy zigzag**; vạch nhô lên mặt sàn | `mat_cat._duong_bao_t`, `canh_ban_cua_t=70` |
| Cao độ: tam giác rỗng đè chữ | Tam giác **đặc**, chữ tầng / cao độ tách | `_Ve.tam_giac_dac`, `_nhan_cao_do` |
| "chữ ⓝ" ngược | "ⓝ nội dung" cho mọi nhãn; thanh trên: khung ngang + thả xuống; thanh dưới: trên (sườn cao) hoặc ngay dưới đáy dầm (sườn thấp); đai: đoạn ngang ngắn | `mat_cat.ve_mat_cat_dam` |
| Cột: đường toả từ vòng tròn xa | Một điểm neo sát mặt cắt → từng thanh → đoạn ngang ngắn; đai thả xuống rồi ngang | `mat_cat.ve_mat_cat_cot` |
| Kích thước 25·170·25 và chữ dính "25170" | Tới **tim đai** (28·164·28); chữ hẹp ra ngoài vạch; chữ đứng xoay 90° (`VeChu.goc_do`) | `mat_cat._chuoi_ngang/_chuoi_doc`, `backend_com` |
| Bong bóng trục xa | Đặt sát (≈15 mm giấy) | `mat_cat.py` |
| 36 mặt cắt | Cột khử trùng theo **cấu hình thép dọc**; chiều dài thanh làm tròn lên bội 50 (chung số hiệu) ⇒ 20 mặt cắt (12 dầm + 8 cột) | `ke_hoach._lap_mat_cat`, `ke_hoach.lap_ke_hoach` |
| Bố cục chiếm A0 | Chi tiết nút 3D thu nhỏ một hàng trên mặt đứng ⇒ **A1 1:50** như bản mẫu | `bo_cuc._thu` |

**Còn lại / hạn chế (trung thực):**
- Cột lệch tâm so với trục (bản mẫu 110 | 190): dữ liệu ETABS không có ⇒ chưa vẽ; mặt cắt cột ghi 150|150 (đối xứng).
- Còn 8 cột mặt cắt thay vì 5 của bản mẫu: số hiệu thanh cột khác nhau theo tầng (chiều dài thanh khác) nên chưa gộp thêm.
- Đoạn đậm dựng đứng ở tim cánh trong 1-1 của bản mẫu: **chưa hiểu** nó biểu diễn gì nên không vẽ.
- Nhãn "6Ø18" cột đè nhẹ lên vạch dóng kích thước phía trên (tương tự bản mẫu); chưa tách.
- Lần chạy kiểm chứng có 2/9 lần trong phiên này trả lỗi từ AutoCAD COM (không lặp lại sau đó); pipeline nay ghi rõ "Lỗi khi kiểm chứng" thay vì im lặng.
- Chưa chạy lại bằng OpenAI thật; mọi kiểm chứng ở đây dùng LLM giả. 360 test đạt; chưa commit.
