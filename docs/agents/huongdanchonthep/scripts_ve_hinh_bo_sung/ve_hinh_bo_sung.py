"""Sinh 14 hình bổ sung (bs_01 … bs_14) cho bộ skill chọn thép / nhập dữ liệu / kiểm chứng.

Chạy từ thư mục gốc repo:
    python docs/agents/huongdanchonthep/scripts_ve_hinh_bo_sung/ve_hinh_bo_sung.py

Hình chỉ là SƠ ĐỒ minh hoạ quy trình (không phải bản vẽ kỹ thuật theo tỉ lệ). Agent không xem được ảnh:
mỗi hình đều có khối "Mô tả bằng chữ" trong file skill tương ứng. Số liệu trong hình lấy từ skill, không bịa thêm.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arc, FancyArrowPatch, Polygon

plt.rcParams["font.family"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

GOC = Path(__file__).resolve().parents[4]
IMG_CT = GOC / "docs" / "agents" / "huongdanchonthep" / "img"
IMG_ND = GOC / "docs" / "agents" / "huongdannhapdulieu" / "img"
IMG_KC = GOC / "docs" / "agents" / "huongdankiemchung" / "img"
for p in (IMG_CT, IMG_ND, IMG_KC):
    p.mkdir(parents=True, exist_ok=True)

XANH = ("#dbe9f6", "#2c5f8a")   # có tool
XAM = ("#eeeeee", "#777777")    # kiến thức / ETABS đã cho
DO = ("#fde2e0", "#c0392b")     # chưa có tool / dừng
CAM = ("#ffe9c9", "#d9822b")    # có tool nhưng giới hạn
LUC = ("#e0f1dd", "#3f7d3a")    # đạt / đủ
VANG = ("#fff6c9", "#b59a12")


def new(w, h, title=None):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    if title:
        ax.text(0.2, h - 0.3, title, fontsize=13, fontweight="bold", va="top")
    return fig, ax


def box(ax, x, y, w, h, text, col=XANH, fs=9, dashed=False, bold=False, wrap=None, align="center"):
    ec = col[1]
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=col[0], ec=ec,
                       lw=1.4, ls="--" if dashed else "-")
    ax.add_patch(p)
    if wrap:
        text = "\n".join(textwrap.fill(t, wrap) for t in text.split("\n"))
    ha = {"center": "center", "left": "left"}[align]
    tx = x + w / 2 if align == "center" else x + 0.1
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, fontweight="bold" if bold else "normal")


def arrow(ax, p0, p1, col="#444444", lw=1.4, ls="-", rad=0.0, label=None, fs=8):
    a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=12, color=col, lw=lw, ls=ls,
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if label:
        ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 0.12, label, fontsize=fs, color=col, ha="center")


def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("ghi", path.relative_to(GOC))


# ---------------------------------------------------------------- bs_01
def bs_01():
    fig, ax = new(14, 7.4, "Phân vai tool và skill — bốn agent và bảy tool của Rule Engine Agent")
    xs = [0.4, 3.9, 7.4, 10.9]
    ten = ["Input Adapter\n(đọc ETABS, chuẩn hoá)", "Rule Engine\n(chọn thép, tự kiểm tra)", "Drawing\n(vẽ qua AutoCAD COM)",
           "Verification\n(đọc lại bản vẽ)"]
    for x, t in zip(xs, ten):
        box(ax, x, 5.4, 2.7, 1.1, t, XANH if "Rule" in t else XAM, fs=10, bold=True)
    for i in range(3):
        arrow(ax, (xs[i] + 2.7, 5.95), (xs[i + 1], 5.95))
    tools = ["tra_vat_lieu", "tinh_lech_tam_cot\n(η = 1)", "chon_thep_doc", "tinh_cot_dai", "tinh_neo_noi",
             "tu_kiem_tra", "hoi_nguoi_dung"]
    for i, t in enumerate(tools):
        col = CAM if i in (1, 5) else XANH
        box(ax, 0.3 + i * 1.95, 3.4, 1.8, 0.95, t, col, fs=8.5)
    ax.text(0.3, 4.55, "7 tool hiện có (xanh = có; cam = có nhưng giới hạn)", fontsize=10, fontweight="bold")
    arrow(ax, (5.25, 5.4), (5.25, 4.5), lw=1.0)
    gaps = [("Cấu tạo nút khung\n(nut_khung.py chưa nối)", "module 05"),
            ("Bố trí dọc: điểm cắt,\nchiều dài thanh, vùng đai", "module 06"),
            ("Cổng hình học nút\n14.2 / 14.3", "module 09"),
            ("Kháng chấn\n(R31–R40)", "module 07"),
            ("Xoắn, dầm cao,\nlỗ mở (R47–R52)", "module 09")]
    ax.text(0.3, 2.65, "5 việc CHƯA có tool — agent áp dụng luật định tính, ghi basis, gắn cờ, không tự bịa số", fontsize=10,
            fontweight="bold", color=DO[1])
    for i, (t, m) in enumerate(gaps):
        box(ax, 0.3 + i * 2.7, 0.9, 2.5, 1.3, t + "\n→ " + m, DO, fs=8.5, dashed=True)
    ax.text(0.3, 0.35, "Skill KHÔNG thay tool: mọi con số kỹ thuật phải đến từ kết quả tool.", fontsize=9, style="italic")
    save(fig, IMG_CT / "bs_01_ban_do_tool_skill.png")


# ---------------------------------------------------------------- bs_02
def bs_02():
    fig, ax = new(15, 8.3, "16 bước chọn thép dầm — nơi có tool và nơi chưa có")
    lanes = [
        ("Thép dọc", 5.6, [("1 Chốt dữ liệu\ntra_vat_lieu", XANH), ("2 ξR, αR, μmax", XAM), ("3 a, h0", XAM),
                           ("4 Chữ nhật / T", XAM), ("5 αm\ncốt đơn / kép", XAM), ("6 As (ETABS đã cho)", XAM),
                           ("7 μmin ≤ μ ≤ μmax\ntu_kiem_tra", XANH), ("8 Chọn Ø, hàng\nchon_thep_doc", XANH)]),
        ("Thép ngang", 3.5, [("9 Q ≤ 0,3·Rb·b·h0\ntinh_cot_dai", XANH), ("10 Q so Qb,min\ntinh_cot_dai", XANH),
                             ("11 Đai: smax, qsw, s\ntinh_cot_dai (một phần)", CAM), ("12 Cốt xiên\nKHÔNG tool", DO),
                             ("13 Cốt treo\nKHÔNG tool", DO)]),
        ("Bố trí – kiểm tra", 1.4, [("14 Cắt/uốn, hình bao\nKHÔNG tool", DO), ("15 Neo\ntinh_neo_noi", XANH),
                                    ("16 Nứt-võng, thống kê\nKHÔNG tool", DO)]),
    ]
    pos = {}
    for ten, y, items in lanes:
        ax.text(0.2, y + 1.55, ten, fontsize=11, fontweight="bold")
        for i, (t, c) in enumerate(items):
            x = 0.2 + i * 1.85
            box(ax, x, y, 1.7, 1.2, t, c, fs=8, dashed=(c == DO))
            pos[t.split()[0]] = (x, y)
            if i:
                arrow(ax, (x - 0.15, y + 0.6), (x, y + 0.6), lw=1.0)
    x7, y7 = pos["7"]
    x8, y8 = pos["8"]
    arrow(ax, (x7 + 0.85, y7 - 0.02), (x8 + 0.85, y8 - 0.02), col="#c0392b", rad=0.9, lw=1.2)
    ax.text(x8 + 1.5, y8 - 0.35, "dat=false và còn lượt tự sửa → chọn lại", color="#c0392b", fontsize=8)
    box(ax, 9.5, 1.4, 3.6, 1.2, "Hết lượt tự sửa (het_luot_tu_sua)\n→ hoi_nguoi_dung", DO, fs=9, bold=True)
    box(ax, 9.5, 3.0, 5.3, 0.5, "", VANG)
    ax.text(9.6, 3.25, "Với nguồn ETABS thật: dầm không có Q thô → bỏ tinh_cot_dai, chỉ đề xuất Ø8 cấu tạo", fontsize=8, va="center")
    save(fig, IMG_CT / "bs_02_dam_16_buoc_luong.png")


# ---------------------------------------------------------------- bs_03
def bs_03():
    fig, ax = new(14, 8.2, "14 bước chọn thép cột — phần có tool, phần chỉ kiểm bằng skill")
    steps = [
        ("1 Cặp nội lực nguy hiểm\n(chỉ 1 cặp đại diện)", CAM), ("2 Vật liệu, hệ số\ntra_vat_lieu", XANH),
        ("3 Hình học, l0 = 0,7H, λ", XAM), ("4 e1, ea, e0\ntinh_lech_tam_cot", XANH),
        ("5 η — tool đặt η = 1\nl0/h > 7 → hỏi", CAM), ("6 Lớn / bé\ntinh_lech_tam_cot", XANH),
        ("7 As = A's (ETABS đã cho)", XAM), ("8 μmin, μmax\ntu_kiem_tra (μ mỗi phía ≤ 3%)", CAM),
        ("9 Chọn thép dọc\nchon_thep_doc(loai=cot)", XANH), ("10 Kiểm trong / ngoài mặt phẳng\n(ngoài mp: KHÔNG tool)", CAM),
        ("11 Biểu đồ tương tác, mọi cặp\nKHÔNG tool", DO), ("12 Cốt đai\ntinh_cot_dai", XANH),
        ("13 Nối, neo\ntinh_neo_noi", XANH), ("14 Kéo, xiên, thống kê\nKHÔNG tool → dừng/hỏi", DO),
    ]
    for i, (t, c) in enumerate(steps):
        col, row = divmod(i, 7)
        x = 0.4 + col * 6.8
        y = 7.1 - row * 1.0
        box(ax, x, y - 0.35, 5.6, 0.8, t, c, fs=9, dashed=(c == DO))
        if row:
            arrow(ax, (x + 2.8, y + 0.55), (x + 2.8, y + 0.45), lw=1.0)
    arrow(ax, (6.0, 1.25), (7.2, 7.45), rad=-0.25, lw=1.2)
    ax.text(0.4, 0.45, "Vòng lặp: kiểm tra không đạt → quay Bước 9 (tăng thép); μt > 4% → tăng tiết diện (R10).", fontsize=9,
            color="#c0392b")
    save(fig, IMG_CT / "bs_03_cot_14_buoc_luong.png")


# ---------------------------------------------------------------- bs_04
def bs_04():
    fig, ax = new(15, 9.2, "Cây quyết định chọn loại nút khung")
    box(ax, 0.2, 3.8, 1.8, 0.9, "Nút ở đâu?", XAM, bold=True, fs=10)
    nhanh = [("Góc mái", 7.0), ("Giữa mái", 5.6), ("Biên trung gian", 4.1), ("Giữa trung gian", 2.6), ("Xà gãy khúc", 1.5),
             ("Cột – móng", 0.5)]
    for t, y in nhanh:
        box(ax, 2.7, y, 1.9, 0.6, t, XANH, fs=9)
        arrow(ax, (2.0, 4.25), (2.7, y + 0.3), lw=1.0)
    # góc mái
    box(ax, 5.2, 7.0, 2.2, 0.55, "Dấu M đầu dầm?", XAM, fs=9)
    arrow(ax, (4.6, 7.2), (5.2, 7.27), lw=1.0)
    box(ax, 8.0, 7.45, 2.3, 0.55, "ĐÓNG: e0/h?", XAM, fs=9)
    box(ax, 8.0, 6.0, 2.3, 0.55, "MỞ: μ dầm?", XAM, fs=9)
    arrow(ax, (7.4, 7.35), (8.0, 7.7), lw=1.0)
    arrow(ax, (7.4, 7.2), (8.0, 6.3), lw=1.0)
    leaves = [("≤ 0,25 → Hình 9.5a", 8.0), ("0,25–0,5 → 9.5b (+≥2 thanh)", 7.4), ("> 0,5 → 9.5c (2Lan); nách 9.5d", 6.8)]
    for t, y in leaves:
        box(ax, 10.8, y, 4.0, 0.5, t, LUC, fs=8.5)
    arrow(ax, (10.3, 7.7), (10.8, 7.6), lw=0.8)
    box(ax, 10.8, 6.0, 4.0, 0.5, "μ < 2% → 9.6a (chữ U)", LUC, fs=8.5)
    box(ax, 10.8, 5.4, 4.0, 0.5, "μ ≥ 2% → 9.6b (+chéo 20%)", LUC, fs=8.5)
    arrow(ax, (10.3, 6.3), (10.8, 6.25), lw=0.8)
    box(ax, 10.8, 4.5, 4.0, 0.6, "mọi nút góc: hd ≥ 1,5·hc → thêm\nđai kín / chữ U (9.5e)", CAM, fs=8.2)
    box(ax, 5.2, 5.5, 2.4, 0.7, "→ Hình 9.7 (cột uốn vòm\nhoặc ra hai bên, r ≥ 5Ø)", LUC, fs=8)
    box(ax, 5.2, 3.7, 4.6, 1.1, "tanβ = (h2 − h1)/hd\nkhông đổi → 9.8a;  ≤ 1/6 → 9.8b (bẻ nghiêng)\n> 1/6 → 9.8c (neo Lan, chờ riêng)", LUC, fs=8)
    box(ax, 5.2, 2.5, 4.6, 0.8, "dầm hai bên cùng cao: thép liên tục\nkhác cao: neo sâu → Hình 9.9", LUC, fs=8)
    box(ax, 5.2, 1.3, 4.6, 0.9, "α ≥ 160° → 9.10a (liên tục + đai dày)\nα < 160° → 9.10b (tách, neo vùng nén); nhọn → 9.10c", LUC, fs=8)
    box(ax, 5.2, 0.3, 4.6, 0.7, "Thép chờ cùng thép tầng 1, chân L ≥ 200 → 9.11", LUC, fs=8)
    for y in (5.9, 4.25, 2.9, 1.75, 0.65):
        pass
    box(ax, 10.2, 0.3, 4.6, 2.2, "MỌI nhánh dẫn tới:\n① Lan từ tinh_neo_noi (so 0,3·L0,an)\n② bán kính uốn r ≥ 5d / 8d\n③ KIỂM 14.2 / 14.3 trước khi vẽ\n④ không kiểm → cờ, không in ĐẠT", DO, fs=9, align="left")
    save(fig, IMG_CT / "bs_04_nut_chon_loai.png")


# ---------------------------------------------------------------- bs_05
def bs_05():
    fig, ax = new(16, 9.2, "Bảng điều kiện thêm thép — nút khung / dầm / cột (mã trùng module 05)")
    cards = [
        ("NÚT KHUNG (NK)", [
            "NK-01  góc mái đóng e0/h ≤ 0,25 → uốn xuống Lan",
            "NK-02  0,25–0,5 → + ≥2 thanh quá đáy dầm Lan",
            "NK-03  > 0,5 → cột lên mép dầm; 2Lan ⚠; ≤2 thanh/tiết diện",
            "NK-04  nách: 0,1L; 0,4h; đai nghiêng; 20% uốn xiên",
            "NK-05  hd ≥ 1,5hc → đai kín / chữ U",
            "NK-06/07  góc mở: chữ U; μ ≥ 2% → chéo 20%",
            "NK-08  giữa mái: kéo lên Lan, r ≥ 5Ø",
            "NK-09–11  biên: đai ≤ min(300;10d); tanβ 1/6",
            "NK-12/13  giữa: dầm thấp neo sâu",
            "NK-14/15  gãy khúc: α ≥ / < 160°",
            "NK-16  cột–móng: chờ cùng thép, chân L ≥ 200",
            "NK-17  mọi nút: đai không cắt, đai phụ ≤ 100",
            "NK-18/19  kiểm khe 14.2; dầm thấp a' = a + d",
            "NK-20  kháng chấn ⚠ (module 07)"]),
        ("DẦM (DM)", [
            "DM-01  As gối − As suốt > 0 → thanh gia cường",
            "DM-02  mặt trên: ≥2 thanh góc chạy suốt",
            "DM-03  dầm phụ gác lên → cốt treo ≥4–5 đai/bên",
            "DM-04  hai dầm cùng cao → vùng 3b",
            "DM-05  h > 700 (=700) → cốt cạnh bên 2Ø12",
            "DM-06  đai không đủ → cốt xiên (không tool)",
            "DM-07  b > 350 → ≥3 nhánh đai",
            "DM-08  có cốt nén → đai kín s ≤ 15d",
            "DM-09  có T → đai kín xoắn (R47–R50)",
            "DM-10  tải ngang → thép dưới neo đủ L0,an",
            "DM-11  console → neo vào dầm kề ≥ Lan",
            "DM-12  gối biên → uốn xuống cột ≥ Lan",
            "DM-13  nhiều nhịp → gia cường xuyên cột"]),
        ("CỘT (CT)", [
            "CT-01  h > 500 → thanh giữa cạnh dài",
            "CT-02  cạnh > 400 / > 4 thanh → đai phụ",
            "CT-03  μt > 3% (A) / nén > 1,5% (D) → s ≤ min(10d;300)",
            "CT-04  đoạn nối → đai ≤ min(10d;300) trên Lov",
            "CT-05  hai đầu cột → đai dày trên ld",
            "CT-06  > 4 thanh/cạnh → nối so le ≤ 50%",
            "CT-07  chân cột → chờ cùng thép, neo 0,75L0,an",
            "CT-08  đổi tiết diện → bẻ nghiêng / cắt + neo",
            "CT-09  cột kéo → hàn / nối cơ khí",
            "CT-10  N chuyển kéo (động đất) → Lan +50% ⚠",
            "CT-11  d ≥ 32 → không nối chồng",
            "CT-12  cạnh ≤ 400 và ≤ 4 thanh → một đai"]),
    ]
    for i, (ten, dong) in enumerate(cards):
        x = 0.2 + i * 5.3
        ax.add_patch(Rectangle((x, 0.3), 5.1, 8.2, fc="#fafafa", ec="#2c5f8a", lw=1.6))
        ax.text(x + 0.15, 8.2, ten, fontsize=11, fontweight="bold", color="#2c5f8a")
        for k, d in enumerate(dong):
            col = "#c0392b" if ("⚠" in d or "không tool" in d) else "#222222"
            ax.text(x + 0.15, 7.75 - k * 0.52, textwrap.fill(d, 62), fontsize=7.8, va="top", color=col)
    save(fig, IMG_CT / "bs_05_nut_bang_dieu_kien_them_thep.png")


# ---------------------------------------------------------------- bs_06
def bs_06():
    fig, ax = new(14, 7.6, "Kiểm hình học nút (14.2): thép dầm có lọt giữa các thanh cột không")
    steps = [
        "1  Lấy bc, lớp bảo vệ C, Ø đai, danh sách Ø thanh cột trên mặt đang xét",
        "2  y0 = bc/2 − C − dđai − d1/2;  khe wi = (y(i+1) − yi) − (di + d(i+1))/2",
        "3  Thanh dầm Ø db lọt khe i khi wi ≥ db + 2δ,  δ ≥ 10 mm",
        "4  Số thanh dầm trong MỘT lớp ≤ số khe lọt được ?",
    ]
    for i, t in enumerate(steps):
        box(ax, 0.3, 6.1 - i * 1.25, 8.0, 0.95, t, XANH if i < 3 else XAM, fs=9, bold=(i == 3))
        if i:
            arrow(ax, (4.3, 6.1 - (i - 1) * 1.25), (4.3, 6.1 - i * 1.25 + 0.95), lw=1.0)
    box(ax, 0.3, 0.45, 3.8, 0.9, "CÓ → đạt lớp này; lặp cho thép trên,\nthép dưới và dầm vuông góc", LUC, fs=8.5)
    box(ax, 4.5, 0.45, 3.8, 0.9, "KHÔNG → R41: KHÔNG VẼ;\ntrả phương án 1–4 cho kỹ sư", DO, fs=8.5, dashed=True)
    arrow(ax, (2.2, 2.35), (2.2, 1.35), lw=1.0)
    arrow(ax, (6.4, 2.35), (6.4, 1.35), lw=1.0, col="#c0392b")
    box(ax, 8.8, 3.5, 4.9, 3.5, "Ví dụ số (đã kiểm bằng code)\n\ncột 250: mỗi mặt 2Ø25+1Ø22\n→ 2 khe, mỗi khe 61 mm\n3 thanh dầm → chỉ lọt 2\n\ncột 300: 4Ø22 mỗi mặt (1521 mm²)\n→ 3 khe, mỗi khe 52 mm\n→ lọt cả 3 thanh", VANG, fs=9, align="left")
    box(ax, 8.8, 0.45, 4.9, 2.7, "Phương án khi không lọt\n1 tăng bc lên 300, 4 thanh/mặt\n2 bỏ thanh giữa, tăng Ø cột\n3 đổi sang Ø dầm lớn hơn, ít thanh\n4 dầm rộng hơn cột", CAM, fs=8.8, align="left")
    save(fig, IMG_CT / "bs_06_nut_kiem_khe_thuat_toan.png")


# ---------------------------------------------------------------- bs_07
def bs_07():
    import numpy as np
    fig, ax = new(15, 9.8, "Bố trí dọc dầm: thanh suốt, gia cường, điểm cắt, đoạn kéo dài W và vùng đai (sơ đồ)")
    L0, L1 = 1.6, 13.4
    base = 6.6                                   # cao độ gốc của hình bao
    f = lambda x: base + 2.0 * (1 - 3.3 * ((x - L0) / (L1 - L0)) * (1 - (x - L0) / (L1 - L0)))
    xs = np.linspace(L0, L1, 200)
    ax.plot(xs, [f(x) for x in xs], color="k", lw=1.9)
    ax.text(7.5, 7.0 + 1.9, "|M| mô men âm (hình bao)", fontsize=9, ha="center")
    mu_hi, mu_lo = f(L0) + 0.15, 7.45             # Mu đủ thép; Mu chỉ còn thanh suốt
    # x_lt: nơi |M| = mu_lo (bên trái), đối xứng bên phải
    t = np.linspace(L0, (L0 + L1) / 2, 4000)
    xlt = t[np.argmin(abs(np.array([f(x) for x in t]) - mu_lo))]
    xlt2 = L0 + L1 - xlt
    W = 1.5
    xa, xb = xlt + W, xlt2 - W
    ax.plot([L0 - 0.5, xa, xa, xb, xb, L1 + 0.5], [mu_hi, mu_hi, mu_lo, mu_lo, mu_hi, mu_hi], ls="--", color="#2c5f8a", lw=1.6)
    ax.text(L0 - 0.4, mu_hi + 0.15, "Mu (đủ thép gối)", fontsize=8, color="#2c5f8a")
    ax.text((xa + xb) / 2, mu_lo + 0.12, "Mu (chỉ còn thanh suốt)", fontsize=8, color="#2c5f8a", ha="center")
    for x in (xlt, xlt2):
        ax.plot([x], [mu_lo], "ko")
        ax.plot([x, x], [mu_lo, 5.6], color="k", lw=0.7, ls=":")
    for x in (xa, xb):
        ax.plot([x, x], [mu_lo, 5.6], color="#2c5f8a", lw=0.7, ls=":")
    ax.annotate("", xy=(xa, 5.9), xytext=(xlt, 5.9), arrowprops=dict(arrowstyle="<|-|>", lw=1))
    ax.text((xa + xlt) / 2, 6.02, "W", fontsize=9, ha="center")
    ax.text(xlt, 5.35, "x_lt", fontsize=8.5, ha="center")
    ax.text(xa, 5.35, "x_cắt = x_lt + W\n(làm tròn lên 50)", fontsize=8, ha="center", va="top")
    ax.text(7.5, 5.7, "W = Q/(2·qsw) + 5d ≥ 20d", fontsize=8.5, ha="center")
    # dầm
    y0, y1 = 2.9, 4.5
    ax.add_patch(Rectangle((L0, y0), L1 - L0, y1 - y0, fc="none", ec="k", lw=1.4))
    for xc in (L0, L1):
        ax.add_patch(Rectangle((xc - 0.6, 1.9), 1.2, 3.8, fc="#eeeeee", ec="k", lw=1.2, alpha=0.6))
    ax.plot([L0 - 0.5, L1 + 0.5], [y1 - 0.2, y1 - 0.2], color="#2c5f8a", lw=3)
    ax.plot([L0 - 0.5, xa], [y1 - 0.48, y1 - 0.48], color="#2c5f8a", lw=2.2)
    ax.plot([xb, L1 + 0.5], [y1 - 0.48, y1 - 0.48], color="#2c5f8a", lw=2.2)
    ax.plot([L0 - 0.5, L1 + 0.5], [y0 + 0.2, y0 + 0.2], color="#3f7d3a", lw=3)
    ax.text(7.5, 4.65, "thanh suốt trên: ≥2 thanh góc, uốn xuống cột (ℓ ≥ Lan)", fontsize=8, ha="center")
    ax.text(xa / 2 + 1.2, 3.5, "thanh gia cường gối", fontsize=8)
    ax.text(L1 - 3.2, 3.5, "thanh gia cường gối", fontsize=8)
    ax.text(7.5, 2.55, "thanh dưới suốt, neo vào cột ≥ max(Lan,min; 5d qua tim); có tải ngang → L0,an", fontsize=8, ha="center")
    for x in np.arange(L0 + 0.1, L0 + 3.6, 0.32):
        ax.plot([x, x], [y0 + 0.05, y1 - 0.05], color="#c0392b", lw=1)
    for x in np.arange(L1 - 0.1, L1 - 3.6, -0.32):
        ax.plot([x, x], [y0 + 0.05, y1 - 0.05], color="#c0392b", lw=1)
    for x in np.arange(L0 + 4.0, L1 - 3.6, 0.85):
        ax.plot([x, x], [y0 + 0.05, y1 - 0.05], color="#c0392b", lw=0.7)
    for x in (6.7, 6.95, 7.2, 7.45, 7.9, 8.15, 8.4, 8.65):
        ax.plot([x, x], [y0 + 0.05, y1 - 0.05], color="#c0392b", lw=2)
    ax.text(7.7, 5.0, "cốt treo (dầm phụ gác lên)", fontsize=8, color="#c0392b", ha="center")
    ys = 1.45
    ax.annotate("", xy=(L0, ys), xytext=(L0 + 3.6, ys), arrowprops=dict(arrowstyle="<|-|>", lw=1))
    ax.text(L0 + 1.8, ys - 0.38, "l1 = max(L/4; x1), s theo h", fontsize=8, ha="center")
    ax.annotate("", xy=(L0 + 3.6, ys), xytext=(L1 - 3.6, ys), arrowprops=dict(arrowstyle="<|-|>", lw=1))
    ax.text(7.5, ys - 0.38, "giữa nhịp: s ≤ min(3h/4; 500)", fontsize=8, ha="center")
    ax.annotate("", xy=(L1 - 3.6, ys), xytext=(L1, ys), arrowprops=dict(arrowstyle="<|-|>", lw=1))
    ax.text(L1 - 1.8, ys - 0.38, "l1", fontsize=8, ha="center")
    ax.text(0.3, 0.35, "Đai đầu tiên cách mép cột 50; số đai một vùng n = ⌊(l − 50)/s⌋ + 1; thanh dầm dài hơn 11,7 m phải có vị trí nối.",
            fontsize=8.5, style="italic")
    save(fig, IMG_CT / "bs_07_dam_bo_tri_doc_so_do.png")


# ---------------------------------------------------------------- bs_08
def bs_08():
    fig, ax = new(9.5, 10.5, "Vùng đai và mối nối dọc cột (sơ đồ)")
    cx0, cx1 = 1.2, 2.6
    ax.add_patch(Rectangle((cx0 - 0.4, 0.3), 2.2, 0.5, fc="#cccccc", ec="k"))
    ax.text(cx0 + 0.7, 0.55, "móng — 3 đai, chân L ≥ 200", fontsize=7.5, ha="center")
    for x in (cx0, cx1):
        ax.plot([x, x], [0.8, 9.6], color="k", lw=1.2)
    zones = [(0.8, 1.9, "đầu cột tầng 1\nld = max(hc; Hn/6; 450)\ns ≤ 10dmin", "#f3b9b3", 0.18),
             (1.9, 4.2, "giữa cột\ns ≤ min(15dmin; 500)", "#ffffff", 0.45),
             (4.2, 5.1, "đầu cột (sát sàn)\ns ≤ 10dmin", "#f3b9b3", 0.18),
             (5.1, 5.9, "NÚT — đai không cắt", "#d98880", 0.2),
             (5.9, 7.4, "đoạn nối Lov\ns ≤ min(10dmin; 300)", "#f3b9b3", 0.18),
             (7.4, 9.0, "giữa cột tầng 2\ns ≤ min(15dmin; 500)", "#ffffff", 0.45)]
    for y0, y1, t, c, st in zones:
        ax.add_patch(Rectangle((cx0, y0), cx1 - cx0, y1 - y0, fc=c, ec="none", alpha=0.7))
        y = y0 + 0.05
        while y < y1:
            ax.plot([cx0, cx1], [y, y], color="#7b241c", lw=0.9)
            y += st
        ax.text(3.0, (y0 + y1) / 2, t, fontsize=8, va="center")
    ax.plot([cx0 + 0.25, cx0 + 0.25], [0.8, 7.4], color="#2c5f8a", lw=3)
    ax.plot([cx0 + 0.4, cx0 + 0.4], [5.9, 9.4], color="#3f7d3a", lw=3)
    ax.text(0.2, 7.55, "thép tầng 1 nhô Lov\nqua sàn tầng 2", fontsize=7.5, color="#2c5f8a")
    ax.text(0.2, 9.55, "thép tầng 2 bắt đầu\ntừ mặt sàn", fontsize=7.5, color="#3f7d3a")
    ax.add_patch(Rectangle((cx0 - 1.0, 5.1), 1.0, 0.8, fc="#bbbbbb", ec="k", alpha=0.6))
    ax.add_patch(Rectangle((cx1, 5.1), 1.0, 0.8, fc="#bbbbbb", ec="k", alpha=0.6))
    ax.text(5.0, 6.0, "≤ 4 thanh/cạnh: nối 1 vị trí;\n> 4 thanh: nối so le ≤ 50%,\ncách ≥ 1,5·Lan", fontsize=8, color="#c0392b")
    save(fig, IMG_CT / "bs_08_cot_vung_dai_noi_so_do.png")


# ---------------------------------------------------------------- bs_09
def bs_09():
    fig, ax = new(10.5, 9, "Cổng chặn trước khi xuất bản vẽ (R41–R46)")
    items = [("R41  Kiểm hình học nút 14.2\n(thép trên, dưới, dầm vuông góc)", DO, "không đạt → KHÔNG VẼ, trả phương án"),
             ("R42  Kiểm phạm vi 14.1\n(xoắn, dầm cao, lỗ mở, vách, động đất…)", DO, "thuộc diện → DỪNG, ghi lý do"),
             ("R43  Hai dầm cắt nhau cùng cao độ\n→ tính lại h0 dầm thấp (a' = a + d_kia)", CAM, "Mu < M → chọn lại thép"),
             ("R44  Tiền lượng / μ ngoài khoảng 14.4", VANG, "chỉ CẢNH BÁO, không chặn"),
             ("R45  Gắn basis cho mọi con số\nTCVN / thuc_hanh / uoc_luong / can_xac_nhan", CAM, "có uoc_luong / can_xac_nhan → cờ\n'chưa đủ để phát hành'"),
             ("R46  Hoàn tất", LUC, "KHÔNG in 'ĐẠT' khi còn cờ R41–R45\nhoặc ⚠ ở Chương 13")]
    for i, (t, c, ghi) in enumerate(items):
        y = 7.6 - i * 1.38
        box(ax, 0.3, y, 5.2, 1.0, t, c, fs=8.8, dashed=(c == DO))
        ax.text(5.8, y + 0.5, ghi, fontsize=8.5, va="center", color="#c0392b" if c == DO else "#333")
        if i:
            arrow(ax, (2.9, y + 1.38), (2.9, y + 1.0), lw=1.0)
    save(fig, IMG_CT / "bs_09_cong_chan_R41_R46.png")


# ---------------------------------------------------------------- bs_10
def bs_10():
    fig, ax = new(15, 7.2, "Phạm vi áp dụng của skill: đủ / chưa đủ / dừng và hỏi")
    cols = [("ĐỦ chọn và bố trí", LUC,
             ["Khung BTCT toàn khối", "dầm chữ nhật/chữ T, cột chữ nhật", "tải đứng + gió, cấu kiện thường",
              "(Chương 7–9, 12)", "điều kiện: qua cổng hình học nút 14.2"]),
            ("CHƯA ĐỦ / CÓ QUY TRÌNH", VANG,
             ["Có động đất → Chương 13 sơ bộ (⚠), cần TCVN 9386:2012", "Dầm chịu xoắn → 15.1 (3 điểm ⚠, R47–R50)",
              "Cột nén lệch tâm xiên → gần đúng, kiểm phần mềm", "Chống cháy, môi trường xâm thực → chỉ lớp bảo vệ"]),
            ("DỪNG VÀ HỎI (R42)", DO,
             ["Dầm cao  L_ef/h < 3  → R51", "Lỗ mở xuyên dầm  → R52", "Khung có vách cứng, lõi thang", "Sàn, móng, giằng móng, cầu thang",
              "Dầm ứng lực trước, nhịp lớn", "Cột tròn / vành khuyên"])]
    for i, (ten, c, dong) in enumerate(cols):
        x = 0.3 + i * 4.9
        ax.add_patch(Rectangle((x, 0.4), 4.6, 5.8, fc=c[0], ec=c[1], lw=1.8))
        ax.text(x + 0.15, 5.85, ten, fontsize=11, fontweight="bold", color=c[1])
        for k, d in enumerate(dong):
            ax.text(x + 0.15, 5.2 - k * 0.85, textwrap.fill("• " + d, 42), fontsize=9, va="top")
    save(fig, IMG_CT / "bs_10_pham_vi_ap_dung.png")


# ---------------------------------------------------------------- bs_11
def bs_11():
    fig, ax = new(11, 8, "Cột mạnh – dầm yếu: Σ MRc ≥ 1,3 Σ MRb (⚠ EN 1998-1)")
    cx, cy = 4.0, 4.0
    ax.add_patch(Rectangle((cx - 0.45, 0.8), 0.9, 6.4, fc="#eeeeee", ec="k"))
    ax.add_patch(Rectangle((0.8, cy - 0.45), 6.4, 0.9, fc="#eeeeee", ec="k"))
    ax.add_patch(Rectangle((cx - 0.45, cy - 0.45), 0.9, 0.9, fc="#cccccc", ec="k"))
    for (x, y, dx, dy, t, c) in [(cx - 0.9, 6.3, 1.0, 0.0, "MRc,top", "#2c5f8a"), (cx + 0.9, 1.6, -1.0, 0.0, "MRc,bot", "#2c5f8a")]:
        ax.add_patch(Arc((cx, y), 1.8, 1.0, theta1=20, theta2=160, color=c, lw=2.2))
        ax.text(cx + 1.2, y + 0.2, t, color=c, fontsize=10)
    ax.add_patch(Arc((1.9, cy), 1.0, 1.7, theta1=110, theta2=250, color="#d9822b", lw=2.2))
    ax.text(0.3, cy + 1.2, "MRb,trái", color="#d9822b", fontsize=10)
    ax.add_patch(Arc((6.1, cy), 1.0, 1.7, theta1=-70, theta2=70, color="#d9822b", lw=2.2))
    ax.text(6.3, cy - 1.4, "MRb,phải", color="#d9822b", fontsize=10)
    ax.plot([1.0, 1.0], [cy - 0.1, cy + 0.1], "o", color="#c0392b", ms=9)
    ax.plot([7.0, 7.0], [cy - 0.1, cy + 0.1], "o", color="#c0392b", ms=9)
    ax.text(0.5, cy - 0.9, "khớp dẻo\nở dầm", color="#c0392b", fontsize=8.5)
    box(ax, 7.6, 5.4, 3.2, 1.6, "Σ MRc ≥ 1,3 · Σ MRb\n(N của tổ hợp động đất,\nthép thực tế của dầm)", XANH, fs=9)
    box(ax, 7.6, 3.2, 3.2, 1.5, "Không đạt → báo\ntăng cột / giảm thép dầm\nKHÔNG tự tăng thép cột (R39)", DO, fs=9)
    box(ax, 7.6, 1.0, 3.2, 1.6, "Vd_dầm = V(g+ψq) ± γRd·ΣMRb/lcl\nγRd = 1,0 (DCM), 1,2 (DCH)", XAM, fs=8.5)
    save(fig, IMG_CT / "bs_11_cot_manh_dam_yeu.png")


# ---------------------------------------------------------------- bs_14
def bs_14():
    import numpy as np
    fig, ax = new(11, 6.2, "Bán kính uốn hay đường kính uốn? — ba nguồn, hai đại lượng (thanh Ø16)")
    # thanh uốn vuông: ngang rồi xuống
    r = 1.3
    ax.plot([0.6, 3.4], [4.4, 4.4], color="k", lw=7, solid_capstyle="butt")
    cxx, cyy = 3.4, 4.4 - r
    ang = np.linspace(np.pi / 2, 0, 40)
    ax.plot(cxx + r * np.cos(ang), cyy + r * np.sin(ang), color="k", lw=7)
    ax.plot([cxx + r, cxx + r], [cyy, 1.4], color="k", lw=7, solid_capstyle="butt")
    ax.add_patch(Circle((cxx, cyy), r, fc="none", ec="#c0392b", lw=1.4, ls="--"))
    ax.add_patch(Circle((cxx, cyy), r / 2, fc="none", ec="#2c5f8a", lw=1.4, ls="--"))
    ax.plot([cxx, cxx + r], [cyy, cyy], color="#c0392b", lw=1.6)
    ax.text(cxx + r / 2, cyy - 0.28, "r = 5d = 80", color="#c0392b", fontsize=9, ha="center")
    ax.plot([cxx - r / 2, cxx + r / 2], [cyy - 0.6, cyy - 0.6], color="#2c5f8a", lw=1.6)
    ax.text(cxx, cyy - 0.95, "D = 5d = 80", color="#2c5f8a", fontsize=9, ha="center")
    ax.text(0.5, 0.5, "A (hình 5.13): BÁN KÍNH trong r ≥ 5d (d<20), 8d (d≥20)  → D = 160 (Ø16)\n"
                      "code neo_noi.duong_kinh_uon_toi_thieu: ĐƯỜNG KÍNH D = 5d / 8d  → 80 (Ø16), 200 (Ø25)\n"
                      "skill Vẽ (TCVN 4453): D ≥ 5d (d ≤ 10), 8d (12–28), 10d (> 28)  → 128 (Ø16), 200 (Ø25)",
            fontsize=8.5, va="bottom")
    box(ax, 6.7, 2.2, 3.9, 2.3, "Mặc định an toàn:\nA — bán kính 5d / 8d\n(ghi rõ 'bán kính' hay 'đường kính'\nvà nguồn khi giao Drawing)", LUC, fs=9)
    save(fig, IMG_CT / "bs_14_uon_neo_bankinh.png")


# ---------------------------------------------------------------- bs_12 (Input Adapter)
def bs_12():
    fig, ax = new(14, 9.6, "Báo cáo ETABS thật: nối các bảng theo Frame → phần tử chuẩn hoá")
    bang = [("Grid Lines", "GridID, XRYZCoord (m) → toa_do_truc (mm)"),
            ("Story Definitions", "Name, Elevation (m) → cao_do_moc (mm)"),
            ("Joint Coordinates", "Joint, GlobalX, GlobalZ (m)"),
            ("Connectivity - Frame", "Frame, JointI, JointJ, Length (m)"),
            ("Frame Section Assignments", "Frame → DesignSect"),
            ("Frame Props 01 – General", "SectionName, Material, t2 = b, t3 = h (m)"),
            ("Frame Props 03/06 (bê tông)", "RebarMatL (thép dọc), RebarMatC (đai)"),
            ("Conc Sum1 (CỘT, PMM)", "PMMDemandN, PMMDemandM, PMMArea (m²), PMMCombo"),
            ("Conc Sum2 (DẦM)", "Location, FTopArea, FBotArea (m²), VRebar, Combo")]
    for i, (t, d) in enumerate(bang):
        y = 7.4 - i * 0.82
        box(ax, 0.3, y, 4.9, 0.68, t + "\n" + d, XAM, fs=7.8)
        arrow(ax, (5.2, y + 0.34), (7.0, 4.4), lw=0.9, col="#888888")
    box(ax, 7.0, 3.3, 3.2, 2.2, "PhanTuKhung\nten, loai (dam/cot), b, h,\nmac_be_tong, nhom_thep_doc/dai,\ntruc, tang, chieu_dai,\nvi_tri[ ] { As_yc, M, N, Q, to_hop }", XANH, fs=8.8)
    box(ax, 10.7, 5.6, 3.0, 1.6, "Đơn vị: m → mm; m² → mm²\nlực kN, mô men kN·m", VANG, fs=8.5)
    box(ax, 10.7, 3.5, 3.0, 1.7, "Cột: N = |PMMDemandN|\n(ETABS nén âm → nén dương)\nAs_yc = PMMArea là MỖI PHÍA", LUC, fs=8.5)
    box(ax, 10.7, 1.3, 3.0, 1.9, "Dầm: KHÔNG có Q thô, KHÔNG có M\n→ \"Q: KHÔNG CÓ\"\ngối = mặt trên (FTop), nhịp = mặt dưới", DO, fs=8.5)
    save(fig, IMG_ND / "bs_12_etabs_noi_bang.png")


# ---------------------------------------------------------------- bs_13 (Verification)
def bs_13():
    fig, ax = new(15, 9.4, "Kiểm chứng: việc tool đọc được bản vẽ và việc chỉ kiểm bằng dữ liệu/ báo cáo")
    rows = [
        ("Layer hợp lệ (mục 10.7.2)", "TOOL", "kiem_chung_ban_ve"),
        ("Mặt cắt khớp kích thước b×h", "TOOL", "mat_cat"),
        ("Đủ nhãn mặt cắt kỳ vọng", "TOOL", "mat_cat"),
        ("Số cấu kiện vẽ ra ≥ kỳ vọng", "TOOL", "mat_dung_khung"),
        ("Số vòng tròn số hiệu thép ≥ kỳ vọng", "TOOL", "mat_dung_khung"),
        ("Vòng tròn ký hiệu trục", "TOOL", "mat_dung_khung"),
        ("Bảng thống kê đủ 8 cột", "TOOL", "mat_dung_khung"),
        ("Khớp As trong nhãn với As_thuc", "DỮ LIỆU", "so sánh với kết quả Rule Engine trong yêu cầu"),
        ("Điểm cắt thép, chiều dài thanh, vùng đai (12.8)", "BÁO CÁO", "không đọc được từ bản vẽ — hỏi/ghi cờ"),
        ("Hình học nút: thép dầm lọt thép cột (14.7)", "BÁO CÁO", "R41 — không có tool"),
        ("Cấu tạo nút theo bảng NK/DM/CT", "BÁO CÁO", "không có tool"),
        ("Kháng chấn, xoắn, dầm cao, lỗ mở", "DỪNG", "R42, R51, R52"),
        ("Cờ basis (uoc_luong / can_xac_nhan)", "BÁO CÁO", "R45, R46: không in 'ĐẠT'"),
    ]
    mau = {"TOOL": XANH, "DỮ LIỆU": CAM, "BÁO CÁO": VANG, "DỪNG": DO}
    ax.text(0.3, 8.65, "Việc kiểm", fontsize=10, fontweight="bold")
    ax.text(7.2, 8.65, "Cách kiểm", fontsize=10, fontweight="bold")
    ax.text(9.4, 8.65, "Ghi chú", fontsize=10, fontweight="bold")
    for i, (t, loai, ghi) in enumerate(rows):
        y = 7.85 - i * 0.6
        ax.add_patch(Rectangle((0.2, y - 0.22), 14.6, 0.5, fc=mau[loai][0] if loai == "TOOL" else "#ffffff", ec="#cccccc"))
        ax.text(0.3, y, t, fontsize=9, va="center")
        box(ax, 7.0, y - 0.2, 1.9, 0.42, loai, mau[loai], fs=8.5, bold=True)
        ax.text(9.4, y, ghi, fontsize=8.5, va="center")
    save(fig, IMG_KC / "bs_13_kiem_chung_ma_tran.png")


def main():
    for f in (bs_01, bs_02, bs_03, bs_04, bs_05, bs_06, bs_07, bs_08, bs_09, bs_10, bs_11, bs_12, bs_13, bs_14):
        f()


if __name__ == "__main__":
    sys.exit(main())
