# -*- coding: utf-8 -*-
"""11/12(木) 18:1x 「過去商品の時間をあけたヒットは難しいのかな？」
日次CSV（6/29〜11/11）から、広告を14日以上止めたあとに再開した配信をすべて拾い、再開後の成績を並べる（終日・代表原価の近似）。
 再開＝直前14日の広告費が0で、その日3,000円以上（それより前に広告費がある商品だけ）。配信は広告費が1,000円未満になる日まで。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, A, CAMP = g['S'], g['series'], g['A'], g['CAMP']
gp = lambda r: r['sales'] - (r['cost'] or 0)
out = []
for n in S:
    if not any(A[CAMP.get(n, n)].values()): continue
    rs = series(n)
    for i, r in enumerate(rs):
        if r['ad'] >= 3000 and i >= 14 and all(x['ad'] == 0 for x in rs[i - 14:i]) and any(x['ad'] > 0 for x in rs[:i - 14]):
            run = []
            for x in rs[i:]:
                if x['ad'] < 1000: break
                run.append(x)
            prev = [x for x in rs[:i] if x['ad'] >= 1000]; gap = (datetime.date.fromisoformat(r['date']) - datetime.date.fromisoformat(prev[-1]['date'])).days - 1
            p7 = prev[-7:]; a = sum(x['ad'] for x in run); f7 = run[:7]
            out.append(dict(n=n, d=r['date'], gap=gap, days=len(run), ad=a, m=sum(gp(x) for x in run) / a, prof=sum(gp(x) for x in run) - a,
                            mprev=sum(gp(x) for x in p7) / sum(x['ad'] for x in p7), mall=sum(gp(x) for x in prev) / sum(x['ad'] for x in prev), m7=sum(gp(x) for x in f7) / sum(x['ad'] for x in f7), ongoing=run[-1]['date'] == rs[-1]['date']))
out.sort(key=lambda o: o['d'])
print(f"■ 14日以上あけて再開した配信（6/29〜11/11）: {len(out)}回")
print('  商品（再開日・あけた日数）: 続いた日数・広告費・再開後の倍率（最初の7日）・利益 ｜止める前7日の倍率・それまでの通算')
for o in out:
    print(f"  {o['n']}（{o['d'][5:]}・{o['gap']}日あけ）: {o['days']}日{'（継続中）' if o['ongoing'] else ''}・{o['ad']:,.0f}円・{o['m']:.2f}（{o['m7']:.2f}）・{o['prof']:+,.0f} ｜{o['mprev']:.2f}・{o['mall']:.2f}")
big = [o for o in out if o['ad'] >= 20000]
print(f"\n  広告費2万円以上の再開 {len(big)}回: 倍率1.25以上 {sum(o['m'] >= 1.25 for o in big)}回・7日以上続いた {sum(o['days'] >= 7 for o in big)}回・利益が出た {sum(o['prof'] > 0 for o in big)}回・利益の合計 {sum(o['prof'] for o in big):+,.0f}・広告費の合計 {sum(o['ad'] for o in big):,.0f}")
print(f"  止める前7日より再開後の最初の7日のほうが良かった: {sum(o['m7'] > o['mprev'] for o in big)}/{len(big)}回・中央値 止める前 {st.median(o['mprev'] for o in big):.2f} → 再開後の最初の7日 {st.median(o['m7'] for o in big):.2f}")
small = [o for o in out if o['ad'] < 20000]
print(f"  広告費2万円未満で終わった再開 {len(small)}回: 広告費の合計 {sum(o['ad'] for o in small):,.0f}・利益の合計 {sum(o['prof'] for o in small):+,.0f}（" + '・'.join(f"{o['n']} {o['d'][5:]} {o['days']}日" for o in small) + '）')
