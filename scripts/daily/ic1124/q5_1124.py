# -*- coding: utf-8 -*-
"""11/24 10時台「卓上加湿器ってどっち？なんで追加？／ドア・UV2・毛玉V2・ノーズV2はどうすれば／洗車ブラシを出し直すべき？」
商品ごとの日別: 広告費・クリック・クリック1回・クリック1回の粗利・注文（個数）・倍率。洗車ブラシは週ごと（日曜はじまり）。
入力: w1123.py（売上・原価・広告費）・o1123/ad_level_1026_1123.txt（リンククリック）"""
import io, contextlib, collections, datetime
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, MAP, MULTI = g['A'], g['ALLD'], g['agg'], g['WIN'], g['MAP'], g['MULTI']
CL = collections.defaultdict(lambda: collections.defaultdict(int))
for l in open('scripts/daily/o1123/ad_level_1026_1123.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(','); CL[c][d] += int(clk)
camps = lambda n: MULTI.get(n, (MAP.get(n, n),))
def one(n, ds, key):
    WIN[key] = ds; N, DC, Q, K = agg(ds, key); a = A(ds, n); k = sum(CL[c][d] for c in camps(n) for d in ds); gp = N.get(n, 0) - K.get(n, 0)
    return a, k, gp, Q.get(n, 0)
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
for n, st in (('充電式ダブルミスト卓上加湿器', '2026-11-19'), ('コードレス毛玉クリーナー', '2026-11-22'), ('UV歯ブラシ除菌器', '2026-11-22'), ('マグネットドアクッション', '2026-11-17'), ('スマートノーズEMS美顔器', '2026-11-17')):
    P(f'■ {n}（日別: 広告費・クリック・クリック1回 ↔ クリック1回の粗利・個数・倍率）')
    ds_all = [d for d in ALLD if d >= st]
    for d in ds_all + ['計']:
        ds = ds_all if d == '計' else [d]; a, k, gp, q = one(n, ds, 'q' + d)
        if not a: continue
        P(f"  {d if d == '計' else d[5:]}: {a:,.0f}円・{k}クリック・{a/k:.0f}円 ↔ {gp/k:.0f}円・{q}個・{gp/a:.2f}")
P('■ 伸縮ワックス洗車ブラシ（週ごと・日曜はじまり。クリックは 10/26 から）')
for s0 in ['2026-10-26', '2026-11-02', '2026-11-09', '2026-11-16']:
    ds = [d for d in ALLD if s0 <= d <= (datetime.date.fromisoformat(s0) + datetime.timedelta(6)).isoformat()]
    a, k, gp, q = one('伸縮ワックス洗車ブラシ', ds, 'b' + s0)
    if a: P(f'  {s0[5:]}〜: 広告費 {a/len([d for d in ds if A([d], "伸縮ワックス洗車ブラシ")]):,.0f}円/日・{k}クリック・{a/k:.0f}円 ↔ {gp/k:.0f}円・{q}個・{gp/a:.2f}')
open('scripts/daily/ic1124/q5_1124.txt', 'w').write('\n'.join(out) + '\n')
