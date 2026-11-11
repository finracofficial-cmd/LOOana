# -*- coding: utf-8 -*-
"""11/12 00時台: スリッパ・ディスペンサーなど停止商品の配信期間（ラン）ごとの実績と月別の倍率（CSV実測・6/29〜11/11・読み取りのみ）。
定義は revive_multi.py と同じ（ラン=広告費500円以上の日の連なり・3日以上空いたら別のラン）。"""
import io, contextlib, datetime, collections, sys
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1111.py').read(), g)
WIN, ALLD, MAP, AD, S = g['WIN'], g['ALLD'], g['MAP'], g['AD'], g['S']
D = lambda s: datetime.date.fromisoformat(s)
def W(days, n):
    key = 'd' + n + days[0] + days[-1] + str(len(days)); WIN[key] = days
    sal = sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
    q, k = g['qty'](n, days, key)
    return sal, k, q
for n in sys.argv[1:]:
    c = MAP.get(n, n)
    days = sorted(d for d in AD[c] if AD[c][d] >= 500 and d in ALLD)
    print(f'■ {n}（キャンペーン: {c}）広告の出た日 {len(days)}日')
    if not days: continue
    rs = [[days[0]]]
    for d in days[1:]:
        if (D(d) - D(rs[-1][-1])).days >= 3: rs.append([d])
        else: rs[-1].append(d)
    for r in rs:
        span = [d for d in ALLD if r[0] <= d <= r[-1]]
        s, k, q = W(span, n); a = sum(AD[c].get(d, 0) for d in span)
        print(f'  配信 {r[0][5:]}〜{r[-1][5:]}（{len(r)}日）広告{a:,.0f}・{q}個・倍率{(s-k)/a:.2f}・利益{s-k-a:+,.0f}')
    bym = collections.defaultdict(list)
    for d in ALLD:
        if days[0] <= d <= days[-1]: bym[d[:7]].append(d)
    for m, ds in sorted(bym.items()):
        a = sum(AD[c].get(d, 0) for d in ds)
        if a < 500: continue
        s, k, q = W(ds, n)
        print(f'  {m}: 広告{a:,.0f}・{q}個・倍率{(s-k)/a:.2f}・利益{s-k-a:+,.0f}・広告1日あたり{a/len([d for d in ds if AD[c].get(d,0)>=500]):,.0f}')
    # 広告を止めたあとの売れ方（広告なしで売れた個数）
    after = [d for d in ALLD if d > days[-1]]
    if after:
        s, k, q = W(after, n); print(f'  広告を止めたあと {after[0][5:]}〜{after[-1][5:]}（{len(after)}日）: {q}個・実売{s:,.0f}')
