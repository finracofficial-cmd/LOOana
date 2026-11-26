# -*- coding: utf-8 -*-
"""下調べの係の報告（会話の記録に入っている本文）を、そのままテキストで保存する（手で写さない）。
使い方: python3 save_report.py <係のID> <保存先>"""
import json, sys, glob, os, re
aid, out = sys.argv[1], sys.argv[2]
src = sorted(glob.glob('/root/.claude/projects/-home-user-LOOana/*.jsonl'), key=os.path.getmtime)[-1]
tag = f'<agent-message from="{aid}">'; found = None
def walk(o):
    global found
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, str) and tag in o and '</agent-message>' in o:
        found = o[o.index(tag) + len(tag):o.index('</agent-message>')]
for line in open(src, encoding='utf-8', errors='replace'):
    if aid not in line: continue
    try: walk(json.loads(line))
    except Exception: pass
assert found, 'not found: ' + aid
body = found.split('The report follows:', 1)[-1]
body = '\n'.join(l[2:] if l.startswith('  ') else l for l in body.strip('\n').split('\n'))
open(out, 'w', encoding='utf-8').write(body + '\n'); print(out, len(body), '字', body.count('\n') + 1, '行')
