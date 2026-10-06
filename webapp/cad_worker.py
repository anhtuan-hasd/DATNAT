"""1 THREAD NỀN DUY NHẤT chạy pipeline (`src/orchestrator/pipeline.chay_toan_bo_khung`)
cho từng job, TUẦN TỰ — KHÔNG BAO GIỜ 2 job chạy song song.

Vì sao cần thế này (CHANGE_REQUESTS.md mục 8): AutoCAD COM Automation là STA
(Single-Threaded Apartment) — gọi vào 1 Document COM từ nhiều thread Python
khác nhau CÙNG LÚC không an toàn (không được COM hỗ trợ đúng cách nếu không
tự marshal con trỏ interface qua `pythoncom.CoMarshalInterThreadInterfaceInStream`,
việc này không đáng làm cho 1 công cụ nội bộ). Toàn bộ `chay_toan_bo_khung`
(không chỉ phần vẽ) chạy trong CÙNG 1 thread worker này để đơn giản — tách
riêng "chỉ phần COM" khỏi "phần LLM" trong 1 job sẽ phức tạp hơn nhiều (phải
tạm dừng/tiếp tục vòng lặp tool-calling giữa chừng) mà không thêm giá trị
thật cho công cụ nội bộ này: file docstring gốc của `webapp/app.py` đã ghi
rõ "server này chỉ chạy local, phục vụ 1 người dùng" — 1 job tại 1 thời điểm
khớp ĐÚNG giới hạn vận hành đã biết đó, không phải cắt giảm tính năng.

Nhiều job gửi tới trong lúc worker đang bận chỉ xếp hàng (FIFO qua
`queue.Queue`) — `Job.trang_thai` của các job đang xếp hàng vẫn là
"dang_cho" cho tới khi worker rảnh và lấy ra chạy, người dùng trang web vẫn
thấy trạng thái cập nhật bình thường, chỉ là job của họ chạy sau job trước.
"""

from __future__ import annotations

import queue
import threading
from typing import Callable

_HANG_DOI: "queue.Queue[Callable[[], None]]" = queue.Queue()
_worker_thread: threading.Thread | None = None
_khoa_khoi_dong = threading.Lock()


def _vong_lap_worker() -> None:
    while True:
        viec = _HANG_DOI.get()
        try:
            viec()
        except Exception:
            # Lỗi nghiệp vụ (vd OPENAI_API_KEY sai, AutoCAD không mở) đã
            # được chính `viec` (jobs.chay_job) tự bắt và ghi vào job.loi —
            # bắt lại ở đây CHỈ để đảm bảo 1 job lỗi không làm CHẾT hẳn
            # thread worker, khiến mọi job sau mãi mãi không được chạy.
            pass
        finally:
            _HANG_DOI.task_done()


def _dam_bao_worker_dang_chay() -> None:
    global _worker_thread
    with _khoa_khoi_dong:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_thread = threading.Thread(target=_vong_lap_worker, daemon=True, name="cad_worker")
            _worker_thread.start()


def gui_viec(viec: Callable[[], None]) -> None:
    """Xếp 1 việc (thường là `functools.partial(jobs.chay_job, job)`) vào
    hàng đợi — khởi động worker thread nếu chưa chạy. Trả về NGAY (không
    chờ việc chạy xong) — Flask request-handler gọi hàm này rồi redirect
    người dùng sang trang theo dõi job, y hệt hành vi cũ (chỉ khác là job
    giờ CHẮC CHẮN chạy tuần tự thay vì mỗi job tự mở 1 thread + tự đụng COM)."""
    _dam_bao_worker_dang_chay()
    _HANG_DOI.put(viec)


def so_viec_dang_cho() -> int:
    """Số job đang xếp hàng (chưa tính job đang chạy) — webapp có thể hiện
    cho người dùng biết vd 'còn 2 job trước bạn' nếu muốn, tuỳ chọn."""
    return _HANG_DOI.qsize()
