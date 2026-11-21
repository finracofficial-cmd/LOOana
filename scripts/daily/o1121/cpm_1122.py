# -*- coding: utf-8 -*-
"""11/22 定例: 同じキャンペーンの中での CPM（直近7日 11/15〜21 ↔ その前の7日 11/8〜14）と、ナノの日ごとの CPM。入力は o1121/ad_level_1026_1121.txt"""
import collections, os
D0 = os.path.dirname(os.path.abspath(__file__)); R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(os.path.join(D0, 'ad_level_1026_1121.txt')):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
out = ['■ 同じキャンペーンの中での CPM: その前の7日（11/8〜14）→ 直近7日（11/15〜21）｜11/21 の1日（11/21 に広告費が出たもの）']
def agg(c, a, b): v = [x for d, x in R[c].items() if a <= d <= b]; return sum(x[0] for x in v), sum(x[1] for x in v), sum(x[2] for x in v)
tot = [[0, 0], [0, 0]]
for c in sorted(R, key=lambda c: -R[c].get('2026-11-21', [0])[0]):
    t = R[c].get('2026-11-21', [0, 0, 0])
    if t[0] < 100: continue
    p = agg(c, '2026-11-08', '2026-11-14'); q = agg(c, '2026-11-15', '2026-11-21')
    for i, v in enumerate((p, q)): tot[i][0] += v[0]; tot[i][1] += v[1]
    s = f'{p[0]/p[1]*1000:,.0f} → {q[0]/q[1]*1000:,.0f}（{(q[0]/q[1])/(p[0]/p[1])-1:+.0%}）' if p[1] > 2000 else f'（前の7日は配信が少ない）→ {q[0]/q[1]*1000:,.0f}'
    out.append(f'  {c}: {s}｜11/21 {t[0]/t[1]*1000:,.0f}・クリック率 {t[2]/t[1]:.2%}')
out.append(f'  上の合計: {tot[0][0]/tot[0][1]*1000:,.0f} → {tot[1][0]/tot[1][1]*1000:,.0f}（{(tot[1][0]/tot[1][1])/(tot[0][0]/tot[0][1])-1:+.0%}）')
n = R['ナノガラス脱毛パッド']; out.append('■ ナノの CPM（日ごと）: ' + '・'.join(f'{d[5:]} {n[d][0]/n[d][1]*1000:,.0f}' for d in sorted(n) if d >= '2026-11-12'))
h = R['充電式ダブルミスト卓上加湿器']['2026-11-21']; out.append(f'■ 新しい加湿器の3日目（11/21 終日）: 表示 {h[1]:,}・リンクのクリック {h[2]}・クリック率 {h[2]/h[1]:.2%}（2日目 11/20 は 3.22%。基準5 の判定は2日目で済み・次は7日の倍率）')
open(os.path.join(D0, 'cpm_1122.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
