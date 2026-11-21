# -*- coding: utf-8 -*-
"""11/22 「商品名が在庫セールの場合の売れ筋はどう？」
今「【在庫セール⏰】」が付いている商品（label_products_raw.json・Shopify 直読 11/22 00時台）と、それ以外（【本日終了⏰】）を、直近7日（11/15〜21）で並べる。
売上・原価・広告費は scripts/daily/w1121.py の積み直し、注文数は orders_7d_1115_1121_raw.json（7日・商品別）と o1121/orders_by_product_1120_1121.txt（11/21）"""
import io, contextlib, json, re, os, collections
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(D0, '..', '..', '..'); os.chdir(ROOT)
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1121.py').read(), g)
WIN, agg, A, ALLD, MAP = g['WIN'], g['agg'], g['A'], g['ALLD'], g['MAP']
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
STOCK = {nm(p['title']): p['totalInventory'] for p in json.load(open(os.path.join(D0, 'label_products_raw.json')))['data']['products']['nodes']}
assert len(STOCK) == 8, STOCK
IDN = {r[0]: nm(r[1]) for f in ('product_totals_1022_1120_raw.json', 'product_totals_0629_1120_raw.json') for r in json.load(open('scripts/daily/ic1121/aov/' + f))['rows'] if r[0]}
O7 = {IDN[r[0]]: int(r[1]) for r in json.load(open(os.path.join(D0, 'orders_7d_1115_1121_raw.json')))['rows'] if r[0] in IDN}   # 7日の注文数（商品別・Shopify）
O1 = {}
for l in open('scripts/daily/o1121/orders_by_product_1120_1121.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == '2026-11-21': O1[p[1]] = int(p[2])
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
def block(days, lab, OR):
    key = 'lab' + lab; WIN[key] = days; N, DC, Q, K = agg(days, key)
    names = {n for n in set(N) | set(MAP) if A(days, n)}
    P(f'■ {lab}（広告費が出た商品）')
    for grp, test in (('在庫セール表記', lambda n: n in STOCK), ('本日終了表記', lambda n: n not in STOCK)):
        rows = [(n, OR.get(n, 0), Q.get(n, 0), N.get(n, 0), K.get(n, 0), A(days, n)) for n in names if test(n)]
        o, q, s, k, a = (sum(r[i] for r in rows) for i in range(1, 6))
        P(f'  {grp}: {len(rows)}商品・注文 {o}・{q}個・実売 {s:,}・広告費 {a:,.0f}・倍率 {(s-k)/a:.2f}・利益 {s-k-a:+,.0f}')
        for n, o_, q_, s_, k_, a_ in sorted(rows, key=lambda r: -r[5]):
            P(f'     {n}: 注文 {o_}・{q_}個・広告費 {a_:,.0f}・倍率 {(s_-k_)/a_:.2f}・利益 {s_-k_-a_:+,.0f}')
block(ALLD[-7:], '直近7日（11/15〜21）', O7); P(''); block(ALLD[-1:], '11/21 の1日', O1)
P(''); P('■ 今「在庫セール」が付いている商品と Shopify の在庫数（11/22 00時台）: ' + '・'.join(f'{n} {v:,}' for n, v in STOCK.items()))
open(os.path.join(D0, 'label_1122.txt'), 'w').write('\n'.join(L) + '\n')
