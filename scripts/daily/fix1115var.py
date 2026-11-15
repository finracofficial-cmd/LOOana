# -*- coding: utf-8 -*-
"""11/15 のバリアント行の追記漏れを補う（append1115.py はナノだけ書いていた）。
出典: scripts/daily/o1115/var_1115_raw.json の『高見えレザーヘッドレストフック / ブラック 11940円 3個』。冪等（既にあれば何もしない）。"""
import csv, json
P='data/daily/daily_variant.csv'
raw=json.load(open('scripts/daily/o1115/var_1115_raw.json',encoding='utf-8'))
g=[int(r[2]) for r in raw['rows'] if 'ヘッドレストフック' in r[0] and r[1]=='ブラック']
assert g==[11940], g
rows=list(csv.DictReader(open(P,encoding='utf-8')))
if any(r['date']=='2026-11-15' and r['name']=='高見えレザーヘッドレストフック' for r in rows):
    print('already present')
else:
    with open(P,'a',newline='',encoding='utf-8') as f: csv.writer(f).writerow(['2026-11-15','高見えレザーヘッドレストフック','黒',11940])
    print('appended hook 黒 11940')
