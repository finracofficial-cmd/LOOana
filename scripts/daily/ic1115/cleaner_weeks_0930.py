# -*- coding: utf-8 -*-
"""伸縮ガラスクリーナーが長く売れ続けているか（出してからの週ごと・data/daily）。比べる: W固定・洗車ブラシ・ワイパー・ドアクッション（2026-11-15 09:1x）"""
import csv, sys, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
for n in ('伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '伸縮ワックス洗車ブラシ', 'ワイド水切りワイパー', 'マグネットドアクッション'):
    rs = [r for r in g['series'](n) if r['ad'] > 0 and r['date'] <= '2026-11-14']
    st = datetime.date.fromisoformat(rs[0]['date']); W = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in g['series'](n):
        d = datetime.date.fromisoformat(r['date'])
        if st <= d <= datetime.date(2026, 11, 14):
            w = (d - st).days // 7; W[w][0] += r['sales']; W[w][1] += r['cost'] or 0; W[w][2] += r['ad']; W[w][3] += 1
    print(f'{n}（{st} から）: ' + ' ／ '.join(f"{w+1}週目 {(v[0]-v[1])/v[2]:.2f}・{v[2]/v[3]:,.0f}円/日" + (f'（{v[3]}日）' if v[3] < 7 else '') for w, v in sorted(W.items()) if v[2] > 0))
