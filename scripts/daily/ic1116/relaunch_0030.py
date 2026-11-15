# -*- coding: utf-8 -*-
"""出し直し（14日以上 広告費0 → 再開）の成績を、今回の3本（新キャンペーン・新しい広告）と過去の出し直しで並べる。
実測のみ: 売上・原価は w1115.py の積み直し関数（data/daily の Shopify 実測）、広告費は data/daily/daily_ad.csv（Meta 実測）。
倍率 =（実売−原価）÷ 広告費。再開1〜2日目／1〜7日目／8〜21日目、止める前の14日（広告費>0 の最後の日から遡る14日）。"""
import io, contextlib, collections, datetime, statistics as st
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1115.py').read(), g)
WIN, agg, ALLD, AD, MAP, MULTI = g['WIN'], g['agg'], g['ALLD'], g['AD'], g['MAP'], g['MULTI']
def W(days):
    key = 'r' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
inv = collections.defaultdict(set)
for n, c in MAP.items(): inv[c].add(n)
for n, cs in MULTI.items():
    for c in cs: inv[c].add(n)
def prod_of(c):
    if c in inv: return sorted(inv[c])[0]
    if c in g['S']: return c
    return None
# 商品ごとの日別広告費（その商品の全キャンペーン）
PA = collections.defaultdict(lambda: collections.defaultdict(float))
for c, v in AD.items():
    n = prod_of(c)
    if n is None: continue
    for d, x in v.items(): PA[n][d] += x
def mult(n, days):
    a = sum(PA[n].get(d, 0) for d in days)
    if not a: return None, 0, 0, 0
    N, Q, K = W(days); s = N.get(n, 0); k = K.get(n, 0)
    return (s - k) / a, s - k - a, Q.get(n, 0), a
dd = lambda d, k: (datetime.date.fromisoformat(d) + datetime.timedelta(k)).isoformat()
rows = []
for n, v in PA.items():
    days_on = sorted(d for d, x in v.items() if x > 0 and d <= ALLD[-1])
    for i, d in enumerate(days_on):
        if i == 0: continue
        gap = (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(days_on[i - 1])).days - 1
        if gap < 14: continue
        prev_end = days_on[i - 1]
        pre = [x for x in ALLD if dd(prev_end, -13) <= x <= prev_end]
        r12 = [x for x in ALLD if d <= x <= dd(d, 1)]
        r7 = [x for x in ALLD if d <= x <= dd(d, 6)]
        r821 = [x for x in ALLD if dd(d, 7) <= x <= dd(d, 20)]
        new_camp = any(c for c in AD if prod_of(c) == n and AD[c].get(d, 0) > 0 and not any(AD[c].get(x, 0) for x in ALLD if x < d))
        rows.append((n, d, gap, new_camp, mult(n, pre), mult(n, r12), mult(n, r7), mult(n, r821), len(r7), len(r821)))
f = lambda m: '—' if m[0] is None else f'{m[0]:.2f}'
print('商品 ／ 再開日（休んだ日数）／ 新キャンペーン ／ 止める前14日 倍率（広告費）／ 1〜2日目 倍率・個数・広告費 ／ 1〜7日目 倍率・利益・広告費 ／ 8〜21日目 倍率・広告費')
for r in sorted(rows, key=lambda r: r[1]):
    n, d, gap, nc, pre, a12, a7, a821, l7, l821 = r
    print(f'  {n} ／ {d}（{gap}日）／ {"新" if nc else "既存"} ／ {f(pre)}（{pre[3]:,.0f}）／ {f(a12)}・{a12[2]}個・{a12[3]:,.0f} ／ {f(a7)}・{a7[1]:+,.0f}・{a7[3]:,.0f}（{l7}日）／ {f(a821)}（{a821[3]:,.0f}・{l821}日）')
# 1〜2日目の広告費が 4,000円以上の出し直しだけで比べる（数時間で止めたものを除く）
real = [r for r in rows if r[5][3] >= 4000]
print('\n1〜2日目に広告費 4,000円以上使った出し直し:', len(real), '件')
past = [r for r in real if r[1] < '2026-11-14']
cur = [r for r in real if r[1] >= '2026-11-14']
for lab, rs in [('過去', past), ('今回（11/14〜）', cur)]:
    xs = [r[5][0] for r in rs if r[5][0] is not None]
    if xs: print(f'  {lab}: 1〜2日目の倍率 中央値 {st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}）・1.86以上 {sum(x>=1.86 for x in xs)}/{len(xs)}')
for lab, rs in [('過去', past)]:
    pairs = [(r[5][0], r[6][0], r[7][0]) for r in rs if r[5][0] is not None and r[6][0] is not None]
    print(f'  {lab}: 1〜2日目 → 1〜7日目 → 8〜21日目 の倍率（中央値） {st.median([p[0] for p in pairs]):.2f} → {st.median([p[1] for p in pairs]):.2f} → {st.median([p[2] for p in pairs if p[2] is not None]):.2f}')
    hi = [p for p in pairs if p[0] >= 1.86]
    if hi: print(f'  過去で 1〜2日目が 1.86以上だった {len(hi)}件: 1〜7日目 ' + '・'.join(f'{p[1]:.2f}' for p in hi) + ' ／ 8〜21日目 ' + '・'.join('—' if p[2] is None else f'{p[2]:.2f}' for p in hi))
# ---- 14日の休みの条件に入らない今回の2本（ノーズ: 6/29 以降 広告なし／フック: 11/3 で止め、11/11・12 に既存キャンペーンで短く再開）----
print('\n今回の残り2本と、フックの 11/11・12（既存キャンペーンでの短い再開）')
for n, lab, ds in [('スマートノーズEMS美顔器', 'ノーズEMS v2（11/14〜・新キャンペーン）', ['2026-11-14', '2026-11-15']),
                   ('高見えレザーヘッドレストフック', 'フック v2（11/15・新キャンペーン）', ['2026-11-15']),
                   ('高見えレザーヘッドレストフック', 'フック 既存キャンペーン（11/11〜12）', ['2026-11-11', '2026-11-12']),
                   ('高見えレザーヘッドレストフック', 'フック 止める前14日（10/21〜11/3）', [x for x in ALLD if '2026-10-21' <= x <= '2026-11-03']),
                   ('携帯電動シェーバー', 'シェーバー 9/18 再開の1〜2日目（既存）', ['2026-09-18', '2026-09-19'])]:
    m = mult(n, ds); print(f'  {lab}: 倍率 {f(m)}・{m[2]}個・広告 {m[3]:,.0f}・利益 {m[1]:+,.0f}')
