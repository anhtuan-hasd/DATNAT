# Change Requests — lịch sử đưa code về kiến trúc đã chốt (4 agent, 100% AutoCAD)

Danh sách này liệt kê **chính xác từng thay đổi code** cần làm để đưa hệ thống từ kiến trúc cũ (1 agent
duy nhất, backend vẽ còn `ezdxf` ở nhiều chỗ) sang kiến trúc đã chốt mô tả trong
`docs/TONGQUAN_AI_AGENT.md` và `docs/agents/*.md`. Đánh số theo mức ưu tiên (1 = làm trước để các mục sau
khả thi). Cột "Trạng thái" cập nhật khi mục đó đã xong và đã kiểm chứng.

## Quyết định đã chốt (trước đây để ngỏ)

- **`webapp/`** (Flask, gọi thẳng `tools.py`/`pipeline.py` kiểu cũ): **viết lại** để chạy qua 4 agent mới,
  không xoá — xem mục 8 dưới đây.
- **`ezdxf`/`backend_dxf.py`**: **xoá hoàn toàn** khỏi repo (không giữ làm dev-tool). Mọi test/chạy liên
  quan tới vẽ từ nay cần máy có AutoCAD cài sẵn và đang mở.

## 1. Refactor `orchestrator/` thành 4 agent riêng (ưu tiên cao nhất)

**Trạng thái:** ✅ đã xong, đã kiểm chứng bằng test (`tests/test_agents_*.py`,
`tests/test_orchestrator_pipeline_integration.py`).

**File:** `src/orchestrator/agents/{input_adapter_agent,rule_engine_agent,drawing_agent,verification_agent}.py`,
`src/orchestrator/shared/{hop_dong_du_lieu,hoi_nguoi_dung_tool}.py`, `src/orchestrator/pipeline.py`.

Tách hệ thống prompt + tool thành 4 file riêng (mỗi agent 1 file), theo đúng phân nhóm:

| Agent | Tool |
| --- | --- |
| Input Adapter | `doc_va_do_schema`, `de_xuat_anh_xa`, `xac_nhan_anh_xa_voi_nguoi_dung`, `chuan_hoa_du_lieu`, `suy_luan_hinh_hoc` |
| Rule Engine | `tra_vat_lieu`, `tinh_lech_tam_cot`, `chon_thep_doc`, `tinh_cot_dai`, `tinh_neo_noi`, `tu_kiem_tra` |
| Drawing | `ve_mat_cat`, `lap_rap_mat_dung_khung`, `xuat_ban_ve` |
| Verification | `kiem_chung_ban_ve` |
| (dùng chung) | `hoi_nguoi_dung` |

`tools.py` (13 tool gộp 1 file) và `pipeline.py` bản cũ (1 system prompt cho 7 bước) đã bị xoá. `pipeline.py`
mới chỉ còn vai trò "dây dẫn" gọi 4 hàm `chay_<ten>_agent()` theo đúng thứ tự — không tự gọi LLM.
`BoDemVongLap` (`loops.py`, không đổi) dùng 1 instance riêng cho mỗi agent có vòng lặp nội bộ (Rule Engine:
đếm "tu_sua"; Drawing/Verification: đếm "kiem_chung_ve") — không dùng chung 1 instance cho cả 4 agent.

## 2. Bỏ `ezdxf`/`backend_dxf.py` khỏi pipeline VÀ bộ test

**Trạng thái:** ✅ đã xong. Các hàm COM-based mới trong `verify_drawing.py` đã
test bằng "Document COM giả" (`tests/test_drawing_verify_com.py`,
`tests/test_agents_verification.py`) — đúng logic so sánh, xác nhận cuối
cùng với AutoCAD thật vẫn cần người dùng tự chạy `scripts/smoke_test_com.py`.

- `backend_dxf.py`: **đã xoá**.
- `backend_com.py`: thêm `luu_file_dwg(doc, duong_dan_dwg)` (SaveAs qua COM).
- `verify_drawing.py`: bỏ `import ezdxf` + mọi hàm `*_dxf`, thay bằng đọc trực tiếp qua COM
  (`doc.ModelSpace`, `.ObjectName`, `.Layer`, `.TextString`, `.Coordinates`). Giữ nguyên 3 hàm dựa trên IR
  (không phụ thuộc backend nào): `hop_gioi_han_da_giac_ir`, `kiem_tra_mat_cat_ir`, `dem_thanh_thep_ir`.
- Bổ sung kiểm tra mở rộng (VERIFICATION_AGENT.md mục 2, trước đây chưa có): đếm cấu kiện theo layer
  OUTLINE, đếm vòng tròn ký hiệu trục (layer AXIS), kiểm tra nhãn thép đủ cả 3 vị trí/dầm, đếm đủ cột bảng
  thống kê.
- `requirements.txt`: bỏ dòng `ezdxf`.
- Script/test phụ thuộc `ezdxf`/`backend_dxf` (`scripts/demo_ve_phase3.py`,
  `scripts/demo_ve_mat_bang_va_chi_tiet.py`, `scripts/ve_khung_truc5_day_du.py`,
  `scripts/chay_lien_mach_khung.py`, `tests/test_drawing_backend_dxf.py`): **đã xoá**, thay bằng
  `scripts/chay_pipeline_day_du.py` (chạy `pipeline.chay_toan_bo_khung` end-to-end qua COM).

## 3. Thêm tool lắp ráp mặt đứng khung

**Trạng thái:** ✅ đã xong (`drawing_agent.lap_rap_mat_dung_khung`, hàm nội bộ
`_mo_ta_thep_gop` gộp nhãn bằng NỐI CHUỖI thay vì gán đè — hồi quy test ở
`tests/test_agents_drawing.py`).

**File:** `src/orchestrator/agents/drawing_agent.py` (tool `lap_rap_mat_dung_khung`, bọc
`geometry.ve_mat_dung_khung()` + `khung_ve.lap_rap_mat_dung_khung()` đã có, vẽ qua `backend_com` thay vì
`backend_dxf`). Khi gộp nhãn thép cho mặt đứng khung, PHẢI gộp đúng cả 3 vị trí của mỗi dầm (gối
trái/giữa nhịp/gối phải) thành 1 chuỗi nhãn — không ghi đè chỉ giữ vị trí cuối cùng (lỗi đã biết ở script
cũ `ve_khung_truc5_day_du.py`, nay đã xoá).

## 4. Sửa thiếu vòng tròn ký hiệu trục A/B/C

**Trạng thái:** ✅ đã xác nhận không phải lỗi ở `geometry.py`/`backend_com.py`
(cả 2 đều xử lý `bv.vong_tron` đúng — nghi vấn nằm ở script cũ đã lỗi thời,
xoá theo mục 2). Đã thêm `verify_drawing.dem_vong_tron_theo_layer_com` +
kiểm tra tương ứng trong `verification_agent._kiem_tra_mat_dung_khung`
("vòng tròn ký hiệu trục") để MỌI lần lắp ráp khung sau này đều tự phát hiện
lại nếu thiếu — không chỉ tin tưởng đã sửa 1 lần là xong.

## 5. Input Adapter — suy luận hình học (toạ độ trục, cao độ tầng) từ dữ liệu

**Trạng thái:** ✅ đã xong (`tests/test_input_adapter_hinh_hoc.py`, 7 test —
gồm cả trường hợp nhiều thành phần liên thông tách biệt). Với dữ liệu ETABS
thật, `toa_do_truc`/`cao_do_moc` lấy TRỰC TIẾP từ Grid Lines/Story
Definitions (chính xác hơn suy luận) — xem `etabs_reader.doc_etabs_thuc`,
không qua `hinh_hoc.py`.

**File:** `src/input_adapter/hinh_hoc.py` (mới). Suy luận `toa_do_truc`/`cao_do_moc` từ tên trục/tầng +
`chieu_dai` (nhịp/chiều cao đoạn) đã chuẩn hoá trong `PhanTuKhung`. Khi dữ liệu không đủ để suy luận chắc
chắn, trả về trạng thái "cần hỏi người dùng" (không tự bịa, không dùng lại giá trị mẫu của khung trục 5) —
Input Adapter Agent gọi `hoi_nguoi_dung` trong trường hợp đó qua tool `suy_luan_hinh_hoc`.

## 6. Rà soát ràng buộc đường kính thép tối thiểu (Rule Engine)

**Trạng thái:** ✅ đã xong (`tests/test_cot_doc.py` — 3 test hồi quy). Root cause: `sinh_va_loc_to_hop`/`chon_to_hop_thep_chu_vi_cot`
(`src/rule_engine/cot_doc.py`) không có ràng buộc đường kính tối thiểu — chấp nhận mọi giá trị trong
`duong_kinh_cho_phep` do người gọi truyền. Đã thêm hằng số `DUONG_KINH_DOC_TOI_THIEU_MM = 12.0` (mục 5.4.2
RULES "φ12–φ40" cho cột, áp dụng chung cho dầm theo thực hành cấu tạo) và lọc ngay trong 2 hàm sinh tổ hợp.

## 7. Sửa mâu thuẫn nội bộ trong `README.md`

**Trạng thái:** ✅ đã sửa — `README.md` viết lại toàn bộ, phản ánh đúng kiến trúc 4-agent hiện hành.

## 8. Viết lại `webapp/` cho kiến trúc 4-agent

**Trạng thái:** ✅ đã xong — xem `docs/BAOCAO_KIEMTHU.md` mục "Phase 6".

**Hiện trạng cũ:** `webapp/jobs.py` gọi thẳng `tools.tao_dispatch`/`pipeline.HE_THONG_PROMPT`/
`agent.chay_vong_lap_tool` (1 phiên, 13 tool cũ) và render ảnh xem trước bằng `ezdxf.addons.drawing` — cả
2 điều này không còn tồn tại sau mục 1 và 2.

**Đã làm:**
- `webapp/cad_worker.py` (mới): hàng đợi 1-thread (`queue.Queue` + 1 worker thread daemon) chạy TOÀN BỘ
  `pipeline.chay_toan_bo_khung` của mỗi job tuần tự — đơn giản hơn "chỉ serialize phần COM" (tách phần LLM
  khỏi phần COM giữa chừng 1 job phức tạp không cần thiết cho 1 công cụ nội bộ phục vụ 1 người dùng).
- `webapp/jobs.py`: viết lại hoàn toàn, ngắn hơn nhiều — gọi ĐÚNG 1 lần `pipeline.chay_toan_bo_khung(...,
  quan_sat=job.quan_sat)`, không tự dò sheet/tự ghép log/tự chặn tinh_cot_dai thủ công như bản cũ (các việc
  đó nay thuộc về `pipeline.py`/`rule_engine_agent.py`). Bỏ `_render_png` (ezdxf đã xoá) — phục vụ trực
  tiếp PDF đã xuất qua COM.
- `webapp/templates/job.html`: xem trước bằng `<iframe>` PDF + link tải DWG, thay cho gallery `<img>` PNG.
- Phát hiện + sửa 1 lỗ hổng thật khi rà lại: cơ chế "chặn `tinh_cot_dai` khi dầm nguồn ETABS không có Q
  thô" trước đây CHỈ ở tầng webapp (`_chay_1_yeu_cau_co_log`) — đã chuyển vào `rule_engine_agent.py`
  (`NguCanhRuleEngine.khong_co_Q`) để CẢ webapp lẫn CLI đều được bảo vệ.

## Quyết định còn mở

Không còn — 2 quyết định trước đây để ngỏ (webapp, ezdxf) đã chốt ở đầu file này.
