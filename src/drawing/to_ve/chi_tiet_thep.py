"""Chi tiết hình học thép trên mặt đứng: đường tim có BO CUNG tại chỗ uốn, thanh vẽ bằng HAI nét song song (cách nhau đúng đường
kính thật), chiều dài trải thẳng theo đường tim có cung, và các hằng số chân uốn ở nút/móng.

Đối chiếu bản mẫu `data/samples/BoTriThep_KhungTruc5_mau.pdf` (phóng to nút mái, nút tầng giữa, chân cột trong móng) và thuyết
minh Khung Trục 5 (Bảng 28, Hình 31–34); nguồn từng hằng số ghi ở chú thích — skill: Rule Engine 05 mục 9.7.8 (R57, R58), skill
Vẽ Phần Q "Hình thái nét thép trên mặt đứng". Hàm thuần số học, không cần AutoCAD.
"""

from __future__ import annotations

import math

from ...rule_engine import neo_noi

# Chân uốn ở nút (R57, thuyết minh KT5 Bảng 28): cột uốn vào dầm 500; thanh trên dầm uốn xuống cột 600 — là GIÁ TRỊ TỐI THIỂU;
# $L_{an}$ tính toán lớn hơn thì lấy bội 50 ≥ L_an và ghi ⚠ (thuyết minh KT5 không làm vậy ở vài nút tầng giữa).
L_COT_VAO_DAM_TOI_THIEU = 500.0
L_DAM_XUONG_COT_TOI_THIEU = 600.0
CHAN_L_NGANG = 200.0  # đoạn ngang chân L thép chờ trong móng ≥ 200 (skill 05 NK-16)
CAO_CHAN_L = 110.0  # tâm đoạn ngang chân L cách đáy đài; lưới thép đáy nằm DƯỚI (thấp hơn) mức này
CAO_LUOI_DAY = 60.0  # tâm thanh lưới đáy cách đáy đài (thanh nằm ngang, vẽ hai nét)
D_LUOI = 12.0  # đường kính thanh lưới đáy vẽ minh hoạ (mm)


def lam_tron_len(x: float, buoc: float = 50.0) -> float:
    return math.ceil(x / buoc - 1e-9) * buoc


def ban_kinh_tim(d: float) -> float:
    """Bán kính TIM cung uốn thanh Ø`d`: đường kính uốn TRONG tối thiểu (`neo_noi.duong_kinh_uon_toi_thieu`, có gờ: 5d khi
    d<20; 8d khi d≥20) chia 2, cộng d/2."""
    return neo_noi.duong_kinh_uon_toi_thieu(d, True) / 2.0 + d / 2.0


def chieu_dai_neo_nut(l_an_tinh_toan: float | None, toi_thieu: float) -> tuple[float, bool]:
    """Chân uốn ở nút = max(tối thiểu; bội 50 ≥ L_an tính toán). Trả (chiều dài, có_vượt_tối_thiểu) — vượt ⇒ ghi ⚠ trên bản vẽ."""
    if not l_an_tinh_toan:
        return toi_thieu, False
    can = lam_tron_len(l_an_tinh_toan)
    return (can, True) if can > toi_thieu + 1e-9 else (toi_thieu, False)


# ---------------------------------------------------------------------------
# Đường tim có cung
# ---------------------------------------------------------------------------


def _chuan_hoa(vx: float, vy: float) -> tuple[float, float, float]:
    do_dai = math.hypot(vx, vy)
    return vx / do_dai, vy / do_dai, do_dai


def _tinh_goc_uon(pts: list[tuple[float, float]], r: float, ban_kinh_nho_nhat: float):
    """Với mỗi đỉnh trong: (A, B, tâm, r_hiệu_dụng, quay_trái) — A/B là hai tiếp điểm. Bán kính bị giảm khi đoạn kề quá ngắn;
    không bao giờ nhỏ hơn `ban_kinh_nho_nhat` (để nét trong của thanh không bị suy biến)."""
    n = len(pts)
    ux, uy, lu = [], [], []
    for i in range(n - 1):
        x, y, dd = _chuan_hoa(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        ux.append(x), uy.append(y), lu.append(dd)
    goc: dict[int, tuple] = {}
    for i in range(1, n - 1):
        cross = ux[i - 1] * uy[i] - uy[i - 1] * ux[i]
        dot = ux[i - 1] * ux[i] + uy[i - 1] * uy[i]
        theta = math.atan2(abs(cross), dot)  # góc quay 0..π
        if theta < 1e-6:
            continue  # thẳng hàng — không có chỗ uốn
        t = math.tan(theta / 2.0)
        du_dai = min(lu[i - 1] * (0.5 if i > 1 else 1.0), lu[i] * (0.5 if i < n - 2 else 1.0))
        r_hd = max(min(r, du_dai / t), ban_kinh_nho_nhat)
        tl = r_hd * t
        a = (pts[i][0] - ux[i - 1] * tl, pts[i][1] - uy[i - 1] * tl)
        b = (pts[i][0] + ux[i] * tl, pts[i][1] + uy[i] * tl)
        trai = cross > 0
        nx, ny = (-uy[i - 1], ux[i - 1]) if trai else (uy[i - 1], -ux[i - 1])
        goc[i] = (a, b, (a[0] + nx * r_hd, a[1] + ny * r_hd), r_hd, trai)
    return goc


def duong_tim(pts: list[tuple[float, float]], r: float, ban_kinh_nho_nhat: float = 0.0):
    """Đường tim thanh: danh sách phần tử theo thứ tự dọc đường — ('doan', A, B) hoặc ('cung', tâm, r, a0°, a1°, quay_trái)."""
    goc = _tinh_goc_uon(pts, r, ban_kinh_nho_nhat)
    phan_tu: list[tuple] = []
    diem = pts[0]
    for i in range(1, len(pts) - 1):
        if i not in goc:
            continue
        a, b, tam, r_hd, trai = goc[i]
        phan_tu.append(("doan", diem, a))
        a0 = math.degrees(math.atan2(a[1] - tam[1], a[0] - tam[0])) % 360.0
        a1 = math.degrees(math.atan2(b[1] - tam[1], b[0] - tam[0])) % 360.0
        phan_tu.append(("cung", tam, r_hd, a0, a1, trai))
        diem = b
    phan_tu.append(("doan", diem, pts[-1]))
    return [p for p in phan_tu if p[0] != "doan" or math.dist(p[1], p[2]) > 1e-6]


def chieu_dai_duong_uon(pts: list[tuple[float, float]], r: float) -> float:
    """Chiều dài trải thẳng theo đường tim (đoạn thẳng + cung)."""
    tong = 0.0
    for p in duong_tim(pts, r):
        if p[0] == "doan":
            tong += math.dist(p[1], p[2])
        else:
            _, _, rr, a0, a1, trai = p
            quet = (a1 - a0) % 360.0 if trai else (a0 - a1) % 360.0
            tong += math.radians(quet) * rr
    return tong


def net_song_song(pts: list[tuple[float, float]], r: float, d: float):
    """Hai nét song song cách nhau `d` bao quanh đường tim, đóng hai đầu bằng đoạn vuông góc.
    Trả (các_đoạn [(x1,y1,x2,y2)], các_cung [(cx,cy,r,a0°,a1°)])."""
    h = d / 2.0
    doan: list[tuple[float, float, float, float]] = []
    cung: list[tuple[float, float, float, float, float]] = []
    pt = duong_tim(pts, r, h * 1.05)
    for ben in (1.0, -1.0):  # +1 = bên trái hướng đi
        for p in pt:
            if p[0] == "doan":
                a, b = p[1], p[2]
                nx, ny, _ = _chuan_hoa(-(b[1] - a[1]), b[0] - a[0])
                doan.append((a[0] + ben * h * nx, a[1] + ben * h * ny, b[0] + ben * h * nx, b[1] + ben * h * ny))
            else:
                _, tam, rr, a0, a1, trai = p
                r_ben = rr - ben * h if trai else rr + ben * h
                if trai:
                    cung.append((tam[0], tam[1], r_ben, a0, a1))
                else:
                    cung.append((tam[0], tam[1], r_ben, a1, a0))
    # nắp hai đầu
    for diem, huong in ((pt[0][1], pt[0]), (pt[-1][2], pt[-1])):
        a, b = huong[1], huong[2]
        nx, ny, _ = _chuan_hoa(-(b[1] - a[1]), b[0] - a[0])
        doan.append((diem[0] + h * nx, diem[1] + h * ny, diem[0] - h * nx, diem[1] - h * ny))
    return doan, cung
