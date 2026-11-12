# -*- coding: utf-8 -*-
"""11/12 11:2x: 当たり商品が「急に売れなくなる」ときに何が動いているか（Meta日別 × Shopify・読み取りのみ）。
売れ方 = 広告費 × (クリック÷広告費) × (購入÷クリック)。Meta購入はピクセル計上、個数はShopify（CSV）。"""
import os, csv, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
M = collections.defaultdict(dict)
for l in open(D + 'hits_meta_daily_raw.txt'):
    if l[0] == '#' or not l.strip(): continue
    d, n, *v = l.strip().split(','); M[n][d] = [int(float(x)) for x in v]   # cost, imp, reach, clicks, LPV, ATC, purchase
U = collections.defaultdict(dict)
PR = {'クリアビューレインガードフィルム': 3980, '伸縮ワックス洗車ブラシ': 4980, 'マグネットドアクッション': 3980, 'ワイド水切りワイパー': 3980}
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] in PR: U[r['name']][r['date']] = int(r['gross']) // PR[r['name']]
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'rain_sess_day_raw.json'))['rows']}
n = 'クリアビューレインガードフィルム'
print('■ レインガード 日別: 広告費 ｜ 表示単価・クリック率・1クリック・クリック数 ｜ 着地ページ 来訪→カート→購入完了（率）｜ 個数 ｜ 1日に同じ人へ出た回数')
for d in sorted(M[n]):
    c, im, rc, cl, lp, atc, pu = M[n][d]
    if c < 3000: continue
    s = SE.get(d, [0, 0, 0, 0])
    print(f"  {d[5:]}: {c:,} ｜ {c/im*1000:,.0f}・{cl/im*100:.2f}%・{c/cl:.0f}円・{cl} ｜ {s[0]}→{s[1]}→{s[3]}（{s[3]/s[0]*100:.1f}%）｜ {U[n].get(d,0)}個 ｜ {im/rc:.2f}")
def agg(n, ds):
    t = [sum(M[n][d][i] for d in ds if d in M[n]) for i in range(7)]; u = sum(U[n].get(d, 0) for d in ds)
    return dict(cost=t[0], cpm=t[0]/t[1]*1000, ctr=t[3]/t[1]*100, cpc=t[0]/t[3], cvr=t[6]/t[4]*100, units=u, upc=u/t[3]*100, days=len(ds))
print('\n■ 当たり4商品: 売れていた時期 → 直近3日（11/9-11）: 表示単価・クリック率・1クリック・着地→Meta購入・クリック100回あたりの個数（Shopify）')
P = {'クリアビューレインガードフィルム': ['2026-11-06', '2026-11-07', '2026-11-08'], '伸縮ワックス洗車ブラシ': ['2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30'],
     'マグネットドアクッション': ['2026-11-01', '2026-11-02', '2026-11-03'], 'ワイド水切りワイパー': ['2026-11-05', '2026-11-06', '2026-11-07']}
L = ['2026-11-09', '2026-11-10', '2026-11-11']
for n, e in P.items():
    a, b = agg(n, e), agg(n, L)
    pc = lambda x, y: f'{(y/x-1)*100:+.0f}%'
    print(f"  {n}（{e[0][5:]}〜{e[-1][5:]} → 11/9-11）: 表示単価 {a['cpm']:,.0f}→{b['cpm']:,.0f}（{pc(a['cpm'],b['cpm'])}）・クリック率 {a['ctr']:.2f}→{b['ctr']:.2f}%（{pc(a['ctr'],b['ctr'])}）・1クリック {a['cpc']:.0f}→{b['cpc']:.0f}円（{pc(a['cpc'],b['cpc'])}）・着地→購入 {a['cvr']:.1f}→{b['cvr']:.1f}%・クリック100回あたり {a['upc']:.1f}→{b['upc']:.1f}個（{pc(a['upc'],b['upc'])}）・広告費/日 {a['cost']/a['days']:,.0f}→{b['cost']/b['days']:,.0f}")
# レインガード 11/8 → 11/11 の分解
n = 'クリアビューレインガードフィルム'   # 上のループで n が書き換わるので指定し直す
a, b = M[n]['2026-11-08'], M[n]['2026-11-11']; ua, ub = U[n]['2026-11-08'], U[n]['2026-11-11']
print(f"\n■ レインガード 11/8→11/11: 個数 {ua}→{ub}（{ub/ua:.2f}倍）＝ 広告費 {b[0]/a[0]:.2f}倍 × 1円あたりのクリック {(b[3]/b[0])/(a[3]/a[0]):.2f}倍 × クリックあたりの個数 {(ub/b[3])/(ua/a[3]):.2f}倍")
