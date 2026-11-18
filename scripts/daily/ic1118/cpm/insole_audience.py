# -*- coding: utf-8 -*-
"""11/18 「インソールはなんで復活してきた？」: 旧キャンペーン（10/19〜11/17）と v3（11/16〜17）の 年齢×性別の広告費の割合と購入（agegender_raw.txt・Meta 計上）"""
import collections
num = lambda x: 0 if x == 'null' else float(x)
D = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0, 0.0]))
for l in open('agegender_raw.txt'):
    if l[0] == '#': continue
    c, a, g, cost, imp, clk, pur = l.strip().split(',')
    if c in ('快適マジックインソール', '快適マジックインソール v3'):
        k = 'v3' if 'v3' in c else '旧'
        band = '18-34' if a in ('18-24', '25-34') else ('35-54' if a in ('35-44', '45-54') else '55+')
        v = D[k][band]; v[0] += num(cost); v[1] += num(imp); v[2] += num(pur)
for k in ('旧', 'v3'):
    tot = sum(v[0] for v in D[k].values()); ti = sum(v[1] for v in D[k].values()); tp = sum(v[2] for v in D[k].values())
    print(f'{k}: 広告費 {tot:,.0f}・CPM {tot/ti*1000:,.0f}・購入 {tp:.0f}（1万円あたり {tp/tot*1e4:.2f}）')
    for b in ('18-34', '35-54', '55+'):
        v = D[k][b]
        print(f'   {b}: 広告費の割合 {v[0]/tot:.0%}・CPM {v[0]/v[1]*1000:,.0f}・購入 {v[2]:.0f}（1万円あたり {v[2]/v[0]*1e4 if v[0] else 0:.2f}）')
