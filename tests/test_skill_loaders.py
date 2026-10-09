"""Test loader skill dùng chung (`src/orchestrator/shared/doc_skill.py`) và việc 3 agent nạp skill vào system prompt.

Thuần Python (thư mục tạm), không LLM/AutoCAD.
"""

from __future__ import annotations

from pathlib import Path

from src.orchestrator.agents import input_adapter_agent as iaa
from src.orchestrator.agents import rule_engine_agent as rea
from src.orchestrator.agents import verification_agent as vca
from src.orchestrator.shared import doc_skill as ds

# ---------------------------------------------------------------- hàm loader


def test_thay_anh_bang_chu_thich_bo_duong_dan_giu_alt():
    ra = ds.thay_anh_bang_chu_thich("trước ![Hình 9.5: nút giữa](img/a.png) sau")
    assert "img/a.png" not in ra and "!["  not in ra
    assert "Hình 9.5: nút giữa" in ra and ra.startswith("trước ") and ra.endswith(" sau")


def test_doc_file_skill_thieu_file_tra_rong(thu_muc_tam: Path):
    assert ds.doc_file_skill(thu_muc_tam / "khong_co.md") == ""


def test_liet_ke_module_theo_ten_va_bo_qua_file_khac(thu_muc_tam: Path):
    for ten in ("02_b.md", "00_a.md", "10_c.md", "ghi_chu.md", "1_x.md", "03_d.txt"):
        (thu_muc_tam / ten).write_text("x", encoding="utf-8")
    assert [p.name for p in ds.liet_ke_module(thu_muc_tam)] == ["00_a.md", "02_b.md", "10_c.md"]
    assert ds.liet_ke_module(thu_muc_tam / "khong_co") == []


def test_doc_bo_skill_thieu_thu_muc_dung_du_phong(thu_muc_tam: Path):
    dp = thu_muc_tam / "cu.md"
    dp.write_text("RULE BASE CŨ", encoding="utf-8")
    assert ds.doc_bo_skill(thu_muc_tam / "khong_co", du_phong=dp) == "RULE BASE CŨ"
    assert ds.doc_bo_skill(thu_muc_tam / "khong_co") == ""


def test_doc_bo_skill_che_do_gon_va_day_du(thu_muc_tam: Path):
    (thu_muc_tam / "00_a.md").write_text("A\n", encoding="utf-8")
    (thu_muc_tam / "01_b.md").write_text(
        "đầu\n<!-- PROMPT:BAT_DAU -->\ngiữ\n<!-- PROMPT:KET_THUC -->\ncuối\n"
        "<!-- PROMPT:BO_BAT_DAU -->\nbỏ\n<!-- PROMPT:BO_KET_THUC -->\n",
        encoding="utf-8",
    )
    day_du = ds.doc_bo_skill(thu_muc_tam)
    gon = ds.doc_bo_skill(thu_muc_tam, che_do=ds.CHE_DO_GON)
    for s in ("đầu", "giữ", "cuối", "bỏ"):
        assert s in day_du
    assert "PROMPT:" not in day_du
    assert "giữ" in gon and "đầu" not in gon and "cuối" not in gon and "bỏ" not in gon
    assert gon.index("MODULE: 00_a.md") < gon.index("MODULE: 01_b.md")  # theo thứ tự tên


def test_doc_bo_skill_vung_bo_trong_vung_prompt(thu_muc_tam: Path):
    (thu_muc_tam / "00_a.md").write_text(
        "<!-- PROMPT:BAT_DAU -->\nX\n<!-- PROMPT:BO_BAT_DAU -->\nY\n<!-- PROMPT:BO_KET_THUC -->\nZ\n"
        "<!-- PROMPT:KET_THUC -->\n",
        encoding="utf-8",
    )
    gon = ds.doc_bo_skill(thu_muc_tam, che_do=ds.CHE_DO_GON)
    assert "X" in gon and "Z" in gon and "Y" not in gon


def test_doc_bo_skill_loai_tru_theo_tien_to(thu_muc_tam: Path):
    for ten in ("00_a.md", "02_b.md", "03_c.md"):
        (thu_muc_tam / ten).write_text(ten, encoding="utf-8")
    ra = ds.doc_bo_skill(thu_muc_tam, loai_tru=("03",))
    assert "02_b.md" in ra and "03_c.md" not in ra


def test_che_do_gon_bo_mo_ta_anh_tru_module_05(thu_muc_tam: Path):
    noi_dung = "![h](a.png)\n\n**Mô tả bằng chữ:** nội dung mô tả.\n\ntiếp\n"
    (thu_muc_tam / "02_x.md").write_text(noi_dung, encoding="utf-8")
    (thu_muc_tam / "05_y.md").write_text(noi_dung, encoding="utf-8")
    gon = ds.doc_bo_skill(thu_muc_tam, che_do=ds.CHE_DO_GON)
    phan_02, phan_05 = gon.split("<!-- MODULE: 05_y.md -->")
    assert "nội dung mô tả" not in phan_02
    assert "nội dung mô tả" in phan_05
    assert "a.png" not in gon


def test_ghep_skill_vao_prompt():
    assert ds.ghep_skill_vao_prompt("P", "", "T", "H") == "P"
    ra = ds.ghep_skill_vao_prompt("P", "SKILL", "T", "H")
    assert ra.startswith("P\n") and "# T" in ra and ra.endswith("SKILL")


def test_bao_cao_thieu_module(thu_muc_tam: Path):
    (thu_muc_tam / "00_a.md").write_text("x", encoding="utf-8")
    assert ds.bao_cao_thieu_module(thu_muc_tam, ["00", "05"]) == ["05"]


# ---------------------------------------------------------------- bộ skill thật


def test_bo_skill_chon_thep_that_du_module_va_khong_con_cu_phap_anh():
    thu_muc = ds.THU_MUC_AGENTS / "huongdanchonthep"
    assert ds.bao_cao_thieu_module(thu_muc, [f"{i:02d}" for i in range(10)]) == []
    for che_do in (ds.CHE_DO_DAY_DU, ds.CHE_DO_GON):
        van_ban = ds.doc_bo_skill(thu_muc, che_do=che_do)
        assert "![" not in van_ban and "](img/" not in van_ban
        assert "PHẦN Q" in van_ban and "Khung Trục 5" in van_ban
        assert "PROMPT:" not in van_ban


def test_che_do_gon_nho_hon_day_du_va_khong_bo_noi_dung_cot_loi():
    thu_muc = ds.THU_MUC_AGENTS / "huongdanchonthep"
    day_du = ds.doc_bo_skill(thu_muc)
    gon = ds.doc_bo_skill(thu_muc, che_do=ds.CHE_DO_GON)
    assert len(gon) < len(day_du)
    # nội dung cốt lõi phải còn trong chế độ gọn
    for s in ("Bước 1. Chốt dữ liệu đầu vào", "NK-01", "DM-01", "CT-01", "R52", "PHẦN Q"):
        assert s in gon, s


# ---------------------------------------------------------------- Rule Engine


def test_rule_engine_theo_loai_loai_tru_module_khong_lien_quan():
    dam = rea.HE_THONG_PROMPT_THEO_LOAI["dam"]
    cot = rea.HE_THONG_PROMPT_THEO_LOAI["cot"]
    assert "MODULE: 03_COT_14_BUOC.md" not in dam and "MODULE: 02_DAM_16_BUOC.md" in dam
    assert "MODULE: 02_DAM_16_BUOC.md" not in cot and "MODULE: 03_COT_14_BUOC.md" in cot
    # module chung vẫn có ở cả hai
    for p in (dam, cot):
        for ten in ("00_NGUYEN_TAC", "01_VAT_LIEU", "05_NUT_KHUNG", "08_BANG_QUYET_DINH"):
            assert ten in p, ten


def test_rule_engine_prompt_goc_giu_dieu_khoan_khong_dat_khi_con_co():
    assert "R45" in rea.HE_THONG_PROMPT and "R46" in rea.HE_THONG_PROMPT


def test_rule_engine_prompt_loai_la_khong_lam_rong_prompt():
    assert rea.HE_THONG_PROMPT_THEO_LOAI.get("khac", rea.HE_THONG_PROMPT) is rea.HE_THONG_PROMPT


def test_rule_engine_ngan_sach_prompt_trong_gioi_han():
    """Ngưỡng cảnh báo kích thước (ký tự) — chặn phình prompt vô ý. Nếu vượt: rút gọn dấu PROMPT trước khi nới ngưỡng."""
    assert len(rea.HE_THONG_PROMPT_THEO_LOAI["dam"]) < 165_000
    assert len(rea.HE_THONG_PROMPT_THEO_LOAI["cot"]) < 165_000


# ---------------------------------------------------------------- Input Adapter, Verification


def test_input_adapter_prompt_co_skill_nhap_du_lieu():
    assert "TÀI LIỆU THAM KHẢO BẮT BUỘC — skill nhập dữ liệu ETABS" in iaa.HE_THONG_PROMPT
    assert len(iaa.HE_THONG_PROMPT) > len(iaa._HE_THONG_PROMPT_GOC) + 5000
    assert iaa.HE_THONG_PROMPT.startswith(iaa._HE_THONG_PROMPT_GOC)
    assert "![" not in iaa.HE_THONG_PROMPT


def test_verification_prompt_co_skill_kiem_chung():
    assert "TÀI LIỆU THAM KHẢO BẮT BUỘC — skill kiểm chứng của kỹ sư" in vca.HE_THONG_PROMPT
    assert vca.HE_THONG_PROMPT.startswith(vca._HE_THONG_PROMPT_GOC)
    assert "KC-11" in vca.HE_THONG_PROMPT and "![" not in vca.HE_THONG_PROMPT


def test_thieu_file_skill_van_tra_prompt_goc(monkeypatch, thu_muc_tam: Path):
    monkeypatch.setattr(iaa, "_DUONG_DAN_SKILL_NHAP_DU_LIEU", thu_muc_tam / "khong_co.md")
    monkeypatch.setattr(vca, "_DUONG_DAN_SKILL_KIEM_CHUNG", thu_muc_tam / "khong_co.md")
    assert iaa._xay_dung_he_thong_prompt() == iaa._HE_THONG_PROMPT_GOC
    assert vca._xay_dung_he_thong_prompt() == vca._HE_THONG_PROMPT_GOC
