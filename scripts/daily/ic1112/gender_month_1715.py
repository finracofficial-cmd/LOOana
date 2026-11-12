# -*- coding: utf-8 -*-
"""11/12(木) 17:1x 「女性と男性の割合が逆転したのはなぜ？女性向けの商品は今もあるのに」
月ごと・商品ごとに、広告費が女性／男性のどちらに使われたかを並べる（Meta・gender_month_1715_raw.json＝広告費3,000円超の行だけ）。利益は日次CSV（代表原価の近似）。
商品の分類: 期間全体で女性に使われた広告費が60%以上＝女性寄り／40%以下＝男性寄り／その間＝半々。"""
import os, sys, csv, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'; iv = lambda x: 0 if x in ('null', '') else int(x)
RAW = json.load(open(D + 'gender_month_1715_raw.json'))
G = collections.defaultdict(lambda: collections.defaultdict(lambda: {'female': [0, 0], 'male': [0, 0]}))
for r in RAW['rows']:
    ym, c, s, co, im, pu = next(csv.reader([r])); m = ym.split('|')[1]
    if s in ('female', 'male'): G[m][c][s][0] += iv(co); G[m][c][s][1] += iv(pu)
MO = ['07', '08', '09', '10', '11']
print('■ 月ごとの広告費の割合（女性／男性）と、女性に使った広告費の上位')
for m in MO:
    f = sum(v['female'][0] for v in G[m].values()); ma = sum(v['male'][0] for v in G[m].values())
    top = sorted(G[m], key=lambda c: -G[m][c]['female'][0])[:5]
    print(f"  {int(m)}月: 女性 {f/(f+ma)*100:.0f}%（{f/10000:,.0f}万）・男性 {ma/(f+ma)*100:.0f}%（{ma/10000:,.0f}万）｜女性の上位: " + '・'.join(f"{c[:14]} {G[m][c]['female'][0]/10000:,.0f}万" for c in top))
print('\n■ 主な商品の女性の割合（月ごと・広告費）と購入1件の広告費（女性／男性）')
for c in ['ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '快適マジックインソール', '伸縮ガラスクリーナー', '4-in-1マルチクリーナー', '高見えレザーヘッドレストフック', 'ポータブルヒートシーラー', 'コードレスダブルミスト加湿器', '伸縮ワックス洗車ブラシ', 'ワイド水切りワイパー', 'マグネットドアクッション', 'クリアビューレインガードフィルム']:
    out = []
    for m in MO:
        if c in G[m]:
            v = G[m][c]; t = v['female'][0] + v['male'][0]
            if t >= 30000: out.append(f"{int(m)}月 {v['female'][0]/t*100:.0f}%（{t/10000:,.0f}万・{v['female'][0]/max(v['female'][1],1):,.0f}／{v['male'][0]/max(v['male'][1],1):,.0f}円）")
    print(f"  {c}: " + ' → '.join(out))
# 9/1以降に広告を始めた商品を、女性寄り／男性寄り／半々に分けて利益を出す
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, A, CAMP = g['S'], g['series'], g['A'], g['CAMP']
inv = {CAMP.get(n, n): n for n in S}
tot = collections.defaultdict(lambda: [0, 0])
for m in MO:
    for c, v in G[m].items(): tot[c][0] += v['female'][0]; tot[c][1] += v['male'][0]
cls = lambda c: '女性寄り' if tot[c][0] / sum(tot[c]) >= 0.6 else '男性寄り' if tot[c][0] / sum(tot[c]) <= 0.4 else '半々'
first = {}
for n in S:
    rs = series(n); ds = [r['date'] for r in rs if r['ad'] >= 1000]
    if ds: first[n] = (ds[0], rs)
print('\n■ 9/1以降に広告を始めた商品（Metaの行がある分）: 分類・女性の割合・広告費・利益・倍率')
grp = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for c in sorted(tot, key=lambda c: -sum(tot[c])):
    n = inv.get(c)
    if not n or n not in first or first[n][0] < '2026-09-01': continue
    rs = [r for r in first[n][1] if r['ad'] > 0]; a = sum(r['ad'] for r in rs); gp = sum(r['sales'] - (r['cost'] or 0) for r in rs); k = cls(c)
    grp[k][0] += 1; grp[k][1] += a; grp[k][2] += gp - a; grp[k][3] += (gp - a) > 30000; grp[k][4] += (gp - a) < 0
    print(f"  {n}（{first[n][0][5:]}〜）: {k}・女性 {tot[c][0]/sum(tot[c])*100:.0f}%・広告費 {a:,.0f}・利益 {gp-a:+,.0f}・倍率 {gp/a:.2f}")
for k, v in grp.items(): print(f"  【{k}】{v[0]}本・広告費 {v[1]:,.0f}・利益の合計 {v[2]:+,.0f}・利益3万円超 {v[3]}本・赤字 {v[4]}本")
