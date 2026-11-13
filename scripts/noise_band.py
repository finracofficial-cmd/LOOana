# -*- coding: utf-8 -*-
"""店全体の効率が「偶然の範囲か」を判定する（2026-11-13 ユーザー指示）。

使い方:
  python3 scripts/noise_band.py 2026-11-12      # その日の終日の数字を判定

入力: data/daily/daily_sales.csv・daily_ad.csv（実測のみ）と scripts/product_tabs.py の原価。
基準（対象日の前日までの30日・祝日を除く）:
  - ふだんの範囲 = 中央値 ×÷ e^σ（σ = 日ごとの対数の標準偏差）。この中なら「偶然の範囲内」
  - e^σ〜e^2σ = 「偶然でも起きるが端」、e^2σ の外 = 「偶然では起きにくい」
  - 7日平均は σ/√7 で同じ判定
  - 3日以上続けて同じ側の端（±σの外側）にいたら「偶然ではなく本当に動いている」とみる
日中の数字はこのスクリプトでは判定しない（同時刻の過去21日と並べて、最小〜最大の外かどうかで判定する）。"""
import csv, sys, math, collections, datetime, statistics as st
R = __file__.rsplit('/scripts/', 1)[0] + '/'
HOL = {'2026-07-20', '2026-08-11', '2026-09-21', '2026-09-22', '2026-09-23', '2026-10-12', '2026-11-03', '2026-11-23'}
D = sys.argv[1] if len(sys.argv) > 1 else None
NET = collections.defaultdict(int); AD = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
D = D or max(AD)
assert D in AD and D in NET, f'{D} は data/daily にない（先に append する）'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
CO = collections.defaultdict(float)
for n in g['S']:
    for r in g['series'](n): CO[r['date']] += r['cost'] or 0
day = lambda d, k: (datetime.date.fromisoformat(d) - datetime.timedelta(k)).isoformat()
MET = {'売上÷広告費': lambda d: NET[d] / AD[d], '倍率': lambda d: (NET[d] - CO[d]) / AD[d]}
base = [day(D, k) for k in range(1, 31) if day(D, k) not in HOL and AD.get(day(D, k))]
assert len(base) >= 20, f'基準の日が足りない（{len(base)}日）'
def verdict(z):
    return '偶然の範囲内' if abs(z) <= 1 else ('偶然でも起きるが端（' + ('上' if z > 0 else '下') + '）' if abs(z) <= 2 else '偶然では起きにくい（' + ('上' if z > 0 else '下') + '）')
print(f'■ {D}（基準: 前日までの30日・祝日除く {len(base)}日）' + ('　※対象日は祝日' if D in HOL else ''))
for name, f in MET.items():
    lv = [math.log(f(d)) for d in base]; mu, sd = st.median(lv), st.stdev(lv)
    lo, hi = math.exp(mu - sd), math.exp(mu + sd)
    z = (math.log(f(D)) - mu) / sd
    w7 = [day(D, k) for k in range(7)]
    v7 = (sum(NET[d] for d in w7) - (sum(CO[d] for d in w7) if name == '倍率' else 0)) / sum(AD[d] for d in w7)
    z7 = (math.log(v7) - mu) / (sd / math.sqrt(7))
    run, side = 0, 0
    for k in range(0, 10):
        d = day(D, k)
        if d not in AD: break
        zz = (math.log(f(d)) - mu) / sd; s = 1 if zz > 1 else (-1 if zz < -1 else 0)
        if s == 0 or (side and s != side): break
        side = s; run += 1
    print(f"  {name}: その日 {f(D):.2f}（ふだんの範囲 {lo:.2f}〜{hi:.2f}・中央値 {math.exp(mu):.2f}・ぶれ ±{(math.exp(sd)-1)*100:.0f}%）→ {verdict(z)}")
    print(f"    7日平均 {v7:.2f}（偶然のぶれ ±{(math.exp(sd/math.sqrt(7))-1)*100:.1f}%・範囲 {math.exp(mu - sd/math.sqrt(7)):.2f}〜{math.exp(mu + sd/math.sqrt(7)):.2f}）→ {verdict(z7)}")
    if run >= 3: print(f"    {run}日続けて範囲の{'上' if side > 0 else '下'}の外 → 偶然ではなく本当に動いているとみる")
    elif run: print(f"    範囲の{'上' if side > 0 else '下'}の外は {run}日（3日続いたら本物とみる）")
print(f"  広告費 {AD[D]:,.0f}・利益 {NET[D]-CO[D]-AD[D]:+,.0f}（量は偶然ではなく予算で決まる。利益＝（倍率−1）×広告費）")
