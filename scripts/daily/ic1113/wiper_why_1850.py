# -*- coding: utf-8 -*-
"""11/13(金) 18:4x 「ワイパーが弱くなった要因を分析せよ」「他の広告を入れた広告セットのパフォーマンスはどう？」
入力: wiper_why_1850_raw.json（11/13 は途中）・data/daily（11/12までの倍率）"""
import os, sys, csv, json, math, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
RAW = json.load(open(D + 'wiper_why_1850_raw.json')); iv = lambda x: 0 if x in ('null', '') else float(x)
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
SER = {r['date']: r for r in g['series']('ワイド水切りワイパー')}
M = {r.split(',')[0]: [iv(x) for x in r.split(',')[1:]] for r in RAW['wiper_meta_daily']['rows']}   # cost, imp, reach, freq, clicks, lpv, atc, purchase
L = {r[0]: [int(x) for x in r[1:]] for r in RAW['wiper_lp_daily']['rows']}                       # sessions, cart, checkout, completed
O = {r[0]: int(r[1]) for r in RAW['wiper_orders_daily']['rows']}
print('■ ワイド水切りワイパー 日別（出した日 11/4・11/13 は 18時台の途中）')
for i, d in enumerate(sorted(M)):
    c, im, rc, fq, cl, lp, atc, pu = M[d]; s, ca, ck, cp = L[d]; r = SER.get(d)
    mult = f"{(r['sales'] - r['cost']) / r['ad']:.2f}" if r and r['ad'] else '—'
    print(f"  {d[5:]}（{i+1}日目）: 広告費 {c:,.0f}・CPM {c/im*1000:,.0f}・クリック率 {cl/im*100:.2f}%｜来訪 {s}・カート {ca/s*100:.1f}%・決済画面→購入 {cp}/{ck}｜注文 {O.get(d,0)}・倍率 {mult}")
def pool(ds):
    s = sum(L[d][0] for d in ds); ca = sum(L[d][1] for d in ds); ck = sum(L[d][2] for d in ds); cp = sum(L[d][3] for d in ds)
    c = sum(M[d][0] for d in ds); im = sum(M[d][1] for d in ds); cl = sum(M[d][4] for d in ds)
    return s, ca, ck, cp, c, im, cl
A, B = ['2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09', '2026-11-10'], ['2026-11-11', '2026-11-12', '2026-11-13']
for lab, ds in (('11/6〜11/10', A), ('11/11〜11/13', B)):
    s, ca, ck, cp, c, im, cl = pool(ds)
    print(f"  {lab}: クリック率 {cl/im*100:.2f}%・CPM {c/im*1000:,.0f}・カート {ca/s*100:.1f}%・決済画面→購入 {cp/ck*100:.0f}%（{cp}/{ck}）・来訪→購入 {cp/s*100:.2f}%")
s, ca, ck, cp, *_ = pool(A); p0 = cp / ck; s2, ca2, ck2, cp2, *_ = pool(B)
z = (cp2 - ck2 * p0) / math.sqrt(ck2 * p0 * (1 - p0))
print(f"  決済画面→購入の下がり方: 前の率 {p0:.0%} なら {ck2*p0:.1f}件のところ {cp2}件（z={z:.1f}）")
rc = {r.split(',')[0]: r for r in RAW['wiper_reach_1104_1108']['rows']}; rc2 = {r.split(',')[0]: r for r in RAW['wiper_reach_1104_1113']['rows']}
a = RAW['wiper_reach_1104_1108']['rows'][0].split(','); b = RAW['wiper_reach_1104_1113']['rows'][0].split(',')
print(f"■ 届いた人数の累計: 11/4〜11/8 {int(a[3]):,}人（頻度 {float(a[4]):.2f}）→ 11/4〜11/13 {int(b[3]):,}人（頻度 {float(b[4]):.2f}）＝5日で {int(b[3])-int(a[3]):,}人増")
print('■ ほかの商品ページの 決済画面→購入（11/6〜11/10 → 11/11〜11/13）')
NM = {'nano-fine': '伸縮ガラスクリーナー', 'vacuum-ad': 'W固定スマホ車載ホルダー', 'washable': 'ナノガラス脱毛パッド', 'car-wash': '伸縮ワックス洗車ブラシ'}
P = collections.defaultdict(lambda: [0, 0, 0, 0])
for d, p, s, ca, ck, cp in RAW['other_lp_daily']['rows']:
    n = next(v for k, v in NM.items() if k in p); key = (n, 'A' if d in A else 'B')
    for i, v in enumerate((s, ca, ck, cp)): P[key][i] += int(v)
for n in NM.values():
    x, y = P[(n, 'A')], P[(n, 'B')]
    print(f"  {n}: {x[3]/x[2]*100:.0f}%（{x[3]}/{x[2]}）→ {y[3]/y[2]*100:.0f}%（{y[3]}/{y[2]}）・カート {x[1]/x[0]*100:.1f}% → {y[1]/y[0]*100:.1f}%")
print('■ ドアクッション・洗車ブラシ 広告別（11/13 15〜19時台・広告Bは15時台に追加）')
for r in RAW['door_brush_ad_15_19']['rows']:
    c, ad, co, im, cl, lp, atc, pu = r.split(',')
    print(f"  {c} {ad}: 広告費 {float(co):,.0f}・表示 {im}・クリック {cl}（{iv(cl)/iv(im)*100:.1f}%）・Metaカート {int(iv(atc))}・Meta購入 {int(iv(pu))}")
