# -*- coding: utf-8 -*-
"""11/18 「インソールはなんでうまく行った？」: 旧キャンペーン（11/9〜15・A と A-コピー）と v3（11/16〜17 終日）を、CPM・クリック率・カート・購入・個数・倍率で並べる
Meta: ad_daily_1103_1117_raw.txt／Shopify: data/daily/daily_sales.csv（gross−値引）／原価・売価: product_tabs"""
import csv, collections
src = open('../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); C, P = ns['COST']['快適マジックインソール'], ns['PRICE']['快適マジックインソール']
num = lambda x: 0 if x == 'null' else float(x)
M = collections.defaultdict(lambda: [0.0] * 6)
for l in open('ad_daily_1103_1117_raw.txt'):
    if l[0] == '#': continue
    d, c, s, a, *v = l.strip().split(',')
    if c.startswith('快適マジックインソール'): 
        k = 'v3' if c == '快適マジックインソール v3' else 'old'
        for i in range(6): M[(k, d)][i] += num(v[i])
S = collections.defaultdict(lambda: [0.0, 0.0])
for r in csv.DictReader(open('../../../data/daily/daily_sales.csv')):
    if r['name'] == '快適マジックインソール': S[r['date']][0] += float(r['gross']); S[r['date']][1] += abs(float(r['disc']))
def show(lab, k, ds):
    m = [sum(M[(k, d)][i] for d in ds) for i in range(6)]; g = sum(S[d][0] for d in ds); dc = sum(S[d][1] for d in ds)
    u = g / P; bai = (g - dc - u * C) / m[0]
    print(f'{lab}: 広告費/日 {m[0]/len(ds):,.0f}・CPM {m[0]/m[1]*1000:,.0f}・クリック率 {m[2]/m[1]*100:.2f}%・カート÷クリック {m[4]/m[2]*100:.1f}%・購入÷クリック {m[5]/m[2]*100:.2f}%（Meta）・個数/日 {u/len(ds):.1f}・値引率 {dc/g:.1%}・倍率 {bai:.2f}')
show('旧 11/3〜8 ', 'old', [f'2026-11-0{i}' for i in range(3, 9)])
show('旧 11/9〜15', 'old', ['2026-11-09'] + [f'2026-11-1{i}' for i in range(0, 6)])
show('v3 11/16  ', 'v3', ['2026-11-16'])
show('v3 11/17  ', 'v3', ['2026-11-17'])
show('v3 11/16〜17', 'v3', ['2026-11-16', '2026-11-17'])
