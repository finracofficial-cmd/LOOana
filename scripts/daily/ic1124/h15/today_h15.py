# -*- coding: utf-8 -*-
"""11/24 16時台「売れ行き悪すぎる。今時点でも」: 0〜15時台（〜15:59）で切り、11/3〜11/23 の同じ時刻と並べる（日中の数字では予算を提案しない）。
入力: sales_h15_raw.json・sess_h15_raw.json（Shopify・hour_of_day <= 15）・meta_h15_1103_1124_raw.json（Meta・時刻で絞った日別）・meta_camp_h15_1124_raw.json（今日のキャンペーン別）・prod_1624_raw.json（今日 16:2x までの商品別）"""
import json, os, statistics as st, math, datetime, re
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
def table(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
V = {r[0]: (int(r[1]), int(r[2]) + int(r[3])) for r in json.load(open(D0 + 'sales_h15_raw.json'))['rows']}
S = {r[0]: (int(r[1]), int(r[2]), int(r[4])) for r in json.load(open(D0 + 'sess_h15_raw.json'))['rows']}
M = {r[0]: (z(r[1]), z(r[2])) for r in table('meta_h15_1103_1124_raw.json')}
T = '2026-11-24'; past = [d for d in sorted(V) if d < T]; assert len(past) == 21
HOL = {'2026-11-03', '2026-11-23'}
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
def row(d): o, net = V[d]; ad, imp = M[d]; s, c, done = S[d]; return dict(o=o, net=net, ad=ad, mer=net / ad, cvr=done / s, cart=c / s, aov=net / o, cpm=ad / imp * 1000, ses=s)
R = {d: row(d) for d in past + [T]}
P('■ 0〜15時台（〜15:59）: 今日 ↔ 11/3〜11/23 の同じ時刻（21日・祝日 11/3・11/23 を含む）')
for k, lab, f in (('net', '売上（値引後）', '{:,.0f}'), ('o', '注文', '{:,.0f}'), ('ad', '広告費', '{:,.0f}'), ('mer', '売上÷広告費', '{:.2f}'), ('ses', '来訪', '{:,.0f}'), ('cart', 'カート率', '{:.2%}'), ('cvr', '買う率', '{:.2%}'), ('aov', '1注文の売上', '{:,.0f}'), ('cpm', 'CPM', '{:,.0f}')):
    v = [R[d][k] for d in past]; t = R[T][k]
    P(f'  {lab}: 今日 {f.format(t)}｜21日 {f.format(min(v))}〜{f.format(max(v))}（中央値 {f.format(st.median(v))}）｜今日より低い日 {sum(x < t for x in v)}/21')
tue = [d for d in past if datetime.date.fromisoformat(d).weekday() == 1]
P('  火曜（' + '・'.join(d[5:] for d in tue) + '）: ' + '・'.join(f"{d[5:]} 売上 {R[d]['net']:,}・注文 {R[d]['o']}・{R[d]['mer']:.2f}" for d in tue))
# 注文数の見込み（21日の 注文÷来訪 × 今日の来訪）とポアソン
rate = sum(R[d]['o'] for d in past) / sum(R[d]['ses'] for d in past); e = rate * R[T]['ses']; k = R[T]['o']
lo = sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(k + 1))
P(f'  注文の見込み（21日の 注文÷来訪 {rate:.2%} × 今日の来訪 {R[T]["ses"]:,}）{e:.1f}件 → 実際 {k}件・この数以下になる確率 {lo:.0%}')
v = sorted(R[d]['mer'] for d in past)
j = '偶然の範囲内' if v[0] <= R[T]['mer'] <= v[-1] else '偶然でも起きるが端'
P(f'  → 売上÷広告費 {R[T]["mer"]:.2f} は 21日の範囲 {v[0]:.2f}〜{v[-1]:.2f} の中・低いほうから {sum(x < R[T]["mer"] for x in v)+1}番目 → {j}')
# キャンペーン別（Meta・0〜15時台）と商品別（Shopify・16:2x まで）
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
P('■ 今日のキャンペーン別（Meta・0〜15時台）: 広告費・クリック・クリック1回・Meta の購入')
for r in sorted(table('meta_camp_h15_1124_raw.json'), key=lambda r: -z(r[1])):
    P(f'  {r[0]}: {z(r[1]):,}円・{z(r[3])}クリック・{z(r[1])/max(1,z(r[3])):.0f}円・購入 {z(r[5])}')
P('■ 今日の商品別（Shopify・16:2x まで）: 注文・個数')
P('  ' + '・'.join(f'{nm(r[0])} {r[1]}注文{r[4]}個' for r in json.load(open(D0 + 'prod_1624_raw.json'))['rows'] if r[0] and not r[0].startswith('VIP')))
open(D0 + 'today_h15.txt', 'w').write('\n'.join(L) + '\n')
