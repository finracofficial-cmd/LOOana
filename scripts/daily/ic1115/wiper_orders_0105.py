# -*- coding: utf-8 -*-
"""ワイパーの広告費あたり注文が本当に落ちているか（2026-11-15 01:0x ユーザー「ワイパーはさげたほうがいいかな？」）
注文: Shopify FROM sales SHOW orders WHERE product_title CONTAINS 'ワイド水切りワイパー' TIMESERIES day（01:0x 取得・下に貼る）
広告費: data/daily/daily_ad.csv。偶然のぶれは注文数から（√(1/前+1/今)）、日ごとのぶれが偶然より大きい分（φ=1.32）も併記"""
import csv, math, collections
R = __file__.rsplit('/scripts/', 1)[0] + '/'
OR = {'2026-11-04': 2, '2026-11-05': 8, '2026-11-06': 15, '2026-11-07': 16, '2026-11-08': 19, '2026-11-09': 23, '2026-11-10': 15, '2026-11-11': 14, '2026-11-12': 13, '2026-11-13': 8, '2026-11-14': 9}
GR = {'2026-11-04': 7960, '2026-11-05': 43780, '2026-11-06': 63680, '2026-11-07': 75620, '2026-11-08': 87560, '2026-11-09': 115420, '2026-11-10': 59700, '2026-11-11': 67660, '2026-11-12': 55720, '2026-11-13': 35820, '2026-11-14': 35820}
AD = collections.defaultdict(float); G = collections.defaultdict(int)
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if r['campaign'] == 'ワイド水切りワイパー': AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == 'ワイド水切りワイパー': G[r['date']] += int(r['gross'])
for d in OR: assert G[d] == GR[d], (d, G[d], GR[d])   # Shopify の取り直しと data/daily の売上が一致
P = {'11/6〜9（ピーク）': ['2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09'], '11/10〜12': ['2026-11-10', '2026-11-11', '2026-11-12'], '11/13〜14': ['2026-11-13', '2026-11-14']}
V = {}
for k, ds in P.items():
    o = sum(OR[d] for d in ds); a = sum(AD[d] for d in ds); V[k] = (o, a)
    print(f'{k}: 注文 {o}・広告費 {a:,.0f} → 1万円あたり {o/a*10000:.2f}件')
for a_, b_ in (('11/6〜9（ピーク）', '11/13〜14'), ('11/10〜12', '11/13〜14')):
    (o1, x1), (o2, x2) = V[a_], V[b_]
    r = (o2 / x2) / (o1 / x1); s = math.sqrt(1 / o1 + 1 / o2); z = math.log(r) / s
    v = lambda z: '偶然の範囲内' if abs(z) <= 1 else ('端' if abs(z) <= 2 else '偶然では起きにくい')
    print(f'  {a_} → {b_}: {(r-1)*100:+.0f}%・z {z:+.2f}（{v(z)}）／ φ=1.32 込み z {z/math.sqrt(1.32):+.2f}（{v(z/math.sqrt(1.32))}）')
