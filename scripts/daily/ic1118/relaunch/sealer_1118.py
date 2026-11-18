# -*- coding: utf-8 -*-
"""11/18 「ヒートシーラーを別のCRと新規CPで復活ありかな」: 30日の配信を週ごとに分ける（Meta の表示・クリック・購入＋Shopify の売上で倍率）"""
import csv, collections
src = open('../../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); C, P = ns['COST']['ポータブルヒートシーラー'], ns['PRICE']['ポータブルヒートシーラー']
num = lambda x: 0 if x == 'null' else float(x)
M = {l.split(',')[0]: [num(x) for x in l.strip().split(',')[3:]] for l in open('sealer_meta_raw.txt') if l[0] != '#'}
S = collections.defaultdict(lambda: [0.0, 0.0])
for r in csv.DictReader(open('../../../../data/daily/daily_sales.csv')):
    if r['name'] == 'ポータブルヒートシーラー': S[r['date']][0] += float(r['gross']); S[r['date']][1] += abs(float(r['disc']))
W = [('10/12〜18', '2026-10-12', '2026-10-18'), ('10/19〜25', '2026-10-19', '2026-10-25'), ('10/26〜11/1', '2026-10-26', '2026-11-01'), ('11/2〜9', '2026-11-02', '2026-11-09')]
print('週・広告費/日・CPM・クリック率・カート÷クリック（Meta）・購入÷クリック（Meta）・倍率（Shopify）')
for lab, a, b in W:
    ds = [d for d in M if a <= d <= b]; v = [sum(M[d][i] for d in ds) for i in range(6)]
    g = sum(S[d][0] for d in ds); dc = sum(S[d][1] for d in ds)
    bai = (g - dc - g / P * C) / v[0]
    print(f'  {lab}: {v[0]/len(ds):,.0f}・{v[0]/v[1]*1000:,.0f}・{v[2]/v[1]*100:.2f}%・{v[4]/v[2]*100:.1f}%・{v[5]/v[2]*100:.2f}%・{bai:.2f}（{g/P:.0f}個）')
