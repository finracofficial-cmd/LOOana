# -*- coding: utf-8 -*-
"""11/18 「CPM 安い商品ってなんだ」: ①4/1〜11/17 の商品ごとの CPM（life/reach_life_raw.txt）と、商品の性質（data/product-lifetime-2026-10-17.csv）
②10/19〜11/17 の 年齢×性別の構成（cpm/agegender_raw.txt）と CPM の関係"""
import csv, collections, math
num = lambda x: 0 if x == 'null' else float(x)
LT = {r['商品']: r for r in csv.DictReader(open('../../../data/product-lifetime-2026-10-17.csv'))}
def lt(n):
    return LT.get(n) or next((r for k, r in LT.items() if n[:6] in k or k[:6] in n), None)
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r
def rho(a, b):
    ra, rb = rank(a), rank(b); n = len(a); ma, mb = sum(ra) / n, sum(rb) / n
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
rows = []
for l in open('life/reach_life_raw.txt'):
    if l[0] == '#': continue
    c, cost, imp, reach, fq, clk, pur = l.strip().split(',')
    cost, imp = float(cost), float(imp)
    if cost < 100000 or c.startswith('カタログ'): continue
    r = lt(c)
    rows.append(dict(c=c, cpm=cost / imp * 1000, ctr=num(clk) / imp * 100, cat=r['カテゴリ'] if r else '?', season=r['季節'] if r else '?', price=float(r['売価']) if r else None, demo=r['実演性(2高/1中/0低)'] if r else '', alt=r['安価な代替(1あり)'] if r else ''))
rows.sort(key=lambda x: x['cpm'])
print('■ 4/1〜11/17 の CPM（広告費10万円以上・安い順）')
for x in rows: print(f"  {x['c'][:18]:<18} CPM {x['cpm']:>5,.0f}・クリック率 {x['ctr']:.2f}%・{x['cat']}・{x['season']}・{x['price'] or '?'}円")
s = [x for x in rows if x['price']]
print(f"  CPM と売価の順位相関 {rho([x['cpm'] for x in s], [x['price'] for x in s]):+.2f}（{len(s)}商品）・CPM とクリック率 {rho([x['cpm'] for x in rows], [x['ctr'] for x in rows]):+.2f}")
G = collections.defaultdict(list)
for x in rows: G[x['cat']].append(x['cpm'])
print('  カテゴリ別の CPM（中央値）: ' + '・'.join(f'{k} {sorted(v)[len(v)//2]:,.0f}（{len(v)}）' for k, v in sorted(G.items(), key=lambda kv: sorted(kv[1])[len(kv[1])//2])))
# ② 年齢×性別
A = collections.defaultdict(lambda: collections.defaultdict(float))
for l in open('cpm/agegender_raw.txt'):
    if l[0] == '#': continue
    c, a, g, cost, imp, clk, pur = l.strip().split(',')
    if c.startswith('カタログ'): continue
    d = A[c]; d['cost'] += num(cost); d['imp'] += num(imp)
    if a in ('18-24', '25-34'): d['young'] += num(imp)
    if a in ('55-64', '65+'): d['old'] += num(imp)
    if g == 'female': d['f'] += num(imp)
R = [(c, d['cost'] / d['imp'] * 1000, d['young'] / d['imp'], d['old'] / d['imp'], d['f'] / d['imp']) for c, d in A.items() if d['cost'] >= 50000]
R.sort(key=lambda x: x[1])
print('■ 10/19〜11/17・広告費5万円以上: CPM ／ 表示のうち 35歳未満 ／ 55歳以上 ／ 女性')
for c, cpm, y, o, f in R: print(f'  {c[:18]:<18} {cpm:>5,.0f} ／ {y:.0%} ／ {o:.0%} ／ {f:.0%}')
print(f'  CPM との順位相関（{len(R)}商品）: 35歳未満の割合 {rho([r[1] for r in R], [r[2] for r in R]):+.2f}・55歳以上 {rho([r[1] for r in R], [r[3] for r in R]):+.2f}・女性 {rho([r[1] for r in R], [r[4] for r in R]):+.2f}')
