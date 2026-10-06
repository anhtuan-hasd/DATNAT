# Quy Tắc & Công Thức Thiết Kế Cốt Thép Khung BTCT

Thống kê đầy đủ, đối chiếu toàn bộ TCVN 5574:2018 (193 trang) và tài liệu "Hướng dẫn thiết kế khung phẳng BTCT toàn khối" ĐH Kiến Trúc Hà Nội (198 trang) — bản mở rộng, dùng làm cơ sở lập trình Rule Engine

Phạm vi hệ thống: **khung phẳng BTCT toàn khối** (chỉ dầm \+ cột, không sàn/bản/tường/móng), **không** dùng cốt thép ứng suất trước, **không** phải kết cấu lắp ghép, **không** có cần trục. Agent nhận As đã tính sẵn từ ETABS, không tự phân tích kết cấu. Tài liệu này thống kê **toàn bộ** nội dung liên quan trong hai nguồn — kể cả các công thức tính As (dùng để tự kiểm tra chéo/verify, không phải để thay ETABS tính lại).

## 0\. Bảng đối chiếu phạm vi — toàn bộ mục lục hai tài liệu

| Mục / Chương | Nội dung | Phạm vi | Lý do |
| --- | --- | --- | --- |
| Chương 7 TCVN | Kết cấu bê tông không cốt thép | Ngoài | Khung luôn có cốt thép chịu lực |
| 8\.1.1 | Yêu cầu chung tính độ bền TTGH1 | Trong | Nền tảng các mục sau |
| 8\.1.2 | Uốn \+ nén/kéo lệch tâm (tiết diện thẳng góc) | **Trong (đầy đủ)** | Dùng để tự kiểm tra chéo As từ ETABS |
| 8\.1.3 | Chịu cắt (tiết diện nghiêng) | **Trong (đầy đủ)** | Dùng để tính/kiểm tra cốt đai |
| 8\.1.4 | Xoắn | Ngoài (có điều kiện bỏ qua an toàn) | Khung phẳng chịu tải trong mặt phẳng, xoắn ≈ 0 |
| 8\.1.5 | Nén cục bộ | Ngoài phần lớn | Chỉ cần khi có gối tựa/console đặc biệt |
| 8\.1.6 | Chọc thủng | Ngoài | Chỉ áp dụng bản/móng |
| 8\.1.7 | Bản và tường phẳng | Ngoài | Không có bản/tường trong phạm vi |
| 8\.2 | TTGH2 — nứt, biến dạng/võng | Ngoài | ETABS/kỹ sư đã kiểm tra trước khi xuất As |
| Chương 9 | Kết cấu ứng suất trước | Ngoài | Không dùng ứng suất trước |
| Chương 10 | Yêu cầu cấu tạo | **Trong (đầy đủ)** | Cốt lõi của Rule Engine |
| Chương 11 | Khôi phục/gia cường kết cấu cũ | Ngoài | Thiết kế mới |
| Chương 12 | Tính toán chịu mỏi | Ngoài | Không có tải trọng lặp (cần trục) |
| Phụ lục A, B | Quan hệ cường độ, biểu đồ biến dạng phi tuyến | Tham khảo | Dùng cho phân tích phi tuyến, không bắt buộc |
| Phụ lục C | Hướng dẫn áp dụng loại cốt thép | **Trong** | Bảng quy đổi thép nước ngoài ↔ TCVN |
| Phụ lục D | Chi tiết đặt sẵn (bản mã, bulong) | Ngoài | Khung toàn khối không dùng bản mã liên kết |
| Phụ lục E | Tính toán hệ kết cấu | Ngoài | Đã có ETABS làm trước |
| Phụ lục F | Cột tiết diện vành khuyên/tròn | Ngoài | Chỉ có cột chữ nhật |
| Phụ lục G | Chốt bê tông | Ngoài | Không phải kết cấu lắp ghép |
| Phụ lục H | Công xôn ngắn (vai cột đỡ dầm cầu trục) | Ngoài | Không có cần trục |
| Phụ lục I | Kết cấu bán lắp ghép | Ngoài | Kết cấu toàn khối |
| Phụ lục K | Cốt thép hạn chế biến dạng ngang (cột nén lớn) | Tham khảo | Cơ sở lý thuyết cho cấu tạo đai dày cột nén lớn |
| Phụ lục L | Hệ số mô men kháng uốn đàn dẻo | Ngoài | Dùng cho kiểm tra nứt (TTGH2), không tính As |
| Phụ lục M | Độ võng và chuyển vị | Tham khảo | Có thể dùng verify độ võng sau này nếu mở rộng |
| Phụ lục N | Nhóm chế độ làm việc cần trục | Ngoài | Không có cần trục |
| Chương 1–4 (sách HD) | Hệ khung, sơ đồ tính, tải trọng, tổ hợp | Ngoài | Thuộc phân tích kết cấu (ETABS làm) |
| Chương 5 (sách HD) | Tính toán & cấu tạo cốt thép | **Trong (đầy đủ)** | Cốt lõi — đã có ở các mục 4–7 bên dưới |
| Chương 6 (sách HD) | Ví dụ thực hành trường học | **Trong (đầy đủ)** | Bộ dữ liệu kiểm chứng thứ hai — mục 10 |

## 1\. Bảng tra vật liệu

### 1\.1 Bê tông — cường độ tính toán (TTGH1, Bảng 7 TCVN 5574:2018)

| Cấp độ bền B | Rb (MPa) | Rbt (MPa) | Eb ×10³ (MPa, Bảng 10) |
| --- | --- | --- | --- |
| B15 | 8,5 | 0,75 | 24,0 |
| B20 | 11,5 | 0,90 | 27,5 |
| B25 | 14,5 | 1,05 | 30,0 |
| B30 | 17,0 | 1,15 | 32,5 |
| B35 | 19,5 | 1,30 | 34,5 |
| B40 | 22,0 | 1,40 | 36,0 |
| B45 | 25,0 | 1,50 | 37,0 |
| B50 | 27,5 | 1,60 | 38,0 |

### 1\.2 Cốt thép — cường độ tính toán (Bảng 13, 14 TCVN 5574:2018)

| Nhóm thép | Rs \= kéo (MPa) | Rsc \= nén (MPa) | Rsw \= đai (MPa) | Es (MPa) |
| --- | --- | --- | --- | --- |
| CB240\-T | 210 | 210 | 170 | 2,0×10⁵ |
| CB300\-T | 260 | 260 | 210 | 2,0×10⁵ |
| CB300\-V | 260 | 260 | 210 | 2,0×10⁵ |
| CB400\-V | 350 | 350 | 280 | 2,0×10⁵ |
| CB500\-V | 435 | 435 (400 dài hạn) | 300 | 2,0×10⁵ |

Rsw mọi nhóm ≤ 300 MPa (6.2.2.3). Es dây kéo nguội \= 2,05×10⁵ MPa; cáp \= 1,95×10⁵ MPa.

### 1\.3 Bảng đường kính – diện tích tiết diện thanh thép (As \= πd²/4)

| d (mm) | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 25 | 28 | 32 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| As 1 thanh (mm²) | 28,3 | 50,3 | 78,5 | 113,1 | 153,9 | 201,1 | 254,5 | 314,2 | 380,1 | 490,9 | 615,8 | 804,2 |

Diện tích n thanh \= n × As(1 thanh) — bảng tra chuẩn theo Phụ lục 1 (trích TCVN 1651\-1:2008) trong tài liệu hướng dẫn, cho n \= 1–9 thanh; công thức nhân trực tiếp là đủ, không cần bảng tra rời.

## 2\. Công thức tính duyệt/tính As theo mô men uốn và lực dọc (mục 8.1.2 TCVN 5574:2018)

Mục này KHÔNG dùng để agent tự tính As thay ETABS — mà dùng làm cơ sở **tự kiểm tra chéo** (verify) giá trị As nhận được có hợp lý so với M, N của phần tử hay không, và dùng để tính lại Mu/Nu khi As thực tế bố trí khác As lý thuyết (ví dụ khi làm tròn lên theo bảng đường kính).

### 2\.1 Hệ số ξR — chiều cao tương đối giới hạn vùng nén

```math
\xi_R = \frac{0{,}8}{1+\varepsilon_{s,el}/\varepsilon_{b2}}, \qquad \varepsilon_{s,el}=\frac{R_s}{E_s}
```

εb2 \= 0,0035 (bê tông thường, tải ngắn hạn). Với bê tông B70–B100 hoặc bê tông hạt nhỏ: thay hệ số 0,8 bằng **0,7**.

### 2\.2 Độ lệch tâm ngẫu nhiên ea (dùng cho cột)

ea ≥ max(L/600 ; h/30 ; 10 mm). Kết cấu siêu tĩnh: e₀ \= max(e₁ ; ea). Kết cấu tĩnh định: e₀ \= e₁ \+ ea (e₁ \= M/N).

### 2\.3 Dầm — tiết diện chữ nhật (đặt cốt đơn/kép)

```math
M_u = R_b bx(h_0-0{,}5x) + R_{sc}A_s'(h_0-a'), \qquad x=\frac{R_sA_s-R_{sc}A_s'}{R_b b}
```

Điều kiện dẻo bắt buộc: **x ≤ ξR·h₀**. Khi As thực tế bố trí lớn hơn As lý thuyết (vượt điều kiện dẻo), lấy thẳng **x \= ξR·h₀** thay vào Mu để tính lại khả năng chịu lực thực tế.

Đặt cốt đối xứng (RsAs \= RscA's): Mu \= RsAs(h₀−a′); nếu x (tính không kể A's) \< 2a′ thì thay a′ bằng x/2.

### 2\.4 Dầm — tiết diện chữ T/chữ I (cánh nằm vùng nén)

Kiểm tra trục trung hòa qua cánh: nếu RsAs ≤ Rb·b'f·h'f \+ RscA's → tính như tiết diện chữ nhật rộng b'f. Ngược lại (trục qua sườn):

```math
M_u = R_b bx(h_0-0{,}5x) + R_b(b_f'-b)h_f'(h_0-0{,}5h_f') + R_{sc}A_s'(h_0-a')
```

**Bề rộng cánh b'f đưa vào tính toán** — mỗi bên không vượt 1/6 nhịp cấu kiện, và không vượt: 1/2 khoảng cách thông thủy giữa sườn dọc (có sườn ngang, h'f≥0,1h); 6h'f (không sườn ngang, h'f\<0,1h); với cánh công\-xôn: 6h'f (h'f≥0,1h), 3h'f (0,05h≤h'f\<0,1h), bỏ qua nếu h'f\<0,05h.

### 2\.5 Cột — nén lệch tâm, tiết diện chữ nhật

```math
Ne \leq R_b bx(h_0-0{,}5x) + R_{sc}A_s'(h_0-a'), \qquad e=e_0\eta+\frac{h_0-a'}{2}
```

**Lệch tâm lớn** (ξ\=x/h₀ ≤ ξR — thử trước):

```math
x=\frac{N+R_sA_s-R_{sc}A_s'}{R_b b}
```

**Lệch tâm bé** (nếu x tính ở trên \> ξR·h₀ → chuyển sang nhánh này):

```math
x=\frac{N+R_sA_s\frac{1+\xi_R}{1-\xi_R}-R_{sc}A_s'}{R_b b+\frac{2R_sA_s}{h_0(1-\xi_R)}}
```

Quy trình chuẩn (đã xác nhận qua ví dụ thực hành chương 6): **luôn thử lệch tâm lớn trước**; nếu x \> ξR·h₀ thì tính lại theo công thức lệch tâm bé (hoặc công thức thực nghiệm bậc 2 dùng n\=N/(Rb·b·h₀), ε\=e/h₀, γa\=(h₀−a′)/h₀).

### 2\.6 Hệ số uốn dọc η (kể P\-Δ, khi L₀/i \> 14)

```math
\eta=\frac{1}{1-N/N_{cr}}, \qquad N_{cr}=\frac{\pi^2 D}{L_0^2}, \qquad D=k_bE_bI+0{,}7E_sI_s
```

```math
k_b=\frac{0{,}15}{\varphi_l(0{,}3+\delta_e)}, \qquad \varphi_l=1+\frac{M_{L1}}{M_L}\ (\leq 2), \qquad \delta_e=\frac{e_0}{h}\ (0{,}15\leq\delta_e\leq1{,}5)
```

ML: mô men do toàn bộ tải trọng; ML1: mô men do tải thường xuyên \+ tạm thời dài hạn.

### 2\.7 Công thức đơn giản hóa (cột đối xứng, e₀≤h/30, L₀/h≤20)

```math
N \leq \varphi(R_bA+R_{sc}A_{s,tot})
```

φ tra theo Bảng 16 (độ mảnh L₀/h, cấp bê tông, tải dài hạn): ví dụ B20–B55, L₀/h\=10 → φ\=0,90; L₀/h\=20 → φ\=0,70. Tải ngắn hạn: nội suy φ\=0,9 (L₀/h\=10) đến 0,85 (L₀/h\=20).

**Chiều dài tính toán L₀** theo liên kết 2 đầu: 2 khớp → 1,0L; ngàm\-tự do (công\-xôn) → 2,0L; khớp cố định\-ngàm cứng → 0,7L; 2 ngàm cứng → 0,5L (bảng đầy đủ hơn có 10 trường hợp liên kết trong TCVN, dao động 0,5L–2,0L).

### 2\.8 Kéo đúng tâm / kéo lệch tâm (ít gặp trong dầm/cột khung, nêu đủ)

Kéo đúng tâm: N ≤ Rs·As,tot. Kéo lệch tâm (N nằm giữa As, A's): Ne ≤ Rs·A's(h₀−a′); Ne′ ≤ Rs·As(h₀−a′). N nằm ngoài khoảng As, A's: dùng công thức tương tự dầm chữ nhật nhưng trừ N ở tử số tính x.

## 3\. Công thức tính/kiểm tra cốt đai theo lực cắt (mục 8.1.3 TCVN 5574:2018)

### 3\.1 Điều kiện chống ép vỡ bụng (khống chế kích thước tiết diện)

```math
Q \leq \varphi_{b1}R_bbh_0, \qquad \varphi_{b1}=0{,}3
```

Nếu không thỏa: phải tăng b, h hoặc cấp bê tông — **không thể chỉ tăng cốt đai**.

### 3\.2 Điều kiện cơ bản chịu cắt

```math
Q \leq Q_b+Q_{sw}, \qquad Q_b=\frac{\varphi_{b2}R_{bt}bh_0^2}{C}\ (0{,}5R_{bt}bh_0 \leq Q_b \leq 2{,}5R_{bt}bh_0), \qquad \varphi_{b2}=1{,}5
```

```math
Q_{sw}=\varphi_{sw}q_{sw}C, \qquad \varphi_{sw}=0{,}75, \qquad q_{sw}=\frac{R_{sw}A_{sw}}{s_w}
```

**Công thức đơn giản hóa** (không cần dò C nguy hiểm nhất, C lấy h₀–2h₀):

```math
Q_1 \leq Q_{b,1}+Q_{sw,1}, \qquad Q_{b,1}=0{,}5R_{bt}bh_0, \qquad Q_{sw,1}=q_{sw}h_0
```

Gần gối tựa (a\<2,5h₀): nhân Qb,1 với 2,5/(a/h₀) (≤2,5Rbtbh₀); nếu a\<h₀: nhân Qsw,1 với a/h₀.

**Điều kiện đặt cốt đai:** qsw ≥ 0,25·Rbt·b — nếu không thỏa nhưng vẫn muốn kể cốt đai, dùng Qb \= 4φb2h₀²qsw/C.

**Bước đai tối đa theo khả năng chịu cắt:** sw,max/h₀ \= Rbt·b·h₀/Q.

### 3\.3 Hệ số φn (khi cấu kiện chịu đồng thời N — quan trọng cho CỘT)

`\varphi_n=1+\frac{\sigma_m}{R_b}\ (0\le\sigma_m\le0{,}25R_b);\quad 1{,}25\ (0{,}25R_b\le\sigma_m\le0{,}75R_b);\quad 5(1-\sigma_m/R_b)\ (0{,}75R_b\le\sigma_m\le R_b)`
`\varphi_n=1-\frac{\sigma_t}{2R_{bt}}\ (\text{khi }\sigma_t\text{ là ứng suất kéo do }N)`

Nhân φn vào vế phải các điều kiện (3.1), (3.2) — cột chịu N nén được **tăng** khả năng chịu cắt (đến 1,25 lần), N kéo thì **giảm**. Cho phép bỏ qua ảnh hưởng cốt thép khi tính σm, σt nếu μ\_dọc ≤ 3%.

### 3\.4 Kiểm tra theo tiết diện nghiêng chịu mô men (xác định vị trí cắt/uốn cốt dọc)

```math
M \leq M_s+M_{sw}, \qquad M_s=R_sA_s\cdot z_s\ (z_s=0{,}9h_0), \qquad M_{sw}=0{,}5\,Q_{sw}\,C
```

Dùng để xác định vị trí hợp lý cắt bớt/uốn cốt thép dọc dọc theo chiều dài dầm mà vẫn đảm bảo đủ khả năng chịu mô men tại tiết diện nghiêng — cần thiết khi bản vẽ thể hiện cắt thép không đồng đều suốt nhịp.

### 3\.5 Xoắn — điều kiện được phép bỏ qua (mục 8.1.4)

```math
T \leq 0{,}1\,R_b\,b^2h
```

Với khung phẳng chịu tải trong mặt phẳng (không có bản/console lệch trục truyền xoắn), T ngoại lực ≈ 0 → điều kiện trên gần như luôn thỏa, **có thể bỏ qua kiểm tra xoắn** một cách an toàn.

## 4\. Điều kiện cốt thép dọc (mục 10.3.3, 5.4.1–5.4.2)

### 4\.1 Hàm lượng tối thiểu μ \= As/(b·h₀)·100%

| Trường hợp | μ\_min |
| --- | --- |
| Uốn/nén lệch tâm/kéo lệch tâm, độ mảnh L₀/h ≤ 17 (chữ nhật L₀/h ≤ 5) | 0,10% |
| Độ mảnh trung gian | Nội suy tuyến tính |
| Độ mảnh lớn L₀/i ≥ 87 (chữ nhật L₀/h ≥ 25) | 0,25% |
| Cốt bố trí đều chu vi, hoặc kéo đúng tâm | Gấp đôi (0,20% / 0,50%) |
| Cốt cấu tạo tại đổi tiết diện, mép lỗ mở, mép biên chịu kéo do lệch tâm | ≥ 0,025% |

**Hàm lượng tối đa μ\_max** (xác nhận qua ví dụ thực hành thực tế, mục 5.6 giáo trình): **3%** cho cấu kiện chịu uốn (dầm); cột đặt đối xứng thì mỗi phía ≤ 3% (tổng μt ≤ 6%). Đây là ngưỡng cảnh báo thực hành (kèm quy tắc mối nối 10.3.6.4 dùng chung ngưỡng 3%), không phải trị số tuyệt đối duy nhất trong TCVN nhưng là chuẩn áp dụng phổ biến.

Khuyến nghị kinh tế: μ dầm 0,6–1,2%; μ tổng cột 1–2%.

### 4\.2 Số lượng & bố trí thanh

- Dầm b\>150mm: ≥2 thanh chịu kéo; b≤150mm: 1 thanh đủ.
- Kéo vào gối: ≥1/2 As nhịp và ≥2 thanh (dầm); ≥1/3 As/m bề rộng (bản).
- Không quá 3 loại đường kính/dầm; không chênh lệch đúng 1mm; trong cùng miền chịu lực không chênh quá 6mm.
- Cột: bố trí đối xứng theo chu vi; đường kính φ12–φ40.
- Khi hai gối liền kề có |M| gần bằng nhau: **thiết kế chung theo giá trị lớn hơn**, không tính riêng (xác nhận qua ví dụ thực hành).
- Dầm console/nhịp phụ có M nhỏ hơn nhiều so với dầm chính liền kề: **không tính riêng**, dùng thép của dầm liền kề kéo dài qua để đảm bảo liên tục tại gối chung, chỉ kiểm tra lại h₀/khoảng hở.

### 4\.3 Lớp bê tông bảo vệ (Bảng 19)

| Điều kiện | Chiều dày tối thiểu |
| --- | --- |
| Trong nhà, độ ẩm ≤ 75% | 20 mm |
| Trong nhà, độ ẩm \> 75% | 25 mm |
| Ngoài trời | 30 mm |
| Trong đất/móng | 40 mm |

Cốt cấu tạo giảm 5mm so với cốt chịu lực; luôn ≥ đường kính thanh và ≥10mm.

### 4\.4 Khoảng cách giữa các thanh thép dọc

**Tối thiểu** (không nhỏ hơn đường kính lớn nhất, và không nhỏ hơn): 25mm (dưới, 1–2 lớp); 30mm (trên); 50mm (dưới từ lớp 3, hoặc đứng). Bó thanh: dùng đường kính quy đổi d\_red\=√(Σdᵢ²).

**Tối đa**\: dầm/bản h≤150mm → 200mm; h\>150mm → min(1,5h;400mm); cột → 400mm (vuông góc mặt uốn) / 500mm (mặt uốn).

## 5\. Điều kiện cốt thép ngang (đai) — mục 10.3.4, 5.4.2

### 5\.1 Đường kính tối thiểu

d\_đai ≥ max(0,25×d\_dọc,max ; 6mm).

### 5\.2 Bước đai — dầm

| Trường hợp | Bước tối đa |
| --- | --- |
| Cần đai theo tính toán (Q vượt khả năng bê tông) | min(0,5h₀ ; 300mm) |
| Đai theo cấu tạo (Q ≤ khả năng bê tông) | min(0,75h₀ ; 500mm) |
| h \< 150mm | Không bắt buộc |

s thiết kế \= min(s\_max ở trên ; s\_tt \= Rsw·Asw/qsw ; s\_ct cấu tạo theo đoạn đầu/giữa dầm).

### 5\.3 Bước đai — cột

| Trường hợp | Bước tối đa |
| --- | --- |
| Bình thường | min(15d\_dọc,min ; 500mm) |
| μ\_dọc \> 1,5% (một mặt), hoặc trong đoạn nối chồng | min(10d\_dọc,min ; 300mm) |

b\>400mm và \>4 thanh/cạnh: bắt buộc thêm đai phụ.

## 6\. Công thức neo & nối cốt thép — mục 10.3.5–10.3.7

### 6\.1 Chiều dài neo cơ sở

```math
L_{0,an}=\frac{R_sA_s}{R_{bond}u_s}, \qquad R_{bond}=\eta_1\eta_2R_{bt}
```

η₁ \= 2,5 (thép gờ, cán nóng); 1,5 (thép trơn). η₂ \= 1,0 (d≤32mm); 0,9 (d≥36mm).

### 6\.2 Chiều dài neo tính toán

```math
L_{an}=\alpha L_{0,an}\frac{A_{s,cal}}{A_{s,ef}}, \qquad \alpha=1{,}0\ (\text{kéo}),\ 0{,}75\ (\text{nén})
```

Ràng buộc: Lan ≥ max(15d ; 200mm).

### 6\.3 Chiều dài nối chồng

```math
L_{lap}=\alpha L_{0,an}\frac{A_{s,cal}}{A_{s,ef}}, \qquad \alpha=1{,}2\ (\text{kéo}),\ 0{,}9\ (\text{nén})
```

Ràng buộc: Llap ≥ max(0,4αL0,an ; 20d ; 250mm). Khoảng cách 2 mối nối cạnh nhau ≥ max(2d;30mm); số thanh nối trong 1 tiết diện ≤ 50% (thép trơn có móc ≤25%), có thể tăng đến 100% nếu có chi tiết neo bổ sung.

### 6\.4 Đường kính uốn tối thiểu

| Loại thép | d \< 20mm | d ≥ 20mm |
| --- | --- | --- |
| Trơn | 2,5d | 4d |
| Có gờ | 5d | 8d |

## 7\. Cấu tạo tại nút khung — mục 10.4.11, 5.4.3

| Loại nút | Yêu cầu chính |
| --- | --- |
| Góc mái "đóng", e₀/h ≤ 0,25 | Thép kéo dầm uốn xuống mép ngoài cột, đoạn Lan |
| Góc mái "đóng", 0,25\<e₀/h≤0,5 | Thêm ≥2 thanh kéo xuống đáy dầm đoạn Lan |
| Góc mái "đóng", e₀/h\>0,5 | Một số thanh cột kéo lên mép trên dầm; thép dầm neo sâu vào cột |
| Góc mái "mở" | Thép dọc uốn chữ U nối dầm–cột; μ≥2% thêm thép chéo gia cường ≈20% thép chịu lực đầu dầm |
| Giữa khung mái | Thép cột kéo lên mặt dầm/sàn đoạn Lan, bán kính uốn ≥50mm |
| Biên tầng trung gian, tiết diện cột không đổi | Đai ≤min(300;10d\_min) trong đoạn Lan tại nút |
| Biên, cột đổi tiết diện tgβ≤1/6 | Cốt dọc cột dưới vuốt liên tục lên chờ nối cột trên |
| Biên, cột đổi tiết diện tgβ\>1/6 | Cốt dọc cột dưới kéo lên mặt dầm, neo đoạn Lan riêng |
| Giữa tầng trung gian | Thép dầm liên tục qua nút; dầm 2 bên chênh cao thì neo sâu dầm thấp hơn |
| Cột – móng | Thép chờ chữ L từ móng tương đương thép cột nối lên |
| Gãy khúc, α≥160° | Thép dọc chịu kéo liên tục qua nút, có cốt ngang gia cường |
| Gãy khúc, α\<160° | Thép dọc chịu kéo tách rời, neo vào vùng nén đoạn Lan; ôm cốt ngang |
| Dầm phụ – dầm chính | Đai gia cường ôm cốt dọc, đoạn b\+2h (dầm chính)/h/3 (dầm phụ) |

Nguyên tắc chung: chiều dài neo mọi thanh quy tụ vào nút phải đủ Lan; tránh tập trung quá nhiều cốt thép; mạch ngừng thi công nên đặt tại mặt dưới dầm.

## 8\. Phụ lục C — Bảng tương đương cốt thép quốc tế (tham khảo khi input dùng ký hiệu nước ngoài)

| Giới hạn chảy (MPa) | Ký hiệu | Tiêu chuẩn | Loại |
| --- | --- | --- | --- |
| 240/300 | CB240\-T / CB300\-T | TCVN 1651\-1:2008 | Thanh trơn |
| 235 | A\-I (A240) | GOST 5781\-82\* | Thanh trơn |
| 300/400/500 | CB300\-V / CB400\-V / CB500\-V | TCVN 1651\-2:2008 | Thanh vằn |
| 295/390 | A\-II (A300) / A\-III (A400) | GOST 5781\-82\* | Thanh vằn |
| 295–500 | SD295/SD345/SD390/SD490 | JIS G 3112\-2010 | Thanh vằn |
| 500 | B500A/B/C | BS 4449:2005 / EN 10080:2005 | Thanh vằn |
| 280–520 | gr.280/420/520 | ASTM A615M | Thanh vằn |
| 335–500 | HRB335/400/500 | GB 1499\-2007 | Thanh vằn |

Rule Engine nên nhận diện các ký hiệu nước ngoài phổ biến (A\-II≈CB300\-V, A\-III≈CB400\-V, gr.420≈CB400\-V) khi input không theo chuẩn TCVN. Các bảng thép ứng suất trước cường độ cao (C4\-C7 phụ lục gốc) không thuộc phạm vi.

## 9\. Cốt thép hạn chế biến dạng ngang cho cột chịu nén lớn — Phụ lục K (tham khảo)

Khi cột chịu nén lệch tâm với lực nén lớn/độ mảnh lớn, việc bố trí **cốt đai dày (bó bê tông lõi)** làm tăng cường độ nén quy đổi của bê tông:

```math
R_{b,red}=R_b+\varphi\mu_{s,xy}R_{s,xy}, \qquad \varphi=\frac{1}{0{,}23+\alpha_{red}}, \qquad \alpha_{red}=\frac{\mu_{xy}R_{s,xy}}{R_b+10}
```

Đây là cơ sở lý thuyết cho yêu cầu thực hành "cốt đai dày tại đầu cột/vùng nối chồng/cột chịu nén lớn" đã nêu ở mục 5.3 — Rule Engine không cần tính Rb,red chi tiết nhưng nên áp bước đai giảm (mục 5.3) khi phát hiện cột chịu N lớn.

## 10\. Bộ dữ liệu kiểm chứng thứ hai — Ví dụ "Khung trục 3, trường học" (Chương 6 tài liệu hướng dẫn)

Đây là ví dụ thực hành đầy đủ thứ hai (ngoài khung trục 5 của chính đồ án), dùng làm test case bổ sung để kiểm chứng Rule Engine trên bộ vật liệu khác (B30/CB500\-V/CB240\-T thay vì B25/CB500\-V/CB240\-T).

### 10\.1 Vật liệu & hằng số dùng chung

Bê tông B30: Rb\=17MPa, Rbt\=1,15MPa, Eb\=32500MPa. Cốt dọc CB500\-V: Rs\=Rsc\=435MPa. Cốt đai CB240\-T: Rsw\=170MPa.

ξR \= 0,8/(1\+(435/200000)/0,0035) \= **0,493**; αR \= ξR(1−ξR/2) \= **0,371**.

### 10\.2 Bảng 6.24 — Thống kê thép dầm khung, tầng 3 và tầng 5

| Vị trí | Phần tử | Tiết diện | As tt (mm²) | μ% | As chọn | Asw chọn |
| --- | --- | --- | --- | --- | --- | --- |
| Tầng 3 | 44\-45 | Gối trái | 1212 | 0,73 | 5ϕ18 (1272) | ϕ6 s150 |
| Tầng 3 | 44\-45 | Gối phải | 1103 | 0,67 | 3ϕ18\+2ϕ16 (1166) | ϕ6 s150 |
| Tầng 3 | 44\-45 | Giữa nhịp | 569 | 0,34 | 3ϕ16 (603) | Cấu tạo s200 |
| Tầng 3 | 13 | Gối trái | 327 | 0,36 | 2ϕ18 (509) | Cấu tạo s200 |
| Tầng 3 | 13 | Gối phải | 341 | 0,38 | 2ϕ18 (509) | Cấu tạo s200 |
| Tầng 3 | 13 | Giữa nhịp | 390 | 0,43 | 2ϕ16 (402) | Cấu tạo s200 |
| Tầng 5 | 48\-49 | Gối trái | 690 | 0,42 | 2ϕ18\+1ϕ16 (710) | ϕ6 s150 |
| Tầng 5 | 48\-49 | Gối phải | 593 | 0,36 | 2ϕ18\+1ϕ16 (710) | ϕ6 s150 |
| Tầng 5 | 48\-49 | Giữa nhịp | 379 | 0,23 | 2ϕ16 (402) | Cấu tạo s200 |
| Tầng 5 | 11 | Gối trái | 28 | 0,03 | 2ϕ18 (509) | Cấu tạo s200 |
| Tầng 5 | 11 | Gối phải | 155 | 0,17 | 2ϕ18 (509) | Cấu tạo s200 |
| Tầng 5 | 11 | Giữa nhịp | 153 | 0,17 | 2ϕ16 (402) | Cấu tạo s200 |

### 10\.3 Bảng 6.25 — Thống kê thép cột khung, tầng 3 và tầng 5

| Vị trí | Phần tử | Tiết diện | As\=A's tt (mm²) | μ\=μ'% | As chọn |
| --- | --- | --- | --- | --- | --- |
| Tầng 3 | 20 | Chân | 710 | 0,51 | 2ϕ20\+1ϕ16 (829) |
| Tầng 3 | 26 | Chân | 780 | 0,56 | 2ϕ20\+1ϕ16 (829) |
| Tầng 3 | 32 | Chân | 300 | 0,21 | 2ϕ16 (402) |
| Tầng 5 | 18 | Chân | 360 | 0,26 | 2ϕ16 (402) |
| Tầng 5 | 24 | Chân | 360 | 0,26 | 2ϕ16 (402) |
| Tầng 5 | 30 | Chân | 140 | 0,10 | 2ϕ16 (402) |

### 10\.4 Ví dụ chi tiết cột 22 tầng 1 (250×600mm, TH12: M\=417,74kNm, N\=1514,38kN)

ea\=max(h/600;hc/30;10)\=20mm; e₀\=max(M/N;ea)\=275,85mm; λh\=l₀/h\=6,07\>4 → cần η. φL\=1\+ML1/ML\=1,42; δe\=e₀/h\=0,46; kb\=0,15/\[φL(0,3\+δe)\]\=0,139; D\=kbEbI\+0,7EsIs\=46828 kNm²; η\=1/(1−N/Ncr)\=1,05; e\=ηe₀\+h/2−a\=550mm.

Thử lệch tâm lớn: x\=N/(Rb·b)\=356mm \> ξRh₀\=276mm → **sai, chuyển lệch tâm bé** → công thức thực nghiệm bậc 2 → x\=326mm (thỏa h₀≥x\>ξRh₀) → As\=A's\=\[Ne−Rbbx(h₀−0,5x)\]/\[Rsc(h₀−a′)\]≈1250mm² → μ\=0,89% → **chọn 2ϕ25\+1ϕ22 (1362mm²) mỗi phía**.

Kiểm chứng bằng biểu đồ tương tác (5 điểm A,B,C,D,E) với toàn bộ 17 tổ hợp tải trọng ở cả 2 đầu phần tử — mọi điểm nằm trong biểu đồ → đạt.

Cốt đai cột: ϕ ≥ max(ϕmax/4;5mm) → chọn ϕ8; bước ngoài đoạn nối \= min(15dmin;500)\=375→chọn 350mm; bước trong đoạn nối \= min(10dmin;300)\=250→chọn 200mm.

### 10\.5 Ví dụ dầm 40\-41 tầng 1 (nhịp CB, 250×700mm)

Gối C/B: |M|≈462/435kNm → thiết kế chung theo giá trị lớn hơn (gối C) → αm\=0,262\<αR → ξ\=0,31 → As\=1954mm² (μ\=1,21%) → **chọn 2ϕ25\+3ϕ22 (2122mm²), 2 hàng**.

Nhịp (chữ T, hf'\=100mm): Mf\=2540,7kNm \> Mmax\=315,47kNm → trục qua cánh, tính như chữ nhật bf'\=2450mm → As\=1074mm² (μ\=0,65%) → **chọn 3ϕ22 (1140mm²)**.

Cốt đai: Qmax\=240,3kN → kiểm tra ép vỡ bụng (thỏa) → Qb,min\=92,7kN\<Q → cần tính đai → qsw\=107,3N/mm → stt\=159,4mm → s thiết kế\=150mm (đầu dầm), 250mm (giữa dầm) — kiểm tra không cần cốt xiên (Qu,min\=242,9kN\>Q).

**Cốt treo chống giật đứt** (dầm phụ gác vào dầm chính): F(1−hs/h₀)≤ΣRswAsw → F\=28,035kN, hs\=375mm → ΣAsw≥69,03mm² → chọn đai ϕ8 2 nhánh, **5 cái mỗi bên** (làm tròn lên từ 0,69).

### 10\.6 Bảy nguyên tắc xử lý trường hợp biên (rút ra từ ví dụ, đưa thẳng vào logic Rule Engine)

1. Hai gối liền kề có |M| gần bằng nhau → thiết kế chung theo giá trị lớn hơn.
2. Cấu kiện phụ/console có M nhỏ hơn nhiều so với cấu kiện chính liền kề → dùng thép cấu kiện chính kéo dài qua, chỉ kiểm tra lại h₀/khoảng hở.
3. Cột lệch tâm: luôn thử "lệch tâm lớn" trước; nếu x\>ξRh₀ thì chuyển "lệch tâm bé".
4. Sau khi chọn thép cột, bắt buộc dựng biểu đồ tương tác và kiểm tra toàn bộ tổ hợp tải trọng (không chỉ 1 cặp nội lực nguy hiểm nhất) nằm trong biểu đồ.
5. μmin \< μ \< μmax\=3% (uốn) hoặc 2μmin\<μt\<6% (cột đối xứng).
6. Cốt treo (giật đứt) tính khi có dầm phụ gác vào dầm chính; số lượng luôn làm tròn lên, bố trí đều 2 bên vị trí lực tập trung.
7. Bước đai thiết kế \= min(s\_max chống ép vỡ bụng, s\_tt theo tính toán, s\_ct cấu tạo theo vị trí đầu/giữa dầm).

### 10\.7 Quy ước trình bày bản vẽ (mục "Thể hiện bản vẽ", nguyên văn \+ suy ra từ hình vẽ thực tế)

Checklist nội dung bản vẽ theo giáo trình: mặt bằng kết cấu công trình; mặt cắt dọc khung; mặt cắt ngang từng cấu kiện; cấu tạo nút khung; bảng thống kê thép; ghi chú vật liệu (cấp bền bê tông, mác thép, cường độ tính toán, quy định nối/hàn thép và chiều dài nối); đầy đủ kích thước, cao trình, trục định vị.

Quy ước ký hiệu suy ra từ các bản vẽ mẫu trong tài liệu (không có mẫu khung tên/tỷ lệ chính thức, nhưng thực tế áp dụng):

- Trục định vị: số (1,2,3…) một phương, chữ cái (A,B,C…) phương kia, đặt trong vòng tròn ở đầu trục.
- Tên cấu kiện ghi trực tiếp trên mặt bằng: cột "C\-bxh" (vd C\-25x60), dầm "D\-bxh" (vd D\-25x70).
- Mặt bằng kiến trúc/kết cấu: tỷ lệ phổ biến 1/100; mặt cắt: 1/75.
- Cao độ ghi bằng ký hiệu mức (±0.000, \+3.900…) kèm mũi tên tam giác.
- Kích thước ghi theo 2–3 cấp chồng nhau (chi tiết → nhịp → tổng thể).
- Thép trên mặt cắt/khai triển: đường trục thép là nét liền đậm, ký hiệu số lượng\+đường kính (2ϕ16), kích thước đoạn neo/uốn ghi bằng số (mm).

#### 10\.7.1 Nguồn dữ liệu quyết định kích thước hình học khi vẽ

Khi vẽ cho MỘT bộ input bất kỳ (không phải riêng khung trục 5), toàn bộ kích thước hình học phải suy ra
từ dữ liệu đã chuẩn hoá qua Input Adapter và kết quả Rule Engine — **không được hard\-code** theo ví dụ
mẫu. Cụ thể:

| Đại lượng hình học cần vẽ | Lấy từ đâu |
| --- | --- |
| Vị trí & tên trục lưới (số/chữ), khoảng cách giữa các trục | Danh sách trục \+ khoảng cách nhịp/bước cột do Input Adapter chuẩn hoá (tương ứng `spans`/`span_names` kiểu dữ liệu đã có) |
| Cao độ các mốc (đáy móng, tự nhiên, ±0.000, các tầng, mái) | Danh sách tên mốc \+ cao độ tuyệt đối do Input Adapter chuẩn hoá (`story_levels`/`level_names`) — cần quy đổi thống nhất về 1 đơn vị (mm) trước khi vẽ |
| Kích thước tiết diện b×h của từng loại cột/dầm (K1, K2, D1…) | Bảng gán tiết diện trong Excel/ETABS gốc (vd sheet "Frame Section Assignments"/"Frame Props") sau khi Input Adapter ánh xạ |
| Chiều dài mỗi đoạn dầm | \= khoảng cách giữa 2 trục mà dầm đó nối — suy ra từ lưới trục, không nhập riêng |
| Chiều cao mỗi đoạn cột | \= hiệu 2 cao độ liền kề mà cột đó nối — suy ra từ danh sách cao độ, không nhập riêng |
| Số thanh, đường kính, số lớp thép dọc tại mỗi mặt cắt (gối trái/giữa nhịp/gối phải với dầm; mặt cắt đại diện với cột) | Kết quả `rule_engine` (Phase 1) — không phải As lý thuyết, mà là cấu hình thép THẬT đã chọn |
| Đường kính & bước cốt đai theo từng đoạn (đầu dầm/giữa dầm — mục 5.2; theo cột — mục 5.3) | Kết quả `rule_engine` phần thiết kế cốt đai (mục 3 của tài liệu này) |
| Chiều dài đoạn neo/nối chồng/đoạn cắt lý thuyết | Kết quả `rule_engine` phần neo/nối/cắt thép (mục 6 và 3.4) |
| Khoảng lùi cốt thép vào từ mép tiết diện | Lớp bê tông bảo vệ `cover` theo mục 4.3 |
| Hệ số quy đổi mm thực → đơn vị vẽ | Tỷ lệ bản vẽ theo loại hình vẽ đang vẽ (mặt bằng/mặt đứng khung ≈1/100, mặt cắt chi tiết ≈1/20–1/25 — xem trên) |

Nguyên tắc chung: **mọi con số xuất hiện trên bản vẽ phải trace được về một trường dữ liệu cụ thể** (từ
Input Adapter hoặc từ Rule Engine) — nếu module vẽ cần một con số mà không trace được, đó là dấu hiệu
thiếu dữ liệu ở Input Adapter/Rule Engine, phải bổ sung ở đó, không tự đặt cứng trong code vẽ.

#### 10\.7.2 Bảng quy ước đường nét theo chức năng thể hiện

Mỗi loại nét trong bản vẽ kỹ thuật xây dựng có một nhiệm vụ thể hiện riêng — không dùng chung 1 kiểu nét
cho mọi đối tượng. Bảng dưới đây là quy ước cần áp dụng (đối chiếu thêm với
`data/samples/BoTriThep_KhungTruc5_mau.pdf` và các `.dwg` mẫu khác nếu có, vì mức độ đậm/nhạt cụ thể có
thể khác nhau đôi chút giữa các đồ án, nhưng PHÂN LOẠI chức năng theo bảng này là bắt buộc):

| Loại nét | Đặc điểm | Dùng để thể hiện | Layer gợi ý |
| --- | --- | --- | --- |
| Nét liền rất đậm (cutting line) | Liền, dày nhất | Đường bao mặt cắt bê tông tại đúng vị trí bị cắt qua (contour tiết diện dầm/cột trên mặt cắt ngang) | `OUTLINE_CUT` |
| Nét liền đậm | Liền, dày vừa | Đường bao cấu kiện nhìn thấy được (mép ngoài dầm/cột trên mặt đứng khung, mặt bằng); trục thép dọc/cốt đai (nổi bật hơn nét kích thước) | `OUTLINE`, `REBAR_MAIN`, `REBAR_STIRRUP` |
| Nét liền mảnh | Liền, mảnh | Đường kích thước (dimension), đường dẫn/ghi chú (leader), đường gạch mặt cắt bê tông (hatch), khung bảng thống kê | `DIM`, `HATCH`, `TEXT` |
| Nét đứt | Đứt quãng đều | Cấu kiện/chi tiết bị khuất — nằm phía sau hoặc ẩn trong cấu kiện khác, không nhìn thấy trực tiếp từ hướng nhìn đó | `HIDDEN` |
| Nét chấm gạch (trục/tâm) | Gạch dài – chấm – gạch dài, mảnh | Đường tim trục lưới (cột, dầm), đường tâm đối xứng của tiết diện | `AXIS` |
| Nét lượn sóng / zíc\-zắc (break line) | Lượn sóng hoặc zíc\-zắc, mảnh | Giới hạn chỗ cắt rời một cấu kiện dài (dầm/cột) khi vẽ rút ngắn, không thể hiện hết chiều dài thật | `BREAK` |

Ghi chú thêm:

- Cốt thép (dọc và đai) LUÔN vẽ đậm hơn đường kích thước/hatch để nổi bật, kể cả khi cùng là "nét liền" —
  phân biệt bằng bề dày nét (lineweight) hoặc layer riêng, không chỉ dựa vào màu.
- Trên mặt cắt ngang, cốt thép dọc vẽ dạng hình tròn đặc (tiết diện thanh thép nhìn dọc trục); cốt đai
  vẽ dạng đường bao khép kín quanh các thanh dọc.
- Ký hiệu số hiệu mặt cắt: số có gạch chân dưới cho mặt cắt ngang qua CỘT (mặt phẳng cắt nằm ngang); số
  kèm 1 vạch đứng ngắn ngay sau cho mặt cắt ngang qua DẦM (mặt phẳng cắt thẳng đứng) — đúng quy ước đã
  quan sát được từ bản vẽ mẫu.

## 11\. Quy ước đặt tên phần tử & bảng tra hỗ trợ Input Adapter

- Cấu kiện được gọi tên theo giao điểm trục lưới (vd "cột B\-2"); ký hiệu tiết diện gắn kèm tên (C\-bxh, D\-bxh).
- Nút/đầu cấu kiện khi trình bày nội lực đôi khi dùng chữ cái \+ dấu phẩy phân biệt tầng (A, A′, A″) hoặc số La Mã (I, II, IV, V) cho đầu cột — Input Adapter cần nhận diện linh hoạt các quy ước đánh số này.
- Quy tắc làm tròn tiết diện sơ bộ (để validate input hình học có hợp lý không): ≤600mm → bội số 50; \>600mm → bội số 100.
- Giới hạn độ mảnh cột: λ\=l₀/i≤120 (tiết diện chữ nhật: l₀/b≤35).
- Tải trọng sơ bộ tham khảo (Bảng 1.1): nhà ở 8–10 kN/m²; văn phòng/trường học 10–13 kN/m²; TTTM/chung cư/khách sạn 13–16 kN/m² — dùng làm ngưỡng cảnh báo nếu input bất thường.
- Hoạt tải tiêu chuẩn TCVN 2737:2023: phòng học 2kN/m² (γf\=1,3); hành lang/cầu thang 3kN/m² (γf\=1,3); mái không sử dụng 0,3kN/m² (γf\=1,3).
- Hệ số tầm quan trọng công trình γn: mức thấp 0,87; trung bình 1,00; cao 1,15.
- Ngưỡng dầm cần tính như nén lệch tâm: N \> 0,1×Rb×b×h₀ (nếu lực dọc trong dầm vượt ngưỡng này, Input Adapter cần cảnh báo dùng công thức cột thay vì dầm thuần túy).

## 12\. Thuật toán tổng hợp cho Rule Engine (pseudocode mở rộng)

```
function tu_kiem_tra_As(As_etabs, M, N, b, h, h0, mac_be_tong, nhom_thep, loai):
    # Bước tùy chọn: dùng mục 2 để verify As nhận từ ETABS có hợp lý không
    xiR = tinh_xiR(nhom_thep, mac_be_tong)          # mục 2.1
    if loai == "dam":
        Mu = tinh_Mu_dam(As_etabs, b, h0, mac_be_tong, nhom_thep)   # mục 2.3/2.4
        canh_bao_neu(M > Mu * 1.02)                                 # sai lệch bất thường
    else:  # cot
        x = thu_lech_tam_lon(N, As_etabs, b, mac_be_tong, nhom_thep)
        if x > xiR * h0:
            x = thu_lech_tam_be(...)                                # mục 2.5
        Mu = tinh_Mu_cot(...)
        canh_bao_neu(N*e > Mu * 1.02)

function chon_thep_doc(As_yc, b, h, h0, loai_cauKien, do_manh, mac_be_tong, nhom_thep):
    mu_min = tra_mu_min(loai_cauKien, do_manh)          # mục 4.1
    mu_max = 0.03                                        # mục 4.1 — cảnh báo nếu vượt
    As_min = mu_min * b * h0 / 100
    As_target = max(As_yc, As_min)
    ung_vien = sinh_to_hop(As_target, BANG_DUONG_KINH, gioi_han_so_thanh=[2,3,4,5,6])
    ung_vien = loc_theo_khoang_cach(ung_vien, b)         # mục 4.4
    canh_bao_neu(As_target/(b*h0) > mu_max)
    return chon_toi_uu(ung_vien)                          # ≤3 loại đường kính/dầm — mục 4.2

function tinh_cot_dai_va_neo(phan_tu, thep_da_chon, Q, N, mac_be_tong, nhom_thep):
    phi_n = tinh_phi_n(N, mac_be_tong)                   # mục 3.3 — quan trọng cho cột
    kiem_tra_ep_vo_bung(Q, phi_n)                         # mục 3.1
    qsw = tinh_qsw(Q, phi_n, mac_be_tong)                 # mục 3.2
    s = min(s_max_chong_cat, Rsw*Asw/qsw, s_ct_cau_tao)   # mục 5.2/5.3
    L0_an = Rs*As_1thanh/(eta1*eta2*Rbt*chu_vi_thanh)     # mục 6.1
    L_an  = alpha*L0_an*(As_cal/As_ef)                     # mục 6.2
    L_lap = alpha_lap*L0_an*(As_cal/As_ef)                 # mục 6.3
    return {dai: ..., buoc_dai: s, neo: L_an, noi_chong: L_lap}

function xu_ly_truong_hop_bien(phan_tu_hien_tai, phan_tu_lan_can):
    # áp 7 nguyên tắc mục 10.6: gối gần bằng nhau → dùng giá trị lớn;
    # console/dầm phụ M nhỏ → kéo dài thép dầm chính; luôn làm tròn số lượng cốt treo lên
    ...

function kiem_tra_rang_buoc(phan_tu, ket_qua):
    # đối chiếu toàn bộ mục 4-7; nếu vi phạm → vòng lặp tự sửa (xem tài liệu tổng quan bài toán)
```
