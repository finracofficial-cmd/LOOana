# -*- coding: utf-8 -*-
"""11/19 CPM が上がった中身（終日の数字。11/19 は 13時ごろまでの途中）。基準＝11/12〜16 の5日、比べる日＝11/17・11/18・11/19。
①同じ商品の中で: 年齢の配分が変わった分（配分）と、同じ年齢の中で単価が上がった分（単価）に分ける ②配信面（Instagram/Facebook の面）でも同じ分け方
表示÷広告費（ipy）＝Σ 広告費の割合 × その層の ipy。cost > 300 の行だけ（小さい行は入っていない）"""
import collections
R = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])))   # R[camp][date][age]
for l in open('age_raw.txt'):
    if l[0] == '#': continue
    d, c, a, cost, imp = l.strip().split(','); R[c][d][a] = [int(cost), int(imp)]
BASE = ['2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16']
def pool(c, days):
    out = collections.defaultdict(lambda: [0, 0])
    for d in days:
        for a, (x, y) in R[c].get(d, {}).items(): out[a][0] += x; out[a][1] += y
    return out
def decomp(b, t):
    bc = sum(v[0] for v in b.values()); bi = sum(v[1] for v in b.values()); tc = sum(v[0] for v in t.values()); ti = sum(v[1] for v in t.values())
    if not bc or not tc or not ti or not bi: return None
    mix = within = 0
    for a in set(b) | set(t):
        wb = b[a][0] / bc if a in b else 0; wt = t[a][0] / tc if a in t else 0
        ib = b[a][1] / b[a][0] if a in b and b[a][0] else None; it = t[a][1] / t[a][0] if a in t and t[a][0] else None
        if ib is None: ib = it
        if it is None: it = ib
        mix += (wt - wb) * ib; within += wt * (it - ib)
    ipb = bi / bc
    return bc / bi * 1000, tc / ti * 1000, 1000 / (ipb + mix), 1000 / (ipb + within)
ALLC = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for c in R:
    for d in R[c]:
        for a, (x, y) in R[c][d].items(): ALLC[d][a][0] += x; ALLC[d][a][1] += y
R['（全商品）'] = ALLC
OLD = lambda p: sum(v[0] for a, v in p.items() if a in ('55-64', '65+')) / sum(v[0] for v in p.values())
print('■ 年齢で分ける: CPM 基準（11/12〜16）→ その日 ｜ 年齢の配分だけ変わった場合 ／ 同じ年齢の中の単価だけ変わった場合 ｜ 55歳以上の広告費の割合')
for c in ('（全商品）', 'ナノガラス脱毛パッド', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ワイド水切りワイパー', '4-in-1マルチクリーナー', 'マグネットドアクッション', 'カタログ全部（テスト）'):
    b = pool(c, BASE)
    for d in ('2026-11-17', '2026-11-18', '2026-11-19'):
        t = pool(c, [d]); r = decomp(b, t)
        if not r: continue
        print(f"  {c} {d[5:]}: {r[0]:,.0f} → {r[1]:,.0f}（{r[1]/r[0]-1:+.0%}）｜ 配分 {r[2]:,.0f}（{r[2]/r[0]-1:+.0%}）／ 単価 {r[3]:,.0f}（{r[3]/r[0]-1:+.0%}）｜ 55歳以上 {OLD(b):.0%} → {OLD(t):.0%}")
print('■ ナノ: 年齢ごとの CPM（基準 → 11/17 → 11/18 → 11/19）と広告費の割合')
b = pool('ナノガラス脱毛パッド', BASE); bc = sum(v[0] for v in b.values())
for a in sorted(b):
    s = f"  {a}: 基準 {b[a][0]/b[a][1]*1000:,.0f}（{b[a][0]/bc:.0%}）"
    for d in ('2026-11-17', '2026-11-18', '2026-11-19'):
        t = pool('ナノガラス脱毛パッド', [d]); tc = sum(v[0] for v in t.values())
        if a in t: s += f" → {t[a][0]/t[a][1]*1000:,.0f}（{t[a][0]/tc:.0%}）"
    print(s)
# ② 配信面
PL = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for l in open('place_raw.txt'):
    if l[0] == '#': continue
    d, p, q, cost, imp = l.strip().split(','); PL[d][q] = [int(cost), int(imp)]
def poolp(days):
    out = collections.defaultdict(lambda: [0, 0])
    for d in days:
        for a, (x, y) in PL[d].items(): out[a][0] += x; out[a][1] += y
    return out
print('■ 配信面で分ける（全商品）: CPM 基準 → その日 ｜ 面の配分だけ ／ 同じ面の中の単価だけ')
b = poolp(BASE)
for d in ('2026-11-17', '2026-11-18', '2026-11-19'):
    r = decomp(b, poolp([d])); print(f"  {d[5:]}: {r[0]:,.0f} → {r[1]:,.0f}（{r[1]/r[0]-1:+.0%}）｜ 配分 {r[2]:,.0f}（{r[2]/r[0]-1:+.0%}）／ 単価 {r[3]:,.0f}（{r[3]/r[0]-1:+.0%}）")
print('  面ごとの CPM（基準 → 11/18 → 11/19）: ' + '・'.join(f"{q} {b[q][0]/b[q][1]*1000:,.0f}→{PL['2026-11-18'][q][0]/PL['2026-11-18'][q][1]*1000:,.0f}→{PL['2026-11-19'][q][0]/PL['2026-11-19'][q][1]*1000:,.0f}" for q in ('feed', 'instagram_reels', 'instagram_stories', 'facebook_reels', 'threads_feed') if q in PL['2026-11-19']))
