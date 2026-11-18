# -*- coding: utf-8 -*-
"""11/19 定例: ワイパーの日別（個数・広告費・倍率）と広告別（取り分・クリック率・Meta 購入）。7日の利益の差で一番大きく減った商品。
入力: data/daily（売上・広告費）・o1118/ad_level_1026_1118.txt（広告別 cost,imp,link_clicks）"""
import csv, collections
P, C = 3980, None
for l in open('scripts/daily/w1118.py'):
    if "'ワイド水切りワイパー':" in l and l.startswith('COST'): pass
src = open('scripts/daily/w1118.py').read(); ns = {}
exec(src[src.index('COST='):src.index('MAP=')], ns); C = ns['COST']['ワイド水切りワイパー']; assert ns['PRICE']['ワイド水切りワイパー'] == P
S = collections.defaultdict(lambda: [0, 0]); AD = collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    if r['name'] == 'ワイド水切りワイパー': S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    if r['campaign'] == 'ワイド水切りワイパー': AD[r['date']] += float(r['cost'])
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open('scripts/daily/o1118/ad_level_1026_1118.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(',')
    if c == 'ワイド水切りワイパー': x = R[d][ad]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
print(f'ワイパー（売価 {P}・原価 {C}）日別: 個数・広告費・倍率 ／ 広告別 取り分・クリック率')
for d in sorted(set(AD) | set(S)):
    if d < '2026-11-01': continue
    g, dc = S[d]; q = g // P; a = AD[d]; m = (g - dc - q * C) / a if a else None
    ads = R[d]; tot = sum(v[0] for v in ads.values()) or 1
    s = '・'.join(f"{k} {v[0]/tot:.0%} {v[2]/v[1]*100 if v[1] else 0:.2f}%" for k, v in sorted(ads.items()) if v[0])
    print(f"  {d}: {q}個・広告 {a:,.0f}・倍率 {'—' if m is None else f'{m:.2f}'} ／ {s}")
for lab, a_, b_ in (('11/5〜11', '2026-11-05', '2026-11-11'), ('11/12〜18', '2026-11-12', '2026-11-18')):
    ds = [d for d in AD if a_ <= d <= b_]; g = sum(S[d][0] for d in ds); dc = sum(S[d][1] for d in ds); q = g // P; a = sum(AD[d] for d in ds)
    imp = sum(v[1] for d in ds for v in R[d].values()); clk = sum(v[2] for d in ds for v in R[d].values())
    print(f'{lab}: {q}個・広告 {a:,.0f}・倍率 {(g-dc-q*C)/a:.2f}・CPM {a/imp*1000:,.0f}・クリック率 {clk/imp:.2%}・1クリックあたり {a/clk:.0f}円・個数÷クリック {q/clk:.2%}')
