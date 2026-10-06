# Đồ án: AI Agent thiết kế khung BTCT & sinh bản vẽ tự động

Hệ thống đọc file Excel kết quả tính As của ETABS, tự chọn cốt thép theo TCVN 5574:2018, và vẽ bản vẽ kỹ
thuật (mặt cắt dầm/cột, mặt đứng khung tổng thể, bảng thống kê thép, khung tên) **100% qua AutoCAD thật**
(COM Automation) — xuất PDF/DWG.

**Đọc theo thứ tự này để hiểu hệ thống:**

1. `docs/TONGQUAN_AI_AGENT.md` — kiến trúc tổng thể: 4 agent LLM riêng, luồng bàn giao dữ liệu.
2. `docs/agents/{INPUT_ADAPTER,RULE_ENGINE,DRAWING,VERIFICATION}_AGENT.md` — vai trò, quy trình, tool,
   hợp đồng dữ liệu, lỗi thật đã gặp của TỪNG agent.
3. `docs/RULES_TCVN5574.md` — nguồn công thức/quy tắc DUY NHẤT mà `src/rule_engine/` trích dẫn.
4. `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md` — quy ước ký hiệu/nét vẽ/bố trí thép mà `src/drawing/` tuân theo.
5. `docs/CHANGE_REQUESTS.md` — lịch sử các quyết định/thay đổi kiến trúc đã thực hiện (Phase 6).
6. `docs/HUONG_DAN_CHAY.md` — hướng dẫn tự chạy và tự kiểm chứng từng bước.

## Kiến trúc: 4 agent LLM riêng, mỗi agent 1 file

Không có 1 LLM điều phối duy nhất — hệ thống chia thành 4 phiên LLM độc lập, mỗi agent chỉ thấy đúng nhóm
tool thuộc phạm vi trách nhiệm của mình (`docs/TONGQUAN_AI_AGENT.md` mục 4):

| Agent | File | Vai trò |
| --- | --- | --- |
| Input Adapter | `src/orchestrator/agents/input_adapter_agent.py` | Đọc & chuẩn hoá Excel/CSV (kể cả báo cáo ETABS thật, đa bảng), suy luận toạ độ trục/cao độ tầng |
| Rule Engine | `src/orchestrator/agents/rule_engine_agent.py` | Chọn thép, tính cấu tạo đai/neo/nối, tự kiểm tra theo TCVN 5574:2018 |
| Drawing | `src/orchestrator/agents/drawing_agent.py` | Vẽ mặt cắt + lắp ráp mặt đứng khung + bảng thống kê + khung tên, xuất PDF/DWG — 100% AutoCAD COM |
| Verification | `src/orchestrator/agents/verification_agent.py` | Đọc lại bản vẽ qua COM để đối chiếu dữ liệu + quy ước bản vẽ mẫu |

`src/orchestrator/pipeline.py` là lớp điều phối cấp cao DUY NHẤT (`chay_toan_bo_khung`) — gọi 4 agent theo
đúng thứ tự, KHÔNG tự gọi LLM. `src/orchestrator/agent.py` (không đổi) là engine tool-calling chung dùng
lại bởi cả 4 agent (Protocol `NhaCungCapChat`, `OpenAIChatProvider` chính thức, `ClaudeChatProvider` thay
thế). `src/orchestrator/shared/` chứa những gì THẬT SỰ dùng chung (tool `hoi_nguoi_dung`, dataclass hợp
đồng dữ liệu giữa các agent, `PhienCAD` — tham chiếu AutoCAD COM sống dùng chung xuyên suốt 1 khung).

Nguyên tắc xuyên suốt: **LLM không bao giờ tính số** — mọi công thức/ngưỡng kỹ thuật nằm trong
`src/rule_engine/` và `src/drawing/`, agent chỉ quyết định gọi tool nào tiếp theo dựa trên kết quả tool
trước đó. Nhiều "chặn ở tầng code" (x/e cột tự tính lại, mu_max cố định, đường kính thép tối thiểu 12mm...)
là kết quả của các lỗi thật đã gặp khi để LLM tự đoán số liệu — xem "Lỗi thật đã từng gặp" trong từng file
`docs/agents/*.md`.

## Chạy test

```bash
pip install -r requirements.txt
pytest
```

190 test tự động pass, không cần AutoCAD/API key (chỉ đọc dữ liệu, tính toán, và test các hàm đọc-lại-qua-
COM bằng "Document COM giả" — duck-typing, không phải AutoCAD thật). Xem `docs/BAOCAO_KIEMTHU.md` mục
"Phase 6" cho chi tiết. Chạy `scripts/chay_pipeline_day_du.py` để kiểm chứng toàn trình với AutoCAD thật
(cần mở sẵn AutoCAD + `OPENAI_API_KEY`) — xem `docs/HUONG_DAN_CHAY.md`.

## Cấu trúc `src/rule_engine/`

| File | Nội dung | Mục RULES_TCVN5574.md |
| --- | --- | --- |
| `vat_lieu.py` | Bảng tra Rb/Rbt/Eb, Rs/Rsc/Rsw/Es, đường kính-diện tích, quy đổi thép nước ngoài | 1, 8 |
| `uon_nen.py` | ξR, ea/e0, Mu dầm chữ nhật/chữ T, cột lệch tâm lớn/bé, η, công thức đơn giản hoá | 2 |
| `cot_dai.py` | Điều kiện ép vỡ bụng, Qb/Qsw/qsw, φn, Ms/Msw, bước đai, cốt treo | 3, 5 |
| `cot_doc.py` | μmin/μmax, khoảng cách, chọn tổ hợp thép dọc cho dầm và cột (`chon_to_hop_thep_chu_vi_cot`), **đường kính thép dọc tối thiểu 12mm** (`DUONG_KINH_DOC_TOI_THIEU_MM`) | 4, 5.4.2 |
| `neo_noi.py` | Chiều dài neo/nối chồng, đường kính uốn | 6 |
| `nut_khung.py` | Bảng yêu cầu cấu tạo tại nút khung | 7 |
| `truong_hop_bien.py` | 7 nguyên tắc xử lý biên | 10.6 |
| `verify.py` | Tự kiểm tra tổng hợp cho 1 tiết diện đã chọn thép | 4-7 |

Ràng buộc xuyên suốt: không dùng giải thuật di truyền/metaheuristic/ngẫu nhiên; mọi ngưỡng số lấy đúng từ
`docs/RULES_TCVN5574.md` (trừ 2 ràng buộc đồ án tự thêm có ghi rõ nguồn: `MU_MAX_PHAN_TRAM`,
`DUONG_KINH_DOC_TOI_THIEU_MM`).

## Cấu trúc `src/input_adapter/`

| File | Nội dung |
| --- | --- |
| `models.py` | Schema chuẩn nội bộ: `BoDuLieuKhung` → `PhanTuKhung` → `DuLieuViTri`/`NoiLuc` |
| `heuristics.py` | Dò tên cột bằng token + so khớp mờ (không gọi mạng); dò đơn vị lực |
| `llm_mapping.py` | Fallback gọi LLM khi heuristic không đủ tin cậy — chỉ đề xuất tên cột, không tính số |
| `readers.py` | Đọc thô Excel (nhiều sheet)/CSV, lọc sheet không liên quan — đường "1 sheet phẳng" |
| `etabs_reader.py` | Đọc trực tiếp báo cáo ETABS THẬT (đa bảng quan hệ: Grid Lines, Joint Coordinates, Connectivity - Frame...), JOIN qua Frame ID — trả về CẢ `toa_do_truc`/`cao_do_moc` chính xác từ Grid Lines/Story Definitions |
| `adapter.py` | Điều phối đường "1 sheet phẳng": heuristic → (tuỳ chọn) LLM → xác nhận người dùng → chuẩn hoá |
| `hinh_hoc.py` | Suy luận `toa_do_truc`/`cao_do_moc` từ `truc`/`tang`/`chieu_dai` đã chuẩn hoá — dùng khi nguồn KHÔNG có lưới trục tường minh (đường "1 sheet phẳng") |

Input Adapter Agent thử `etabs_reader` (báo cáo ETABS thật) TRƯỚC, chỉ rẽ sang đường "1 sheet phẳng" +
`hinh_hoc.py` nếu file không phải định dạng đó — xem `docs/agents/INPUT_ADAPTER_AGENT.md`.

## Cấu trúc `src/drawing/`

| File | Nội dung |
| --- | --- |
| `layers.py` | Khai báo layer/nét theo mục 10.7.2 (10 layer, mỗi layer 1 chức năng) |
| `geometry.py` | IR độc lập backend: mặt cắt dầm/cột, bảng thống kê thép (8 cột, mục 3.9), khung tên, mặt đứng khung, mặt bằng kết cấu sàn, hình phối cảnh 3D nút khung |
| `backend_com.py` | Backend DUY NHẤT — vẽ qua AutoCAD COM (`pywin32`): `ve_vao_doc`, `xuat_pdf`, `luu_file_dwg` |
| `verify_drawing.py` | Đọc lại IR (trước khi vẽ) VÀ đọc trực tiếp qua AutoCAD COM (sau khi vẽ) để đối chiếu — không còn phụ thuộc `ezdxf` |

`ezdxf`/`backend_dxf.py` đã bị loại bỏ hoàn toàn khỏi repo (xem `docs/CHANGE_REQUESTS.md` mục 2) — mọi
test/chạy liên quan tới vẽ THẬT đều cần AutoCAD cài sẵn và đang mở; các test logic (không đụng AutoCAD)
dùng kỹ thuật "Document COM giả" (duck-typing) để vẫn chạy nhanh, tự động, không cần AutoCAD.

## Cấu trúc `src/orchestrator/`

```
src/orchestrator/
  agent.py                    # engine tool-calling chung (không đổi giữa 4 agent)
  loops.py                    # BoDemVongLap — giới hạn CỨNG cho vòng lặp tự sửa/kiểm chứng
  khung_ve.py                 # lắp ráp mặt đứng khung từ PhanTuKhung + toạ độ — dùng bởi drawing_agent.py
  pipeline.py                 # chay_toan_bo_khung() — điều phối cấp cao, gọi 4 agent theo thứ tự
  shared/
    hop_dong_du_lieu.py       # dataclass hợp đồng dữ liệu giữa các agent (khớp docs/agents/*.md)
    hoi_nguoi_dung_tool.py    # tool hoi_nguoi_dung DÙNG CHUNG
    phien_cad.py              # PhienCAD — tham chiếu AutoCAD COM sống, dùng chung xuyên suốt 1 khung
  agents/
    input_adapter_agent.py
    rule_engine_agent.py
    drawing_agent.py
    verification_agent.py
```

## `data/` — dữ liệu kiểm chứng

`data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx` — file ETABS thật (định dạng xuất chuẩn CSI, 15+ bảng quan hệ),
đóng vai trò input mẫu chính thức. Ground truth: Bảng 26 (thép cột, 12 phần tử) và Bảng 27 (thép dầm, 8
phần tử) trong thuyết minh gốc, khung trục 5.

## `webapp/`

Giao diện web nội bộ (tải Excel lên, chat hỏi-đáp khi cần xác nhận, xem bản vẽ PDF + tải DWG) — gọi qua
`pipeline.chay_toan_bo_khung` (4 agent), không còn đường 1-agent cũ. `webapp/cad_worker.py` là 1 hàng đợi
1-thread xử lý TUẦN TỰ từng job (AutoCAD COM là STA — không an toàn khi nhiều thread cùng đụng vào; khớp
đúng giới hạn "chỉ phục vụ 1 người dùng tại 1 thời điểm" webapp này đã có từ đầu). Chạy: `python
webapp/app.py`, mở `http://127.0.0.1:5000` — cần mở sẵn AutoCAD trước.
