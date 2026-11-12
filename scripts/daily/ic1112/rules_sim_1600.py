# -*- coding: utf-8 -*-
"""11/12(木) 16:0x 「この運用で本当にいいの？説得してみて」
新しい基準を、実際の日次の数字（終日・CSV）に当てはめたら、11/4〜11/12の朝に「動かす」と出たのは何回だったかを数える【試算】。
 実際の倍率は実際の予算で出たものなので、基準どおりに動かしていた場合の結果ではない。数えているのは「基準が何回・どの商品に反応したか」だけ。
 基準: 下げ=2日続けて倍率1.25未満で−20%／上げA=出して10日以内・前日と通算が1.86以上・消化95%以上で+4,000円（毎日可）／上げB=それ以外・7日1.86以上・消化95%以上で+20%（直近2日が続けて1.25未満なら上げない）／同じ商品は2日あける（上げAは例外）。広告費3,000円未満の日は判定に使わない。"""
import os, sys, csv, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series, A, CAMP = g['S'], g['series'], g['A'], g['CAMP']
SER = {n: series(n) for n in S if any(A[CAMP.get(n, n)].values())}; SD = {n: {r['date']: r for r in rs} for n, rs in SER.items()}
dn = lambda d, k: (datetime.date.fromisoformat(d) + datetime.timedelta(days=k)).isoformat()
gp = lambda r: r['sales'] - (r['cost'] or 0); mm = lambda r: gp(r) / r['ad']
starts = collections.defaultdict(list)
for n, rs in SER.items():
    for i, r in enumerate(rs):
        if r['ad'] >= 1000 and i >= 14 and all(x['ad'] == 0 for x in rs[i - 14:i]): starts[n].append(r['date'])
def age(n, d):
    ls = [s for s in starts[n] if s <= d]; return None if not ls else (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(max(ls))).days + 1
SN = collections.defaultdict(dict); key = lambda k: (k[:10], k[10:])
for r in csv.DictReader(open(R + 'data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
last = {}
for k in sorted(SN, key=key): last[k[:10]] = k
CB = {d: collections.Counter() for d in last}
for d, k in last.items():
    for (c, s), v in SN[k].items(): CB[d][c] += v
MORN = [dn('2026-11-04', i) for i in range(9)]   # 11/4〜11/12 の朝（前日までの終日で判定）
ev = []; lock = {}
for morning in MORN:
    y = dn(morning, -1)
    for n in SER:
        r = SD[n].get(y)
        if not r or r['ad'] < 3000: continue
        c = CAMP.get(n, n); bud = CB.get(y, {}).get(c); used = (r['ad'] / bud) if bud else None; a = age(n, y)
        r1 = SD[n].get(dn(y, -1)); bad2 = r1 and r1['ad'] >= 3000 and mm(r) < 1.25 and mm(r1) < 1.25
        locked = n in lock and (datetime.date.fromisoformat(morning) - datetime.date.fromisoformat(lock[n])).days <= 2
        if bad2:
            if not locked: ev.append((morning, n, '下げ −20%', f"{mm(r1):.2f}・{mm(r):.2f}")); lock[n] = morning
            continue
        if a is not None and a <= 10:
            run = [SD[n][dn(y, -i)] for i in range(a) if dn(y, -i) in SD[n] and SD[n][dn(y, -i)]['ad'] > 0]
            cum = sum(gp(x) for x in run) / sum(x['ad'] for x in run)
            if mm(r) >= 1.86 and cum >= 1.86 and used and used >= 0.95: ev.append((morning, n, '上げA +4,000円', f"前日{mm(r):.2f}・通算{cum:.2f}・{a}日目"))
        else:
            w = [SD[n].get(dn(y, -i)) for i in range(7)]
            if all(x and x['ad'] >= 3000 for x in w):
                m7 = sum(gp(x) for x in w) / sum(x['ad'] for x in w)
                if m7 >= 1.86 and used and used >= 0.95 and not locked: ev.append((morning, n, '上げB +20%', f"7日{m7:.2f}")); lock[n] = morning
print(f"■ 新しい基準を 11/4〜11/12 の朝に当てはめた場合【試算】: 動かす {len(ev)}回（下げ {sum('下げ' in e[2] for e in ev)}・上げA {sum('上げA' in e[2] for e in ev)}・上げB {sum('上げB' in e[2] for e in ev)}）・1日あたり {len(ev)/9:.1f}回 ／ 実際は金額の変更63回（1日あたり7.0回）")
for m in MORN:
    xs = [e for e in ev if e[0] == m]
    print(f"  {m[5:]}朝: " + ('なし' if not xs else ' ｜ '.join(f"{e[1]} {e[2]}（{e[3]}）" for e in xs)))
