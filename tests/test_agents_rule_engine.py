"""Test src/orchestrator/agents/rule_engine_agent.py.

2 nhóm:
1. `trich_phuong_an_thep` — thuần Python, không cần LLM/AutoCAD, kiểm tra kỹ
   trường hợp KHÓ: 1 vị trí phải tự sửa nhiều lần (gọi lại chon_thep_doc)
   trước khi đạt, phải gộp đúng thành 1 vị trí duy nhất, không đếm nhầm
   thành nhiều "vị trí ảo" theo số lần gọi tool.
2. `chay_rule_engine_agent` qua FakeChatProvider (kịch bản dựng sẵn, không
   gọi OpenAI thật) — xác nhận dispatch nối đúng vào rule_engine thật (không
   phải giả lập số liệu) và bo_dem hoạt động.
"""

from __future__ import annotations

from src.orchestrator import agent
from src.orchestrator.agents import rule_engine_agent as rea
from src.orchestrator.loops import BoDemVongLap


def _muc(ten: str, dau_vao: dict, ket_qua: dict) -> dict:
    return {"ten": ten, "dau_vao": dau_vao, "ket_qua": ket_qua}


def test_he_thong_prompt_nap_du_rule_base_chon_thep():
    """Hồi quy — người dùng cung cấp tài liệu hợp nhất 76 trang
    (docs/agents/huongdanchonthep/RULE_BASE_CHON_THEP_KHUNG_BTCT.md) và yêu
    cầu tường minh "bổ sung để hoàn thiện Agent hơn". Khoá lại: HE_THONG_PROMPT
    phải chứa nội dung Phần Q (bảng quyết định trường hợp đặc biệt) — không
    chỉ trích dẫn đường dẫn — cùng cách Drawing Agent đã nạp
    SKILL_VE_KY_THUAT_BTCT.md trước đó."""
    assert "PHẦN Q" in rea.HE_THONG_PROMPT  # bảng ~70 trường hợp Điều kiện→Xử lý
    assert "D2" in rea.HE_THONG_PROMPT  # 1 mã trường hợp đặc trưng (N là lực kéo)
    assert "Khung Trục 5" in rea.HE_THONG_PROMPT  # Phần R, ví dụ đối chiếu dữ liệu thật


# ---------------------------------------------------------------------------
# trich_phuong_an_thep — nhóm 1.
# ---------------------------------------------------------------------------


def test_trich_phuong_an_thep_1_vi_tri_dat_ngay():
    kq = agent.KetQuaVongLapAgent(
        nhat_ky_tool=[
            _muc("tra_vat_lieu", {}, {"be_tong": {"Rb": 14.5}}),
            _muc("chon_thep_doc", {}, {"thanh": [{"duong_kinh": 18, "so_luong": 2}], "As_thuc": 509}),
            _muc("tinh_cot_dai", {}, {"phi_n": 1.0}),
            _muc("tinh_neo_noi", {}, {"L_an": 500}),
            _muc("tu_kiem_tra", {}, {"dat": True, "vi_pham": []}),
        ]
    )
    pa = rea.trich_phuong_an_thep(kq, ten_phan_tu="32", loai="dam", b=220, h=500)
    assert len(pa.vi_tri) == 1
    assert pa.vi_tri[0].dat is True
    assert pa.vi_tri[0].thep_doc["As_thuc"] == 509


def test_trich_phuong_an_thep_tu_sua_1_lan_khong_bi_dem_thanh_2_vi_tri():
    # Vị trí 1: chon_thep_doc (hỏng) -> tu_kiem_tra dat=false, còn lượt -> chon_thep_doc (đạt) -> tu_kiem_tra dat=true.
    # Vị trí 2: chon_thep_doc -> tu_kiem_tra dat=true ngay.
    kq = agent.KetQuaVongLapAgent(
        nhat_ky_tool=[
            _muc("chon_thep_doc", {}, {"thanh": [{"duong_kinh": 12, "so_luong": 2}], "As_thuc": 226}),
            _muc("tu_kiem_tra", {}, {"dat": False, "vi_pham": ["As thiếu"], "so_lan_tu_sua_con_lai": 2}),
            _muc("chon_thep_doc", {}, {"thanh": [{"duong_kinh": 18, "so_luong": 3}], "As_thuc": 763}),
            _muc("tinh_cot_dai", {}, {"phi_n": 1.0}),
            _muc("tu_kiem_tra", {}, {"dat": True, "vi_pham": []}),
            _muc("chon_thep_doc", {}, {"thanh": [{"duong_kinh": 16, "so_luong": 2}], "As_thuc": 402}),
            _muc("tu_kiem_tra", {}, {"dat": True, "vi_pham": []}),
        ]
    )
    pa = rea.trich_phuong_an_thep(kq, ten_phan_tu="32", loai="dam", b=220, h=500)
    assert len(pa.vi_tri) == 2  # KHÔNG phải 3, dù chon_thep_doc bị gọi 3 lần
    # Vị trí 1 phải giữ ĐÚNG lần gọi CUỐI (đã đạt), không phải lần gọi hỏng đầu tiên.
    assert pa.vi_tri[0].thep_doc["As_thuc"] == 763
    assert pa.vi_tri[0].cot_dai == {"phi_n": 1.0}
    assert pa.vi_tri[0].dat is True
    assert pa.vi_tri[1].thep_doc["As_thuc"] == 402
    # Vị trí 2 KHÔNG được "thừa kế" tinh_cot_dai của vị trí 1 (đã reset đúng lúc chốt vị trí 1).
    assert pa.vi_tri[1].cot_dai == {}


def test_trich_phuong_an_thep_het_luot_tu_sua_van_duoc_chot_du_chua_dat():
    kq = agent.KetQuaVongLapAgent(
        nhat_ky_tool=[
            _muc("chon_thep_doc", {}, {"thanh": [{"duong_kinh": 12, "so_luong": 2}], "As_thuc": 226}),
            _muc("tu_kiem_tra", {}, {"dat": False, "vi_pham": ["μ vượt max"], "het_luot_tu_sua": True}),
        ]
    )
    pa = rea.trich_phuong_an_thep(kq, ten_phan_tu="cot_9", loai="cot", b=250, h=250)
    assert len(pa.vi_tri) == 1
    assert pa.vi_tri[0].dat is False
    assert pa.vi_tri[0].vi_pham == ["μ vượt max"]
    assert pa.moi_vi_tri_dat is False  # phần tử KHÔNG được coi là sẵn sàng bàn giao Drawing Agent


def test_chon_thep_doc_cot_As_target_la_moi_phia_khong_chia_doi():
    """Hồi quy — 2 LỖI THẬT liên tiếp, hướng NGƯỢC NHAU, cùng quanh 1 câu hỏi
    "As_target cho cột nghĩa là gì": (1) ban đầu không rõ ràng nên có rủi ro
    hiểu sai; (2) một lần sửa SAI đã thử coi As_yc là TỔNG rồi chia đôi trong
    tool — chạy thật ngay lập tức cho thấy hàng loạt cột KHÔNG ĐẠT tu_kiem_tra
    (N·e > Mu, thiếu thép). Xác nhận độc lập bằng chính công thức TCVN 5574
    mục 2.5 (uon_nen.thiet_ke_cot_doi_xung_lech_tam_be — không liên quan As_yc):
    N,M,b,h,vật liệu thật của phần tử '14' (N=483.24kN, M=91.41kNm, 220x300mm,
    B25/CB500-V) cho As MỖI PHÍA=630.2mm², XẤP XỈ (không phải MỘT NỬA) giá trị
    As_yc gốc (752.76mm², từ PMMArea ETABS phần tử '14') — chia đôi sẽ cho
    ~376mm², thiếu ~40% so với 630.2mm² thật cần. Khoá lại: As_target truyền
    THẲNG vào, không qua phép chia/nhân nào — As_thuc_moi_phia (không phải
    As_thuc_tong) mới là giá trị xấp xỉ As_target."""
    nc = rea.NguCanhRuleEngine(hoi_nguoi_dung=lambda c, l: "đồng ý", bo_dem=BoDemVongLap(), khong_co_Q=False)

    # As_target = As_yc thật (752.76mm², đúng PMMArea gốc của phần tử '14').
    ket_qua = rea.chon_thep_doc(nc, {"As_target": 752.76, "b": 220, "h": 300, "loai": "cot"})

    assert "loi" not in ket_qua
    # As MỖI PHÍA thực phải xấp xỉ As_target truyền vào (dư ít — cho phép dư
    # tới 1 bước đường kính), KHÔNG PHẢI một nửa như lỗi chia-đôi đã gặp.
    assert ket_qua["As_thuc_moi_phia"] >= 752.76
    assert ket_qua["As_thuc_moi_phia"] < 1.5 * 752.76
    # As TỔNG (2 phía) do đó phải xấp xỉ GẤP ĐÔI As_target, không phải bằng nó.
    assert ket_qua["As_thuc_tong"] > 1.5 * 752.76


def test_chon_thep_doc_khong_ep_dung_chung_duong_kinh_giua_cac_vi_tri():
    """Hồi quy — đã thử ép dùng chung 1 đường kính toàn công trình và SAI: dầm
    cần As=57mm² bị gán 2Ø22 (760mm²). Mỗi vị trí phải chọn theo yêu cầu của
    chính nó: As nhỏ -> 2Ø16, As lớn -> 3Ø18, dù cùng 1 phần tử."""
    nc = rea.NguCanhRuleEngine(hoi_nguoi_dung=lambda c, l: "đồng ý", bo_dem=BoDemVongLap(), khong_co_Q=False)
    nho = rea.chon_thep_doc(nc, {"As_target": 57.34, "b": 220, "loai": "dam"})
    lon = rea.chon_thep_doc(nc, {"As_target": 686.02, "b": 220, "loai": "dam"})
    assert nho["thanh"] == [{"duong_kinh": 16, "so_luong": 2}]
    assert lon["thanh"] == [{"duong_kinh": 18, "so_luong": 3}]


def test_chon_thep_doc_khop_thuyet_minh_goc_cot_14():
    nc = rea.NguCanhRuleEngine(hoi_nguoi_dung=lambda c, l: "đồng ý", bo_dem=BoDemVongLap(), khong_co_Q=False)
    kq = rea.chon_thep_doc(nc, {"As_target": 752.76, "b": 220, "h": 300, "loai": "cot"})
    assert (kq["duong_kinh"], kq["so_thanh_canh_b"]) == (18, 3)  # 3Ø18/phía như Bảng 26


# ---------------------------------------------------------------------------
# chay_rule_engine_agent qua FakeChatProvider — nhóm 2.
# ---------------------------------------------------------------------------


class FakeChatProvider:
    def __init__(self, kich_ban: list[dict]):
        self._kich_ban = kich_ban
        self._lan_goi = 0

    def goi(self, he_thong, messages, tools):
        resp = self._kich_ban[self._lan_goi]
        self._lan_goi += 1
        return resp


def _tool_use(id_, name, input_):
    return {"type": "tool_use", "id": id_, "name": name, "input": input_}


def _text(noi_dung):
    return {"type": "text", "text": noi_dung}


def test_chay_rule_engine_agent_1_vi_tri_dam_thanh_cong():
    # Kịch bản: tra_vat_lieu -> chon_thep_doc -> tinh_cot_dai -> tinh_neo_noi
    # -> tu_kiem_tra (dùng đúng số liệu thật do rule_engine tính, không giả
    # lập) -> end_turn. Xác nhận dispatch nối đúng vào rule_engine thật.
    provider = FakeChatProvider(
        [
            {"content": [_tool_use("1", "tra_vat_lieu", {"mac_be_tong": "B25", "nhom_thep_doc": "CB400-V", "nhom_thep_dai": "CB240-T"})]},
            {"content": [_tool_use("2", "chon_thep_doc", {"As_target": 700.0, "b": 220, "loai": "dam"})]},
            {"content": [_text("Đã chọn thép, kết thúc để test đơn giản.")]},
        ]
    )
    ket_qua, nc = rea.chay_rule_engine_agent(provider, "Dầm 32, gối trái", hoi_nguoi_dung=lambda c, l: "đồng ý")

    assert ket_qua.dung_vi == "end_turn"
    goi_tra_vat_lieu = [t for t in ket_qua.nhat_ky_tool if t["ten"] == "tra_vat_lieu"][0]
    assert goi_tra_vat_lieu["ket_qua"]["be_tong"]["Rb"] > 0  # số liệu THẬT từ vat_lieu.py, không phải giả lập

    goi_chon_thep = [t for t in ket_qua.nhat_ky_tool if t["ten"] == "chon_thep_doc"][0]
    assert goi_chon_thep["ket_qua"]["As_thuc"] >= 700.0
    # Mọi đường kính chọn ra phải >= 12mm (CHANGE_REQUESTS.md mục 6).
    assert all(th["duong_kinh"] >= 12 for th in goi_chon_thep["ket_qua"]["thanh"])


def test_chay_rule_engine_agent_khong_co_Q_chan_tinh_cot_dai():
    # Nguồn ETABS thật không có Q thô cho dầm — dù LLM vẫn cố gọi
    # tinh_cot_dai, tool PHẢI bị chặn ở tầng code (không phải chỉ dặn prompt).
    provider = FakeChatProvider(
        [
            {"content": [_tool_use("1", "tinh_cot_dai", {"Q": 0, "Rb": 14.5, "Rbt": 1.05, "Rsw": 170, "b": 220, "h0": 260})]},
            {"content": [_text("xong")]},
        ]
    )
    ket_qua, _ = rea.chay_rule_engine_agent(provider, "test", hoi_nguoi_dung=lambda c, l: "đồng ý", khong_co_Q=True)
    goi = ket_qua.nhat_ky_tool[0]
    assert "loi" in goi["ket_qua"]
    assert "Qb1" not in goi["ket_qua"]  # KHÔNG phải kết quả tính thật


def test_chay_rule_engine_agent_khong_co_Q_tu_kiem_tra_chi_kiem_as_doc():
    thong_so = {"As_thuc": 226.2, "As_yc": 102.78, "Q": 999}  # Q bịa — phải bị NGÓ LƠ hoàn toàn
    provider = FakeChatProvider(
        [
            {"content": [_tool_use("1", "tu_kiem_tra", {"loai": "dam", "thong_so": thong_so})]},
            {"content": [_text("xong")]},
        ]
    )
    ket_qua, _ = rea.chay_rule_engine_agent(provider, "test", hoi_nguoi_dung=lambda c, l: "đồng ý", khong_co_Q=True)
    goi = ket_qua.nhat_ky_tool[0]["ket_qua"]
    assert goi["dat"] is True  # As_thuc=226.2 >= As_yc=102.78
    assert "canh_bao" in goi


def test_chay_rule_engine_agent_khong_co_Q_khong_anh_huong_cot():
    # Cờ khong_co_Q chỉ áp dụng cho DẦM — cột vẫn chạy verify.kiem_tra_tong_hop_cot thật bình thường.
    thong_so = {"As_thuc": 760.2, "b": 220, "h": 300, "N": 546.427, "M": 87.0233, "Rb": 14.5, "Rsc": 435}
    provider = FakeChatProvider(
        [
            {"content": [_tool_use("1", "tu_kiem_tra", {"loai": "cot", "thong_so": thong_so})]},
            {"content": [_text("xong")]},
        ]
    )
    ket_qua, _ = rea.chay_rule_engine_agent(provider, "test", hoi_nguoi_dung=lambda c, l: "đồng ý", khong_co_Q=True)
    goi = ket_qua.nhat_ky_tool[0]["ket_qua"]
    assert "canh_bao" not in goi  # tool THẬT đã chạy, không phải nhánh chặn/cảnh báo
    assert "dat" in goi


def test_chay_rule_engine_agent_chan_duong_kinh_duoi_12mm_tu_llm():
    # LLM (giả lập) cố tình nới duong_kinh_cho_phep xuống 8mm lúc "tự sửa" —
    # phải bị chặn ở tầng code (cot_doc.py), KHÔNG trả về đường kính < 12mm.
    provider = FakeChatProvider(
        [
            {"content": [_tool_use("1", "chon_thep_doc", {"As_target": 50.0, "b": 250, "loai": "dam", "duong_kinh_cho_phep": [8, 10, 12]})]},
            {"content": [_text("xong")]},
        ]
    )
    ket_qua, _ = rea.chay_rule_engine_agent(provider, "test", hoi_nguoi_dung=lambda c, l: "đồng ý")
    goi = ket_qua.nhat_ky_tool[0]
    assert all(th["duong_kinh"] >= 12 for th in goi["ket_qua"]["thanh"])
