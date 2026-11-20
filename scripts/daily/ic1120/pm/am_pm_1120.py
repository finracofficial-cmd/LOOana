# -*- coding: utf-8 -*-
"""11/20 「たまたまかな？午前めっちゃ良かったのに」: 朝（0〜10時台）が良い日は午後（11〜16時台）が悪くなるのか、を過去21日で見る。
入力は ../h11/raw.txt（0〜10時台）と ../h17/raw.txt（0〜16時台）の S 行（来訪・カート・決済画面・購入）"""
import os, math, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__))
def S(path):
    return {p[1]: [int(x) for x in p[2:]] for p in (l.strip().split(',') for l in open(path) if l.startswith('S,'))}
a = S(os.path.join(D0, '..', 'h11', 'raw.txt')); b = S(os.path.join(D0, '..', 'h17', 'raw.txt'))
TD = '2026-11-20'; days = sorted(d for d in a if d in b)
am = {d: a[d][3] / a[d][0] for d in days}; pm = {d: (b[d][3] - a[d][3]) / (b[d][0] - a[d][0]) for d in days}
past = [d for d in days if d < TD]; assert len(past) == 21
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
P('■ 朝（0〜10時台）と午後（11〜16時台）の買う率・過去21日＋今日')
for d in days: P(f'  {d[5:]}: 朝 {am[d]:.2%}・午後 {pm[d]:.2%}')
xs = [am[d] for d in past]; ys = [pm[d] for d in past]; mx, my = st.mean(xs), st.mean(ys)
r = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
P(f'  過去21日の相関（朝の買う率 と 午後の買う率）: {r:+.2f}（−1 に近いほど「朝が良いと午後が悪い」・0 は無関係。21日だと ±0.43 の内側は偶然と区別できない）')
top = sorted(past, key=lambda d: -am[d])[:7]; bot = sorted(past, key=lambda d: am[d])[:7]
P(f'  朝が良かった7日の午後: 平均 {st.mean(pm[d] for d in top):.2%}（' + '・'.join(f'{d[5:]} {pm[d]:.2%}' for d in top) + '）')
P(f'  朝が悪かった7日の午後: 平均 {st.mean(pm[d] for d in bot):.2%}（' + '・'.join(f'{d[5:]} {pm[d]:.2%}' for d in bot) + '）')
P(f'  今日: 朝 {am[TD]:.2%}（21日の最高 {max(xs):.2%} より上）・午後 {pm[TD]:.2%}（21日の最低 {min(ys):.2%}）・0〜16時台 {b[TD][3]/b[TD][0]:.2%}（21日の中央値 {st.median(b[d][3]/b[d][0] for d in past):.2%}）')
open(os.path.join(D0, 'am_pm_1120.txt'), 'w').write('\n'.join(L) + '\n')
