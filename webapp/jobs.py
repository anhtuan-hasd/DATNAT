"""Quản lý "job" (1 lượt xử lý 1 file người dùng tải lên) cho webapp — chạy
`src/orchestrator/pipeline.chay_toan_bo_khung` (4 agent) qua `cad_worker`
(hàng đợi 1-thread, xem docstring module đó), cho phép trang web hỏi-đáp với
LLM qua cơ chế chặn/mở khoá (`threading.Event`) thay vì `input()` dòng lệnh.

Module này KHÔNG chứa logic nghiệp vụ TCVN nào — chỉ là lớp "ống dẫn" nối
web request/response với `pipeline.chay_toan_bo_khung` đã có sẵn (Phase 6),
đúng tinh thần không sửa lại code lõi cho mục đích web.

Viết lại HOÀN TOÀN so với bản trước (CHANGE_REQUESTS.md mục 8): bản cũ tự
mình dò sheet/gọi LLM 1 lần duy nhất/ghép log thủ công qua `tools.py` cũ (13
tool phẳng) — giờ TOÀN BỘ việc đó (kể cả nhận diện ETABS thật, suy luận hình
học, lặp qua từng phần tử, lắp ráp mặt đứng khung) đã nằm gọn trong
`pipeline.chay_toan_bo_khung`, `jobs.py` chỉ cần gọi ĐÚNG 1 LẦN và chuyển
tiếp `quan_sat`/`hoi_nguoi_dung` — file này vì vậy NGẮN HƠN NHIỀU so với bản
cũ, không phải vì làm ít việc hơn mà vì việc đó giờ thuộc về đúng lớp của
nó (orchestrator), không lặp lại ở tầng web nữa.
"""

from __future__ import annotations

import sys
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path

GOC_DU_AN = Path(__file__).parent.parent
sys.path.insert(0, str(GOC_DU_AN))

from src.orchestrator import agent, pipeline  # noqa: E402

from . import cad_worker  # noqa: E402

THU_MUC_OUTPUT = GOC_DU_AN / "output" / "webapp"
THU_MUC_UPLOAD = GOC_DU_AN / "output" / "webapp_upload"


@dataclass
class MucNhatKy:
    loai: str  # "he_thong" | "tool" | "cau_hoi" | "tra_loi" | "loi" | "ket_thuc"
    noi_dung: str
    chi_tiet: dict | None = None


@dataclass
class Job:
    id: str
    duong_dan_file: Path
    trang_thai: str = "dang_cho"  # dang_cho -> dang_chay -> can_tra_loi <-> dang_chay -> xong | loi
    nhat_ky: list[MucNhatKy] = field(default_factory=list)
    cau_hoi_dang_cho: dict | None = None
    duong_dan_pdf: str | None = None  # đường dẫn TUYỆT ĐỐI trên đĩa — route Flask tự lấy basename khi phục vụ
    duong_dan_dwg: str | None = None
    so_phan_tu_dat: int = 0
    tong_so_phan_tu: int = 0
    loi: str | None = None

    _event_tra_loi: threading.Event = field(default_factory=threading.Event, repr=False)
    _tra_loi: str | None = field(default=None, repr=False)
    _khoa: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def thu_muc(self) -> Path:
        d = THU_MUC_OUTPUT / self.id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def ghi_log(self, loai: str, noi_dung: str, chi_tiet: dict | None = None) -> None:
        with self._khoa:
            self.nhat_ky.append(MucNhatKy(loai, noi_dung, chi_tiet))

    def hoi_nguoi_dung(self, cau_hoi: str, lua_chon: list[str] | None) -> str:
        """Callback truyền thẳng vào `pipeline.chay_toan_bo_khung` — CHẶN
        (block) worker thread cho đến khi trang web POST câu trả lời tới
        `nhan_tra_loi()`. Chữ ký hàm KHÔNG đổi so với bản trước (chỉ khác là
        giờ được truyền vào pipeline.py thay vì tools.py cũ) nên logic chặn/
        mở khoá này giữ nguyên."""
        self.ghi_log("cau_hoi", cau_hoi, {"lua_chon": lua_chon})
        with self._khoa:
            self.cau_hoi_dang_cho = {"cau_hoi": cau_hoi, "lua_chon": lua_chon}
            self.trang_thai = "can_tra_loi"
            self._event_tra_loi.clear()
        self._event_tra_loi.wait()  # NGHẼN Ở ĐÂY đến khi có người trả lời qua web
        with self._khoa:
            tra_loi = self._tra_loi or ""
            self.cau_hoi_dang_cho = None
            self.trang_thai = "dang_chay"
        self.ghi_log("tra_loi", tra_loi)
        return tra_loi

    def nhan_tra_loi(self, tra_loi: str) -> bool:
        with self._khoa:
            if self.trang_thai != "can_tra_loi":
                return False
            self._tra_loi = tra_loi
        self._event_tra_loi.set()
        return True

    def quan_sat(self, giai_doan: str, ten: str, ket_qua_agent) -> None:
        """`quan_sat` (observer) truyền vào `pipeline.chay_toan_bo_khung` —
        gọi mỗi khi 1 trong 4 agent con chạy xong 1 phiên. Log cả dòng tóm
        tắt LẪN từng tool đã gọi bên trong phiên đó (giữ độ chi tiết y hệt
        UI cũ, dù nay đến từ `KetQuaVongLapAgent.nhat_ky_tool` thay vì tự bọc
        dispatch thủ công như `_chay_1_yeu_cau_co_log` bản trước)."""
        self.ghi_log(
            "he_thong",
            f"=== [{giai_doan}] {ten} — {ket_qua_agent.so_lan_goi_model} lượt gọi model, "
            f"dừng vì: {ket_qua_agent.dung_vi} ===",
        )
        for muc in ket_qua_agent.nhat_ky_tool:
            self.ghi_log("tool", muc["ten"], {"dau_vao": muc["dau_vao"], "ket_qua": muc["ket_qua"]})


_JOBS: dict[str, Job] = {}
_JOBS_KHOA = threading.Lock()


def tao_job(duong_dan_file: Path) -> Job:
    job = Job(id=uuid.uuid4().hex[:12], duong_dan_file=duong_dan_file)
    with _JOBS_KHOA:
        _JOBS[job.id] = job
    return job


def lay_job(job_id: str) -> Job | None:
    with _JOBS_KHOA:
        return _JOBS.get(job_id)


def chay_job(job: Job) -> None:
    """Chạy TOÀN BỘ pipeline cho 1 job — gọi ĐÚNG 1 lần
    `pipeline.chay_toan_bo_khung`, không tự lặp/tự dò sheet/tự ghép log như
    bản trước (nay thuộc về pipeline.py). Hàm này chạy TRONG worker thread
    của `cad_worker` (xem `bat_dau_job_nen`), không phải thread riêng của
    job — vì vậy KHÔNG được có 2 job gọi hàm này đồng thời (đảm bảo bởi
    `cad_worker` xử lý hàng đợi tuần tự)."""
    job.trang_thai = "dang_chay"
    try:
        job.ghi_log("he_thong", f"Bắt đầu xử lý '{job.duong_dan_file.name}'...")
        # max_completion_tokens=8192 (KHÔNG phải 800 như trước) — LỖI THẬT đã
        # gặp: tool lap_rap_mat_dung_khung yêu cầu model "SAO CHÉP NGUYÊN VĂN"
        # 1 khối JSON lớn (toa_do_truc/cao_do_moc/phan_tu của TOÀN BỘ phần tử,
        # vd 20 phần tử x tới 3 vị trí/phần tử) làm tham số tool — với
        # max_completion_tokens=800, OpenAI cắt cụt phần input đang sinh giữa
        # chừng, JSON dở dang không parse được, agent.py nuốt lỗi JSONDecodeError
        # và trả input={} rỗng, khiến tool báo "thiếu khóa toa_do_truc" dù dữ
        # liệu đã có sẵn trong tin nhắn. Nâng cap KHÔNG tốn thêm chi phí cho
        # các bước nhỏ khác (OpenAI chỉ tính phí theo token THỰC SINH, không
        # theo giá trị max_completion_tokens khai báo).
        provider = agent.OpenAIChatProvider(max_completion_tokens=8192)
        ket_qua = pipeline.chay_toan_bo_khung(
            nha_cung_cap=provider,
            duong_dan_file=str(job.duong_dan_file),
            hoi_nguoi_dung=job.hoi_nguoi_dung,
            thu_muc_xuat_ban_ve=str(job.thu_muc),
            ten_khung=job.id,
            quan_sat=job.quan_sat,
        )

        for dong in ket_qua.nhat_ky:
            job.ghi_log("he_thong", dong)

        job.duong_dan_pdf = ket_qua.duong_dan_pdf
        job.duong_dan_dwg = ket_qua.duong_dan_dwg
        job.so_phan_tu_dat = ket_qua.so_phan_tu_dat
        job.tong_so_phan_tu = len(ket_qua.ket_qua_phan_tu)

        job.trang_thai = "xong"
        job.ghi_log(
            "ket_thuc",
            f"Hoàn tất — {job.so_phan_tu_dat}/{job.tong_so_phan_tu} phần tử đạt tự kiểm tra + kiểm chứng bản vẽ.",
        )
    except Exception as e:  # không để lỗi bất kỳ làm treo job mãi mãi trên web, hay làm chết worker thread
        job.loi = f"{type(e).__name__}: {e}"
        job.ghi_log("loi", job.loi)
        job.trang_thai = "loi"


def bat_dau_job_nen(job: Job) -> None:
    """Xếp job vào hàng đợi `cad_worker` — KHÔNG tự mở thread riêng nữa
    (khác bản trước dùng `threading.Thread(...).start()` cho MỖI job, có
    thể khiến nhiều job cùng đụng AutoCAD COM đồng thời — xem
    `cad_worker.py`)."""
    cad_worker.gui_viec(lambda: chay_job(job))
