# -*- coding: utf-8 -*-
"""11/28 定例: 11/27 に広告費が出た全商品を1行ずつ。注文数が偶然の範囲かは、その商品の直近7日（11/21〜27）の「注文÷広告費」× 11/27 の広告費 を見込みにして、ポアソンで見る。
入力: an1128_out.json・orders_7d_1121_1127_raw.json・orders_by_product_1126_1127.txt・daily_ad.csv（w1127.py 経由）"""
import io, contextlib, json, re, os, math
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1127.py').read(), g)
A, ALLD = g['A'], g['ALLD']; D7 = ALLD[-7:]; D1 = ALLD[-1:]
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
IDN = {r[0]: nm(r[1]) for f in ('product_totals_1022_1120_raw.json', 'product_totals_0629_1120_raw.json') for r in json.load(open('scripts/daily/ic1121/aov/' + f))['rows'] if r[0]}
R7 = json.load(open(os.path.join(D0, 'orders_7d_1121_1127_raw.json')))['rows']; miss = [r for r in R7 if r[0] and r[0] not in IDN and int(r[3])]; assert not miss, ('名前の分からない商品ID', miss)
O7 = {IDN[r[0]]: int(r[1]) for r in R7 if r[0] in IDN}
O1 = {}
for l in open(os.path.join(D0, 'orders_by_product_1126_1127.txt')):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == '2026-11-27': O1[p[1]] = int(p[2])
OUT = json.load(open(os.path.join(D0, 'an1128_out.json')))
pois = lambda k, l: math.exp(-l + k * math.log(l) - math.lgamma(k + 1))
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
P('■ 11/27 に広告費が出た商品（広告費の多い順）: 注文・個数・広告費・倍率（11/27）・7日の倍率・11/27 の利益｜注文数の見込み（7日の 注文÷広告費 × 11/27 の広告費）と、その数以下／以上になる確率')
tot = 0
for o in sorted(OUT, key=lambda o: -o['a1']):
    if not o['a1']: continue
    n = o['n']; a1 = A(D1, n); a7 = A(D7, n); k = O1.get(n, 0); e = a1 * O7.get(n, 0) / a7 if a7 else 0
    lo = sum(pois(i, e) for i in range(k + 1)) if e else 1; hi = 1 - sum(pois(i, e) for i in range(k)) if e else 1; p = min(lo, hi)
    j = '偶然の範囲内' if p >= 0.16 else ('偶然でも起きるが端' if p >= 0.025 else '偶然では起きにくい')
    P(f"  {n}: 注文 {k}・{o['q1']}個・広告費 {a1:,.0f}・倍率 {o['m1']:.2f}・7日 {o['m7']:.2f}・利益 {o['p1']:+,.0f}｜見込み {e:.1f}件・{'以下' if lo <= hi else '以上'} {p:.0%} → {j}"); tot += o['p1']
P(f"  カタログ全部（テスト）: 広告費 {g['CAT'](D1):,.0f}（商品に分けられない）")
open(os.path.join(D0, 'prod_1128.txt'), 'w').write('\n'.join(L) + '\n')
