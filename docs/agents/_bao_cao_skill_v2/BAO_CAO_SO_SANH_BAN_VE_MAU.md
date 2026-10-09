# So sánh bản vẽ chạy mẫu với bản vẽ chuẩn `data/samples/BoTriThep_KhungTruc5_mau.pdf`

Chạy mẫu: dữ liệu ETABS thật → tool Rule Engine thật → tool Drawing/Verification thật trên AutoCAD 2024, **không dùng LLM** (script ở scratchpad, không nằm trong repo). Kết quả: 20/20 phần tử đạt Rule Engine, kiểm chứng tổng thể ĐẠT, 36/36 mặt cắt ĐẠT; chạy lại cho PDF giống hệt (cùng 2113 ký tự chữ, 7618 nét). Bố cục và lỗi giống hệt lần chạy bằng LLM ngày 7/10 (`output/khung_truc5_day_du/preview_cuoi.png`) ⇒ **nguyên nhân không nằm ở LLM hay skill**.

Verification báo ĐẠT vì nó chỉ đếm (số đa giác, vòng tròn số hiệu, trục, tiêu đề bảng 8 cột, layer hợp lệ), không so hình học/bố cục (xem KC-11…KC-24 trong skill kiểm chứng).

## Bản chuẩn có gì (đọc từ PDF)
- Dầm: **mặt trên dầm bằng cốt sàn** (cả dầm 220×500 và 220×300), dầm treo xuống; có bản sàn dày 100 (cánh T) ở mặt cắt.
- Đai theo vùng, ghi theo đoạn: `1300(Ø6a150)`, `2620(Ø6a200)`, `5200(Ø6a200)`, `1200(Ø6a200)`; cột đai a150 vùng chân/nút, a250 giữa cột (nhãn 6/6A/7/7A).
- Thép dọc dầm có điểm cắt (nhãn 13/14, 12, 10, 1300–2620–1300), thép trên liền qua nút và **uốn móc xuống cột**; đai cột chạy qua nút (nét đứt).
- Chân cột: móng (đài) có lưới thép đáy, thép cột chờ **bẻ chữ L** trong móng, bê tông lót; **COS tôn nền / COS tự nhiên / COS đỉnh móng** và chuỗi kích thước 450/550/1000, 2700/3200, 500/400/200/300.
- Hệ chú thích: vòng tròn số hiệu + số lượng Ø hoặc Ø/bước, đường dẫn, ghi lặp ở nhiều chỗ nhưng cùng số hiệu; ký hiệu **mặt cắt (vạch đậm + số)** trên mặt đứng nối với hình mặt cắt `n-n`; khung nét đứt "CHI TIẾT 1–4" nối với hình 3D nút.
- Cả tờ: mặt bằng kết cấu sàn, mặt đứng, 4 chi tiết 3D nút, 15 mặt cắt (T, có cánh sàn, kích thước 28/164/28, cốt sàn, trục), ghi chú vật liệu, bảng thống kê có hình dáng thanh, bảng K, khung tên.

## Bản chạy mẫu thiếu/sai gì và nguyên nhân (đã đối chiếu mã)
| # | Hiện tượng | Nguyên nhân trong mã/dữ liệu |
|:-:|:--|:--|
| 1 | Dầm to/nhỏ **đối xứng qua đường cao độ**, mặt trên không phẳng | `src/drawing/geometry.py:921` `y0, y1 = dam.y_truc - dam.h/2, dam.y_truc + dam.h/2`; `DoanDamVe` chỉ có `y_truc` + `h`, không có khái niệm "mặt trên = cốt sàn". Khối 3D nút (`geometry.py:1170`) cũng đặt dầm tâm y=0 |
| 2 | Đai dầm/cột đặt đều 450 mm "minh hoạ", không có vùng a150/a200/a250 | `geometry.py` `BUOC_DAI_MINH_HOA = 450`; kết quả `tinh_cot_dai` có trong `KetQuaViTriDaThietKe.cot_dai` nhưng `pipeline._du_lieu_lap_rap` **không chuyển** sang bước lắp ráp (chính mã đã ghi chú "chưa truyền tới… Phase B") |
| 3 | Thép dầm chỉ là 1 đường trên + 1 đường dưới suốt nhịp; không điểm cắt, không móc vào cột, không liền qua nút | Không có dữ liệu: chưa có tool bố trí theo chiều dài (GAP G4) và chi tiết nút (GAP G3); `nut_khung.py` có 13 loại nút nhưng không tool nào gọi. Skill (module 05/06) mô tả đủ nhưng **không có hàm nào tiêu thụ** |
| 4 | Không có móng, thép chờ chữ L, COS tôn nền/tự nhiên/đỉnh móng | `khung_ve.lap_rap_mat_dung_khung` có tham số `moc_tham_chieu`, `ten_mat_dat` nhưng `drawing_agent.lap_rap_mat_dung_khung` **không truyền**; dữ liệu ETABS không có móng (chỉ có mốc "Mong" = 0) và hợp đồng dữ liệu không có trường móng/COS |
| 5 | Không có mặt bằng kết cấu, chi tiết 3D nút | `ve_mat_bang_ket_cau`, `ThongSoChiTietNutKhung` (3D) tồn tại trong `geometry.py` nhưng **không có tool nào trong `drawing_agent`** (chỉ 3 tool: `ve_mat_cat`, `lap_rap_mat_dung_khung`, `xuat_ban_ve`) ⇒ agent không gọi được |
| 6 | Mặt cắt dầm là hình chữ nhật trần, nhãn "32/goi_trai", không có cánh sàn, cốt sàn, trục, kích thước 28/164/28, nhãn `1-1` | `ve_mat_cat_dam` chỉ vẽ chữ nhật + thép + đai + kích thước ngoài; nhãn do pipeline đặt `p.ten/vi_tri` |
| 7 | Không có ký hiệu mặt cắt trên mặt đứng, không có khung "CHI TIẾT" | Không có hàm tạo; không có liên kết dữ liệu giữa mặt đứng và mặt cắt |
| 8 | Cao độ vẽ đều nhau, không đúng tỷ lệ (tầng 1 = 4200 vẽ bằng tầng 3200) | `khung_ve._toa_do_deu_giu_thu_tu` (vẽ sơ đồ, chỉ nhãn số là thật) |
| 9 | Bảng thống kê là khối đen; khung tên không đọc được; 36 mặt cắt xếp 1 hàng rất dài, cả tờ thu rất nhỏ | PDF xuất fit-to-extents toàn ModelSpace (một tờ, không viewport/tỷ lệ); nét bảng quá dày so với chiều cao dòng; chưa có tờ/khổ giấy |
| 10 | Thiếu ghi chú vật liệu, bảng K, hình dáng thanh trong bảng | Chưa có hàm; `ve_bang_thong_ke` chỉ 8 cột chữ |

## Vì sao "đã cung cấp đủ tài liệu" mà bản vẽ không đổi
Skill chỉ vào **system prompt của LLM**; hình học do mã tất định quyết định và LLM chỉ chép JSON vào tool. Muốn bản vẽ thể hiện nút, điểm cắt, đai theo vùng, móng, COS thì cần (a) dữ liệu trong hợp đồng giữa agent, (b) tool/hàm hình học tương ứng. Hiện cả hai chưa có; skill mới làm xong phần "biết cần gì", chưa có phần "nạp vào bản vẽ".

## Đề xuất sửa (chưa làm — vùng `src/drawing/**`, `drawing_agent.py`, skill Vẽ đang bị khoá)
1. Dầm: đặt mặt trên = cốt sàn (`y1 = y_truc`, `y0 = y_truc - h`); thêm bản sàn/cánh T vào mặt cắt. (nhỏ, ưu tiên 1)
2. Chuyển `cot_dai` (bước/vùng đai) vào dữ liệu lắp ráp; vẽ đai theo vùng và ghi `L(Ø/bước)`.
3. Truyền `moc_tham_chieu`/`ten_mat_dat`; thêm móng (đài, lót, thép chờ L) với dữ liệu móng do người dùng/Input Adapter cung cấp (hỏi nếu thiếu).
4. Thêm tool vẽ mặt bằng, chi tiết nút 3D; ký hiệu mặt cắt + khung CHI TIẾT.
5. Thêm tool bố trí theo chiều dài/điểm cắt và chi tiết nút (GAP G3, G4) để có dữ liệu cho (2)–(4).
6. Bố cục tờ vẽ: khổ giấy, tỷ lệ, lưới mặt cắt, nét bảng, khung tên.
7. Verification: thêm kiểm tra hình học (cốt đỉnh dầm bằng nhau, có COS, có đai theo vùng…) — hiện KC-08/KC-09 để trống cho việc này.

## Trạng thái sau khi sửa (cùng ngày, nhánh `feat/ban-ve-theo-mau-khung-truc5`)

| # | Hiện tượng | Trạng thái |
|:-:|:--|:--|
| 1 | Dầm đối xứng qua cốt sàn | **Đã sửa**: mặt trên = cốt sàn, dầm treo xuống (test `test_mat_tren_moi_dam_bang_cot_san_dam_treo_xuong`) |
| 2 | Đai minh hoạ 450 | **Đã sửa**: đai theo vùng, ghi `1300(Ø6a150)` |
| 3 | Thép dầm 1 đường, không móc/điểm cắt | **Một phần**: suốt + gia cường L/4 + móc biên; chưa có hình bao vật liệu |
| 4 | Không móng/COS | **Đã vẽ** (móng minh hoạ + COS; giả định ghi trên tờ) |
| 5 | Không chi tiết 3D, ký hiệu mặt cắt, khung CHI TIẾT | **Đã vẽ** (4 chi tiết trục đo, vạch + số, khung nét đứt) |
| 5b | Không mặt bằng kết cấu | **Chưa** — thiếu dữ liệu toàn nhà |
| 6 | Mặt cắt chữ nhật trần | **Đã sửa**: chữ T, cốt sàn, kích thước, trục, `n-n` |
| 7 | Cao độ vẽ đều nhau | **Đã sửa**: vẽ theo toạ độ thật |
| 8 | Bảng đen, khung tên không đọc được, tờ nhỏ xíu | **Đã sửa**: tờ A1/A0 có khung, bảng đọc được, PDF đen trắng |
| 9 | Ghi chú vật liệu, bảng K | Ghi chú vật liệu **đã có** (tra từ `vat_lieu`); bảng K **chưa** |

