# Nghiên cứu mô hình AI Agent cho bài toán thiết kế khung BTCT và sinh bản vẽ tự động

Tổng quan bài toán & phương pháp nghiên cứu · Đồ án tốt nghiệp CNTT · ĐH Kiến Trúc Hà Nội

> **Trạng thái kiến trúc:** đây là kiến trúc **hiện hành** (Phase 6 đã triển khai) — **4 agent LLM riêng
> biệt**, bàn giao kết quả theo từng phần tử khung; backend vẽ **100% AutoCAD COM Automation**, không dùng
> `ezdxf`/DXF ở bất kỳ đâu trong pipeline sản phẩm lẫn bộ test. Lịch sử quyết định kiến trúc và danh sách
> thay đổi code đã thực hiện để đạt được trạng thái này: xem `docs/CHANGE_REQUESTS.md`.

## 1. Đặt vấn đề

Thiết kế khung bê tông cốt thép (BTCT) toàn khối hiện nay trải qua ba công đoạn: (1) phân tích kết cấu (tải trọng → nội lực) bằng phần mềm chuyên dụng như ETABS, (2) tính toán và bố trí cốt thép theo tiêu chuẩn, (3) thể hiện kết quả thành bản vẽ kỹ thuật trên AutoCAD. Công đoạn (2) và (3) hiện vẫn phần lớn làm thủ công hoặc bán tự động, tốn nhiều thời gian và dễ sai sót khi khối lượng cấu kiện lớn.

Đồ án đặt câu hỏi: có thể xây dựng một **AI Agent** — một hệ thống có khả năng tự lập kế hoạch, gọi công cụ (tool-use) và tự kiểm tra kết quả — để tự động hoá trọn vẹn hai công đoạn này hay không, thay vì chỉ viết một script xử lý tuần tự cố định?

## 2. Phạm vi bài toán

**Đầu vào:** file Excel chứa kết quả tính As (diện tích cốt thép yêu cầu) đã được ETABS xuất ra cho từng phần tử khung (dầm, cột), kèm hình học tiết diện, mác vật liệu, tổ hợp tải trọng chi phối. Đầu vào không cố định một schema — có thể là nhiều dạng file Excel khác nhau tuỳ nguồn xuất. **Kích thước/bố trí hình học (toạ độ trục, cao độ tầng, nhịp, chiều cao cột...) cũng không cố định** — hệ thống tự suy ra từ chính file dữ liệu của mỗi công trình, không hard-code theo 1 công trình mẫu (xem mục 10.7.1 `RULES_TCVN5574.md`, mục 3.11 `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md`, và `src/input_adapter/hinh_hoc.py`).

**Đầu ra:** bản vẽ kỹ thuật (mặt cắt dầm/cột, mặt đứng khung tổng thể, bố trí cốt thép, bảng thống kê thép) vẽ **100% qua AutoCAD thật (COM Automation)**, xuất được ra PDF/DWG. Không dùng `ezdxf`/DXF làm backend cho sản phẩm cuối — kể cả khi chạy test.

**Ranh giới rõ ràng — Agent KHÔNG tự làm:**

- Phân tích kết cấu (tải trọng → nội lực): việc này ETABS đã thực hiện trước, agent chỉ nhận kết quả As yêu cầu làm đầu vào.
- Tính toán tối ưu hoá bằng thuật toán tìm kiếm mù (như Genetic Algorithm ở hướng làm cũ) — không còn phù hợp vì không gian lựa chọn thép là hữu hạn, có thể vét cạn.

**Hệ thống (4 agent) chịu trách nhiệm cho:**

- Đọc và chuẩn hoá dữ liệu từ file Excel có cấu trúc thay đổi, **và suy ra hình học tổng thể của công trình** (toạ độ trục, cao độ tầng) từ chính dữ liệu đó.
- Áp dụng đúng bộ điều kiện cấu tạo cốt thép theo TCVN 5574:2018 để chọn ra phương án thép cụ thể (đường kính, số thanh, bước đai, chiều dài neo/nối).
- Tự kiểm tra kết quả so với các ràng buộc, xử lý ngoại lệ (dữ liệu thiếu, vượt giới hạn cấu tạo).
- Điều phối công cụ AutoCAD (qua COM) để sinh bản vẽ hoàn chỉnh — cả mặt cắt từng cấu kiện lẫn mặt đứng khung tổng thể — và tự đọc lại để kiểm chứng.

## 3. Vì sao đây là một AI Agent, không chỉ là một script

**Nguyên tắc cốt lõi của phương pháp:** phần tính toán có công thức và ràng buộc rõ ràng (số liệu kỹ thuật) phải là **code xác định (deterministic)** — không giao cho LLM suy luận ra con số. Vai trò của "agent" nằm ở lớp **điều phối**: nhận diện dữ liệu đầu vào biến thiên, ra quyết định khi có nhiều phương án hợp lệ hoặc dữ liệu không chuẩn, gọi đúng công cụ theo đúng trình tự, và tự xác minh kết quả trước khi bàn giao.

Một pipeline cố định (đọc file A → tính theo công thức B → vẽ theo mẫu C) chỉ là tự động hoá thông thường. Nó trở thành *agent* khi hệ thống phải:

1. Tự nhận diện cấu trúc một file Excel không biết trước (không thể hard-code tên cột) **và hình học công trình không biết trước** (không thể hard-code toạ độ trục/cao độ theo 1 công trình mẫu).
2. Tự quyết định giữa nhiều phương án thép hợp lệ theo tiêu chí (kinh tế, thi công thuận tiện — mục 5.4.1 tài liệu hướng dẫn: không quá 3 loại đường kính/dầm).
3. Tự phát hiện và xử lý trường hợp bất thường (As vượt hàm lượng tối đa 3%, thiếu dữ liệu mác vật liệu…) — quyết định hỏi lại người dùng hoặc áp dụng giá trị mặc định hợp lý.
4. Tự kiểm tra bản vẽ sinh ra có khớp với dữ liệu đầu vào hay không trước khi hoàn tất.

## 4. Kiến trúc tổng thể — 4 agent LLM riêng, bàn giao theo từng phần tử

Hệ thống được chia thành **4 agent LLM độc lập**, mỗi agent phụ trách trọn vẹn 1 nhóm bước, nhận đầu vào từ agent trước và bàn giao đầu ra có cấu trúc cho agent sau. Ranh giới giữa các agent trùng với ranh giới các "lớp" đã có (Input Adapter / Rule Engine / AutoCAD Tool) — điểm khác so với thiết kế 1-agent trước đó là **mỗi lớp có 1 phiên LLM riêng ra quyết định cho lớp đó**, thay vì 1 LLM duy nhất phải nhớ toàn bộ 7 bước trong 1 phiên hội thoại tool-calling dài.

| Agent | Vai trò | Input nhận | Output bàn giao | File cài đặt |
| --- | --- | --- | --- | --- |
| **Input Adapter Agent** | Nhận diện & chuẩn hoá cột dữ liệu từ Excel bất kỳ về schema chuẩn nội bộ; suy ra toạ độ trục/cao độ tầng của công trình | Đường dẫn file Excel/CSV | `BoDuLieuKhungChuanHoa` (phan_tu[] + toa_do_truc + cao_do_moc) | `src/orchestrator/agents/input_adapter_agent.py` |
| **Rule Engine Agent** | Áp dụng điều kiện TCVN 5574:2018 để chọn thép, tính neo/nối/bước đai, tự sửa lỗi | 1 phần tử (dầm/cột) đã chuẩn hoá, cho từng vị trí | `PhuongAnThepPhanTu` — phương án thép + cấu tạo đã **đạt tự kiểm tra** | `src/orchestrator/agents/rule_engine_agent.py` |
| **Drawing Agent** | Vẽ mặt cắt từng vị trí VÀ lắp ráp mặt đứng khung tổng thể + bảng thống kê + khung tên — 100% qua AutoCAD COM | Phương án thép đã đạt của toàn bộ phần tử trong 1 khung | `KetQuaVeBanVe` — Document AutoCAD đã vẽ + file PDF/DWG | `src/orchestrator/agents/drawing_agent.py` |
| **Verification Agent** | Đọc lại bản vẽ AutoCAD (qua COM) để đối chiếu với dữ liệu đầu vào VÀ với quy ước bản vẽ mẫu | Document/file AutoCAD vừa vẽ | `KetQuaKiemChung` — đạt/không đạt + danh sách vi phạm cụ thể | `src/orchestrator/agents/verification_agent.py` |

Cả 4 agent đều có thể gọi `hoi_nguoi_dung` khi cần xác nhận hoặc khi hết số lần thử cho phép — tool dùng chung, định nghĩa 1 lần duy nhất ở `src/orchestrator/shared/hoi_nguoi_dung_tool.py`, không lặp lại ở mỗi file agent.

`src/orchestrator/pipeline.py` là lớp điều phối cấp cao (`chay_toan_bo_khung`) — gọi 4 hàm `chay_<ten>_agent()` theo đúng thứ tự mục 5 dưới đây, chuyển tiếp đúng cấu trúc dữ liệu (`src/orchestrator/shared/hop_dong_du_lieu.py`) giữa các agent. Bản thân `pipeline.py` **không gọi LLM trực tiếp** — nó chỉ là "dây dẫn" giữa 4 phiên LLM.

Chi tiết vai trò, quy trình từng bước, quy tắc dùng tool và các lỗi thật đã từng gặp (để agent không lặp lại) được viết đầy đủ trong 4 file riêng dưới `docs/agents/`:

- `docs/agents/INPUT_ADAPTER_AGENT.md`
- `docs/agents/RULE_ENGINE_AGENT.md`
- `docs/agents/DRAWING_AGENT.md`
- `docs/agents/VERIFICATION_AGENT.md`

## 5. Luồng xử lý & bàn giao giữa các agent

**Vòng lặp ngoài cùng (per phần tử khung)** lặp qua **cả chuỗi 4 agent** cho mỗi phần tử, không chỉ lặp trong 1 phiên LLM duy nhất:

1. **Input Adapter Agent** chạy 1 lần cho cả file (không lặp lại theo phần tử) — đọc Excel, xác nhận ánh xạ với người dùng nếu cần, chuẩn hoá toàn bộ `BoDuLieuKhung`, suy ra `toa_do_truc`/`cao_do_moc`. Bàn giao **toàn bộ** danh sách phần tử đã chuẩn hoá cho bước sau.
2. Với **từng phần tử** trong danh sách: **Rule Engine Agent** chạy cho từng vị trí cần As của phần tử đó (dầm: gối trái/giữa nhịp/gối phải; cột: 1 vị trí đại diện) — tra vật liệu, chọn thép, tính cấu tạo, tự kiểm tra (vòng lặp tự sửa nội bộ agent này, giới hạn số lần thử qua 1 `BoDemVongLap` RIÊNG cho phần tử đó). Chỉ bàn giao sang Drawing Agent khi **tất cả vị trí của phần tử đã đạt tự kiểm tra**.
3. Với **mỗi vị trí vừa đạt**: **Drawing Agent** vẽ 1 mặt cắt, rồi **Verification Agent** kiểm chứng NGAY (không đợi vẽ hết cả khung) — nếu lệch, quay lại Drawing Agent với vi phạm cụ thể (vòng lặp riêng, giới hạn số lần thử).
4. Sau khi **toàn bộ phần tử trong 1 khung** đã qua bước 2-3: **Drawing Agent** lắp ráp mặt đứng khung tổng thể + bảng thống kê + khung tên, xuất PDF/DWG. **Verification Agent** kiểm chứng lần cuối trên bản vẽ tổng thể (đối chiếu mục 10.7 `RULES_TCVN5574.md` + `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md`: số cấu kiện, đủ nhãn thép, vòng tròn ký hiệu trục, số mặt cắt, bảng thống kê).

| Vòng lặp | Nằm trong agent nào | Điều kiện dừng |
| --- | --- | --- |
| Vòng lặp ngoài cùng (per phần tử) | Điều phối bởi `pipeline.chay_toan_bo_khung` giữa Rule Engine Agent → Drawing Agent → Verification Agent | Hết danh sách phần tử (dầm/cột) |
| Vòng lặp xác nhận dữ liệu | Input Adapter Agent | Người dùng xác nhận mapping cột/hình học |
| Vòng lặp tự sửa (self-correction) | Rule Engine Agent (tự lặp nội bộ) | Qua được tự kiểm tra, hoặc hết số lần thử → hỏi người dùng |
| Vòng lặp kiểm chứng bản vẽ | Verification Agent → (nếu lệch) → Drawing Agent | Bản vẽ khớp dữ liệu + quy ước mẫu, hoặc hết số lần thử → hỏi người dùng |

Nói cách khác: mỗi agent vẫn là 1 "bộ não" LLM ra quyết định trong phạm vi của nó (gọi tool nào, có cần hỏi người dùng không), nhưng **ranh giới quyết định được tách theo agent thay vì gộp chung 1 phiên** — mỗi agent có system prompt ngắn, tập trung, chỉ thấy đúng nhóm tool của mình.

## 6. Bộ điều kiện cấu tạo áp dụng (TCVN 5574:2018)

| Nội dung | Điều kiện | Nguồn |
| --- | --- | --- |
| Hàm lượng thép dọc tối thiểu | μ ≥ 0,1% (uốn, nén lệch tâm thường); μ ≥ 0,25% khi độ mảnh L₀/i ≥ 87 | 10.3.3.1 |
| Số thanh tối thiểu trong dầm | ≥ 2 thanh khi b > 150 mm; kéo vào gối ≥ 1/2 As nhịp và ≥ 2 thanh | 10.3.3.4–5 |
| Lớp bê tông bảo vệ | 20 mm (trong nhà, độ ẩm thường) / 25 mm (ẩm cao) / 30 mm (ngoài trời) / 40 mm (trong đất); ≥ đường kính thanh, ≥ 10 mm | Bảng 19 |
| Khoảng cách thông thủy tối thiểu | 25 mm (1–2 lớp dưới) / 30 mm (lớp trên) / 50 mm (từ lớp 3) | 10.3.2 |
| Khoảng cách tối đa giữa các thanh | Dầm/bản: 200 mm (h≤150) hoặc min(1,5h; 400 mm); Cột: 400 mm / 500 mm theo phương | 10.3.3.3 |
| Đường kính cốt đai | ≥ 0,25×d_dọc,max và ≥ 6 mm | 10.3.4.2 |
| Bước đai (chịu cắt theo tính toán) | ≤ 0,5h₀ và ≤ 300 mm | 10.3.4.3 |
| Bước đai (không cần tính toán) | ≤ 0,75h₀ và ≤ 500 mm | 10.3.4.3 |
| Bước đai cột | ≤ min(15d; 500 mm); ≤ min(10d; 300 mm) nếu μ > 1,5% hoặc trong đoạn nối | 10.3.4.4, mục 5.4.2 |
| Đường kính thép cột | φ12 – φ40 | Mục 5.4.2 |
| **Đường kính thép dọc tối thiểu (dầm và cột)** | **≥ 12 mm — ràng buộc thực hành đồ án tự thêm (mục 5.4.2 chỉ nêu cho cột, áp dụng chung để tránh cấu hình phi thực tế)** | `cot_doc.DUONG_KINH_DOC_TOI_THIEU_MM` |
| Chiều dài neo cơ sở | L₀,an = Rs·As / (Rbond·us) | Công thức 255–256 |
| Chiều dài nối chồng | L_lap = α·L₀,an, tối thiểu 0,4αL₀,an, 20d, 250 mm | 10.3.6.2, CT 259 |
| Đường kính uốn tối thiểu | 5d (d<20mm) / 8d (d≥20mm) — thép có gân | 10.3.7 |
| Số loại đường kính trong 1 dầm | Khuyến nghị không quá 3 loại; không chênh lệch 1 mm giữa các loại | Mục 5.4.1 |

## 7. Công nghệ

- **Xử lý dữ liệu:** Python, `pandas`/`openpyxl` để đọc/chuẩn hoá Excel.
- **Rule Engine:** module Python thuần (`src/rule_engine/`), có bộ test đối chiếu với số liệu tính tay trong thuyết minh (Bảng 26, 27) làm ground truth.
- **Lớp agent điều phối:** **4 phiên LLM riêng**, mỗi phiên dùng tool-calling — OpenAI API (Chat Completions, function calling) — cho đúng nhóm tool của agent đó (xem mục 4). `ClaudeChatProvider` (`src/orchestrator/agent.py`) vẫn giữ trong code như cài đặt thay thế cùng Protocol, không phải lựa chọn chính thức.
- **Vẽ AutoCAD:** **100% qua `src/drawing/backend_com.py`** (COM Automation, `pywin32`) — backend DUY NHẤT cho pipeline sản phẩm lẫn test. `ezdxf`/`backend_dxf.py` đã bị loại bỏ hoàn toàn khỏi repo (xem `docs/CHANGE_REQUESTS.md` mục 2).

## 8. Dữ liệu kiểm chứng (ground truth)

Dữ liệu kiểm chứng dùng để test Rule Engine là **kết quả tính tay** trong thuyết minh: Bảng 26 (thống kê thép cột, 12 phần tử) và Bảng 27 (thống kê thép dầm, 8 phần tử) của khung trục 5. File Excel định dạng ETABS thật `data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` đóng vai trò input mẫu cho toàn bộ pipeline (đọc qua `src/input_adapter/etabs_reader.py`), chạy end-to-end bằng `scripts/chay_pipeline_day_du.py`.

## 9. Trạng thái triển khai

Toàn bộ mục 1-8 ở trên đã được triển khai (Phase 0-6). Xem `docs/CHANGE_REQUESTS.md` cho lịch sử từng thay đổi code cụ thể, và `docs/BAOCAO_KIEMTHU.md` cho kết quả kiểm thử.
