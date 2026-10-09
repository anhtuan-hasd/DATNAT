"""Loader dùng chung cho tài liệu skill (markdown) nạp vào system prompt của 3 agent
(Input Adapter, Rule Engine, Verification). Drawing Agent giữ loader riêng của nó
(`drawing_agent._doc_skill_ve_ky_thuat`) — không đổi.

Quy ước thống nhất:
- Agent chỉ nhận **văn bản thuần** qua tool-calling, không xem được ảnh. Cú pháp ảnh markdown
  `![chú thích](đường_dẫn)` được thay bằng một dòng chú thích; phần "Mô tả bằng chữ" đi liền sau mỗi ảnh
  trong file skill giữ nguyên để agent đọc.
- Không bao giờ raise khi thiếu file/thư mục: trả `""` (pipeline vẫn chạy với prompt rút gọn). Thiếu skill là
  bất thường cần sửa ngay — `bao_cao_thieu_module` dùng cho test/CLI kiểm tra rõ ràng.
- Bộ skill nhiều module đặt tên `NN_*.md` (NN = 2 chữ số), nạp theo thứ tự tên file.
- Ngân sách ngữ cảnh: chế độ `"gon"` chỉ nạp phần nằm giữa cặp dấu `<!-- PROMPT:BAT_DAU -->` …
  `<!-- PROMPT:KET_THUC -->` của module dài; `loai_tru` bỏ hẳn module không liên quan tới loại cấu kiện.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

GOC_REPO = Path(__file__).resolve().parents[3]
THU_MUC_AGENTS = GOC_REPO / "docs" / "agents"

MAU_ANH_MARKDOWN = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
MAU_TEN_MODULE = re.compile(r"^\d{2}_.+\.md$")
MAU_VUNG_PROMPT = re.compile(r"<!-- PROMPT:BAT_DAU -->\n?(.*?)<!-- PROMPT:KET_THUC -->\n?", re.S)

MAU_BO_QUA = re.compile(r"<!-- PROMPT:BO_BAT_DAU -->\n?(.*?)<!-- PROMPT:BO_KET_THUC -->\n?", re.S)
MAU_MO_TA_ANH = re.compile(r"\n*\*\*Mô tả bằng chữ:\*\*.*?(?=\n\n|\Z)", re.S)
# Module giữ nguyên khối "Mô tả bằng chữ" ở chế độ gọn (hình nút khung truyền hình học mà bảng chữ không thay hết).
MODULE_GIU_MO_TA_ANH = ("05",)

CHE_DO_DAY_DU = "day_du"
CHE_DO_GON = "gon"

_CHU_THICH_ANH = (
    "[hình minh hoạ: {alt} — chỉ có trong file gốc, không kèm được qua tool-calling văn bản; "
    "xem khối 'Mô tả bằng chữ' ngay bên dưới]"
)
_NGAN_MODULE = "\n\n---\n\n"


def thay_anh_bang_chu_thich(van_ban: str) -> str:
    """Thay mọi cú pháp ảnh markdown bằng chú thích văn bản (giữ lại alt, bỏ đường dẫn)."""
    return MAU_ANH_MARKDOWN.sub(lambda m: _CHU_THICH_ANH.format(alt=m.group(1).strip()), van_ban)


def doc_file_skill(duong_dan: Path, bo_anh: bool = True) -> str:
    """Đọc 1 file skill UTF-8. Trả "" nếu không có file. `bo_anh=True`: thay ảnh bằng chú thích."""
    try:
        van_ban = Path(duong_dan).read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return ""
    return thay_anh_bang_chu_thich(van_ban) if bo_anh else van_ban


def liet_ke_module(thu_muc: Path, mau: re.Pattern[str] = MAU_TEN_MODULE) -> list[Path]:
    """Các file module `NN_*.md` trong `thu_muc` (không đệ quy), sắp theo tên. Rỗng nếu thiếu thư mục."""
    thu_muc = Path(thu_muc)
    if not thu_muc.is_dir():
        return []
    return sorted(p for p in thu_muc.iterdir() if p.is_file() and mau.match(p.name))


def trich_vung_prompt(van_ban: str) -> str:
    """Chế độ gọn: có cặp dấu PROMPT:BAT_DAU/KET_THUC ⇒ chỉ giữ các vùng đó; sau đó bỏ các vùng PROMPT:BO_*."""
    cac_vung = MAU_VUNG_PROMPT.findall(van_ban)
    van_ban = "\n\n".join(v.strip() for v in cac_vung) if cac_vung else van_ban
    return MAU_BO_QUA.sub("", van_ban)


def bo_dau_vung_prompt(van_ban: str) -> str:
    """Chế độ đầy đủ: bỏ mọi dấu PROMPT, giữ trọn nội dung."""
    van_ban = MAU_VUNG_PROMPT.sub(lambda m: m.group(1), van_ban)
    return MAU_BO_QUA.sub(lambda m: m.group(1), van_ban)


def bo_khoi_mo_ta_anh(van_ban: str) -> str:
    """Chế độ gọn: bỏ các khối "Mô tả bằng chữ" và rút chú thích ảnh còn 1 dòng ngắn (không còn 'xem bên dưới')."""
    van_ban = MAU_MO_TA_ANH.sub("", van_ban)
    return MAU_ANH_MARKDOWN.sub(lambda m: "[hình minh hoạ: " + m.group(1).strip()[:150] + "]", van_ban)


def doc_bo_skill(
    thu_muc: Path,
    du_phong: Path | None = None,
    bo_anh: bool = True,
    che_do: str = CHE_DO_DAY_DU,
    loai_tru: Iterable[str] = (),
) -> str:
    """Nối các module `NN_*.md` của `thu_muc` (theo thứ tự tên) thành một khối văn bản.

    - `che_do="gon"`: module có cặp dấu PROMPT chỉ nạp phần trong dấu; module không có dấu nạp trọn.
    - `loai_tru`: tiền tố module bỏ qua (vd `("03",)` khi chọn thép dầm).
    - Thư mục không có module nào mà `du_phong` (file đơn, vd rule base cũ đã lưu trữ) tồn tại ⇒ dùng `du_phong`.
    Trả "" nếu không có gì."""
    tat_ca = liet_ke_module(thu_muc)
    if not tat_ca:
        return doc_file_skill(du_phong, bo_anh) if du_phong else ""
    bo_qua = set(loai_tru)
    phan = []
    for p in tat_ca:
        if p.name[:2] in bo_qua:
            continue
        noi_dung = doc_file_skill(p, bo_anh=False)
        if not noi_dung:
            continue
        gon = che_do == CHE_DO_GON
        noi_dung = trich_vung_prompt(noi_dung) if gon else bo_dau_vung_prompt(noi_dung)
        if gon and p.name[:2] not in MODULE_GIU_MO_TA_ANH:
            noi_dung = bo_khoi_mo_ta_anh(noi_dung)
        if bo_anh:
            noi_dung = thay_anh_bang_chu_thich(noi_dung)
        phan.append(f"<!-- MODULE: {p.name} -->\n{noi_dung.strip()}")
    return _NGAN_MODULE.join(phan)


def ghep_skill_vao_prompt(prompt: str, skill: str, tieu_de: str, huong_dan: str) -> str:
    """Ghép khối skill vào cuối `prompt` kèm tiêu đề và đoạn hướng dẫn cách dùng. `skill` rỗng ⇒ trả nguyên `prompt`."""
    if not skill:
        return prompt
    return f"{prompt}\n\n# {tieu_de}\n{huong_dan}\n\n{skill}"


def bao_cao_thieu_module(thu_muc: Path, tien_to_bat_buoc: list[str]) -> list[str]:
    """Trả danh sách tiền tố module bắt buộc (vd ["00", "05"]) mà `thu_muc` chưa có — dùng trong test/CLI."""
    co = {p.name[:2] for p in liet_ke_module(thu_muc)}
    return [t for t in tien_to_bat_buoc if t not in co]
