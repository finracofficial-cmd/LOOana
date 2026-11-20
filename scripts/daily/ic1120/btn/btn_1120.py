# -*- coding: utf-8 -*-
"""11/20 朝: 「商品を選ぶ」ボタン（11/19 15:15ごろ・スマホだけ）を入れてからの買う率を、同じ時間帯の過去と比べる。
入れた後＝11/19 の 16〜23時台 ＋ 11/20 の 0〜8時台（スマホ）。前＝同じ時間帯の 10/29〜11/18（0〜8時台は 11/19 も前）。入力は raw.txt だけ。日中の数字なので予算の判断には使わない"""
import math, os, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
R = collections.defaultdict(dict)
for l in open(D + 'raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] in 'AB': R[(p[0], p[2])][p[1]] = [int(x) for x in p[3:]]
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
out = []
AFTER = {'A': ['2026-11-19'], 'B': ['2026-11-20']}
tot_a = [0, 0, 0, 0]; exp_done = exp_cart = 0
for blk, lab in (('A', '16〜23時台'), ('B', '0〜8時台')):
    v = R[(blk, 'mobile')]; aft = AFTER[blk]; bef = [d for d in v if d not in aft]
    s0 = sum(v[d][0] for d in bef); c0 = sum(v[d][1] for d in bef); k0 = sum(v[d][2] for d in bef); d0 = sum(v[d][3] for d in bef)
    a = [sum(v[d][i] for d in aft) for i in range(4)]
    rates = sorted(v[d][3] / v[d][0] for d in bef); carts = sorted(v[d][1] / v[d][0] for d in bef)
    hi = sum(1 for x in rates if x >= a[3] / a[0]); hic = sum(1 for x in carts if x >= a[1] / a[0])
    e = a[0] * d0 / s0; ec = a[0] * c0 / s0
    out.append(f'■ スマホ・{lab}')
    out.append(f'  前（{len(bef)}日）: カート率 {c0/s0:.2%}・買う率 {d0/s0:.2%}・完了÷決済画面 {d0/k0:.0%}（買う率の日ごとの幅 {rates[0]:.2%}〜{rates[-1]:.2%}）')
    out.append(f'  後（{aft[0][5:]}）: 来訪 {a[0]}・カート追加 {a[1]}（{a[1]/a[0]:.2%}）・購入 {a[3]}（{a[3]/a[0]:.2%}）・完了÷決済画面 {a[3]/a[2]:.0%}')
    out.append(f'    購入: 見込み {e:.1f}件 → {a[3]}件。これ以上になる確率 {pge(a[3], e):.0%}・過去{len(bef)}日のうち買う率がこれ以上だった日 {hi}日')
    out.append(f'    カート追加: 見込み {ec:.1f}件 → {a[1]}件。これ以上になる確率 {pge(a[1], ec):.0%}・カート率がこれ以上だった日 {hic}日')
    for i in range(4): tot_a[i] += a[i]
    exp_done += e; exp_cart += ec
out.append('■ 入れてからの合計（スマホ・11/19 16時台〜11/20 8時台）')
out.append(f'  来訪 {tot_a[0]}・カート追加 {tot_a[1]}（{tot_a[1]/tot_a[0]:.2%}・見込み {exp_cart:.1f}・これ以上 {pge(tot_a[1], exp_cart):.0%}）・購入 {tot_a[3]}（{tot_a[3]/tot_a[0]:.2%}・見込み {exp_done:.1f}・これ以上 {pge(tot_a[3], exp_done):.1%}）')
out.append(f'  差の大きさ: 購入 {tot_a[3]/exp_done-1:+.0%}。この件数で偶然に出る幅は ±{2/math.sqrt(exp_done):.0%} くらい')
v = R[('A', 'desktop')]; bef = [d for d in v if d != '2026-11-19']
out.append(f"■ PC（ボタンは出ない）16〜23時台: 前 来訪 {sum(v[d][0] for d in bef)}・購入 {sum(v[d][3] for d in bef)} ／ 11/19 来訪 {v['2026-11-19'][0]}・購入 {v['2026-11-19'][3]} → 件数が小さく、比べる相手にならない")
open(D + 'btn_1120.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
