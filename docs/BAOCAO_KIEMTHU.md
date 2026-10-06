# Báo cáo kiểm thử tổng thể (Phase 5)

Tổng hợp kết quả kiểm thử toàn bộ hệ thống — Phase 1 đến Phase 4 — theo đúng
tinh thần "ca nào đúng, ca nào lệch, lệch bao nhiêu và lý do". Nguồn số liệu
đối chiếu duy nhất: `docs/RULES_TCVN5574.md` mục 10 (ví dụ "Khung trục 3,
trường học"). Trạng thái test tự động: **133/133 pass** (`pytest`).

## 1. Phase 1 — Rule Engine (`src/rule_engine/`)

Đối chiếu trực tiếp với số liệu tính tay trong `RULES_TCVN5574.md` mục 10.

| Đại lượng | Sách | Code | Lệch | Đánh giá |
| --- | --- | --- | --- | --- |
| ξR (CB500-V, B30) | 0,493 | 0,493 | 0% | Đúng |
| αR | 0,371 | 0,371 | 0% | Đúng |
| Cột 22 — ea | 20mm | 20mm | 0% | Đúng |
| Cột 22 — e0 | 275,85mm | 275,85mm | 0% | Đúng |
| Cột 22 — x (lệch tâm lớn, quyết định nhánh) | 356mm | 356,32mm | <0,1% | Đúng — đúng nhánh "lệch tâm bé" |
| Cột 22 — Mu với thép **đã chọn** (2ϕ25+1ϕ22) so N·e | Ne=833,1 ≤ Mu | Ne=833,1 ≤ Mu=848,5 | An toàn dư ~1,8% | Đúng (mục đích "tự kiểm tra chéo") |
| Cột 22 — giải đồng thời As/x từ đầu (thiết kế) | x=326mm, As≈1250mm² | x≈316-320mm, As≈1220-1290mm² (tuỳ điểm khởi tạo) | ~3-8% (x), ~2-6% (As) | **Lệch có giải trình** — xem mục 3 |
| Dầm 40-41 gối C — ξ | 0,31 | 0,31 | 0% | Đúng |
| Dầm 40-41 gối C — Mu với As=1954mm² | ≈462kNm (thiết kế vừa đủ) | 462,0kNm (h0 suy ngược nhất quán) | 0% (theo h0 suy ra) | Đúng, xem ghi chú h0 |
| Dầm 40-41 nhịp (chữ T) — Mu với 3ϕ22 | Mmax=315,47kNm | 315,47kNm (rel 0,02) | <2% | Đúng |
| Dầm 40-41 — Qb,min | 92,7kN | 92,5kN | ~0,2% | Đúng |
| Dầm 40-41 — cốt treo ΣAsw | 69,03mm² | 68,8mm² (dùng h0 suy ngược) | ~0,3% | Đúng |
| Bảng thống kê thép — khối lượng (vd d=18, 4700mm×144) | 1351,96kG | 1352,03kG (dùng As bảng chuẩn × 7850kg/m³) | <0,01% | Đúng |

### Lệch đã ghi nhận và lý do

1. **Giải đồng thời As/x cho cột (thiết kế từ đầu, không phải verify)** — `RULES_TCVN5574.md` chỉ nêu tên biến của "công thức thực nghiệm bậc 2" (n, ε, γa) mà sách dùng để ra x=326mm, KHÔNG cho công thức đầy đủ. Theo đúng nguyên tắc "không tự suy diễn công thức khi tài liệu không nói rõ", `uon_nen.thiet_ke_cot_doi_xung_lech_tam_be` giải **đồng thời 2 phương trình đã có sẵn** ở mục 2.5 bằng phương pháp số (bisection) thay vì dùng công thức tắt của sách → ra nghiệm gần đúng nhưng không trùng khít 100%. Bài test chính (đáng tin cậy hơn) là **verify chiều ngược**: lấy đúng thép sách chọn cuối (2ϕ25+1ϕ22) và xác nhận Ne ≤ Mu theo đúng công thức mục 2.5 gốc — kết quả khớp, sai số 0%.
2. **h0 của dầm 40-41** không được `RULES_TCVN5574.md` nêu trực tiếp — suy ngược nhất quán từ 3 chỉ số độc lập (ξ=0,31; Qb,min=92,7kN; ΣAsw=69,03mm²) đều hội tụ về h0≈643,5mm, nên dùng giá trị này làm chuẩn test thay vì con số tự đặt tuỳ tiện.

### Lỗi thật phát hiện & đã sửa trong Phase 1

`verify.kiem_tra_tong_hop_dam` từng đếm nhầm **số thanh** thành **số loại đường
kính** khi kiểm tra mục 4.2 (`len(list)` thay vì `len(set(list))`). Tổ hợp
1Ø16+4Ø18 (5 thanh, 2 loại) bị báo sai "5 loại đường kính > 3". Phát hiện qua
chạy thật Phase 4 (không phải qua unit test cũ, vì test cũ luôn dùng tổ hợp 1
loại). Đã sửa + thêm `tests/test_verify.py` (trước đây module `verify.py`
chưa có file test riêng).

## 2. Phase 2 — Input Adapter (`src/input_adapter/`)

Không có dữ liệu ETABS thật để đối chiếu (theo xác nhận của người dùng ở
Phase 0) — kiểm thử bằng 2 file tự tạo (`tests/fixtures/`, không phải dữ liệu
tham khảo/code cũ):

- `dam_don_gian.csv` (header tiếng Việt rõ ràng) — heuristic ánh xạ đúng
  100% các trường bắt buộc, độ tin cậy ≥0,95 mọi trường.
- `bao_cao_etabs_day_du.xlsx` (nhiều sheet kiểu ETABS, tiếng Anh, tiết diện
  gộp dạng "D250x700") — heuristic ánh xạ đúng, tự suy b/h từ ký hiệu tiết
  diện qua `_suy_b_h_tu_ky_hieu`.

3 lỗi thuật toán so khớp thật được phát hiện và sửa NGAY khi viết test Phase
2 (trước khi giao — xem lịch sử phiên làm việc): từ khoá ngắn (1-2 ký tự)
khớp nhầm theo substring (vd "b" khớp vào "Beam"); ngưỡng fuzzy 0,6 quá lỏng
khiến "Nhóm thép" khớp nhầm vào trường As_yc. Đã sửa bằng so khớp theo token
+ nâng ngưỡng fuzzy lên 0,75.

## 3. Phase 3 — AutoCAD Tool (`src/drawing/`)

- Backend DXF (`ezdxf`): 19 unit test, đối chiếu kích thước mặt cắt, layer,
  nhãn — tất cả pass.
- Backend COM: **đã xác nhận vẽ thật thành công lên AutoCAD 2024** đang chạy
  trên máy kiểm thử (`scripts/smoke_test_com.py`). 1 lỗi COM thoáng qua thật
  ("Call was rejected by callee") phát hiện và sửa bằng cơ chế thử lại có
  giới hạn (`_thu_lai_khi_com_ban`).
- Đối chiếu bảng thống kê thép với `data/samples/BoTriThep_KhungTruc5_mau.pdf`:
  khớp trong sai số <0,1% (mục "khối lượng" ở bảng trên).
- **Lỗi vẽ thật phát hiện qua phản hồi trực quan (người dùng xem hình demo)**:
  cốt đai được vẽ với 4 góc VUÔNG SẮC (như đường bao bê tông), trong khi thực
  tế đai uốn từ 1 thanh thép tròn luôn có bán kính uốn tại góc (mục 6.4
  "Đường kính uốn tối thiểu"). Đã thêm primitive `VeCung` (cung tròn) vào IR,
  hàm `duong_bao_chu_nhat_bo_tron` dựng đường bao đai gồm 4 đoạn thẳng + 4
  cung (bán kính = đường kính uốn tối thiểu/2, coi đai là thép trơn CB240-T
  theo mục 8), cập nhật cả 2 backend (`ezdxf.add_arc`/COM `AddArc`) — đã xác
  nhận cả bằng ảnh render lẫn vẽ thật lên AutoCAD. Đây là lỗi KHÔNG bắt được
  bằng unit test (test chỉ kiểm tra kích thước/tồn tại đối tượng, không đánh
  giá "nhìn có đúng quy ước bản vẽ kỹ thuật không") — chỉ lộ ra qua người có
  chuyên môn xem trực tiếp bản vẽ, minh chứng thêm cho giới hạn của kiểm thử
  tự động đối với chất lượng THỂ HIỆN bản vẽ (khác với đúng SỐ LIỆU).
- **Đã bổ sung sau đợt kiểm thử đầu**: `ve_mat_bang_ket_cau` (mặt bằng kết
  cấu sàn — lưới trục có vòng tròn+số/chữ đầu trục, cột đúng tiết diện tại
  giao điểm, dầm vẽ đường tim+nhãn) và `ve_chi_tiet_nut_khung` (4 hình chi
  tiết phối cảnh nút khung — dựng bằng PHÉP CHIẾU TRỤC ĐO isometric trên nền
  IR 2D sẵn có, thêm primitive `VeCung`... không cần backend 3D riêng). 5
  test mới (`test_drawing_geometry.py`), đã tự kiểm tra bằng ảnh render
  (`scripts/demo_ve_mat_bang_va_chi_tiet.py`) — bố cục khớp quy ước bản vẽ
  mẫu (trục số/chữ trong vòng tròn, cột tại giao điểm). **Đây là hình MINH
  HOẠ SƠ ĐỒ** (khối cột/dầm giao nhau + vị trí đại diện thép dọc/đai), CHƯA
  vẽ chi tiết uốn móc/neo thật của từng thanh — khác với chi tiết thi công
  đầy đủ trong bản vẽ mẫu, ghi nhận đây là điểm đơn giản hoá có chủ đích.

## 4. Phase 4 — Agent điều phối (`src/orchestrator/`)

Kiểm thử ở 2 mức: (a) `FakeChatProvider` script sẵn kịch bản — 27 test, phủ
toàn bộ cơ chế vòng lặp/bộ đếm; (b) **chạy thật với OpenAI API**
(`gpt-5.6-luna`) — 5 lượt chạy pipeline đầy đủ:

| Kịch bản | Kết quả | Số lượt gọi model |
| --- | --- | --- |
| Dầm 44-45, gối trái | Đạt, sạch, không retry | 11 |
| Dầm 44-45, gối phải | Đạt, sạch, không retry | 11 |
| Dầm 44-45, giữa nhịp | Đạt, sạch, không retry | 11 |
| Cột 22, đại diện | Đạt, sạch, không retry | 12 |
| Batch 2 phần tử liên tiếp (`chay_toan_bo`) | Cả 2 đạt, không ảnh hưởng lẫn nhau | 11 mỗi phần tử |

### 5 lỗi thật phát hiện & sửa qua chạy thật (theo thứ tự phát hiện)

1. **Thiếu tool tra vật liệu** — LLM tự "nhớ" nhầm Rbt=1,22 cho B30 (đúng
   1,15), vi phạm nguyên tắc "LLM không tự tính số". Đã thêm tool
   `tra_vat_lieu` bọc `rule_engine.vat_lieu`, ép trong system prompt phải
   gọi trước bước chọn thép.
2. **Schema `ve_mat_cat` không phân biệt "đường kính" và "số lượng"** — LLM
   truyền `thanh_tren: [1, 4]` (số lượng) thay vì `[16,18,18,18,18]` (đường
   kính từng thanh). Đã bổ sung mô tả rõ ràng trong schema.
3. **`loai_mac_dinh` ghi đè sai loại phần tử khác trong cùng sheet** — LLM
   truyền `loai_mac_dinh='cot'` để xử lý cột 22 nhưng vô tình ép cả dầm
   44-45 (cùng sheet) thành `loai='cot'`. Đã thêm bảo vệ Ở TẦNG CODE (không
   chỉ prompt): bỏ qua `loai_mac_dinh` khi ánh xạ đã có cột "loại" đáng tin
   cậy theo từng dòng.
4. **`chon_to_hop_thep_doc` (logic dầm, xếp hàng) bị dùng nhầm cho cột** —
   ra "9Ø14 xếp 3 lớp" nhưng khi vẽ theo chu vi chỉ dựng được 8 điểm (lệch
   giữa As đã "chọn" và hình học thực vẽ). Đây là **khoảng trống thật ở
   Phase 1**, không phải lỗi vặt: chưa có hàm chọn thép chuyên cho cách bố
   trí "đều chu vi" (mục 4.2). Đã viết `cot_doc.chon_to_hop_thep_chu_vi_cot`
   và nối thẳng `chon_thep_doc → ve_mat_cat` cho cột (cùng 1 shape, không để
   LLM tự suy đổi).
5. **`de_xuat_anh_xa` nhận nhầm tên cột gốc trong file làm `truong_bat_buoc`**
   (đúng ra phải là tên trường chuẩn nội bộ) — khiến `thieu_bat_buoc` báo sai
   toàn bộ dù ánh xạ đã đủ 100%, gây hỏi xác nhận thừa mỗi lượt chạy. Đã
   thêm bảo vệ tầng code (bỏ qua giá trị không khớp trường chuẩn nào) + mô
   tả rõ trong schema.

Sau khi sửa hết 5 lỗi, chạy lại toàn bộ 5 kịch bản: **không còn retry, không
còn hỏi xác nhận thừa, số lượt gọi giảm từ 12 xuống 11**. Tổng chi phí API
cho toàn bộ quá trình debug: ước tính dưới 50 US cent (model rẻ nhất
`gpt-5.6-luna`, $0,20/$1,20 mỗi 1M token).

### Chạy LIỀN MẠCH toàn bộ frame có trong dữ liệu (`scripts/chay_lien_mach_khung.py`)

Khác với 5 kịch bản ở trên (mỗi lần chạy script riêng cho 1 vị trí), đây là
**1 lượt `pipeline.chay_toan_bo` duy nhất** xử lý LẦN LƯỢT cả 4 vị trí có
trong `tests/fixtures/dam_don_gian.csv` (dầm 44-45: gối trái/gối phải/giữa
nhịp; cột 22: đại diện), rồi gộp kết quả THẬT (không bịa số liệu) thành 1 tờ
bản vẽ (`output/chay_lien_mach/TO_BAN_VE_TONG_HOP.dxf`):

| Vị trí | Thép Agent chọn | Kiểm chứng bản vẽ |
| --- | --- | --- |
| Dầm 44-45, gối trái | 1Ø16+4Ø18 (As=1219,1mm²) | ĐẠT |
| Dầm 44-45, gối phải | 1Ø25+1Ø28 (As=1106,7mm²) | ĐẠT |
| Dầm 44-45, giữa nhịp | 1Ø12+3Ø14 (As=574,8mm²) | ĐẠT |
| Cột 22, đại diện | 8Ø28 đều chu vi (As=1847,4mm²/phía) | ĐẠT |

**4/4 vị trí đạt**, đã tự kiểm tra bằng ảnh render tờ bản vẽ gộp — 4 mặt cắt
+ khung tên hiển thị đúng số thanh/đường kính khớp với bảng trên.

**Ghi nhận đáng chú ý**: cột 22 lần chạy liền mạch này ra **8Ø28** (dư
~36% so với As yêu cầu 1362mm²/phía), khác với lần chạy đơn lẻ trước đó ra
**8Ø25** (dư ~8%) — cùng 1 hàm Rule Engine, cùng input, nhưng LLM (bản chất
không hoàn toàn tất định giữa các lần gọi) đề xuất tham số `duong_kinh_cho_phep`
khác nhau cho `chon_thep_doc`. Cả 2 kết quả đều **hợp lệ về kỹ thuật** (qua
hết `tu_kiem_tra`) — đây là minh chứng thực nghiệm cho đúng nguyên tắc kiến
trúc cốt lõi: dù LLM không tất định, **Rule Engine (deterministic) luôn là
lớp quyết định cuối cùng về tính hợp lệ kỹ thuật**, LLM chỉ dao động trong
phạm vi các phương án Rule Engine chấp nhận.

### Webapp nội bộ (`webapp/`) — nhận Excel, chat hỏi-đáp, xem bản vẽ trên trình duyệt

Bọc toàn bộ pipeline trên bằng 1 web app Flask chạy local: upload file →
tự khám phá danh sách (phần_tử, vị_trí) → chạy `agent.chay_vong_lap_tool`
cho từng vị trí, log trực tiếp mọi lời gọi tool lên trang → khi Agent gọi
`hoi_nguoi_dung`, trang hiện hộp chat chặn tiến trình nền tới khi người
dùng trả lời → xong thì hiện ảnh PNG (render từ DXF) + link tải DXF ngay
trên trang. Đây là vòng lặp thật đầu tiên nối liền được **cả 4 vòng lặp**
của mục 5 TONGQUAN_AI_AGENT.md trong 1 phiên chạy duy nhất, qua giao diện
người dùng thật (không phải script/terminal).

Ngay trong lượt chạy thật đầu tiên qua webapp, phát hiện thêm **2 lỗi thật
nghiêm trọng** — cả 2 đều cùng 1 gốc rễ: dữ liệu số có ảnh hưởng an toàn kỹ
thuật bị để ngỏ cho LLM tự cung cấp, dù đã có mô tả tool/prompt yêu cầu
không làm vậy.

6. **LLM tự bịa `x=0`, `e` thô sơ khi gọi `tu_kiem_tra` cho cột** — dù đã có
   tool riêng `tinh_lech_tam_cot` (mục 2.5) và system prompt ghi rõ phải gọi
   trước, LLM vẫn bỏ qua và tự đặt thẳng `x=0` vào `tu_kiem_tra`. Hậu quả:
   `Mu` tính thiếu hẳn phần bê tông chịu nén → điều kiện `N·e ≤ Mu` bị ép
   sai lệch → Agent tưởng thiếu thép và tăng dần `As_target` qua 3 lượt tự
   sửa, kết quả cuối **8Ø32 (As=2412,6mm²/phía)** — dư khoảng **93%** so với
   nhu cầu thật (~1362mm²/phía). Thêm tool không đủ: đã thử thêm tool +
   mô tả "BẮT BUỘC gọi trước" nhưng chạy lại LLM VẪN bỏ qua. Chỉ khắc phục
   được khi chặn Ở TẦNG CODE: gộp công thức mục 2.5 vào 1 hàm nội bộ
   `_tinh_lech_tam_cot_noi_bo`, sửa `tu_kiem_tra` để **không nhận `x`/`e` từ
   LLM nữa** (chỉ nhận `N`, `M`, tiết diện thật), tool tự tính `x`/`e` và bỏ
   qua hoàn toàn mọi giá trị LLM tự đặt cho 2 trường này.
7. **LLM tự đặt sai `mu_max_moi_phia` khi gọi `tu_kiem_tra` cho cột** — phát
   hiện NGAY SAU khi sửa xong lỗi 6 (cùng 1 lượt chạy xác nhận lại): tuy
   `x`/`e` đã đúng, LLM lại tự truyền `mu_max_moi_phia=0.04` (đúng ra ngưỡng
   TCVN mục 4.1 là **3,0%**, LLM nhầm cả giá trị lẫn đơn vị). Hậu quả: 1 cột
   **đã đạt thật** (μ mỗi phía = 1,05–1,07% < 3%) liên tục bị báo vi phạm giả
   `"μ mỗi phía=1,05% > 0,04%"`, tốn hết 3 lượt tự sửa vô ích (tăng đường
   kính, tăng cover... không giải quyết được vì gốc vấn đề là ngưỡng sai chứ
   không phải thiếu thép), cuối cùng suýt phải hỏi người dùng báo cáo "không
   đạt" cho 1 thiết kế thực ra hợp lệ. Áp dụng đúng cách sửa lỗi 6: bỏ hẳn
   `mu_max`/`mu_max_moi_phia` khỏi các trường `tu_kiem_tra` chấp nhận từ LLM
   (cả nhánh dầm lẫn cột), luôn dùng hằng số TCVN cố định
   (`cot_doc.MU_MAX_PHAN_TRAM` / `MU_MAX_COT_MOI_PHIA_PHAN_TRAM`). Chạy lại
   xác nhận: cột 22 qua `tu_kiem_tra` đạt ngay lần đầu (`dat=True,
   vi_pham=[]`), không còn tự sửa thừa.

Cả 2 lỗi trên rút ra cùng 1 nguyên tắc chung, áp dụng ngược lại toàn bộ
`tools.py`: **với bất kỳ tham số nào có vai trò "ngưỡng/định nghĩa cố định
theo quy chuẩn" (không phải input mô tả bài toán), không được để LLM tự
cung cấp dù chỉ là tuỳ chọn — phải chặn ở tầng code, vì mô tả tool/system
prompt không đủ ràng buộc hành vi LLM khi có sai lệch xảy ra.**

### Mở rộng: vẽ KHUNG TỔNG THỂ (mặt đứng khung) trước khi vẽ mặt cắt

Theo yêu cầu mở rộng phạm vi hiển thị (không mở rộng phạm vi TÍNH TOÁN — vẫn
giữ đúng ranh giới "không tự phân tích kết cấu" của TONGQUAN_AI_AGENT.md mục
3): trước khi vẽ từng mặt cắt riêng lẻ, hệ thống giờ có thể lắp 1 bản vẽ MẶT
ĐỨNG KHUNG TỔNG THỂ (toàn bộ cột/dầm, đúng vị trí lưới trục/tầng), dùng ĐÚNG
nhãn thép mà Rule Engine đã tự chọn cho từng phần tử.

- **Input Adapter**: thêm 2 trường tuỳ chọn `truc`/`tang` vào `PhanTuKhung`
  (cùng khuôn mẫu trường `tang` đã có sẵn — không phá vỡ schema cũ, file
  không có 2 cột này vẫn chạy y hệt trước, chỉ bỏ qua bước vẽ khung tổng thể).
- **`src/orchestrator/khung_ve.py`** (mới): lắp `geometry.ve_mat_dung_khung`
  từ danh sách `PhanTuKhung` + nhãn thép thật. Toạ độ lưới trục/cao độ mốc LÀ
  THAM SỐ TƯỜNG MINH (đúng triết lý đã ghi trong `geometry.py`) — khi không
  truyền, tự suy TOẠ ĐỘ ĐỀU NHAU theo thứ tự xuất hiện (tổng quát, dùng được
  cho file bất kỳ có cột truc/tang, nhưng không đúng tỉ lệ nhịp/tầng thật).
- **webapp**: tự động gọi bước lắp khung tổng thể (toạ độ đều nhau) sau khi
  xử lý xong tất cả vị trí, chèn LÊN ĐẦU danh sách ảnh/DXF kết quả — đúng thứ
  tự "khung trước, mặt cắt sau".
- **`scripts/ve_khung_truc5_day_du.py`** (mới): kịch bản chứng minh với TOẠ
  ĐỘ THẬT của khung trục 5 (lấy đúng mục 2 + Hình 4 thuyết minh gốc), chạy
  LIỀN MẠCH cả 12 cột + 8 dầm × 3 vị trí (36 vị trí) — nội lực M/N/Q lấy ĐÚNG
  Bảng 24/25 thuyết minh (vai trò ETABS theo đúng ranh giới phạm vi), As yêu
  cầu lấy đúng Bảng 26/27 (As lý thuyết TRƯỚC khi làm tròn thanh — hệ thống
  TỰ chọn thanh độc lập qua `chon_thep_doc`, không copy đáp án sách).

8. **`tinh_cot_dai` — LLM tự bịa diện tích tiết diện `A` cho cột** — phát
   hiện ngay trong lượt chạy đầu của khung trục 5 đầy đủ: tool cần `A=b×h`
   (mục 3.3, tính φn ảnh hưởng lực dọc N) nhưng chỉ nhận `b`/`h0` (không có
   `h` đầy đủ) nên để LLM tự nhân rồi truyền `A`. LLM truyền sai giá trị này
   cho cột 14 (220×300mm, N=483,2kN, B25 — tiết diện ĐÃ ĐƯỢC XÁC NHẬN đủ khả
   năng trong chính thuyết minh gốc, mục 5.3.2), khiến σm=N/A bị đội giả tạo
   và báo lỗi "σm > Rb — tiết diện quá bé" cho 1 tiết diện thực ra hoàn toàn
   đạt. Cùng gốc rễ với lỗi 6/7: số liệu SUY ĐƯỢC từ input khác (ở đây chỉ là
   phép nhân b×h) không nên để LLM tự làm. Sửa: `tinh_cot_dai` nhận thêm `h`
   (tuỳ chọn) và TỰ TÍNH `A=b*h` nội bộ khi có `h`, bỏ hẳn `A` khỏi schema để
   không mời LLM tự tính rồi truyền vào.

### Kết quả chạy lại sau khi sửa lỗi 8: 36/36 vị trí đạt

Chạy lại `scripts/ve_khung_truc5_day_du.py` sau khi sửa lỗi 8: **36/36 vị
trí đạt kiểm chứng bản vẽ** (12 cột + 8 dầm × 3 vị trí), không còn câu hỏi
bị kẹt. Bản vẽ khung tổng thể (`output/khung_truc5_day_du/MAT_DUNG_KHUNG_
TONG_THE.dxf`) đã tự render và kiểm tra bằng mắt: 3 trục A/B/C đúng tỉ lệ
nhịp thật (A-B rộng 5600mm, B-C hẹp 1500mm), 4 tầng đúng cao độ thật, 20
hình chữ nhật cột/dầm nối đúng vị trí lưới trục — khớp cấu trúc bản vẽ tham
khảo gốc (`data/samples/BoTriThep_KhungTruc5_mau.pdf`).

Đối chiếu tay thép cột hệ thống ĐÃ TỰ CHỌN (độc lập, không copy) với Bảng 26:

| Cột (trục, tầng) | As yêu cầu (mm²) | Sách chọn | Hệ thống chọn | Nhận xét |
| --- | --- | --- | --- | --- |
| 1 (A, tầng2) | 743,19 | 3Ø18 (763,4) | 4Ø22 (760,2) | As gần bằng, khác combo |
| 14 (B, tầng2) | 752,76 | 3Ø18 (763,4) | 4Ø22 (760,2) | As gần bằng, khác combo |
| 15 (B, tầng2-3) | 503,59 | 2Ø18 (508,9) | 4Ø18 (509,0) | Khớp gần như tuyệt đối |
| 4 (A, tầng4-mái) | 304,57 | 2Ø16 (402,1) | 4Ø16 (402,2) | Khớp gần như tuyệt đối |
| 19/20/21 (trục C, tải nhỏ) | 71,6–123,5 | 2Ø16 (402,1) | 4Ø12 (226,2) | Hệ thống bám sát mức tối thiểu cấu tạo hơn — vẫn ≥ As yêu cầu |

Toàn bộ 12 cột đều **As thực ≥ As yêu cầu**; combo thanh cụ thể khác sách ở
nhiều vị trí do khác quy tắc bố trí (đều chu vi tối thiểu 4 thanh + ưu tiên
ít thừa diện tích nhất) — đúng đặc điểm đã ghi ở hạn chế #4, KHÔNG phải lỗi.
8 dầm × 3 vị trí cũng đều đạt.

**Chi phí/thời gian thực tế**: 36 vị trí × trung bình ~11 lượt gọi model ≈
400 lượt gọi `gpt-5.6-luna`, chạy xong trong khoảng 15-20 phút, chi phí ước
tính dưới 1 USD.

### Đọc trực tiếp báo cáo ETABS THẬT (`src/input_adapter/etabs_reader.py`)

Người dùng thử tải lên `data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` — file mẫu
CHÍNH THỨC của đồ án (nhắc tới ở TONGQUAN_AI_AGENT.md mục 3, dựng lại đúng
định dạng ETABS thật) — qua webapp và gặp lỗi "thiếu ánh xạ cho các trường
bắt buộc". Điều tra cho thấy đây KHÔNG phải lỗi vặt mà là khoảng trống kiến
trúc thật: file ETABS thật xuất ra **15+ bảng quan hệ** (Grid Lines, Story
Definitions, Joint Coordinates, Connectivity - Frame, Frame Section
Assignments, Frame Props, Material Props, các bảng "Concrete Design
Summary"...), mỗi bảng có đúng 3 dòng đầu cố định (`TABLE: <tên>` → tên cột
thật → đơn vị) trước khi tới dữ liệu — hoàn toàn khác mô hình "1 sheet
phẳng, mỗi dòng 1 vị trí" mà `adapter.py`/`heuristics.py` xử lý được. Phải
**JOIN nhiều bảng theo "Frame" ID** mới dựng lại được 1 phần tử hoàn chỉnh.

Đã viết `src/input_adapter/etabs_reader.py`: đọc đúng 3 dòng đầu mỗi bảng,
JOIN Connectivity → Joint Coordinates (ra trục/tầng qua so khớp toạ độ với
Grid Lines/Story Definitions) → Frame Section Assignments → Frame Props (ra
b/h, mác vật liệu) → 2 bảng Concrete Design Summary (PMM Summary cho CỘT ra
N/M/As trực tiếp; bảng thiết kế uốn/cắt cho DẦM ra As mỗi mặt cắt). Trả về
CÙNG `BoDuLieuKhung` mà `adapter.chuan_hoa_bang` tạo ra nên mọi code phía
sau (Rule Engine, Agent, khung_ve, webapp) dùng lại nguyên vẹn.

**3 lỗi thật phát hiện thêm trong quá trình này:**

9. **Phân loại vị trí dầm ngắn sai** — nhịp dầm rất ngắn (nhịp B-C 1,5m)
   có 2 mặt cắt kiểm tra CÙNG toạ độ Location (~1,39m — ETABS chỉ báo 1 vị
   trí đại diện gần cuối dầm cho cả kiểm tra giữa nhịp lẫn gối phải). Nếu
   phân loại "gối trái/giữa nhịp/gối phải" chỉ theo NGƯỠNG TOẠ ĐỘ (không
   theo mặt thép chi phối) sẽ gộp nhầm 2 mặt cắt khác nhau thành cùng 1
   nhãn, làm MẤT HẲN 1 vị trí. Sửa: phân loại theo mặt thép chi phối (trên
   = mô men âm = gối, dưới = mô men dương = nhịp) trước, chỉ dùng toạ độ để
   phân biệt gối trái/phải khi mặt trên chi phối.
10. **LLM tự bịa `Q=0` cho `tinh_cot_dai` (cột)** — báo cáo Concrete Design
    Summary của ETABS không xuất lực cắt Q thô cho cột (bảng PMM Summary chỉ
    có `VMajorRebar` đã thiết kế sẵn, phần lớn =0). Dù mô tả yêu cầu đã DẶN
    RÕ "không tự đặt Q", LLM vẫn tự đặt `Q=0` cho cột 1 lần chạy, và một lần
    chạy khác lại làm đúng cho cột 1-4 nhưng TÁI PHẠM ở cột 14 — xác nhận
    lại đúng bài học đã rút ra nhiều lần trong đồ án: **dặn dò qua prompt
    KHÔNG ĐỦ ĐÁNG TIN CẬY, phải chặn ở tầng code**. Sửa: `webapp/jobs.py`
    thêm cờ `bo_qua_tinh_cot_dai` — khi vị trí không có Q thật, mọi lệnh gọi
    `tinh_cot_dai` bị CHẶN CỨNG ngay tại tầng dispatch, trả lỗi rõ ràng thay
    vì thực thi, bất kể LLM truyền Q bao nhiêu.
11. **`tu_kiem_tra` cho DẦM cũng cần Q — chặn mỗi `tinh_cot_dai` không đủ** —
    phát hiện ngay sau khi sửa lỗi 10: `verify.DauVaoVerifyDam.Q` là trường
    bắt buộc (không có default), nên dù đã chặn `tinh_cot_dai`, LLM vẫn lọt
    qua bằng cách tự bịa `Q=0` thẳng vào `tu_kiem_tra` (dầm 41/gối trái) —
    hoặc khi né tránh bịa số thì lại KẸT VÒNG LẶP hỏi người dùng lặp lại 5
    lần vô ích cho vị trí kế tiếp (dầm 41/giữa nhịp) vì không biết xử lý sao
    khi thiếu Q. Sửa: `tu_kiem_tra` cho dầm khi thiếu Q trả về kết quả
    TRUNG THỰC thay vì lỗi hay bịa — chỉ kiểm tra As dọc (dữ liệu có thật,
    đáng tin: `As_thực ≥ As_yêu_cầu`), kèm `canh_bao` rõ ràng "chưa kiểm tra
    được chịu cắt", và hướng dẫn LLM không hỏi lại/không gọi lại.

**Kết quả sau khi sửa cả 3 lỗi — chạy lại toàn bộ qua webapp với file ETABS
thật**: **36/36 vị trí đạt kiểm chứng bản vẽ, 0 câu hỏi cần hỏi người dùng,
0 lần gọi `tinh_cot_dai` (đúng — luôn tránh/bị chặn), 24/24 lượt `tu_kiem_tra`
dầm đều trả về đúng `canh_bao` (không lần nào bịa Q)**. Bản vẽ khung tổng thể
(`KHUNG_TONG_THE.dxf`) tự lắp thành công từ topology THẬT do `etabs_reader`
suy ra (trục/tầng qua so khớp toạ độ Joint Coordinates với Grid Lines/Story
Definitions) — xác nhận toàn bộ chuỗi "đọc ETABS thật → xử lý → vẽ khung
tổng thể" hoạt động end-to-end, tự động hoàn toàn, không cần người can thiệp.

### Bản vẽ khung tổng thể "hoàn toàn sai" — thiếu kích thước hình học

Người dùng xem trực tiếp `KHUNG_TONG_THE.dxf` và phản hồi bản vẽ "hoàn toàn
sai". Điều tra: đúng — `ve_mat_dung_khung` (mới viết ở mục trên) chỉ vẽ
đường tim trục + tên trục/tầng, **hoàn toàn không có kích thước nhịp/chiều
cao tầng nào** — nhìn như 1 sơ đồ trống, thiếu hẳn thông tin bắt buộc phải
có trên 1 bản vẽ kết cấu thật (mục 10.7 checklist).

Đã sửa: bổ sung 3 hàng `VeKichThuoc` (kích thước tuyến tính, cơ chế đã có
sẵn và dùng đúng ở `ve_mat_cat_dam/cot`) — nhịp từng khoang, tổng bề rộng,
chiều cao từng tầng. Trong lúc sửa lộ thêm **2 lỗi thật khác**:

12. **Dimstyle mặc định "EZDXF" của ezdxf có `dimlfac=100`** (hệ số nhân
    khi hiển thị số đo tự động) — nếu để backend TỰ ĐO khoảng cách (không
    truyền `nhan` tường minh), 5600mm hiển thị thành **"560000"**. Sửa: mọi
    kích thước LUÔN tự tính `nhan=f"{abs(p2-p1):g}"` tường minh (đúng khuôn
    mẫu đã dùng ở mặt cắt), không phụ thuộc cấu hình dimstyle của backend.
13. **Cỡ chữ 15mm (đúng cho mặt cắt cỡ 250-700mm) trở nên vô hình ở quy mô
    khung tổng thể (~5600-14500mm, lớn hơn ~20 lần)** — dữ liệu/toạ độ hoàn
    toàn đúng nhưng chữ số/nhãn nhỏ tới mức không đọc được trên bản vẽ thật,
    trông giống "bản vẽ trống" dù không phải lỗi hình học. Phát hiện qua tự
    render lại bằng `ezdxf.addons.drawing` và so sánh trực tiếp với mặt cắt
    (cùng cơ chế, mặt cắt hiện chữ rõ ràng, khung tổng thể thì không) — cô
    lập được nguyên nhân là TỶ LỆ CỠ CHỮ, không phải cơ chế vẽ bị hỏng. Sửa:
    thêm trường `co_chu` vào `VeKichThuoc` (mặc định 15mm, không đổi hành vi
    cũ của mặt cắt), `ve_mat_dung_khung` dùng cỡ chữ lớn hơn hẳn (200-250mm)
    tương xứng quy mô toàn khung.

Xác nhận bằng tự render lại (`ezdxf.addons.drawing`, nền trắng): bản vẽ giờ
hiện rõ đầy đủ — tên trục A/B/C, cao độ từng tầng, kích thước nhịp
**5600/1500/tổng 7100**, chiều cao tầng **4200/3200/3200/3200**, và nhãn
từng phần tử (1-4, 14-17, 18-21 cho cột; 32,34,36,38,39,41,43,45 cho dầm) —
khớp đúng số liệu thật của khung trục 5.

### Quy cách bố trí mặt đứng khung — nhiều vòng phản hồi trực tiếp từ người dùng

Sau khi kích thước hình học đã đúng (mục trên), người dùng tiếp tục phản hồi
bản vẽ vẫn "hoàn toàn sai" về QUY CÁCH THỂ HIỆN (không phải hình học) — dẫn
tới việc tra cứu tài liệu tham chiếu (`Giáo Trình Vẽ Kỹ Thuật Xây Dựng.pdf`
đọc toàn bộ; `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.pdf` — tài liệu tổng hợp TCVN
8-20:2002/4612-88/7-1993/5705-1993/5574:2018, được người dùng xác nhận là quy
tắc chuẩn) và 1 ảnh chụp bản vẽ CAD thật làm bằng chứng đối chiếu. Trải qua
nhiều vòng chỉnh sửa bị phản hồi lại, các lỗi thật phát hiện:

14. **`lineweight` DXF không hiển thị nét đậm** — `layers.py` khai báo
    `do_day_net_mm` đúng theo mục 10.7.2, nhưng `lineweight` là thuộc tính
    HIỂN THỊ mà phần lớn phần mềm xem DXF (kể cả AutoCAD Model Space mặc
    định) KHÔNG bật hiển thị trừ khi người dùng tự bật "Show Lineweight" —
    nét trông mảnh như nhau dù khai báo khác `do_day_net_mm`. Sửa: thêm
    trường hình học THẬT `VeDaGiac.do_rong_net` → `const_width` (ezdxf) /
    `ConstantWidth` (COM `AcadLWPolyline`) — luôn hiển thị đậm bất kể cấu
    hình phần mềm xem, xác nhận bằng đọc lại `e.dxf.const_width` từ file đã
    lưu và render lại không ép hiển thị lineweight.
15. **Hiểu sai chiều áp dụng mục 1.2 (TCVN 4612-88) — VÀ RỒI LẠI HIỂU SAI LẦN
    NỮA KHI "SỬA LẠI" DỰA TRÊN 1 ẢNH CHỤP MÀN HÌNH** — lần đầu vẽ đường bao
    cấu kiện ĐẬM (sai theo câu chữ mục 1.2); sửa lại thành bê tông MẢNH + 2
    đường thép dọc giả ĐẬM (ĐÚNG theo câu chữ); rồi lại đổi theo 1 ảnh chụp
    CAD thật do người dùng cung cấp trông có vẻ đường bao "đậm" và không có
    đường thép dài — kết luận khi đó: "ảnh chụp có độ ưu tiên cao hơn lý
    thuyết", quay lại đường bao đậm + xoá hẳn đường thép dọc giả.

    **PHIÊN SAU (đọc lại đúng tài liệu này) LẶP Y HỆT SAI LẦM ĐẦU TIÊN** (đổi
    lại đường bao mảnh + thêm đường thép dọc), vì không biết lịch sử trên —
    rồi bị người dùng phản hồi lần nữa. Lần này, thay vì tin 1 ảnh chụp màn
    hình khác (vốn CHÍNH LÀ nguồn gây ra kết luận sai ở trên — Lineweight
    KHÔNG hiển thị đúng qua ảnh chụp nếu AutoCAD chưa bật "Show Lineweight",
    đã ghi rõ ở lỗi #14 CÙNG mục này, nhưng bị BỎ QUA khi đọc ảnh ở lỗi #15
    lần đầu!) — đã đọc TRỰC TIẾP thuộc tính `Layer.Lineweight` (số liệu lưu
    trong file, không qua hiển thị/ảnh chụp) của 1 file DWG thật khác
    (`KC.HIEP.dwg`, có layer `01-XMT.Columns`/`02-XMT.Beams` VÀ
    `02-XMT.Reinforcement`/`THEP` tách riêng rõ ràng theo tên):

    ```
    01-XMT.Columns        Lineweight = 0.25mm
    02-XMT.Beams           Lineweight = 0.25mm
    02-XMT.Reinforcement   Lineweight = 0.40mm  <- ĐẬM HƠN đường bao
    THEP                    Lineweight = 0.35mm  <- ĐẬM HƠN đường bao
    ```

    **Đây là bằng chứng KHÁCH QUAN (thuộc tính lưu trong file), không phụ
    thuộc cách hiển thị/độ phân giải ảnh chụp** — xác nhận DỨT ĐIỂM: cốt
    thép vẽ đậm hơn đường bao cấu kiện, ĐÚNG mục 1.2 TCVN 4612-88, sai lầm
    nằm ở lỗi #14 (lineweight không hiển thị đúng qua ảnh chụp) đã lây sang
    cách đọc ảnh ở lỗi #15 lần đầu, không phải bản thân TCVN 4612-88 sai.
    **Bài học sửa lại**: "ảnh chụp thật ưu tiên hơn lý thuyết" chỉ đúng khi
    ảnh chụp phản ánh đúng dữ liệu — với thuộc tính như Lineweight (vốn có
    cơ chế hiển thị BẬT/TẮT độc lập với giá trị lưu), phải đọc THUỘC TÍNH
    THẬT qua COM (`Layer.Lineweight`), không suy diễn qua độ đậm nhìn thấy
    trên ảnh chụp/màn hình.

    Về đường thép dọc chạy dọc thân cấu kiện: đo chiều dài thật ~700 đoạn
    thẳng trên layer `Reinforcement`/`Stirrup` của `KC.HIEP.dwg` cho kết quả
    HỖN HỢP (83% ngắn <2000mm — khớp đường dẫn/móc neo/ký hiệu số hiệu mục
    2.2; nhưng 17% dài >3000mm — khớp thép dọc thật chạy dài) — tức KHÔNG
    phải tuyệt đối "chỉ số hiệu, không đường dài" như kết luận vội trước đó,
    cũng không phải "luôn luôn 2 đường dài suốt cấu kiện" — thực tế là cả
    hai cùng tồn tại. Quyết định cuối: GIỮ đường bao mảnh + cốt thép đậm
    (đúng theo Lineweight thật) VÀ giữ đường thép dọc đơn giản hoá (khớp 1
    phần thực tế quan sát được, dù không copy chính xác 100% cách chia đoạn
    ngắn/dài phức tạp của file tham chiếu).
16. **Bảng màu 3-4 màu theo ảnh mẫu vẫn bị phản hồi "khó nhìn"** — 3 vòng
    liên tiếp thử khớp đúng màu theo ảnh chụp (magenta/xanh lá/cyan mỗi
    layer 1 màu riêng) đều bị phản hồi lại là khó nhìn — vì TCVN thật ra
    KHÔNG quy định màu sắc (chỉ quy định LOẠI NÉT — mục 1.1), nên "đúng
    màu ảnh mẫu" không đồng nghĩa "dễ nhìn nhất" khi nền/thiết bị xem người
    dùng khác với ảnh mẫu. Sửa: bỏ hẳn việc khớp màu theo ảnh, giảm còn
    ĐÚNG 2 màu — màu 7 (ACI, tự đảo đen/trắng theo nền, tương phản tối đa
    mọi thiết bị) cho toàn bộ nét hình học/thép (OUTLINE, REBAR_MAIN,
    REBAR_STIRRUP, TEXT), và 1 màu phụ DUY NHẤT (cyan, ACI 4) dùng chung cho
    mọi chú thích (AXIS + DIM) — tách biệt rõ "hình học thật" khỏi "chú
    thích", không cần đoán màu nền người xem đang dùng.
17. **Nhãn cấu kiện đặt ở góc trên-trái gây chồng lấn khi vẽ thêm nội dung**
    — nhãn cột VÀ nhãn dầm đều đặt ở góc trên-trái cấu kiện, vô tình rơi
    đúng vào dải hẹp ngang qua ranh giới sàn/nút khung (đỉnh cột ≈ tim dầm ≈
    đường tầng) — không rối ở bản vẽ hiện tại (còn ít nội dung) nhưng CHẮC
    CHẮN rối khi bổ sung thêm số hiệu thép/ký hiệu khác vào đúng dải đó.
    Sửa: nhãn cột dời về GIỮA chiều cao đoạn cột (khoảng trống rộng nhất),
    nhãn dầm dời lên CHÍNH GIỮA phía trên dầm (vị trí X giữa nhịp không bao
    giờ trùng dải X của bất kỳ cột nào) — cả 2 vị trí đều là khoảng trống
    thật sự, không phụ thuộc số lượng nội dung bổ sung sau này.
18. **Chữ "tên tầng" lặp lại trong nhãn cao độ là thừa** — nhãn cao độ ban
    đầu ghi `f"{tên_mốc} {cao_độ}"` (vd. "tang2 +3.20") — tên tầng chỉ có ý
    nghĩa nội bộ (khớp dữ liệu `cao_do_moc`/`moc_tham_chieu`), không phải
    thông tin cần thiết trên bản vẽ (đã có trục cao độ bên trái + số liệu
    đủ để đọc). Sửa: chỉ ghi số cao độ (`f"{y/1000:+.2f}"`), bỏ hẳn tên mốc.

Xác nhận bằng tự render lại (`ezdxf.addons.drawing`, dựng lại kịch bản khung
3 tầng × 3 trục, có mốc tham chiếu kiến trúc): bản vẽ giờ chỉ dùng 2 màu
tương phản cao (trắng/đen tự đảo + 1 cyan phụ), không còn chữ tên tầng lặp
lại, nhãn cột/dầm không còn rơi vào dải ranh giới sàn — còn khoảng trống rõ
ràng để bổ sung số hiệu thép (mục 2.2)/bảng thống kê (mục 3.9) sau này mà
không cần bố trí lại. **Vòng lặp mới nhất này CHƯA được người dùng xác nhận
trực tiếp** — cần xem lại trước khi coi là hoàn tất.

## 5. Đánh giá tổng thể

- **Rule Engine (Phase 1)**: đúng trong sai số làm tròn hợp lý (<2%) cho mọi
  đại lượng verify được đối chiếu trực tiếp với sách; 1 lệch có giải trình rõ
  (giải pháp thay thế cho công thức không công bố đầy đủ).
- **Input Adapter, Drawing, Orchestrator**: đúng theo test tự động; đã chạy
  thật (AutoCAD COM, OpenAI API) chứ không chỉ dừng ở giả lập.
- **Giá trị phương pháp luận đáng chú ý cho phần bảo vệ đồ án**: tổng cộng
  **19 lỗi thật** phát hiện trong toàn bộ quá trình (1 ở Rule Engine, 8 ở
  Agent điều phối, 1 ở Input Adapter, 2 ở webapp/tầng ghép nối, 3 ở AutoCAD
  Tool, 4 ở quy cách bố trí bản vẽ mặt đứng khung — phát hiện qua phản hồi
  trực tiếp nhiều vòng của người dùng khi xem bản vẽ thật) — **KHÔNG có lỗi
  nào** trong số này lộ
  ra qua unit test viết trước; tất cả đều lộ qua chạy thật (AutoCAD thật, LLM
  thật) hoặc qua người có chuyên môn xem trực tiếp bản vẽ (lỗi bo góc cốt
  đai). Điều này cho thấy giới hạn thật sự của kiểm thử tự động đơn thuần —
  cả về logic (unit test chỉ đúng với đúng những gì người viết test hình
  dung trước) lẫn về chất lượng thể hiện trực quan (không phần mềm nào tự
  đánh giá "bản vẽ có đúng quy ước kỹ thuật không") — và khẳng định giá trị
  của vòng lặp "chạy thật/xem thật → phát hiện → sửa → chạy lại xác nhận" mà
  kiến trúc 4 vòng lặp của đồ án hướng tới.

## 6. Hạn chế còn tồn đọng (chưa khắc phục)

1. ~~Mặt đứng khung nhận toạ độ tường minh, chưa tự suy từ `BoDuLieuKhung`~~
   — **ĐÃ KHẮC PHỤC MỘT PHẦN**: `PhanTuKhung` giờ có 2 trường tuỳ chọn
   `truc`/`tang`, và `src/orchestrator/khung_ve.py` tự lắp mặt đứng khung từ
   đó (toạ độ đều nhau nếu không có toạ độ thật — xem mục 4). Mặt bằng kết
   cấu sàn, khung tên, 4 hình phối cảnh nút khung VẪN nhận tham số tường
   minh, chưa làm tương tự.
2. **4 hình phối cảnh nút khung là hình MINH HOẠ SƠ ĐỒ** (khối cột/dầm giao
   nhau + vị trí đại diện thép dọc/đai qua phép chiếu trục đo) — CHƯA vẽ chi
   tiết uốn móc/neo thật của từng thanh như chi tiết thi công đầy đủ.
3. ~~Chưa kiểm thử với "khung trục 5" đầy đủ (12 cột + 8 dầm)/chưa có file
   ETABS thật~~ — **ĐÃ KHẮC PHỤC CẢ HAI**: `tests/fixtures/khung_truc5_day_
   du.csv` + `scripts/ve_khung_truc5_day_du.py` chạy liền mạch đủ 12 cột + 8
   dầm × 3 vị trí (36 vị trí, nội lực/As lấy đúng Bảng 24-27 thuyết minh gốc
   — xem mục 4); VÀ `src/input_adapter/etabs_reader.py` đọc trực tiếp báo
   cáo ETABS THẬT (`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx`, 15+ bảng quan
   hệ, JOIN qua Frame ID) — chạy qua webapp: **36/36 đạt, 0 câu hỏi cần hỏi**
   (xem mục "Đọc trực tiếp báo cáo ETABS THẬT"). Vẫn còn 1 giới hạn nhỏ:
   `_kham_pha_danh_sach_yeu_cau` mới join được nội bộ 1 file ETABS chuẩn CSI
   — chưa thử với các biến thể xuất báo cáo khác (SAP2000, ETABS phiên bản
   cũ đặt tên bảng khác, hay file có sheet bị đổi tên tuỳ ý).
4. `chon_to_hop_thep_doc` (dầm) có thể chọn tổ hợp khác với lựa chọn thủ công
   của kỹ sư trong sách (vd ít thanh hơn nhưng đủ As) — đây là đặc điểm đã
   biết của quy tắc ưu tiên tự đặt ("ít thừa diện tích nhất"), không phải lỗi.
5. LLM không hoàn toàn tất định giữa các lần chạy (xem ví dụ cột 22 ở mục 4:
   8Ø25 vs 8Ø28 giữa 2 lần chạy) — Rule Engine luôn đảm bảo hợp lệ kỹ thuật,
   nhưng nghĩa là bản vẽ cuối cùng sinh ra không đảm bảo giống hệt nhau giữa
   các lần chạy cùng 1 input, chỉ đảm bảo cùng ĐÚNG.

## Phase 6 — Refactor sang kiến trúc 4-agent, 100% AutoCAD COM

Cập nhật sau khi thực hiện toàn bộ `docs/CHANGE_REQUESTS.md` (tách `orchestrator/`
thành 4 agent riêng, bỏ `ezdxf`/`backend_dxf.py`, thêm suy luận hình học, thêm
tool lắp ráp mặt đứng khung, sửa ràng buộc đường kính thép tối thiểu, sửa bảng
thống kê đủ 8 cột). Phần Phase 0-5 phía trên giữ nguyên làm hồ sơ lịch sử —
các con số/kết luận ở đó vẫn đúng cho những gì chúng mô tả.

**Trạng thái test tự động:** `pytest -q` (không cần AutoCAD/API key) —
**190/190 pass**. Tăng so với 133 (Phase 5) do thêm test cho: suy luận hình
học (`hinh_hoc.py`, 7 test), ràng buộc đường kính tối thiểu (`cot_doc.py`, 3
test), bảng thống kê 8 cột (`geometry.py`, 2 test), các hàm thuần của 4 agent
mới (`agents/*.py`, ~20 test), và các hàm đọc-lại-qua-COM trong
`verify_drawing.py` test bằng "Document COM giả" — duck-typing thuộc tính
`.ObjectName`/`.Layer`/`.TextString`/`.Coordinates`, KHÔNG cần AutoCAD thật
nhưng vẫn kiểm chứng đúng logic so sánh (21 test), trừ đi các test đã xoá
cùng `ezdxf`/`backend_dxf.py`/`tools.py` cũ (~28 test).

Cũng trong Phase 6: `webapp/` được viết lại hoàn toàn để gọi `pipeline.chay_toan_bo_khung`
(4 agent) qua 1 hàng đợi xử lý tuần tự (`webapp/cad_worker.py`, AutoCAD COM là
STA — không an toàn nếu nhiều thread cùng đụng vào) thay vì đường 1-agent cũ
(`tools.py`/`pipeline.HE_THONG_PROMPT`, đã xoá). Đồng thời phát hiện và sửa 1
lỗ hổng thật: cơ chế "chặn tinh_cot_dai khi dầm nguồn ETABS thật không có Q
thô" trước đây CHỈ tồn tại ở tầng webapp (`_chay_1_yeu_cau_co_log`) — sau khi
tách 4 agent, cơ chế này lẽ ra biến mất hoàn toàn (kể cả cho
`scripts/chay_pipeline_day_du.py`). Đã chuyển hẳn vào `rule_engine_agent.py`
(field `NguCanhRuleEngine.khong_co_Q`, do `pipeline.py` tự suy ra từ dữ liệu,
không cần webapp báo) — nay CẢ webapp lẫn CLI đều được bảo vệ như nhau.

**Việc KHÔNG tự chạy được trong phiên làm việc viết code này** (môi trường
không có AutoCAD đang mở/không xác nhận được đã cài): mọi bước cần AutoCAD
COM thật — `scripts/smoke_test_com.py`, `scripts/chay_pipeline_day_du.py`
(script canonical, thay thế mọi script demo cũ) — cần chính người dùng tự
chạy trên máy có AutoCAD để xác nhận cuối cùng theo đúng
`docs/HUONG_DAN_CHAY.md`. Các enum/hằng số COM dùng trong `backend_com.py`
(`AcSaveAsType`, `AcDimArrowheadType`) được TRA CỨU trực tiếp tài liệu
AutoCAD ActiveX Reference chính thức của Autodesk (không đoán theo trí nhớ),
nhưng bản thân lệnh gọi COM thực thi đúng hay không vẫn cần xác nhận bằng
cách chạy thật.

**Đã root-cause và sửa dứt điểm mục "Vấn đề đang mở" của `RULE_ENGINE_AGENT.md`
bản trước** (đường kính thép ra rất nhỏ 3Ø8/2Ø10): không phải do thiếu ràng
buộc kiểm tra sau khi chọn, mà do các hàm sinh tổ hợp (`sinh_va_loc_to_hop`,
`chon_to_hop_thep_chu_vi_cot`) hoàn toàn không có sàn đường kính — đã thêm
`DUONG_KINH_DOC_TOI_THIEU_MM=12.0` lọc ngay tại nguồn.
