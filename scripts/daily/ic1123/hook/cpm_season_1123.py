# -*- coding: utf-8 -*-
"""11/23「CPM は年末だから上がってる？」: ①配置ごとの CPM（前の28日 10/19〜11/15 → 直近7日 11/16〜22・アカウント全体）②キャンペーンごとの週別 CPM（10/26〜・4週）
③アカウントの CPM の変化を「同じキャンペーンの中での値上がり」と「お金の行き先が変わった分」に分ける。入力: acct_placement_*_raw.json・o1122/ad_level_1026_1122.txt"""
import json, os, collections
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
def table(f):
    out = []
    for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:]:
        l = l.strip()
        if l: out.append(l.split(','))
    return out
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
a = {r[0] + ' ' + r[1]: (z(r[2]), z(r[3]), z(r[4])) for r in table('acct_placement_1019_1115_raw.json')}; b = {r[0] + ' ' + r[1]: (z(r[2]), z(r[3]), z(r[4])) for r in table('acct_placement_1116_1122_raw.json')}
ta = [sum(v[i] for v in a.values()) for i in range(3)]; tb = [sum(v[i] for v in b.values()) for i in range(3)]
P('■ ① 配置ごと（アカウント全体）: 前の28日（10/19〜11/15）→ 直近7日（11/16〜22）｜CPM・表示の割合・クリック率')
for k in sorted(a, key=lambda k: -a[k][0])[:6]:
    x, y = a[k], b[k]; P(f'  {k}: CPM {x[0]/x[1]*1000:,.0f} → {y[0]/y[1]*1000:,.0f}（{(y[0]/y[1])/(x[0]/x[1])-1:+.0%}）・表示の割合 {x[1]/ta[1]:.0%} → {y[1]/tb[1]:.0%}・クリック率 {x[2]/x[1]:.2%} → {y[2]/y[1]:.2%}')
P(f'  全体: CPM {ta[0]/ta[1]*1000:,.0f} → {tb[0]/tb[1]*1000:,.0f}（{(tb[0]/tb[1])/(ta[0]/ta[1])-1:+.0%}）')
within = sum(a[k][1] / ta[1] * ((b[k][0] / b[k][1] if k in b and b[k][1] else a[k][0] / a[k][1]) - a[k][0] / a[k][1]) * 1000 for k in a if a[k][1])
P(f'  うち 同じ配置の中での値上がり（配置の割合を前のままにした場合）: {within:+,.0f}円 ／ 配置の割合が変わった分: {(tb[0]/tb[1]-ta[0]/ta[1])*1000-within:+,.0f}円')
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(D0 + '../../o1122/ad_level_1026_1122.txt'):
    if l[0] == '#': continue
    d, c, ad_set, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
W = [('10/26〜11/1', '2026-10-26', '2026-11-01'), ('11/2〜8', '2026-11-02', '2026-11-08'), ('11/9〜15', '2026-11-09', '2026-11-15'), ('11/16〜22', '2026-11-16', '2026-11-22')]
def agg(c, a_, b_): v = [x for d, x in R[c].items() if a_ <= d <= b_]; return [sum(x[i] for x in v) for i in range(3)]
P('■ ② 4週とも配信があったキャンペーンの週別 CPM（' + '・'.join(w[0] for w in W) + '）と 広告費/日')
for c in sorted(R, key=lambda c: -agg(c, W[3][1], W[3][2])[0]):
    v = [agg(c, w[1], w[2]) for w in W]
    if any(x[1] < 5000 for x in v): continue
    P(f'  {c}: CPM ' + ' → '.join(f'{x[0]/x[1]*1000:,.0f}' for x in v) + f'（4週で {(v[3][0]/v[3][1])/(v[0][0]/v[0][1])-1:+.0%}）｜広告費/日 ' + ' → '.join(f'{x[0]/7:,.0f}' for x in v) + f'｜クリック率 {v[0][2]/v[0][1]:.2%} → {v[3][2]/v[3][1]:.2%}')
P('■ ③ アカウントの CPM（10/26〜11/1 → 11/16〜22）を分ける')
p0 = {c: agg(c, W[0][1], W[0][2]) for c in R}; p1 = {c: agg(c, W[3][1], W[3][2]) for c in R}
T0 = [sum(v[i] for v in p0.values()) for i in range(3)]; T1 = [sum(v[i] for v in p1.values()) for i in range(3)]
cp0, cp1 = T0[0] / T0[1] * 1000, T1[0] / T1[1] * 1000
both = [c for c in R if p0[c][1] and p1[c][1]]
w_in = sum(p0[c][1] / T0[1] * (p1[c][0] / p1[c][1] - p0[c][0] / p0[c][1]) * 1000 for c in both)
P(f'  CPM {cp0:,.0f} → {cp1:,.0f}（{cp1-cp0:+,.0f}円・{cp1/cp0-1:+.0%}）')
P(f'  同じキャンペーンの中での値上がり（表示の割合を前のままにした場合）: {w_in:+,.0f}円 ／ お金の行き先が変わった分（止めた・始めた・割合が変わった）: {cp1-cp0-w_in:+,.0f}円')
P('  表示の割合の変化（大きいもの）: ' + '・'.join(f'{c} {p0[c][1]/T0[1]:.0%} → {p1[c][1]/T1[1]:.0%}（CPM {(p1[c][0]/p1[c][1]*1000 if p1[c][1] else p0[c][0]/p0[c][1]*1000):,.0f}）' for c in sorted(R, key=lambda c: -abs(p1[c][1] / T1[1] - p0[c][1] / T0[1]))[:6]))
ct0, ct1 = T0[2] / T0[1], T1[2] / T1[1]; c_in = sum(p0[c][1] / T0[1] * (p1[c][2] / p1[c][1] - p0[c][2] / p0[c][1]) for c in both)
P(f'  クリック率 {ct0:.2%} → {ct1:.2%}（{(ct1-ct0)*100:+.2f}ポイント）: 同じキャンペーンの中 {c_in*100:+.2f}・行き先が変わった分 {(ct1-ct0-c_in)*100:+.2f}')
open(D0 + 'cpm_season_1123.txt', 'w').write('\n'.join(out) + '\n')
# ---- ④ クリック1回の値段（CPC）で同じ分け方: アカウントの CPC ＝ Σ クリックの割合 × そのキャンペーンの CPC
out2 = []
def P2(*x):
    s = ' '.join(str(i) for i in x); print(s); out2.append(s)
c0, c1 = T0[0] / T0[2], T1[0] / T1[2]
k_in = sum(p0[c][2] / T0[2] * (p1[c][0] / p1[c][2] - p0[c][0] / p0[c][2]) for c in both if p0[c][2] and p1[c][2])
P2('■ ④ クリック1回の値段（10/26〜11/1 → 11/16〜22）')
P2(f'  アカウント: {c0:.0f}円 → {c1:.0f}円（{c1-c0:+.0f}円）＝ 同じキャンペーンの中 {k_in:+.1f}円 ＋ お金の行き先が変わった分 {c1-c0-k_in:+.1f}円')
P2('  4週とも配信があったキャンペーン: ' + '・'.join(f'{c} {p0[c][0]/p0[c][2]:.0f} → {p1[c][0]/p1[c][2]:.0f}円' for c in ('伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', 'マグネットドアクッション', '4-in-1マルチクリーナー', 'カタログ全部（テスト）')))
P2('  直近7日のクリック1回の値段（広告費の多い順）: ' + '・'.join(f'{c} {p1[c][0]/p1[c][2]:.0f}円（広告費の {p1[c][0]/T1[0]:.0%}）' for c in sorted(R, key=lambda c: -p1[c][0]) if p1[c][2] and p1[c][0] > 3000))
hi = [c for c in R if p1[c][2] and p1[c][0] / p1[c][2] > 130]; P2(f'  クリック1回 130円を超えるキャンペーンの広告費: 直近7日 {sum(p1[c][0] for c in hi):,}円（{sum(p1[c][0] for c in hi)/T1[0]:.0%}）: ' + '・'.join(hi))
open(D0 + 'cpm_season_1123.txt', 'a').write('\n'.join(out2) + '\n')
