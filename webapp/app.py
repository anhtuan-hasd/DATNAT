"""Trang web nội bộ (chạy trên máy bạn, KHÔNG public) cho toàn bộ pipeline
4-agent: tải file Excel/CSV/ETABS thật lên -> pipeline.chay_toan_bo_khung tự
chạy Input Adapter -> Rule Engine -> Drawing -> Verification cho từng phần tử
-> hỏi lại qua khung chat khi không chắc chắn -> xem bản vẽ PDF ngay trên
trang, tải DWG.

Chạy: python webapp/app.py
Rồi mở trình duyệt: http://127.0.0.1:5000

OPENAI_API_KEY được tự nạp từ file .env ở gốc dự án (xem dotenv bên dưới)
nếu có; nếu không có .env, vẫn có thể đặt trực tiếp bằng biến môi trường
trước khi chạy (xem docs/HUONG_DAN_CHAY.md). CẦN mở sẵn AutoCAD trước khi
tải file lên — pipeline vẽ 100% qua AutoCAD COM (không còn dự phòng ezdxf).
"""

from __future__ import annotations

import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).parent.parent
sys.path.insert(0, str(THU_MUC_GOC))

from dotenv import load_dotenv

load_dotenv(THU_MUC_GOC / ".env")  # nạp OPENAI_API_KEY từ .env nếu có, không báo lỗi nếu thiếu file

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

from webapp import jobs

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB — đủ cho file Excel/CSV thông thường

DUOI_FILE_CHO_PHEP = {".xlsx", ".xls", ".csv"}


@app.route("/")
def trang_chu():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def tai_file_len():
    file = request.files.get("file")
    if file is None or file.filename == "":
        return render_template("index.html", loi="Bạn chưa chọn file."), 400

    duoi = Path(file.filename).suffix.lower()
    if duoi not in DUOI_FILE_CHO_PHEP:
        return render_template("index.html", loi=f"Chỉ chấp nhận file {sorted(DUOI_FILE_CHO_PHEP)}."), 400

    jobs.THU_MUC_UPLOAD.mkdir(parents=True, exist_ok=True)
    job = jobs.tao_job(duong_dan_file=Path())  # tạm, gán đường dẫn thật ngay dưới
    duong_dan_luu = jobs.THU_MUC_UPLOAD / f"{job.id}{duoi}"
    file.save(duong_dan_luu)
    job.duong_dan_file = duong_dan_luu

    jobs.bat_dau_job_nen(job)
    return redirect(url_for("trang_job", job_id=job.id))


@app.route("/job/<job_id>")
def trang_job(job_id: str):
    job = jobs.lay_job(job_id)
    if job is None:
        return render_template("index.html", loi="Không tìm thấy job (có thể server đã khởi động lại)."), 404
    return render_template("job.html", job_id=job_id, ten_file=job.duong_dan_file.name)


@app.route("/api/job/<job_id>/status")
def api_trang_thai_job(job_id: str):
    job = jobs.lay_job(job_id)
    if job is None:
        return jsonify({"loi": "khong_tim_thay_job"}), 404
    return jsonify(
        {
            "trang_thai": job.trang_thai,
            "nhat_ky": [
                {"loai": m.loai, "noi_dung": m.noi_dung, "chi_tiet": m.chi_tiet} for m in job.nhat_ky
            ],
            "cau_hoi_dang_cho": job.cau_hoi_dang_cho,
            "co_pdf": job.duong_dan_pdf is not None,
            "co_dwg": job.duong_dan_dwg is not None,
            "so_phan_tu_dat": job.so_phan_tu_dat,
            "tong_so_phan_tu": job.tong_so_phan_tu,
            "loi": job.loi,
        }
    )


@app.route("/api/job/<job_id>/answer", methods=["POST"])
def api_tra_loi_job(job_id: str):
    job = jobs.lay_job(job_id)
    if job is None:
        return jsonify({"ok": False, "loi": "khong_tim_thay_job"}), 404
    tra_loi = (request.json or {}).get("tra_loi", "")
    da_nhan = job.nhan_tra_loi(tra_loi)
    return jsonify({"ok": da_nhan})


@app.route("/job/<job_id>/pdf")
def pdf_ket_qua(job_id: str):
    """Xem trước bản vẽ tổng thể (PDF, mọi mặt cắt + mặt đứng khung + bảng
    thống kê + khung tên trên 1 tờ) NGAY trên trình duyệt qua <iframe> —
    thay cho gallery ảnh PNG bản trước (ezdxf đã bị loại bỏ, không còn cách
    render PNG offline không cần AutoCAD nữa — PDF do chính AutoCAD xuất qua
    COM, trình duyệt tự hiển thị được, không cần thêm thư viện nào)."""
    job = jobs.lay_job(job_id)
    if job is None or job.duong_dan_pdf is None:
        return "Chưa có bản vẽ PDF cho job này", 404
    return send_file(job.duong_dan_pdf, mimetype="application/pdf")


@app.route("/job/<job_id>/dwg")
def dwg_ket_qua(job_id: str):
    job = jobs.lay_job(job_id)
    if job is None or job.duong_dan_dwg is None:
        return "Chưa có bản vẽ DWG cho job này", 404
    return send_file(job.duong_dan_dwg, as_attachment=True)


if __name__ == "__main__":
    print("Mở trình duyệt tại: http://127.0.0.1:5000")
    print("LƯU Ý: mở sẵn AutoCAD trước khi tải file lên (vẽ 100% qua AutoCAD COM).")
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=False)
