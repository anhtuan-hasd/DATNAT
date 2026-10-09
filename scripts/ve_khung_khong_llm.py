"""Vẽ tờ bố trí thép khung từ báo cáo ETABS THẬT mà KHÔNG gọi LLM/API (không tốn phí, không gửi dữ liệu ra ngoài).

Đường đi: báo cáo ETABS → `etabs_reader` (thật) → tool Rule Engine THẬT (chính sách chọn thép tất định thay vai LLM: thử
bậc đường kính tăng dần cho tới khi `tu_kiem_tra` đạt) → tool Drawing/Verification THẬT trên AutoCAD COM.

KHÁC `scripts/chay_pipeline_day_du.py` (4 agent LLM): đây KHÔNG kiểm tra hành vi của LLM — dùng để (1) xem bản vẽ ổn định
đến đâu độc lập với LLM, (2) chạy lại nhanh khi sửa mã vẽ. Rule Engine ở đây chỉ chọn thép theo `As_yc` ETABS (cột kèm
`tu_kiem_tra` N–M), KHÔNG tính uốn dọc η (tool hiện mặc định η=1 — xem docs/agents/_bao_cao_skill_v2/BAO_CAO_DOI_CHIEU_CODE_TAI_LIEU.md).

Chạy (cần AutoCAD cài sẵn, tự mở nếu chưa chạy):
    python scripts/ve_khung_khong_llm.py [file_etabs.xlsx] [thu_muc_xuat] [ten_file]
Mặc định: data/KhungTruc5_BaoCaoETABS_TaiTao.xlsx → output/chay_mau_khong_llm/KHUNG_TRUC5.{pdf,dwg}.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(THU_MUC_GOC))

from src.input_adapter import etabs_reader  # noqa: E402
from src.orchestrator.agents import drawing_agent, rule_engine_agent, verification_agent  # noqa: E402
from src.orchestrator.loops import BoDemVongLap  # noqa: E402

BAC_DUONG_KINH = [[12, 14, 16, 18, 20, 22, 25], [16, 18, 20, 22, 25, 28], [20, 22, 25, 28, 32]]


def _hoi(cau_hoi, lua_chon=None):
    print(f"  [HỎI NGƯỜI DÙNG] {cau_hoi} → tự trả lời 'đồng ý' (chạy không giám sát)")
    return "đồng ý"


def dung_du_lieu(duong_dan: Path) -> tuple[dict, list[str]]:
    """Dữ liệu khung (định dạng `pipeline._du_lieu_lap_rap`) + danh sách vị trí KHÔNG đạt Rule Engine."""
    bo, truc, moc = etabs_reader.doc_etabs_thuc(duong_dan)
    phan_tu, loi = [], []
    for p in bo.phan_tu:
        loai = p.loai.value
        co_q = all(v.noi_luc.Q is not None for v in p.du_lieu_vi_tri)
        nc = rule_engine_agent.NguCanhRuleEngine(hoi_nguoi_dung=_hoi, bo_dem=BoDemVongLap(), khong_co_Q=not co_q and loai == "dam")
        d = rule_engine_agent.tao_dispatch(nc)
        vl = d["tra_vat_lieu"]({"mac_be_tong": p.mac_be_tong, "nhom_thep_doc": p.nhom_thep_doc, "nhom_thep_dai": p.nhom_thep_dai or "CB240-T"})
        Rb, Rbt, Rs, Rsc = vl["be_tong"]["Rb"], vl["be_tong"]["Rbt"], vl["thep_doc"]["Rs"], vl["thep_doc"]["Rsc"]
        vi_tri_json = []
        for v in p.du_lieu_vi_tri:
            tc, neo, dat = {}, {}, False
            for bac in BAC_DUONG_KINH:
                if loai == "cot":
                    tc = d["chon_thep_doc"]({"loai": "cot", "As_target": v.As_yc, "b": p.tiet_dien.b, "h": p.tiet_dien.h, "cover": 40.0, "duong_kinh_cho_phep": bac})
                else:
                    tc = d["chon_thep_doc"]({"loai": "dam", "As_target": v.As_yc, "b": p.tiet_dien.b, "cover": 25.0, "duong_kinh_cho_phep": bac})
                if "loi" in tc:
                    continue
                dk = tc["duong_kinh"] if loai == "cot" else max(t["duong_kinh"] for t in tc["thanh"])
                neo = d["tinh_neo_noi"]({"duong_kinh": dk, "Rs": Rs, "Rbt": Rbt})
                if loai == "cot":
                    kt = d["tu_kiem_tra"]({"loai": "cot", "thong_so": {"N": v.noi_luc.N, "M": v.noi_luc.M, "b": p.tiet_dien.b, "h": p.tiet_dien.h,
                                                                        "As_thuc": tc["As_thuc_moi_phia"], "Rb": Rb, "Rsc": Rsc, "Rs": Rs, "a_prime": 40.0}})
                else:
                    kt = d["tu_kiem_tra"]({"loai": "dam", "thong_so": {"As_thuc": tc["As_thuc"], "As_yc": v.As_yc}})
                dat = bool(kt.get("dat"))
                if dat:
                    break
            if not dat:
                loi.append(f"{p.ten}/{v.vi_tri}")
                continue
            thanh = tc.get("thanh") or [{"duong_kinh": tc["duong_kinh"], "so_luong": tc["tong_so_thanh"]}]
            vi_tri_json.append({"vi_tri": v.vi_tri, "mo_ta_thep": tc.get("mo_ta", "?"), "As_yc": v.As_yc, "thanh": thanh, "thep_doc": tc, "neo_noi": neo})
        if len(vi_tri_json) == len(p.du_lieu_vi_tri):
            phan_tu.append({"ten": p.ten, "loai": loai, "b": p.tiet_dien.b, "h": p.tiet_dien.h, "truc": p.truc, "tang": p.tang,
                            "mac_be_tong": p.mac_be_tong, "nhom_thep_doc": p.nhom_thep_doc, "chieu_dai": p.chieu_dai, "vi_tri": vi_tri_json})
    return {"toa_do_truc": truc, "cao_do_moc": moc, "phan_tu": phan_tu}, loi


def main() -> None:
    import win32com.client

    from src.drawing import backend_com
    from src.orchestrator.shared.phien_cad import PhienCAD

    file = Path(sys.argv[1]) if len(sys.argv) > 1 else THU_MUC_GOC / "data" / "KhungTruc5_BaoCaoETABS_TaiTao.xlsx"
    ra = Path(sys.argv[2]) if len(sys.argv) > 2 else THU_MUC_GOC / "output" / "chay_mau_khong_llm"
    ten = sys.argv[3] if len(sys.argv) > 3 else "KHUNG_TRUC5"
    ra.mkdir(parents=True, exist_ok=True)

    du_lieu, loi = dung_du_lieu(file)
    print(f"Rule Engine: {len(du_lieu['phan_tu'])} phần tử đạt" + (f"; KHÔNG đạt: {loi}" if loi else ""))
    if not du_lieu["phan_tu"]:
        sys.exit("Không có phần tử nào đạt — dừng.")

    try:  # đóng document cũ (tránh SaveAs trùng tên với document còn mở)
        app = win32com.client.GetActiveObject("AutoCAD.Application")
        for i in range(app.Documents.Count - 1, -1, -1):
            for _ in range(20):
                try:
                    app.Documents.Item(i).Close(False)
                    break
                except Exception:
                    time.sleep(0.5)
    except Exception:
        pass
    app = backend_com.ket_noi_autocad()
    doc = backend_com.tao_ban_ve_moi(app)
    phien = PhienCAD(app=app, doc=doc, thu_muc_xuat=str(ra))
    phien.du_lieu_lap_rap = du_lieu
    phien.cau_hinh_to_ve = {"ten_khung_truc": etabs_reader.doc_ten_truc_khung(file)}

    dv = drawing_agent.tao_dispatch(drawing_agent.NguCanhDrawing(hoi_nguoi_dung=_hoi, phien_cad=phien))
    kq = dv["lap_rap_mat_dung_khung"]({})
    print("lap_rap_mat_dung_khung:", kq)
    if "loi" in kq:
        sys.exit(1)
    print("xuat_ban_ve:", dv["xuat_ban_ve"]({"ten_file": ten}))
    kc = verification_agent.kiem_chung_ban_ve(
        verification_agent.NguCanhVerification(hoi_nguoi_dung=_hoi, phien_cad=phien, bo_dem=BoDemVongLap()),
        {"loai_kiem_tra": "mat_dung_khung", "ten_truc_ky_vong": sorted(du_lieu["toa_do_truc"], key=du_lieu["toa_do_truc"].get)},
    )
    print("kiểm chứng:", "ĐẠT" if kc.get("dat") else "CHƯA ĐẠT", kc.get("vi_pham", []))
    print("LƯU Ý: 'ĐẠT' chỉ nghĩa là các kiểm tra tự động của tool đạt (đếm/kích thước/layer/tiêu đề bảng); còn cờ canh_bao và các hạng mục"
          " chưa kiểm được — xem docs/agents/huongdankiemchung/SKILL_KIEM_CHUNG_KY_SU.md. Bản vẽ chưa đủ để phát hành.")


if __name__ == "__main__":
    main()
