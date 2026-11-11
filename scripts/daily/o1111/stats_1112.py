# -*- coding: utf-8 -*-
"""11/12 定例の本文用の補助数値（来訪・購入率・Meta配信指標・広告セット別）。実測ファイルのみ"""
import csv, collections, io, contextlib
O = 'scripts/daily/o1111/'
ses = {}
for l in open(O + 'sess_1027_1111_raw.txt'):
    if l[0] != '#': d, s, c, k, f = l.strip().split(','); ses[d] = (int(s), int(c), int(k), int(f))
bands = {r[0]: [int(x) for x in r[1:]] for r in list(csv.reader(open('data/daily/daily_order_bands.csv')))[1:] if r}
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1111.py').read(), g)
STORE = g['STORE']; GROSSD = g['GROSSD']
days = sorted(ses); T = '2026-11-11'; P = [d for d in days if d < T]
cvr = lambda d: bands[d][0] / ses[d][0] * 100; cart = lambda d: ses[d][1] / ses[d][0] * 100; comp = lambda d: ses[d][3] / ses[d][2] * 100; aov = lambda d: STORE[d] / bands[d][0]
for lab, f, fm in [('セッション', lambda d: ses[d][0], '{:,.0f}'), ('注文', lambda d: bands[d][0], '{:.0f}'), ('CVR%', cvr, '{:.2f}'), ('カゴ投入率%', cart, '{:.2f}'), ('完了率%', comp, '{:.1f}'), ('客単価', aov, '{:,.0f}'),
                   ('7000円以上の割合%', lambda d: bands[d][1] / bands[d][0] * 100, '{:.1f}'), ('値引率%', lambda d: (GROSSD[d] - STORE[d]) / GROSSD[d] * 100, '{:.1f}')]:
    xs = [f(d) for d in P]
    print(f"{lab}: 11/11 {fm.format(f(T))} ／ 前日 {fm.format(f('2026-11-10'))} ／ 前週水11/4 {fm.format(f('2026-11-04'))} ／ 15日（{P[0][5:]}〜{P[-1][5:]}） {fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日{sum(x < f(T) for x in xs)}/15")
print('11/11 内訳: カート', ses[T][1], '決済到達', ses[T][2], '完了', ses[T][3], '／11/10', ses['2026-11-10'], '／11/4', ses['2026-11-04'], '注文', bands['2026-11-04'])
print('帯 11/11', bands[T], '11/10', bands['2026-11-10'], '11/4', bands['2026-11-04'])
M = collections.defaultdict(lambda: [0] * 6)
for l in open(O + 'meta_camp_1110_1111_raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    for i in range(6): M[p[0]][i] += int(p[2 + i])
for d, v in sorted(M.items()):
    print(f"Meta {d}: 広告{v[0]:,} 表示{v[1]:,} クリック{v[2]:,} LPV{v[3]:,} カート{v[4]} 購入{v[5]} ／ CPM{v[0]/v[1]*1000:,.0f} CTR{v[2]/v[1]*100:.2f}% 1LPV{v[0]/v[3]:.1f}円 カート÷LPV{v[4]/v[3]*100:.2f}%")
print('広告セット別（11/11・Meta計上）')
for l in open(O + 'adsets_1111_raw.txt'):
    if l[0] in '#[': continue
    p = l.strip().split(',')
    if p[0] in ('伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー'):
        c = int(p[4]); n = int(p[5]) if p[5] != 'null' else 0
        print(f"  {p[1]}: {c:,}円・{n}件・CPA{c/n:,.0f}" if n else f"  {p[1]}: {c:,}円・0件")
A = g['A']; W_ = g['WIN']; agg = g['agg']
for n in ['防風あったか裏起毛パンツ', 'すき間収納シートポケット', 'コードレスダブルミスト加湿器']:
    for l in open(O + 'meta_camp_1110_1111_raw.txt'):
        p = l.strip().split(',')
        if p[0] == T and p[1] == n: print(f"  {n}: 広告{int(p[2]):,} 表示{int(p[3]):,} クリック{p[4]} CTR{int(p[4])/int(p[3])*100:.2f}% LPV{p[5]} カート{p[6]} Meta購入{p[7]}")
print('終日の合計予算（各日の最後のスナップショット）')
snap = collections.OrderedDict()
for r in list(csv.reader(open('data/budget-snapshots.csv')))[1:]:
    if r: snap.setdefault(r[0], []).append(int(r[3]))
for d in ['2026-11-09', '2026-11-10', '2026-11-11']:
    ks = [k for k in snap if k[:10] == d]; print(' ', d, ks[-1], len(snap[ks[-1]]), 'セット', sum(snap[ks[-1]]))
