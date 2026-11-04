# -*- coding: utf-8 -*-
"""単日の倍率で予算を動かして当たるか（9/7〜11/3・日次CSV・広告3,000円以上の日）。倍率＝(実売−原価)÷広告。ナノの原価はバリアント加重の近似750"""
import ast, csv, collections, statistics as st, datetime as dt, os
B = os.path.dirname(os.path.abspath(__file__)) + '/../../../'
tree = ast.parse(open(B + 'scripts/daily/w1103.py', encoding='utf-8').read()); V = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], 'id', None) in ('COST', 'PRICE', 'MAP'): V[node.targets[0].id] = ast.literal_eval(node.value)
COST, PRICE, MAP = V['COST'], V['PRICE'], V['MAP']; COST['ナノガラス脱毛パッド'] = 750
G = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])); A = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B + 'data/daily/daily_sales.csv')): G[r['name']][r['date']][0] += int(r['gross']); G[r['name']][r['date']][1] += int(r['disc'])
for r in csv.DictReader(open(B + 'data/daily/daily_ad.csv')): A[r['campaign']][r['date']] += float(r['cost'])
def day(n, d):
    g, dc = G[n][d]; a = A[MAP.get(n, n)][d]; return (g - dc - g / PRICE[n] * COST[n]), a
prods = ['伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '快適マジックインソール', 'ポータブルヒートシーラー', '4-in-1マルチクリーナー', '姿勢サポートチェア']
start, end = dt.date(2026, 9, 7), dt.date(2026, 11, 3)
days = [(start + dt.timedelta(i)).isoformat() for i in range((end - start).days + 1)]
allw = good = 0; bad = [0, 0]; bad2 = [0, 0]; gd = [0, 0]; rows = []
for n in prods:
    ds = [d for d in days if A[MAP.get(n, n)][d] > 3000]
    m = {d: day(n, d)[0] / day(n, d)[1] for d in ds}
    p = [(m[a], m[b]) for a, b in zip(ds, ds[1:]) if (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days == 1]
    rows.append((n, len(ds), round(st.correlation([x for x, _ in p], [y for _, y in p]), 2)))
    for i in range(2, len(ds) - 3):
        nxt = sum(day(n, ds[j])[0] for j in range(i + 1, i + 4)) / sum(day(n, ds[j])[1] for j in range(i + 1, i + 4))
        allw += 1; good += nxt >= 1.43
        if m[ds[i]] < 1.25: bad[0] += 1; bad[1] += nxt >= 1.43
        if m[ds[i]] < 1.25 and m[ds[i - 1]] < 1.25: bad2[0] += 1; bad2[1] += nxt >= 1.43
        if m[ds[i]] >= 1.86: gd[0] += 1; gd[1] += nxt >= 1.43
for r in rows: print('翌日の倍率との相関', r)
print(f'全体: 次の3日が1.43以上 {good}/{allw}={good/allw:.0%}')
print(f'単日<1.25 → 次の3日1.43以上 {bad[1]}/{bad[0]}={bad[1]/bad[0]:.0%}')
print(f'2日続けて<1.25 → 次の3日1.43以上 {bad2[1]}/{bad2[0]}={bad2[1]/bad2[0]:.0%}')
print(f'単日≥1.86 → 次の3日1.43以上 {gd[1]}/{gd[0]}={gd[1]/gd[0]:.0%}')
