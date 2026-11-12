# -*- coding: utf-8 -*-
"""11/12(木) 15:4x 「11日目以降は週1厳しくない？」
出して11日目以降・以前からの商品について、①7日の倍率1.86以上（上げる条件）がどれくらい続くか ②前3日の倍率が高かったときに「上げた日」と「動かさなかった日」で、後3日の利益がどう違ったか を数える（終日・CSV・代表原価の近似）。
 ※②は条件別に数えただけ。件数が少なく、同じ商品の日が重なっている。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, DATES, A, CAMP = g['S'], g['series'], g['DATES'], g['A'], g['CAMP']
SER = {n: series(n) for n in S if any(A[CAMP.get(n, n)].values())}; SD = {n: {r['date']: r for r in rs} for n, rs in SER.items()}
dn = lambda d, k: (datetime.date.fromisoformat(d) + datetime.timedelta(days=k)).isoformat()
gp = lambda r: r['sales'] - (r['cost'] or 0)
# 開始日（直前14日の広告費0・その日3,000円以上）
starts = collections.defaultdict(list)
for n, rs in SER.items():
    for i, r in enumerate(rs):
        if r['ad'] >= 3000 and i >= 14 and all(x['ad'] == 0 for x in rs[i - 14:i]): starts[n].append(r['date'])
def age(n, d):
    ls = [s for s in starts[n] if s <= d]; return None if not ls else (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(max(ls))).days + 1
mature = lambda n, d: age(n, d) is None or age(n, d) > 10
SN = collections.defaultdict(dict); key = lambda k: (k[:10], k[10:])
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
last = {}
for k in sorted(SN, key=key): last[k[:10]] = k
CB = {d: collections.Counter() for d in last}
for d, k in last.items():
    for (c, s), v in SN[k].items(): CB[d][c] += v
# ---------- ① 7日の倍率1.86以上・消化95%以上がどれくらいあるか（10/1〜11/11・出して11日目以降） ----------
print('■① 出して11日目以降・以前からの商品で「7日の倍率1.86以上」だった日（10/1〜11/11・7日とも広告費3,000円以上）')
tot = 0; hitd = collections.defaultdict(list)
for n, rs in SER.items():
    for r in rs:
        d = r['date']
        if not ('2026-10-01' <= d <= '2026-11-11') or not mature(n, d): continue
        w = [dn(d, -i) for i in range(7)]
        if not all(z in SD[n] and SD[n][z]['ad'] >= 3000 for z in w): continue
        tot += 1; m7 = sum(gp(SD[n][z]) for z in w) / sum(SD[n][z]['ad'] for z in w)
        if m7 >= 1.86:
            b = CB.get(d, {}).get(CAMP.get(n, n)); a7 = sum(SD[n][z]['ad'] for z in w) / 7
            hitd[n].append((d, m7, None if not b else SD[n][d]['ad'] / b))
print(f"  対象 {tot}商品×日のうち 1.86以上は {sum(len(v) for v in hitd.values())}日（{sum(len(v) for v in hitd.values())/tot*100:.0f}%）")
for n, v in sorted(hitd.items(), key=lambda z: -len(z[1])):
    ds = [x[0] for x in v]; runs = []; s = ds[0]; p = ds[0]
    for d in ds[1:]:
        if d != dn(p, 1): runs.append((s, p)); s = d
        p = d
    runs.append((s, p))
    print(f"  {n}: {len(v)}日・続いた期間 " + '、'.join(f"{a[5:]}〜{b[5:]}（{(datetime.date.fromisoformat(b)-datetime.date.fromisoformat(a)).days+1}日）" for a, b in runs))
# ---------- ② 上げた日 と 動かさなかった日（10/20〜11/8） ----------
rows = []
for n in SER:
    c = CAMP.get(n, n)
    for d in sorted(x for x in CB if '2026-10-20' <= x <= '2026-11-08'):
        p = dn(d, -1)
        if p not in CB or not CB[p].get(c) or not CB[d].get(c) or not mature(n, d): continue
        bf = [dn(d, -i) for i in (3, 2, 1)]; af = [dn(d, i) for i in (1, 2, 3)]
        if not all(z in SD[n] and SD[n][z]['ad'] >= 3000 for z in bf + af): continue
        r = CB[d][c] / CB[p][c] - 1
        f = lambda zs: (sum(gp(SD[n][z]) for z in zs) / 3, sum(SD[n][z]['ad'] for z in zs) / 3)
        (g1, a1), (g2, a2) = f(bf), f(af)
        rows.append(dict(n=n, d=d, r=r, m1=g1 / a1, m2=g2 / a2, p1=g1 - a1, p2=g2 - a2, a1=a1, a2=a2, g1=g1, g2=g2))
print(f"\n■② 出して11日目以降・以前からの商品（10/20〜11/8・{len(rows)}商品×日）: 前3日 → 後3日")
for band, fb in [('前3日の倍率 1.86以上', lambda o: o['m1'] >= 1.86), ('前3日の倍率 1.25〜1.86', lambda o: 1.25 <= o['m1'] < 1.86)]:
    print(f"  【{band}】")
    for lab, fr in [('上げた（+5%超）', lambda o: o['r'] > 0.05), ('動かさなかった', lambda o: abs(o['r']) <= 0.05), ('下げた（−5%超）', lambda o: o['r'] < -0.05)]:
        xs = [o for o in rows if fb(o) and fr(o)]
        if not xs: print(f"    {lab}: 0件"); continue
        da = sum(o['a2'] - o['a1'] for o in xs); dg = sum(o['g2'] - o['g1'] for o in xs)
        print(f"    {lab}: {len(xs)}件・倍率の中央値 {st.median(o['m1'] for o in xs):.2f} → {st.median(o['m2'] for o in xs):.2f}・広告費/日 平均 {sum(o['a1'] for o in xs)/len(xs):,.0f} → {sum(o['a2'] for o in xs)/len(xs):,.0f}・利益/日 平均 {sum(o['p1'] for o in xs)/len(xs):+,.0f} → {sum(o['p2'] for o in xs)/len(xs):+,.0f}（差 {sum(o['p2']-o['p1'] for o in xs)/len(xs):+,.0f}・増えた {sum(o['p2'] > o['p1'] for o in xs)}件）")
