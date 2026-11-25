# -*- coding: utf-8 -*-
"""11/25 21:35 の自分への確認: 今日は Meta の配信が1日を通して少なく、17時台から全キャンペーンで落ちた。夜に戻ったかを確かめる。
0〜20時台（〜20:59）で切って 11/4〜24 の同じ時刻と並べ、時間ごとには 11/18〜24 の同じ時間と並べる。日中の数字なので予算の提案はしない。
入力（どれも結果をそのまま保存）:
  sales_h20_raw・sess_h20_raw（Shopify・0〜20時台・日別）／sess_hourly_1118_1125_2139_raw・sales_hourly_1118_1125_2139_raw（Shopify・時間別）
  meta_h20_1104_1125_raw（Meta・0〜20時台・日別）／meta_hourly_1118_1125_2139_raw（時間別・21:38 ごろ取得）
  meta_hourly_1125_late_raw・sess_17_21_1125_late_raw（今日の時間別の取り直し・21:42 ごろ。あれば今日の分はこちらを使う）
  meta_camp_hourly_1125_2139_raw（今日のキャンペーン×時間）／meta_history_1125_2138_raw（今日の変更履歴）"""
import json, csv, io, os, math, collections, statistics as st, datetime
B = 'scripts/daily/ic1125/h21/'
def table(f):
    raw = json.load(open(B + f, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    return [dict(zip(cols, r)) for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
z = lambda x: 0.0 if x in ('null', '', None) else float(x)
T = '2026-11-25'; H = 20
out = []
def P(s=''): print(s); out.append(s)
# ---- ① 0〜20時台: 今日 ↔ 21日 ----
V = {r[0][:10]: (int(r[1]), float(r[2]) + float(r[3])) for r in json.load(open(B + 'sales_h20_raw.json'))['rows']}
S = {r[0][:10]: tuple(int(x) for x in r[1:]) for r in json.load(open(B + 'sess_h20_raw.json'))['rows']}
M = {r['date']: (z(r['cost']), z(r['impressions']), z(r['link_clicks'])) for r in table('meta_h20_1104_1125_raw.json')}
past = sorted(d for d in V if d < T); assert len(past) == 21 and set(V) == set(S) == set(M)
def row(d):
    o, net = V[d]; ad, imp, clk = M[d]; ses, cart, chk, done = S[d]
    return dict(o=o, net=net, ad=ad, mer=net / ad, ses=ses, cvr=done / ses, cart=cart / ses, aov=net / o, cpm=ad / imp * 1000, spa=ses / ad * 1000)
R = {d: row(d) for d in past + [T]}
P('■ ① 0〜20時台（〜20:59）: 今日 ↔ 11/4〜11/24 の同じ時刻（21日）')
for k, lab, f in (('net', '売上（値引後）', '{:,.0f}'), ('o', '注文', '{:,.0f}'), ('ad', '広告費', '{:,.0f}'), ('mer', '売上÷広告費', '{:.2f}'), ('ses', '来訪（セッション）', '{:,.0f}'), ('spa', '広告費1,000円あたりの来訪', '{:.1f}'), ('cart', 'カート率', '{:.2%}'), ('cvr', '買う率', '{:.2%}'), ('aov', '1注文の売上', '{:,.0f}'), ('cpm', 'CPM', '{:,.0f}')):
    v = [R[d][k] for d in past]; t = R[T][k]
    P(f'  {lab}: 今日 {f.format(t)}｜21日 {f.format(min(v))}〜{f.format(max(v))}（中央値 {f.format(st.median(v))}）｜今日より低い日 {sum(x < t for x in v)}/21')
v = sorted(R[d]['mer'] for d in past)
P(f"  → 売上÷広告費 {R[T]['mer']:.2f} は 21日の範囲 {v[0]:.2f}〜{v[-1]:.2f} の{'中' if v[0] <= R[T]['mer'] <= v[-1] else '外'}・低いほうから {sum(x < R[T]['mer'] for x in v) + 1}番目（21日の低い順 3つ: " + '・'.join(f'{x:.2f}' for x in v[:3]) + '）')
rate = sum(R[d]['o'] for d in past) / sum(R[d]['ses'] for d in past); e = rate * R[T]['ses']; k = R[T]['o']
pl = lambda e, k: sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(k + 1))
P(f"  注文の見込み（21日の 注文÷来訪 {rate:.2%} × 今日の来訪 {R[T]['ses']:,}）{e:.1f}件 → 実際 {k}件・この数以下になる確率 {pl(e, k):.0%}")
P(f"  前日（11/24）の同じ時刻との差: 売上 {R['2026-11-24']['net']:,.0f} → {R[T]['net']:,.0f}（{R[T]['net'] / R['2026-11-24']['net'] - 1:+.0%}）＝ 広告費 {R['2026-11-24']['ad']:,.0f} → {R[T]['ad']:,.0f}（{R[T]['ad'] / R['2026-11-24']['ad'] - 1:+.0%}）× 売上÷広告費 {R['2026-11-24']['mer']:.2f} → {R[T]['mer']:.2f}（{R[T]['mer'] / R['2026-11-24']['mer'] - 1:+.0%}）")
# ---- ② 時間ごと: 今日 ↔ 11/18〜24 の同じ時間 ----
SH = collections.defaultdict(dict)
for r in json.load(open(B + 'sess_hourly_1118_1125_2139_raw.json'))['rows']: SH[r[0][:10]][int(r[1])] = (int(r[2]), int(r[3]), int(r[4]))
OH = collections.defaultdict(dict)
for r in json.load(open(B + 'sales_hourly_1118_1125_2139_raw.json'))['rows']: OH[r[0][:10]][int(r[1])] = int(r[2])
MH = collections.defaultdict(dict)
for r in table('meta_hourly_1118_1125_2139_raw.json'): MH[r['date']][int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2])] = (z(r['cost']), z(r['impressions']), z(r['link_clicks']))
first = dict(MH[T]); late = os.path.exists(B + 'meta_hourly_1125_late_raw.json')
if late:
    MH[T] = {int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2]): (z(r['cost']), z(r['impressions']), z(r['link_clicks'])) for r in table('meta_hourly_1125_late_raw.json')}
if os.path.exists(B + 'sess_17_21_1125_late_raw.json'):
    for r in json.load(open(B + 'sess_17_21_1125_late_raw.json'))['rows']: SH[T][int(r[1])] = (int(r[2]), int(r[3]), int(r[4]))
w7 = [d for d in sorted(SH) if d < T]; assert len(w7) == 7
P('■ ② 時間ごと（15〜21時台）: 今日 ↔ 11/18〜24 の同じ時間（最小〜最大・中央値）。★＝7日の最小より低い・▲＝7日の最大より高い')
mark = lambda x, v: '★' if x < min(v) else ('▲' if x > max(v) else '')
for h in range(15, H + 2):
    s7 = [SH[d].get(h, (0, 0, 0))[0] for d in w7]; a7 = [MH[d][h][0] for d in w7]; i7 = [MH[d][h][1] for d in w7]; p7 = [MH[d][h][0] / MH[d][h][1] * 1000 for d in w7]; o7 = [OH[d].get(h, 0) for d in w7]
    s, o = SH[T].get(h, (0, 0, 0))[0], OH[T].get(h, 0); a, i, c = MH[T].get(h, (0, 0, 0)); cpm = a / i * 1000 if i else 0
    P(f"  {h:02d}時台{'（途中）' if h > H else ''}: 広告費 {a:,.0f}{mark(a, a7)}（{min(a7):,.0f}〜{max(a7):,.0f}・{st.median(a7):,.0f}）｜表示 {i:,.0f}{mark(i, i7)}（{min(i7):,.0f}〜{max(i7):,.0f}）｜CPM {cpm:,.0f}{mark(cpm, p7)}（{min(p7):,.0f}〜{max(p7):,.0f}）｜来訪 {s}{mark(s, s7)}（{min(s7)}〜{max(s7)}・{st.median(s7):.0f}）｜注文 {o}（{min(o7)}〜{max(o7)}）")
if late: P('  （今日の Meta の時間別と 17時台からの来訪は 21:42 ごろに取り直した値。1回目 21:38 ごろの取得では 20時台 ' + f"{first[20][0]:,.0f}・21時台 {first.get(21, (0,))[0]:,.0f}）")
for a, b, lab in ((17, 19, '17〜19時台'), (19, 20, '19〜20時台'), (17, 20, '17〜20時台'), (0, 16, '0〜16時台')):
    hs = range(a, b + 1); f = lambda d, j: sum(MH[d].get(h, (0, 0, 0))[j] for h in hs); g = lambda d: sum(SH[d].get(h, (0,))[0] for h in hs)
    p_a = [f(d, 0) for d in w7]; p_s = [g(d) for d in w7]; p_c = [f(d, 0) / f(d, 1) * 1000 for d in w7]
    P(f"  {lab}: 広告費 今日 {f(T, 0):,.0f}｜7日 {min(p_a):,.0f}〜{max(p_a):,.0f}（中央値 {st.median(p_a):,.0f}・今日÷中央値 {f(T, 0) / st.median(p_a):.0%}）｜CPM 今日 {f(T, 0) / f(T, 1) * 1000:,.0f}｜7日 {min(p_c):,.0f}〜{max(p_c):,.0f}｜来訪 今日 {g(T):,}｜7日 {min(p_s):,}〜{max(p_s):,}（中央値 {st.median(p_s):,.0f}・{g(T) / st.median(p_s):.0%}）")
# ---- ③ 0〜20時台の広告費 ÷ 日予算 ----
bud = {}
for r in csv.DictReader(open('data/budget-snapshots.csv', encoding='utf-8')): bud[(r['campaign'], r['adset'])] = (r['snapshot_date'], float(r['daily_budget']))
full = max(d for d, _ in bud.values() if len(d) == 10); BUD = sum(b for d, b in bud.values() if d >= full); assert BUD == 202000, BUD
t20 = sum(MH[T][h][0] for h in range(H + 1))
sh = [sum(MH[d][h][0] for h in range(H + 1)) / sum(x[0] for x in MH[d].values()) for d in w7]
p20 = [sum(MH[d][h][0] for h in range(H + 1)) for d in w7]
P(f'■ ③ 0〜20時台の広告費 {t20:,.0f} ÷ 日予算の合計 {BUD:,.0f} ＝ {t20 / BUD:.0%}（0〜17時台の時点は 57%）')
P(f"  ふだん 0〜20時台までに使う割合（その日の広告費に対して・11/18〜24）: {min(sh):.0%}〜{max(sh):.0%}（中央値 {st.median(sh):.0%}）")
P(f"  11/18〜24 の 0〜20時台の広告費: {min(p20):,.0f}〜{max(p20):,.0f}（中央値 {st.median(p20):,.0f}）→ 今日÷中央値 {t20 / st.median(p20):.0%}（0〜17時台の時点は、7日の実績があるキャンペーンで 85%）")
# ---- ④ キャンペーンごとの 18 → 19 → 20時台 ----
ch = collections.defaultdict(dict)
for r in table('meta_camp_hourly_1125_2139_raw.json'): ch[r['adcampaign_name']][int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2])] = (z(r['cost']), z(r['impressions']))
act = {c: v for c, v in ch.items() if v.get(18, (0,))[0] > 0}
P('■ ④ 今日の 18 → 19 → 20時台の広告費（キャンペーンごと・21:38 ごろ取得）: ' + '・'.join(f"{c} {v[18][0]:,.0f}→{v.get(19, (0,))[0]:,.0f}→{v.get(20, (0,))[0]:,.0f}" for c, v in sorted(act.items(), key=lambda x: -x[1][18][0])))
P(f"  19時台に 18時台より下がったキャンペーン {sum(1 for v in act.values() if v.get(19, (0,))[0] < v[18][0])}/{len(act)}・20時台に 18時台より上がったキャンペーン {sum(1 for v in act.values() if v.get(20, (0,))[0] > v[18][0])}/{len(act)}")
NEW = ('2WAYシートボックスv2', '3WAY着る電気ブランケットv2')
for h in (17, 18, 19, 20):
    a = sum(v.get(h, (0, 0))[0] for c, v in ch.items()); i = sum(v.get(h, (0, 0))[1] for c, v in ch.items())
    a2 = sum(v.get(h, (0, 0))[0] for c, v in ch.items() if c not in NEW); i2 = sum(v.get(h, (0, 0))[1] for c, v in ch.items() if c not in NEW)
    p7 = [MH[d][h][0] / MH[d][h][1] * 1000 for d in w7]
    P(f"  {h}時台の CPM: 全部 {a / i * 1000:,.0f}・今日出した2本（ブランケット v2・シートボックス v2）を除くと {a2 / i2 * 1000:,.0f}｜7日の同じ時間 {min(p7):,.0f}〜{max(p7):,.0f}")
# ---- ⑤ 今日の変更履歴（Meta・UTC の 11/25＝日本時間 9時〜） ----
hist = json.load(open(B + 'meta_history_1125_2138_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
jt = lambda t: datetime.datetime.fromisoformat(t.replace('+0000', '+00:00')) + datetime.timedelta(hours=9)
key = [h for h in hist if h['operation'] in ('CREATE_CAMPAIGN_GROUP', 'AD_ACCOUNT_BILLING_CHARGE', 'FIRST_DELIVERY_EVENT') or h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET')]
P(f'■ ⑤ Meta の変更履歴（日本時間 11/25 9時〜21:38・{len(hist)}件）: ' + '・'.join(f"{jt(h['timestamp']).strftime('%H:%M')} {h['operation']}（{h['campaign_name']}{' ' + h['campaign_id'] if h['operation'] == 'FIRST_DELIVERY_EVENT' else ''}{' ' + format(h['change_values']['new_value'], ',') + '円' if h['operation'] == 'AD_ACCOUNT_BILLING_CHARGE' else ''}）" for h in sorted(key, key=lambda h: h['timestamp'])))
stop = [h for h in hist if h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET') or (h['operation'].endswith('RUN_STATUS') and h['change_values'].get('new_value') in ('オフ', '停止', '一時停止'))]
P(f"  予算の金額の変更・停止の操作: {len(stop)}件｜18時以降の操作: " + ('・'.join(f"{jt(h['timestamp']).strftime('%H:%M')} {h['operation']}" for h in sorted(hist, key=lambda h: h['timestamp']) if jt(h['timestamp']).hour >= 18) or 'なし'))
bc = sorted(jt(h['timestamp']) for h in hist if h['operation'] == 'AD_ACCOUNT_BILLING_CHARGE')
if len(bc) == 2:
    mid = sum(MH[T][h][0] for h in range(bc[0].hour + 1, bc[1].hour)); lo = mid; hi = mid + MH[T][bc[0].hour][0] + MH[T].get(bc[1].hour, (0,))[0]
    P(f"  課金 {bc[0].strftime('%H:%M')} → {bc[1].strftime('%H:%M')} の間の広告費: {bc[0].hour + 1}〜{bc[1].hour - 1}時台 {lo:,.0f} ＋ 両端の時間の一部（多くても {hi:,.0f}）＝ 1回の課金 100,000円の前後")
open(B + 'hourly_h21.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
