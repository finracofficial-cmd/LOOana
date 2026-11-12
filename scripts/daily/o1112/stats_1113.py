# -*- coding: utf-8 -*-
"""11/13 定例の本文用の数字（店の来訪・購入率・決済・客単価・注文帯・Metaのカート÷LPV・CPM）。入力: o1112 の取得ファイル・o1111/sess_1027_1111_raw.txt・日次CSV"""
import json, csv, collections, statistics as st
O = 'scripts/daily/o1112/'
S = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(O + 'sess_1028_1112_raw.json'))['rows']}
G = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open('data/daily/daily_sales.csv')): G[r['date']][0] += int(r['gross']); G[r['date']][1] += int(r['disc'])
B = {r['date']: r for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
D15 = sorted(S)[-15:]; assert D15[-1] == '2026-11-12' and D15[0] == '2026-10-29'
cvr = {d: int(B[d]['orders']) / S[d][0] for d in D15}; comp = {d: S[d][3] / S[d][2] for d in D15}; cart = {d: S[d][1] / S[d][0] for d in D15}
T, P, Y = '2026-11-12', '2026-11-05', '2026-11-11'
f = lambda x: f'{x*100:.2f}%'
print(f"セッション {S[T][0]:,}（前週木 {S[P][0]:,}・前日 {S[Y][0]:,}・15日 {min(S[d][0] for d in D15):,}〜{max(S[d][0] for d in D15):,}・下から{sorted(S[d][0] for d in D15).index(S[T][0])+1}番目）")
print(f"CVR {f(cvr[T])}（前週木 {f(cvr[P])}・前日 {f(cvr[Y])}・15日 {f(min(cvr.values()))}〜{f(max(cvr.values()))}）")
print(f"カゴ投入率 {f(cart[T])}（{S[T][1]}/{S[T][0]}・15日 {f(min(cart.values()))}〜{f(max(cart.values()))}）")
print(f"決済完了率 {comp[T]*100:.1f}%（{S[T][3]}/{S[T][2]}・前日 {comp[Y]*100:.1f}%・15日 {min(comp.values())*100:.1f}〜{max(comp.values())*100:.1f}%）")
net = {d: G[d][0] - G[d][1] for d in G}
aov = {d: net[d] / int(B[d]['orders']) for d in D15}
print(f"客単価 {aov[T]:,.0f}（前週木 {aov[P]:,.0f}・前日 {aov[Y]:,.0f}・15日 {min(aov.values()):,.0f}〜{max(aov.values()):,.0f}）・値引 {G[T][1]:,}（gross比 {G[T][1]/G[T][0]*100:.1f}%・前日 {G[Y][1]/G[Y][0]*100:.1f}%・前週木 {G[P][1]/G[P][0]*100:.1f}%）")
for d in (T, P, Y): print(f"  注文帯 {d[5:]}: {B[d]['orders']}件・7,000円以上 {B[d]['ge7000']}（{int(B[d]['ge7000'])/int(B[d]['orders'])*100:.1f}%）・8,000円以上 {B[d]['ge8000']}・10,000円以上 {B[d]['ge10000']}")
M = collections.defaultdict(lambda: [0] * 6)
for l in open(O + 'meta_camp_1111_1112_raw.txt'):
    p = l.strip().split(',')
    if len(p) > 7 and p[0][:2] == '20':
        for j, x in enumerate(p[2:8]): M[p[0]][j] += int(x)
for d in (Y, T):
    c, i, cl, lpv, atc, pu = M[d]
    print(f"Meta {d[5:]}: 広告 {c:,}・CPM {c/i*1000:,.0f}・CTR {cl/i*100:.2f}%・1クリック {c/cl:.0f}円・カート÷LPV {atc/lpv*100:.2f}%（{atc}/{lpv}）・購入 {pu}")
