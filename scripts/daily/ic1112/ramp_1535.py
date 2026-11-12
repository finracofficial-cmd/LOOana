# -*- coding: utf-8 -*-
"""11/12(木) 15:3x 「3（上げるのは週1回）は上げる頻度厳しくなりそうじゃない？」
①9/1以降に広告を始めた（再開を含む）商品の、開始からの日数ごとの倍率と広告費（終日・CSV・代表原価の近似）。開始＝直前14日の広告費が0で、その日3,000円以上。
②10/20〜11/8 に予算を上げた15件（pace_1515.py と同じ条件）を、開始から何日目の増額だったかで分ける。
③ワイド水切りワイパー・クリアビューレインガードフィルムの日別（予算・広告費・倍率・利益）と、8,000円のままだった場合の【試算】。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, DATES, A, CAMP = g['S'], g['series'], g['DATES'], g['A'], g['CAMP']
SER = {n: series(n) for n in S if any(A[CAMP.get(n, n)].values())}
mult = lambda r: (r['sales'] - (r['cost'] or 0)) / r['ad'] if r['ad'] else None
launch = {}   # (商品, 開始日) -> その後の行
for n, rs in SER.items():
    for i, r in enumerate(rs):
        if r['date'] >= '2026-09-01' and r['ad'] >= 3000 and all(x['ad'] == 0 for x in rs[max(0, i - 14):i]) and i >= 14:
            run = []
            for x in rs[i:]:
                if x['ad'] < 1000: break
                run.append(x)
            launch[(n, r['date'])] = run
print('■① 9/1以降の開始・再開（開始から3日以上続いたもの）: 開始からの日ごとの倍率（広告費・千円）')
hit = []
for (n, d), run in sorted(launch.items(), key=lambda z: z[0][1]):
    if len(run) < 3: continue
    a3 = sum(x['ad'] for x in run[:3]); m3 = sum(x['sales'] - (x['cost'] or 0) for x in run[:3]) / a3
    tag = '◎' if m3 >= 1.86 else ''
    if m3 >= 1.86: hit.append((n, d, run))
    print(f"  {tag}{n}（{d[5:]}〜・{len(run)}日・最初の3日 {m3:.2f}）: " + ' '.join(f"{mult(x):.1f}({x['ad']/1000:.0f})" for x in run[:12]))
print(f"\n  最初の3日の倍率が1.86以上だった {len(hit)}本の、開始からの日ごとの倍率の中央値: " + ' '.join(f"{i+1}日目 {st.median(mult(run[i]) for _, _, run in hit if len(run) > i):.2f}({sum(1 for _, _, run in hit if len(run) > i)}本)" for i in range(12)))
print('  同じく、倍率1.86以上だった本数: ' + ' '.join(f"{i+1}日目 {sum(1 for _, _, run in hit if len(run) > i and mult(run[i]) >= 1.86)}/{sum(1 for _, _, run in hit if len(run) > i)}" for i in range(12)))
print('  同じく、利益の合計（全本）: ' + ' '.join(f"{i+1}日目 {sum(run[i]['sales'] - (run[i]['cost'] or 0) - run[i]['ad'] for _, _, run in hit if len(run) > i):+,.0f}" for i in range(12)))
# ② 増額15件を開始からの日数で分ける
first = {}
for (n, d), run in launch.items(): first.setdefault(n, []).append(d)
SN = collections.defaultdict(dict); key = lambda k: (k[:10], k[10:])
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
last = {}
for k in sorted(SN, key=key): last[k[:10]] = k
CB = {d: collections.Counter() for d in last}
for d, k in last.items():
    for (c, s), v in SN[k].items(): CB[d][c] += v
inv = {CAMP.get(n, n): n for n in S}; dn = lambda d, k: (datetime.date.fromisoformat(d) + datetime.timedelta(days=k)).isoformat()
SD = {n: {r['date']: r for r in rs} for n, rs in SER.items()}; out = []
for d in sorted(x for x in CB if '2026-10-19' <= x <= '2026-11-08'):
    p = dn(d, -1)
    if p not in CB: continue
    for c in set(CB[d]) & set(CB[p]):
        x, y = CB[p][c], CB[d][c]
        if y <= x or c not in inv or inv[c] not in SD: continue
        n = inv[c]; bf = [dn(d, -i) for i in (3, 2, 1)]; af = [dn(d, i) for i in (1, 2, 3)]
        if not all(z in SD[n] and SD[n][z]['ad'] >= 3000 for z in bf + af): continue
        f = lambda zs: sum(SD[n][z]['sales'] - (SD[n][z]['cost'] or 0) - SD[n][z]['ad'] for z in zs) / 3
        ls = [l for l in first.get(n, []) if l <= d]; age = (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(max(ls))).days + 1 if ls else None
        out.append((n, d, y / x - 1, age, f(bf), f(af)))
print(f"\n■② 予算を上げた{len(out)}件: 開始から何日目だったか（—は9/1より前からの商品）")
for lab, fn in [('開始から10日以内', lambda o: o[3] is not None and o[3] <= 10), ('開始から11日目以降・以前からの商品', lambda o: o[3] is None or o[3] > 10)]:
    xs = [o for o in out if fn(o)]
    print(f"  {lab}: {len(xs)}件・利益が増えた {sum(o[5] > o[4] for o in xs)}件・利益/日の合計 {sum(o[4] for o in xs):+,.0f} → {sum(o[5] for o in xs):+,.0f}")
    for o in sorted(xs, key=lambda o: o[1]): print(f"    {o[1][5:]} {o[0]} {o[2]*100:+.0f}%（{'—' if o[3] is None else str(o[3])+'日目'}）利益/日 {o[4]:+,.0f} → {o[5]:+,.0f}")
# ③ 2本の日別
print('\n■③ 当たり2本の日別（その日の最後の予算／広告費／倍率／利益）と、8,000円のままで同じ倍率だった場合の利益【試算】')
for n in ['ワイド水切りワイパー', 'クリアビューレインガードフィルム']:
    rs = [r for r in SER[n] if r['ad'] >= 3000]; tot = 0; alt = 0
    for r in rs:
        m = mult(r); p_ = r['sales'] - (r['cost'] or 0) - r['ad']; tot += p_; alt += (m - 1) * min(r['ad'], 8000)
        print(f"  {n} {r['date'][5:]}: 予算 {CB.get(r['date'], {}).get(CAMP.get(n, n), 0):,}／{r['ad']:,.0f}／{m:.2f}／{p_:+,.0f}")
    print(f"   → 実際の利益の合計 {tot:+,.0f} ／ 【試算】8,000円のままで同じ倍率だった場合 {alt:+,.0f}（差 {tot-alt:+,.0f}。少ない予算なら倍率はもっと高かった可能性があり、差は多めに出ている）")
