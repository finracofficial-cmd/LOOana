# -*- coding: utf-8 -*-
"""11/05 08:0x: 今日の朝（0〜6時台）の配信と来訪後を、過去7日（10/29〜11/4）の同じ時間帯と比べる。Shopifyは0〜7時台も見る。Metaの7時台は今日分のLPVが未着地のため使わない"""
import os, math, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'
M = {}; S = {}; O = {}
for l in open(D + 'meta_h_0007.txt'):
    if l[0] == '#': continue
    d, *hs = l.strip().split('|'); M[d] = [list(map(int, h.split(','))) for h in hs]; assert len(M[d]) == 8
for l in open(D + 'shop_h_0007.txt'):
    if l[0] == '#': continue
    k, d, *hs = l.strip().split('|')
    for h in hs:
        x = list(map(int, h.split(':')))
        (S if k == 'S' else O).setdefault(d, {})[x[0]] = x[1:]
assert sum(v[0] for v in O['2026-11-04'].values()) == 14   # 11/4 0〜7時台の注文（h1104/shop.txt の0〜7時台合計と同じ）
DAYS = sorted(M); T = '2026-11-05'; P = [d for d in DAYS if d < T]
def cut(d, H):
    m = [sum(M[d][h][i] for h in range(H)) for i in range(5)]
    s = [sum(S[d].get(h, [0, 0, 0, 0])[i] for h in range(H)) for i in range(4)]
    o = sum(O[d].get(h, [0, 0])[0 + 0] for h in range(H)); g = sum(O[d].get(h, [0, 0])[1] for h in range(H))
    return m, s, o, g
def show(lab, f, H, fm='{:,.0f}'):
    t = f(*cut(T, H)); xs = [f(*cut(d, H)) for d in P]
    print(f'  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値 {fm.format(st.median(xs))}・{fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日 {sum(x < t for x in xs)}/7')
print('■ 0〜6時台（Meta・Shopifyとも）')
show('広告費', lambda m, s, o, g: m[0], 7)
show('CPM', lambda m, s, o, g: m[0] / m[1] * 1000, 7)
show('CTR(%)', lambda m, s, o, g: m[2] / m[1] * 100, 7, '{:.2f}')
show('LPV', lambda m, s, o, g: m[3], 7)
show('1LPVあたり広告費', lambda m, s, o, g: m[0] / m[3], 7, '{:.1f}')
show('来訪(Shopify)', lambda m, s, o, g: s[0], 7)
show('注文', lambda m, s, o, g: o, 7)
show('来訪→購入(%)', lambda m, s, o, g: o / s[0] * 100, 7, '{:.2f}')
show('カゴ投入率(%)', lambda m, s, o, g: s[1] / s[0] * 100, 7, '{:.2f}')
print('■ 0〜7時台（Shopifyのみ・8:00まで）')
show('来訪', lambda m, s, o, g: s[0], 8); show('注文', lambda m, s, o, g: o, 8)
show('来訪→購入(%)', lambda m, s, o, g: o / s[0] * 100, 8, '{:.2f}'); show('カゴ投入率(%)', lambda m, s, o, g: s[1] / s[0] * 100, 8, '{:.2f}')
show('gross', lambda m, s, o, g: g, 8)
# 今日の来訪数に過去7日の同時刻の購入率を当てたときの注文数と、この数以下になる確率
for H in (7, 8):
    _, s, o, _ = cut(T, H); r = sum(cut(d, H)[2] for d in P) / sum(cut(d, H)[1][0] for d in P); lam = s[0] * r
    pk = sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(o + 1))
    print(f'  0〜{H-1}時台: 来訪{s[0]}×過去7日の購入率{r*100:.2f}% = {lam:.1f}件 → 実際{o}件・この数以下 {pk*100:.0f}%')
