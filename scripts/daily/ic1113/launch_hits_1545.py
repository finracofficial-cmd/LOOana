# -*- coding: utf-8 -*-
"""11/13(金) 15:4x 「とにかく売れる商品を見つけなきゃあかんね」
9/1以降に広告を始めた商品（広告費1,000円以上の日が初めて来た日が9/1以降）を、9/1〜11/12 の利益・倍率・最初の3日の倍率で並べる（data/daily・代表原価）"""
import os, csv, sys, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, PRICE = g['S'], g['series'], g['PRICE']
CAR = {'伸縮ガラスクリーナー', '高見えレザーヘッドレストフック', '伸縮ワックス洗車ブラシ', 'ワイド水切りワイパー', 'マグネットドアクッション', 'クリアビューレインガードフィルム', '高見えレザードアポケット', 'すき間収納シートポケット'}
A, B = '2026-09-01', '2026-11-12'; rows = []
for n in S:
    ser = series(n); ds = sorted(r['date'] for r in ser if r['ad'] >= 1000)
    if not ds or ds[0] < A: continue
    rs = [r for r in ser if A <= r['date'] <= B]; ad = sum(r['ad'] for r in rs); gp = sum(r['sales'] - (r['cost'] or 0) for r in rs)
    e = (datetime.date.fromisoformat(ds[0]) + datetime.timedelta(2)).isoformat(); d3 = [r for r in ser if ds[0] <= r['date'] <= e]
    a3 = sum(r['ad'] for r in d3); g3 = sum(r['sales'] - (r['cost'] or 0) for r in d3)
    rows.append((n, ds[0], len(ds), ad, gp - ad, gp / ad, PRICE.get(n), g3 / a3 if a3 else 0, n in CAR))
for r in sorted(rows, key=lambda x: -x[4]):
    print(f"  {'車' if r[8] else '　'} {r[0]}（{r[1][5:]}〜・{r[2]}日・{r[6]}円）: 広告費 {r[3]:,.0f}・利益 {r[4]:+,.0f}・倍率 {r[5]:.2f}・最初の3日 {r[7]:.2f}")
hit = [r for r in rows if r[4] >= 100000]
print(f"\n■ {len(rows)}本中 利益10万円以上 {len(hit)}本（利益の合計 {sum(r[4] for r in hit):+,.0f}）・赤字 {sum(r[4] < 0 for r in rows)}本（赤字の合計 {sum(r[4] for r in rows if r[4] < 0):+,.0f}）")
for lab, f in (('車用品', lambda r: r[8]), ('それ以外', lambda r: not r[8])):
    s = [r for r in rows if f(r)]; print(f"  {lab}: {len(s)}本中 利益10万円以上 {sum(r[4] >= 100000 for r in s)}本")
print(f"  最初の3日の倍率 2.4以上: 当たり {sum(r[7] >= 2.4 for r in hit)}/{len(hit)}本・当たり以外 {sum(r[7] >= 2.4 for r in rows if r[4] < 100000)}/{len(rows)-len(hit)}本（当たり以外の最高 {max(r[7] for r in rows if r[4] < 100000):.2f}）")
