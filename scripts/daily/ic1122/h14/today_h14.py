# -*- coding: utf-8 -*-
"""11/22 14時台「今時点のパフォーマンス」: 0〜13時台（〜13:59）で切り、11/1〜11/21 の同じ時刻と並べる（日中の数字では予算を提案しない）。
入力: sales_h13_raw.json・sess_h13_raw.json（Shopify・hour_of_day <= 13）／Meta: meta_h13_1101_1117_raw.json（1本）・meta_h13_1118_raw.json（1日）・
11/19〜21 は o1119〜o1121 の hourly_*_raw.txt の MH 行（0〜13時台を足す）・今日は meta_hourly_1122_raw.json（14:3x 取得・14時台は途中なので使わない）"""
import json, os, statistics as st, math
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
def table(f):
    out = []
    for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:]:
        l = l.strip()
        if not l: continue
        if l.startswith('"'): h, rest = l[1:].split('",', 1); out.append([h] + rest.split(','))
        else: out.append(l.split(','))
    return out
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
V = {r[0]: (int(r[1]), int(r[2]) + int(r[3])) for r in json.load(open(D0 + 'sales_h13_raw.json'))['rows']}          # 注文・売上（値引後）
S = {r[0]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open(D0 + 'sess_h13_raw.json'))['rows']}             # 来訪・カート・購入
M = {r[0]: (z(r[1]), z(r[2])) for r in table('meta_h13_1101_1117_raw.json') + table('meta_h13_1118_raw.json')}
for d, f in (('2026-11-19', '../../o1119/hourly_1119_raw.txt'), ('2026-11-20', '../../o1120/hourly_1120_raw.txt'), ('2026-11-21', '../../o1121/hourly_1121_raw.txt')):
    c = i = 0
    for l in open(D0 + f):
        if l.startswith('MH,'):
            p = l.strip().split(',')
            if int(p[1]) <= 13: c += int(p[2]); i += int(p[3])
    M[d] = (c, i)
t = [(int(r[0][:2]), z(r[1]), z(r[2])) for r in table('meta_hourly_1122_raw.json')]
M['2026-11-22'] = (sum(x[1] for x in t if x[0] <= 13), sum(x[2] for x in t if x[0] <= 13))
T = '2026-11-22'; past = [d for d in sorted(V) if d < T]; assert len(past) == 21 and all(d in M and d in S for d in past + [T])
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
def row(name, f, fmt):
    v = f(T); ps = [f(d) for d in past]; lo = sum(1 for x in ps if x < v)
    pos = '範囲の外（上）' if v > max(ps) else ('範囲の外（下）' if v < min(ps) else '範囲の中')
    P(f'  {name}: 今日 {fmt.format(v)}｜過去21日 {fmt.format(min(ps))}〜{fmt.format(max(ps))}・中央値 {fmt.format(st.median(ps))}・今日より低い日 {lo}/21 → {pos}')
    return v, ps, lo
P('■ 11/22（日・3連休の中日）0〜13時台 ↔ 11/1〜11/21 の同じ時刻')
r = row('売上÷広告費', lambda d: V[d][1] / M[d][0], '{:.2f}')
row('売上（値引後）', lambda d: V[d][1], '{:,.0f}'); row('広告費', lambda d: M[d][0], '{:,.0f}'); row('注文', lambda d: V[d][0], '{:.0f}')
row('1注文の売上', lambda d: V[d][1] / V[d][0], '{:,.0f}'); row('来訪', lambda d: S[d][0], '{:,.0f}')
row('カート率', lambda d: S[d][1] / S[d][0] * 100, '{:.2f}%'); row('買う率（購入÷来訪）', lambda d: S[d][2] / S[d][0] * 100, '{:.2f}%')
row('CPM', lambda d: M[d][0] / M[d][1] * 1000, '{:,.0f}'); row('来訪÷広告費1万円', lambda d: S[d][0] / M[d][0] * 1e4, '{:.0f}')
cv = sum(S[d][2] for d in past) / sum(S[d][0] for d in past); e = S[T][0] * cv; k = S[T][2]
pois = lambda k, l: math.exp(-l + k * math.log(l) - math.lgamma(k + 1)); p_hi = 1 - sum(pois(i, e) for i in range(k)); p_lo = sum(pois(i, e) for i in range(k + 1))
P(f'  購入の件数: 来訪 {S[T][0]:,} × 過去21日の買う率 {cv:.2%} ＝ 見込み {e:.1f}件・実際 {k}件（この数以上 {p_hi:.0%}・以下 {p_lo:.0%}）')
v, ps, lo = r
P('  結論: ' + ('偶然の範囲内' if 3 <= lo <= 17 else ('偶然でも起きるが端' if min(ps) <= v <= max(ps) else '偶然では起きにくい')) + f'（売上÷広告費 {v:.2f}・21日中 {lo}日が今日より低い）')
open(D0 + 'today_h14.txt', 'w').write('\n'.join(L) + '\n')
