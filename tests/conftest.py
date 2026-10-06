"""
Fixture dùng chung cho test suite.

`tmp_path` mặc định của pytest quét thư mục Windows Temp gốc
(C:\\Users\\...\\AppData\\Local\\Temp\\pytest-of-<user>) để đánh số thư mục —
trên máy này thư mục đó bị chặn quyền (PermissionError), không liên quan đến
code đang test. Dùng 1 thư mục tạm CỤC BỘ trong chính project thay thế, luôn
ghi được vì mọi tool khác trong phiên làm việc đã ghi vào đây bình thường.
"""

import shutil
import uuid
from pathlib import Path

import pytest

_THU_MUC_TAM_GOC = Path(__file__).parent / "_tmp_test_output"


@pytest.fixture
def thu_muc_tam() -> Path:
    d = _THU_MUC_TAM_GOC / uuid.uuid4().hex
    d.mkdir(parents=True, exist_ok=True)
    yield d
    shutil.rmtree(d, ignore_errors=True)
