# -*- coding: utf-8 -*-
"""11/12(木) 17:0x 「倍率判定（上げる基準 1.86）が厳しすぎるんじゃないの？」
予算の記録がある全期間（7/18〜11/8）で、その日に予算を 上げた／動かさなかった／下げた 商品×日を、直前3日の倍率の帯ごとに並べ、後3日の粗利と広告費の変化を比べる（終日・CSV・代表原価の近似）。
 「足した（減らした）広告費1円あたり、粗利がいくら増えた（減った）か」＝ (実際の後3日の粗利 − 動かさなかった場合の見込み) ÷ 広告費の変化。
 見込み＝同じ帯で動かさなかった日の「後3日の粗利 ÷ 前3日の粗利」を前3日の粗利に掛けたもの（良い日のあとは下がり、悪い日のあとは戻る分を差し引くため）。
 ※件数が少ない帯がある。同じ商品の日が重なっている。動かさなかった日＝その日と前後3日に予算の変更がない日。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, A, CAMP = g['S'], g['series'], g['A'], g['CAMP']
SD = {n: {r['date']: r for r in series(n)} for n in S if any(A[CAMP.get(n, n)].values())}
dn = lambda d, k: (datetime.date.fromisoformat(d) + datetime.timedelta(days=k)).isoformat(); gp = lambda r: r['sales'] - (r['cost'] or 0)
SN = collections.defaultdict(dict); key = lambda k: (k[:10], k[10:])
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
last = {}
for k in sorted(SN, key=key): last[k[:10]] = k
CB = {d: collections.Counter() for d in last}
for d, k in last.items():
    for (c, s), v in SN[k].items(): CB[d][c] += v
rows = []
for n in SD:
    c = CAMP.get(n, n)
    for d in sorted(x for x in CB if '2026-07-21' <= x <= '2026-11-08'):
        if not all(dn(d, k) in CB and CB[dn(d, k)].get(c) for k in range(-4, 4)): continue
        bf = [dn(d, -i) for i in (3, 2, 1)]; af = [dn(d, i) for i in (1, 2, 3)]
        if not all(z in SD[n] and SD[n][z]['ad'] >= 3000 and SD[n][z]['cost'] is not None for z in bf + af): continue
        r = CB[d][c] / CB[dn(d, -1)][c] - 1
        quiet = all(CB[dn(d, k)][c] == CB[dn(d, k - 1)][c] for k in range(-3, 4))
        g1 = sum(gp(SD[n][z]) for z in bf) / 3; a1 = sum(SD[n][z]['ad'] for z in bf) / 3; g2 = sum(gp(SD[n][z]) for z in af) / 3; a2 = sum(SD[n][z]['ad'] for z in af) / 3
        kind = '上げた' if r > 0.05 else '下げた' if r < -0.05 else ('動かさず' if quiet else None)
        if kind: rows.append(dict(n=n, d=d, r=r, kind=kind, m1=g1 / a1, g1=g1, a1=a1, g2=g2, a2=a2))
print(f"対象 {len(rows)}商品×日（7/21〜11/8）: 上げた {sum(o['kind']=='上げた' for o in rows)}・下げた {sum(o['kind']=='下げた' for o in rows)}・動かさず {sum(o['kind']=='動かさず' for o in rows)}")
BANDS = [('1.25未満', 0, 1.25), ('1.25〜1.5', 1.25, 1.5), ('1.5〜1.86', 1.5, 1.86), ('1.86以上', 1.86, 99)]
print('直前3日の倍率の帯｜動き: 件数・倍率（前→後）・広告費/日（前→後）・利益/日 平均（前→後・増えた件数）｜足した(減らした)1円あたりの粗利の増減')
for lab, lo, hi in BANDS:
    ctl = [o for o in rows if o['kind'] == '動かさず' and lo <= o['m1'] < hi]
    drift = sum(o['g2'] for o in ctl) / sum(o['g1'] for o in ctl) if ctl else None; adr = sum(o['a2'] for o in ctl) / sum(o['a1'] for o in ctl) if ctl else None
    for kind in ('上げた', '動かさず', '下げた'):
        xs = [o for o in rows if o['kind'] == kind and lo <= o['m1'] < hi]
        if not xs: print(f"  {lab}｜{kind}: 0件"); continue
        n_ = len(xs); G1 = sum(o['g1'] for o in xs); A1 = sum(o['a1'] for o in xs); G2 = sum(o['g2'] for o in xs); A2 = sum(o['a2'] for o in xs)
        line = f"  {lab}｜{kind}: {n_}件・{G1/A1:.2f}→{G2/A2:.2f}・{A1/n_:,.0f}→{A2/n_:,.0f}・{(G1-A1)/n_:+,.0f}→{(G2-A2)/n_:+,.0f}（増えた {sum((o['g2']-o['a2']) > (o['g1']-o['a1']) for o in xs)}）"
        if kind != '動かさず' and drift:
            exp_g = G1 * drift; exp_a = A1 * adr
            inc = (G2 - exp_g) / (A2 - exp_a) if abs(A2 - exp_a) > 1 else float('nan')
            line += f"｜見込みとの差: 広告費 {(A2-exp_a)/n_:+,.0f}・粗利 {(G2-exp_g)/n_:+,.0f} → 1円あたり {inc:.2f}・利益への効果 {((G2-exp_g)-(A2-exp_a))/n_:+,.0f}円/日"
        print(line)
# 直前7日の倍率の帯で、下げた日と動かさなかった日を比べる（下げる基準を「7日の倍率」で見た場合）
rows7 = []
for n in SD:
    c = CAMP.get(n, n)
    for d in sorted(x for x in CB if '2026-07-25' <= x <= '2026-11-08'):
        if not all(dn(d, k) in CB and CB[dn(d, k)].get(c) for k in range(-4, 4)): continue
        b7 = [dn(d, -i) for i in range(1, 8)]; bf = [dn(d, -i) for i in (3, 2, 1)]; af = [dn(d, i) for i in (1, 2, 3)]
        if not all(z in SD[n] and SD[n][z]['ad'] >= 3000 and SD[n][z]['cost'] is not None for z in b7 + af): continue
        r = CB[d][c] / CB[dn(d, -1)][c] - 1; quiet = all(CB[dn(d, k)][c] == CB[dn(d, k - 1)][c] for k in range(-3, 4))
        kind = '上げた' if r > 0.05 else '下げた' if r < -0.05 else ('動かさず' if quiet else None)
        if not kind: continue
        m7 = sum(gp(SD[n][z]) for z in b7) / sum(SD[n][z]['ad'] for z in b7)
        rows7.append(dict(kind=kind, m7=m7, g1=sum(gp(SD[n][z]) for z in bf) / 3, a1=sum(SD[n][z]['ad'] for z in bf) / 3, g2=sum(gp(SD[n][z]) for z in af) / 3, a2=sum(SD[n][z]['ad'] for z in af) / 3))
print('\n直前7日の倍率の帯｜動き: 件数・利益/日 平均（前3日→後3日）｜見込みとの差')
for lab, lo, hi in [('1.25未満', 0, 1.25), ('1.25〜1.5', 1.25, 1.5), ('1.5〜1.86', 1.5, 1.86), ('1.86以上', 1.86, 99)]:
    ctl = [o for o in rows7 if o['kind'] == '動かさず' and lo <= o['m7'] < hi]
    if not ctl: continue
    drift = sum(o['g2'] for o in ctl) / sum(o['g1'] for o in ctl); adr = sum(o['a2'] for o in ctl) / sum(o['a1'] for o in ctl)
    print(f"  {lab}｜動かさず: {len(ctl)}件・{sum(o['g1']-o['a1'] for o in ctl)/len(ctl):+,.0f}→{sum(o['g2']-o['a2'] for o in ctl)/len(ctl):+,.0f}（増えた {sum((o['g2']-o['a2']) > (o['g1']-o['a1']) for o in ctl)}）")
    for kind in ('上げた', '下げた'):
        xs = [o for o in rows7 if o['kind'] == kind and lo <= o['m7'] < hi]
        if not xs: print(f"  {lab}｜{kind}: 0件"); continue
        n_ = len(xs); G1 = sum(o['g1'] for o in xs); A1 = sum(o['a1'] for o in xs); G2 = sum(o['g2'] for o in xs); A2 = sum(o['a2'] for o in xs)
        print(f"  {lab}｜{kind}: {n_}件・{(G1-A1)/n_:+,.0f}→{(G2-A2)/n_:+,.0f}（増えた {sum((o['g2']-o['a2']) > (o['g1']-o['a1']) for o in xs)}）｜広告費 {(A2-A1*adr)/n_:+,.0f}・粗利 {(G2-G1*drift)/n_:+,.0f} → 1円あたり {(G2-G1*drift)/(A2-A1*adr):.2f}・利益への効果 {((G2-G1*drift)-(A2-A1*adr))/n_:+,.0f}円/日")
# 条件を満たす日の割合（10/1〜11/11・出して11日目以降は区別せず、7日とも広告費3,000円以上）
tot = 0; cnt = collections.Counter()
for n in SD:
    for d, r in SD[n].items():
        if not ('2026-10-01' <= d <= '2026-11-11'): continue
        w = [SD[n].get(dn(d, -i)) for i in range(7)]
        if not all(x and x['ad'] >= 3000 for x in w): continue
        m7 = sum(gp(x) for x in w) / sum(x['ad'] for x in w); tot += 1
        for th in (1.25, 1.4, 1.5, 1.6, 1.86): cnt[th] += m7 >= th
print('\n7日の倍率が基準以上の日の割合（10/1〜11/11・' + str(tot) + '商品×日）: ' + '・'.join(f"{th}以上 {cnt[th]/tot*100:.0f}%" for th in (1.25, 1.4, 1.5, 1.6, 1.86)))
