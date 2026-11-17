# -*- coding: utf-8 -*-
"""11/17(火) 18:3x 「ガラスは最近広告費上げたんだっけ？急に売れなくなった理由はなんだろ。たまたま？」
ガラスクリーナーの 0〜17時台を、①商品ページから入った来訪の流れ（Shopify・過去21日の同時刻）②広告セット別（Meta・11/10〜14 の同時刻）で比べる。日中の数字なので予算の判定には使わない
入力: glass_landing_0017.json・glass_adsets_0017.txt・sales_prod_0017.txt"""
import json, math, collections, statistics as st
D = __file__.rsplit('/', 1)[0] + '/'
T = '2026-11-17'
def ple(k, l): return sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
L = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'glass_landing_0017.json'))['rows']}
P = sorted(d for d in L if d < T); assert len(P) == 21
def band(lab, f, fm):
    t = f(T); xs = [f(d) for d in P]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('範囲の外（下）' if t < min(xs) else '範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/21 → {out}")
print('■ ガラスの商品ページから入った来訪（Shopify・0〜17時台・過去21日の同時刻）')
band('来訪', lambda d: L[d][0], '{}')
band('カートに入れた来訪%', lambda d: L[d][1] / L[d][0] * 100, '{:.1f}')
band('決済画面まで%', lambda d: L[d][2] / L[d][0] * 100, '{:.1f}')
band('購入まで%', lambda d: L[d][3] / L[d][0] * 100, '{:.1f}')
band('購入÷カート%', lambda d: L[d][3] / L[d][1] * 100, '{:.0f}')
for i, lab in ((1, 'カート'), (3, '購入')):
    r = sum(L[d][i] for d in P) / sum(L[d][0] for d in P); lam = r * L[T][0]
    print(f"  → {lab} {L[T][i]}（来訪{L[T][0]}×過去21日の率{r*100:.1f}%＝期待 {lam:.1f}）・この数以下 {ple(L[T][i], lam)*100:.0f}%")
low = [d for d in P if L[d][1] / L[d][0] <= L[T][1] / L[T][0]]
print('  カート率が今日以下だった日: ' + '・'.join(f"{d[5:]}（{L[d][1]}/{L[d][0]}）" for d in low))
# 広告セット別
M = collections.defaultdict(lambda: [0] * 5)
for l in open(D + 'glass_adsets_0017.txt'):
    if l[0] == '#': continue
    d, s, a, *v = l.strip().split(','); v = [int(x) for x in v]
    for k in (f'{d}|{s}{a}', f'{d}|計'):
        M[k] = [x + y for x, y in zip(M[k], v)]
P5 = [f'2026-11-{x}' for x in range(10, 15)]
def agg(days, key): return [sum(M[f'{d}|{key}'][i] for d in days) for i in range(5)]
print('■ 広告セット別（Meta・0〜17時台）。購入は Meta 計上')
for key, lab in (('mainA', '主力 A'), ('mainB', '主力 B（11/14〜）'), ('sabuA', 'サブ A'), ('計', '合計')):
    for days, dl in ((P5, '11/10〜14'), (['2026-11-16'], '11/16'), ([T], '11/17')):
        c, im, lp, atc, pu = agg(days, key)
        if not c: continue
        print(f"  {lab} {dl}: 広告費 {c:,}（日 {c/len(days):,.0f}）・CPM {c/im*1000:,.0f}・着地÷表示 {lp/im*100:.2f}%・着地/1万円 {lp/c*1e4:.0f}・カート÷着地 {atc/lp*100:.1f}%・購入÷着地 {pu/lp*100:.1f}%（{pu}）")
    if key in ('mainA', 'sabuA', '計'):
        c, im, lp, atc, pu = agg(P5, key); ct = M[f'{T}|{key}']
        lam = pu / lp * ct[2]; lam2 = atc / lp * ct[2]
        print(f"    → 今日の着地 {ct[2]} から: 購入 期待 {lam:.1f}・実際 {ct[4]}・この数以下 {ple(ct[4], lam)*100:.0f}% ／ カート 期待 {lam2:.1f}・実際 {ct[3]}・この数以下 {ple(ct[3], lam2)*100:.0f}%")
c = agg([T], '計')[0]; b = M[f'{T}|mainB'][0]; print(f"  今日の B の取り分（主力の中）: {b/(b+M[f'{T}|mainA'][0])*100:.0f}%")
# 商品別の注文（Shopify）
PO = collections.defaultdict(int)
for l in open(D + 'sales_prod_0017.txt'):
    if l[0] != '#':
        d, n, g, dc, o = l.strip().split(',')
        if n == '伸縮ガラスクリーナー': PO[d] += int(o)
print('■ ガラスの注文（Shopify・0〜17時台）: ' + '・'.join(f"{d[5:]} {PO[d]}" for d in sorted(PO)))
