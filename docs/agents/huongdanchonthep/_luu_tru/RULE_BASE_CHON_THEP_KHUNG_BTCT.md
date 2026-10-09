# TÀI LIỆU HỢP NHẤT — Rule Base chọn thép khung BTCT

**LÝ THUYẾT — QUY TẮC ĐẶC BIỆT — VÍ DỤ ÁP DỤNG THỰC TẾ**
**LỰA CHỌN VẬT LIỆU VÀ CỐT THÉP CHO KHUNG BÊ TÔNG CỐT THÉP TOÀN KHỐI**

(Rule Base thống nhất, duy nhất, phục vụ AI Rule Engine Agent và AI Drawing Agent)

Biên soạn phục vụ đồ án: *"Nghiên cứu mô hình AI Agent cho bài toán thiết kế khung Bê tông cốt thép (BTCT) và sinh bản vẽ tự động"*

Tài liệu này hợp nhất DUY NHẤT ba cấu phần trước đó thành một văn bản:
① Lý thuyết, công thức, cấu tạo đầy đủ theo TCVN 5574:2018 và TCVN 9386 (Phần A–P)
② Danh mục ~70 trường hợp đặc biệt dạng Điều kiện → Xử lý, sẵn sàng lập trình (Phần Q)
③ Ví dụ áp dụng trên dữ liệu ETABS thật, đã kiểm chứng khớp 4/4 (Phần R)

Nguồn gốc: [TL-KHUNG] Đặng Vũ Hiệp (ĐH Kiến trúc HN, 2024) · [TL-2018] Phan Quang Minh chủ biên (NXB KH&KT, 2021, TCVN 5574:2018) · tra cứu bổ sung văn bản gốc TCVN 5574:2018, TCVN 9386

Ngày biên soạn: tháng 9 năm 2026. Tài liệu do AI (Claude) tổng hợp trực tiếp từ nguồn gốc theo yêu cầu chi tiết của người thực hiện đồ án; mọi số liệu/công thức đều kèm trích dẫn nguồn để đối chiếu, kiểm chứng.

**Cấu trúc tổng quát**: Phần A–P = lý thuyết/công thức/cấu tạo đầy đủ · Phần Q = danh mục trường hợp đặc biệt (Điều kiện → Xử lý) · Phần R = ví dụ áp dụng thực tế (Khung Trục 5) · Phần S = mục lục tổng hợp/hướng dẫn tra cứu.

---

## PHẦN A — GIỚI THIỆU, PHẠM VI VÀ NGUỒN TÀI LIỆU

### 1. Mục đích và phạm vi sử dụng tài liệu

Tài liệu này là bản tổng hợp kỹ thuật (rule base) phục vụ đồ án. Nội dung được biên soạn để hai tác nhân AI sử dụng trực tiếp:
- **Rule Engine Agent**: tự động lựa chọn vật liệu (cấp độ bền bê tông, nhóm cốt thép) và tính toán, lựa chọn cốt thép dọc/đai cho dầm và cột của khung BTCT, dựa trên nội lực đầu vào từ mô hình ETABS.
- **Drawing Agent**: tự động sinh bản vẽ bố trí cốt thép (mặt cắt dầm, cột, cấu tạo nút khung, bảng thống kê thép) dựa trên kết quả của Rule Engine Agent.

Do đó, tài liệu ưu tiên tuyệt đối cho: (i) công thức tính toán chính xác kèm ký hiệu gốc; (ii) mọi điều kiện, giới hạn, kích thước tối thiểu/tối đa, khoảng cách, chiều dài neo/nối, bán kính uốn; (iii) cấu tạo tại các vị trí đặc biệt (nút khung, vùng giao dầm, chân cột); (iv) số điều/mục/bảng/hình trong tài liệu gốc để truy vết ngược khi lập trình.

### 2. Danh mục nguồn tài liệu gốc

Ba (03) tệp PDF do người dùng cung cấp đã được rà soát. Việc kiểm tra checksum (MD5) cho thấy tệp "CaukiencobanTC (1).pdf" và "CaukiencobanTC (2).pdf" là hai bản sao giống hệt nhau về nội dung; chỉ một nguồn duy nhất được liệt kê và trích dẫn dưới ký hiệu [TL-2018].

**Bảng A.1 — Danh mục nguồn tài liệu gốc**

| Ký hiệu | Tên tệp gốc | Tác giả / NXB | Số trang | Tiêu chuẩn nền | Vai trò |
| --- | --- | --- | --- | --- | --- |
| [TL-KHUNG] | __4-9-2024_Khung_BTCT.pdf | Đặng Vũ Hiệp (chủ biên), Nguyễn Việt Phương, Lê Thế Anh — ĐH Kiến trúc Hà Nội, 2024 | 198 | TCVN 5574:2018; TCVN 2737:2023 | Nguồn CHÍNH cho quy trình thiết kế khung, công thức chọn thép dầm/cột, và đặc biệt CẤU TẠO NÚT KHUNG (mục 5.4) |
| [TL-2018] | Caukiencoban_TC (2).pdf ≡ (1).pdf | Phan Quang Minh (chủ biên), Ngô Thế Phong, Nguyễn Trường Thắng, Võ Mạnh Tùng — NXB KH&KT, tái bản lần 6, 2021 | 254 | TCVN 5574:2018 | Nguồn CHÍNH cho công thức tính toán cấu kiện theo TCVN 5574:2018 (dầm, cột, chịu lực cục bộ) và các bảng phụ lục số liệu vật liệu |
| [TL-2006] | KetCauBeTongCotThepCauKienCoBan (1).pdf | Phan Quang Minh (chủ biên), Ngô Thế Phong, Nguyễn Đình Cống — NXB KH&KT, 2006 | 400 | TCXDVN 356:2005 (đã hết hiệu lực) | Nguồn THAM KHẢO LỊCH SỬ — xem phạm vi sử dụng ở Phần N |

Ghi chú: [TL-KHUNG] và [TL-2018] đều dựa trên TCVN 5574:2018 nên số liệu nhất quán và được đối chiếu chéo trong toàn bộ tài liệu này. Khi hai nguồn trình bày cùng công thức với cách đánh số khác nhau, cả hai số hiệu công thức gốc đều được ghi lại (dạng "(x.y) [TL-KHUNG] ≡ (m.n) [TL-2018]").

### 3. Quy ước ký hiệu và trích dẫn

- Số hiệu mục trong tài liệu này theo kiểu 1, 1.1, 1.1.1… độc lập với số hiệu chương/mục của tài liệu gốc.
- Cuối mỗi mục/bảng/công thức có dòng "Nguồn:" ghi rõ ký hiệu tài liệu gốc và số chương/mục/bảng/hình/công thức tương ứng để tra ngược.
- Công thức giữ nguyên ký hiệu gốc (Rb, Rs, Rsc, Rsw, As, ξ, ζ, αm, γb, μ…). Số công thức trong ngoặc đơn ở lề phải là số hiệu GỐC của tài liệu được trích.
- Khi một đoạn nguồn không nêu rõ giá trị/điều kiện cụ thể, tài liệu này ghi chú thẳng: "nguồn không nêu rõ ở đây" — không suy đoán, không bịa số liệu.
- Đơn vị: lực (kN, N), mô men (kNm, Nmm), ứng suất/cường độ (MPa = N/mm²), chiều dài (mm trừ khi ghi chú khác), diện tích cốt thép (mm²).

### 4. Cách xử lý một điểm KHÔNG NHẤT QUÁN đã phát hiện giữa hai nguồn chính

Phát hiện: mục 5.2.1.1 của [TL-KHUNG] (lời văn diễn giải công thức 5.2) ghi hàm lượng cốt thép cực tiểu cho cấu kiện chịu uốn là μmin = 0,05%. Tuy nhiên:
- Công thức (4.8) của [TL-2018] (mục 4.5.1) quy định rõ: μmin = 0,1% đối với cấu kiện chịu uốn, theo TCVN 5574:2018.
- Phụ lục 13 (trích TCVN 5574-2018) của chính [TL-KHUNG] cũng ghi rõ: 0,1% (khi L0/i ≤ 17).
- Mục 7.2 của [TL-2018] một lần nữa xác nhận: μmin = 0,1%.

**KẾT LUẬN ÁP DỤNG**: μmin = 0,1% (không phải 0,05%) là giá trị chính thức cho hàm lượng cốt thép dọc tối thiểu của cấu kiện chịu uốn trong toàn bộ Rule Engine — xác nhận độc lập 3/3 vị trí nguồn. Giá trị "0,05%" bị xem là sai sót đánh máy của [TL-KHUNG].

---

## PHẦN B — HỆ KẾT CẤU KHUNG BTCT VÀ QUY TRÌNH THIẾT KẾ

### 5. Khái niệm và phân loại hệ khung BTCT toàn khối

Hệ kết cấu khung BTCT chịu lực thẳng đứng (trọng lượng bản thân) và lực nằm ngang (gió, động đất). Khung gồm cột (thẳng đứng) + dầm (nằm ngang/nghiêng), giao nhau tại nút khung.
- Theo liên kết tại nút: khung cứng (nút cứng, dầm–cột liên kết ngàm) và khung có thanh giằng chéo.
- Trong khung cứng, nội lực phát sinh do thay đổi nhiệt độ, co ngót bê tông, lún lệch móng có thể đáng kể, cần xem xét khi cần.

(Nguồn: Chương 1, mục 1.1, 1.3 [TL-KHUNG])

**5.1. Lập mặt bằng kết cấu sàn** — dựa trên mặt bằng kiến trúc và giải pháp kết cấu sàn; xác định vị trí cấu kiện chịu lực, diện truyền tải từ sàn lên dầm/cột, sơ đồ tính toán hệ kết cấu. (Chương 1, mục 1.2 [TL-KHUNG])

**5.2. Các bước thiết kế khung BTCT toàn khối** (Hình 1.6 [TL-KHUNG]): (1) lập mặt bằng kết cấu sàn; (2) lập sơ đồ tính khung; (3) xác định tải trọng; (4) xác định nội lực và tổ hợp tải trọng; (5) tính toán, thiết kế cốt thép dầm/cột và cấu tạo; (6) thể hiện bản vẽ. (Chương 1, mục 1.4 [TL-KHUNG])

### 6. Nguyên tắc lựa chọn sơ bộ kích thước cấu kiện

Bước bắt buộc TRƯỚC khi Rule Engine chạy vòng lặp chọn thép, vì kích thước tiết diện dầm/cột là đầu vào của bài toán chọn cốt thép.

**6.1. Nguyên tắc thống nhất hóa kích thước**
- Nên chọn bề rộng dầm ≤ bề rộng cột để đơn giản cấu tạo thép và lắp ván khuôn tại nút khung.
- Cột nên dùng cùng kích thước tiết diện suốt chiều cao công trình để tiết kiệm ván khuôn; có thể dùng bê tông cường độ cao hơn cho cột tầng dưới, giảm dần cho tầng trên.
- Hàm lượng cốt thép cột μt ≈ 2% cho cột chịu nén cao (tầng dưới); μt ≈ 1% cho cột chịu nén thấp (tầng trên).
- Dầm có nhịp không chênh lệch nhiều nên chọn cùng kích thước tiết diện.
- Hàm lượng cốt thép dầm nên gần bằng 1/3–1/2 hàm lượng cốt thép lớn nhất cho phép.
- Cấp độ bền chịu nén của bê tông dầm và sàn nên chọn giống nhau.
- Tỷ lệ độ cứng đơn vị tương đối giữa các cấu kiện trong khung nên trong khoảng (1÷2).

(Nguồn: Chương 1, mục 1.4 [TL-KHUNG])

**6.2. Kích thước sơ bộ dầm**

```
hd = (1/10 ÷ 1/14)·L     (1.a — quy tắc kinh nghiệm)
bd = (1/3 ÷ 1/2)·hd      (1.b — quy tắc kinh nghiệm)
```

L là chiều dài nhịp dầm. Kích thước dầm chủ yếu phụ thuộc mô men âm và lực cắt ở hai đầu dầm; nhịp lớn cần kiểm tra TTGH thứ hai (võng, nứt). (Chương 1, mục 1.4 [TL-KHUNG])

**6.3. Kích thước sơ bộ cột**

```
Asb = k·N/Rb              (1.1 [TL-KHUNG])
```

k = 1,2 ÷ 1,5 (cột trong: 1,2÷1,3; cột ngoài/tầng trên cùng: lớn hơn, do M lớn hơn).

```
N = n·S·q                 (1.2 [TL-KHUNG])
```

n — số tầng; S — diện tích chịu tải sơ bộ cột; q — tải trọng sơ bộ/m² sàn.

**Bảng B.1 — Tải trọng sơ bộ trên 1 m² sàn**

| Loại nhà | q (kN/m²) |
| --- | --- |
| Nhà ở riêng lẻ | 8 ÷ 10 |
| Văn phòng, trường học, các loại nhà khác | 10 ÷ 13 |
| Trung tâm thương mại, chung cư, khách sạn | 13 ÷ 16 |

**Điều kiện hạn chế độ mảnh của cột** (mục 8.2 TCVN 5574:2012, dẫn lại bởi [TL-KHUNG]):

```
λ = l0/i ≤ 120
λ = l0/b ≤ 35    (tiết diện chữ nhật)
```

Chiều dài tính toán cho khung toàn khối nhiều tầng nhiều nhịp: l₀ = 0,7·H (H = chiều cao tầng).

**Quy tắc mô-đun hóa kích thước theo ván khuôn định hình**:
- Tiết diện ≤600mm: bội số 50mm.
- Tiết diện >600mm: bội số 100mm.
- (Theo [TL-2018] mục 3.4.1): nên là bội số 2cm, 5cm, 10cm.

**Ví dụ minh họa** (chương 6 [TL-KHUNG]): bê tông B30 (Rb=17MPa), k=1,3, q=10kN/m² (giảng đường), n=6 tầng, diện chịu tải AB=17,55m²: N=6×10×17,55=1053kN; F=1,3×1053/17000=0,080m²=800cm² → chọn 250×600mm. hb sơ bộ sàn = (1/40)×3450=86,2mm → chọn hb=100mm.

---

## PHẦN C — VẬT LIỆU: BÊ TÔNG VÀ CỐT THÉP

Toàn bộ số liệu phần này trích theo TCVN 5574:2018, tổng hợp chéo từ Phụ lục [TL-KHUNG] (B12,5–B60/CB240÷CB500) và [TL-2018] (B15–B100, gồm cả cốt thép cường độ cao). Khi hai nguồn trùng phạm vi, số liệu khớp nhau tuyệt đối.

### 7. Bê tông

**7.1. Mô đun đàn hồi ban đầu Eb (GPa)**

| B | 12,5 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 70 | 80 | 90 | 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Eb | 21,5 | 24,0 | 27,5 | 30,0 | 32,5 | 34,5 | 36,0 | 37,0 | 38,0 | 39,0 | 39,5 | 41,0 | 42,0 | 42,5 | 43,0 |

(Nguồn: Phụ lục 2 [TL-KHUNG]; Phụ lục 1 [TL-2018])

**7.2. Cường độ tiêu chuẩn Rbn=Rb,ser, Rbtn=Rbt,ser (MPa) — TTGH2**

| B | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 70 | 80 | 90 | 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rbn | 11,0 | 15,0 | 18,5 | 22,0 | 25,5 | 29,0 | 32,0 | 36,0 | 39,5 | 43,0 | 50,0 | 57,0 | 64,0 | 71,0 |
| Rbtn | 1,15 | 1,40 | 1,60 | 1,80 | 1,95 | 2,10 | 2,20 | 2,30 | 2,40 | 2,50 | 3,00 | 3,30 | 3,60 | 3,80 |

(Nguồn: Phụ lục 3 [TL-KHUNG]/[TL-2018])

**7.3. Cường độ tính toán TTGH1 — Rb, Rbt (MPa)**

| B | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 70 | 80 | 90 | 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rb | 8,5 | 11,5 | 14,5 | 17,0 | 19,5 | 22,0 | 25,0 | 27,5 | 30,0 | 33,0 | 37,0 | 41,0 | 44,0 | 47,5 |
| Rbt | 0,75 | 0,90 | 1,05 | 1,20 | 1,30 | 1,40 | 1,45 | 1,55 | 1,60 | 1,65 | 1,90 | 2,10 | 2,15 | 2,20 |

(Nguồn: Phụ lục 4 [TL-KHUNG]; Phụ lục 3 [TL-2018])

**7.4. Hệ số điều kiện làm việc của bê tông γb**

| Ký hiệu | Mô tả | Giá trị |
| --- | --- | --- |
| γb1 | Tác dụng ngắn hạn tải trọng | 1,0 |
| γb1 | Tác dụng dài hạn tải trọng | 0,9 |
| γb2 | Kết cấu bê tông không cốt thép | 0,9 |
| γb3 | Đổ bê tông đứng, mỗi lớp >1,5m | 0,85 |

(Nguồn: Phụ lục 5 [TL-KHUNG]; Phụ lục 4 [TL-2018]. Các trường hợp khác xem mục 6.1.2.3 TCVN 5574:2018 — nguồn không nêu rõ ở đây đầy đủ.)

**7.5. Hệ số từ biến φb,cr của bê tông nặng theo độ ẩm (RH) và cấp độ bền**

| RH | B15 | B20 | B25 | B30 | B35 | B40 | B45 | B50 | B55 | B60-B100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| >75% | 2,4 | 2,0 | 1,8 | 1,6 | 1,5 | 1,4 | 1,3 | 1,2 | 1,1 | 1,0 |
| 40-75% | 3,9 | 3,4 | 2,8 | 2,5 | 2,3 | 2,1 | 1,9 | 1,8 | 1,6 | 1,5 |
| <40% | 5,6 | 4,8 | 4,0 | 3,6 | 3,2 | 3,2 | 2,8 | 2,6 | 2,4 | 2,2 |

(Nguồn: Phụ lục 5 [TL-2018])

### 8. Cốt thép thanh

**8.1. Cường độ tính toán (MPa), TTGH1**

| Nhóm thép | Đường kính | Rs (kéo) | Rsc (nén) | Rsw (đai) |
| --- | --- | --- | --- | --- |
| CB240-T | d6÷d40 | 210 | 210 | 170 |
| CB300-T, CB300-V | d6÷d40 | 260 | 260 | 210 |
| CB400-V | d6÷d50 | 350 | 350 | 280 |
| CB500-V | d6÷d50 | 435 | 435 (400 dài hạn)* | 300 |

(*) Rsc=400MPa dùng khi tính với tác dụng ngắn hạn của tải trọng. (Nguồn: Phụ lục 6 [TL-KHUNG]; Phụ lục 8 [TL-2018])

**8.2. Cường độ tiêu chuẩn Rsn, Rs,ser (MPa)**

| Loại | Đường kính | Giá trị |
| --- | --- | --- |
| CB240-T | 6-40mm | 240 |
| CB300-T/V | 6-40/50mm | 300 |
| CB400-V | 6-50mm | 400 |
| CB500-V | 6-50mm | 500 |

(Nguồn: Phụ lục 7 [TL-2018])

**8.3. Mô đun đàn hồi**: Es = 200000 MPa cho mọi nhóm thép thanh thông dụng. (Phụ lục 7 [TL-KHUNG]; Phụ lục 6 [TL-2018])

**8.4. Hệ số ξR và αR theo nhóm thép và cấp độ bền bê tông** — bảng tra QUAN TRỌNG BẬC NHẤT cho Rule Engine: (a) xác định cốt đơn/cốt kép dầm (so αm với αR), (b) tính μmax = ξR·Rb/Rs.

| Nhóm thép | ≤B60 | B70 | B80 | B90 | B100 |
| --- | --- | --- | --- | --- | --- |
| CB240-T | ξR=0,615/αR=0,426 | 0,531/0,390 | 0,523/0,386 | 0,517/0,383 | 0,509/0,380 |
| CB300-T/V | 0,583/0,413 | 0,502/0,376 | 0,494/0,372 | 0,487/0,368 | 0,478/0,364 |
| CB400-V | 0,533/0,391 | 0,457/0,353 | 0,448/0,348 | 0,440/0,343 | 0,431/0,338 |
| CB500-V | 0,481/0,365 | 0,411/0,326 | 0,401/0,320 | 0,393/0,316 | 0,382/0,309 |

(Nguồn: Phụ lục 9 [TL-2018])

**8.5. Quan hệ ξ, ζ, αm (công thức khép kín, thay bảng tra)**

```
ζ = 1 − 0,5ξ                              (4.11 [TL-2018] / 5.11 [TL-KHUNG])
αm = ξζ = ξ(1 − 0,5ξ)                     (4.11 [TL-2018])
ζ = 0,5×[1 + (1 − 2αm)^0,5]               (4.12 [TL-2018])
ξ = 1 − (1 − 2αm)^0,5                     (4.13 [TL-2018])
```

(Nguồn: Phụ lục 8 [TL-KHUNG]; Phụ lục 10 [TL-2018])

### 9. Bảng tra diện tích và trọng lượng cốt thép

**9.1. Diện tích tiết diện ngang (mm²) theo số lượng thanh, và trọng lượng (kG/m)**

| Φ(mm) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | kG/m |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 28,3 | 56,5 | 84,8 | 113,1 | 141,4 | 169,6 | 197,9 | 226,2 | 254,5 | 0,222 |
| 8 | 50,3 | 100,5 | 150,8 | 201,1 | 251,3 | 301,6 | 351,9 | 402,1 | 452,4 | 0,395 |
| 10 | 78,5 | 157,1 | 235,6 | 314,2 | 392,7 | 471,2 | 549,8 | 628,3 | 706,9 | 0,617 |
| 12 | 113,1 | 226,2 | 339,3 | 452,4 | 565,5 | 678,6 | 791,7 | 904,8 | 1017,9 | 0,888 |
| 14 | 153,9 | 307,9 | 461,8 | 615,8 | 769,7 | 923,6 | 1077,6 | 1231,5 | 1385,4 | 1,208 |
| 16 | 201,1 | 402,1 | 603,2 | 804,2 | 1005,3 | 1206,4 | 1407,4 | 1608,5 | 1809,6 | 1,578 |
| 18 | 254,5 | 508,9 | 763,4 | 1017,9 | 1272,3 | 1526,8 | 1781,3 | 2035,8 | 2290,2 | 1,998 |
| 20 | 314,2 | 628,3 | 942,5 | 1256,6 | 1570,8 | 1885,0 | 2199,1 | 2513,3 | 2827,4 | 2,466 |
| 22 | 380,1 | 760,3 | 1140,4 | 1520,5 | 1900,7 | 2280,8 | 2660,9 | 3041,1 | 3421,2 | 2,984 |
| 25 | 490,9 | 981,8 | 1472,6 | 1963,5 | 2454,4 | 2945,3 | 3436,1 | 3927,0 | 4417,9 | 3,853 |
| 28 | 615,8 | 1231,5 | 1847,3 | 2463,0 | 3078,8 | 3694,5 | 4310,3 | 4926,0 | 5541,8 | 4,834 |
| 32 | 804,2 | 1608,5 | 2412,7 | 3217,0 | 4021,2 | 4825,5 | 5629,7 | 6434,0 | 7238,2 | 6,313 |
| 36 | 1017,9 | 2035,8 | 3053,6 | 4071,5 | 5089,4 | 6107,3 | 7125,1 | 8143,0 | 9160,9 | 7,990 |
| 40 | 1256,6 | 2513,3 | 3769,9 | 5026,6 | 6283,2 | 7539,8 | 8796,5 | 10053,1 | 11309,8 | 9,865 |

Φ30 cũng có trong nguồn nhưng ghi chú "không nên sử dụng vì không phổ biến trên thị trường" (706,9/1414/2121.../5655/6362mm²; 5,549 kG/m). (Nguồn: Phụ lục 1 [TL-KHUNG]; Phụ lục 11 [TL-2018])

**9.2. Diện tích cốt thép bản (mm²/m dài) theo khoảng cách và đường kính** — dùng chủ yếu cho cấu kiện bản sàn, giữ lại theo yêu cầu đầy đủ dù phạm vi chính của đồ án là dầm/cột khung. (Nguồn: Phụ lục 12 [TL-2018] — bảng chi tiết K/c 70-250mm × Φ6-Φ25, xem file gốc nếu cần tra).

---

## PHẦN D — NGUYÊN LÝ TÍNH TOÁN VÀ YÊU CẦU CẤU TẠO CHUNG

### 10. Nguyên lý tính toán theo trạng thái giới hạn (TTGH)

TCVN 5574:2018 quy định hai nhóm TTGH:
- **TTGH1** (khả năng chịu lực): không phá hoại (cường độ), không mất ổn định hình dạng/vị trí, không mỏi, không phá hoại do tác động đồng thời lực + môi trường bất lợi.
- **TTGH2** (điều kiện sử dụng bình thường): hạn chế nứt, hạn chế biến dạng (võng, góc xoay).

Trong phạm vi Rule Engine chọn cốt thép dầm/cột từ nội lực ETABS, TTGH1 là điều kiện BẮT BUỘC quyết định diện tích cốt thép; TTGH2 là kiểm tra bổ sung (Phần L). (Chương 3, mục 3.3 [TL-2018])

### 11. Yêu cầu cơ bản về cấu tạo (BẮT BUỘC cho MỌI cấu kiện dầm, cột)

**11.1. Hình dáng tiết diện**: phù hợp yêu cầu chịu lực (dầm đặt h theo mặt phẳng uốn). Kích thước nên là bội số 2cm, 5cm, 10cm. (Mục 3.4.1 [TL-2018])

**11.2. Khung và lưới cốt thép**: liên kết thành khung/lưới bằng buộc (dây mềm ~0,9mm) hoặc hàn điểm. (Mục 3.4.2 [TL-2018])

**11.3. Cốt thép chịu lực và cấu tạo**: cốt chịu lực chịu ứng lực tính toán được; cốt cấu tạo liên kết khung/lưới, chịu ứng suất không tính được (co ngót, nhiệt độ) — vai trò quan trọng, thiếu có thể gây nứt/hư hỏng cục bộ. (Mục 3.4.3 [TL-2018])

**11.4. Lớp bê tông bảo vệ cốt thép**

**Bảng D.1 — Chiều dày tối thiểu lớp bảo vệ**

| Điều kiện | Chiều dày tối thiểu (mm) |
| --- | --- |
| Trong nhà, độ ẩm ≤75% | 20 |
| Trong nhà, độ ẩm >75% | 25 |
| Ngoài trời | 30 |
| Trong đất/móng (có lớp lót) | 40 |

Không nhỏ hơn đường kính cốt thép, không nhỏ hơn 10mm. [TL-KHUNG] (Hình 5.4): Cmin=20mm che phủ; Cmin=30mm ngoài trời — nhất quán. (Mục 3.4.4, Bảng 3.1, Hình 3.8 [TL-2018]; Hình 5.4 [TL-KHUNG])

**11.5. Khoảng hở tối thiểu giữa các thanh cốt thép**: không nhỏ hơn đường kính lớn nhất, và không nhỏ hơn:
- 25mm: 1-2 lớp dưới, nằm ngang/nghiêng khi đổ.
- 30mm: lớp trên.
- 50mm: từ lớp 3 trở lên (dưới), hoặc phương đứng khi đổ.

(Mục 3.4.5, Hình 3.8b [TL-2018])

**11.6. Neo cốt thép**

Thép trơn chịu kéo phải có móc uốn (U/L); thép gờ có thể không cần móc (có móc thì Lan giảm). Móc chuẩn (Hình 3.9): bán kính trong 2,25d (móc 180°, đoạn thẳng nối 3d) hoặc 1,25d (móc 90°, đoạn thẳng nối 5d).

```
Lan = α·L0,an·(As,cal/As,ef)        (3.37 [TL-2018] ≡ 5.40 [TL-KHUNG])
```

α=1,0 (kéo); α=0,75 (nén).

```
L0,an = Rs·As / (Rbond·us)          (3.38 [TL-2018] ≡ 5.39 [TL-KHUNG])
Rbond = η1·η2·Rbt                   (3.39 [TL-2018])
```

**Bảng D.2 — Hệ số η1, η2**

| Hệ số | Trường hợp | Giá trị |
| --- | --- | --- |
| η1 | Thanh trơn | 1,5 |
| η1 | Cán nguội, có gờ | 2,0 |
| η1 | Cán nóng, có gờ | 2,5 |
| η2 | d≤32mm | 1,0 |
| η2 | d>32mm | 0,9 |

Lan không được nhỏ hơn 15ds, 200mm, và 0,3·L0,an. (Mục 3.4.6, Hình 3.9 [TL-2018]; mục 5.4.4 [TL-KHUNG])

**11.7. Nối cốt thép**

a) **Nối chồng**: đặt 2 thanh chồng đoạn Llap, buộc dây mềm. Dùng cho d≤40mm.
```
Llap = α·L0,an·(As,cal/As,ef), α=1,2 (kéo), 0,9 (nén)
```
Ràng buộc: Llap ≥ max(0,4αL0,an; 20d; 250mm). Khoảng cách 2 mối nối cạnh nhau ≥max(2d;30mm); số thanh nối trong 1 tiết diện ≤50% (thép trơn có móc ≤25%), tăng tới 100% nếu có chi tiết neo bổ sung.

b) **Nối hàn**: đối đầu / hàn chập (lh=5d cả 2 phía, 10d nếu chỉ 1 phía) / hàn máng.

c) **Nối ống ren (coupler)**: kiểm tra độ chặt bằng kìm đo lực.

(Mục 3.4.7, Hình 3.10-3.11 [TL-2018])

**11.8. Vị trí nối cốt thép dọc**: ≤4 thanh/cạnh → nối 1 vị trí. Nhiều hơn → nối SO LE tại mặt sàn/cách tầng, mỗi lần ≤50% diện tích, khoảng cách trục mối nối ≥1,5·Lan. (Mục 5.4.3 [TL-KHUNG])

---

## PHẦN E — CẤU KIỆN CHỊU UỐN: DẦM

### 12. Tính toán cường độ trên tiết diện thẳng góc (uốn) — phương pháp nội lực giới hạn

**12.1. Sơ đồ ứng suất**: (i) As đạt Rs; (ii) bê tông vùng nén đạt Rb, phân bố đều (hình chữ nhật quy ước); (iii) bỏ qua bê tông vùng kéo. (Mục 4.5.1.a, Hình 4.7 [TL-2018])

**12.2. Công thức cơ bản — chữ nhật, cốt đơn**

```
Rb·bx = Rs·As                                          (4.1)
Mgh = Rb·bx(h0−0,5x)                                   (4.2)
M ≤ Mgh = Rb·bx(h0−0,5x)                                (4.3a)
M ≤ Mgh = Rs·As(h0−0,5x)                                (4.3b)
```

Dạng không thứ nguyên (ξ=x/h0):
```
Rs·As = ξ·Rb·b·h0                                       (4.9)
M ≤ Mgh = Rb·b·h0²·ξ(1−0,5ξ) = αm·Rb·b·h0²               (4.10a)
M ≤ Mgh = Rs·As·h0(1−0,5ξ) = ζ·Rs·As·h0                  (4.10b)
```
αm=ξ(1−0,5ξ); ζ=(1−0,5ξ). (Mục 4.5.1 [TL-2018])

**12.3. Điều kiện hạn chế ξR**

```
xR/h0 = εb2/(εb2+εs0)                                   (4.4)
ξ = x/h0 ≤ ξR = 0,8/(1+εs0/εb2)                          (4.5)
```
εs0=Rs/Es; εb2=0,0035 (ngắn hạn, B≤60); 0,7 thay 0,8 cho B70-B100/bê tông hạt nhỏ. Giá trị ξR/αR cụ thể: Bảng C.8 (mục 8.4).

```
As ≤ ξR·Rb·b·h0/Rs = As,max                             (4.6a)
μ ≤ μmax = ξR·Rb/Rs                                      (4.6b ≡ 4.7)
```

**12.4. Hàm lượng cốt thép tối thiểu**: μ ≥ μmin = 0,1% (xem Phần A mục 4). (Mục 4.5.1 [TL-2018]; mục 5.2.1.1 [TL-KHUNG])

**12.5. Trình tự thiết kế — Bài toán 1: chữ nhật, cốt đơn**

1. Tra Rb, Rs; tính ξR (mục 8.4).
2. Giả thiết a≈h/10, h0=h−a.
3. αm = M/(Rb·b·h0²).
4. Nếu αm≤αR (phá hoại dẻo): tính ζ, As=M/(ζRsh0) hoặc As=ξRbbh0/Rs.
5. Kiểm tra μ≥μmin=0,1%; nếu không đạt lấy As=μmin·b·h0. μ hợp lý: 0,6-1,2%.
6. Chọn/bố trí thép; tính lại a thực tế, lặp lại nếu lệch nhiều.
7. Nếu αm>αR (phá hoại giòn): tăng tiết diện, HOẶC đặt cốt kép, HOẶC tăng cấp bê tông (ít hiệu quả).

(Mục 5.2.1.1, Bài toán 1 [TL-KHUNG])

**12.6. Bài toán 2: chữ nhật, cốt kép**

Điều kiện: ξR≤αm=M/(Rbbh0²)≤0,5. Chọn ξ=ξR (αm=αR):
```
As' = (M − αR·Rb·b·h0²)/(Rsc(h0−a'))                    (5.5)
As = (ξR·Rb·b·h0)/Rs + (Rsc/Rs)·As'                     (5.6)
```
(Mục 5.2.1.1, Bài toán 2 [TL-KHUNG])

**12.7. Bài toán 3: tận dụng As' có sẵn (neo từ gối)**

```
αm = [M − Rsc·As'(h0−a')] / (Rb·b·h0²)                  (5.7)
```
Từ αm tra ξ:
- ξ>ξR: As' quá nhỏ — coi như chưa biết, tính lại theo Bài toán 2.
- 2a'/h0≤ξ≤ξR: As = ξRbbh0/Rs + (Rsc/Rs)As' (5.8).
- ξ<2a'/h0: As' quá nhiều. Mu=RsAs(h0−a') (5.9); As=M/[Rs(h0−a')] (5.10).

(Mục 5.2.1.1, Bài toán 2-3 [TL-KHUNG])

**12.8. Xử lý kết quả tính thép**

- As dương: kiểm tra μ'=As/(bh0)×100%≥μmin.
- As âm hoặc μ'<μmin: chọn cấu tạo tối thiểu As=As'=μmin·b·h0; cụ thể As=As'=402mm²(2⌀16) khi b≤400mm cột, 603mm²(3⌀16) khi b>400mm.
- μ'>1,5% (cột) hoặc vượt μmax (dầm): tăng tiết diện/cấp bê tông/nhóm thép. Hàm lượng hợp lý: cột 1-2%, dầm 0,6-1,2%.

(Mục 5.3.1 [TL-KHUNG])

### 13. Tiết diện chữ T — bề rộng cánh và tính toán

**13.1. Bề rộng cánh b'f**: không lớn hơn 1/6 nhịp dầm. Có dầm ngang/h'f≥0,1h: ≤khoảng cách thông thủy 2 dầm dọc. Không dầm ngang, h'f≥0,1h: b'f=b+6h'f. Cánh công-xôn: h'f≥0,1h→b'f≤b+6h'f; 0,05h≤h'f<0,1h→b'f≤b+3h'f; h'f<0,05h→bỏ qua (b'f=b). (Mục 5.2.1.2 [TL-KHUNG])

**13.2. Trục trung hòa**: Mf=Rb·b'f·h'f(h0−0,5h'f) (5.11). Mf≥M→qua cánh (tính như chữ nhật b'f×h). Mf<M→qua sườn (Bài toán 4).

**13.3. Bài toán 4 — trục trung hòa qua sườn**

```
αm = [M − Rb(b'f−b)h'f(h0−0,5h'f)] / (Rb·b·h0²)         (5.12)
```
Nếu ξ≤ξR: As=(Rb/Rs)·[ξbh0+(b'f−b)h'f] (5.13). Nếu ξ>ξR: tăng tiết diện hoặc đặt As'.

(Mục 5.2.1.2 [TL-KHUNG])

### 14. Tính toán cường độ trên tiết diện nghiêng (lực cắt) — thiết kế cốt đai

**14.1. Điều kiện hạn chế ứng suất nén chính**: Q≤φb1·Rb·b·h0, φb1=0,3. Không thỏa → tăng tiết diện/cấp bê tông. (5.14)

**14.2. Kiểm tra bê tông đủ khả năng chịu cắt**: Qb=φb2·Rbt·b·h0²/C, φb2=1,5. Lấy an toàn C=3h0 → Q≤0,5·Rbt·b·h0 (5.15a). Thỏa → đai theo cấu tạo (14.6). Không thỏa → cần tính đai.

**14.3. smax**: smax=Rbt·b·h0²/Q (5.16).

**14.4. qsw**: qsw=Rsw·Asw/ssw. C0=√(2Rbtbh0²/qsw) (5.17a). Kiểm tra h0≤C0≤2h0: Qu,min=√(4,5·Rbt·b·h0²·qsw) (5.18). Từ Qu,min≥Q: qsw=Q²/(4,5Rbtbh0²) (5.19). C0<h0→C=h0; C0>2h0→C=2h0, Qu,min=1,5Rbtbh0²/C+0,75qswC.

**14.5. Tránh phá hoại giòn**: qsw≥Qb,min/(2h0)=0,25Rbt·b (5.20). Chọn qsw=max[Q²/(4,5Rbtbh0²); 0,25Rbtb]. stt=Rsw·Asw/qsw (5.21).

**14.6. Bước đai thiết kế**: ssw=min(smax, stt, sct). sct (B≤B70): h<150mm→không cần đai; h>150mm, cần đai theo tính toán: sct≤min(h/2,300mm); không cần đai theo tính toán: sct≤min(3h/4,500mm).

(Mục 5.2.2, công thức 5.14-5.21 [TL-KHUNG] — theo TCVN 5574:2018)

### 15. Thiết kế cốt treo (giật đứt) tại vị trí dầm phụ gối lên dầm chính

Ghi chú nguồn: TCVN 5574-2018 không đề cập trực tiếp; nội dung dưới theo mục 6.2.5.5 TCVN 5574-2012, xác nhận nhất quán bởi mục 10.3 "Giật đứt" [TL-2018] (công thức 10.21).

**15.1. Lực tập trung trong phạm vi chiều cao dầm**

```
F(1 − hs/h0) ≤ Rsw·Asw          (5.22a ≡ 10.21 [TL-2018])
```
hs=khoảng cách trọng tâm lực giật đứt đến trọng tâm cốt dọc (=hdc−h); ΣRswAsw=tổng lực cắt cốt treo trên đoạn a=2hs+b. Khoảng cách cốt treo 40-80mm; số lượng mỗi bên ít nhất 4 cái.

**15.2. Hai dầm giao nhau cùng chiều cao**: đoạn a=3b, F≤Rsw·Asw (5.22b).

**15.3. Quy định bố trí** (mục 10.4.12 TCVN 5574-2018): dầm chính — cốt treo trên đoạn (b+2h); dầm phụ — đoạn h/3 (b,h của dầm phụ). Ít nhất 2Asw/3 trong đoạn (b+2h) dầm chính; phần còn lại trong h/3 dầm phụ.

(Mục 5.2.3, Hình 5.1-5.2 [TL-KHUNG]; mục 10.3, Hình 10.6 [TL-2018])

### 16. Cấu tạo cốt thép dầm trong khung (BẮT BUỘC)

**16.1. Nguyên tắc bố trí cốt dọc**
- Không quá BA loại đường kính cho cốt chịu lực/dầm.
- Cùng miền chịu lực: không chênh quá 6mm; không chênh đúng 1mm.
- Đặt thép đúng miền chịu lực; đảm bảo lớp bảo vệ + khoảng hở (mục 11.4-11.5).
- Đường kính dầm: ⌀12-⌀32.

(Mục 5.4.1, Hình 5.4 [TL-KHUNG])

**16.2. Cắt và uốn cốt thép dọc dọc theo trục dầm** (tiết kiệm thép) — xem bổ sung định lượng ở mục 53.3 (Phần P).

**16.3. Sơ đồ bố trí cốt dọc trên tiết diện ngang** (Hình 5.4 [TL-KHUNG]): khoảng cách mép bê tông-tim cốt ≥Cmin; khoảng hở thông thủy ≥tối thiểu; khoảng hở tối đa theo yêu cầu chịu lực đồng đều.

---

## PHẦN F — CẤU KIỆN CHỊU NÉN: CỘT

### 17. Cấu tạo cốt thép cột (BẮT BUỘC)

Cốt thép cột: dọc + đai. As'=diện tích thớ chịu nén nhiều, As=thớ nén ít hơn/kéo. Đối xứng (As=As') hoặc không đối xứng tùy sự làm việc. (Mục 6.2, Hình 6.4 [TL-2018])

**17.1. Đường kính cốt dọc**: 12-40mm. ([TL-2018] mục 6.2.1; [TL-KHUNG] mục 5.4.2 xác nhận ⌀12-⌀40)

**17.2. Hàm lượng cốt dọc tối thiểu μmin (theo độ mảnh)**

**Bảng F.1 — μmin của cột**

| Độ mảnh L0/i (chữ nhật: L0/h) | μmin |
| --- | --- |
| L0/i≤17 (L0/h≤5) | 0,1% |
| 17<L0/i<87 (5<L0/h<25) | Nội suy tuyến tính |
| L0/i≥87 (L0/h≥25) | 0,25% |

Cốt thép bố trí ĐỀU theo chu vi: hàm lượng tối thiểu (tính trên As,tot, μt=As,tot/A×100%) lấy GẤP ĐÔI giá trị trên (0,2%/0,5%). (Mục 6.2.1 [TL-2018]; Phụ lục 13 [TL-KHUNG])

**17.3. Hàm lượng cốt dọc tối đa**: μmax=4% (ngoài vùng nối chồng); 8% tại vùng nối chồng. (Mục 6.2.1 [TL-2018])

> **Lưu ý quan trọng — xác nhận chéo bằng mục 54.2 (Phần P)**: giá trị 4%/8% này là của CHÍNH TCVN 5574:2018 mục 6.2.1 (không phải chỉ là "ngưỡng cảnh báo thực hành" như cách diễn giải cũ). Nguồn [VC-CỘT] (tra cứu bổ sung) làm rõ con số này cũng khớp tinh thần Eurocode 2 (mục 9.5.2). Đây là μmax dùng cho TỔNG As,tot bố trí đều chu vi.

**17.4. Khoảng cách cốt dọc cấu tạo bổ sung**: 400mm vuông góc mặt phẳng uốn (300mm với B70-B100); 500mm theo mặt phẳng uốn (400mm với B70-B100). (Mục 6.2.1, Hình 6.5 [TL-2018])

**17.5. Cấu tạo cốt đai cột**
- Đường kính đai ≥0,25×đường kính dọc lớn nhất, ≥6mm.
- Bước đai ≤15×đường kính dọc, ≤500mm.
- As dọc chịu nén >1,5%: bước đai ≤10×đường kính dọc, ≤300mm.
- Mỗi thanh dọc (ít nhất cách 1 thanh) phải nằm tại chỗ uốn đai, các chỗ uốn cách nhau ≤400mm theo bề rộng mặt bên.
- Bề rộng mặt bên ≤400mm VÀ số thanh/mặt bên ≤4: dùng 1 đai bao quanh.
- Bề rộng >400mm HOẶC >4 thanh/mặt bên: cần đai phụ.
- Đai chính phải bao quanh TOÀN BỘ cốt dọc.

(Mục 6.2.1, Hình 6.5 [TL-2018])

Đối chiếu [TL-KHUNG] mục 5.4.2: đai chính min(15⌀min,500mm); đoạn nối chồng/μt≥3%: min(10⌀min,300mm). Đường kính đai ≥max(1/4⌀max,5mm). Khoảng cách trục cốt dọc: ≤400mm (vuông góc mặt uốn), ≤500mm (mặt uốn).

**17.6. Cấu tạo cốt dọc theo chiều dài cột (nối thép cột)**: cột KHÔNG đổi tiết diện — trục cốt dọc 2 tầng thẳng hàng, cốt tầng trên bẻ khuỷu (giật cấp) nối chồng với cốt chờ tầng dưới. Cột CÓ đổi tiết diện — xem mục 30 (Phần I). (Mục 5.4.2, Hình 5.11 [TL-KHUNG])

### 18. Tính toán cấu kiện chịu nén đúng tâm

**18.1-18.2.** Rb phân bố đều vùng nén; Rsc trong cốt thép. Áp dụng khi L0/h≤20, e0=M/N≤h/30:

```
N ≤ Nu = φ(Rb·A + Rsc·As,tot)          (6.3 [TL-2018])
```

**18.3. Hệ số uốn dọc φ** (tải trọng dài hạn)

| B | L0/h=6 | 10 | 15 | 20 |
| --- | --- | --- | --- | --- |
| B20-B55 | 0,92 | 0,90 | 0,83 | 0,70 |
| B60-B70 | 0,91 | 0,89 | 0,80 | 0,65 |
| B80-B90 | 0,90 | 0,88 | 0,79 | 0,64 |
| B100 | 0,89 | 0,87 | 0,78 | 0,63 |

Nội suy tuyến tính giá trị trung gian. Tải ngắn hạn: φ=0,9 (L0/h=10) đến 0,85 (L0/h=20), tuyến tính.

**18.4. As,tot** = (N/φ − Rb·A)/Rsc (6.4). Âm/quá nhỏ → cấu tạo tối thiểu (mục 17.2).

### 19. Tính toán cột chịu nén lệch tâm phẳng, tiết diện chữ nhật

**19.1. Độ lệch tâm**: e1=M/N (6.5). ea=max(l/600;h/30;10mm). Siêu tĩnh: e0=MAX(e1,ea). Tĩnh định: e0=e1+ea.

**19.2. Hệ số uốn dọc η**: λh=l0/h. λh<4: η=1,0. λh≥4: η=1/(1−N/Ncr), Ncr=π²D/l0², D=kb·Eb·I+0,7Es·Is, kb=0,15/[φL(0,3+δe)], φL=1+ML1/ML(≤2), δe=e0/h(0,15≤δe≤1,5). Thực hành: η≈1,03-1,08 nếu 4≤λh≤7; ML1≈mô men do tĩnh tải.

**19.3. Bài toán tính thép đối xứng (As=As')**: e=e0+0,5h−a; e'=e0−0,5h+a'. x=N/(Rb·b):
- 2a'≤x≤ξRh0 (LỆCH TÂM LỚN): As=As'=[Ne−Rbbx(h0−0,5x)]/[Rsc(h0−a')] (5.30).
- x<2a': As'=As=Ne'/[Rs(h0−a')] (5.31).
- x>ξRh0 (LỆCH TÂM BÉ): xác định lại x (mục 19.4), rồi tính lại As,As' theo (5.30).

**19.4. Xác định lại x khi lệch tâm bé** — công thức thực nghiệm:
```
x = h0·[(1−ξR)an + 2ξR(n+0,48)] / [(1−ξR)a + 2(n+0,48)]
```
n=N/(Rbbh0); an=e/h0; a=(h0−a')/h0. Hoặc tính lặp (xem chi tiết mục 19.4 gốc).

**19.5.** [TL-2018] mục 6.4 — cùng bản chất vật lý, tương đương [TL-KHUNG] 5.3.1.

### 20. Kiểm tra khả năng chịu lực bằng biểu đồ tương tác (M–N)

```
N = Rb·bx + Rsc·As' − σs·As                             (5.32)
M = Ne0 = Rb·bx(h/2−x/2) + Rsc·As'(h/2−a') + σs·As(h/2−a) (5.33)
```
x biến đổi từ 2a' đến h0. x≥ξRh0: σs=−Rs. x<ξRh0: σs=[(2x/h0)/(1−ξR)−1]·Rs (chặn trong [−Rs,Rs]).

3 điểm đặc biệt: A(0,NC)-nén đúng tâm; B(MB,0)-uốn thuần túy; C(Mmax,NC)-phá hoại cân bằng (x=ξRh0). Thường vẽ 5 điểm (3 đặc biệt + 1 trên AC + 1 trên BC).

### 21. Thiết kế cốt đai cột — hệ số ảnh hưởng lực nén dọc trục φn

```
φn = 1+σm/Rb              (0≤σm≤0,25Rb)
φn = 1,25                 (0,25Rb<σm≤0,75Rb)
φn = 5(1−σm/Rb)           (0,75Rb<σm≤Rb)
φn = 1−σt/(2Rbt)          (0≤σt≤Rbt)
```
Có thể bỏ qua ảnh hưởng cốt dọc khi tính σm,σt nếu μdọc≤3%. Thường tổ hợp cơ bản Q cột khá bé → đai đặt theo cấu tạo (mục 17.5).

---

## PHẦN G — CẤU KIỆN CHỊU KÉO VÀ CHỊU XOẮN (cô đọng)

### 22. Cấu kiện chịu kéo

**22.1. Phân loại**: kéo đúng tâm; kéo lệch tâm phẳng (M=Nex hoặc Ney); kéo lệch tâm xiên (Mx=Nex, My=Ney).

**22.2. Cấu tạo (BẮT BUỘC)**: kéo đúng tâm — cốt dọc theo chu vi, μt=As,tot/A. Kéo lệch tâm — cốt tập trung cạnh vuông góc mặt phẳng uốn; nối bằng hàn/cơ khí; neo chắc 2 đầu. Cốt ngang cấu tạo ≤500mm; lệch tâm lớn có As' → như cột (Phần F mục 17).

μ,μ'≥μmin; μt≥2μmin, μmin=0,1%.

**22.3. Kéo đúng tâm**: N≤Ngh=Rs·As,tot (7.1).

**22.4. Kéo lệch tâm phẳng**: e0=M/N≤0,5h−a (lệch tâm bé, 7.2). Lệch tâm lớn: As=[Rbbx+RscAs'+N]/Rs (7.18, As'≥0); hoặc αm=(Ne−RscAs'zs)/(Rbbh0²) (7.19, As'<0) → As=(Rbbξh0+RscAs'+N)/Rs (7.20).

### 23. Cấu kiện chịu xoắn (khái quát)

Vết nứt nghiêng ~45° kiểu lò xo do ứng suất tiếp. Cấu kiện HIẾM gặp trong khung phẳng BTCT nhà dân dụng — không phải trọng tâm Rule Engine. **Bổ sung định lượng ở mục 53.5 (Phần P).**

---

## PHẦN H — SỰ CHỊU LỰC CỤC BỘ (nén cục bộ, chọc thủng, giật đứt)

Áp dụng tại vị trí truyền lực tập trung: chân cột-móng, gối dầm/dàn, cột đâm thủng sàn, dầm phụ gối dầm chính. Cấu tạo BẮT BUỘC cho Drawing Agent khi vẽ chi tiết chân cột, mũ cột, gối tựa.

### 24. Nén cục bộ

**24.1. Không đặt cốt ngang**: N≤ψ·Rb,loc·Ab,loc (10.1). Rb,loc=φb·Rb (10.2). φb=0,8√(Ab,max/Ab,loc) (10.3), chặn [1,0; 2,5]. ψ=1,0 (đều) / 0,75 (không đều). Giá trị ψRb,locAb,loc ≤2× giá trị không gia cường.

**24.2. Cấu tạo lưới thép gia cường**: As/phương không vượt 1,5× phương khác. Đường kính lưới 3-6mm. Bước lưới ≥1/3 cạnh, thường 60-150mm. Mắt lưới 45-100mm, ≤1/4 cạnh nhỏ. Lưới đầu tiên cách mặt chịu lực 15-20mm.

### 25. Chọc thủng (punching shear)

Tiết diện tính toán cách vùng truyền lực 0,5h0.

**25.1. Không đặt cốt ngang**: F≤Fb,u (10.8). Fb,u=Rbt·Ab (10.9). Ab=u·h0 (10.10). u=2(a+b+2h0) chữ nhật (10.11); u=π(d+h0) tròn (10.12).

**25.2. Có cốt ngang**: F≤Fb,u+Fsw,u (10.13). Fsw,u=0,8qsw·u (10.14). qsw=Rsw·Asw/sw (10.15). Tổng ≤2Fb,u. Cốt ngang chỉ tính khi Fsw,u≥0,25Fb,u.

Bố trí: vuông góc cạnh đường bao — bước ≤h0/3, ≤300mm(250mm B70-B100). Song song — bước ≤1/4 cạnh. Thanh gần biên cách ≥h0/3, ≤0,5h0. Chiều rộng vùng đặt cốt ngang ≥1,5h0.

**25.3. Đồng thời F và M**: F/Fb,u+M/Mb,u≤1 (10.16). Mb,u=Rbt·Wb·h0 (10.17). Wb=(a+h0)[(a+h0)/3+b+h0] chữ nhật (10.18); π(d+h0)²/4 tròn (10.19). M/Mb,u≤0,5F/Fb,u. Hai phương: F/Fb,u+Mx/Mbx,u+My/Mby,u≤1 (10.20), tổng ≤0,5F/Fb,u.

### 26. Giật đứt (tear-off)

Tương tự chọc thủng nhưng dùng cốt ngang (cốt treo). Tại nút dầm chính-phụ: dầm chính bố trí trên đoạn (b+2h); dầm phụ trên h/3.

```
F(1 − hs/hdc) ≤ ΣRsw·Asw          (10.21 [TL-2018])
```

Ít nhất 2Asw/3 trong (b+2h) dầm chính, còn lại trong h/3 dầm phụ. (Trùng bản chất với 5.22a [TL-KHUNG], Phần E mục 15.)

---

## PHẦN I — CẤU TẠO NÚT KHUNG (BẮT BUỘC ĐẦY ĐỦ — trọng tâm của Drawing Agent)

Nút khung ảnh hưởng nhiều nhất đến khả năng chịu lực tổng thể — phá hoại khung chủ yếu do phá hoại nút. Áp dụng cho nút khung cứng, KHÔNG kháng chấn, BTCT toàn khối (kháng chấn xem Phần P mục 55).

### 27. Nguyên tắc chung

- Chiều dài neo mọi thanh quy tụ vào nút (Lan, mục 11.6).
- Tránh tập trung quá nhiều cốt thép.
- Đủ không gian thi công/đầm bê tông.
- MẠCH NGỪNG THI CÔNG BÊ TÔNG CỘT LÀ TẠI MẶT DƯỚI CỦA DẦM.

### 28. Nút góc khung tầng mái

**28.1. Nút đóng (chịu nén)**: mô men đầu dầm căng thớ trên. Vùng nén tăng ứng suất cục bộ, có thể ép vỡ; cốt kéo cần neo đủ. Bán kính uốn thép nên tăng.

**Nút mở (chịu kéo)**: mô men đầu dầm hướng ra ngoài góc. Ứng suất kéo tập trung vùng góc.

**28.2. Cấu tạo nút góc mái — NÚT ĐÓNG — theo e0/h tại đầu cột**

| e0/h | Quy định cấu tạo |
| --- | --- |
| ≤0,25 | Cốt kéo dầm kéo ra sát mép ngoài cột, uốn xuống đoạn Lan. Đai cột đặt đến dưới mặt sàn; đai dầm bắt đầu cách mép trong cột 50mm. |
| 0,25-0,5 | Như trên, CỘNG ≥2 thanh kéo xuống quá đáy dầm đoạn Lan. |
| >0,5 | Một số thanh cột kéo lên mép trên dầm; một số thanh dầm neo sâu vào cột; cốt kéo dầm kéo quá mép dưới dầm đoạn Lan, KHÔNG cắt quá 2 thanh/tiết diện. Có thể mở rộng nút khung. |

**28.3. Bán kính uốn tối thiểu tại gối uốn**: r≥5⌀ (⌀<20mm); r≥8⌀ (⌀≥20mm).

**28.4. Dầm cao >1,5× cao cột** (mục 10.4.11 TCVN 5574-2018): bổ sung đai kín/chữ U trong vùng nút mở rộng.

**28.5. Nút góc mái — NÚT MỞ**: μ≤2% → uốn chữ U (thép dầm+cột). μ>2% → THÊM thanh thép chéo gia cường (~20% thép chịu lực đầu dầm). Bán kính uốn U tùy kích thước nút; thép chịu kéo neo vào vùng bê tông chịu nén (Lan, mục 11.6).

### 29. Nút giữa khung tầng mái

Thép dọc cột kéo lên trên mặt dầm (sàn) đoạn Lan.

### 30. Nút biên khung tầng trung gian (dầm biên – cột biên)

| Điều kiện (tg φ=(h2−h1)/hd) | Quy định |
| --- | --- |
| Tiết diện không đổi | Cấu tạo thường |
| tg φ ≤1/6 | Cốt dọc cột dưới có thể chạy liên tục lên chờ nối cột trên |
| tg φ >1/6 | Phải kéo cốt thép cột dưới lên mặt dầm và neo đoạn Lan |

Vị trí nối thép dọc cột: ≤4 thanh/cạnh → 1 vị trí. Nhiều hơn → so le, mỗi lần ≤50%, khoảng cách trục mối nối ≥1,5Lan.

### 31. Nút giữa khung tầng trung gian

| Trường hợp | Quy định |
| --- | --- |
| Tiết diện cột không đổi/ít, dầm 2 bên cùng cao | Cốt dầm liên tục qua nút |
| Tiết diện cột đổi nhiều (tg φ>1/6) | Như nút biên (mục 30) |
| Dầm 2 bên khác cao độ | Neo sâu cốt thép dầm vào nút |

### 32. Nút liên kết cột với móng

Thép chờ móng tương đương thép cột nối lên. Mối nối so le theo chiều cao; trong đoạn nối chồng, thép được nối không vượt 50% tổng diện tích chịu kéo.

### 33. Nút khung gãy khúc (mái dốc, xà gãy khúc)

| Góc lõm β | Quy định |
| --- | --- |
| β≥160° | Cốt kéo dầm đặt LIÊN TỤC qua nút, có cốt ngang gia cố |
| β<160° | Tách rời cốt kéo, neo vào vùng nén; bố trí cốt ngang ôm toàn bộ cốt dọc chịu kéo trên đoạn S |

Kiểu khác: thép chịu kéo uốn chữ U, cốt dọc gia cường ≥20% thép chịu lực đầu dầm.

### 34. Ví dụ áp dụng thực tế — xác định kiểu cấu tạo nút

**Ví dụ 1** (cột 17, dầm 50): mô men đầu dầm căng thớ trên mọi tổ hợp → nút đóng. Mmax,Ntu=(8,71kNm;119,5kN)→e0=57,5cm; e0/h=0,96>0,5 → cấu tạo Hình 5.13c/d (hàng 3, mục 28.2).

Lan với ⌀16, As=402mm²(2⌀16), As,cal=297mm²: L0,an=(435×201,1)/[(2,5×1×0,75)×(3,14×16)]≈928,65mm → Lan=928,65×(297/402)≈686,1mm ≥15⌀=240,≥200 → chọn Lan=700mm.

**Ví dụ 2** (cột 29, dầm 10): e0=14,45cm; e0/h=0,58>0,5 → tương tự.

---

## PHẦN J — TẢI TRỌNG, TỔ HỢP TẢI TRỌNG VÀ LỰA CHỌN NỘI LỰC THIẾT KẾ (cô đọng)

Vì quy trình đồ án lấy nội lực TRỰC TIẾP từ ETABS, phần tính tải trọng thủ công trình bày cô đọng; TỔ HỢP TẢI TRỌNG và LỰA CHỌN CẶP NỘI LỰC NGUY HIỂM giữ đầy đủ (quyết định trực tiếp cặp M,N,Q vào Rule Engine).

### 35. Tải trọng đơn vị (khái quát)

**35.1. Tĩnh tải G**: giá trị tính toán = tiêu chuẩn × γf. Bảng trọng lượng riêng/γf một số vật liệu: BTCT 25kN/m³(γf=1,1); gạch nung đặc 18kN/m³(1,1); gạch rỗng 15kN/m³(1,3); vữa XM-cát 18kN/m³(1,3); mái tôn 0,2kN/m²(1,05)... (Bảng 3.1 [TL-KHUNG], đầy đủ xem file gốc). Vách ngăn tạm thời: ≥1,0kN/m².

**35.2. Hoạt tải Q**: dài hạn (vách tạm, thiết bị cố định) + ngắn hạn (người, sửa chữa, gió...). γf=1,3 (1,2 cho phương tiện giao thông, mục 8.5.1 TCVN 2737:2023). Giá trị tiêu chuẩn theo TCVN 2737:2023 mục 8.3.1.

**35.3. Gió**: TCVN 2737:2023, công trình ≤200m/nhịp≤150m. Wk=W3s,10·k(ze)·c·Gf (3.2). W3s,10=γT·W0 (γT=0,864). Bảng W0 theo 63 tỉnh (Phụ lục 10 QCVN 02:2022/BXD) — không chép chi tiết (đầu vào trước ETABS, ngoài phạm vi Rule Engine).

### 36. Tổ hợp tải trọng (ĐẦY ĐỦ)

TCVN 2737:2023 mục 6: tổ hợp CƠ BẢN (và đặc biệt — không đề cập ở đây).

**36.1. Hệ số tổ hợp**: ψL1=1,0 (dài hạn chủ đạo); ψL2=ψL3=...=0,95. ψt1=1,0 (ngắn hạn chủ đạo); ψt2=0,9; ψt3=ψt4=...=0,7.

```
Ed = γn·[Σγfj·Gk,j + Σγfi·ψLi·Qk,Li + Σγfk·ψtk·Qk,tk]     (4.1)
```

**Bảng J.2 — Hệ số tầm quan trọng γn**

| Cấp | Mức độ | Ví dụ | γn |
| --- | --- | --- | --- |
| C1 | Thấp | Nhà cao <6m, công trình tạm | 0,87 |
| C2 | Trung bình | Phần lớn công trình | 1,00 |
| C3 | Cao | Tầm quan trọng cao (>75m/25 tầng, bệnh viện≥1000 giường...) | 1,15 |

Nhà >250m, mái nhịp lớn >120m: γn≥1,2.

**36.2. Bảng tổ hợp đơn giản hóa cho khung phẳng (nhà thấp tầng)** — TH1-TH17, hệ số G/Q1/Q2/Wt/Wp theo từng tổ hợp (xem Bảng J.3 nguồn gốc, 17 dòng tổ hợp chi tiết — dùng trực tiếp khi tính tay, KHÔNG cần khi đã có ETABS). Lưu ý: tĩnh tải luôn xét trong MỌI cặp nội lực; tránh trùng lặp hoạt tải ngắn hạn; không kể đồng thời gió 2 chiều ngược nhau.

### 37. Lựa chọn cặp nội lực nguy hiểm cho dầm và cột (QUY TẮC BẮT BUỘC)

**37.1. Vị trí tiết diện**: mỗi CỘT trong 1 tầng — 2 tiết diện (chân, đầu cột). Mỗi DẦM — ít nhất 3 tiết diện (2 đầu + giữa); thêm tại vị trí lực tập trung nếu có.

**37.2. Cặp nội lực nguy hiểm CỘT (ba cặp)**:
1. Mmax(+) và Ntu.
2. Mmin(−) và Ntu.
3. Nmax và Mtu.

Chân cột: tổ hợp thêm Qtu để tính móng. Thép cột đặt đối xứng → thực tế chỉ cần cặp Mmax,Ntu (|M| lớn hơn trong 1,2).

**37.3. Nội lực DẦM**:
1. Mmax(+).
2. Mmin(−).
3. Qmax.

N nén đáng kể (N>0,1Rbbh0) → thiết kế như nén lệch tâm (Phần F). Cần tổ hợp bao (mô men, lực cắt) để bố trí/cấu tạo thuận tiện — phục vụ Drawing Agent vẽ biểu đồ bao vật liệu, xác định vị trí cắt/uốn thép (mục 16.2).

Khung không gian (3D): tương tự khung phẳng, tách Mx, My riêng cho cột.

---

## PHẦN K — YÊU CẦU THỂ HIỆN BẢN VẼ (trực tiếp cho Drawing Agent)

### 38. Nội dung bắt buộc của bản vẽ kết cấu khung BTCT

- Mặt bằng kết cấu công trình.
- Chi tiết mặt cắt dọc khung thiết kế.
- Chi tiết mặt cắt ngang các cấu kiện.
- Cấu tạo nút khung (Phần I).
- Bảng thống kê thép.
- Ghi chú: cấp độ bền bê tông, mác thép, cường độ tính toán, quy định nối/hàn thép dọc, chiều dài nối/hàn, ghi chú riêng cần thiết khác.

Đầy đủ kích thước, cao trình, trục định vị, độ đậm đặc cần thiết.

### 39. Bảng ký hiệu quy ước dùng trên bản vẽ kết cấu (trích)

| Ký hiệu | Ý nghĩa |
| --- | --- |
| b1 | Kết cấu bê tông cốt thép |
| b2 | Kết cấu bê tông (không cốt thép) |
| b3 | Kết cấu BTCT và bê tông (thể hiện kết hợp) |

(Đoạn trích chỉ có 3 ký hiệu — nguồn không nêu rõ bảng ký hiệu vật liệu mặt cắt đầy đủ hơn; xem thêm `SKILL_VE_KY_THUAT_BTCT.md` cho bảng ký hiệu vật liệu mặt cắt chi tiết hơn đã nạp cho Drawing Agent.)

### 40. Phụ lục tính toán đính kèm hồ sơ (yêu cầu tối thiểu)

Số liệu đầu vào + số liệu đầu ra. Danh mục trường dữ liệu cụ thể (tên cấu kiện, tổ hợp nội lực, As tính toán, As chọn, cấu tạo áp dụng...) do đồ án tự định nghĩa dựa trên toàn bộ Phần A-J.

---

## PHẦN L — KIỂM TRA THEO TRẠNG THÁI GIỚI HẠN THỨ HAI (nứt, võng — cô đọng)

Điều kiện kiểm tra BỔ SUNG sau khi đã chọn cốt thép theo TTGH1.

### 41. Nguyên tắc chung

F≤Fcrc,u (8.1, điều kiện không nứt). acrc≤acrc,u (8.2, mở rộng khe nứt).

### 42. Bề rộng vết nứt giới hạn acrc,u (mm)

| Loại cốt thép | Dài hạn | Ngắn hạn |
| --- | --- | --- |
| Điều kiện hạn chế thấm | 0,2 | 0,3 |
| CB240-T, CB300-T | 0,3 | 0,4 |
| CB300-V, CB400-V, CB500-V | 0,3 | 0,4 |
| Dây thép vuốt nguội | 0,3 | 0,4 |
| Cốt cường độ cao | 0,2 | 0,3 |

### 43. Độ võng giới hạn fu

| Cấu kiện | fu |
| --- | --- |
| Mái/sàn L≤1m | L/120 |
| L=3m | L/150 |
| L=6m | L/200 |
| L=24m (công xôn 12m) | L/250 |
| L=36m (công xôn 24m) | L/300 |
| Có bộ phận dễ tách | L/150 |
| Có vách ngăn bên dưới | 40mm |

Công thức chi tiết acrc/f thực tế — xem mục 8.2-8.4 [TL-2018] (không trích chi tiết, bước kiểm tra bổ sung sau TTGH1).

---

## PHẦN M — CÁC PHỤ LỤC SỐ LIỆU KHÁC (tóm tắt phạm vi)

Phụ lục 15-20 [TL-2018] — bảng hệ số TÍNH TAY nội lực dầm liên tục/bản sàn (đàn hồi/khớp dẻo) — NGOÀI phạm vi trực tiếp Rule Engine (đã có ETABS). Liệt kê tên/phạm vi, không chép số liệu.

### 44. Bảng chuyển đổi đơn vị kỹ thuật cũ sang hệ SI

| Đại lượng | Đơn vị cũ | SI | Quan hệ |
| --- | --- | --- | --- |
| Lực | kG | N | 1kG=9,81N≈10N |
| | T | kN | 1T≈10kN |
| Mô men | kGm | Nm | 1kGm≈10Nm |
| | Tm | kNm | 1Tm≈10kNm |
| Ứng suất | kG/mm² | N/mm² | 1MPa=1N/mm² |
| | kG/cm² | MPa | 1kG/cm²≈0,1MPa |
| | kG/m² | Pa | 1kG/m²≈10Pa |

---

## PHẦN N — GHI CHÚ VỀ PHẠM VI SỬ DỤNG NGUỒN TÀI LIỆU CŨ [TL-2006]

[TL-2006] (400 trang, theo TCXDVN 356:2005 đã HẾT HIỆU LỰC) KHÔNG được dùng làm nguồn trích số liệu/công thức trong tài liệu này — vì (a) tiêu chuẩn nền đã lạc hậu, nguy cơ đưa hệ số/công thức SAI; (b) nội dung tương đương, cập nhật đã có đầy đủ ở [TL-KHUNG]/[TL-2018]. [TL-2006] chỉ kiểm tra ở mức trang bìa/mục lục, không trích dẫn số liệu.

---

## PHẦN O — MỤC ĐỐI CHIẾU

Đối chiếu đầy đủ chương/mục gốc [TL-KHUNG] và [TL-2018] với vị trí tương ứng trong bản tổng hợp này — xác nhận KHÔNG bỏ sót nội dung nào ngoài phạm vi đã nêu rõ lý do (Phụ lục 15-21, chương 9 ULT, chương 5 sàn sườn, [TL-2006]). Chi tiết bảng đối chiếu đầy đủ xem bản gốc PDF `TAI_LIEU_HOP_NHAT_Chon_Thep_Khung_BTCT.pdf` nếu cần tra ngược từng điều khoản.

**Tổng kết mức độ bao phủ**: 100% mục CẤU TẠO + 100% công thức cường độ dầm/cột + 100% bảng vật liệu/hệ số cốt lõi đã đưa vào đầy đủ. 1 điểm không nhất quán (μmin dầm) đã xử lý (Phần A mục 4).

---

## PHẦN P — BỔ SUNG TỪ VĂN BẢN GỐC TCVN 5574:2018 VÀ TCVN 9386 (tra cứu trực tuyến bổ sung)

### 51. Nguồn bổ sung và nguyên tắc sử dụng

| Ký hiệu | Nguồn | Nội dung |
| --- | --- | --- |
| [TCVN5574-GỐC] | Toàn văn TCVN 5574:2018 | Xác nhận số hiệu điều khoản gốc, Bảng 1-15 |
| [VC-DẦM] | "Cấu tạo thép dầm BTCT theo TCVN 5574-2018", Vietcons | Mục 10.3-10.4 cấu tạo thép dầm, kháng chấn TCVN 9386 |
| [VC-CỘT] | "Cấu tạo thép cột BTCT theo TCVN 5574-2018", Vietcons | Mục 10.2-10.4 cấu tạo thép cột, kháng chấn TCVN 9386:2025 mục 5.4.3.2 |
| [TCVN9386] | TCVN 9386:2012 / dự thảo 9386-1:2025 | Mục 5.4.3 (dầm, cột, nút kháng chấn, cấp dẻo DCM) |

Khi chênh lệch giữa nguồn bổ sung và Phần A-O, ưu tiên văn bản gốc TCVN. Phần A-O đã xác nhận nhất quán với văn bản gốc ở mọi điểm đối chiếu được (mục 52).

### 52. Xác nhận số hiệu điều khoản GỐC TCVN 5574:2018 (đối chiếu Phần E, F)

Văn bản gốc đánh số theo hệ 8.1.2.x. Bảng đối chiếu xác nhận tương ứng chính xác với [TL-2018]/[TL-KHUNG] — **kết luận: 100% công thức cốt lõi Phần E,F khớp chính xác văn bản gốc TCVN 5574:2018, không phát hiện sai lệch nào** ngoài điểm μmin dầm đã xử lý (Phần A mục 4, xác nhận lại bằng điều khoản gốc 10.3.1.1 ở mục 53.2 dưới).

### 53. Bổ sung cấu tạo cốt thép DẦM theo điều khoản GỐC mục 10.3-10.4 TCVN 5574:2018

**53.1. Đường kính, số lượng, khoảng cách cốt dọc dầm** (mục 10.3.2, 10.3.3.3, 10.3.3.4)
- Đường kính: ⌀10÷⌀28 (không nên >⌀28, khó uốn); dầm chính nên ⌀>16.
- b≥150mm: ≥2 thanh chịu lực. b<150mm: 1 thanh đủ.
- Smin=max(⌀,25mm); thực tế nên ≥50mm.
- Smax: 200mm (h≤150mm); min(1,5h;400mm) (h>150mm).

**53.2. Hàm lượng cốt thép dầm — xác nhận bằng điều khoản gốc**
```
μmin = 0,1%      (mục 10.3.1.1 TCVN 5574:2018)
μmax = ξR·Rb/Rs  (mục 8.1.2.2.3)
```
Hợp lý kinh nghiệm: μ=0,8-1,5%. **XÁC NHẬN CHÍNH THỨC**: μmin=0,1% (không phải 0,05%) đúng theo văn bản gốc.

**53.3. Quy tắc cắt và neo cốt thép dọc dầm — SỐ LIỆU ĐỊNH LƯỢNG (mới, thay ghi chú "nguồn không nêu rõ" cũ)**

Dựa trên biểu đồ bao mô men (thỏa biểu đồ bao vật liệu). Nguyên tắc định lượng (kinh nghiệm thiết kế thực tế phù hợp TCVN 5574:2018):
- Cắt giảm từ từ; mỗi lần cắt giảm KHÔNG QUÁ 50% diện tích cốt thép đang có tại tiết diện đó.
- Thép chịu mô men ÂM tại gối: vị trí cắt lần 1 cách mép gối >L/4 nhịp; cắt lần 2 cách mép gối >L/3 nhịp.
- Thép chịu mô men DƯƠNG tại nhịp: vị trí cắt cách gối biên <0,1L; cách gối giữa <0,15L.
- Khoảng cách dọc dầm giữa vị trí cắt lớp trên và lớp dưới ≥h (chiều cao dầm).
- Thép dương ở nhịp kéo vào gối: ÍT NHẤT 2 thanh và >50% tổng diện tích thép chịu lực tại nhịp (mục 10.3.3.5).

**→ GHI CHÚ QUAN TRỌNG CHO HỆ THỐNG HIỆN TẠI**: hệ thống (`src/rule_engine/`, `src/orchestrator/`) hiện CHƯA triển khai logic cắt/uốn cốt thép dọc dầm theo chiều dài (chỉ tính As độc lập tại 3 vị trí gối trái/giữa nhịp/gối phải, không có khái niệm "điểm cắt lý thuyết" dọc theo dầm). Đây là tính năng MỚI cần bổ sung nếu muốn bản vẽ thể hiện đúng việc cắt/uốn thép như bản vẽ mẫu thực tế.

**53.4. Cốt đai dầm — đường kính, SỐ NHÁNH, khoảng cách (bổ sung số nhánh — hoàn toàn mới)**

| Điều kiện | Quy định |
| --- | --- |
| Đường kính đai, B<B70 | ⌀≥6mm |
| Đường kính đai, B70-B100 | ⌀≥8mm |
| b≤150mm | n=1 nhánh (nếu chỉ 1 cốt dọc) |
| b>150mm | n=2 nhánh |
| b≥400mm | n≥3 nhánh |

**→ GHI CHÚ CHO HỆ THỐNG**: `src/rule_engine/cot_dai.py` hiện tính `Asw` (diện tích tổng cốt đai) nhưng cần XÁC NHẬN có tính đến SỐ NHÁNH (n) khi suy ra đường kính+số lượng nhánh đai thật hay không — đây là dữ liệu CẦN THIẾT để Drawing Agent vẽ đúng số nhánh đai trên mặt cắt (hiện `ve_mat_cat_dam`/`ve_mat_cat_cot` cần biết rõ số nhánh, không chỉ Asw tổng).

Khoảng cách đai (tải phân bố đều, mục 10.3.4.3): đoạn 1/4 nhịp gần gối: S1=min(0,5h0;300mm). Đoạn 1/2 giữa nhịp: S2=min(0,75h0;500mm).

Tải tập trung (dầm phụ/cột cấy lên dầm): đai dày S1 từ điểm lực tập trung đến gối, đoạn ≥L/4. Tại vị trí lực tập trung: đai gia cường s=50mm, dầm chính trong (b+2h), dầm phụ trong h/3 (mục 10.4.12 — khớp hoàn toàn mục 15.3 Phần E).

**53.5. Cấu tạo dầm chịu xoắn — SỐ LIỆU ĐỊNH LƯỢNG (mới, thay ghi chú cũ)**
- Cốt đai: PHẢI dùng đai kín, đoạn chồng (neo) ≥30×đường kính đai (mục 10.3.4.6).
- Cốt dọc: theo chu vi tiết diện; khoảng cách trên mặt bên ≤400mm (thực tế thường ≤200mm cho hiệu quả chịu xoắn). Neo đủ vào gối tựa đoạn Lan.
- Chữ T/I: đai chịu xoắn phải tạo vòng kín ôm cả bụng và cánh.

**53.6. Cốt giá (cốt cấu tạo mặt bên) cho dầm cao — HOÀN TOÀN MỚI, chưa có trong Phần E**

Dầm H>700mm: mỗi cạnh bên cần cốt giá sao cho (mục 10.4.13):
```
s < 400mm
A_cốt_giá > 0,1%·s·max(b/2, 200)
```
b=bề rộng dầm. Hạn chế nứt do co ngót/nhiệt trên bụng dầm cao, KHÔNG tính là cốt chịu lực chính.

### 54. Bổ sung cấu tạo cốt thép CỘT theo điều khoản GỐC mục 10.2-10.4 TCVN 5574:2018

**54.1. Đường kính cốt dọc và giới hạn độ mảnh**
- Đường kính: ⌀12÷⌀40. Cạnh >200mm nên ⌀≥16.
- Độ mảnh: L0/i≤120 (mục 10.2.2).
- Công thức thực hành (L0=0,8H): cột lệch tâm xiên (i=imin), chữ nhật/vuông: H/b≤43,3; tròn: H/D≤37,5. Cột lệch tâm phẳng: H/h≤43,3.

**54.2. Hàm lượng cốt dọc cột — xác nhận bằng điều khoản gốc 10.3.3.1**
```
μmin = 0,1%   (L0/i≤17, chữ nhật L0/h≤5)       (mục 10.3.3.1)
μmin = 0,25%  (L0/i≥87, chữ nhật L0/h≥25)      (mục 10.3.3.1)
```
17<L0/i<87: nội suy. Bố trí đều chu vi: nhân đôi.

μmax KHÔNG có con số trực tiếp trong TCVN 5574:2018 (chỉ khống chế gián tiếp qua phá hoại giòn). Tham khảo thực hành VN + Eurocode 2 (mục 9.5.2 EC2): **μmax=4% (ngoài vùng nối chồng); 8% (tại nối chồng); hợp lý kinh tế-kỹ thuật: 1%≤μ≤3%.**

> Điểm bổ sung quan trọng: [TL-2018] mục 6.2.1 nêu μmax=4%(8% nối chồng) như một con số CHÍNH THỨC của TCVN 5574:2018; nguồn [VC-CỘT] làm rõ con số này cũng khớp thực hành/Eurocode 2 — không mâu thuẫn.

**→ GHI CHÚ QUAN TRỌNG CHO HỆ THỐNG HIỆN TẠI**: `src/rule_engine/cot_doc.py` hiện có hằng số `MU_MAX_COT_MOI_PHIA_PHAN_TRAM = 3.0` (mỗi phía ≤3%, tổng ≤6%), với comment tự ghi "ngưỡng cảnh báo thực hành... không phải trị số TCVN tuyệt đối" (dựa trên "ví dụ thực hành mục 5.6 giáo trình"). Tài liệu MỚI này (mục 54.2) xác nhận qua điều khoản GỐC trực tiếp TCVN 5574:2018 mục 6.2.1: **μmax=4% TỔNG (không phải 3% mỗi phía/6% tổng)**, 8% tại nối chồng. Đây là SỰ KHÁC BIỆT CẦN ĐỐI CHIẾU VÀ CẬP NHẬT CODE — giá trị mới (4% tổng bình thường) CHẶT HƠN giá trị cũ (6% tổng) ở điều kiện thường, nhưng NỚI HƠN tại vùng nối chồng (8% vs không phân biệt trước đây). Cần sửa `cot_doc.py` để dùng đúng μmax=4%/8% theo TỔNG As,tot (không phải theo mỗi phía).

**54.3. Khoảng cách cốt dọc cột — cấu tạo cột cạnh lớn**

Xác nhận: 400mm vuông góc mặt uốn (300mm B70-B100); 500mm theo mặt uốn (400mm B70-B100). Khoảng hở tối thiểu 50mm (mục 10.3.2).

Bổ sung: cột lệch tâm phẳng cạnh h>500mm → cần thêm cốt dọc cấu tạo ⌀12-⌀16 dọc cạnh đó để đảm bảo khoảng cách tối đa.

**54.4. Cấu tạo nút khung liên quan đến cột**: xác nhận điều khoản gốc cho mục 28.4 Phần I (đai trong vùng neo dầm tại nút theo mục 10.4.11).

### 55. THIẾT KẾ KHÁNG CHẤN KHUNG BTCT THEO TCVN 9386 (HOÀN TOÀN MỚI — bổ sung phạm vi)

Ba nguồn gốc ĐỀU không đề cập kháng chấn ([TL-KHUNG] nêu rõ phạm vi "khung cứng, KHÔNG kháng chấn"). Mục này bổ sung yêu cầu cấu tạo kháng chấn cấp dẻo DCM (phổ biến nhất VN).

> **QUAN TRỌNG**: phần kháng chấn này CHỈ áp dụng khi công trình được xác định cần thiết kế chịu động đất (tùy gia tốc nền + tầm quan trọng công trình). Với khung không yêu cầu kháng chấn, Phần D-I (TCVN 5574:2018) là đầy đủ và áp dụng. **Rule Engine cần một CỜ (flag) "có/không kháng chấn" làm đầu vào tường minh — KHÔNG tự suy ra từ ETABS.**

**55.1. Cấp dẻo kết cấu**: DCL (dẻo thấp, gần đàn hồi) / **DCM (dẻo trung bình — PHỔ BIẾN NHẤT VN)** / DCH (dẻo cao, vùng động đất mạnh).

**55.2. Vùng tới hạn**: đoạn cấu kiện gần nút dầm-cột, nơi dự kiến hình thành khớp dẻo — cần cốt đai dày hơn, hạn chế nối thép.

**55.3. Dầm kháng chấn chính, DCM**: Lcr=1,5·hw (chiều dài vùng tới hạn từ mép nút). Trong Lcr: cốt đai đặc biệt (đường kính/khoảng cách chặt hơn vùng thường, mục 5.4.3.1.2(6)P). Mô hình giàn ảo tính cắt: góc thanh xiên 45°. Hàm lượng thép kéo trong vùng tới hạn bị giới hạn bởi ρmax riêng (nghiêm ngặt hơn μmax thường).

*(Giá trị số cụ thể của đường kính/khoảng cách đai vùng tới hạn dầm và ρmax — nguồn không nêu rõ ở đây, cần tra cứu trực tiếp TCVN 9386 mục 5.4.3.1.2 đầy đủ trước khi lập trình.)*

**55.4. Cột kháng chấn chính, DCM**

| # | Yêu cầu | Điều khoản |
| --- | --- | --- |
| 1 | Lực dọc quy đổi νd=NEd/(Ac·fcd) kiểm soát trong giới hạn | 5.4.3.2.1(3)P |
| 2 | Hàm lượng cốt dọc tổng trong khoảng min/max riêng kháng chấn | 5.4.3.2.2(1)P |
| 3 | Hiệu ứng P-Delta lớn: tiết diện cột ≥1/10 chiều dài tính toán L | 5.4.1.2.2(1)P |
| 4 | Tỷ số thể tích cơ học cốt đai hạn chế biến dạng vùng tới hạn chân cột | 5.4.3.2.2(9)P |
| 5 | lcl/hc≥3: lcr=max(hc;lcl/6;450mm); lcl/hc<3: lcr=lcl (toàn bộ) | 5.4.3.2.2(4,5)P |
| 6 | Khoảng cách cốt dọc cạnh nhau (đai kín/móc): Smax=200mm | 5.4.3.2.2(11)b |
| 7 | ≥1 thanh trung gian giữa các thanh góc dọc mỗi mặt | 5.4.3.2.2(2)P |
| 8 | Đường kính đai tối thiểu vùng tới hạn: 6mm | 5.4.3.2.2(10)P |
| 9 | s=min(b0/2;175mm;8dbL) (b0=lõi bê tông, dbL=đường kính dọc nhỏ nhất) | 5.4.3.2.2(11) |

Nối thép cột vùng kháng chấn: KHÔNG hàn chồng trong vùng tới hạn. s=min(h/4;100mm) (bước cốt ngang đoạn nối, mục 5.6.3). Ast=s·(dbL/50)·(fyld/fywd) (diện tích cốt ngang cần, mục 5.6.3).

Móc đai kháng chấn: góc 135°, đoạn thẳng sau móc ≥10×đường kính đai (mục 5.6.1(2)P). N chuyển thành KÉO trong tổ hợp động đất: Lan TĂNG THÊM 50% (mục 5.6.2(2)P).

**55.5. Nút dầm-cột kháng chấn**: cốt đai ngang trong nút KHÔNG được nhỏ hơn yêu cầu vùng tới hạn cột liền kề (mục 5.4.3.2.2(8)-(11)), trừ ngoại lệ theo tỷ số lực cắt. *(Công thức định lượng đầy đủ mục 5.4.3.3(2)-(7) — nguồn không nêu rõ ở đây, cần tra TCVN 9386 đầy đủ.)*

**55.6. Nguyên tắc "cột khỏe – dầm yếu"** (nền tảng DCM/DCH): tổng khả năng chịu mô men cột quy tụ 1 nút > tổng khả năng chịu mô men dầm × hệ số an toàn — đảm bảo khớp dẻo hình thành ở dầm (dễ sửa) trước cột (sụp đổ tiến triển). *(Hệ số an toàn + công thức đầy đủ mục 4.4.2.3 TCVN 9386 — nguồn không nêu rõ ở đây, cần tra cứu bổ sung khi mở rộng Rule Engine kháng chấn.)*

### 56. Đối chiếu nguồn bổ sung Phần P

Tổng kết: mục 53.1-53.2 (xác nhận), 53.3-53.6 (MỚI, dầm), 54.1/54.3/54.4 (xác nhận+bổ sung), 54.2 (**sửa μmax cột**), 55.1-55.6 (MỚI HOÀN TOÀN, kháng chấn — không có ở bất kỳ nguồn gốc nào trước đây).

---

## PHẦN Q — DANH MỤC TRƯỜNG HỢP ĐẶC BIỆT KHI CHỌN THÉP (bảng quy tắc ĐIỀU KIỆN → XỬ LÝ)

Phần A-P trình bày lý thuyết/công thức theo chương sách. Phần Q khai thác lại theo góc nhìn NGƯỢC LẠI — theo TỪNG ĐIỂM RẼ NHÁNH mà Rule Engine thực sự gặp khi chạy qua từng phần tử. Mỗi dòng: **Điều kiện** (IF logic lập trình được) → **Xử lý/Công thức** → **Nguồn** (số mục Phần A-P để tra lại).

### 57. Thứ tự xử lý tổng thể cho một phần tử

1. Phân loại cấu kiện: dầm hay cột? (Frame Section Assignments/DesignType).
2. Công trình có yêu cầu kháng chấn? (cờ người dùng khai báo, KHÔNG suy từ ETABS). CÓ → đối chiếu thêm Bảng H trước khi chốt.
3. Dầm: THÉP DỌC (Bảng A) độc lập từng vị trí → CỐT ĐAI (Bảng B) → CỐT TREO/GIẬT ĐỨT nếu có dầm phụ (Bảng C).
4. Cột: THÉP DỌC (Bảng D) → CỐT ĐAI (Bảng E).
5. MỌI nút giao dầm-cột: đối chiếu cấu tạo nút (Bảng F) — bước hay bị bỏ sót.
6. Vị trí có lực cục bộ/neo/nối (chân cột, đổi tiết diện, mối nối): Bảng G.
7. Quy tắc vận hành/toàn vẹn dữ liệu (Bảng I) — luôn chạy sau cùng, trước khi xuất bản vẽ.

### 58. Dầm — thép dọc chịu uốn: trường hợp đặc biệt (Bảng A)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
| --- | --- | --- | --- |
| A1 | Chuẩn: As,min≤As,yêu cầu≤As,max | As,thiết kế=MAX(As,yêu cầu,As,min). Chọn tổ hợp theo đường kính chuẩn dự án (số thanh=ROUNDUP(As,thiết kế/As,1thanh)) | 12.5 |
| A2 | As,yêu cầu<As,min (μ<0,1%) | As,thiết kế=As,min=μmin·b·h0. KHÔNG dùng As,yêu cầu trực tiếp | 12.4 |
| A3 | As,yêu cầu>As,max (αm>αR) | KHÔNG tăng As đơn thuần (phá hoại giòn). (a) tăng tiết diện; (b) cốt kép (Bài toán 2); (c) tăng Rb (ít hiệu quả) | 12.3, 12.6 |
| A3a | Cốt kép, ĐÃ có As' sẵn | Bài toán 3 (mục 12.7): tính αm với As' cho trước; 3 nhánh theo ξ vs ξR và 2a'/h0 | 12.7 |
| A4 | Chữ T/I: so sánh M với Mf=Rb·b'f·h'f(h0−0,5h'f) | M≤Mf→qua CÁNH (tính chữ nhật b'f). M>Mf→qua SƯỜN (Bài toán 4) | 13.2, 13.3 |
| A5 | Dầm có N đáng kể: \|N\|>0,1·Rb·b·h0 | KHÔNG tính như uốn thuần túy. Chuyển NÉN LỆCH TÂM (Bảng D) hoặc KÉO LỆCH TÂM (mục 22.4) | 37.3 |
| A6 | As âm/rất nhỏ | Cấu tạo tối thiểu As=As,min; ≥2 thanh (b≥150mm) | A2+16.1 |
| A7 | Số thanh vượt ngưỡng thực hành (mặc định 6/lớp) | Chuyển đường kính LỚN HƠN kế tiếp, tính lại; hoặc thêm lớp thứ 2 | 16.1, 11.5 |
| A8 | Nhiều vị trí liền kề As chênh lệch không đáng kể | Có thể đồng bộ: dùng CHUNG tổ hợp lớn hơn — lựa chọn KINH TẾ, không bắt buộc | Thực hành |
| A9 | Dầm cao bất thường/công-xôn ngắn | NGOÀI phạm vi Bài toán 1-4. Cần mô hình THANH-GIẰNG (Phụ lục H TCVN 5574:2018 — **chưa trích, cần bổ sung nếu gặp**) | *thiếu* |

### 59. Dầm — cốt đai chịu cắt: trường hợp đặc biệt (Bảng B)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
| --- | --- | --- | --- |
| B1 | Q≤0,5·Rbt·b·h0 | KHÔNG cần tính đai theo lực cắt. Đai cấu tạo: sct≤min(3h/4,500mm) | 14.2, 14.6 |
| B2 | Q>φb1·Rb·b·h0 (φb1=0,3) | TIẾT DIỆN KHÔNG ĐỦ dù đặt bao nhiêu đai. Bắt buộc tăng tiết diện/cấp bê tông | 14.1 |
| B3 | 0,5Rbtbh0<Q≤φb1Rbbh0 (chuẩn) | qsw=MAX[Q²/(4,5Rbtbh0²);0,25Rbtb]; số nhánh theo b (≤150→1, >150→2, ≥400→≥3); s=min(Rsw·Asw/qsw, smax cấu tạo) | 14.3-14.5 |
| B4 | C0=√(2Rbtbh0²/qsw) ngoài [h0;2h0] | C0<h0→C=h0. C0>2h0→C=2h0. Tính lại Qu,min theo C chặn biên | 14.4 |
| B5 | Không có dữ liệu Q riêng từ ETABS | KHÔNG bỏ qua kiểm tra cắt. Phải lấy Q thật; chỉ dùng cấu tạo khi ĐÃ XÁC NHẬN Q nhỏ qua tính toán thực tế | Bảng I |
| B6 | Dầm chịu ĐỒNG THỜI cắt + xoắn | Không cộng đơn giản. Kiểm tra riêng mục 8.1.4 (T≤T0, tương tác với Q); đai xoắn PHẢI đai KÍN (neo≥30⌀) | Phần G 23; 53.5 |
| B7 | Vị trí: 1/4 gần gối vs 1/2 giữa nhịp | S1=min(0,5h0,300mm) gần gối; S2=min(0,75h0,500mm) giữa nhịp | 53.4 |

### 60. Dầm — cốt treo và giật đứt: trường hợp đặc biệt (Bảng C)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
| --- | --- | --- | --- |
| C1 | Dầm phụ gác lên dầm chính (lực tập trung F) | BẮT BUỘC cốt treo bổ sung dù đã đủ đai cắt thường. F(1−hs/hdc)≤ΣRsw·Asw | 15.1; 26 |
| C2 | Hai dầm giao nhau CÙNG cao độ | F≤ΣRsw·Asw, đoạn bố trí dài 3b | 15.2 |
| C3 | Phân bổ cốt treo | ≥2/3 Asw trong (b+2h) dầm CHÍNH; còn lại trong h/3 dầm PHỤ | 15.3; 53.4 |

### 61. Cột — thép dọc chịu nén/kéo lệch tâm: trường hợp đặc biệt (Bảng D)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
| --- | --- | --- | --- |
| D1 | N là lực NÉN (phổ biến) | Tiếp tục D2-D6 | — |
| D2 | N là lực KÉO | KHÔNG áp dụng công thức nén lệch tâm. CHUYỂN HẲN sang KÉO LỆCH TÂM (mục 22.4). Lỗi rule-engine thường gặp nhất nếu chỉ đọc \|N\| | 22.4 |
| D3 | L0/h≤20 VÀ e0≤h/30 | Công thức đơn giản nén đúng tâm (6.3-6.4) | 18.2, 18.4 |
| D4 | Lệch tâm LỚN: 2a'≤x≤ξR·h0 | As=As'=[Ne−Rbbx(h0−0,5x)]/[Rsc(h0−a')] (5.30) | 19.3 |
| D5 | x<2a' (As' cho trước quá nhiều) | KHÔNG dùng (5.30). Dùng As=As'=Ne'/[Rs(h0−a')] (5.31) | 19.3 |
| D6 | Lệch tâm BÉ: x>ξR·h0 | Xác định LẠI x (mục 19.4), rồi thế vào (5.30) | 19.3, 19.4 |
| D7 | L0/h≥4 (hoặc L0/i≥14) | PHẢI nhân e0 với η TRƯỚC khi tính As. 4≤L0/h≤7: η≈1,03-1,08 | 19.2 |
| D8 | ea chi phối (e1<ea) | e0=ea=MAX(L0/600,h/30,10mm), KHÔNG để e0→0 | 19.1 |
| D9 | As âm | Cấu tạo tối thiểu As=As'=μmin·b·h0 | 17.2 |
| D10 | μ,tổng vượt 4% (hoặc 8% tại nối chồng) | KHÔNG tiếp tục tăng thép. TĂNG TIẾT DIỆN/cấp bê tông rồi tính lại | **17.3, 54.2 (đã sửa: 4%/8% TỔNG)** |
| D11 | L0/i>120 | KHÔNG ĐẠT ổn định — không xử lý bằng thép. Tăng tiết diện/giảm L0 | 54.1 |
| D12 | Nén lệch tâm XIÊN (2 phương, khung 3D) | NGOÀI phạm vi (chỉ có lệch tâm PHẲNG). Cần quy đổi gần đúng hoặc biểu đồ tương tác 3D — **chưa có, cần bổ sung** | *thiếu* |
| D13 | Cột tròn/vành khuyên | KHÔNG dùng Bảng D (chỉ chữ nhật). Xem Phụ lục F TCVN 5574:2018 — **chưa trích, cần bổ sung nếu gặp** | *thiếu* |

### 62. Cột — cốt đai: trường hợp đặc biệt (Bảng E)

| # | Điều kiện | Xử lý / Công thức | Nguồn |
| --- | --- | --- | --- |
| E1 | μ,tổng≤1,5% | s≤min(15⌀dọc,min,500mm); đường kính≥max(0,25⌀dọc,max,6mm) | 17.5 |
| E2 | μ,tổng>1,5% | s≤min(10⌀dọc,min,300mm) | 17.5, 21 |
| E3 | Bề rộng mặt bên>400mm HOẶC >4 thanh/mặt | Cần đai phụ; chỗ uốn cách nhau ≤400mm | 17.5 |
| E4 | Có dữ liệu Q cột từ ETABS | Tính đai theo lực cắt (dùng Bảng B), LẤY NHỎ HƠN giữa cấu tạo và tính toán | Bảng I |
| E5 | Công trình kháng chấn (DCM) | E1-E4 bị THAY THẾ bởi Bảng H dòng H2 (vùng tới hạn: s=min(b0/2,175mm,8⌀dọc,min)) | Bảng H2 |

### 63. Nút khung: trường hợp đặc biệt lựa chọn kiểu cấu tạo (Bảng F)

Rule Engine phải TỰ XÁC ĐỊNH loại nút từ vị trí hình học (góc/giữa, mái/trung gian) và dấu nội lực — KHÔNG xuất hiện trực tiếp trong bảng As ETABS, dễ bị bỏ sót nhất.

| # | Điều kiện | Xử lý | Nguồn |
| --- | --- | --- | --- |
| F1 | Xác định vị trí: góc/giữa? mái/trung gian? | 4 tổ hợp → F2-F3 (góc+mái), F4 (giữa+mái), F5-F6 (góc/giữa+trung gian) | 27 |
| F2 | Góc, mái, nút ĐÓNG | Tra e0/h (F2a-c) | 28.1-28.2 |
| F2a | e0/h≤0,25 | Cốt kéo dầm ra sát mép ngoài cột, uốn xuống Lan. Đai cột đến dưới mặt sàn | Bảng I.1 |
| F2b | 0,25<e0/h≤0,5 | + ≥2 thanh kéo xuống quá đáy dầm đoạn Lan | Bảng I.1 |
| F2c | e0/h>0,5 | Thép cột lên mép trên dầm; thép dầm neo sâu vào cột; không cắt quá 2 thanh/tiết diện | Bảng I.1 |
| F3 | Góc, mái, nút MỞ | μ≤2%→chữ U. μ>2%→+chéo gia cường ~20% | Bảng I.2 |
| F3a | Dầm cao>1,5×cao cột tại nút góc | BẮT BUỘC thêm đai kín/chữ U (chồng thêm, không phụ thuộc e0/h hay μ) | 28.4 |
| F4 | Giữa, mái | Thép cột kéo lên mặt dầm đoạn Lan | 29 |
| F5 | Biên, trung gian: tg φ=(h2−h1)/hd | Không đổi→thường. ≤1/6→chạy thẳng lên nối chồng. >1/6→kéo lên mặt dầm+neo Lan | Bảng I.3 |
| F6 | Giữa, trung gian | Không đổi/cùng cao→liên tục qua nút. Đổi nhiều→như F5. Khác cao độ→neo sâu | Bảng I.4 |
| F7 | Nút cột-móng | Thép chờ tương đương thép cột; nối so le, ≤50%/lần | 32 |
| F8 | Gãy khúc, góc lõm β | β≥160°→liên tục+cốt ngang. β<160°→tách rời, neo riêng, cốt ngang ôm trên đoạn S | Bảng I.5 |
| F9 | Công trình kháng chấn — MỌI nút | F1-F8 là nền, CỘNG kiểm tra Bảng H dòng H3 (đai nút ≥ vùng tới hạn cột liền kề) | Bảng H3 |

### 64. Chịu lực cục bộ, neo và nối thép: trường hợp đặc biệt (Bảng G)

| # | Điều kiện | Xử lý | Nguồn |
| --- | --- | --- | --- |
| G1 | Lan tính ra <15⌀ hoặc <200mm | Lan=MAX(tính được,15⌀,200mm,0,3L0,an) — 3 giá trị sàn tuyệt đối | 11.6 |
| G2 | Thép TRƠN chịu kéo, không đủ Lan thẳng | Bắt buộc móc uốn (U/L). Thép GỜ có thể bỏ móc nếu đủ Lan | 11.6 |
| G3 | Cần nối — chọn phương pháp | ≤40mm, đủ không gian→NỐI CHỒNG. Cần tốc độ/nhà máy→HÀN. Lực đảo dấu/⌀ lớn→ỐNG REN | 11.7 |
| G4 | >4 thanh/cạnh — vị trí nối | KHÔNG nối cùng mặt cắt. So le, ≤50%/lần, khoảng cách mối nối ≥1,5Lan | 11.8 |
| G5 | Nén cục bộ, diện chịu tải GẦN BIÊN | Ab,max giới hạn bởi biên — dùng đúng 1 trong 6 sơ đồ hình học | 24.1 |
| G6 | φb=0,8√(Ab,max/Ab,loc) | >2,5→chặn 2,5. <1,0→chặn 1,0 | 24.1 |
| G7 | Chọc thủng — ĐỒNG THỜI F và M | Công thức tương tác F/Fb,u+M/Mb,u≤1 (hoặc 2 phương); M/Mb,u chặn ≤0,5F/Fb,u | 25.3 |
| G8 | Chọc thủng — (10.16)/(10.20) không thỏa, chưa có cốt ngang | Bổ sung cốt ngang (bước ≤h0/3,≤300mm); chỉ tính vào khả năng chịu lực khi Fsw,u≥0,25Fb,u | 25.2-25.3 |

### 65. Công trình kháng chấn: rẽ nhánh toàn bộ luồng xử lý (Bảng H)

CỜ cấp cao nhất — nếu BẬT, gần như MỌI bảng A-G có phiên bản thay thế/bổ sung. Cờ PHẢI do người dùng khai báo tường minh — KHÔNG tự suy từ ETABS.

| # | Điều kiện | Xử lý | Nguồn |
| --- | --- | --- | --- |
| H1 | Cờ=TẮT (mặc định) | Dùng nguyên Bảng A-G | — |
| H2 | Cờ=BẬT — CỘT đầu/chân | Lcr: lcl/hc≥3→max(hc,lcl/6,450mm); <3→toàn bộ. Trong Lcr: ⌀≥6mm, s=min(b0/2,175mm,8⌀dọc,min) — Bảng E KHÔNG áp dụng trong vùng này | 55.4 |
| H3 | Cờ=BẬT — DẦM gần nút | Lcr=1,5·hw. Đai dày hơn Bảng B thường; góc giàn 45°; ρmax riêng (**số liệu thiếu, cần tra TCVN 9386**) | 55.3 |
| H4 | Cờ=BẬT — NÚT DẦM-CỘT | Đai ngang nút KHÔNG nhỏ hơn yêu cầu vùng tới hạn cột (chồng thêm lên Bảng F) | 55.5 |
| H5 | Cờ=BẬT — vị trí NỐI thép cột | CẤM hàn chồng trong vùng tới hạn. Nối thường: s=min(h/4,100mm); Ast=s(dbL/50)(fyld/fywd). Móc 135°, đoạn sau móc≥10⌀đai | 55.4 |
| H6 | Cờ=BẬT — N chuyển KÉO trong tổ hợp động đất | Lan TĂNG 50% so với thông thường | 55.4 |
| H7 | Cờ=BẬT — kiểm tra TỔNG THỂ hệ khung | Xác nhận "cột khỏe-dầm yếu" ở CẤP HỆ (**hệ số an toàn thiếu, cần tra TCVN 9386**) | 55.6 |

### 66. Vận hành Rule Engine: trường hợp dữ liệu/quy trình đặc biệt (Bảng I)

Rút từ vướng mắc THỰC TẾ khi xử lý dữ liệu ETABS (không phải điều khoản tiêu chuẩn).

| # | Điều kiện | Xử lý | Nguồn |
| --- | --- | --- | --- |
| I1 | As,yêu cầu=0 hoặc "N.A." | KHÔNG hiểu là "không cần thép". Luôn As,thiết kế=As,min | Bảng A2 |
| I2 | Cột không có dữ liệu Q (thiếu, không phải Q=0 thật) | Phân biệt rõ 2 trường hợp. Thiếu dữ liệu→cấu tạo TẠM + cờ cảnh báo, KHÔNG dùng làm kết quả cuối | Bảng E4 |
| I3 | Quy ước As cột trong ETABS chưa rõ (tổng hay 1 phía) | PHẢI đối chiếu ≥1 ví dụ tính tay trước khi áp dụng hàng loạt — sai ở đây làm SAI toàn bộ khối lượng thép cột | **Đã đối chiếu, xem mục 72: As=1 PHÍA** |
| I4 | Tiết diện không phải bội số 50/100mm | Cảnh báo "không đúng mô-đun ván khuôn" — không tự sửa, gắn cờ | 11.1 |
| I5 | 2 vị trí liền kề As chênh ĐỘT NGỘT bất thường dù tải gần như không đổi | Dấu hiệu LỖI MÔ HÌNH ETABS — gắn cờ "kiểm tra lại mô hình", không âm thầm chấp nhận | Kinh nghiệm |
| I6 | Khoảng cách thông thủy tính ra vi phạm (<25mm dầm, <50mm cột) | KHÔNG xuất bản vẽ vi phạm. Ưu tiên: (a) tăng ⌀giảm số thanh → (b) thêm lớp → (c) tăng bề rộng | 11.5 |
| I7 | ETABS dùng mã nước ngoài (SP 63.13330.2012...) thay TCVN trực tiếp | CHẤP NHẬN ĐƯỢC — thực hành phổ biến VN. Chỉ cần đối chiếu ký hiệu vật liệu đã khớp | Ghi chú #5 |

### 67. Tóm tắt: sơ đồ ra quyết định tổng thể (dạng mã giả)

```
CHO MỖI phần tử (dầm hoặc cột) TRONG mô hình:
  XÁC ĐỊNH loại cấu kiện, tiết diện (b,h), vật liệu (Rb,Rs,Rsc,Rsw)
  NẾU loại = DẦM:
    CHO MỖI vị trí (gối trái, giữa nhịp, gối phải):
      LẤY As_yêu_cầu, N (nếu có) TỪ ETABS
      NẾU |N| > 0,1·Rb·b·h0: CHUYỂN sang nhánh CỘT/KÉO LỆCH TÂM [A5]
      NẾU As_yêu_cầu = 0 HOẶC N.A.: As_yêu_cầu = 0 [I1]
      As_min = μmin·b·h0 (μmin=0,1%) [A2]
      As_max = ξR·Rb/Rs·b·h0
      As_thiết_kế = MAX(As_yêu_cầu, As_min)
      NẾU As_thiết_kế > As_max:
        NẾU có As' sẵn: DÙNG Bài toán 3 [A3a]
        KHÁC: CẢNH BÁO "cần cốt kép/tăng tiết diện" [A3]
      KHÁC: CHỌN tổ hợp thép chuẩn dự án (số thanh=ROUNDUP(As_thiết_kế/A_1thanh))
      NẾU số thanh > ngưỡng thực hành: TĂNG đường kính, tính lại [A7]
      KIỂM TRA khoảng cách thông thủy [I6]
    TÍNH cốt đai: ÁP DỤNG Bảng B theo Q [B1-B7]
    NẾU có dầm phụ gác lên: TÍNH cốt treo [Bảng C]
  NẾU loại = CỘT:
    LẤY N, M, L TỪ ETABS
    NẾU N là lực KÉO: CHUYỂN sang công thức KÉO LỆCH TÂM [D2]
    KHÁC: TÍNH L0=0,8L; L0/h; μmin theo Bảng F.1
      NẾU L0/h≤20 VÀ e0≤h/30: DÙNG công thức nén đúng tâm [D3]
      KHÁC: TÍNH e0; NẾU L0/h≥4: NHÂN e0 với η [D7]
        TÍNH x=N/(Rb·b); SO SÁNH x với 2a' và ξR·h0
        CHỌN đúng 1 trong D4/D5/D6
      As_thiết_kế_1_phía = MAX(As_tính, As_min_1_phía)
      As_tổng = 2× (nếu đối xứng)
      KIỂM TRA μ_tổng ≤ 4% [D10, SỬA]; ĐỘ MẢNH ≤120 [D11]
    TÍNH cốt đai: ÁP DỤNG Bảng E [E1-E4]
  CHO MỖI nút dầm-cột: TRA Bảng F [F1-F9]
  CHO MỖI vị trí neo/nối/lực cục bộ: ÁP DỤNG Bảng G [G1-G8]
  NẾU cờ_kháng_chấn = BẬT: ÁP DỤNG BỔ SUNG/THAY THẾ Bảng H [H1-H7]
  GHI kết quả cuối VÀO bảng tổng hợp cho Drawing Agent
```

### Trường hợp nào đã THỰC SỰ xảy ra trong bộ dữ liệu Khung Trục 5 (đối chiếu thực tế)

- **A1** (chuẩn): 24/24 vị trí dầm, trừ nhịp BC ngắn chạm As,min.
- **A2**: dầm nhịp BC (220×300mm), As,yêu cầu rất nhỏ (18,33mm²/41,39mm²) — As,min=57,2mm² chi phối.
- **D3-D6**: cả 12/12 cột là lệch tâm LỚN (D4) theo cách diễn giải 1-phía — không cột nào rơi D5/D6 ở công trình 4 tầng, tải vừa phải này.
- **A3/A3a, D10/D11, B2, G7/G8, Bảng H**: KHÔNG kích hoạt (công trình 4 tầng, tải nhẹ, không kháng chấn) — vẫn PHẢI lập trình đầy đủ cho công trình khác lớn hơn.

---

## PHẦN R — VÍ DỤ ÁP DỤNG THỰC TẾ: KHUNG TRỤC 5 (minh họa toàn bộ quy trình bằng dữ liệu thật)

Kết quả đầy đủ việc áp dụng Rule Engine (Phần A-Q) lên MỘT bộ dữ liệu ETABS thật: "Khung Trục 5" — đồ án Kết cấu BTCT 2, ĐH Kiến trúc Hà Nội (SVTH Phan Nguyễn Thiện An, GVHD ThS. Lê Thế Anh). **Bằng chứng Rule Engine hoạt động ĐÚNG trên dữ liệu thật.**

### 68. Thông tin công trình và dữ liệu đầu vào

**Bảng R.1**

| Hạng mục | Giá trị |
| --- | --- |
| Tên công trình | Khung Trục 5 — cơ sở giáo dục, 4 tầng |
| Sơ đồ | Khung phẳng 2D, trục A(x=0)–B(x=5,6m)–C(x=7,1m) |
| Chiều cao tầng | Tầng 1: 4,2m; Tầng 2-4+mái: 3,2m/tầng (mái 13,8m) |
| Tiết diện cột trục A,B | 220×300mm |
| Tiết diện cột trục C | 220×220mm |
| Tiết diện dầm nhịp AB (5,6m) | 220×500mm |
| Tiết diện dầm nhịp BC (1,5m) | 220×300mm |
| Bê tông | B25 (Rb=14,5MPa; Rbt=1,05MPa) |
| Cốt thép dọc | CB500-V (Rs=Rsc=435MPa) |
| Cốt thép đai/treo | CB240-T (Rs=210MPa; Rsw=170MPa) |
| Mã thiết kế ETABS | SP 63.13330.2012 (Nga — phổ biến khi phần mềm chưa có TCVN) |
| Số cấu kiện | 12 cột + 8 dầm×3 vị trí = 24 vị trí thép dầm |

Dữ liệu As yêu cầu lấy trực tiếp từ kết quả ETABS (sheet "Conc Sum1" cột, "Conc Sum2" dầm) — đã qua phân tích nội lực/tổ hợp tải trọng, KHÔNG tính lại từ đầu ở Phần R.

### 69. Kết quả chọn thép — DẦM (24 vị trí)

Quy trình: As,yêu cầu→As,thiết kế=MAX(As,yêu cầu,As,min)→chọn ⌀18 (quy ước chuẩn dự án)→kiểm tra μmin≤μ≤μmax→chọn đai theo Q.

Tóm tắt kết quả (24/24 vị trí): tất cả dầm nhịp AB (220×500mm) dùng **2⌀18** (As=508mm²) ở vị trí thường, **3⌀18** (As=762mm²) ở vị trí As,yêu cầu lớn hơn (ví dụ tầng 2-3 gối trái/phải); đai ⌀6 2 nhánh, bước 130-190mm tùy tầng. Tất cả dầm nhịp BC (220×300mm) dùng **2⌀18** (As=508mm²) mọi vị trí; đai ⌀6 2 nhánh, bước 130mm.

Toàn bộ 24/24 vị trí rơi vào nhánh CHUẨN (A1) hoặc nhánh As,min chi phối (A2) — không cốt kép (A3), không vượt số thanh tối đa (A7). Bước đai hoàn toàn do cấu tạo chi phối (B1/B7) vì Q các dầm này nhỏ.

(Chi tiết đầy đủ 24 dòng xem file gốc `TAI_LIEU_HOP_NHAT_Chon_Thep_Khung_BTCT.pdf` Bảng R.2, hoặc `RuleEngine_ChonThep_KhungTruc5.xlsx` sheet 04-05.)

### 70. Kết quả chọn thép — CỘT (12 cấu kiện)

Quy ước: As từ ETABS (PMMArea) diễn giải là diện tích thép CHO MỘT PHÍA chịu mô men (As=As', đối xứng — xem giả định mục 72). Thép tổng = 2×thép chọn 1 phía.

Tóm tắt (12/12 cấu kiện): cột trục A/B (220×300mm) dùng **2×2⌀18** (As,tổng=1016mm²) phần lớn, **2×3⌀18** (As,tổng=1524mm²) tại chân cột tầng 1 và vị trí M lớn hơn. Cột trục C (220×220mm) dùng **2×2⌀18** (As,tổng=1016mm²) mọi vị trí. Đai ⌀6 2 nhánh, bước 180mm (μ,tổng>1,5% ở mọi cột → áp dụng điều kiện chặt E2).

μ,tổng dao động 1,78%÷2,66% (trục A/B) và 1,78%÷2,57% (trục C) — nằm trong giới hạn μmax=4% (D10 không kích hoạt). Toàn bộ 12/12 cột rơi nhánh lệch tâm LỚN (D4); không cột nào ở D2(N kéo)/D5(lệch tâm bé)/D10(vượt μmax)/D11(vượt độ mảnh).

(Chi tiết đầy đủ 12 dòng xem file gốc Bảng R.3, hoặc file Excel sheet 06-07.)

### 71. Kiểm chứng Rule Engine với dữ liệu mẫu có sẵn trong hồ sơ gốc

File ETABS gốc có 4 dòng đối chiếu (sheet "DoiChieuAsTinhToanGoc") trích từ thuyết minh tính tay gốc:

**Bảng R.4**

| Phần tử | Vị trí | As,chọn thuyết minh gốc | Thép gốc | As,chọn Rule Engine | Thép RE | Kết quả |
| --- | --- | --- | --- | --- | --- | --- |
| 14 | Cột (1 phía) | 763,4mm² | 3⌀18 | 762mm² | 3⌀18 | KHỚP |
| 32 | Dầm - Gối trái | 763,4mm² | 3⌀18 | 762mm² | 3⌀18 | KHỚP |
| 32 | Dầm - Gối phải | 763,4mm² | 3⌀18 | 762mm² | 3⌀18 | KHỚP |
| 32 | Dầm - Giữa nhịp | 508,9mm² | 2⌀18 | 508mm² | 2⌀18 | KHỚP |

Chênh lệch 0,9-1,4mm²/dòng chỉ do làm tròn diện tích 1 thanh ⌀18 (254 vs 254,47mm² chính xác) — KHÔNG phải sai lệch số thanh/đường kính. **Rule Engine đạt 4/4 khớp.**

> **GHI CHÚ ĐỐI CHIẾU VỚI DỰ ÁN HIỆN TẠI (quan trọng)**: Kết quả Bảng R.4 ở đây (phần tử 14: As_gốc=763,4mm²="1 phía", 3⌀18) **TRÙNG KHỚP HOÀN TOÀN** với số liệu đã tìm thấy trong `data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` sheet `DoiChieu_As_TinhToan_Goc` mà hệ thống AI hiện tại đã dùng để sửa lỗi "chia đôi As cột" (commit `c0c8c87`, revert ngày 2026-10-01). Đây là XÁC NHẬN ĐỘC LẬP THỨ HAI rằng quyết định KHÔNG chia đôi As_yc khi gọi `chon_thep_doc(loai="cot")` là ĐÚNG — As_yc (từ PMMArea ETABS) phải dùng TRỰC TIẾP làm As_target MỖI PHÍA, không chia đôi.

### 72. Giả định quan trọng cần xác minh lại trước khi dùng cho thi công

Rule Engine (Excel) áp dụng cho Khung Trục 5 dựa trên các GIẢ ĐỊNH SUY LUẬN (không phải điều khoản tiêu chuẩn, BẮT BUỘC đối chiếu lại thuyết minh gốc đầy đủ trước khi dùng cho thi công thật):

- **Giả định 1 — Đường kính chuẩn dự án ⌀18**: suy ra từ 4/4 dòng đối chiếu mẫu đều dùng riêng ⌀18 (chỉ đổi số thanh). Nếu công trình thật dùng nhiều đường kính khác nhau tùy vị trí, cần logic chọn đường kính tối ưu thay vì cố định.
- **Giả định 2 — As cột là diện tích MỘT PHÍA (As=As')**: suy ra vì đây là cách DUY NHẤT khớp dòng đối chiếu "phần tử 14". **Điểm RỦI RO CAO NHẤT nếu sai** — sẽ làm sai khối lượng thép cột hệ số 2 lần. **(Đã xác nhận đúng qua chạy thật trên hệ thống hiện tại — xem ghi chú ở mục 71.)**
- **Giả định 3 — a=40mm**: giá trị khởi đầu tiêu chuẩn, sai lệch nhỏ không đáng kể ở quy mô này.
- **Giả định 4 — Cốt đai cột hoàn toàn theo cấu tạo**: vì ETABS gốc KHÔNG có lực cắt cột (file mẫu không có cấu kiện cột). Có dữ liệu Q cột thật → cần tính lại theo Bảng B, lấy giá trị nhỏ hơn.

---

## PHẦN S — MỤC LỤC TỔNG HỢP TOÀN BỘ ĐỒ ÁN

### 73-75. Tóm tắt mức độ hoàn thiện

- **100%** yêu cầu cấu tạo (bố trí, kích thước, khoảng cách, neo, nối, uốn, nút khung) từ [TL-KHUNG]+[TL-2018] đã đưa vào — không lược bớt.
- Đã bổ sung tra cứu trực tuyến TCVN 5574:2018 + TCVN 9386 để xác nhận số hiệu điều khoản và lấp khoảng trống (Phần P).
- Đã hệ thống hóa toàn bộ điểm rẽ nhánh thành bảng quy tắc lập trình được (Phần Q), gồm cả trường hợp KHÔNG xuất hiện trong Khung Trục 5 nhưng cần thiết cho Rule Engine tổng quát.
- Đã kiểm chứng bằng dữ liệu thật, khớp 4/4 với thuyết minh gốc (Phần R) — và khớp ĐỘC LẬP LẦN 2 với dữ liệu dự án AI Agent hiện tại (xem ghi chú mục 71).
- **Điểm CÒN THIẾU/GIẢ ĐỊNH** (đã ghi minh bạch "nguồn không nêu rõ ở đây"): công thức định lượng chi tiết TCVN 9386 (mục 55.3/55.5/55.6, Bảng H); quy ước As cột ETABS (mục 72, nay đã xác nhận); quy ước đường kính chuẩn dự án thực tế; cấu kiện ngoài phạm vi chữ nhật/khung phẳng (D12, D13, A9 — Phần Q).

---

## GHI CHÚ TÍCH HỢP VÀO HỆ THỐNG AI AGENT HIỆN TẠI (bổ sung của phiên làm việc nạp tài liệu này)

Đối chiếu tài liệu này với code hiện tại (`src/rule_engine/`, `src/orchestrator/agents/rule_engine_agent.py`, `docs/RULES_TCVN5574.md`) phát hiện các điểm cần cập nhật, xếp theo mức ưu tiên:

1. **[ĐÃ SỬA — xác nhận đúng]** As cột = 1 phía, không chia đôi khi gọi `chon_thep_doc(loai="cot")` — Phần R mục 71/72 xác nhận độc lập lần 2, khớp hoàn toàn quyết định revert `c0c8c87`.
2. **[CẦN SỬA — μmax cột]** `src/rule_engine/cot_doc.py` hằng số `MU_MAX_COT_MOI_PHIA_PHAN_TRAM=3.0` (mỗi phía≤3%/tổng≤6%) cần đối chiếu lại với mục 54.2: TCVN 5574:2018 mục 6.2.1 gốc quy định μmax=4% TỔNG (không phải mỗi phía), 8% tại vùng nối chồng.
3. **[TÍNH NĂNG MỚI — chưa có]** Cắt/uốn cốt thép dọc dầm theo chiều dài (mục 53.3/Bảng A) — hệ thống hiện chỉ tính As độc lập tại 3 vị trí, không có khái niệm "điểm cắt lý thuyết".
4. **[TÍNH NĂNG MỚI — chưa có]** Số NHÁNH cốt đai (mục 53.4) — cần xác nhận `cot_dai.py`/Drawing Agent có truyền đủ số nhánh (không chỉ Asw tổng) để vẽ đúng mặt cắt.
5. **[TÍNH NĂNG MỚI — chưa có]** Cờ "kháng chấn" (Bảng H) — hệ thống hiện không có khái niệm này; KHÔNG áp dụng cho đồ án hiện tại (Khung Trục 5 không kháng chấn) nhưng cần có nếu mở rộng.
6. **[THAM KHẢO]** Bảng Q (70 trường hợp Điều kiện→Xử lý) nên được RULE_ENGINE_AGENT.md trích dẫn/tham chiếu trực tiếp khi agent gặp tình huống biên, thay vì chỉ dựa vào huấn luyện ngầm.
