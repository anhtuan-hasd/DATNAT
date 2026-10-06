# QUY CÁCH VẼ VÀ ĐẶC TẢ ĐỒ HỌA DÀNH CHO AI AGENT: KHUNG VẼ KỸ THUẬT XÂY DỰNG VÀ KẾT CẤU BÊ TÔNG CỐT THÉP (TCVN 8-20:2002, TCVN 4612-88, TCVN 5705-1993)

> **Mục tiêu tài liệu**: Cung cấp bộ thông số đồ họa chi tiết, mã mẫu SVG vector, quy tắc render tọa độ, và bộ tiêu chí kiểm thử hình học để AI Agent có thể **tự động vẽ, biểu diễn và xuất bản vẽ 2D kỹ thuật chính xác 100%** theo các tiêu chuẩn Việt Nam (TCVN).

---

## I. MÔ HÌNH TỌA ĐỘ VÀ THAM SỐ KHỔ GIẤY (GRAPHICS & COORDINATE SYSTEM)

AI Agent khi sinh bản vẽ đồ họa vector (SVG/DXF/Canvas/Matplotlib) phải tuân thủ hệ tọa độ phẳng tiêu chuẩn:

1. **Gốc tọa độ $(0, 0)$**: Đặt tại **Góc dưới - bên trái (Bottom-Left)** của tờ giấy (đối với DXF/CAD/Matplotlib) hoặc **Góc trên - bên trái (Top-Left)** (đối với SVG/Canvas, với trục Y hướng xuống).
2. **Đơn vị hệ thống**: Milimét ($mm$) thực tế trên khổ giấy. Đối với SVG/Raster: $1mm = 3.779528 px$ (ở độ phân giải 96 DPI) hoặc $1mm = 1.0 unit$ (SVG User Unit).

### Bảng tham số kích thước khổ giấy & khung tên (TCVN 7285-2003)

| Khổ giấy | Kích thước $(W \times H)$ (mm) | Lề trái (Đóng tập) | Lề ngoài (Xén) | Khung bản vẽ $(W_f \times H_f)$ | Vị trí Khung tên (Góc dưới-phải) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A0** | $1189 \times 841$ | $25mm$ | $10mm$ | $1154 \times 821$ | $(1179-140, 10) \rightarrow (1179, 10+60)$ |
| **A1** | $841 \times 594$ | $25mm$ | $10mm$ | $806 \times 574$ | $(831-140, 10) \rightarrow (831, 10+60)$ |
| **A2** | $594 \times 420$ | $25mm$ | $5mm$ | $564 \times 410$ | $(589-140, 5) \rightarrow (589, 5+60)$ |
| **A3** | $420 \times 297$ | $25mm$ | $5mm$ | $390 \times 287$ | $(415-140, 5) \rightarrow (415, 5+60)$ |
| **A4** | $210 \times 297$ | $25mm$ | $5mm$ | $180 \times 287$ | $(205-140, 5) \rightarrow (205, 5+60)$ |

---

## II. ĐẶC TẢ 7 LOẠI NÉT VẼ ĐỒ HỌA (TCVN 8-20:2002)

AI Agent phải cấu hình thuộc tính `stroke-width`, `stroke-dasharray`, và `stroke` theo đúng chuẩn nét vẽ:

![Quy cách 7 loại nét vẽ TCVN 8-20:2002](visual_spec/fig1_line_types.png)

### 1. Bảng quy đổi thông số Đồ họa cho 7 loại Nét vẽ (Khổ A3/A4 chọn $s = 0.7mm$)

| Ký hiệu | Tên nét vẽ | Bề rộng nét $s$ (mm) | thuộc tính SVG `stroke-width` | thuộc tính `stroke-dasharray` | Màu chuẩn CAD / Vector |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **A** | **Nét liền đậm** | $s = 0.70mm$ | `2.64px` ($0.7mm$) | `none` (Liền nét) | `#000000` (Black) |
| **B** | **Nét liền mảnh** | $s/3 = 0.25mm$ | `0.94px` ($0.25mm$) | `none` (Liền nét) | `#333333` (Dark Gray) |
| **C** | **Nét đứt** | $s/2 = 0.35mm$ | `1.32px` ($0.35mm$) | `12 4` (Gạch 3mm, hở 1mm) | `#000000` (Black) |
| **D** | **Nét gạch chấm mảnh** | $s/3 = 0.25mm$ | `0.94px` ($0.25mm$) | `24 4 2 4` (Gạch 6mm, hở 1mm, chấm 0.5mm, hở 1mm) | `#1a5276` (Navy Blue) |
| **E** | **Nét cắt** | $1.2s = 0.85mm$ | `3.20px` ($0.85mm$) | `none` (Vết cắt đầu/cuối dài 10-15mm) | `#c0392b` (Red / Dark Red) |
| **F** | **Nét zíc-zắc** | $s/2 = 0.35mm$ | `1.32px` ($0.35mm$) | Dạng đường gấp khúc đều đặn | `#333333` (Dark Gray) |
| **G** | **Nét lượn sóng** | $s/2 = 0.35mm$ | `1.32px` ($0.35mm$) | Đường cong Bezier biên giới cắt riêng | `#333333` (Dark Gray) |

### 2. Mẫu mã SVG (SVG Vector Pattern) biểu diễn 7 nét vẽ

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220" viewBox="0 0 400 220">
  <!-- A. Nét liền đậm (s = 0.7mm) -->
  <line x1="20" y1="20" x2="380" y2="20" stroke="#000000" stroke-width="2.64" stroke-linecap="butt" />
  
  <!-- B. Nét liền mảnh (s/3 = 0.25mm) -->
  <line x1="20" y1="50" x2="380" y2="50" stroke="#333333" stroke-width="0.94" />
  
  <!-- C. Nét đứt (s/2 = 0.35mm) -->
  <line x1="20" y1="80" x2="380" y2="80" stroke="#000000" stroke-width="1.32" stroke-dasharray="12 4" />
  
  <!-- D. Nét gạch chấm mảnh (s/3 = 0.25mm) -->
  <line x1="20" y1="110" x2="380" y2="110" stroke="#1a5276" stroke-width="0.94" stroke-dasharray="24 4 2 4" />
  
  <!-- E. Nét cắt (1.2s = 0.85mm) -->
  <line x1="20" y1="140" x2="80" y2="140" stroke="#c0392b" stroke-width="3.20" />
  <line x1="80" y1="140" x2="320" y2="140" stroke="#c0392b" stroke-width="0.94" stroke-dasharray="24 4 2 4" />
  <line x1="320" y1="140" x2="380" y2="140" stroke="#c0392b" stroke-width="3.20" />
  
  <!-- G. Nét lượn sóng (s/2 = 0.35mm) -->
  <path d="M 20 170 Q 40 160 60 170 T 100 170 T 140 170 T 180 170 T 220 170 T 260 170 T 300 170 T 340 170 T 380 170" fill="none" stroke="#333333" stroke-width="1.32" />
</svg>
```

---

## III. QUY TẮC RENDER CẤU TRÚC GHI KÍCH THƯỚC (TCVN 5705-1993)

Mọi kích thước do AI Agent vẽ ra phải cấu thành đủ 3 thành phần hình học:

![Cấu trúc đường ghi kích thước TCVN 5705-1993](visual_spec/fig2_dimensioning.png)

1. **Đường dóng kích thước (Extension Lines)**:
   - Dùng **Nét liền mảnh** (`stroke-width="0.94px"`).
   - Vẽ vuông góc với đoạn cần đo.
   - Phải **vượt quá đường kích thước một khoảng $2 \div 3mm$**.
2. **Đường kích thước (Dimension Lines)**:
   - Dùng **Nét liền mảnh** (`stroke-width="0.94px"`), song song với đoạn cần đo.
   - Khoảng cách từ đường kích thước đến đường bao vật thể: tối thiểu $7 \div 10mm$.
   - **Đầu đường kích thước**: Giới hạn bằng mũi tên đặc (góc nhọn $15^\circ \div 20^\circ$, chiều dài $4s \div 6s \approx 3 \div 4mm$) hoặc gạch chéo $45^\circ$ dài $2 \div 3mm$.
3. **Con số kích thước (Dimension Text)**:
   - Font chữ kỹ thuật (`DejaVu Sans` / `ISOCPEUR` / `Arial`).
   - Đặt ở **chính giữa và phía trên đường kích thước**, cách đường kích thước $1 \div 1.5mm$.
   - Chiều cao chữ $h = 2.5mm \div 3.5mm$.

### Mẫu mã SVG chi tiết cho Đường Kích Thước:

```xml
<g id="dimension_line_example">
  <!-- Marker Mũi tên -->
  <defs>
    <marker id="arrow_start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 0 L 0 5 L 10 10 z" fill="#000000" />
    </marker>
    <marker id="arrow_end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#000000" />
    </marker>
  </defs>

  <!-- 1. Đường dóng (Extension lines) -->
  <line x1="50" y1="100" x2="50" y2="140" stroke="#333333" stroke-width="0.94" />
  <line x1="250" y1="100" x2="250" y2="140" stroke="#333333" stroke-width="0.94" />

  <!-- 2. Đường kích thước (Dimension line với mũi tên 2 đầu) -->
  <line x1="50" y1="130" x2="250" y2="130" stroke="#000000" stroke-width="0.94" marker-start="url(#arrow_start)" marker-end="url(#arrow_end)" />

  <!-- 3. Con số kích thước (Text) -->
  <text x="150" y="125" font-family="DejaVu Sans, Arial" font-size="12" font-weight="bold" text-anchor="middle" fill="#000000">3000</text>
</g>
```

---

## IV. QUY TẮC BÊ TÔNG TRONG SUỐT VÀ CHI TIẾT DẦM BTCT (TCVN 4612-88)

Đối với bản vẽ kết cấu BTCT, AI Agent phải thực thi quy tắc đặc thù: **Lớp bê tông được quy ước coi là trong suốt, để cốt thép bên trong nổi bật lên**.

![Quy tắc Bê tông trong suốt và Dầm BTCT TCVN 4612-88](visual_spec/fig3_rc_beam.png)

### 1. Phân định độ dày nét vẽ cho Cấu kiện BTCT

- **Đường bao bê tông (Mép ngoài dầm/cột/sàn)**: Dùng **Nét liền mảnh** ($s/3 = 0.25mm$, thuộc tính `stroke-width="0.94px"`, màu xám xậm/đen mảnh).
- **Cốt thép chịu lực chính (Thanh dọc $\varnothing 16, \varnothing 20, \varnothing 22$)**: Dùng **Nét liền đậm** ($s = 0.7 \div 1.0mm$, thuộc tính `stroke-width="2.64px \div 3.78px"`, màu đen đậm).
- **Cốt đai ($\varnothing 6, \varnothing 8$)**: Dùng nét đậm vừa ($s/2 = 0.35 \div 0.5mm$, thuộc tính `stroke-width="1.32px \div 1.89px"`).
- **Trên Mặt cắt ngang**: Cốt thép dọc bị cắt qua được thể hiện bằng **Hình tròn đặc (Solid Black Circle)** với đường kính $r = 1.5 \div 2.5mm$.

### 2. Bán kính uốn & Móc neo Cốt thép (TCVN 4453:1995 & TCVN 5574:2018)

- **Cốt thép trơn (CB240-T, $\varnothing \le 10mm$)**: Móc uốn $180^\circ$, đường kính uốn $D \ge 2.5d$, đoạn thẳng kéo dài sau móc $l_n \ge 3d$ (tối thiểu $30mm$).
- **Cốt thép gai (CB300-V, CB400-V, $\varnothing \ge 12mm$)**: Đoạn uốn $90^\circ \div 135^\circ$, đường kính uốn $D \ge 5d \div 8d$.
- **Móc cốt đai ($135^\circ$)**: Đoạn neo sau móc $l_n \ge 5d \div 10d$ (tối thiểu $50mm$).

### 3. Mã SVG Vector mẫu cho Mặt cắt ngang Dầm BTCT ($300 \times 500mm$)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="260" height="360" viewBox="0 0 260 360">
  <!-- 1. Đường bao Bê tông (Nét liền mảnh s/3) -->
  <rect x="30" y="30" width="200" height="300" fill="#ffffff" stroke="#555555" stroke-width="0.94" />
  
  <!-- 2. Cốt đai Ø6 (Nét s/2, ôm trong lớp bảo vệ 25mm) -->
  <rect x="45" y="45" width="170" height="270" rx="8" ry="8" fill="none" stroke="#e67e22" stroke-width="1.89" />
  
  <!-- 3. Cốt thép dọc (Các chấm tròn đặc tô đen) -->
  <!-- 2 Thanh lớp trên 2Ø16 -->
  <circle cx="55" cy="55" r="6" fill="#000000" />
  <circle cx="205" cy="55" r="6" fill="#000000" />
  
  <!-- 3 Thanh lớp dưới 3Ø20 -->
  <circle cx="55" cy="305" r="7.5" fill="#000000" />
  <circle cx="130" cy="305" r="7.5" fill="#000000" />
  <circle cx="205" cy="305" r="7.5" fill="#000000" />

  <!-- 4. Ký hiệu Số hiệu thanh & Đường dẫn -->
  <!-- Đường dẫn chỉ cốt đai -->
  <polyline points="100,100 60,130 10,130" fill="none" stroke="#333333" stroke-width="0.94" />
  <circle cx="10" cy="130" r="10" fill="#ffffff" stroke="#000000" stroke-width="0.94" />
  <text x="10" y="134" font-family="Arial" font-size="10" font-weight="bold" text-anchor="middle">5</text>
  <text x="35" y="125" font-family="Arial" font-size="9" font-weight="bold">Ø6a150</text>
  
  <!-- Đường kích thước tiết diện -->
  <line x1="30" y1="340" x2="230" y2="340" stroke="#000000" stroke-width="0.94" marker-start="url(#arrow_start)" marker-end="url(#arrow_end)" />
  <text x="130" y="335" font-family="Arial" font-size="11" font-weight="bold" text-anchor="middle">300</text>
</svg>
```

---

## V. KÝ HIỆU VẬT LIỆU TRÊN MẶT CẮT (TCVN 7-1993)

AI Agent phải định nghĩa đúng mẫu Hatch Pattern trong SVG `<defs>` để tô vật liệu trên mặt cắt:

![Ký hiệu vật liệu trên mặt cắt TCVN 7-1993](visual_spec/fig4_material_hatching.png)

### Mã SVG Hatch Patterns cho 4 Vật liệu Xây dựng Phổ biến:

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0">
  <defs>
    <!-- 1. Hatch Bê tông cốt thép (BTCT): Đường nghiêng 45 deg + Dấu chấm rải rác -->
    <pattern id="hatch_btct" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="20" stroke="#000000" stroke-width="0.8" />
      <line x1="10" y1="0" x2="10" y2="20" stroke="#000000" stroke-width="0.8" />
      <circle cx="5" cy="5" r="1" fill="#000000" />
      <circle cx="15" cy="15" r="1" fill="#000000" />
    </pattern>

    <!-- 2. Hatch Bê tông thường (BT): Đường nghiêng 45 deg cách đều -->
    <pattern id="hatch_betong" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="12" stroke="#000000" stroke-width="0.8" />
    </pattern>

    <!-- 3. Hatch Tường gạch xây: Nét đôi 45 deg song song -->
    <pattern id="hatch_gach" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="16" stroke="#000000" stroke-width="0.8" />
      <line x1="3" y1="0" x2="3" y2="16" stroke="#000000" stroke-width="0.8" />
    </pattern>

    <!-- 4. Hatch Kim loại / Thép: Đường kẻ nghiêng 45 deg mật độ dày -->
    <pattern id="hatch_kimloai" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="6" stroke="#000000" stroke-width="0.8" />
    </pattern>
  </defs>
</svg>
```

---

## VI. BẢNG THỐNG KÊ CỐT THÉP chuẩn 8 CỘT (TCVN 4612-88)

Bảng thống kê cốt thép bắt buộc đặt sát phía trên Khung tên bản vẽ, có cấu trúc **đúng 8 cột** từ trái qua phải:

```xml
<!-- Khung Bảng Thống kê Cốt thép 8 Cột trong SVG -->
<g id="rebar_schedule_table" transform="translate(10, 10)">
  <!-- Khung bao ngoại -->
  <rect x="0" y="0" width="500" height="120" fill="none" stroke="#000000" stroke-width="1.89" />
  
  <!-- Tiêu đề 8 cột -->
  <path d="M 0,30 L 500,30 M 0,60 L 500,60" stroke="#000000" stroke-width="0.94" />
  
  <!-- Các vạch dọc chia 8 cột -->
  <!-- Cột 1: Tên cấu kiện (60mm) | Cột 2: Số hiệu (40mm) | Cột 3: Hình dáng (100mm) | Cột 4: Đường kính (40mm) | Cột 5: Chiều dài 1 thanh (60mm) | Cột 6: Số lượng (40mm) | Cột 7: Tổng chiều dài (80mm) | Cột 8: Tổng trọng lượng (80mm) -->
  <line x1="60" y1="0" x2="60" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="100" y1="0" x2="100" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="200" y1="0" x2="200" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="240" y1="0" x2="240" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="300" y1="0" x2="300" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="340" y1="0" x2="340" y2="120" stroke="#000000" stroke-width="0.94" />
  <line x1="420" y1="0" x2="420" y2="120" stroke="#000000" stroke-width="0.94" />

  <!-- Text Tiêu đề các Cột -->
  <text x="30" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Tên CK</text>
  <text x="80" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Số hiệu</text>
  <text x="150" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Hình dáng thanh</text>
  <text x="220" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Ø (mm)</text>
  <text x="270" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">L (mm)</text>
  <text x="320" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Số lượng</text>
  <text x="380" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Tổng L (m)</text>
  <text x="460" y="20" font-family="Arial" font-size="9" font-weight="bold" text-anchor="middle">Trọng lượng (kg)</text>
</g>
```

---

## VII. PYTHON ENGINE CHO AI AGENT SINH BẢN VẼ ĐỒ HỌA CHUẨN TCVN

AI Agent có thể thực thi đoạn script Python dưới đây để tự động tạo file vector SVG hoặc ảnh PNG chất lượng cao cho bất kỳ dầm BTCT nào:

```python
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_rc_beam_drawing(beam_length, beam_width, beam_height, output_filepath):
    """
    Hàm sinh bản vẽ đồ họa Dầm BTCT chuẩn TCVN dành cho AI Agent
    """
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(-10, beam_length + 20)
    ax.set_ylim(-20, beam_height + 40)
    ax.axis('off')

    # 1. Vẽ bao bê tông (Nét liền mảnh s/3)
    concrete_box = patches.Rectangle((0, 0), beam_length, beam_height, 
                                     linewidth=0.8, edgecolor='#333333', 
                                     facecolor='#fdfdfd', linestyle='--')
    ax.add_patch(concrete_box)

    # 2. Bố trí Cốt thép dọc (Nét đậm s = 0.7mm)
    cover = 25  # Lớp bảo vệ bê tông 25mm
    # Thép dưới
    ax.plot([cover, beam_length - cover], [cover, cover], color='black', linewidth=2.5)
    # Thép trên
    ax.plot([cover, beam_length - cover], [beam_height - cover, beam_height - cover], color='black', linewidth=2.0)

    # 3. Bố trí Cốt đai (Nét s/2)
    stirrup_spacing = 150
    for x in range(cover, int(beam_length - cover), stirrup_spacing):
        ax.plot([x, x], [cover, beam_height - cover], color='#e67e22', linewidth=1.2)

    # 4. Ghi kích thước dầm (TCVN 5705-1993)
    ax.plot([0, beam_length], [-12, -12], color='black', linewidth=0.8)
    ax.plot([0, 0], [-5, -15], color='black', linewidth=0.8)
    ax.plot([beam_length, beam_length], [-5, -15], color='black', linewidth=0.8)
    ax.text(beam_length / 2, -10, f"L = {beam_length}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.title(f"BẢN VẼ THIẾT KẾ DẦM BTCT {beam_width}x{beam_height} - CHUẨN TCVN", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_filepath)
    plt.close()

# Ví dụ thực thi cho dầm dài 4000mm, tiết diện 200x400mm
generate_rc_beam_drawing(4000, 200, 400, "/workspace/scratch/visual_spec/rc_beam_auto.png")
```

---

## VIII. CHECKLIST TỰ KIỂM HÌNH HỌC & ĐỒ HỌA DÀNH CHO AI AGENT (VALIDATION MATRIX)

Trước khi xuất file bản vẽ chính thức cho người dùng, AI Agent phải thực hiện tự kiểm 8 quy tắc hình học:

- [x] **RULE-G01**: Mép ngoài bê tông dùng đúng nét liền mảnh ($s/3 = 0.25mm$).
- [x] **RULE-G02**: Cốt thép chính dùng đúng nét liền đậm ($s = 0.7 \div 1.0mm$).
- [x] **RULE-G03**: Đường dóng kích thước vượt qua đường kích thước đúng $2 \div 3mm$.
- [x] **RULE-G04**: Con số kích thước nằm ở giữa và phía trên đường kích thước $1 \div 1.5mm$.
- [x] **RULE-G05**: Trục định vị dùng nét gạch chấm mảnh, đầu trục có vòng tròn $\varnothing 7 \div 8mm$.
- [x] **RULE-G06**: Vết mặt cắt dùng nét cắt $E$ độ dày $1.2s$ kèm mũi tên hướng nhìn.
- [x] **RULE-G07**: Mặt cắt ngang dầm tô đen tròn các điểm cắt cốt thép dọc.
- [x] **RULE-G08**: Bảng thống kê cốt thép đầy đủ đúng 8 cột và đặt ngay phía trên Khung tên.
