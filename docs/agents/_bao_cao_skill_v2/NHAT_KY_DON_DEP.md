# Nhật ký dọn dẹp (chỉ trong `docs/agents/`)

| Hành động | Đối tượng | Lý do | Cách hoàn tác |
|:--|:--|:--|:--|
| `git mv` (lưu trữ, **không xoá**) | `docs/agents/huongdanchonthep/RULE_BASE_CHON_THEP_KHUNG_BTCT.md` → `huongdanchonthep/_luu_tru/` | Rule base cũ 74,6k ký tự được thay bằng bộ module 00–09; vẫn là dự phòng của loader khi thư mục module trống | `git mv` ngược lại |
| Không xoá file nào | — | Rà `docs/agents/` (trừ `huongdanvebanve/` bị khoá và gói nguồn): không có tệp tạm/trùng/cache cần dọn | — |

Không đụng: `huongdanvebanve/**`, `DRAWING_AGENT.md`, mọi thứ ngoài `docs/agents/`.

## Việc còn lại của người dùng (có sẵn từ trước, KHÔNG do đợt này tạo, KHÔNG được `git add`)
- `docs/agents/huongdanvebanve/SKILL_VE_KY_THUAT_BTCT.md` đang ở trạng thái sửa chưa commit.
- 10 ảnh `huongdanvebanve/img/mau_*.png` chưa theo dõi.
- Ngoài `docs/agents/`: `SH.zip`, PDF "Quy_Cach_Trinh_Bay…(Ngày 28-9).pdf", tệp khoá Word `~$I_LIEU_HUONG_DAN_HE_THONG_DAY_DU.docx` (đang ở trạng thái đã xoá).
