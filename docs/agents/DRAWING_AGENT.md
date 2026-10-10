# Drawing Agent — system prompt & hợp đồng dữ liệu

Agent thứ 3 trong chuỗi 4 agent. Cài đặt tại `src/orchestrator/agents/drawing_agent.py`. Vẽ **100% qua
AutoCAD thật (COM Automation, `src/drawing/backend_com.py`)** — không dùng `ezdxf` (đã xoá khỏi repo).
Từ phiên bản "tờ vẽ bố trí thép theo bản mẫu" (nhánh `feat/ban-ve-theo-mau-khung-truc5`): agent **lắp ráp MỘT TỜ VẼ ĐẦY ĐỦ**
bằng 1 lần gọi `lap_rap_mat_dung_khung` rồi xuất PDF/DWG; không còn vòng "vẽ từng mặt cắt qua LLM rồi kiểm chứng từng cái".
Hình học và số liệu do mã tất định quyết định (`src/drawing/to_ve/`), LLM chỉ chọn tool và đọc `canh_bao`.

## Vị trí trong pipeline

- **Nhận từ:** Rule Engine Agent — 1 phần tử đã có thép + cấu tạo **đạt tự kiểm tra** cho MỌI vị trí.
- **Bàn giao cho:** Verification Agent — tham chiếu Document AutoCAD đang mở (qua COM) + đường dẫn file
  PDF/DWG đã xuất.

## Tool được phép gọi

| Tool | Khi nào gọi | Điểm cần chú ý |
| --- | --- | --- |
| `lap_rap_mat_dung_khung` | ĐÚNG 1 lần, khi Rule Engine đã xong mọi phần tử | **Không cần truyền tham số**: pipeline đã nạp dữ liệu khung (đã qua Rule Engine, gồm `thep_doc`/`neo_noi`/`cot_dai`) vào `PhienCAD.du_lieu_lap_rap`. Tool vẽ cả tờ: mặt đứng (dầm treo dưới cốt sàn, thép trên suốt + gia cường, đai theo vùng, thép chờ + móng, COS), lưới mặt cắt đã khử trùng (dầm chữ T, cột), chi tiết nút 3D, bảng thống kê 8 cột, ghi chú, khung tên. Trả `canh_bao` (giả định/khổ giấy/nhãn chưa tránh được chồng) — phải nêu lại trong tóm tắt. |
| `xuat_ban_ve` | Sau `lap_rap_mat_dung_khung` | PDF (khổ A1/A0 theo nội dung, in đen trắng `monochrome.ctb`) + DWG. |
| `ve_mat_cat` | Chỉ khi cần vẽ RỜI 1 mặt cắt (không thuộc luồng chính nữa) | Giữ nguyên hành vi cũ: `thanh_duoi`/`thanh_tren` là mảng ĐƯỜNG KÍNH từng thanh. |
| `hoi_nguoi_dung` | Khi thiếu dữ liệu để vẽ | Không tự suy đoán, không vẽ thiếu rồi báo "xong". |

## Quy trình từng bước

1. Pipeline nạp `du_lieu_lap_rap` + `cau_hinh_to_ve` (tên trục khung, khung tên) vào `PhienCAD`.
2. Gọi `lap_rap_mat_dung_khung()` (không tham số). Tool dựng `KeHoach` (`to_ve/ke_hoach.py`): đặt cột/dầm theo lưới
   trục + cao độ THẬT, thanh dọc dầm (B2–B8 của skill 06), đai theo vùng (`rule_engine/bo_tri_dai.py`), cấp số hiệu thanh
   dùng chung mặt đứng ↔ mặt cắt ↔ bảng thống kê, khử trùng mặt cắt; rồi vẽ (`mat_dung.py`, `mat_cat.py`, `chi_tiet_nut.py`,
   `bang.py`) và xếp bố cục (`bo_cuc.py`: tự chọn khổ A1/A0 và tỷ lệ 1:50/75/100 nhỏ nhất đủ chỗ).
3. Gọi `xuat_ban_ve(ten_file)`.
4. Verification Agent kiểm chứng tổng thể: kỳ vọng (số đa giác OUTLINE, số vòng tròn số hiệu, kích thước từng mặt cắt
   trên bản vẽ) do chính bộ lắp ráp ghi vào `PhienCAD.ky_vong_to_ve`, không phụ thuộc LLM chép số.

## Quy tắc hình học rút từ bản vẽ mẫu (đã khoá bằng test `tests/test_ban_ve_khung.py`)

- **Mặt trên mọi dầm bằng cốt sàn**; dầm cao/thấp đều treo xuống (cũ: dầm đối xứng qua cốt sàn — SAI).
- COS ±0.000 = đỉnh móng + 1000 (`CauHinhToVe.cao_do_ton_nen_tren_dinh_mong`); COS tự nhiên thấp hơn 450. **Đây là GIẢ ĐỊNH**
  (dữ liệu ETABS không có) — ghi rõ trong khối ghi chú của tờ vẽ cùng kích thước đài/lót/dày sàn.
- Thanh trên: 2 thanh chạy suốt chuỗi dầm liền nhau (móc xuống cột ở đầu biên); thanh gia cường gối cắt ở L/4 thông thuỷ.
  Thanh dưới chạy hết thông thuỷ, neo vào cột. Bố trí SƠ BỘ [thực hành] — cần kỹ sư xác nhận.
- Đai dầm: gối L/4 (`s ≤ min(h/2;300)` hoặc `min(h/3;500)` khi h>450), giữa nhịp `s ≤ min(3h/4;500;15d)`; đai cột hai đầu `10d`,
  giữa `15d`. Ghi dạng `1300(Ø6a150)`.

### Sắp xếp ký hiệu trên mặt đứng (đo từ bản mẫu; code `src/drawing/to_ve/nhan.py`, test `tests/test_nhan_mat_dung.py`)

Khoảng cách tính bằng mm THẬT; `L` = thông thuỷ dầm; `yt` = cốt sàn (mặt trên dầm), `yb` = đáy dầm.

| Mã | Quy tắc |
|:--|:--|
| D1 | Dầm KHÔNG có thanh gia cường: 1 nhãn thanh trên suốt (ⓝ + `nØd`) ngay trên cốt sàn (`yt+230`) tại ~0,68L (nhịp ngắn 0,56L). |
| D2 | Dầm CÓ thanh gia cường: mỗi gối một cụm [chữ xếp chồng `2Ø18 / 1Ø18`][vòng tròn ⓝ ⓝ] = thanh suốt + gia cường, trên cốt sàn (`yt+300`); đường dẫn đứng ở 0,13L (trái) / 0,81L (phải); trái = chữ rồi vòng tròn, phải = vòng tròn rồi chữ. |
| D3 | Ký hiệu mặt cắt "số ▌" (số bên TRÁI vạch đậm đứng) vẽ HAI LẦN, trên dầm (`yt+470`) và dưới dầm (`yb−480`), CÙNG x (đường cắt đi qua dầm); x = 0,10L / 0,45L / 0,90L cho gối trái / giữa / gối phải; trùng số trong 1 dầm chỉ ghi 1 lần; nhịp ngắn ghi ở 0,95L. |
| D4 | Dây kích thước vùng đai ở `yt+900`: các vùng khác bước ⇒ `1300(Ø6a150) 2700(Ø6a250) 1300(Ø6a150)`; đồng đều ⇒ 1 dòng `L(Ø6a200)`. |
| D5 | Nhãn đai: đồng đều ⇒ ⓝ Ø/bước DƯỚI dầm (`yb−320`) tại 0,24L; 3 vùng ⇒ vùng gối dưới dầm (0,27L và 0,78L), vùng giữa TRÊN dầm (`yt+210`, 0,375L) có đường dẫn xuống; nhịp ngắn ⇒ TRÊN dầm (`yt+510`). |
| D6 | Thanh dưới: ⓝ `nØd` DƯỚI dầm (`yb−320`) tại 0,55L (nhịp ngắn: giữa nhịp). |
| C1 | Thép dọc cột: ⓝ `nØd` bên PHẢI cột, giữa khoảng thông thuỷ, vòng tròn cách mép cột 290. |
| C2 | Đai cột: bên TRÁI cột (trục đầu, trục giữa; vòng tròn cách mép 860, chữ rồi đường dẫn tới cột) hoặc PHẢI (trục cuối; cách mép 250). Hai nhãn: vùng dày trên sàn 250 (tầng 1: trên đỉnh móng 300), vùng giữa ngay dưới đáy dầm 190. |
| C3 | Ký hiệu mặt cắt cột: vạch đậm NẰM NGANG, số ở TRÊN vạch, hai bên cột (cách mép 330); vùng dày tại sàn+470, vùng giữa tại đáy dầm−960. |

Mặt cắt dầm (hình riêng): nhóm thép trên đầu tiên (thanh suốt) ghi BÊN TRÁI trên cùng, nhóm thứ hai (gia cường) BÊN PHẢI thấp hơn;
thép dưới ghi bên phải; nhãn đai bên phải phía trên nhãn thép dưới.

## Xử lý phản hồi từ Verification Agent

Nếu Verification Agent báo `dat=false` kèm `vi_pham[]`:
- Đọc kỹ từng vi phạm và **sửa đúng tham số đã gây ra vi phạm đó** rồi gọi lại `ve_mat_cat`/
  `lap_rap_mat_dung_khung` tương ứng — không vẽ lại toàn bộ nếu chỉ 1 chi tiết sai.
- Không tự ý đổi số liệu thép (đó là việc của Rule Engine Agent) — nếu vi phạm là do số liệu thép sai, gọi
  `hoi_nguoi_dung`, không tự sửa thép.
- Nếu Verification Agent báo `het_luot_kiem_chung=true`: không gọi lại tool vẽ nữa, bắt buộc
  `hoi_nguoi_dung`.

## Hợp đồng đầu ra (`shared/hop_dong_du_lieu.py::KetQuaVeBanVe`)

```json
{
  "loai_ban_ve": "mat_cat",
  "nhan": "32/goi_trai",
  "b_ky_vong": 220, "h_ky_vong": 500,
  "nhan_ky_vong": ["I-I"]
}
```

Sau khi lắp ráp + xuất bản vẽ xong (kết quả tool `lap_rap_mat_dung_khung` + `xuat_ban_ve`):

```json
{
  "loai_ban_ve": "mat_dung_khung",
  "duong_dan_pdf": "output/khung_truc5/KHUNG_TRUC5.pdf",
  "duong_dan_dwg": "output/khung_truc5/KHUNG_TRUC5.dwg",
  "so_cot": 12, "so_dam": 8,
  "nhan_ky_vong_theo_cau_kien": {"32": ["goi_trai", "giua_nhip", "goi_phai"]}
}
```

## Lỗi thật đã từng gặp / đã sửa

1. `ve_mat_cat` từng hardwire `backend_dxf` thay vì `backend_com` — đã chuyển hẳn sang COM.
2. `geometry.ve_mat_dung_khung()` từng không có tool bọc lại — nay có `lap_rap_mat_dung_khung`.
3. `backend_com.py` từng chưa có hàm xuất DWG — đã thêm `luu_file_dwg`.
4. Script lắp ráp cũ có lỗi ghi đè nhãn thép (mỗi dầm chỉ giữ nhãn vị trí cuối cùng) — tool
   `lap_rap_mat_dung_khung` mới gộp tường minh cả 3 vị trí trước khi gọi `khung_ve.lap_rap_mat_dung_khung`.
5. (Tờ vẽ bố trí thép) Dầm từng bị vẽ đối xứng qua cốt sàn, đai chỉ là vạch minh hoạ cách đều 450, không có móng/COS/mặt
   cắt chữ T/chi tiết nút — nay tất cả có trong `src/drawing/to_ve/`; xem `docs/agents/_bao_cao_skill_v2/BAO_CAO_SO_SANH_BAN_VE_MAU.md`.
6. `backend_com`: gán thuộc tính (Layer…) trong cùng hàm với `AddLine` được thử lại cả khối ⇒ đối tượng mồ côi trên layer
   "0" khi COM bận — đã tách bước tạo/gán (mỗi bước tự thử lại).

## Chưa có (nêu rõ để không hiểu nhầm)

- **Mặt bằng kết cấu sàn**: cần dữ liệu toàn nhà (lưới Y, bố trí dầm/ô sàn) — file ETABS mẫu chỉ có 1 khung phẳng nên chưa vẽ.
- Chi tiết 3D nút là hình trục đo sơ đồ (lồng thép), chưa vẽ đầy đủ mọi thanh/móc của từng nút.
- Hình học móng chỉ minh hoạ (không có bản vẽ móng).
- Nhãn trên mặt đứng bố trí theo quy tắc D1–D6/C1–C3 ở trên; một số ít chỗ còn chồng (nhịp ngắn, vùng nút) được báo trong `canh_bao`.

