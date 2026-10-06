"""
Lắp ráp bản vẽ MẶT ĐỨNG KHUNG TỔNG THỂ từ danh sách PhanTuKhung (Input
Adapter, mục 5 bước 2 — có thêm trường tuỳ chọn `truc`/`tang`) cộng với nhãn
thép ĐÃ ĐƯỢC RULE ENGINE CHỌN THẬT cho từng phần tử qua pipeline (không bịa,
không copy số liệu từ nguồn tham khảo nào).

Quy ước dữ liệu (đọc trực tiếp từ 2 trường tuỳ chọn `truc`/`tang` của
PhanTuKhung — KHÔNG bắt buộc, file không có 2 cột này thì bỏ qua bước vẽ
khung tổng thể, chỉ vẽ mặt cắt như trước):
- Cột: `truc` là tên 1 trục đứng (vd "A"); `tang` là "<mốc_dưới>_<mốc_trên>"
  (vd "tang2_tang3") — 2 mốc phải khớp tên trong `cao_do_moc`.
- Dầm: `truc` là "<trục_trái>-<trục_phải>" (vd "A-B"); `tang` là TÊN 1 mốc
  cao độ (dầm nằm ngang tại 1 cao độ, không phải khoảng).

toa_do_truc/cao_do_moc LÀ THAM SỐ TƯỜNG MINH (đúng triết lý đã ghi trong
src/drawing/geometry.py: toạ độ lưới trục KHÔNG tự suy trong hàm vẽ) — khi
người gọi không cung cấp, hàm này tự suy TOẠ ĐỘ ĐỀU NHAU theo đúng thứ tự
xuất hiện đầu tiên trong dữ liệu (tổng quát, dùng được cho BẤT KỲ file nào có
cột truc/tang, nhưng KHÔNG đúng tỉ lệ nhịp/tầng thật — muốn đúng tỉ lệ phải
tự truyền toa_do_truc/cao_do_moc thật, xem scripts/ve_khung_truc5_day_du.py).
"""

from __future__ import annotations

from ..drawing import geometry
from ..input_adapter.models import LoaiCauKien, PhanTuKhung


def _toa_do_deu(ten_theo_thu_tu: list[str], buoc: float) -> dict[str, float]:
    """Toạ độ đều nhau theo thứ tự xuất hiện đầu tiên, loại trùng — fallback
    tổng quát khi không có toạ độ thật."""
    thu_tu = list(dict.fromkeys(ten_theo_thu_tu))
    return {ten: i * buoc for i, ten in enumerate(thu_tu)}


def _toa_do_deu_giu_thu_tu(that: dict[str, float]) -> dict[str, float]:
    """Toạ độ VẼ (schematic) đều nhau, GIỮ NGUYÊN thứ tự thật (`that`) nhưng
    khoảng cách giữa 2 trục/mốc liên tiếp LUÔN bằng nhau — thấy thật: người
    dùng phản hồi trực tiếp ("tại sao lại phải có đoạn thì to đoạn thì nhỏ...
    tôi thấy trong bản vẽ người ta vẽ khung bằng nhau") khi xem bản vẽ vẽ
    ĐÚNG TỶ LỆ THẬT — nhịp 1500mm bị nén sát vào nhau trong khi nhịp 5600mm
    rộng thênh thang, vừa mất cân đối thị giác vừa khiến ký hiệu số hiệu ở
    nhịp ngắn không đủ chỗ. Xác nhận qua tra cứu: "sơ đồ bố trí thép không
    cần vẽ theo đúng tỷ lệ... các kích thước cụ thể vẫn phải ghi rõ" (đúng
    nguyên tắc đã dùng — kích thước THẬT vẫn ghi qua `x_truc_dung_nhan`/
    `y_cao_do_nhan` ở geometry.ve_mat_dung_khung, CHỈ vị trí hình học vẽ đều).

    Bước đều = khoảng cách LỚN NHẤT giữa 2 mốc thật liên tiếp (đảm bảo đủ chỗ
    cho ký hiệu ở CẢ nhịp/tầng nhỏ nhất, không riêng gì nhịp/tầng đó), tối
    thiểu 3000mm (đủ chỗ tối thiểu cho 1 cụm ký hiệu số hiệu bất kể dữ liệu
    thật có khoảng cách nhỏ hơn)."""
    ten_sx = sorted(that, key=lambda t: that[t])
    if len(ten_sx) < 2:
        return dict(that)
    khoang_cach = [that[b] - that[a] for a, b in zip(ten_sx, ten_sx[1:])]
    buoc = max([3000.0] + khoang_cach)
    return {ten: i * buoc for i, ten in enumerate(ten_sx)}


def lap_rap_mat_dung_khung(
    danh_sach_phan_tu: list[PhanTuKhung],
    ky_hieu_theo_ten: dict[str, list[geometry.KyHieuThep]] | None = None,
    toa_do_truc: dict[str, float] | None = None,
    cao_do_moc: dict[str, float] | None = None,
    moc_tham_chieu: dict[str, float] | None = None,
    ten_mat_dat: str | None = None,
) -> geometry.BanVe | None:
    """Trả về None (KHÔNG phải lỗi) khi dữ liệu không có đủ truc/tang để xác
    định topology — lớp gọi khi đó chỉ bỏ qua bước vẽ khung tổng thể.

    moc_tham_chieu: mốc cao độ KIẾN TRÚC bổ sung (vd "Tự nhiên": -450, "Tôn
    nền": 0, "Đỉnh móng": -1000, đơn vị mm) — KHÔNG đến từ Story Definitions
    kết cấu (ETABS không có), chỉ hiện ký hiệu tam giác/chữ tham chiếu, KHÔNG
    tham gia chuỗi kích thước chiều cao (xem geometry.ve_mat_dung_khung).

    ten_mat_dat: tên mốc đại diện MẶT ĐẤT TỰ NHIÊN (vd "Tự nhiên") — đường
    tim mốc này vẽ nét liền đậm thay vì nét chấm gạch mảnh (Giáo Trình Vẽ Kỹ
    Thuật Xây Dựng, tr.168) — xem geometry.ve_mat_dung_khung."""
    cac_pt_cot = [p for p in danh_sach_phan_tu if p.loai == LoaiCauKien.COT and p.truc and p.tang]
    cac_pt_dam = [p for p in danh_sach_phan_tu if p.loai == LoaiCauKien.DAM and p.truc and p.tang]
    if not cac_pt_cot and not cac_pt_dam:
        return None

    ky_hieu_theo_ten = ky_hieu_theo_ten or {}

    if toa_do_truc is None:
        toa_do_truc = _toa_do_deu([p.truc for p in cac_pt_cot], buoc=3000.0)

    if cao_do_moc is None:
        moc: list[str] = []
        for p in cac_pt_cot:
            for tk in p.tang.split("_"):
                if tk not in moc:
                    moc.append(tk)
        for p in cac_pt_dam:
            if p.tang not in moc:
                moc.append(p.tang)
        cao_do_moc = _toa_do_deu(moc, buoc=3200.0)

    # Toạ độ VẼ (schematic, đều nhau) tách biệt khỏi toạ độ THẬT (toa_do_truc/
    # cao_do_moc, dùng để ghi nhãn kích thước — xem geometry.ve_mat_dung_khung
    # tham số x_truc_dung_nhan/y_cao_do_nhan) — chỉ hình học (vị trí cột/dầm/
    # trục/mốc cao độ) dùng toạ độ vẽ; MỌI con số ghi trên bản vẽ (kích thước
    # nhịp, chiều cao tầng, cao độ ▽) vẫn lấy từ toạ độ thật, không sai lệch.
    toa_do_truc_ve = _toa_do_deu_giu_thu_tu(toa_do_truc)
    cao_do_moc_ve = _toa_do_deu_giu_thu_tu(cao_do_moc)

    cac_cot: list[geometry.DoanCotVe] = []
    for p in cac_pt_cot:
        if p.truc not in toa_do_truc:
            continue
        moc2 = p.tang.split("_")
        if len(moc2) != 2 or moc2[0] not in cao_do_moc or moc2[1] not in cao_do_moc:
            continue
        y_duoi, y_tren = sorted((cao_do_moc_ve[moc2[0]], cao_do_moc_ve[moc2[1]]))
        cac_cot.append(
            geometry.DoanCotVe(
                x_truc=toa_do_truc_ve[p.truc], y_duoi=y_duoi, y_tren=y_tren,
                # Hiển thị theo "h" (kích thước tiết diện chịu uốn TRONG mặt
                # phẳng khung, mục 5.3.2 sách gốc) — không phải "b" (phương
                # vuông góc/dọc nhà, không thấy trên mặt đứng khung phẳng).
                b=p.tiet_dien.h,
                nhan=p.ten, ky_hieu=tuple(ky_hieu_theo_ten.get(p.ten, [])),
            )
        )

    cac_dam: list[geometry.DoanDamVe] = []
    for p in cac_pt_dam:
        hai_truc = p.truc.split("-")
        if len(hai_truc) != 2 or hai_truc[0] not in toa_do_truc or hai_truc[1] not in toa_do_truc:
            continue
        if p.tang not in cao_do_moc:
            continue
        x1, x2 = sorted((toa_do_truc_ve[hai_truc[0]], toa_do_truc_ve[hai_truc[1]]))
        cac_dam.append(
            geometry.DoanDamVe(
                x_trai=x1, x_phai=x2, y_truc=cao_do_moc_ve[p.tang], h=p.tiet_dien.h,
                nhan=p.ten, ky_hieu=tuple(ky_hieu_theo_ten.get(p.ten, [])),
            )
        )

    if not cac_cot and not cac_dam:
        return None

    ten_truc_sx = sorted(toa_do_truc, key=lambda t: toa_do_truc[t])
    ten_cao_do_sx = sorted(cao_do_moc, key=lambda t: cao_do_moc[t])
    return geometry.ve_mat_dung_khung(
        ten_truc_dung=ten_truc_sx,
        x_truc_dung=[toa_do_truc_ve[t] for t in ten_truc_sx],
        x_truc_dung_nhan=[toa_do_truc[t] for t in ten_truc_sx],
        ten_cao_do=ten_cao_do_sx,
        y_cao_do=[cao_do_moc_ve[t] for t in ten_cao_do_sx],
        y_cao_do_nhan=[cao_do_moc[t] for t in ten_cao_do_sx],
        cac_cot=cac_cot,
        cac_dam=cac_dam,
        moc_tham_chieu=sorted(moc_tham_chieu.items(), key=lambda kv: kv[1]) if moc_tham_chieu else None,
        ten_mat_dat=ten_mat_dat,
    )
