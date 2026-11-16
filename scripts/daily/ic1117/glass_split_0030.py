# -*- coding: utf-8 -*-
"""11/17 00:3x ユーザー「ガラスクリーナーは予算配分変えた方がいいとかある？」
ガラスクリーナーの2つの広告セット（主力・sabu）を Meta の計上（購入・購入金額）で比べる。Shopify では同じ商品なので広告セット別の実売は分けられない
→ Meta の計上は判断の主には使わない決まりだが、同じ商品の中で2つを比べる物差しはこれしかない。偶然のぶれは購入件数（ポアソン）で見る"""
import collections, math
D = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0, 0]))
for l in open(__file__.rsplit('/', 1)[0] + '/glass_adsets_1027_1116.txt'):
    if l[0] == '#': continue
    d, a, *v = l.strip().split(','); D[a][d] = [int(x) for x in v]
def days(a, b): return [d for d in sorted({d for x in D.values() for d in x}) if a <= d <= b]
for lab, a, b in [('7日 11/10-16', '2026-11-10', '2026-11-16'), ('前の7日 11/03-09', '2026-11-03', '2026-11-09'), ('3週 10/27-11/16', '2026-10-27', '2026-11-16')]:
    print(f'■ {lab}')
    for s in ('伸縮ガラスクリーナー sabu', '伸縮ガラスクリーナー'):
        c, i, k, p, v = [sum(D[s][d][j] for d in days(a, b)) for j in range(5)]
        print(f'  {s}: 広告費 {c:,}・購入 {p}（1件 {c/p:,.0f}円）・Meta計上の売上÷広告費 {v/c:.2f}・クリック率 {k/i:.2%}・CPM {c/i*1000:,.0f}')
    s1, s2 = '伸縮ガラスクリーナー sabu', '伸縮ガラスクリーナー'
    c1 = sum(D[s1][d][0] for d in days(a, b)); p1 = sum(D[s1][d][3] for d in days(a, b))
    c2 = sum(D[s2][d][0] for d in days(a, b)); p2 = sum(D[s2][d][3] for d in days(a, b))
    # 購入/広告費 の比の偶然のぶれ（ポアソン・log の ±2σ）
    r = (p1 / c1) / (p2 / c2); band = 2 * math.sqrt(1 / p1 + 1 / p2)
    print(f'  → sabu の 購入/広告費 は主力の {r:.2f}倍（偶然のぶれ ×÷{math.exp(band):.2f}＝{r/math.exp(band):.2f}〜{r*math.exp(band):.2f}）→ ' + ('1 を含む＝偶然の範囲' if r / math.exp(band) <= 1 <= r * math.exp(band) else '1 を含まない'))
