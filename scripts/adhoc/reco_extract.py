# -*- coding: utf-8 -*-
"""looty-japan.com の公開エンドポイント /recommendations/products.json から
各商品ページに実際に出ている「関連商品」を取得し、1本のCSVに落とす。
Shopifyのアルゴリズム推薦（intent=related）なので、テーマ側に手動リストは無い。
"""
import json, csv, os
from collections import Counter
rows = []
for line in open('/tmp/plist.tsv', encoding='utf-8'):
    pid, sfx, name = line.rstrip('\n').split('\t')
    d = json.load(open(f'data/raw/reco/{pid}.json', encoding='utf-8'))
    for i, p in enumerate(d['products'], 1):
        rows.append(dict(src_id=pid, src=name, rank=i, rec_id=p['id'], rec_title=p['title'],
                         rec_price=int(float(p['variants'][0]['price'])) if p.get('variants') else None))
os.makedirs('data/raw', exist_ok=True)
with open('data/raw/recommendations_20260814.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['src_id', 'src', 'rank', 'rec_id', 'rec_title', 'rec_price'])
    w.writeheader(); w.writerows(rows)
print('抽出', len(rows), '行 /', len({r['src_id'] for r in rows}), '商品')
print('1商品あたりの推薦件数:', dict(Counter(
    len([x for x in rows if x['src_id'] == s]) for s in {r['src_id'] for r in rows})))
