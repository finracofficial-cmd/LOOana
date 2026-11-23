# -*- coding: utf-8 -*-
"""11/23 12時台「今時点のパフォーマンス」: 0〜11時台（〜11:59）で切り、11/2〜11/22 の同じ時刻と並べる（日中の数字では予算を提案しない）。
入力: sales_h11_raw.json・sess_h11_raw.json（Shopify・hour_of_day <= 11）／Meta: meta_h11_1102_1118_raw.json（1本・時刻で絞った日別）・
11/19〜22 は o1119〜o1122 の hourly_*_raw.txt の MH 行（0〜11時台を足す）・今日は meta_hourly_1123_raw.json（12:2x 取得・12時台は途中なので使わない）"""
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
V = {r[0]: (int(r[1]), int(r[2]) + int(r[3])) for r in json.load(open(D0 + 'sales_h11_raw.json'))['rows']}          # 注文・売上（値引後）
S = {r[0]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open(D0 + 'sess_h11_raw.json'))['rows']}             # 来訪・カート・購入
M = {r[0]: (z(r[1]), z(r[2])) for r in table('meta_h11_1102_1118_raw.json')}
for d, f in (('2026-11-19', '../../o1119/hourly_1119_raw.txt'), ('2026-11-20', '../../o1120/hourly_1120_raw.txt'), ('2026-11-21', '../../o1121/hourly_1121_raw.txt'), ('2026-11-22', '../../o1122/hourly_1122_raw.txt')):
    c = i = 0
    for l in open(D0 + f):
        if l.startswith('MH,'):
            p = l.strip().split(',')
            if int(p[1]) <= 11: c += int(p[2]); i += int(p[3])
    M[d] = (c, i)
t = [(int(r[0][:2]), z(r[1]), z(r[2])) for r in table('meta_hourly_1123_raw.json')]
M['2026-11-23'] = (sum(x[1] for x in t if x[0] <= 11), sum(x[2] for x in t if x[0] <= 11))
T = '2026-11-23'; past = [d for d in sorted(V) if d < T]; assert len(past) == 21 and all(d in M and d in S for d in past + [T])
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
def row(name, f, fmt):
    v = f(T); ps = [f(d) for d in past]; lo = sum(1 for x in ps if x < v)
    pos = '範囲の外（上）' if v > max(ps) else ('範囲の外（下）' if v < min(ps) else '範囲の中')
    P(f'  {name}: 今日 {fmt.format(v)}｜過去21日 {fmt.format(min(ps))}〜{fmt.format(max(ps))}・中央値 {fmt.format(st.median(ps))}・今日より低い日 {lo}/21 → {pos}')
    return v, ps, lo
P('■ 11/23（月・祝日＝3連休の最終日）0〜11時台 ↔ 11/2〜11/22 の同じ時刻')
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
P('  同じ時刻の売上÷広告費（日ごと）: ' + '・'.join(f'{d[5:]} {V[d][1]/M[d][0]:.2f}' for d in past[-10:] + [T]))
# 今日の商品別（0〜11時台の広告費と、12:1x 時点の注文の実数。日中なので良い悪いは決めない）
nm = lambda s: __import__('re').sub(r'【[^】]*】', '', s).replace('LOOTY', '', 1).strip()
O = {nm(r[0]): (int(r[1]), int(r[4])) for r in json.load(open(D0 + 'orders_by_product_1123_h12_raw.json'))['rows'] if r[0] and not r[0].startswith('VIP')}
C2P = {'伸縮ガラスクリーナー': '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド': 'ナノガラス脱毛パッド', 'ワイド水切りワイパー': 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー': 'W固定スマホ車載ホルダー', '快適マジックインソール v3': '快適マジックインソール', 'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', 'マグネットドアクッション': 'マグネットドアクッション', '4-in-1マルチクリーナー': '4-in-1マルチクリーナー', '360°マルチクリップ車載スマホホルダー': '360°マルチクリップ車載スマホホルダー', '高見えレザーヘッドレストフックv5': '高見えレザーヘッドレストフック', '充電式ダブルミスト卓上加湿器': '充電式ダブルミスト卓上加湿器', 'コードレス毛玉クリーナーv2': 'コードレス毛玉クリーナー', 'UV歯ブラシ除菌器 v2': 'UV歯ブラシ除菌器'}
P('■ 今日の商品別（広告費・表示・クリックは 0〜11時台／注文は 12:1x までの実数）')
for c, cost, imp, clk, atc, pu in sorted(table('meta_camp_h11_1123_raw.json'), key=lambda r: -z(r[1])):
    if not z(cost): continue
    p = C2P.get(c); o = O.get(p, (0, 0)) if p else None
    P(f"  {c}: 広告費 {z(cost):,}・CPM {z(cost)/z(imp)*1000:,.0f}・クリック率 {z(clk)/z(imp):.2%}（{z(clk)}/{z(imp):,}）・カート {z(atc)}" + (f'・注文 {o[0]}（{o[1]}個）' if o is not None else f'・Meta 計上の購入 {z(pu)}'))
P('  広告なしで売れた商品: ' + '・'.join(f'{n} {o}注文' for n, (o, q) in O.items() if n not in C2P.values()))
open(D0 + 'today_h11.txt', 'w').write('\n'.join(L) + '\n')
