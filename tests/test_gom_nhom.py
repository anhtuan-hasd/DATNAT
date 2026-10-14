"""Test gom nhóm thép R53 (cột cùng tầng/tiết diện) và R54 (hai gối dầm cùng bố trí) — số liệu lấy từ thuyết minh Khung Trục 5
(Bảng 26–27). Thuần Python, không LLM/AutoCAD."""

from __future__ import annotations

from src.orchestrator.gom_nhom_khung import ap_dung_gom_nhom
from src.orchestrator.shared.hop_dong_du_lieu import (
    BoDuLieuKhungChuanHoa, KetQuaPhanTu, KetQuaViTriDaThietKe, PhanTuChuanHoa, PhuongAnThepPhanTu,
)
from src.rule_engine import gom_nhom, vat_lieu


def _cot(d: int, n_phia: int) -> dict:
    a = vat_lieu.dien_tich_1_thanh(d) * n_phia
    return {"duong_kinh": d, "so_thanh_canh_b": n_phia, "so_thanh_canh_h": 2, "tong_so_thanh": 2 * n_phia,
            "As_thuc_moi_phia": a, "mo_ta": f"{2 * n_phia}Ø{d}"}


def _dam(*nhom: tuple[int, int]) -> dict:
    a = sum(vat_lieu.dien_tich_1_thanh(d) * n for d, n in nhom)
    return {"thanh": [{"duong_kinh": d, "so_luong": n} for d, n in nhom], "As_thuc": a, "mo_ta": "+".join(f"{n}Ø{d}" for d, n in nhom)}


def _khung_cot(cac_cot: list[tuple[str, str, float, float, dict]]):
    goc, kq = [], []
    for ten, tang, b, h, thep in cac_cot:
        goc.append(PhanTuChuanHoa(ten=ten, loai="cot", b=b, h=h, mac_be_tong="B25", nhom_thep_doc="CB500-V", tang=tang))
        vt = KetQuaViTriDaThietKe(vi_tri="vi_tri_1", thep_doc=thep, neo_noi={"L_an": 1.0}, dat=True)
        pa = PhuongAnThepPhanTu(ten_phan_tu=ten, loai="cot", b=b, h=h, vi_tri=[vt],
                                dai={"loai": "cot", "duong_kinh_dai": 6, "buoc_dau": 150.0, "buoc_giua": 250.0, "canh_bao": "x"})
        kq.append(KetQuaPhanTu(ten_phan_tu=ten, loai="cot", trang_thai="cho_ve_mat_cat", phuong_an_thep=pa, rule_engine_dat=True))
    return BoDuLieuKhungChuanHoa(phan_tu=goc), kq


def test_r53_cot_a_tang_3_lay_theo_cot_b_nhu_thuyet_minh():
    """Bảng 26: tầng 3 cột A cần 382,13 (2Ø16 đủ) nhưng cột B cần 503,59 ⇒ cả hai 2Ø18/phía."""
    du_lieu, kq = _khung_cot([
        ("2", "Tang2_Tang3", 220, 300, _cot(16, 2)),
        ("15", "Tang2_Tang3", 220, 300, _cot(18, 2)),
    ])
    nhat_ky = ap_dung_gom_nhom(du_lieu, kq)
    thep_a = kq[0].phuong_an_thep.vi_tri[0].thep_doc
    assert thep_a["mo_ta"] == "4Ø18" and thep_a["gom_nhom_tu"] == "cột 15"
    assert kq[1].phuong_an_thep.vi_tri[0].thep_doc["mo_ta"] == "4Ø18"  # cột chuẩn không đổi
    assert len(nhat_ky) == 1 and "R53" in nhat_ky[0] and "'2'" in nhat_ky[0]


def test_r53_khong_gom_khac_tang_khac_tiet_dien_hoac_thieu_tang():
    du_lieu, kq = _khung_cot([
        ("1", "Mong_Tang2", 220, 300, _cot(18, 3)),
        ("2", "Tang2_Tang3", 220, 300, _cot(16, 2)),  # khác tầng
        ("19", "Tang2_Tang3", 220, 220, _cot(16, 2)),  # khác tiết diện (cột C)
        ("x", None, 220, 300, _cot(16, 2)),  # thiếu tầng
        ("y", None, 220, 300, _cot(18, 3)),
    ])
    assert ap_dung_gom_nhom(du_lieu, kq) == []
    assert [k.phuong_an_thep.vi_tri[0].thep_doc["mo_ta"] for k in kq] == ["6Ø18", "4Ø16", "4Ø16", "4Ø16", "6Ø18"]


def test_r53_chi_nang_khong_ha_va_tinh_lai_neo_va_dai():
    du_lieu, kq = _khung_cot([
        ("a", "T", 220, 300, _cot(16, 2)),
        ("b", "T", 220, 300, _cot(18, 3)),
    ])
    ap_dung_gom_nhom(du_lieu, kq)
    pa_a = kq[0].phuong_an_thep
    assert pa_a.vi_tri[0].thep_doc["As_thuc_moi_phia"] >= vat_lieu.dien_tich_1_thanh(18) * 3  # nâng, không hạ
    # neo/nối tính lại theo Ø18 (L0,an = Rs·d/(4·Rbond) = 435·18/(4·2,625) ≈ 745,7)
    assert abs(pa_a.vi_tri[0].neo_noi["L0_an"] - 745.7) < 1.0
    # đai tính lại theo Ø dọc mới, giữ cảnh báo cũ
    assert pa_a.dai["duong_kinh_doc_max"] == 18 and pa_a.dai["canh_bao"] == "x"
    assert pa_a.dai["buoc_dau"] == 150.0  # 10·18 = 180 → làm tròn xuống bội 50 = 150


def _khung_dam(ten: str, h: float, goi_trai: dict, giua: dict, goi_phai: dict):
    goc = PhanTuChuanHoa(ten=ten, loai="dam", b=220, h=h, mac_be_tong="B25", nhom_thep_doc="CB500-V", tang="Tang2")
    vts = [KetQuaViTriDaThietKe(vi_tri=n, thep_doc=t, neo_noi={}, dat=True)
           for n, t in (("goi_trai", goi_trai), ("giua_nhip", giua), ("goi_phai", goi_phai))]
    pa = PhuongAnThepPhanTu(ten_phan_tu=ten, loai="dam", b=220, h=h, vi_tri=vts, dai={})
    return BoDuLieuKhungChuanHoa(phan_tu=[goc]), [KetQuaPhanTu(ten_phan_tu=ten, loai="dam", trang_thai="x", phuong_an_thep=pa, rule_engine_dat=True)]


def test_r54_dam_45_hai_goi_cung_2phi18_nhip_giu_2phi16():
    """Bảng 27: dầm 45 gối trái 439,35 → 2Ø18; gối phải 388,69 (2Ø16 đủ) vẫn 2Ø18; nhịp 292,01 → 2Ø16."""
    du_lieu, kq = _khung_dam("45", 300, _dam((18, 2)), _dam((16, 2)), _dam((16, 2)))
    nhat_ky = ap_dung_gom_nhom(du_lieu, kq)
    vt = {v.vi_tri: v.thep_doc for v in kq[0].phuong_an_thep.vi_tri}
    assert vt["goi_phai"]["mo_ta"] == "2Ø18" and vt["goi_phai"]["gom_nhom_tu"] == "dầm 45 goi_trai"
    assert vt["giua_nhip"]["mo_ta"] == "2Ø16" and "gom_nhom_tu" not in vt["giua_nhip"]
    assert len(nhat_ky) == 1 and "R54" in nhat_ky[0]


def test_r54_hai_goi_da_giong_nhau_khong_doi_va_khong_co_gi_trong_nhat_ky():
    du_lieu, kq = _khung_dam("32", 500, _dam((18, 3)), _dam((18, 2)), _dam((18, 3)))
    assert ap_dung_gom_nhom(du_lieu, kq) == []


def test_r54_neo_noi_tinh_lai_chi_khi_vi_tri_da_co_neo_noi():
    du_lieu, kq = _khung_dam("45", 300, _dam((18, 2)), _dam((16, 2)), _dam((16, 2)))
    kq[0].phuong_an_thep.vi_tri[2].neo_noi = {"L_an": 1.0}  # gối phải có neo/nối do agent tính ⇒ tính lại theo Ø18
    ap_dung_gom_nhom(du_lieu, kq)
    assert abs(kq[0].phuong_an_thep.vi_tri[2].neo_noi["L0_an"] - 745.7) < 1.0
    assert kq[0].phuong_an_thep.vi_tri[1].neo_noi == {}  # nhịp không đổi


def test_tim_nang_cap_tat_dinh_khi_bang_nhau_va_khong_gom_nhom_le():
    m = [gom_nhom.MucGom("a", ("n",), 500.0, "2Ø18"), gom_nhom.MucGom("b", ("n",), 500.0, "3Ø16"),
         gom_nhom.MucGom("c", ("khac",), 100.0, "2Ø16")]
    assert gom_nhom.tim_nang_cap(m, "R53") == []  # bằng As ⇒ không có cơ sở đổi; nhóm lẻ ⇒ bỏ qua
