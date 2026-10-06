# Ký Hiệu, Nét Vẽ & Quy Tắc Bố Trí Cốt Thép — Bản Vẽ Khung BTCT

Tài liệu này tách riêng phần **ký hiệu, nét vẽ và quy tắc bố trí** ra khỏi `RULES_TCVN5574.md` (vốn có cả
công thức tính toán) — dùng để tra cứu nhanh khi kiểm tra bản vẽ do AI Agent sinh ra, và để đối chiếu trực
quan với `data/samples/BoTriThep_KhungTruc5_mau.pdf`. Nguồn: TCVN 8\-20:2002, TCVN 4612\-88, TCVN7\-1993,
TCVN 5705\-1993 (trích từ giáo trình *Giáo Trình Vẽ Kỹ Thuật Xây Dựng* — Nguyễn Quang Cự, Nguyễn Mạnh Dũng)
và TCVN 5574:2018.

## 0\. Khổ giấy, tỷ lệ & chữ viết kỹ thuật

Ba quy ước nền tảng này áp dụng cho MỌI bản vẽ (kể cả bản vẽ bố trí thép), là phần từng bị bỏ sót ở bản
tổng hợp trước — bổ sung đầy đủ ở đây.

### 0\.1 Khổ giấy & khung tên (TCVN 7285\-2003)

![Khổ giấy vẽ kỹ thuật](img/07_kho_giay_tcvn7285.png)

| Khổ giấy | A0 | A1 | A2 | A3 | A4 |
| --- | --- | --- | --- | --- | --- |
| Kích thước (mm) | 841×1189 | 594×841 | 420×594 | 297×420 | 210×297 |

A0 là khổ lớn nhất (diện tích 1m²); các khổ còn lại lấy bằng cách **chia đôi cạnh dài** của khổ liền kề
lớn hơn. Khổ phụ: cho phép tăng nguyên lần kích thước cạnh ngắn, giữ nguyên cạnh còn lại (VD A3×3, A3×4).

Khung bản vẽ: hình chữ nhật nét liền đậm, cách mép giấy đã xén **10mm** (A0, A1) hoặc **5mm** (A2, A3,
A4); nếu đóng tập, cạnh trái cách mép giấy 25mm. Khung tên: cũng nét liền đậm, đặt ở **góc dưới, bên
phải** bản vẽ, sát khung bản vẽ, cùng hướng đọc với bản vẽ — chứa tên cơ quan/công trình, tên bản vẽ, tỷ
lệ, người vẽ/kiểm tra/duyệt, ngày vẽ.

### 0\.2 Tỷ lệ bản vẽ (TCVN 7286:2003)

| Loại tỷ lệ | Giá trị |
| --- | --- |
| Thu nhỏ | 1:2 — 1:2,5 — 1:5 — 1:10 — 1:20 — 1:50 — 1:100 — 1:200 — 1:500 — 1:1000 |
| Nguyên hình | 1:1 |
| Phóng to | 2:1 — 5:1 — 10:1 — 20:1 — 50:1 — 100:1 |

Tỷ lệ ghi trong khung tên; nếu một chi tiết dùng tỷ lệ khác tỷ lệ chung của bản vẽ, ghi kèm kiểu phân số
ngay cạnh chi tiết đó, ví dụ `A / T.L 10:1`.

### 0\.3 Chữ viết kỹ thuật (TCVN 7284\-2\-2003, bổ sung TCVN 2233\-77)

![Chữ viết kỹ thuật](img/08_chu_viet_ky_thuat.png)

Nét chữ đều, viết thẳng đứng hoặc nghiêng 75° so với dòng kẻ. Khổ chữ h (chiều cao chữ hoa, mm): 2,5 –
3,5 – 5 – 7 – 10 – 14 – 20 – 28 – 40. Quan hệ tỷ lệ: chiều rộng chữ hoa ≈ 6/10 h; chiều cao chữ thường ≈
7/10 h; chiều rộng chữ thường ≈ 5/10 h; chiều rộng nét chữ d \= 1/10 h. Ghi kích thước và ghi chú trên bản
vẽ khổ nhỏ nên dùng h \= 2,5–3,5mm để không rối hình.

## 1\. Nét vẽ

### 1\.1 Bảng 7 loại nét cơ bản (TCVN 8\-20:2002)

![Bảng 7 loại nét vẽ cơ bản](img/01_bang_net_ve_tcvn8_20.png)

| Loại nét | Đặc điểm | Dùng để thể hiện |
| --- | --- | --- |
| A. Nét liền đậm | liền, dày (bề rộng cơ bản s) | Đường bao thấy, cạnh thấy của hình biểu diễn |
| B. Nét liền mảnh | liền, mảnh (≈ s/2 – s/3) | Đường dóng, đường kích thước, đường dẫn, đường bao mặt cắt chập, gạch mặt cắt |
| C. Nét đứt | đoạn ngắn cách quãng đều | Đường bao khuất, cạnh khuất |
| D. Nét gạch chấm mảnh | gạch dài – chấm – gạch dài | Trục đối xứng, đường tâm đường tròn, trục lưới |
| E. Nét cắt | liền đậm, đoạn ngắn có gấp khúc | Đánh dấu vị trí mặt phẳng cắt tưởng tượng (kèm mũi tên \+ tên chữ/số) |
| F. Nét dích dắc | liền, có đoạn zíc‑zắc | Đường cắt lìa dài của cấu kiện khi vẽ rút ngắn |
| G. Nét lượn sóng | đường lượn sóng | Đường cắt lìa / ranh giới giữa hình cắt và hình chiếu |

Quy tắc vẽ nét bắt buộc:

- Trên **một bản vẽ** chỉ dùng 2 bề rộng: đậm (s) và mảnh; tỷ số mảnh/đậm ≤ 1:2. Chọn s trong dãy 0,18 –
  0,25 – 0,35 – 0,5 – 0,7 – 1 – 1,4 – 2 (mm) theo khổ giấy và độ lớn hình vẽ.
- Hai nét D giao nhau bằng đoạn **gạch** (không giao ở chỗ chấm); nét D bắt đầu/kết thúc bằng gạch, vẽ
  vượt quá đường bao \~5mm.
- Nét C giao nhau phải **kín** (là đoạn gạch); chỗ nét C tiếp giáp nét A phải **để hở**.
- Khi nhiều loại nét trùng nhau, thứ tự ưu tiên vẽ: **A → C → E → D → B**.

### 1\.2 Quy ước riêng, bắt buộc cho bản vẽ bố trí cốt thép (TCVN 4612\-88)

Đây là điểm khác biệt quan trọng nhất so với quy ước nét chung ở mục 1.1 — áp dụng riêng cho loại bản vẽ
mà đồ án cần sinh ra:

![Quy ước nét trên mặt cắt bố trí thép](img/02_quyuoc_net_mat_cat_btct.png)

| Đối tượng | Loại nét | Bề rộng |
| --- | --- | --- |
| Đường bao cấu kiện (bê tông) — hình chiếu chính lẫn mặt cắt | Nét liền **mảnh** | s/3 |
| Cốt thép chịu lực (dọc chính) | Nét liền **đậm** | s (hoặc 2s) |
| Cốt đai, cốt phân bố, cốt cấu tạo | Nét liền **đậm** | s/2 (hoặc s) |

Nguyên tắc gốc: bê tông trên hình chiếu chính và trên mặt cắt được coi là **trong suốt**, để cốt thép bên
trong nổi bật lên — ngược lại với cảm giác thông thường (không vẽ đường bao bê tông đậm nhất). Trên mặt
cắt ngang: cốt thép dọc vẽ dạng **hình tròn đặc**; cốt đai vẽ dạng **đường bao khép kín** quanh các thanh
dọc, dùng nét đậm nhưng mảnh hơn cốt dọc.

> Phân biệt với quy ước mặt cắt kiến trúc/kết cấu thông thường: khi vẽ mặt bằng kết cấu/kiến trúc mà
> KHÔNG thể hiện chi tiết cốt thép (ví dụ mặt cắt tường/sàn/cột chỉ để định vị), đường bao mặt cắt của bộ
> phận chịu lực mới vẽ bằng nét liền đậm, còn phần thấy phía sau mặt phẳng cắt vẽ nét liền mảnh — quy tắc
> này KHÔNG áp dụng cho bản vẽ tách riêng chi tiết cốt thép.

## 2\. Ký hiệu

### 2\.1 Ký hiệu ghi kích thước (TCVN 5705\-1993)

![Ký hiệu ghi kích thước](img/06_ky_hieu_ghi_kich_thuoc.png)

| Ký hiệu | Ý nghĩa | Cách dùng |
| --- | --- | --- |
| R | Bán kính | Đặt trước con số, dùng cho cung tròn \< 180°; đường kích thước có 1 mũi tên hướng qua tâm |
| Ø | Đường kính | Đặt trước con số, dùng cho đường tròn hoặc cung ≥ 180° |
| □ | Cạnh hình vuông | Đặt trước con số chỉ kích thước cạnh |
| ∠ (hoặc i) | Độ dốc | Đầu nhọn ký hiệu hướng về phía chân dốc; độ dốc nhỏ dùng chữ i kèm % (VD i\=5%) |
| ▽ | Cao độ | Đỉnh tam giác chạm đường dóng; đơn vị mét, 2 số lẻ (VD ▽\+3,00) |
| ⌢ | Độ dài cung tròn | Đặt phía trên con số chỉ độ dài cung |

Ba thành phần bắt buộc của một kích thước: đường dóng (nét liền mảnh) → đường kích thước (nét liền mảnh,
2 mũi tên dài 4–6s, rộng 2s) → con số kích thước (đặt giữa, phía trên đường kích thước \~1,5mm). Mỗi kích
thước chỉ ghi một lần, ở hình biểu diễn dễ đọc nhất; đơn vị dài là milimét và không ghi đơn vị sau số.

### 2\.2 Ký hiệu số hiệu thanh thép (TCVN 4612\-88)

![Ký hiệu số hiệu thanh thép](img/03_ky_hieu_so_hieu_thanh_thep.png)

- Mỗi thanh/nhóm thanh được đánh **số hiệu trong một vòng tròn Ø7–10mm** (nét liền mảnh), đặt ở đầu mút
  đường dẫn trỏ tới thanh thép — dùng thống nhất trên hình chiếu chính, hình vẽ tách thanh, và mặt cắt.
- **Trên** phần nằm ngang của đường dẫn: ghi *số lượng \+ đường kính*, ví dụ `2Ø20`.
- **Dưới** phần nằm ngang của đường dẫn: ghi *chiều dài thanh kể cả móc* (`L=6830`) cho cốt dọc, hoặc
  *bước cốt đai* (`a=200`) cho cốt đai.
- Thông số đầy đủ của một loại thanh chỉ ghi **một lần duy nhất** trên cả bản vẽ (thường ở hình vẽ tách
  thanh); mọi chỗ khác chỉ cần ghi lại số hiệu trong vòng tròn.

### 2\.3 Ký hiệu vị trí và tên mặt cắt

![Ký hiệu mặt cắt](img/04_ky_hieu_mat_cat.png)

- Ký hiệu bằng nét cắt (loại E, mục 1.1) đặt tại vị trí cắt, kèm mũi tên chỉ hướng nhìn và tên bằng số La
  Mã cặp ở hai đầu: **I‑I, II‑II, III‑III...**
- Mặt cắt đặt tại các vị trí **dọc theo cấu kiện có thay đổi bố trí cốt thép** (nơi thép uốn xiên, cắt
  bớt, hoặc đổi số lượng) — chính là gối trái / giữa nhịp / gối phải đối với dầm thường.
- **Mặt cắt đầu tiên (I‑I)**\: ghi số hiệu **TẤT CẢ** các thanh có mặt tại vị trí đó.
- **Các mặt cắt sau (II‑II, III‑III...)**\: chỉ ghi số hiệu các thanh **có thay đổi** (mới xuất hiện hoặc
  biến mất) so với mặt cắt trước — không lặp lại toàn bộ.

### 2\.4 Ký hiệu trục lưới

![Ký hiệu trục lưới](img/05_ky_hieu_truc_luoi.png)

Vẽ bằng nét D (gạch chấm mảnh); số hiệu trục đặt trong vòng tròn Ø7–8mm ở đầu mút trục — chữ hoa (A, B,
C...) cho một phương, chữ số (1, 2, 3...) cho phương vuông góc còn lại.

### 2\.5 Ký hiệu vật liệu trên mặt cắt (TCVN7\-1993)

![Ký hiệu vật liệu mặt cắt](img/09_ky_hieu_vat_lieu_mo_rong.png)

| Vật liệu | Ký hiệu |
| --- | --- |
| Bê tông cốt thép | Gạch chéo **dày, đậm** |
| Bê tông (không cốt thép) | Gạch chéo **thưa** hơn |
| Kim loại | Gạch chéo hai chiều (ca\-rô chéo) |
| Gạch xây | Ô vuông nhỏ đều |
| Đá | Ký hiệu vân đá (không gạch đều) |
| Đất tự nhiên | Ký hiệu chấm |
| Kính, vật liệu trong suốt | Gạch ngang song song đều |
| Gỗ | Ký hiệu vân gỗ (gạch dọc) |
| Chất dẻo / cách điện–cách nhiệt–cách âm | Ký hiệu chấm tròn đều |

Hai ký hiệu bê tông cốt thép và bê tông thường **khác nhau, không dùng lẫn**. Mặt cắt hẹp (bề rộng ≤2mm
theo tỷ lệ vẽ) cho phép tô đen thay vì gạch ký hiệu; vật liệu ngoài bảng TCVN7\-1993 (ví dụ đất đắp, đất
sét, bê tông gạch vỡ) dùng ký hiệu phụ tự quy định kèm chú thích chữ ngay trên mặt cắt.

### 2\.6 Ký hiệu kiến trúc (dự phòng, nếu đồ án mở rộng sang vẽ mặt bằng)

Cửa đi 1/2/4 cánh: **Đ1 / Đ2 / Đ4** (vẽ bằng nét liền mảnh, cung 1/4 vòng tròn thể hiện quỹ đạo mở cánh;
cửa 4 cánh thể hiện dạng zíc\-zắc cho cánh gấp). Cửa sổ: **S** (hai đoạn nét song song ngắn cắt ngang mảng
tường; cửa sổ trên tường bao ngoài thường là cửa kép, trên vách ngăn trong nhà thường là cửa đơn). Cầu
thang: **TH** (mặt phẳng cắt tưởng tượng luôn cắt qua cánh thang thứ nhất; hướng đi lên là một nét liền
mảnh giữa cánh thang, bắt đầu bằng chấm tròn ở bậc đầu, kết thúc bằng mũi tên ở bậc cuối).

Ký hiệu thiết bị nội thất/vệ sinh (nếu vẽ mặt bằng đầy đủ): mỗi loại có ký hiệu hình học đơn giản riêng —
bàn ghế làm việc, giường đôi/đơn, bàn bếp, bộ bàn ghế ăn, tủ, bộ bàn ghế tiếp khách, chậu rửa, bệ xí, bồn
tắm — vẽ bằng nét liền mảnh, đặt đúng vị trí bố trí trong phòng.

Quy tắc ghi kích thước trên mặt bằng — 3 dãy kích thước phía ngoài nhà (từ trong ra ngoài): (1) chiều
rộng từng mảng tường/lỗ cửa kề nhau; (2) khoảng cách giữa các trục cột/tường kề nhau; (3) khoảng cách
giữa trục các tường bao ngoài (\= kích thước tổng thể ngôi nhà). Kích thước phía trong: chiều dài/rộng
thông thủy phòng, vị trí/chiều rộng lỗ cửa trên tường trong, chiều rộng cánh thang, chiều dày tường,
kích thước mặt cắt cột. Diện tích phòng ghi bằng m² nhưng **không ghi đơn vị** sau số (VD `24,00`). Cao
độ sàn (cốt sàn) so với cốt ±0,00 của tầng 1: đơn vị mét, ký hiệu ▽, ví dụ `▽+3,00`.

Mặt đứng: vẽ bằng nét liền mảnh, chỉ thể hiện bộ phận trông thấy (bậc thềm, cửa, cửa sổ, ban công, mái);
riêng **đường mặt đất luôn vẽ bằng nét liền đậm**, tách biệt hẳn so với các nét khác trên mặt đứng.

## 3\. Quy tắc bố trí cốt thép (không kèm công thức tính toán)

### 3\.1 Lớp bê tông bảo vệ

Tra theo Bảng 19 TCVN 5574:2018 theo điều kiện môi trường (trong nhà độ ẩm ≤75%, \>75%, ngoài trời...) —
giá trị tối thiểu tăng dần theo mức độ tiếp xúc ẩm/xâm thực; xem bảng đầy đủ ở mục 4.3 `RULES_TCVN5574.md`.

### 3\.2 Khoảng cách giữa các thanh thép dọc

Tối thiểu 25mm (lớp dưới, 1–2 lớp) và không nhỏ hơn đường kính lớn nhất của thanh thép tại vị trí đó.

### 3\.3 Số lượng & vị trí bố trí thanh

Dầm bề rộng b\>150mm: cần ≥2 thanh chịu kéo; b≤150mm: 1 thanh là đủ. Lượng thép kéo vào gối: ≥1/2 lượng
thép tại nhịp.

### 3\.4 Hàm lượng thép — chỉ nêu ngưỡng, không nêu cách tính As

Mỗi loại cấu kiện (dầm/cột) và mỗi độ mảnh có một cặp ngưỡng μ\_min/μ\_max riêng — tra bảng theo mục 4.1
`RULES_TCVN5574.md`, không tính bằng công thức khi kiểm tra bố trí.

### 3\.5 Cốt đai — đường kính & bước đai

Đường kính tối thiểu: ≥ max(0,25×đường kính cốt dọc lớn nhất; 6mm). Bước đai tra theo bảng riêng cho dầm
(đoạn đầu dầm/giữa dầm) và cho cột (bình thường/khi hàm lượng dọc \>1,5%) — giá trị max cho từng trường
hợp, không kèm công thức tính lực cắt Q.

### 3\.6 Đường kính uốn tối thiểu (bán kính móc/uốn thanh thép)

| Loại thép | d \< 20mm | d ≥ 20mm |
| --- | --- | --- |
| Trơn | 2,5d | 4d |
| Có gờ | 5d | 8d |

### 3\.7 Cấu tạo tại nút khung

Mỗi loại nút khung (góc mái, nút giữa, nút biên...) có yêu cầu cấu tạo riêng — tra bảng đầy đủ ở mục 7
`RULES_TCVN5574.md` (ví dụ: góc mái phải "đóng" khi e₀/h≤0,25; thép kéo của dầm phải uốn xuống mép ngoài
nút).

### 3\.8 Vị trí & số lượng mặt cắt khi vẽ (theo loại cấu kiện)

| Loại cấu kiện | Số mặt cắt ngang | Vị trí |
| --- | --- | --- |
| Cột | 1 | Giữa đoạn cột |
| Dầm thường (2 gối) | 3 | Gối trái, giữa nhịp, gối phải |
| Dầm công‑xôn (conson) | 1 | Tại gối/ngàm |

### 3\.9 Bảng thống kê cốt thép — 8 cột bắt buộc

Đặt phía trên khung tên, theo đúng thứ tự: (1) Tên cấu kiện — (2) Số hiệu thanh — (3) Hình dáng thanh
(phác thảo: thẳng / có móc / khung đai) — (4) Đường kính Ø (mm) — (5) Chiều dài 1 thanh (mm) — (6) Số
lượng thanh — (7) Tổng chiều dài (m) — (8) Tổng trọng lượng (kg).

### 3\.10 Quy tắc riêng cho thép sàn (dự phòng, nếu mở rộng sang vẽ sàn)

Thép sàn nằm ngang khi làm việc nên hình chiếu bằng chỉ là đoạn thẳng; quy ước coi như đã **quay 90°**
(sang trái hoặc lên trên) trước khi chiếu, để thấy hình dạng thật trên mặt bằng. Nếu các thanh cùng loại
và cách đều nhau, cho phép chỉ vẽ tượng trưng một vài thanh thay vì vẽ hết.

### 3\.11 Nguyên tắc nguồn dữ liệu (bắt buộc cho AI Agent khi sinh bản vẽ)

Mọi kích thước hình học trên bản vẽ (trục lưới, cao độ, tiết diện b×h, chiều dài dầm/cao cột, số
thanh/đường kính/lớp thép, bước cốt đai, chiều dài neo/nối/cắt, lớp bê tông bảo vệ...) phải **trace được
về một trường dữ liệu cụ thể** từ Input Adapter hoặc Rule Engine — không hard\-code theo bản vẽ mẫu
`BoTriThep_KhungTruc5_mau.pdf`. Xem bảng đối chiếu đầy đủ ở mục 10.7.1 `RULES_TCVN5574.md`.
