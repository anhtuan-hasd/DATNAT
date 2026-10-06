"""Smoke test thủ công cho OpenAIChatProvider — gọi OpenAI thật với 1 tool
đơn giản (cộng 2 số) để xác nhận lớp chuyển đổi định dạng hoạt động đúng với
API thật, không chỉ với client giả lập. Chi phí cực nhỏ (model gpt-5.6-luna,
vài chục token). Chạy: python scripts/smoke_test_openai.py — tự nạp
OPENAI_API_KEY từ file `.env` ở gốc dự án nếu có (như webapp/app.py); nếu
chưa có `.env`, đặt trực tiếp: $env:OPENAI_API_KEY = "sk-...".
"""
import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).parent.parent
sys.path.insert(0, str(THU_MUC_GOC))

from dotenv import load_dotenv

load_dotenv(THU_MUC_GOC / ".env")

from src.orchestrator import agent

print("1. Khởi tạo OpenAIChatProvider (gpt-5.6-luna)...", flush=True)
provider = agent.OpenAIChatProvider()
print("   OK", flush=True)

tools = [
    {
        "name": "cong_2_so",
        "description": "Cộng 2 số nguyên và trả về tổng.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    }
]
dispatch = {"cong_2_so": lambda dau_vao: {"tong": dau_vao["a"] + dau_vao["b"]}}

print("2. Chạy vòng lặp tool-calling thật: '17 cộng 25 bằng bao nhiêu?'...", flush=True)
ket_qua = agent.chay_vong_lap_tool(
    nha_cung_cap=provider,
    he_thong="Bạn phải dùng tool cong_2_so để cộng, không tự tính nhẩm.",
    tin_nhan_dau="17 cộng 25 bằng bao nhiêu?",
    tools=tools,
    dispatch=dispatch,
    so_lan_goi_toi_da=5,
)

print(f"   Dừng vì: {ket_qua.dung_vi}, số lần gọi model: {ket_qua.so_lan_goi_model}", flush=True)
print(f"   Nhật ký tool đã gọi: {ket_qua.nhat_ky_tool}", flush=True)
van_ban_cuoi = [b["text"] for b in ket_qua.messages[-1]["content"] if isinstance(b, dict) and b.get("type") == "text"]
print(f"   Câu trả lời cuối: {van_ban_cuoi}", flush=True)

if ket_qua.nhat_ky_tool and ket_qua.nhat_ky_tool[0]["ket_qua"].get("tong") == 42:
    print("HOÀN TẤT — model đã gọi đúng tool và nhận đúng kết quả (42).", flush=True)
else:
    print("CẢNH BÁO — model không gọi tool như kỳ vọng, xem nhật ký ở trên.", flush=True)
