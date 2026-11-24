# -*- coding: utf-8 -*-
"""Shopify・Meta の問い合わせ結果を、会話の記録（jsonl）からそのまま取り出して保存する（手で写さない）。
使い方: python3 extract.py <結果の先頭 600 文字に含まれる文字列> <保存先> [結果の先頭の文字列]"""
import json, sys, glob, os
key, out = sys.argv[1], sys.argv[2]; pre = sys.argv[3] if len(sys.argv) > 3 else '{"query"'
src = sorted(glob.glob('/root/.claude/projects/-home-user-LOOana/*.jsonl'), key=os.path.getmtime)[-1]
found = None
def walk(o):
    global found
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, str) and o.startswith(pre) and key in o[:600]:
        try: found = json.loads(o)
        except Exception: pass
for line in open(src, encoding='utf-8', errors='replace'):
    if key not in line: continue
    try: walk(json.loads(line))
    except Exception: pass
assert found, 'not found: ' + key
json.dump(found, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print(out, 'ok', len(json.dumps(found)))
