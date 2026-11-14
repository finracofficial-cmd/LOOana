# -*- coding: utf-8 -*-
"""11/14 21:5x 「朝昼夜で大きくぶれるのが謎」
朝（0〜8時台）・昼（9〜17時台）・夜（18〜23時台）の購入率（決済完了セッション÷セッション）の「一番高い帯÷一番低い帯」を、
過去29日（10/15〜11/13・祝日11/3除く）で数え、買う確率が一日中同じでも出る幅（シミュレーション）と比べる。今日は21時台途中まで。"""
import json, random, collections, math
D = 'scripts/daily/ic1114/'
n = collections.defaultdict(int); c = collections.defaultdict(int)
for d, h, s, a, r, done in json.load(open(D + 'sess_hourly_1015_1113.json'))['rows']:
    if d == '2026-11-03': continue
    n[d, int(h)] = int(s); c[d, int(h)] = int(done)
days = sorted({k[0] for k in n}); assert len(days) == 29
B = [range(0, 9), range(9, 18), range(18, 24)]
P = sum(c.values()) / sum(n.values())
def spread(ns, cs):
    r = [sum(cs[h] for h in b) / sum(ns[h] for h in b) for b in B]
    return max(r) / min(r) if min(r) > 0 else float('inf'), r
real = {}
for d in days:
    real[d] = spread({h: n[d, h] for h in range(24)}, {h: c[d, h] for h in range(24)})
T = {int(r[0]): (int(r[1]), int(r[4])) for r in json.load(open(D + 'sess_hour_1114_1938.json'))['rows']} if False else None
# 今日（21:38 取得の時間帯別。18〜21時台）
tn = [65,44,33,37,50,51,80,178,160,174,161,122,116,114,99,107,118,129,118,125,136,81] + [0, 0]
tc = [3,1,0,0,0,1,1,4,1,7,6,6,2,3,5,9,3,2,1,1,2,2] + [0, 0]
ts, tr = spread(dict(enumerate(tn)), dict(enumerate(tc)))
print(f'■ 今日: 朝 {tr[0]:.2%}・昼 {tr[1]:.2%}・夜 {tr[2]:.2%} → 一番高い帯÷一番低い帯 {ts:.1f}倍')
xs = sorted(v[0] for v in real.values())
print(f'■ 過去29日の「高い帯÷低い帯」: 中央値 {xs[14]:.2f}倍・最大 {xs[-1]:.2f}倍・今日（{ts:.1f}倍）以上の日 {sum(x >= ts for x in xs)}/29・2倍以上の日 {sum(x >= 2 for x in xs)}/29')
for d in sorted(real, key=lambda d: -real[d][0])[:5]:
    s, r = real[d]; print(f'  {d}: 朝 {r[0]:.2%}・昼 {r[1]:.2%}・夜 {r[2]:.2%} → {s:.2f}倍')
# 買う確率が一日中・毎日同じ（P）でも出る幅（同じ来訪数で）
random.seed(1114); sim = []
def binom(k, p):
    return sum(1 for _ in range(k) if random.random() < p)
for _ in range(300):
    for d in days:
        sim.append(spread({h: n[d, h] for h in range(24)}, {h: binom(n[d, h], P) for h in range(24)})[0])
sim.sort()
print(f'■ 買う確率が一日中同じでも（シミュレーション 300×29日）: 中央値 {sim[len(sim)//2]:.2f}倍・2倍以上になる日の割合 {sum(x >= 2 for x in sim)/len(sim):.0%}・今日（{ts:.1f}倍）以上 {sum(x >= ts for x in sim)/len(sim):.1%}')
