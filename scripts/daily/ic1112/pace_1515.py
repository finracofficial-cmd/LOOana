# -*- coding: utf-8 -*-
"""11/12(木) 15:1x 「伸ばすも減らすも急すぎるの？」
①予算を動かした回数と幅（data/budget-snapshots.csv の全記録・11/4〜11/12）を、決めてある基準（1回2割まで・同じ商品を2日で2回動かさない）と照らす。
②10/20〜11/8 の予算変更（その日の最後の記録どうしの差・キャンペーン合計）について、前3日と後3日の倍率・利益を並べる（終日・CSV）。
 ※②は前後を並べただけ。良い日のあとに上げ、悪い日のあとに下げるので、何もしなくても「上げたあとは下がり、下げたあとは戻る」方向に出やすい。原因の証明ではない。"""
import os, sys, csv, re, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
rows = list(csv.DictReader(open(R + 'data/budget-snapshots.csv')))
key = lambda k: (k[:10], k[10:])
SN = collections.defaultdict(dict)
for r in rows: SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
ks = sorted((k for k in SN if '2026-11-03' <= k[:10] <= '2026-11-12'), key=key)
print(f"■① 11/4〜11/12 の記録 {len([k for k in ks if k[:10] >= '2026-11-04'])}回（1日あたり " + '・'.join(f"{d[5:]} {sum(1 for k in ks if k[:10]==d)}" for d in sorted({k[:10] for k in ks if k[:10] >= '2026-11-04'})) + '）')
EV = []   # (snapshot, campaign, adset, before, after)
for a, b in zip(ks, ks[1:]):
    if b[:10] < '2026-11-04': continue
    for s in set(SN[a]) | set(SN[b]):
        x, y = SN[a].get(s), SN[b].get(s)
        if x != y: EV.append((b, s[0], s[1], x, y))
chg = [e for e in EV if e[3] and e[4]]; on = [e for e in EV if not e[3]]; off = [e for e in EV if not e[4]]
big = [e for e in chg if abs(e[4] / e[3] - 1) > 0.2001]
print(f"  金額の変更 {len(chg)}回（上げ {sum(e[4] > e[3] for e in chg)}・下げ {sum(e[4] < e[3] for e in chg)}）・開始/再開 {len(on)}回・停止 {len(off)}回 ＝ 合計 {len(EV)}回・{len({k[:10] for k in ks if k[:10] >= '2026-11-04'})}日")
print(f"  金額の変更のうち1回2割を超えたもの: {len(big)}/{len(chg)}回（上げ {sum(e[4] > e[3] for e in big)}・下げ {sum(e[4] < e[3] for e in big)}）・変更幅の中央値 上げ {st.median((e[4]/e[3]-1)*100 for e in chg if e[4] > e[3]):+.0f}%・下げ {st.median((e[4]/e[3]-1)*100 for e in chg if e[4] < e[3]):+.0f}%")
byc = collections.defaultdict(list)
for e in EV: byc[e[1]].append(e)
print('  商品ごとの回数（金額の変更＋開始＋停止）と、動かした日:')
rep = 0
for c, es in sorted(byc.items(), key=lambda x: -len(x[1])):
    days = sorted({e[0][:10] for e in es}); dd = [datetime.date.fromisoformat(d) for d in days]
    consec = sum(1 for p, q in zip(dd, dd[1:]) if (q - p).days == 1); same = sum(1 for d in days if sum(1 for e in es if e[0][:10] == d) >= 2)
    rep += (consec > 0 or same > 0)
    print(f"    {c}: {len(es)}回・{len(days)}日（{'・'.join(d[8:] for d in days)}日）・2日続けて動かした {consec}回・同じ日に2回以上 {same}日 ｜ " + ' '.join(('開始' if not e[3] else '停止' if not e[4] else f"{(e[4]/e[3]-1)*100:+.0f}%") for e in es))
print(f"  2日続けて、または同じ日に2回以上動かした商品: {rep}/{len(byc)}")
# ---------- ② 変更の前後（終日） ----------
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, CAMP, series, DATES = g['S'], g['CAMP'], g['series'], g['DATES']
inv = {CAMP.get(n, n): n for n in S}
SER = {n: {r['date']: r for r in series(n)} for n in S}
allk = sorted(SN, key=key); last = {}
for k in allk: last[k[:10]] = k
CB = {d: collections.Counter() for d in last}
for d, k in last.items():
    for (c, s), v in SN[k].items(): CB[d][c] += v
ds = sorted(d for d in CB if '2026-10-19' <= d <= '2026-11-08'); out = []
dn = lambda d, n: (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()
for d in ds:
    p = dn(d, -1)
    if p not in CB: continue
    for c in set(CB[d]) & set(CB[p]):
        x, y = CB[p][c], CB[d][c]
        if x == y or c not in inv: continue
        n = inv[c]; bf = [dn(d, -i) for i in (3, 2, 1)]; af = [dn(d, i) for i in (1, 2, 3)]
        if not all(z in SER[n] and SER[n][z]['ad'] >= 3000 for z in bf + af): continue
        f = lambda zs: (sum(SER[n][z]['sales'] - (SER[n][z]['cost'] or 0) for z in zs), sum(SER[n][z]['ad'] for z in zs))
        (g1, a1), (g2, a2) = f(bf), f(af)
        out.append(dict(d=d, n=n, r=y / x - 1, m1=g1 / a1, m2=g2 / a2, p1=(g1 - a1) / 3, p2=(g2 - a2) / 3, a1=a1 / 3, a2=a2 / 3))
print(f"\n■② 10/20〜11/8 の予算変更 {len(out)}件（前3日・後3日とも広告費3,000円以上）: 前3日 → 後3日（変更当日は除く）")
for lab, f in [('上げ・2割超', lambda o: o['r'] > 0.2001), ('上げ・2割まで', lambda o: 0 < o['r'] <= 0.2001), ('下げ・2割まで', lambda o: -0.2001 <= o['r'] < 0), ('下げ・2割超', lambda o: o['r'] < -0.2001)]:
    xs = [o for o in out if f(o)]
    if not xs: print(f"  {lab}: 0件"); continue
    print(f"  {lab}: {len(xs)}件・倍率の中央値 {st.median(o['m1'] for o in xs):.2f} → {st.median(o['m2'] for o in xs):.2f}（下がった {sum(o['m2'] < o['m1'] for o in xs)}件）・広告費/日 {st.median(o['a1'] for o in xs):,.0f} → {st.median(o['a2'] for o in xs):,.0f}・利益/日の合計 {sum(o['p1'] for o in xs):+,.0f} → {sum(o['p2'] for o in xs):+,.0f}（増えた {sum(o['p2'] > o['p1'] for o in xs)}件）")
print('  明細: ' + ' ｜ '.join(f"{o['d'][5:]} {o['n']} {o['r']*100:+.0f}% 倍率{o['m1']:.2f}→{o['m2']:.2f} 利益/日{o['p1']:+,.0f}→{o['p2']:+,.0f}" for o in sorted(out, key=lambda o: o['r'])))
