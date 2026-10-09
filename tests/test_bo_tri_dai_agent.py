"""Test tool `bo_tri_dai` của Rule Engine Agent và đường dữ liệu agent → tờ vẽ (Agent đọc skill, quyết định đai, bản vẽ dùng
đúng quyết định đó). Không LLM/AutoCAD: dùng nhà cung cấp GIẢ có kịch bản + dispatch THẬT."""

from __future__ import annotations

from src.drawing.to_ve import ke_hoach
from src.drawing.to_ve.co_so import CauHinhToVe
from src.orchestrator import pipeline
from src.orchestrator.agents import rule_engine_agent as rea
from src.orchestrator.loops import BoDemVongLap
from src.orchestrator.shared.hop_dong_du_lieu import KetQuaPhanTu, PhanTuChuanHoa, ViTriChuanHoa


def _nc(khong_co_Q=True):
    return rea.NguCanhRuleEngine(hoi_nguoi_dung=lambda c, l=None: "đồng ý", bo_dem=BoDemVongLap(), khong_co_Q=khong_co_Q)


def test_tool_bo_tri_dai_dam_khop_ban_ve_mau():
    nc = _nc()
    d = rea.tao_dispatch(nc)
    d["chon_thep_doc"]({"loai": "dam", "As_target": 686.02, "b": 220, "cover": 25.0})  # → 3Ø18
    kq = d["bo_tri_dai"]({"loai": "dam", "h": 500})
    assert "loi" not in kq
    assert kq["duong_kinh_dai"] == 6 and kq["buoc_goi"] == 150
    assert kq["buoc_giua"] >= kq["buoc_goi"]
    assert "canh_bao" in kq  # dầm ETABS không có Q ⇒ chỉ theo cấu tạo, phải cảnh báo


def test_tool_bo_tri_dai_chua_chon_thep_bao_loi():
    kq = rea.tao_dispatch(_nc())["bo_tri_dai"]({"loai": "dam", "h": 500})
    assert "loi" in kq and "chon_thep_doc" in kq["loi"]


def test_tool_bo_tri_dai_thieu_h_bao_loi():
    nc = _nc()
    d = rea.tao_dispatch(nc)
    d["chon_thep_doc"]({"loai": "dam", "As_target": 300.0, "b": 220})
    assert "loi" in d["bo_tri_dai"]({"loai": "dam"})
    assert "loi" in d["bo_tri_dai"]({"loai": "khac", "h": 500})


def test_tool_bo_tri_dai_cot_hai_dau_10d_giua_15d():
    nc = _nc(khong_co_Q=False)
    d = rea.tao_dispatch(nc)
    d["chon_thep_doc"]({"loai": "cot", "As_target": 743.19, "b": 220, "h": 300, "cover": 40.0})  # 6Ø18
    kq = d["bo_tri_dai"]({"loai": "cot", "h": 300})
    assert kq["buoc_dau"] == 150 and kq["buoc_giua"] >= kq["buoc_dau"]


def test_buoc_tinh_toan_tu_tinh_cot_dai_duoc_tool_tu_lay():
    """Bước đai theo tính toán đi từ tinh_cot_dai sang bo_tri_dai KHÔNG qua LLM chép số."""
    nc = _nc(khong_co_Q=False)
    d = rea.tao_dispatch(nc)
    d["chon_thep_doc"]({"loai": "dam", "As_target": 700.0, "b": 220, "cover": 25.0})
    r = d["tinh_cot_dai"]({"Q": 200.0, "Rb": 14.5, "Rbt": 1.05, "Rsw": 170.0, "b": 220, "h0": 460, "Asw": 56.5, "loai": "dam"})
    s_tt = r.get("buoc_dai_toi_da_theo_kha_nang_chiu_cat")
    kq = d["bo_tri_dai"]({"loai": "dam", "h": 500})
    if s_tt:
        assert nc.buoc_dai_tinh_toan == s_tt
        assert kq["buoc_goi"] <= max(50.0, (s_tt // 50) * 50)
        assert kq["buoc_tinh_toan_da_xet"] == s_tt


class _Gia:
    def __init__(self, kb):
        self.kb, self.i = kb, 0

    def goi(self, he_thong, messages, tools):
        r = self.kb[self.i]
        self.i += 1
        return r


def _tu(i, n, inp):
    return {"type": "tool_use", "id": i, "name": n, "input": inp}


def test_agent_kich_ban_goi_bo_tri_dai_va_phuong_an_mang_dai():
    """LLM giả gọi đúng chuỗi theo prompt/skill; trích phương án phải mang kết quả bo_tri_dai sang hợp đồng dữ liệu."""
    prov = _Gia([
        {"content": [_tu("1", "tra_vat_lieu", {"mac_be_tong": "B25", "nhom_thep_doc": "CB500-V", "nhom_thep_dai": "CB240-T"})]},
        {"content": [_tu("2", "chon_thep_doc", {"loai": "dam", "As_target": 686.02, "b": 220, "cover": 25.0})]},
        {"content": [_tu("3", "tu_kiem_tra", {"loai": "dam", "thong_so": {"As_thuc": 763.4, "As_yc": 686.02}})]},
        {"content": [_tu("4", "bo_tri_dai", {"loai": "dam", "h": 500})]},
        {"content": [{"type": "text", "text": "xong"}]},
    ])
    kq, _ = rea.chay_rule_engine_agent(prov, "Dầm 32", hoi_nguoi_dung=lambda c, l=None: "đồng ý", khong_co_Q=True, loai="dam")
    pa = rea.trich_phuong_an_thep(kq, ten_phan_tu="32", loai="dam", b=220, h=500)
    assert pa.dai and pa.dai["duong_kinh_dai"] == 6 and pa.dai["buoc_goi"] == 150
    assert pa.moi_vi_tri_dat


def test_yeu_cau_cho_agent_yeu_cau_goi_bo_tri_dai():
    p = PhanTuChuanHoa(ten="32", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB500-V",
                       vi_tri=[ViTriChuanHoa("goi_trai", As_yc=686.0)])
    mo_ta = pipeline._mo_ta_yeu_cau_rule_engine("K5", p)
    assert "bo_tri_dai" in mo_ta and "h=500" in mo_ta
    pc = PhanTuChuanHoa(ten="1", loai="cot", b=220, h=300, mac_be_tong="B25", nhom_thep_doc="CB500-V",
                        vi_tri=[ViTriChuanHoa("dai_dien", As_yc=743.0, N=500.0, M=90.0)])
    assert "loai='cot', h=300" in pipeline._mo_ta_yeu_cau_rule_engine("K5", pc)  # cột: cạnh lớn


def test_du_lieu_lap_rap_mang_quyet_dinh_dai():
    from src.orchestrator.shared.hop_dong_du_lieu import BoDuLieuKhungChuanHoa, KetQuaViTriDaThietKe, PhuongAnThepPhanTu

    goc = PhanTuChuanHoa(ten="32", loai="dam", b=220, h=500, mac_be_tong="B25", nhom_thep_doc="CB500-V", truc="A-B", tang="Tang2",
                         chieu_dai=5600.0, vi_tri=[ViTriChuanHoa("goi_trai", As_yc=686.0)])
    pa = PhuongAnThepPhanTu("32", "dam", 220, 500,
                            [KetQuaViTriDaThietKe("goi_trai", {"thanh": [{"duong_kinh": 18, "so_luong": 3}]}, dat=True)],
                            dai={"duong_kinh_dai": 6, "buoc_goi": 150, "buoc_giua": 200})
    bo = BoDuLieuKhungChuanHoa(phan_tu=[goc], toa_do_truc={"A": 0.0, "B": 5600.0}, cao_do_moc={"Mong": 0.0, "Tang2": 4200.0})
    dl = pipeline._du_lieu_lap_rap(bo, [KetQuaPhanTu("32", "dam", "cho_ve_mat_cat", pa, rule_engine_dat=True)])
    assert dl["phan_tu"][0]["dai"] == {"duong_kinh_dai": 6, "buoc_goi": 150, "buoc_giua": 200}


# ---------------------------------------------------------------- tờ vẽ dùng đúng quyết định của agent


def _du_lieu(dai_dam=None, dai_cot=None):
    def th(ds):
        o: dict[int, int] = {}
        for d in ds:
            o[d] = o.get(d, 0) + 1
        return [{"duong_kinh": d, "so_luong": n} for d, n in o.items()]

    thep_cot = {"duong_kinh": 18, "so_thanh_canh_b": 3, "so_thanh_canh_h": 2, "tong_so_thanh": 6}
    cot = {"ten": "1", "loai": "cot", "b": 220, "h": 300, "truc": "A", "tang": "Mong_Tang2", "chieu_dai": 4200.0,
           "vi_tri": [{"vi_tri": "dai_dien", "mo_ta_thep": "?", "thanh": th([18] * 6), "thep_doc": thep_cot, "neo_noi": {"L_lap": 800.0}}]}
    cot2 = {**cot, "ten": "2", "truc": "B"}
    dam = {"ten": "32", "loai": "dam", "b": 220, "h": 500, "truc": "A-B", "tang": "Tang2", "chieu_dai": 5000.0,
           "vi_tri": [{"vi_tri": "goi_trai", "mo_ta_thep": "?", "thanh": th([18, 18, 18])},
                      {"vi_tri": "giua_nhip", "mo_ta_thep": "?", "thanh": th([18, 18])},
                      {"vi_tri": "goi_phai", "mo_ta_thep": "?", "thanh": th([18, 18, 18])}]}
    if dai_dam:
        dam["dai"] = dai_dam
    if dai_cot:
        cot["dai"] = dai_cot
        cot2["dai"] = dai_cot
    return {"toa_do_truc": {"A": 0.0, "B": 5000.0}, "cao_do_moc": {"Mong": 0.0, "Tang2": 4200.0}, "phan_tu": [cot, cot2, dam]}


def test_to_ve_dung_dung_buoc_dai_agent_da_chot():
    kh = ke_hoach.lap_ke_hoach(_du_lieu({"duong_kinh_dai": 8, "buoc_goi": 100, "buoc_giua": 150},
                                        {"duong_kinh_dai": 8, "buoc_dau": 100, "buoc_giua": 200}), CauHinhToVe())
    d = kh.dams[0]
    assert [z.buoc_mm for z in d.vung][:1] == [100] and d.vung[0].duong_kinh == 8
    assert {z.buoc_mm for z in d.vung} <= {100, 150}
    c = kh.cots[0]
    assert c.vung[0].buoc_mm == 100 and c.vung[0].duong_kinh == 8
    assert not [w for w in kh.canh_bao if "bo_tri_dai" in w]  # đã có quyết định ⇒ không cảnh báo


def test_to_ve_canh_bao_khi_agent_chua_goi_bo_tri_dai():
    kh = ke_hoach.lap_ke_hoach(_du_lieu(), CauHinhToVe())
    w = [x for x in kh.canh_bao if "bo_tri_dai" in x]
    assert w and "đai cấu tạo mặc định" in w[0]
    assert kh.dams[0].vung[0].buoc_mm == 150  # mặc định theo skill 06 B8
