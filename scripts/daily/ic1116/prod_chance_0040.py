# -*- coding: utf-8 -*-
"""商品別 11/15 の注文数は偶然の範囲か。期待＝（11/8〜14 の注文 ÷ 11/8〜14 の広告費）× 11/15 の広告費。ポアソンで 片側の確率。
注文: o1115/orders_by_product_1115.txt（Shopify 実測）・広告費: data/daily/daily_ad.csv（w1115.py の A 関数＝商品⇄キャンペーンの対応）"""
import io, contextlib, math
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1115.py').read(), g)
A, ALLD = g['A'], g['ALLD']
P7 = [d for d in ALLD if '2026-11-08' <= d <= '2026-11-14']
def pois_cdf(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
print('商品: 11/15 注文（個数）／ 期待注文 ／ 判定（片側の確率）')
for l in open('scripts/daily/o1115/orders_by_product_1115.txt'):
    if l[0] == '#': continue
    n, o, q, o7 = l.strip().split(','); o, q, o7 = int(o), int(q), int(o7)
    a1, a7 = A(['2026-11-15'], n), A(P7, n)
    if a7 < 20000 or o7 < 5: print(f'  {n}: {o}（{q}個）／ 比べる過去なし（11/8〜14 広告費 {a7:,.0f}・注文 {o7}）'); continue
    lam = o7 / a7 * a1
    p = 1 - pois_cdf(o - 1, lam) if o >= lam else pois_cdf(o, lam)
    v = '偶然の範囲内' if p > 0.16 else ('偶然でも起きるが端' if p > 0.025 else '偶然では起きにくい')
    print(f'  {n}: {o}（{q}個）／ 期待 {lam:.1f}（広告費 {a1:,.0f}）／ {"多い" if o >= lam else "少ない"}側 {p:.0%} → {v}')
