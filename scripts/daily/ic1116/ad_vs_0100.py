# -*- coding: utf-8 -*-
"""同じ広告セットに広告が2本ある所で、片方が明らかに悪いか（止めるべきか）。11/13〜15 の Meta 購入を広告費の比で分けたときの期待と比べる（二項・片側）。
入力: ic1116/ad_purchase_0100.txt（Meta 実測）。購入は Meta の帰属なので、広告どうしの比べにだけ使う"""
import collections, math
G = collections.defaultdict(list)
for l in open('scripts/daily/ic1116/ad_purchase_0100.txt'):
    if l[0] == '#': continue
    c, a, ad, cost, clk, atc, pur = l.strip().split(','); G[(c, a)].append((ad, int(cost), int(clk), int(atc), int(pur)))
def binom_tail(k, n, p, upper):
    pr = lambda i: math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    return sum(pr(i) for i in (range(k, n + 1) if upper else range(0, k + 1)))
for k, v in G.items():
    if len(v) < 2: continue
    v.sort(key=lambda x: -x[1]); (a1, c1, k1, t1, p1), (a2, c2, k2, t2, p2) = v[:2]
    n = p1 + p2; s = c2 / (c1 + c2); e = n * s
    up = p2 >= e; pv = binom_tail(p2, n, s, up) if n else 1
    v_ = '偶然の範囲内' if pv > 0.16 else ('偶然でも起きるが端' if pv > 0.025 else '偶然では起きにくい')
    f = lambda ad, c, k_, t, p: f'{ad} {c:,}円・クリック{k_}・カート{t}・購入{p}（{c/p:,.0f}円/件）' if p else f'{ad} {c:,}円・クリック{k_}・カート{t}・購入0'
    print(f'{k[1]}: {f(a1,c1,k1,t1,p1)} ／ {f(a2,c2,k2,t2,p2)} → {a2} の購入 {p2}（広告費の比なら {e:.1f}）・{"多い" if up else "少ない"}側 {pv:.0%} ＝ {v_}')
