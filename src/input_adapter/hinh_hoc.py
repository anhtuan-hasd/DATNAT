"""Suy luận hình học TỔNG THỂ công trình (toạ độ lưới trục, cao độ mốc tầng)
từ chính dữ liệu đã chuẩn hoá — CHANGE_REQUESTS.md mục 5. Trước đây 2 giá trị
này bị hard-code thủ công riêng cho khung trục 5 trong từng script demo
(`TOA_DO_TRUC = {"A": 0.0, "B": 5600.0, "C": 7100.0}`...) — không tổng quát
cho công trình khác. Module này thay thế hoàn toàn cách làm đó.

Nguồn dữ liệu duy nhất: 2 trường đã có sẵn trong `PhanTuKhung` (models.py) —
`truc`/`tang` (TÊN trục/tầng, dạng chuỗi) và `chieu_dai` (khoảng cách bằng
số, mm — nhịp dầm hoặc chiều cao đoạn cột). KHÔNG đọc thêm cột nào khác,
KHÔNG suy đoán từ tên phần tử.

Nguyên tắc: khi dữ liệu không đủ để xác định TOẠ ĐỘ TUYỆT ĐỐI của 1 trục/tầng
(không có đường nào nối nó với phần còn lại kèm chiều dài cụ thể), hàm trả về
`hoan_tat=False` kèm mô tả CHÍNH XÁC còn thiếu gì — không tự bịa số, không
dùng lại giá trị mẫu của khung trục 5 hay bất kỳ công trình nào khác. Input
Adapter Agent (`orchestrator/agents/input_adapter_agent.py`) đọc `thieu` này
để hỏi người dùng, rồi gọi lại hàm với `da_biet` đã bổ sung.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import LoaiCauKien, PhanTuKhung


@dataclass
class KetQuaSuyLuanHinhHoc:
    hoan_tat: bool
    gia_tri: dict[str, float] = field(default_factory=dict)
    thieu: list[str] = field(default_factory=list)


def _dinh_vi_theo_canh(
    canh: list[tuple[str, str, float | None]],
    nut_don_le: set[str],
    da_biet: dict[str, float] | None,
    ten_doi_tuong: str,  # "trục" hoặc "tầng" — chỉ dùng để viết thông báo lỗi dễ hiểu
) -> KetQuaSuyLuanHinhHoc:
    """Định vị TƯƠNG ĐỐI 1 tập "nút" (tên trục hoặc tên tầng) trên 1 trục số,
    dựa vào các "cạnh" đã biết khoảng cách giữa 2 nút liền kề — đúng bài toán
    "định vị nút theo cạnh có trọng số đã biết một phần" (không phải thuật
    toán tối ưu/tìm kiếm mù nào, chỉ là lan truyền giá trị đã biết theo cạnh
    có độ dài xác định, dùng cho MỌI công trình bất kỳ, không riêng khung nào).

    QUAN TRỌNG — gieo gốc toạ độ theo TỪNG THÀNH PHẦN LIÊN THÔNG riêng biệt,
    không phải 1 gốc chung cho cả tập nút. "Thành phần liên thông" ở đây là
    nhóm nút nối được với nhau qua ÍT NHẤT 1 cạnh (bất kể cạnh đó đã biết độ
    dài hay chưa — có cạnh nghĩa là CÓ QUAN HỆ, chỉ là chưa biết số; không có
    cạnh nào nghĩa là KHÔNG CÓ CĂN CỨ để đặt nó ở đâu cả). Nếu gieo 1 gốc
    chung cho toàn bộ tập nút, 1 trục/tầng hoàn toàn tách biệt (không phần
    tử nào nối nó với phần còn lại) sẽ vô tình bị gán trùng gốc 0 với thành
    phần khác — SAI mà không hề báo lỗi. Thuật toán đúng:

    1. Chia `tat_ca_nut` thành các thành phần liên thông theo `canh` (không
       quan tâm cạnh đã biết độ dài hay chưa) — nút không có cạnh nào là 1
       thành phần đơn lẻ (chỉ chứa chính nó).
    2. Với mỗi thành phần: nếu đã có ≥1 nút nằm trong `da_biet`, dùng đúng
       giá trị đó làm gốc (không tự đặt số khác). Nếu KHÔNG có nút nào đã
       biết:
       - Thành phần chỉ có 1 nút (không cạnh nào cả) → CHỈ được mặc định 0
         khi đây là thành phần DUY NHẤT trong toàn bộ tập nút (tức công
         trình chỉ có đúng 1 trục/tầng, không có gì để so sánh) — ngược lại
         để nút này rơi vào `thieu`, không tự bịa gốc trùng thành phần khác.
       - Thành phần có ≥2 nút (có ít nhất 1 cạnh) → gán nút NHỎ NHẤT theo
         alphabet trong thành phần đó = 0 (gốc CỤC BỘ, chỉ dùng nội bộ thành
         phần này).
    3. Lặp điểm cố định (dừng chắc chắn — mỗi vòng phải tiến triển hoặc dừng
       ngay): với mỗi cạnh (a, b, dai) có `dai` khác None, nếu đúng 1 trong 2
       đầu đã có toạ độ và đầu kia chưa, gán đầu kia = toạ_độ_đã_biết ± dai.
    4. Nút nào vẫn chưa có toạ độ sau bước 3 → `thieu`. Cạnh có `dai=None` mà
       1 trong 2 đầu vẫn chưa có toạ độ (bị cạnh thiếu số này chặn đường lan
       truyền) → cũng ghi vào `thieu`, nêu rõ đúng cạnh nào thiếu chiều dài.
    """
    gia_tri: dict[str, float] = dict(da_biet or {})
    tat_ca_nut: set[str] = set(nut_don_le) | {n for a, b, _ in canh for n in (a, b)}

    # Bước 1 — chia thành phần liên thông bằng Union-Find đơn giản (mảng cha,
    # nén đường đi) — đủ nhanh và đủ rõ ràng cho quy mô 1 công trình (vài
    # chục trục/tầng), không cần thư viện đồ thị ngoài.
    cha: dict[str, str] = {n: n for n in tat_ca_nut}

    def _tim(n: str) -> str:
        while cha[n] != n:
            cha[n] = cha[cha[n]]  # nén đường đi
            n = cha[n]
        return n

    def _hop(n1: str, n2: str) -> None:
        r1, r2 = _tim(n1), _tim(n2)
        if r1 != r2:
            cha[r2] = r1

    for a, b, _ in canh:
        _hop(a, b)

    thanh_phan: dict[str, set[str]] = {}
    for n in tat_ca_nut:
        thanh_phan.setdefault(_tim(n), set()).add(n)

    # Bước 2 — gieo gốc cho từng thành phần CHƯA có nút nào trong da_biet.
    chi_1_thanh_phan_duy_nhat = len(thanh_phan) == 1
    for nhom in thanh_phan.values():
        if nhom & gia_tri.keys():
            continue  # thành phần này đã có gốc từ da_biet, không cần gieo thêm
        if len(nhom) == 1:
            if chi_1_thanh_phan_duy_nhat:
                gia_tri[next(iter(nhom))] = 0.0
            # else: để trống — sẽ rơi vào `thieu` ở bước 4, KHÔNG mặc định 0
            # (tránh trùng gốc giả với thành phần khác, xem docstring).
        else:
            gia_tri[min(nhom)] = 0.0

    con_tien_trien = True
    while con_tien_trien:
        con_tien_trien = False
        for a, b, dai in canh:
            if dai is None:
                continue
            if a in gia_tri and b not in gia_tri:
                gia_tri[b] = gia_tri[a] + dai
                con_tien_trien = True
            elif b in gia_tri and a not in gia_tri:
                gia_tri[a] = gia_tri[b] - dai
                con_tien_trien = True

    thieu: list[str] = []
    nut_thieu = sorted(tat_ca_nut - gia_tri.keys())
    for n in nut_thieu:
        thieu.append(
            f"Không xác định được vị trí {ten_doi_tuong} '{n}' — không có phần tử nào có 'chieu_dai' "
            f"nối {ten_doi_tuong} này với phần còn lại đã biết toạ độ."
        )
    for a, b, dai in canh:
        if dai is None and (a not in gia_tri or b not in gia_tri):
            thieu.append(
                f"Phần tử nối {ten_doi_tuong} '{a}' và '{b}' thiếu 'chieu_dai' (nhịp/chiều cao đoạn)."
            )

    return KetQuaSuyLuanHinhHoc(hoan_tat=not thieu, gia_tri=gia_tri, thieu=thieu)


def suy_luan_toa_do_truc(
    phan_tu: list[PhanTuKhung], da_biet: dict[str, float] | None = None
) -> KetQuaSuyLuanHinhHoc:
    """toa_do_truc: suy từ DẦM — `PhanTuKhung.truc` dạng "A-B" (2 trục dầm
    bắc qua) + `PhanTuKhung.chieu_dai` (nhịp, mm) là 1 "cạnh" nối trục A-B.
    Cột chỉ đứng tại 1 trục (`truc` dạng đơn "A") — không tạo cạnh, chỉ thêm
    trục đó vào tập cần định vị (nếu không có dầm nào nối tới, trục đó sẽ rơi
    vào `thieu`)."""
    canh: list[tuple[str, str, float | None]] = []
    nut_don_le: set[str] = set()

    for p in phan_tu:
        if not p.truc:
            continue
        if p.loai == LoaiCauKien.DAM:
            hai_truc = p.truc.split("-")
            if len(hai_truc) == 2 and hai_truc[0] != hai_truc[1]:
                canh.append((hai_truc[0], hai_truc[1], p.chieu_dai))
        elif p.loai == LoaiCauKien.COT:
            nut_don_le.add(p.truc)

    return _dinh_vi_theo_canh(canh, nut_don_le, da_biet, ten_doi_tuong="trục")


def suy_luan_cao_do_moc(
    phan_tu: list[PhanTuKhung], da_biet: dict[str, float] | None = None
) -> KetQuaSuyLuanHinhHoc:
    """cao_do_moc: suy từ CỘT — `PhanTuKhung.tang` dạng "tang2_tang3" (mốc
    dưới_mốc trên của 1 đoạn cột) + `chieu_dai` (chiều cao đoạn, mm) là 1
    "cạnh" nối 2 mốc. Dầm chỉ nằm NGANG tại 1 mốc (`tang` dạng đơn
    "tang3") — không tạo cạnh, chỉ thêm mốc đó vào tập cần định vị."""
    canh: list[tuple[str, str, float | None]] = []
    nut_don_le: set[str] = set()

    for p in phan_tu:
        if not p.tang:
            continue
        if p.loai == LoaiCauKien.COT:
            hai_moc = p.tang.split("_")
            if len(hai_moc) == 2 and hai_moc[0] != hai_moc[1]:
                canh.append((hai_moc[0], hai_moc[1], p.chieu_dai))
        elif p.loai == LoaiCauKien.DAM:
            nut_don_le.add(p.tang)

    return _dinh_vi_theo_canh(canh, nut_don_le, da_biet, ten_doi_tuong="tầng")
