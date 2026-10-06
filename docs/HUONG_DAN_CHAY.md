# Hướng dẫn chạy & tự kiểm tra kết quả

Tài liệu này để BẠN tự chạy và tự đánh giá — không cần tin lời tôi nói, mọi
bước dưới đây đều cho ra kết quả bạn tự xem/đọc được. Chạy theo đúng thứ tự.

## 0. Chuẩn bị

```powershell
cd D:\DA
pip install -r requirements.txt
```

Cần có: Python, AutoCAD (đã xác nhận: AutoCAD 2024) cho các bước vẽ thật, và
OpenAI API key cho các bước chạy agent thật. Bước 1 KHÔNG cần AutoCAD/API key.

## Bước 1 — Chạy toàn bộ test tự động (không tốn phí, không cần AutoCAD/API key)

```powershell
pytest -q
```

**Kỳ vọng**: `190 passed`, không có `failed`/`error`. Đây là các phép kiểm
tra: đối chiếu số liệu tính tay (`docs/RULES_TCVN5574.md` mục 10), logic
hình học (IR — không cần AutoCAD), và các hàm đọc-lại-qua-COM
(`verify_drawing.py`) test bằng "Document COM giả" (duck-typing thuộc tính
`.ObjectName`/`.Layer`/`.TextString`/`.Coordinates` — không cần AutoCAD thật
nhưng vẫn kiểm chứng đúng logic so sánh).

Muốn xem CHI TIẾT test đối chiếu với sách (mục 10 RULES_TCVN5574.md — cột 22
và dầm 40-41):

```powershell
pytest tests/test_khung_truc3_kiem_chung.py -v
```

Muốn xem test đọc trực tiếp báo cáo ETABS THẬT (file mẫu chính thức):

```powershell
pytest tests/test_etabs_reader.py tests/test_agents_input_adapter.py -v
```

## Bước 2 — Vẽ thật lên AutoCAD (cần AutoCAD đang mở)

Mở AutoCAD trước (Windows Start → AutoCAD), đóng hết hộp thoại lần đầu chạy
(vd "Migrate custom settings"), rồi:

```powershell
python scripts/smoke_test_com.py
```

**Kỳ vọng**: in ra lần lượt "OK" cho từng bước (kết nối, tạo document, vẽ 1
mặt cắt, zoom, lưu DWG, xuất PDF) rồi "HOÀN TẤT". Quay sang cửa sổ AutoCAD sẽ
thấy 1 document mới có 1 mặt cắt dầm vừa vẽ (đường bao, cốt thép, cốt đai bo
tròn, kích thước với mũi tên gạch chéo kiểu kiến trúc). File DWG/PDF nằm
trong `output/smoke_test_com/`.

## Bước 3 — Chạy TOÀN TRÌNH 4-agent trên dữ liệu ETABS thật (tốn vài chục US cent)

Đặt API key — **không dán key vào chat với AI, đặt trực tiếp trên máy**.
Script tự nạp `OPENAI_API_KEY` từ file `.env` ở gốc dự án nếu có (qua
`python-dotenv`, giống `webapp/app.py`):

```
# D:\DA\.env
OPENAI_API_KEY=sk-proj-...key-thật-của-bạn...
```

Nếu chưa có `.env`, tạo file này (1 dòng như trên) hoặc đặt biến môi trường
trực tiếp trong phiên PowerShell đang chạy:

```powershell
$env:OPENAI_API_KEY = "sk-proj-...key-thật-của-bạn..."
```

Mở sẵn AutoCAD (như Bước 2), rồi:

```powershell
python scripts/chay_pipeline_day_du.py
```

Script này chạy `pipeline.chay_toan_bo_khung` — đúng 4 agent theo thứ tự
(Input Adapter → Rule Engine → Drawing → Verification) — trên
`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` (file ETABS thật, 12 cột + 8 dầm =
20 phần tử, 36 vị trí cần chọn thép).

**Kỳ vọng** (đọc log in ra màn hình):
1. Input Adapter Agent nhận diện đúng "báo cáo ETABS thật" (qua tool
   `doc_etabs_that`), đọc được 20 phần tử, `toa_do_truc`/`cao_do_moc` khớp
   đúng lưới trục/tầng thật — **không cần hỏi gì** (dữ liệu đã đủ).
2. Với từng phần tử: Rule Engine Agent tra vật liệu → chọn thép → tính cấu
   tạo → tự kiểm tra (`dat: true`) cho mọi vị trí.
3. Drawing Agent vẽ từng mặt cắt, Verification Agent xác nhận ngay từng mặt
   cắt (`dat: true`).
4. Sau khi hết 20 phần tử: Drawing Agent lắp ráp mặt đứng khung tổng thể +
   bảng thống kê (8 cột) + khung tên, xuất PDF/DWG; Verification Agent kiểm
   chứng tổng thể (đủ 12 cột + 8 dầm, đủ nhãn thép 3 vị trí/dầm, đủ vòng
   tròn ký hiệu trục, đủ bảng thống kê).
5. Cuối log: bảng trạng thái từng phần tử + đường dẫn
   `output/khung_truc5_day_du/KHUNG_TRUC5.pdf`/`.dwg`.

Lưu ý: LLM không hoàn toàn tất định — mỗi lần chạy có thể chọn đường kính
thép hơi khác nhau (vd cột ra 8Ø25 lần này, 8Ø28 lần khác). Điều quan trọng
cần kiểm tra là: dù chọn gì, mọi vị trí phải `dat: true` VÀ Verification
Agent phải báo `ĐẠT` cho bản vẽ tổng thể.

Nếu bất kỳ bước nào báo `False`/`loi` — đọc kỹ `vi_pham`/`loi` để hiểu, đây
KHÔNG hẳn là lỗi hệ thống (có thể model chưa self-correct đúng, xem
`so_lan_tu_sua_con_lai`/`so_lan_con_lai`).

## Bước 4 — Tự đọc lại số liệu, đối chiếu tay với sách

Mở `output/khung_truc5_day_du/KHUNG_TRUC5.pdf` (hoặc `.dwg` bằng AutoCAD), so
đường kính/số thanh thép hiện trên hình với số model in ra ở log (vd
"1Ø16+4Ø18") — phải khớp nhau tuyệt đối (đây chính là điều Verification Agent
đã tự kiểm tra, bạn kiểm tra lại lần nữa bằng mắt cho chắc). Đối chiếu As đã
chọn với Bảng 26/27 thuyết minh gốc — hệ thống TỰ CHỌN thép độc lập (không
copy đáp án sách) nên combo cụ thể có thể khác, miễn As thực ≥ As yêu cầu và
mọi điều kiện cấu tạo đạt thì KHÔNG phải lỗi.

## Bước 5 — Chạy qua giao diện WEB (tải Excel/ETABS lên, chat hỏi-đáp, xem PDF)

Cách chạy "liền mạch" đầy đủ nhất — 1 trang web local nối toàn bộ pipeline 4
agent: nhận file Excel/CSV/ETABS thật → tự động xử lý → nếu cần xác nhận sẽ
hiện hộp chat hỏi ngay trên trang, chờ bạn trả lời rồi chạy tiếp → xong thì
hiện PDF xem trước ngay trên trang + link tải DWG, không cần mở terminal.

```powershell
python webapp/app.py
```

(Server tự nạp `OPENAI_API_KEY` từ file `.env` ở gốc dự án nếu có; nếu chưa
tạo `.env`, đặt `$env:OPENAI_API_KEY = "sk-..."` trước khi chạy như Bước 3.)

Mở trình duyệt tại `http://127.0.0.1:5000`, chọn file (có thể dùng
`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` để thử ngay với dữ liệu ETABS
thật), bấm tải lên. Trang tự chuyển sang `/job/<id>` và tự làm mới mỗi ~1,2
giây. Khi thấy hộp câu hỏi hiện lên, trả lời rồi bấm gửi — tiến trình phía
sau đang bị CHẶN chờ đúng câu trả lời đó (không phải giả lập). Khi xong,
PDF bản vẽ khung tổng thể hiện ngay trên trang, kèm link tải DWG.

Lưu ý vận hành (Windows): server này chỉ chạy local, phục vụ 1 người dùng —
nhiều file tải lên cùng lúc sẽ tự XẾP HÀNG chạy lần lượt (`webapp/cad_worker.py`,
vì AutoCAD COM chỉ an toàn khi 1 thread đụng vào tại 1 thời điểm), không
chạy song song. Nếu cần khởi động lại server, đừng chỉ `pkill -f
"webapp/app.py"` — trên môi trường Windows/Git Bash lệnh này không đảm bảo
dừng hẳn tiến trình cũ; hãy kiểm tra `netstat -ano | grep ":5000"` rồi
`taskkill //F //PID <pid>` cho từng PID đang LISTEN trước khi chạy lại.

## Tổng kết: sau khi chạy xong 5 bước trên, bạn sẽ tự trả lời được

| Câu hỏi | Cách tự trả lời |
| --- | --- |
| Code có chạy được không? | Bước 1: `190 passed` |
| Số liệu tính có đúng sách không? | Bước 1 chi tiết: đọc test + so `docs/RULES_TCVN5574.md` mục 10 |
| Có vẽ được lên AutoCAD thật không? | Bước 2 |
| Đọc được file ETABS thật không? | Bước 1 (`test_etabs_reader.py`) + Bước 3 |
| 4 agent có tự chạy đúng quy trình, đúng ranh giới trách nhiệm không? | Bước 3: đọc log `[giai_đoạn] tên — N lượt gọi model` |
| Bản vẽ tổng thể có đúng quy ước (đủ cấu kiện, nhãn, vòng tròn trục, bảng thống kê) không? | Bước 3 (Verification Agent kiểm chứng tổng thể) + Bước 4 (tự nhìn) |
| Model tính thép/bản vẽ có nhất quán không? | Bước 4: đối chiếu tay |

Xem thêm `docs/BAOCAO_KIEMTHU.md` để biết đầy đủ các lỗi đã tìm ra & sửa
trong quá trình làm, và những gì CHƯA làm (mục "Hạn chế còn tồn đọng").
