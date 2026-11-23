# -*- coding: utf-8 -*-
"""11/24 定例: 同じキャンペーンの中での CPM（直近7日 11/17〜23 ↔ その前の7日 11/10〜16）と、新しい3本（毛玉 v2・UV v2・レインガード v2）の2日目の判定用の数字。入力は o1123/ad_level_1026_1123.txt と ad_purchase_1122_1123.txt（Meta のカート・購入は meta_ad_1123_raw.json）"""
import collections, os, json
D0 = os.path.dirname(os.path.abspath(__file__)); R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(os.path.join(D0, 'ad_level_1026_1123.txt')):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
out = ['■ 同じキャンペーンの中での CPM: その前の7日（11/10〜16）→ 直近7日（11/17〜23）｜11/23 の1日（11/23 に広告費が出たもの）']
def agg(c, a, b): v = [x for d, x in R[c].items() if a <= d <= b]; return sum(x[0] for x in v), sum(x[1] for x in v), sum(x[2] for x in v)
tot = [[0, 0], [0, 0]]
for c in sorted(R, key=lambda c: -R[c].get('2026-11-23', [0])[0]):
    t = R[c].get('2026-11-23', [0, 0, 0])
    if t[0] < 100: continue
    p = agg(c, '2026-11-10', '2026-11-16'); q = agg(c, '2026-11-17', '2026-11-23')
    for i, v in enumerate((p, q)): tot[i][0] += v[0]; tot[i][1] += v[1]
    s = f'{p[0]/p[1]*1000:,.0f} → {q[0]/q[1]*1000:,.0f}（{(q[0]/q[1])/(p[0]/p[1])-1:+.0%}）' if p[1] > 2000 else f'（前の7日は配信が少ない）→ {q[0]/q[1]*1000:,.0f}'
    out.append(f'  {c}: {s}｜11/23 {t[0]/t[1]*1000:,.0f}・クリック率 {t[2]/t[1]:.2%}')
out.append(f'  上の合計: {tot[0][0]/tot[0][1]*1000:,.0f} → {tot[1][0]/tot[1][1]*1000:,.0f}（{(tot[1][0]/tot[1][1])/(tot[0][0]/tot[0][1])-1:+.0%}）')
n = R['ナノガラス脱毛パッド']; out.append('■ ナノの CPM（日ごと）: ' + '・'.join(f'{d[5:]} {n[d][0]/n[d][1]*1000:,.0f}' for d in sorted(n) if d >= '2026-11-15'))
M = [l.strip().split(',') for l in json.load(open(os.path.join(D0, 'meta_ad_1123_raw.json')))['data']['data'].split('\n')[1:] if l.strip()]
z = lambda x: 0 if x in ('null', '') else int(x)
out.append('■ 新しい3本（基準5: 2日目の終日のクリック率 4.5%超で延長／2.5%未満かつカート0で停止）。11/23 の数字（Meta・広告セット合計）')
for c, lab in (('コードレス毛玉クリーナーv2', '毛玉 v2（11/22 14:4x〜・2日目＝11/23）'), ('UV歯ブラシ除菌器 v2', 'UV v2（11/22 15時台〜・2日目＝11/23・広告B は 11/23 12:5x〜）'), ('クリアビューレインガードフィルムv2', 'レインガード v2（11/23 16時台〜・初日。2日目は 11/24）')):
    rs = [r for r in M if r[1] == c]; cost = sum(z(r[4]) for r in rs); imp = sum(z(r[5]) for r in rs); clk = sum(z(r[6]) for r in rs); atc = sum(z(r[8]) for r in rs); pu = sum(z(r[9]) for r in rs)
    per = '・'.join(f'{r[3]} {z(r[6])}/{z(r[5]):,}（{z(r[6])/max(1,z(r[5])):.2%}）' for r in rs)
    out.append(f'  {lab}: 広告費 {cost:,}・表示 {imp:,}・クリック {clk}・クリック率 {clk/imp:.2%}（{per}）・カート {atc}・購入 {pu}（Meta）・クリック1回 {cost/clk:.0f}円')
open(os.path.join(D0, 'cpm_1124.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
