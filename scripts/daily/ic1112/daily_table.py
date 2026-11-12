# -*- coding: utf-8 -*-
"""11/12 11:4x: いまオンの広告すべてを日別で並べる（11/5〜11/11・終日）。
倍率=(売上−原価)÷広告費は商品単位（Shopify×Meta）。広告セットが2つある商品は、広告セット別に Meta計上の購入・売上を並べる（Shopifyは広告セット別に分けられない）。"""
import os, csv, pickle, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
P = pickle.load(open('/tmp/rep1111w.pkl', 'rb')); COST = dict(P['COST']); PRICE = dict(P['PRICE']); MAP = P['MAP']
COST['ナノガラス脱毛パッド'] = (927 * 757 + 326 * 740) / 1253
S = collections.defaultdict(dict); A = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['date'] >= '2026-11-05': S[r['name']][r['date']] = (int(r['gross']), int(r['disc']))
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if r['date'] >= '2026-11-05': A[r['campaign']][r['date']] = A[r['campaign']].get(r['date'], 0) + float(r['cost'])
VC = collections.defaultdict(float)
VG = {'防風あったか裏起毛パンツ': {'S':1140,'M':1148,'L':1219,'XL':1233,'XL灰':1338,'XXL':1251}}
for r in csv.DictReader(open(R + 'data/daily/daily_variant.csv')):
    if r['name'] in VG: VC[(r['date'], r['name'])] += int(r['gross']) / 3980 * VG[r['name']][r['cost_group']]
D7 = ['2026-11-%02d' % i for i in range(5, 12)]
def day(n, d):
    g, dc = S[n].get(d, (0, 0)); u = g / PRICE[n]; k = VC[(d, n)] if n in VG else u * COST[n]; a = A[MAP.get(n, n)].get(d, 0)
    return g - dc, k, a, u
print('■ 店全体 日別（倍率・利益）')
tot = collections.defaultdict(lambda: [0, 0, 0])
for n in S:
    if n not in PRICE or n not in COST: continue
    for d in D7:
        x = day(n, d); tot[d][0] += x[0]; tot[d][1] += x[1]
for c in A:
    for d in D7: tot[d][2] += A[c].get(d, 0)
print('  ' + '・'.join(f"{d[8:]}日 {(tot[d][0]-tot[d][1])/tot[d][2]:.2f}（{tot[d][0]-tot[d][1]-tot[d][2]:+,.0f}）" for d in D7))
ORDER = ['ワイド水切りワイパー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '伸縮ワックス洗車ブラシ', 'クリアビューレインガードフィルム', 'マグネットドアクッション', '4-in-1マルチクリーナー', '快適マジックインソール', '防風あったか裏起毛パンツ']
print('\n■ 商品別 日別の倍率（個数）: 11/5 … 11/11 ｜ 7日の倍率・利益 ｜ 1.25以上の日数')
for n in ORDER:
    cells = []; ok = 0; act = 0
    for d in D7:
        net, k, a, u = day(n, d)
        if a < 500: cells.append('—'); continue
        m = (net - k) / a; act += 1; ok += m >= 1.25; cells.append(f'{m:.2f}（{u:.0f}）')
    xs = [day(n, d) for d in D7]; net = sum(x[0] for x in xs); k = sum(x[1] for x in xs); a = sum(x[2] for x in xs)
    print(f"  {n}: " + '・'.join(cells) + f" ｜ {(net-k)/a:.2f}・{net-k-a:+,.0f} ｜ {ok}/{act}日")
print('\n■ 広告セット別（Meta計上・日別の 購入件数／広告費）と7日計')
AS = collections.defaultdict(dict)
for l in open(D + 'adset_daily_1105_1111_raw.txt'):
    if l[0] == '#' or not l.strip(): continue
    d, c, a, *v = l.strip().split(','); AS[a][d] = [float(x) for x in v]
for a in ['伸縮ガラスクリーナー', '伸縮ガラスクリーナー sabu', 'W固定スマホ車載ホルダー', 'W固定スマホ車載ホルダー -sab', 'ナノガラス脱毛パッド２', 'カタログ全部（テスト）']:
    t = [sum(AS[a][d][i] for d in D7 if d in AS[a]) for i in range(6)]
    print(f"  {a}: " + '・'.join(f"{AS[a][d][4]:.0f}件/{AS[a][d][0]:,.0f}" for d in D7) + f" ｜ 7日 広告{t[0]:,.0f}・購入{t[4]:.0f}件・1件{t[0]/t[4]:,.0f}円・Meta計上売上÷広告費 {t[5]/t[0]:.2f}・1クリック{t[0]/t[2]:.0f}円・クリック率{t[2]/t[1]*100:.2f}%")
    h1 = [sum(AS[a][d][i] for d in D7[:4]) for i in range(6)]; h2 = [sum(AS[a][d][i] for d in D7[4:]) for i in range(6)]
    print(f"      11/5-8 1件{h1[0]/h1[4]:,.0f}円・{h1[5]/h1[0]:.2f} → 11/9-11 1件{h2[0]/h2[4]:,.0f}円・{h2[5]/h2[0]:.2f}")
