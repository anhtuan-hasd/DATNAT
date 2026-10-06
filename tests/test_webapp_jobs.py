"""Test webapp/jobs.py + webapp/cad_worker.py — viết lại hoàn toàn cho kiến
trúc 4-agent (CHANGE_REQUESTS.md mục 8). Các test cũ về cơ chế "chặn
tinh_cot_dai khi thiếu Q" đã CHUYỂN sang `tests/test_agents_rule_engine.py`
(cơ chế đó nay nằm trong `rule_engine_agent.py`, không còn ở tầng webapp —
lợi ích: cả webapp lẫn CLI script đều được bảo vệ như nhau).

File này test 2 việc THUẦN webapp, không cần OpenAI/AutoCAD thật:
1. `Job.hoi_nguoi_dung`/`nhan_tra_loi` — cơ chế chặn/mở khoá thread bằng
   `threading.Event`, không đổi so với bản trước nhưng cần xác nhận lại vì
   đây là phần "ống dẫn" quan trọng nhất nối web request với pipeline.
2. `cad_worker` — hàng đợi 1-thread xử lý TUẦN TỰ, không chạy song song.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

from webapp import cad_worker, jobs

_FILE_GIA = Path("khong_dung_toi.csv")


def test_hoi_nguoi_dung_chan_thread_den_khi_co_tra_loi():
    job = jobs.Job(id="t1", duong_dan_file=_FILE_GIA)
    ket_qua: list[str] = []

    def _luong_hoi():
        ket_qua.append(job.hoi_nguoi_dung("Câu hỏi test?", ["a", "b"]))

    t = threading.Thread(target=_luong_hoi)
    t.start()

    # Đợi tới khi job chuyển sang "can_tra_loi" (thread kia đã NGHẼN ở .wait()).
    for _ in range(50):
        if job.trang_thai == "can_tra_loi":
            break
        time.sleep(0.02)
    assert job.trang_thai == "can_tra_loi"
    assert job.cau_hoi_dang_cho == {"cau_hoi": "Câu hỏi test?", "lua_chon": ["a", "b"]}

    da_nhan = job.nhan_tra_loi("đồng ý")
    t.join(timeout=2)

    assert da_nhan is True
    assert ket_qua == ["đồng ý"]
    assert job.trang_thai == "dang_chay"  # nhan_tra_loi trả nó về dang_chay, KHÔNG tự chuyển "xong"
    assert job.cau_hoi_dang_cho is None


def test_nhan_tra_loi_that_bai_khi_khong_dang_cho():
    job = jobs.Job(id="t2", duong_dan_file=_FILE_GIA)
    assert job.trang_thai == "dang_cho"
    assert job.nhan_tra_loi("đồng ý") is False  # không có ai đang chờ trả lời


def test_quan_sat_ghi_ca_dong_tom_tat_lan_tung_tool():
    job = jobs.Job(id="t3", duong_dan_file=_FILE_GIA)

    class _KetQuaAgentGia:
        so_lan_goi_model = 3
        dung_vi = "end_turn"
        nhat_ky_tool = [{"ten": "tra_vat_lieu", "dau_vao": {"mac_be_tong": "B25"}, "ket_qua": {"be_tong": {"Rb": 14.5}}}]

    job.quan_sat("rule_engine", "32", _KetQuaAgentGia())

    dong_he_thong = [n for n in job.nhat_ky if n.loai == "he_thong"]
    dong_tool = [n for n in job.nhat_ky if n.loai == "tool"]
    assert any("rule_engine" in d.noi_dung and "32" in d.noi_dung for d in dong_he_thong)
    assert len(dong_tool) == 1
    assert dong_tool[0].noi_dung == "tra_vat_lieu"
    assert dong_tool[0].chi_tiet["ket_qua"]["be_tong"]["Rb"] == 14.5


def test_cad_worker_chay_tuan_tu_khong_song_song():
    """2 'việc' gửi gần như đồng thời — cad_worker PHẢI chạy lần lượt (KHÔNG
    2 việc chạy chồng lên nhau), đúng lý do AutoCAD COM là STA."""
    dang_chay: list[bool] = [False]
    tung_chong_lan: list[bool] = [False]
    thu_tu: list[int] = []

    def _viec(n: int):
        if dang_chay[0]:
            tung_chong_lan[0] = True  # phát hiện việc khác đang chạy CÙNG LÚC -> SAI
        dang_chay[0] = True
        time.sleep(0.05)
        thu_tu.append(n)
        dang_chay[0] = False

    cad_worker.gui_viec(lambda: _viec(1))
    cad_worker.gui_viec(lambda: _viec(2))
    cad_worker.gui_viec(lambda: _viec(3))

    # Chờ hàng đợi xử lý xong (tối đa ~2s, đủ dư cho 3 việc x 0,05s).
    for _ in range(100):
        if len(thu_tu) == 3:
            break
        time.sleep(0.02)

    assert thu_tu == [1, 2, 3]  # đúng thứ tự FIFO
    assert tung_chong_lan[0] is False  # không có 2 việc nào chạy chồng lên nhau
