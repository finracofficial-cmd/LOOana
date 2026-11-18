# -*- coding: utf-8 -*-
"""11/18 「レインガード復活どう？それかほかの商品」: 止めた商品の出し直し候補を、過去の配信の中身で並べる
data/daily/daily_sales.csv（gross−値引）・daily_ad.csv・scripts/product_tabs.py の COST/PRICE（1商品1単価＝バリエーションで原価が違う商品は近似）
倍率＝（売上−原価）÷広告費。配信が続いた区間（広告費>0 の連続日）ごとに、通算・最初の3日・最後の3日・7日の最高を出す"""
import csv, collections, datetime
src = open('../../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); COST, PRICE = ns['COST'], ns['PRICE']
key = lambda n: next((k for k in COST if k == n), None) or next((k for k in COST if k in n or n in k), None)
CAND = ['クリアビューレインガードフィルム', 'コードレスダブルミスト加湿器', 'ポータブルヒートシーラー', '姿勢サポートチェア', '2WAYシートボックス', 'すき間収納シートポケット', 'コードレス毛玉クリーナー',
        'ナノバブルシャワーヘッド', 'バランスケアスリッパ', 'ムダ毛シェーバー', '壁掛けディスペンサー', 'UV歯ブラシ除菌器', '高見えレザーヘッドレストフック', '防風あったか裏起毛パンツ', 'ファスナー修理キット', 'シリコンホールド膝サポーター', '伸縮ワックス洗車ブラシ', '3WAY着る電気ブランケット', '高見えレザードアポケット']
CMAP = {'ディスペンサー': '壁掛けディスペンサー'}
def prod_of(c):
    c = CMAP.get(c, c)
    return next((p for p in CAND if c.startswith(p) or p.startswith(c.rstrip('v0123456789 '))), None)
S = collections.defaultdict(float); G = collections.defaultdict(float); A = collections.defaultdict(float)
PRICE_FIX = {'姿勢サポートチェア': 5980, 'ムダ毛シェーバー': 6980}  # PRICE が None の商品は 11/18 graphql の直読の売価
for r in csv.DictReader(open('../../../../data/daily/daily_sales.csv')):
    if r['date'] >= '2026-09-01' and r['name'] in CAND: S[(r['name'], r['date'])] += float(r['gross']) - abs(float(r['disc'])); G[(r['name'], r['date'])] += float(r['gross'])
for r in csv.DictReader(open('../../../../data/daily/daily_ad.csv')):
    p = prod_of(r['campaign'])
    if r['date'] >= '2026-09-01' and p: A[(p, r['date'])] += float(r['cost'])
def gp(p, d):
    k = key(p); s = S.get((p, d), 0); pr = PRICE.get(k) or PRICE_FIX.get(p)
    return s - G.get((p, d), 0) / pr * COST[k]  # 個数＝gross÷売価（返品を引かない）
days = sorted({d for (p, d) in A} | {d for (p, d) in S})
last = max(d for (p, d) in A)
print(f'最後のデータ日 {last}。区間＝広告費>0 の連続日（1日以内の空きはつなぐ）')
for p in CAND:
    ds = sorted(d for (q, d) in A if q == p and A[(q, d)] > 0)
    if not ds: print(f'■ {p}: 9/1 以降の広告なし'); continue
    segs = []; cur = [ds[0]]
    for d in ds[1:]:
        if (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(cur[-1])).days <= 2: cur.append(d)
        else: segs.append(cur); cur = [d]
    segs.append(cur)
    print(f'■ {p}（売価 {PRICE.get(key(p)) or PRICE_FIX.get(p)}・原価 {COST.get(key(p))}）')
    for sg in segs[-2:]:
        ad = sum(A[(p, d)] for d in sg); g = sum(gp(p, d) for d in sg)
        f3 = sg[:3]; l3 = sg[-3:]
        b = lambda L: sum(gp(p, d) for d in L) / max(1, sum(A[(p, d)] for d in L))
        w7 = max((b(sg[i:i+7]) for i in range(max(1, len(sg) - 6))), default=0)
        rest = (datetime.date.fromisoformat(last) - datetime.date.fromisoformat(sg[-1])).days
        print(f'   {sg[0][5:]}〜{sg[-1][5:]}（{len(sg)}日）広告費 {ad:,.0f}・倍率 {g/ad:.2f}・利益 {g-ad:+,.0f}・最初の3日 {b(f3):.2f}・最後の3日 {b(l3):.2f}・7日の最高 {w7:.2f}' + (f'・止めて {rest} 日' if rest > 0 else '・配信中'))
