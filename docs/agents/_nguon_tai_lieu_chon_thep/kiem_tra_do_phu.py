#!/usr/bin/env python3
"""Kiểm tra ĐỘ PHỦ: mọi mục của tài liệu nguồn (NOI_DUNG_GOC.md) phải xuất hiện trong bộ skill.

Cách dùng (từ thư mục gốc repo):
  python docs/agents/_nguon_tai_lieu_chon_thep/kiem_tra_do_phu.py \
      --nguon docs/agents/_nguon_tai_lieu_chon_thep/NOI_DUNG_GOC.md \
      --skills docs/agents/huongdanchonthep docs/agents/huongdannhapdulieu docs/agents/huongdankiemchung \
      --ban-do docs/agents/BAN_DO_PHU_NGUON_SANG_SKILL.md

Thoát mã 1 nếu thiếu: luật R1–R52, hình (Hình x.y), mục nhỏ B1–B10/C1–C8, bước 1–16 (dầm) và 1–14 (cột),
mục 9.7.x, dòng Phụ lục B, hoặc mục bị bỏ khỏi bản đồ phủ. Các cảnh báo (số liệu, nhãn ⚠/[thực hành]) không làm
thoát mã 1 nhưng PHẢI được rà từng dòng và giải thích trong báo cáo cuối.
"""
import argparse, re, sys, pathlib, unicodedata

def norm(s):
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'[`*_$\\{}]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip(' .:;-–—')

def doc_all(paths):
    txt = []
    for p in paths:
        p = pathlib.Path(p)
        files = [p] if p.is_file() else sorted(p.rglob('*.md'))
        for f in files:
            txt.append(f.read_text(encoding='utf-8'))
    return '\n'.join(txt)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nguon', required=True)
    ap.add_argument('--skills', nargs='+', required=True)
    ap.add_argument('--ban-do', default=None)
    a = ap.parse_args()
    src = pathlib.Path(a.nguon).read_text(encoding='utf-8')
    sk = doc_all(a.skills)
    skn = norm(sk)
    bad = 0
    def rep(title, missing, hard=True):
        nonlocal bad
        print(f'\n## {title}: thiếu {len(missing)}')
        for m in missing[:200]:
            print('  -', m)
        if hard and missing:
            bad += 1

    # 1. Luật R1..R52 (R1–R13 ở mục 10.4 viết dạng '| 1 |')
    rules = sorted({f'R{n}' for n in re.findall(r'^\| (R\d+) \|', src, flags=re.M) for n in [n[1:]]}, key=lambda s: int(s[1:]))
    rules = sorted(set(rules) | {f'R{i}' for i in range(1, 14)}, key=lambda s: int(s[1:]))
    rep('Luật R1–R52', [r for r in rules if not re.search(rf'\b{r}\b', sk)])

    # 2. Hình
    figs = sorted(set(re.findall(r'!\[(Hình \d+\.\d+[a-e]?)\.', src)))
    rep('Hình', [f for f in figs if f.lower() not in skn])

    # 3. B1–B10, C1–C8 (mục 12.2, 12.3)
    bc = [f'B{i}' for i in range(1, 11)] + [f'C{i}' for i in range(1, 9)]
    rep('Mục B1–B10, C1–C8', [x for x in bc if not re.search(rf'\b{x}\b', sk)])

    # 4. Bước dầm (Chương 7) và cột (Chương 8): tiêu đề bước phải xuất hiện
    steps = []
    for m in re.finditer(r'^## (Bước \d+)\.\s*(.+)$', src, flags=re.M):
        steps.append((m.group(1), m.group(2)))
    rep('Tiêu đề Bước (dầm 1–16, cột 1–14)', [f'{b}. {t}' for b, t in steps if norm(t)[:40] not in skn])

    # 5. Tiêu đề mọi mục (## ### ####) — mức cảnh báo cứng cho 9.7.x, 12.x, 13.x, 14.x, 15.x
    heads = re.findall(r'^(#{2,4}) (.+)$', src, flags=re.M)
    hard_sets, soft = [], []
    for lv, t in heads:
        n = norm(re.sub(r'^\d+(\.\d+)*\.?\s*', '', t))
        if not n or n in skn: continue
        key = re.match(r'(\d+(\.\d+)*)\.?\s', t)
        if key and re.match(r'(9\.7|12\.|13\.|14\.|15\.)', key.group(1)): hard_sets.append(t)
        else: soft.append(t)
    rep('Tiêu đề 9.7.x/12–15 chưa thấy trong skill', hard_sets)
    rep('Tiêu đề mục khác chưa thấy (cần ghi vào bản đồ phủ là "đã gộp"/"bỏ" kèm lý do)', soft, hard=False)

    # 6. Phụ lục B: các dòng sai khác (| n | ... ) trong khoảng Phụ lục B
    mB = re.search(r'# PHỤ LỤC B(.*?)# PHỤ LỤC C', src, flags=re.S)
    if mB:
        rows = re.findall(r'^\| (\d+) \| ([^|]+)\|', mB.group(1), flags=re.M)
        rep('Phụ lục B (sai khác giữa tài liệu)', [f'{n}: {t.strip()[:60]}' for n, t in rows if norm(t)[:30] not in skn])

    # 7. Số liệu có đơn vị — cảnh báo mềm
    nums = set(re.findall(r'(?<![\w.])(\d+(?:[,.]\d+)?)\s?(?:mm|MPa|kN·m|kN|%|d\b|Ø)', src))
    miss = sorted(n for n in nums if n not in sk and n.replace(',', '.') not in sk and n.replace('.', ',') not in sk)
    rep('Số liệu (kèm đơn vị) trong nguồn nhưng không thấy trong skill — RÀ TỪNG DÒNG', miss, hard=False)

    # 8. Nhãn tin cậy
    for tag in ('⚠', '[thực hành]', '[ước lượng]', '[kinh nghiệm]', '[suy ra từ D]', '[hình học]'):
        print(f'\n## Nhãn {tag}: nguồn {src.count(tag)} — skill {sk.count(tag)}', '' if sk.count(tag) >= src.count(tag) * 0.8 else '  <-- THIẾU NHIỀU, nghi bỏ sót nhãn')

    # 9. Bản đồ phủ
    if a.ban_do:
        bd = pathlib.Path(a.ban_do)
        if not bd.exists():
            print('\n## Bản đồ phủ: KHÔNG TỒN TẠI', a.ban_do); bad += 1
        else:
            t = bd.read_text(encoding='utf-8'); tn = norm(t)
            allh = [h for _, h in heads] + [m[0] for m in re.findall(r'^# (CHƯƠNG \d+|PHỤ LỤC [A-E])', src, flags=re.M)]
            miss = [h for h in allh if norm(re.sub(r'^\d+(\.\d+)*\.?\s*', '', h))[:35] not in tn]
            rep('Mục nguồn chưa có dòng trong BẢN ĐỒ PHỦ', miss)
    print('\nKẾT QUẢ:', 'CÒN THIẾU — chưa đạt' if bad else 'ĐẠT các kiểm tra cứng')
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
