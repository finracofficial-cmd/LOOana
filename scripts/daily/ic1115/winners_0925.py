# -*- coding: utf-8 -*-
"""たくさん売れる商品とそうでない商品の違い（2026-11-15 09:1x ユーザー「ガラスクリーナーってめっちゃ売れてるじゃん？たくさん売れるのとそうではない商品の違いってなんだ？」）
期間 10/16〜11/14（30日）・広告費10万円以上の13商品。Meta（キャンペーン別）と Shopify（商品別の注文・売上）と data/daily（原価・広告費）
注文/広告費1万円 ＝ 表示/1万円（CPMの逆）× クリック率 × 注文/クリック。倍率 ＝ 注文/広告費 × 1注文の売上（値引後）×（1−原価率）
注文/クリックは「Shopify の商品の注文 ÷ Meta のクリック」（カタログや他の入口からの注文も入る目安）"""
import csv, sys, math, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
H = R + 'scripts/daily/ic1115/'
M = {}; O = {}
for l in open(H + 'meta_camp_30d_1016_1114.txt'):
    if l[0] != '#': p = l.strip().split(','); M[p[0]] = [int(x) for x in p[1:]]
for l in open(H + 'prod_orders_30d_1016_1114.txt'):
    if l[0] != '#': p = l.strip().split(','); O[p[0]] = (int(p[1]), int(p[2]), -int(p[3]))
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
DS = [(datetime.date(2026, 10, 16) + datetime.timedelta(k)).isoformat() for k in range(30)]
rows = []
for n in O:
    s = {r['date']: r for r in g['series'](n)}
    net = sum(s[d]['sales'] for d in DS); cogs = sum(s[d]['cost'] or 0 for d in DS); ad = sum(s[d]['ad'] for d in DS)
    gross = sum(int(r['gross']) for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')) if r['name'] == n and r['date'] in DS)
    assert gross == O[n][1], (n, gross, O[n][1])                      # Shopify の取り直し＝data/daily
    assert abs(ad - M[n][0]) <= M[n][0] * 0.005 + 5, (n, ad, M[n][0])   # Meta の取り直し＝data/daily（0.5%以内）
    c, im, cl, lpv, atc, pu = M[n]; o = O[n][0]
    rows.append(dict(n=n, ad=ad, imp_per=im / c * 10000, ctr=cl / im, opc=o / cl, opy=o / c * 10000, aov=net / o, cr=cogs / net, mult=(net - cogs) / ad, prof=net - cogs - ad, o=o, disc=O[n][2] / O[n][1]))
rows.sort(key=lambda r: -r['prof'])
print('商品（30日の利益順）         利益       倍率  注文/1万円 = 表示/1万円 × クリック率 × 注文/クリック ｜ 1注文の売上 原価率 値引率 注文')
for r in rows:
    print(f"{r['n'][:14]:<15} {r['prof']:+10,.0f}  {r['mult']:.2f}   {r['opy']:5.2f}   =  {r['imp_per']:6,.0f}  × {r['ctr']*100:5.2f}% × {r['opc']*100:5.2f}%  ｜ {r['aov']:6,.0f}  {r['cr']*100:4.1f}%  {r['disc']*100:4.1f}%  {r['o']}")
import statistics as st
print('\n13商品の中央値: ' + ' ・ '.join(f"{k} {st.median(r[k] for r in rows)*(100 if k in ('ctr','opc','cr','disc') else 1):.2f}" for k in ('mult', 'opy', 'imp_per', 'ctr', 'opc', 'aov', 'cr')))
# 倍率と各要素の相関（対数）
L = lambda k: [math.log(r[k]) for r in rows]
for k, lab in (('imp_per', '表示/1万円'), ('ctr', 'クリック率'), ('opc', '注文/クリック'), ('aov', '1注文の売上'), ('cr', '原価率')):
    print(f'  倍率と {lab} の相関（13商品・対数）: {st.correlation(L("mult"), L(k)):+.2f}')
