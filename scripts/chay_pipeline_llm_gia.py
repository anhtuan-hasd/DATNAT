"""Chạy TOÀN BỘ pipeline 4 agent (`pipeline.chay_toan_bo_khung` — đúng điểm vào thật) với một LLM GIẢ dựa trên luật:
mô phỏng việc agent làm theo prompt/skill (không API, không tốn phí, không gửi dữ liệu ra ngoài), nhưng mọi TOOL, hợp đồng dữ
liệu giữa agent, tờ vẽ AutoCAD và Verification đều là code THẬT.

Dùng để: (1) kiểm tra điều phối 4 agent + dữ liệu giữa chúng + bản vẽ sau khi sửa code, không tốn tiền API; (2) so với chạy
bằng LLM thật (`scripts/chay_pipeline_day_du.py`) — khác biệt còn lại chỉ là QUYẾT ĐỊNH của LLM (gọi tool nào, chọn Ø nào).
LLM giả đi đúng quy trình trong system prompt: tra_vat_lieu → (chon_thep_doc → tinh_neo_noi → tu_kiem_tra, tự sửa bậc Ø khi
chưa đạt) cho từng vị trí → bo_tri_dai 1 lần/phần tử; Drawing: lap_rap_mat_dung_khung → xuat_ban_ve; Verification: kiem_chung_ban_ve.

Chạy (cần AutoCAD): python scripts/chay_pipeline_llm_gia.py [file_etabs.xlsx] [thu_muc_xuat]
"""

import json, re, sys, time
from pathlib import Path
THU_MUC_GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(THU_MUC_GOC))
from src.orchestrator import pipeline

FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else THU_MUC_GOC / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"
RA = Path(sys.argv[2]) if len(sys.argv) > 2 else THU_MUC_GOC / "output" / "chay_llm_gia"
RA.mkdir(parents=True, exist_ok=True)
BAC = [[12, 14, 16, 18, 20, 22, 25], [16, 18, 20, 22, 25, 28], [20, 22, 25, 28, 32]]


def tu(i, n, inp): return {"type": "tool_use", "id": i, "name": n, "input": inp}
def tx(s): return {"type": "text", "text": s}


def ket_qua_tool(messages, id_):
    for m in messages:
        if m["role"] == "user" and isinstance(m["content"], list):
            for b in m["content"]:
                if b.get("type") == "tool_result" and b["tool_use_id"] == id_:
                    return json.loads(b["content"])
    return None


class LLMGia:
    """Mỗi lần goi(): xác định agent theo bộ tool, rồi đi theo kịch bản luật dựa trên tin nhắn đầu + kết quả tool trước đó."""
    def __init__(self): self.so_lan = 0

    def goi(self, he_thong, messages, tools):
        self.so_lan += 1
        ten_tool = {t["name"] for t in tools}
        dau = messages[0]["content"]
        lan = sum(1 for m in messages if m["role"] == "assistant")
        if "doc_etabs_that" in ten_tool:
            if lan == 0:
                duong_dan = re.search(r"đường dẫn: (.+)$", dau).group(1).strip()
                return {"content": [tu("a1", "doc_etabs_that", {"duong_dan": duong_dan})]}
            return {"content": [tx("Đã đọc báo cáo ETABS thật.")]}
        if "lap_rap_mat_dung_khung" in ten_tool:
            if lan == 0:
                return {"content": [tu("d1", "lap_rap_mat_dung_khung", {})]}
            if lan == 1:
                ten = re.search(r"ten_file='([^']+)'", dau).group(1)
                return {"content": [tu("d2", "xuat_ban_ve", {"ten_file": ten})]}
            return {"content": [tx("Đã lắp ráp và xuất bản vẽ.")]}
        if "kiem_chung_ban_ve" in ten_tool:
            if lan == 0:
                inp = {"loai_kiem_tra": "mat_dung_khung"}
                m = re.search(r"ten_truc_ky_vong=(\[.*?\])", dau)
                if m: inp["ten_truc_ky_vong"] = json.loads(m.group(1))
                return {"content": [tu("v1", "kiem_chung_ban_ve", inp)]}
            return {"content": [tx("Kiểm chứng xong.")]}
        # ---- Rule Engine ----
        return self._rule_engine(dau, messages, lan)

    def _rule_engine(self, dau, messages, lan):
        loai = "cot" if "CỘT" in dau.split("\n")[0] else "dam"
        mb = re.search(r"b=([\d.]+)mm, h=([\d.]+)mm, mác bê tông (\w+), nhóm thép dọc ([\w-]+)", dau)
        b, h, mac, nhom = float(mb.group(1)), float(mb.group(2)), mb.group(3), mb.group(4)
        vts = re.findall(r"- Vị trí '([^']+)': As_yc=([\d.]+)mm², M=([\w.\-]+), N=([\w.\-]+), Q:", dau)
        da_goi = [(m_["name"], m_["id"], m_["input"]) for m in messages if m["role"] == "assistant" for m_ in m["content"] if m_.get("type") == "tool_use"]
        if not da_goi:
            return {"content": [tu("t0", "tra_vat_lieu", {"mac_be_tong": mac, "nhom_thep_doc": nhom, "nhom_thep_dai": "CB240-T"})]}
        vl = ket_qua_tool(messages, "t0")
        Rb, Rbt, Rs, Rsc = vl["be_tong"]["Rb"], vl["be_tong"]["Rbt"], vl["thep_doc"]["Rs"], vl["thep_doc"]["Rsc"]
        so_dat, so_chon = 0, 0  # số vị trí đã đạt; số lần chon_thep_doc trong lần thử hiện tại của vị trí đang xử lý
        for name, id_, inp in da_goi:
            if name == "chon_thep_doc":
                so_chon += 1
            elif name == "tu_kiem_tra":
                kq = ket_qua_tool(messages, id_)
                if kq and kq.get("dat"):
                    so_dat, so_chon = so_dat + 1, 0
        ten_cuoi, id_cuoi, _ = da_goi[-1]
        kq_cuoi = ket_qua_tool(messages, id_cuoi) or {}
        if ten_cuoi == "bo_tri_dai":
            return {"content": [tx("Đã chọn thép cho mọi vị trí và chốt cốt đai theo vùng.")]}
        if so_dat >= len(vts):
            return {"content": [tu("bt", "bo_tri_dai", {"loai": loai, "h": h if loai == "dam" else max(b, h)})]}
        vt, as_yc, M, N = vts[so_dat]
        as_yc = float(as_yc)
        id_ = f"s{self.so_lan}"
        if ten_cuoi in ("tra_vat_lieu",) or (ten_cuoi == "tu_kiem_tra" and kq_cuoi.get("dat")):
            return {"content": [tu(id_, "chon_thep_doc", self._chon(loai, as_yc, b, h, BAC[0]))]}
        if ten_cuoi == "tu_kiem_tra":  # chưa đạt → tự sửa: bậc Ø kế
            return {"content": [tu(id_, "chon_thep_doc", self._chon(loai, as_yc, b, h, BAC[min(so_chon, len(BAC) - 1)]))]}
        if ten_cuoi == "chon_thep_doc":
            if "loi" in kq_cuoi:
                return {"content": [tu(id_, "chon_thep_doc", self._chon(loai, as_yc, b, h, BAC[min(so_chon, len(BAC) - 1)]))]}
            dk = kq_cuoi["duong_kinh"] if loai == "cot" else max(t_["duong_kinh"] for t_ in kq_cuoi["thanh"])
            return {"content": [tu(id_, "tinh_neo_noi", {"duong_kinh": dk, "Rs": Rs, "Rbt": Rbt})]}
        if ten_cuoi == "tinh_neo_noi":
            chon = next(ket_qua_tool(messages, i_) for n_, i_, _ in reversed(da_goi) if n_ == "chon_thep_doc" and "loi" not in (ket_qua_tool(messages, i_) or {}))
            if loai == "cot":
                ts = {"N": float(N), "M": float(M), "b": b, "h": h, "As_thuc": chon["As_thuc_moi_phia"], "Rb": Rb, "Rsc": Rsc, "Rs": Rs, "a_prime": 40.0}
            else:
                ts = {"As_thuc": chon["As_thuc"], "As_yc": as_yc}
            return {"content": [tu(id_, "tu_kiem_tra", {"loai": loai, "thong_so": ts})]}
        return {"content": [tx("?")]}

    @staticmethod
    def _chon(loai, as_yc, b, h, bac):
        if loai == "cot":
            return {"loai": "cot", "As_target": as_yc, "b": b, "h": h, "cover": 40.0, "duong_kinh_cho_phep": bac}
        return {"loai": "dam", "As_target": as_yc, "b": b, "cover": 25.0, "duong_kinh_cho_phep": bac}


# KHÔNG đóng document AutoCAD đang mở (có thể là của người dùng/webapp). Tên file xuất có hậu tố thời gian để SaveAs không
# trùng với document cũ còn mở trong AutoCAD.

llm = LLMGia()
t0 = time.time()
kq = pipeline.chay_toan_bo_khung(
    nha_cung_cap=llm, duong_dan_file=str(FILE), hoi_nguoi_dung=lambda c, l=None: "đồng ý",
    thu_muc_xuat_ban_ve=str(RA), ten_khung="KHUNG_TRUC5_GIA_" + time.strftime("%H%M%S"),
    quan_sat=lambda gd, ten, k: print(f"  [{gd}] {ten} — {k.so_lan_goi_model} lượt, dừng: {k.dung_vi}") if gd != "rule_engine" else None,
)
print(f"({time.time()-t0:.0f}s, {llm.so_lan} lượt LLM giả)")
for d in kq.nhat_ky[-8:]:
    print("  ", d[:200])
print("PDF:", kq.duong_dan_pdf)
print("đạt:", kq.so_phan_tu_dat, "/", len(kq.ket_qua_phan_tu), "| kiểm chứng tổng thể:", kq.kiem_chung_tong_the)
print("phần tử không đạt:", [(k.ten_phan_tu, k.trang_thai) for k in kq.ket_qua_phan_tu if k.trang_thai != "dat"])
print("có dai:", sum(1 for k in kq.ket_qua_phan_tu if k.phuong_an_thep and k.phuong_an_thep.dai), "/", len(kq.ket_qua_phan_tu))
