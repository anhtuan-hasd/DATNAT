"""Test tính toàn vẹn của bộ skill (markdown) cho 3 agent: Input Adapter, Rule Engine, Kiểm chứng.

Không gọi LLM/AutoCAD. Kiểm:
1. File có mặt, cấu trúc (16 bước dầm / 14 bước cột, R1–R52, PHẦN Q, Phụ lục B 31 hàng).
2. Mọi ảnh tham chiếu tồn tại và có khối "Mô tả bằng chữ" liền sau (agent không xem được ảnh).
3. Dấu PROMPT/BO cân bằng.
4. Các con số ví dụ chính được TÍNH LẠI độc lập bằng code (công thức TCVN 5574:2018 như trong skill) rồi so với
   chữ trong skill — chặn sửa tay làm lệch số.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
AGENTS = GOC / "docs" / "agents"
CHON_THEP = AGENTS / "huongdanchonthep"
NHAP = AGENTS / "huongdannhapdulieu" / "SKILL_NHAP_DU_LIEU_ETABS.md"
KIEM_CHUNG = AGENTS / "huongdankiemchung" / "SKILL_KIEM_CHUNG_KY_SU.md"

MODULES = sorted(CHON_THEP.glob("[0-9][0-9]_*.md"))


def _doc(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _chuan_hoa(t: str) -> str:
    """Bỏ định dạng LaTeX của số: `113{,}9` → `113,9`, `240\\,300` → `240300`."""
    return t.replace("{,}", ",").replace("\\,", "").replace(" ", "")


def _module(tien_to: str) -> str:
    (p,) = [m for m in MODULES if m.name.startswith(tien_to)]
    return _chuan_hoa(_doc(p))


def _tat_ca_chon_thep() -> str:
    return "\n".join(_chuan_hoa(_doc(m)) for m in MODULES)


# ---------------------------------------------------------------- 1. cấu trúc


def test_du_10_module_chon_thep_00_den_09():
    assert [m.name[:2] for m in MODULES] == [f"{i:02d}" for i in range(10)]


def test_skill_input_adapter_va_kiem_chung_ton_tai():
    assert NHAP.is_file() and len(_doc(NHAP)) > 5000
    assert KIEM_CHUNG.is_file() and len(_doc(KIEM_CHUNG)) > 3000


def test_dam_du_16_buoc_cot_du_14_buoc():
    dam = _doc(CHON_THEP / "02_DAM_16_BUOC.md")
    cot = _doc(CHON_THEP / "03_COT_14_BUOC.md")
    assert [int(n) for n in re.findall(r"^## Bước (\d+)\.", dam, re.M)] == list(range(1, 17))
    assert [int(n) for n in re.findall(r"^## Bước (\d+)\.", cot, re.M)] == list(range(1, 15))


def test_du_r1_den_r52_trong_bo_skill():
    tat_ca = _tat_ca_chon_thep()
    thieu = [f"R{i}" for i in range(1, 53) if not re.search(rf"\bR{i}\b", tat_ca)]
    assert not thieu, f"thiếu quy tắc: {thieu}"


def test_phan_q_va_d2_trong_module_08():
    m08 = _module("08")
    assert "PHẦN Q" in m08 and "D2" in m08


def test_khung_truc_5_trong_module_09():
    assert "Khung Trục 5" in _module("09")


NGUON = AGENTS / "_nguon_tai_lieu_chon_thep" / "NOI_DUNG_GOC.md"


def _bo_dinh_dang(t: str) -> str:
    return re.sub(r"[`*_$\{}]", "", re.sub(r"\s+", " ", t)).lower()


def test_phu_luc_b_31_hang_nguon_deu_co_trong_skill():
    """Mỗi dòng trong bảng Phụ lục B của nguồn (31 dòng) phải có chữ cột 2 trong bộ skill (cùng cách kiểm của kiem_tra_do_phu.py)."""
    nguon = NGUON.read_text(encoding="utf-8")
    m = re.search(r"# PHỤ LỤC B(.*?)# PHỤ LỤC C", nguon, flags=re.S)
    assert m, "không tìm thấy Phụ lục B trong nguồn"
    hang = re.findall(r"^\| (\d+) \| ([^|]+)\|", m.group(1), flags=re.M)
    assert len(hang) == 31, len(hang)
    skill = _bo_dinh_dang(_tat_ca_chon_thep() + _doc(NHAP) + _doc(KIEM_CHUNG))
    thieu = [n for n, t in hang if _bo_dinh_dang(t.strip())[:30] not in skill]
    assert not thieu, f"thiếu hàng Phụ lục B: {thieu}"


def test_phu_luc_b_bo_sung_b1_den_b17():
    m09 = _module("09")
    assert {int(n) for n in re.findall(r"^\|\s*B(\d{1,2})\s*\|", m09, re.M)} == set(range(1, 18))


def test_bang_nut_khung_nk_dm_ct_day_du():
    m05 = _module("05")
    for ma in [f"NK-{i:02d}" for i in range(1, 21)] + [f"DM-{i:02d}" for i in range(1, 14)] + [
        f"CT-{i:02d}" for i in range(1, 13)
    ]:
        assert ma in m05, ma


def test_kiem_chung_du_kc01_kc24():
    t = _doc(KIEM_CHUNG)
    for i in [*range(1, 8), *range(10, 25)]:
        assert f"| KC-{i:02d} |" in t, i
    # KC-08/09 để trống có chủ đích và phải được nói rõ, không thành lỗ hổng âm thầm
    assert "KC-08, KC-09 để trống" in t
    assert "| KC-08 |" not in t and "| KC-09 |" not in t


# ---------------------------------------------------------------- 2. ảnh + mô tả


_ANH = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_FILES_SKILL = [*MODULES, NHAP, KIEM_CHUNG]


@pytest.mark.parametrize("p", _FILES_SKILL, ids=lambda p: p.name)
def test_anh_ton_tai_va_co_mo_ta_bang_chu(p: Path):
    van_ban = _doc(p)
    for m in _ANH.finditer(van_ban):
        duong_dan = m.group(1).strip()
        if duong_dan.startswith("http"):
            continue
        assert (p.parent / duong_dan).is_file(), f"{p.name}: thiếu ảnh {duong_dan}"
        phan_sau = van_ban[m.end() : m.end() + 600]
        assert "Mô tả bằng chữ" in phan_sau, f"{p.name}: ảnh {duong_dan} không có 'Mô tả bằng chữ' liền sau"


def test_du_32_hinh_nguon_trong_thu_muc_img():
    anh = list((CHON_THEP / "img").glob("*.png"))
    assert len(anh) >= 32 + 12  # 32 hình nguồn + bs_01…bs_11, bs_14


# ---------------------------------------------------------------- 3. dấu PROMPT


@pytest.mark.parametrize("p", MODULES, ids=lambda p: p.name)
def test_dau_prompt_can_bang(p: Path):
    t = _doc(p)
    assert t.count("<!-- PROMPT:BAT_DAU -->") == t.count("<!-- PROMPT:KET_THUC -->")
    assert t.count("<!-- PROMPT:BO_BAT_DAU -->") == t.count("<!-- PROMPT:BO_KET_THUC -->")


# ---------------------------------------------------------------- 4. tính lại số


RB, RBT, RS, RSW, ES = 17.0, 1.15, 435.0, 170.0, 2e5


def _dien_tich(d: float) -> float:
    return math.pi * d * d / 4


def _am_xi_as(m_knm: float, b: float, h0: float) -> tuple[float, float, float]:
    am = m_knm * 1e6 / (RB * b * h0**2)
    xi = 1 - math.sqrt(1 - 2 * am)
    return am, xi, xi * RB * b * h0 / RS


def test_xi_r_cong_thuc_va_bang_lech_nhau():
    """Công thức ξR=0,8/(1+Rs/Es/0,0035) cho 0,493; bảng A cho 0,481 — skill phải ghi cả hai (mâu thuẫn đã biết)."""
    xi_r = 0.8 / (1 + (RS / ES) / 0.0035)
    assert f"{xi_r:.3f}".replace(".", ",") == "0,493"
    m01 = _module("01")
    assert "0,493" in m01 and "0,481" in m01


def test_dam_cb_dien_tich_thep_goi_va_nhip():
    """Dầm CB: As gối C (M=462,37; b=250; h0=645) = 1949,5 mm²; nhịp T (bf=2450, M=315,47, h0=660)."""
    _, _, as_goi = _am_xi_as(462.37, 250, 645)
    assert round(as_goi, 1) == 1949.5
    _, _, as_nhip = _am_xi_as(315.47, 2450, 660)
    assert abs(as_nhip - 1108.5) < 0.6
    m02 = _module("02")
    assert "1949,5" in m02 and "1108,5" in m02


def test_dam_cb_khang_uon_thuc_te():
    """2Ø25+3Ø22 (hai hàng): Mu≈492,5; 2Ø25 một hàng: Mu≈260,2 kNm (đường bậc thang vật liệu)."""
    c, ds = 20.0, 8.0
    a1 = 2 * _dien_tich(25) + _dien_tich(22)
    a2 = 2 * _dien_tich(22)
    y1 = c + ds + 25 / 2
    y2 = c + ds + 25 + 25 + 22 / 2
    a_tb = (a1 * y1 + a2 * y2) / (a1 + a2)
    h0 = 700 - a_tb
    as_ = a1 + a2
    x = RS * as_ / (RB * 250)
    mu = RS * as_ * (h0 - x / 2) / 1e6
    assert abs(mu - 492.5) < 0.6
    as2 = 2 * _dien_tich(25)
    h02 = 700 - (c + ds + 12.5)
    x2 = RS * as2 / (RB * 250)
    mu2 = RS * as2 * (h02 - x2 / 2) / 1e6
    assert abs(mu2 - 260.2) < 0.6
    m02 = _module("02")
    assert "492,5" in m02 and "260,2" in m02


def test_dam_cb_cat_cot_w_1165():
    """W = Q/(2·qsw) + 5d = 240300/(2·113,9)+110 = 1165 ≥ 20d=440."""
    q_sw = RSW * 100.5 / 150  # 2 nhánh Ø8 s150 → 113,9 N/mm
    assert round(q_sw, 1) == 113.9
    w = 240_300 / (2 * q_sw) + 5 * 22
    assert round(w) == 1165 and w >= 20 * 22
    assert "1165" in _module("06")


def test_dam_cb_cot_treo_f():
    """Cốt treo: F = 15,9·1,15 + 7,5·1,3 ... = 28,035 kN (quy ước skill) và đai treo."""
    f = 15.9 * 1.15 + 7.5 * 1.3
    assert round(f, 3) == 28.035
    assert "28,035" in _module("02")


def test_cot_22_lech_tam_va_as():
    """Cột 22 (250×600): η=1,045; As=1275 mm² (Cách 3), chọn 2Ø25+1Ø22 = 1362 mm²."""
    assert round(2 * _dien_tich(25) + _dien_tich(22)) == 1362
    m03 = _module("03")
    for s in ("1,045", "1275", "848,7", "1362"):
        assert s in m03 or s in _module("09"), s


def test_dam_cb_chiu_cat_tool_chat_hon_11a():
    """Mâu thuẫn tool: Qb1+Qsw1 (CB Ø8a150) = 165,4 kN < Q=240,3; mục 11a cho 249,3 kN (qsw=107,3 hoặc 113,9)."""
    b, h0 = 250.0, 645.0
    q_sw = RSW * 100.5 / 150
    c = min(2 * h0, max(h0, math.sqrt(2 * RBT * b * h0**2 / q_sw)))
    qu = (1.5 * RBT * b * h0**2 / c + 0.75 * q_sw * c) / 1e3
    assert 160 < qu < 260
    m02 = _module("02")
    assert "165,4" in m02 and "249,3" in m02


def test_trong_luong_don_vi_thep_hai_cach_ghi():
    """Trọng lượng riêng thép: 0,0061654 (π d²/4·7850) và 0,00617 (làm tròn Vẽ) — ghi cả hai, đánh dấu lệch."""
    kg_per_mm2_m = 7850 * math.pi / 4 * 1e-6  # kg/m cho d² mm²
    assert round(kg_per_mm2_m, 7) == 0.0061654
    m01 = _module("01")
    assert "0,0061654" in m01 and "0,00617" in m01


def test_khe_ho_cot_thep_dam_61_52mm_o_nut():
    t = _module("05")
    assert "61 mm" in t and "52 mm" in t


def test_hang_so_khoi_luong_thep_dam_cb_239_7_kg_va_198():
    t = _module("06")
    assert "239,7" in t and "198" in t
    # 239,7 kg / 1,21 m³ ≈ 198 kg/m³ (cận trên chỉ dẫn 80–200)
    assert round(239.7 / 1.21) == 198


def test_skill_khong_chua_khoa_api():
    """Vệ sinh: skill không chứa khóa API."""
    for p in _FILES_SKILL:
        assert "OPENAI_API_KEY=" not in _doc(p), p.name
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", _doc(p)), p.name
