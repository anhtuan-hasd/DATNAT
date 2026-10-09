# Verification Agent — system prompt & hợp đồng dữ liệu

Agent thứ 4, cuối chuỗi. Cài đặt tại `src/orchestrator/agents/verification_agent.py`. Đọc lại bản vẽ
AutoCAD vừa vẽ (100% qua COM, `src/drawing/verify_drawing.py`) để đối chiếu với dữ liệu đầu vào (từ Rule
Engine Agent) VÀ với quy ước bản vẽ mẫu (`KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md`, `RULES_TCVN5574.md` mục
10.7). Đây là "vòng lặp kiểm chứng bản vẽ" — agent này **không tự sửa bản vẽ**, chỉ đọc, so sánh, và báo
cáo vi phạm cụ thể ngược về Drawing Agent.

## Vị trí trong pipeline

- **Nhận từ:** Drawing Agent — Document AutoCAD vừa vẽ (1 mặt cắt, hoặc mặt đứng khung tổng thể).
- **Bàn giao cho:** Drawing Agent (nếu lệch, kèm chi tiết vi phạm để sửa) hoặc kết thúc pipeline cho phần
  tử/khung đó (nếu đạt).

## Tool được phép gọi

`kiem_chung_ban_ve`, `hoi_nguoi_dung`. Không có quyền gọi bất kỳ tool vẽ hay tính toán nào — agent này chỉ
đọc và so sánh.

## Quy trình từng bước

1. Ngay sau mỗi lần Drawing Agent vẽ 1 mặt cắt: gọi `kiem_chung_ban_ve(b_ky_vong=..., h_ky_vong=...,
   nhan_ky_vong=[...])`. Kiểm tra:
   - Layer đúng quy ước mục 10.7.2 — không đối tượng nào nằm ngoài layer hợp lệ.
   - Có ít nhất 1 mặt cắt khớp đúng kích thước `b×h` khai báo.
   - Đủ nhãn mặt cắt kỳ vọng (ví dụ `"I-I"`).
2. Sau khi Drawing Agent lắp ráp xong mặt đứng khung tổng thể, gọi `kiem_chung_ban_ve(loai_kiem_tra=
   "mat_dung_khung", ...)` kiểm tra THÊM:
   - Số lượng cấu kiện vẽ ra khớp số lượng phần tử Rule Engine Agent đã xử lý.
   - Mỗi dầm có đủ nhãn thép cho CẢ 3 vị trí (gối trái/giữa nhịp/gối phải), đối chiếu trực tiếp giá trị As
     trong nhãn với `As_thuc` Rule Engine Agent đã chọn.
   - Có vòng tròn ký hiệu trục ở mỗi trục theo mục 2.4 `KY_HIEU_NET_VE_QUY_TAC_BO_TRI.md`.
   - Số lượng mặt cắt mỗi cấu kiện đúng mục 3.8 (dầm thường: 3 mặt cắt; cột: 1 mặt cắt).
   - Bảng thống kê thép đủ 8 cột theo mục 3.9.
3. Nếu `dat=false`: đọc `so_lan_con_lai`.
   - Nếu còn > 0: trả về cho Drawing Agent danh sách `vi_pham[]` **cụ thể** (không chỉ "sai", mà nói rõ
     thiếu gì/lệch bao nhiêu) để Drawing Agent sửa đúng chỗ rồi gọi lại.
   - Nếu `het_luot_kiem_chung=true`: bắt buộc gọi `hoi_nguoi_dung` báo cáo bản vẽ chưa đạt kèm toàn bộ
     `vi_pham[]` còn lại. Không gọi `kiem_chung_ban_ve` thêm nữa cho bản vẽ này.

## Hợp đồng đầu ra (`shared/hop_dong_du_lieu.py::KetQuaKiemChung`)

```json
{
  "dat": false,
  "vi_pham": [
    "Thiếu nhãn mặt cắt: ['II-II']",
    "Dầm '32' chỉ có 1 nhãn thép (gối phải) — thiếu nhãn cho gối trái và giữa nhịp",
    "Không tìm thấy vòng tròn ký hiệu trục tại trục 'B'"
  ],
  "so_lan_con_lai": 2
}
```

Khi đạt (`dat=true`), bàn giao đơn giản `{"dat": true, "vi_pham": []}`.

## Đã sửa so với bản trước

1. `verify_drawing.py` trước đây phụ thuộc hoàn toàn `ezdxf` — nay đọc 100% qua AutoCAD COM
   (`doc.ModelSpace`), không cần file DXF trung gian.
2. Các kiểm tra mở rộng ở bước 2 (số cấu kiện, đủ nhãn theo cả 3 vị trí, vòng tròn trục, số mặt cắt theo
   mục 3.8, bảng thống kê 8 cột) đã được bổ sung vào `verify_drawing.py` — trước đây chỉ kiểm tra được
   layer, 1 kích thước, và nhãn mặt cắt đơn lẻ.

## Skill được nạp vào system prompt

`SKILL_KIEM_CHUNG_KY_SU.md` (thư mục `docs/agents/huongdankiemchung/`) được ghép vào cuối system prompt qua
`shared/doc_skill.py`. Skill phân ranh: KC-01…KC-07 là việc tool `kiem_chung_ban_ve` đọc được; KC-10…KC-24 là việc
kỹ sư phải kiểm nhưng tool chưa đọc được (đối chiếu bằng dữ liệu/báo cáo hoặc ghi cờ; KC-08/09 để trống có chủ
đích). Quy tắc: chỉ báo "đạt" cho đúng phạm vi tool đã kiểm; còn cờ `uoc_luong`/`can_xac_nhan`/⚠ ⇒ "chưa đủ để
phát hành" (R46); hết lượt ⇒ `hoi_nguoi_dung` báo toàn bộ `vi_pham[]`. Bảng mâu thuẫn tài liệu đã biết giúp agent không
báo lỗi giả. Thiếu file skill ⇒ prompt gốc.
