# -*- coding: utf-8 -*-
"""11/17 商品別の注文数を「11/10〜16 の注文÷広告費 × 11/17 の広告費」と比べる（ポアソン）。注文は o1117/orders_by_product_1117.txt、広告費は data/daily/daily_ad.csv（v2/v3 は元の商品に足す）"""
import csv, math, collections
def ple(k, l): return sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
A = {}; B = {}
for l in open('scripts/daily/o1117/orders_by_product_1117.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'A': A[p[1]] = (int(p[2]), int(p[3]))
    else: B[p[1]] = int(p[2])
AL = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール',
      '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv3': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック'}
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[AL.get(r['campaign'], r['campaign'])][r['date']] += float(r['cost'])
P = [f'2026-11-{x}' for x in range(10, 17)]; T = '2026-11-17'
for n in sorted(AD, key=lambda n: -AD[n][T]):
    a = AD[n][T]
    if a <= 0: continue
    o, q = A.get(n, (0, 0))
    if n.startswith('カタログ'): print(f'{n}: 広告 {a:,.0f}（商品に分けられない）'); continue
    ab = sum(AD[n][d] for d in P); ob = B.get(n, 0)
    if ab < 10000 or ob < 3: print(f'{n}: {o}注文（{q}個）・広告 {a:,.0f}（比べる過去が短い）'); continue
    lam = ob / ab * a; p = ple(o, lam) if o < lam else 1 - ple(o - 1, lam)
    v = '偶然では起きにくい' if p < 0.025 else ('端' if p < 0.16 else '範囲内')
    print(f"{n}: {o}注文（{q}個）・広告 {a:,.0f}・期待 {lam:.1f}・{'少ない' if o < lam else '多い'}側 {p*100:.1f}% → {v}")
