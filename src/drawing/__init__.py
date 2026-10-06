"""AutoCAD Tool — sinh bản vẽ, 100% qua AutoCAD COM Automation.

- geometry.py: hình học độc lập backend (IR — biểu diễn trung gian).
- layers.py: quy ước layer/nét (RULES_TCVN5574.md mục 10.7.2).
- backend_com.py: backend DUY NHẤT — vẽ qua AutoCAD COM (pywin32).
- verify_drawing.py: đọc lại bản vẽ (IR + trực tiếp qua COM) để đối chiếu,
  dùng bởi Verification Agent.

`ezdxf`/`backend_dxf.py` đã bị loại bỏ hoàn toàn khỏi repo — xem
`docs/CHANGE_REQUESTS.md` mục 2.
"""
