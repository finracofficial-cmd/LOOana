# -*- coding: utf-8 -*-
"""11/13(金) 17:0x 「偶然じゃない場合はなに？」
売上÷広告費 ＝ 表示÷広告費（1/CPM）× クリック÷表示（CTR）× 来訪÷クリック × 購入÷来訪（購入率）× 売上÷購入（客単価）
に分け、それぞれを前日までの30日（祝日除く）のふだんの範囲（中央値 ×÷ e^σ）と比べる。範囲の外の要素が「偶然ではない」部分の場所。
さらに商品別に、その日の利益が直近30日の中央値からどれだけずれたかを並べる。
入力: meta_acct_daily_1002_1112.txt（Meta 終日）・sess_daily_1002_1112.json（Shopify 来訪）・data/daily（売上・広告費・注文数）"""
import os, sys, csv, json, math, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
HOL = {'2026-10-12', '2026-11-03'}
MA = {}
for l in open(D + 'meta_acct_daily_1002_1112.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]   # cost, imp, reach, clicks, lpv, atc, purchase
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'sess_daily_1002_1112.json'))['rows']}
NET = collections.defaultdict(int); AD = collections.defaultdict(float); OR = {}
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv')): OR[r['date']] = int(r['orders'])
F = {'表示÷広告費（CPMの逆）': lambda d: MA[d][1] / AD[d], 'クリック率': lambda d: MA[d][3] / MA[d][1], '来訪÷クリック': lambda d: SE[d][0] / MA[d][3],
     '購入率（注文÷来訪）': lambda d: OR[d] / SE[d][0], '客単価': lambda d: NET[d] / OR[d]}
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
SER = {n: {r['date']: r for r in g['series'](n)} for n in g['S']}
day = lambda d, k: (datetime.date.fromisoformat(d) - datetime.timedelta(k)).isoformat()
for T in sys.argv[1:] or ['2026-11-06', '2026-11-11', '2026-11-12']:
    base = [day(T, k) for k in range(1, 31) if day(T, k) not in HOL and day(T, k) in MA and day(T, k) in SE]
    tot = math.log(NET[T] / AD[T]) - st.median(math.log(NET[d] / AD[d]) for d in base)
    assert abs(sum(math.log(f(T)) for f in F.values()) - math.log(NET[T] / AD[T])) < 1e-9
    print(f"■ {T}: 売上÷広告費 {NET[T]/AD[T]:.2f}（30日の中央値比 {math.exp(tot)-1:+.0%}・基準 {len(base)}日）")
    for k, f in F.items():
        lv = [math.log(f(d)) for d in base]; mu, sd = st.median(lv), st.stdev(lv); z = (math.log(f(T)) - mu) / sd
        mark = '　' if abs(z) <= 1 else ('△' if abs(z) <= 2 else '●')
        print(f"  {mark} {k}: {f(T):.4g}（ふだん {math.exp(mu-sd):.4g}〜{math.exp(mu+sd):.4g}）・中央値比 {math.exp(math.log(f(T))-mu)-1:+.0%}")
    rows = []
    for n, s in SER.items():
        if T not in s: continue
        p = lambda d: (s[d]['sales'] - (s[d]['cost'] or 0) - s[d]['ad']) if d in s else 0
        hist = [p(d) for d in base]; rows.append((n, p(T), p(T) - st.median(hist), s[T]['ad']))
    rows.sort(key=lambda r: r[2])
    print('  商品別 その日の利益と直近30日の中央値との差（大きい順に上下3つ）: ' + '／'.join(f"{n[:14]} {pt:+,.0f}（{dv:+,.0f}）" for n, pt, dv, a in rows[:3] + rows[-3:]))
