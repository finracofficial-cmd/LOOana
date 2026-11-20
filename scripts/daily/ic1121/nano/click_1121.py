# -*- coding: utf-8 -*-
"""11/21 「広告費あたりの注文が同じなら、変わってなくない？ CPM とか流入層のぶれで説明できそう」
ナノの表記の前（10/22〜28）と後（10/31〜11/18）を、Meta のクリックを基準に並べ直す。
入力: ../../ic1120/nano/raw.txt の ND 行（Meta ナノ 終日・日別: date,cost,imp,reach,link_click,purchase）・nano_page_daily_raw.txt（Shopify ナノのページに着いた来訪）"""
import os
D0 = os.path.dirname(os.path.abspath(__file__)); ND = {}; N = {}
for l in open(os.path.join(D0, '..', '..', 'ic1120', 'nano', 'raw.txt')):
    if l.startswith('ND,'): p = l.strip().split(','); ND[p[1]] = [int(x) for x in p[2:]]
for l in open(os.path.join(D0, 'nano_page_daily_raw.txt')):
    if l[0] != '#': p = l.strip().split(','); N[p[0]] = [int(x) for x in p[1:]]
def agg(a, b):
    ds = [d for d in sorted(N) if a <= d <= b]; assert all(d in ND for d in ds)
    return dict(n=len(ds), cost=sum(ND[d][0] for d in ds), imp=sum(ND[d][1] for d in ds), reach=sum(ND[d][2] for d in ds), clk=sum(ND[d][3] for d in ds), mp=sum(ND[d][4] for d in ds),
                ses=sum(N[d][0] for d in ds), cart=sum(N[d][1] for d in ds), done=sum(N[d][3] for d in ds))
b, a = agg('2026-10-22', '2026-10-28'), agg('2026-10-31', '2026-11-18'); assert b['n'] == 7 and a['n'] == 19
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
rows = [('広告費/日', lambda x: x['cost'] / x['n'], '{:,.0f}'), ('CPM', lambda x: x['cost'] / x['imp'] * 1000, '{:,.0f}'), ('クリック率（リンク）', lambda x: x['clk'] / x['imp'] * 100, '{:.2f}%'),
        ('クリック÷広告費1万円', lambda x: x['clk'] / x['cost'] * 1e4, '{:.0f}'), ('Meta の購入÷クリック', lambda x: x['mp'] / x['clk'] * 100, '{:.2f}%'), ('Meta の購入÷広告費1万円', lambda x: x['mp'] / x['cost'] * 1e4, '{:.2f}'),
        ('Shopify の来訪÷クリック', lambda x: x['ses'] / x['clk'], '{:.2f}'), ('Shopify の購入÷クリック', lambda x: x['done'] / x['clk'] * 100, '{:.2f}%'), ('Shopify の購入÷来訪（買う率）', lambda x: x['done'] / x['ses'] * 100, '{:.2f}%'),
        ('Shopify の来訪÷広告費1万円', lambda x: x['ses'] / x['cost'] * 1e4, '{:.0f}'), ('1人あたりの表示回数（日ごと）', lambda x: x['imp'] / x['reach'], '{:.2f}')]
P('■ ナノ: 表記の前（10/22〜28）→ 後（10/31〜11/18）')
for k, f, fm in rows: P(f'  {k}: {fm.format(f(b))} → {fm.format(f(a))}（{f(a)/f(b):.2f}倍）')
P(f"  件数: Meta の購入 {b['mp']} → {a['mp']}・Shopify の購入 {b['done']} → {a['done']}・クリック {b['clk']:,} → {a['clk']:,}・来訪 {b['ses']:,} → {a['ses']:,}")
P(f"  買う率 {(a['done']/a['ses'])/(b['done']/b['ses']):.2f}倍 ＝ 購入÷クリック {(a['done']/a['clk'])/(b['done']/b['clk']):.2f}倍 ÷ 来訪÷クリック {(a['ses']/a['clk'])/(b['ses']/b['clk']):.2f}倍")
open(os.path.join(D0, 'click_1121.txt'), 'w').write('\n'.join(L) + '\n')
