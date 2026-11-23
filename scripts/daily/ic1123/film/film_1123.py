# -*- coding: utf-8 -*-
"""11/23 16時台「レインガードを V2 で復活させてみた」: 前回（11/5〜11/12）の数字を、最初の4日と最後の3日に分けて並べる（V2 の比べる基準）。
入力: data/daily/daily_sales.csv・daily_ad.csv・o1122/ad_level_1026_1122.txt。原価は 798円（Shopify unitCost・film_product_1123_raw.json）"""
import csv, os, json, collections
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D0 + '../../../../'
pr = json.load(open(D0 + 'film_product_1123_raw.json'))['data']['products']['nodes'][0]; v = pr['variants']['nodes'][0]
COST = int(float(v['inventoryItem']['unitCost']['amount'])); PRICE = int(v['price']); assert (COST, PRICE) == (798, 3980) and pr['status'] == 'ACTIVE' and v['availableForSale']
S = collections.defaultdict(lambda: [0, 0]); M = collections.defaultdict(lambda: [0, 0, 0])
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == 'クリアビューレインガードフィルム': S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
for l in open(R + 'scripts/daily/o1122/ad_level_1026_1122.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(',')
    if 'レインガード' in c: x = M[d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P(f"■ 商品（Shopify 直読 11/23 16時台）: {pr['title']}｜{pr['status']}・{PRICE:,}円・原価 {COST}円・在庫 {v['inventoryQuantity']:,}・購入可")
P('■ 前回（キャンペーン「クリアビューレインガードフィルム」11/5 22時台〜11/12）: 日ごと 広告費・個数・倍率｜CPM・クリック率・クリック1回')
for d in sorted(M):
    g, dc = S.get(d, [0, 0]); q = g // PRICE; c = M[d]
    P(f'  {d[5:]}: {c[0]:,}・{q}個・{(g-dc-q*COST)/c[0]:.2f}｜{c[0]/c[1]*1000:,.0f}・{c[2]/c[1]:.2%}・{c[0]/c[2]:.0f}円')
for lab, ds in (('最初の4日（11/6〜9）', ['2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09']), ('最後の3日（11/10〜12）', ['2026-11-10', '2026-11-11', '2026-11-12']), ('全部（11/5〜12）', sorted(M))):
    c = [sum(M[d][i] for d in ds) for i in range(3)]; g = sum(S.get(d, [0, 0])[0] for d in ds); dc = sum(S.get(d, [0, 0])[1] for d in ds); q = g // PRICE
    P(f'  {lab}: 広告費 {c[0]:,}（{c[0]/len(ds):,.0f}/日）・{q}個・倍率 {(g-dc-q*COST)/c[0]:.2f}・利益 {g-dc-q*COST-c[0]:+,}｜CPM {c[0]/c[1]*1000:,.0f}・クリック率 {c[2]/c[1]:.2%}・クリック1回 {c[0]/c[2]:.0f}円・個数÷クリック {q/c[2]:.1%}')
P(f'■ 事故停止の線: 購入0のまま {(PRICE-COST)*3:,}円／倍率 1.25 に届く クリック1回の上限は「1注文の粗利 × 注文÷クリック ÷ 1.25」')
open(D0 + 'film_1123.txt', 'w').write('\n'.join(out) + '\n')
