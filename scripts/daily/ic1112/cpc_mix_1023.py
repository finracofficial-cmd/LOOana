# -*- coding: utf-8 -*-
"""11/12 10:2x: 0〜9時台の「1クリックの広告費」が 11/5-9 → 11/10-12 で上がった分を、商品ごとの上昇と配分の変化に分ける（meta_camp_0009.txt・読み取りのみ）。"""
import os, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
A = collections.defaultdict(dict)
for l in open(D + 'meta_camp_0009.txt'):
    if l[0] == '#' or not l.strip(): continue
    d, n, *v = l.strip().split(','); A[d][n] = [int(x) for x in v]
P1 = ['2026-11-05', '2026-11-06', '2026-11-07', '2026-11-08', '2026-11-09']; P2 = ['2026-11-10', '2026-11-11', '2026-11-12']
def agg(ds):
    t = collections.defaultdict(lambda: [0, 0, 0])
    for d in ds:
        for n, v in A[d].items(): t[n][0] += v[0]; t[n][1] += v[1]; t[n][2] += v[2]
    return t
a, b = agg(P1), agg(P2)
tot = lambda t: (sum(v[0] for v in t.values()), sum(v[1] for v in t.values()), sum(v[2] for v in t.values()))
ca, ia, ka = tot(a); cb, ib, kb = tot(b)
print(f'全体 1クリックの広告費: {ca/ka:.1f}円 → {cb/kb:.1f}円（{((cb/kb)/(ca/ka)-1)*100:+.0f}%）・表示単価 {ca/ia*1000:,.0f}→{cb/ib*1000:,.0f}（{((cb/ib)/(ca/ia)-1)*100:+.0f}%）・クリック率 {ka/ia*100:.2f}→{kb/ib*100:.2f}%')
common = [n for n in b if n in a and a[n][2] >= 100 and b[n][2] >= 100]   # 両期間でクリック100以上
c1 = sum(a[n][0] for n in common); k1 = sum(a[n][2] for n in common); c2 = sum(b[n][0] for n in common); k2 = sum(b[n][2] for n in common)
kmix = sum(b[n][0] / (a[n][0] / a[n][2]) for n in common)
print(f'両期間に出ていた{len(common)}本: {c1/k1:.1f}円 → {c2/k2:.1f}円。配分だけ変わって商品ごとの単価が同じだった場合 {c2/kmix:.1f}円')
for n in sorted(common, key=lambda n: -b[n][0]):
    print(f"  {n}: {a[n][0]/a[n][2]:.0f}→{b[n][0]/b[n][2]:.0f}円（{((b[n][0]/b[n][2])/(a[n][0]/a[n][2])-1)*100:+.0f}%）・表示単価 {a[n][0]/a[n][1]*1000:,.0f}→{b[n][0]/b[n][1]*1000:,.0f}・クリック率 {a[n][2]/a[n][1]*100:.2f}→{b[n][2]/b[n][1]*100:.2f}%")
