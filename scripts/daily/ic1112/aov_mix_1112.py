# -*- coding: utf-8 -*-
"""11/12 10:4x: 客単価が低い理由の確認（3,980円の商品の比率・1注文あたりの個数）と、注文1件あたりの広告費（読み取りのみ）。
終日は data/daily のCSV（個数=gross÷売価・優先配送とVIP特典は個数に入れない）、今日は 0〜9時台の store_0009 / sales_prod_0009 / meta_camp_0009。"""
import os, csv, pickle, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
PRICE = dict(pickle.load(open('/tmp/rep1111w.pkl', 'rb'))['PRICE'])
S = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['date'] >= '2026-10-14': S[r['date']][r['name']] = (int(r['gross']), int(r['disc']))
ORD = {r['date']: int(r['orders']) for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv'))}
NOU = {'優先配送', 'VIP特典'}
def mix(items, orders):
    """items: {商品: (gross, disc)} → 個数・3,980円の個数・平均単価・値引率・個数/注文・客単価"""
    u = u39 = gu = 0; g = dc = 0
    for n, (gr, d) in items.items():
        g += gr; dc += d
        if n in NOU or n not in PRICE or not gr: continue
        q = gr / PRICE[n]; u += q; gu += gr
        if PRICE[n] == 3980: u39 += q
    return u, u39 / u * 100, gu / u, dc / g * 100, u / orders, (g - dc) / orders
def show(lab, ds):
    items = collections.defaultdict(lambda: [0, 0]); o = 0
    for d in ds:
        o += ORD[d]
        for n, (gr, dc) in S[d].items(): items[n][0] += gr; items[n][1] += dc
    u, s39, pu, dr, upo, aov = mix(items, o)
    print(f'  {lab}: 客単価 {aov:,.0f} ｜ 1注文あたり {upo:.3f}個 ｜ 商品の平均単価 {pu:,.0f}円 ｜ 3,980円の商品が個数の {s39:.0f}% ｜ 値引率 {dr:.1f}%')
    return upo, pu, dr, aov
days = sorted(S)
print('■ 週ごと（終日）')
W = [('10/14-20', '2026-10-14', '2026-10-20'), ('10/21-27', '2026-10-21', '2026-10-27'), ('10/28-11/3', '2026-10-28', '2026-11-03'), ('11/4-10', '2026-11-04', '2026-11-10')]
res = {}
for lab, a, b in W: res[lab] = show(lab, [d for d in days if a <= d <= b])
print('■ 日ごと（終日）')
for d in [x for x in days if x >= '2026-11-04']: res[d] = show(d[5:], [d])
# 今日 0〜9時台
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
T = '2026-11-12'
it = {n: (int(g), -int(dc)) for d, n, g, dc in rd('sales_prod_0009.txt') if d == T}
ST = {d: v for d, *v in rd('store_0009.txt')}
u, s39, pu, dr, upo, aov = mix(it, int(ST[T][2]))
print(f'■ 今日 0〜9時台: 客単価 {aov:,.0f} ｜ 1注文あたり {upo:.3f}個 ｜ 商品の平均単価 {pu:,.0f}円 ｜ 3,980円の商品が個数の {s39:.0f}%（{u:.0f}個中）｜ 値引率 {dr:.1f}%')
print('  売れた商品:', '・'.join(f"{n[:8]} {int(g/PRICE[n])}個（{PRICE[n]:,}円）" for n, (g, dc) in sorted(it.items(), key=lambda x: -x[1][0]) if n in PRICE and n not in NOU and g))
# 分解: 10/14-20 の週 → 11/11
a = res['10/14-20']; b = res['2026-11-11']
print(f"\n■ 10/14-20 → 11/11 の客単価 {a[3]:,.0f} → {b[3]:,.0f}（{(b[3]/a[3]-1)*100:+.1f}%）: 1注文あたりの個数 {(b[0]/a[0]-1)*100:+.1f}%・商品の平均単価 {(b[1]/a[1]-1)*100:+.1f}%・値引き {((1-b[2]/100)/(1-a[2]/100)-1)*100:+.1f}%")
# 注文1件あたりの広告費（0〜9時台）
A = collections.defaultdict(int)
for d, n, c, *_ in rd('meta_camp_0009.txt'): A[d] += int(c)
print('\n■ 注文1件あたりの広告費（0〜9時台）: ' + '・'.join(f"{d[5:]} {A[d]/int(ST[d][2]):,.0f}円" for d in sorted(A)))
xs = [A[d] / int(ST[d][2]) for d in sorted(A) if d < T]
print(f"  今日 {A[T]/int(ST[T][2]):,.0f}円（9時台の広告費があと2,500円増えると {(A[T]+2500)/int(ST[T][2]):,.0f}円）／過去7日 中央値 {st.median(xs):,.0f}円（{min(xs):,.0f}〜{max(xs):,.0f}）")
print(f"  客単価だけ過去7日の中央値5,129円だった場合の 売上÷広告費: {5129*int(ST[T][2])/A[T]:.2f}（今日の実際 {(int(ST[T][0])+int(ST[T][1]))/A[T]:.2f}）")
