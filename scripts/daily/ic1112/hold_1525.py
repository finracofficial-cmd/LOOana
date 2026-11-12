# -*- coding: utf-8 -*-
"""11/12(木) 15:2x 「売上下がっても広告費を維持するパターンもあるよね？ディレイする期間あるけどそれでもよいの？」
倍率が悪い日（1.25未満）のあと、予算を大きく動かさずに続けた翌日がどうだったかを、商品×日で数える（終日・CSV・代表原価の近似）。
 対象: その日と翌日の広告費が5,000円以上の商品×日。倍率=(売上−原価)÷広告費・利益=売上−原価−広告費。
 ※過去の実績を条件別に数えただけ。翌日の予算が同じだったとは限らない（広告費が前日の±25%以内のものだけに絞った数字も出す）。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, DATES, A, CAMP = g['S'], g['series'], g['DATES'], g['A'], g['CAMP']
SER = {n: [r for r in series(n)] for n in S if any(A[CAMP.get(n, n)].values())}
def run(lo, hi, lab, same_budget=False):
    seq = collections.defaultdict(list)   # 連続して悪かった日数（その日を含む） -> 翌日の (倍率, 利益, 広告費)
    base = []; first_loss = []
    for n, rs in SER.items():
        streak = 0
        for i, r in enumerate(rs[:-1]):
            if not (lo <= r['date'] <= hi) or r['ad'] < 5000 or r['cost'] is None: streak = 0; continue
            m = (r['sales'] - r['cost']) / r['ad']; nx = rs[i + 1]
            streak = streak + 1 if m < 1.25 else 0
            if nx['ad'] < 5000 or nx['cost'] is None or nx['date'] > hi: continue
            if same_budget and not (0.75 <= nx['ad'] / r['ad'] <= 1.25): continue
            m2 = (nx['sales'] - nx['cost']) / nx['ad']; p2 = nx['sales'] - nx['cost'] - nx['ad']
            seq[min(streak, 3)].append((m2, p2, nx['ad'], r['sales'] - r['cost'] - r['ad'], n, r['date']))
    print(f"\n■ {lab}（{lo[5:]}〜{hi[5:]}）" + ('・翌日の広告費が前日の±25%以内だけ' if same_budget else ''))
    for k, name in [(0, '前日が1.25以上'), (1, '1日だけ1.25未満'), (2, '2日続けて1.25未満'), (3, '3日以上続けて1.25未満')]:
        xs = seq[k]
        if not xs: print(f"  {name}: 0件"); continue
        print(f"  {name}（{len(xs)}件）→ 翌日: 1.25以上に戻った {sum(x[0] >= 1.25 for x in xs)}件（{sum(x[0] >= 1.25 for x in xs)/len(xs)*100:.0f}%）・1.0未満（赤字） {sum(x[0] < 1 for x in xs)/len(xs)*100:.0f}%・倍率の中央値 {st.median(x[0] for x in xs):.2f}・翌日の利益 平均 {sum(x[1] for x in xs)/len(xs):+,.0f}円（合計 {sum(x[1] for x in xs):+,.0f}・全体の倍率 {(sum(x[1] for x in xs)+sum(x[2] for x in xs))/sum(x[2] for x in xs):.2f}）｜その悪かった日の利益 平均 {sum(x[3] for x in xs)/len(xs):+,.0f}円")
    return seq
s1 = run('2026-10-01', '2026-11-11', '10/1以降'); run('2026-10-01', '2026-11-11', '10/1以降', True); run('2026-09-01', '2026-11-11', '9/1以降'); run('2026-06-29', '2026-11-11', '全期間')
# 商品別（10/1以降）: 1日だけ悪かった翌日
print('\n■ 商品別（10/1以降）: 1.25未満の日（連続日数を問わず）の翌日に1.25以上へ戻った割合')
byp = collections.defaultdict(list)
for k in (1, 2, 3):
    for x in s1[k]: byp[x[4]].append(x)
for n, xs in sorted(byp.items(), key=lambda z: -len(z[1])):
    if len(xs) >= 4: print(f"  {n}: {sum(x[0] >= 1.25 for x in xs)}/{len(xs)}件・翌日の利益 平均 {sum(x[1] for x in xs)/len(xs):+,.0f}円")
