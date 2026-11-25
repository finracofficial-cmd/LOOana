# -*- coding: utf-8 -*-
"""11/25 18:4x「今時点のパフォーマンス急に悪化したやん。てかセッションが少なすぎる気がする」
0〜17時台（〜17:59）で切って 11/4〜24 の同じ時刻と並べ、時間ごとには 11/18〜24 の同じ時間と並べる。日中の数字なので予算の提案はしない。
入力（どれも結果をそのまま保存）: sales_h17_raw・sess_source_h17_1104_1125_raw・sess_hourly_1118_1125_raw・sales_hourly_1118_1125_raw（Shopify）
      meta_camp_h17_1104_1125_raw（キャンペーン別・同じ時刻）・meta_hourly_1118_1125_raw（時間別）・meta_camp_hourly_1125_raw（今日のキャンペーン×時間）・meta_history_1125_raw（今日の変更履歴）"""
import json, csv, io, re, math, collections, statistics as st, datetime
B = 'scripts/daily/ic1125/h17/'
def table(f):
    raw = json.load(open(B + f, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    return [dict(zip(cols, r)) for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
z = lambda x: 0.0 if x in ('null', '', None) else float(x)
T = '2026-11-25'; H = 17
out = []
def P(s=''): print(s); out.append(s)
# ---- ① 0〜17時台: 今日 ↔ 21日 ----
V = {r[0][:10]: (int(r[1]), float(r[2]) + float(r[3])) for r in json.load(open(B + 'sales_h17_raw.json'))['rows']}
SRC = collections.defaultdict(dict)
for r in json.load(open(B + 'sess_source_h17_1104_1125_raw.json'))['rows']: SRC[r[0][:10]][r[1]] = (int(r[2]), int(r[3]), int(r[5]))
camp = table('meta_camp_h17_1104_1125_raw.json')
M = collections.defaultdict(lambda: [0, 0, 0])
for r in camp:
    m = M[r['date']]; m[0] += z(r['cost']); m[1] += z(r['impressions']); m[2] += z(r['link_clicks'])
past = sorted(d for d in V if d < T); assert len(past) == 21
def row(d):
    o, net = V[d]; ad, imp, clk = M[d]; ses = sum(v[0] for v in SRC[d].values()); done = sum(v[2] for v in SRC[d].values()); cart = sum(v[1] for v in SRC[d].values())
    return dict(o=o, net=net, ad=ad, mer=net / ad, ses=ses, cvr=done / ses, cart=cart / ses, aov=net / o, cpm=ad / imp * 1000, spa=ses / ad * 1000, soc=SRC[d]['social'][0], dir=SRC[d]['direct'][0])
R = {d: row(d) for d in past + [T]}
P('■ ① 0〜17時台（〜17:59）: 今日 ↔ 11/4〜11/24 の同じ時刻（21日）')
for k, lab, f in (('net', '売上（値引後）', '{:,.0f}'), ('o', '注文', '{:,.0f}'), ('ad', '広告費', '{:,.0f}'), ('mer', '売上÷広告費', '{:.2f}'), ('ses', '来訪（セッション）', '{:,.0f}'), ('soc', '　うち social', '{:,.0f}'), ('dir', '　うち direct', '{:,.0f}'), ('spa', '広告費1,000円あたりの来訪', '{:.1f}'), ('cart', 'カート率', '{:.2%}'), ('cvr', '買う率', '{:.2%}'), ('aov', '1注文の売上', '{:,.0f}'), ('cpm', 'CPM', '{:,.0f}')):
    v = [R[d][k] for d in past]; t = R[T][k]
    P(f'  {lab}: 今日 {f.format(t)}｜21日 {f.format(min(v))}〜{f.format(max(v))}（中央値 {f.format(st.median(v))}）｜今日より低い日 {sum(x < t for x in v)}/21')
v = sorted(R[d]['mer'] for d in past)
P(f"  → 売上÷広告費 {R[T]['mer']:.2f} は 21日の範囲 {v[0]:.2f}〜{v[-1]:.2f} の{'中' if v[0] <= R[T]['mer'] <= v[-1] else '外'}・低いほうから {sum(x < R[T]['mer'] for x in v) + 1}番目")
rate = sum(R[d]['o'] for d in past) / sum(R[d]['ses'] for d in past); e = rate * R[T]['ses']; k = R[T]['o']
pl = lambda e, k: sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(k + 1))
P(f"  注文の見込み（21日の 注文÷来訪 {rate:.2%} × 今日の来訪 {R[T]['ses']:,}）{e:.1f}件 → 実際 {k}件・この数以下になる確率 {pl(e, k):.0%}")
P('  日ごとの来訪（0〜17時台）: ' + '・'.join(f"{d[5:]} {R[d]['ses']:,}" for d in past + [T]))
# ---- ② 時間ごと: 今日 ↔ 11/18〜24 の同じ時間 ----
SH = collections.defaultdict(dict)
for r in json.load(open(B + 'sess_hourly_1118_1125_raw.json'))['rows']: SH[r[0][:10]][int(r[1])] = (int(r[2]), int(r[3]), int(r[4]))
OH = collections.defaultdict(dict)
for r in json.load(open(B + 'sales_hourly_1118_1125_raw.json'))['rows']: OH[r[0][:10]][int(r[1])] = int(r[2])
MH = collections.defaultdict(dict)
for r in table('meta_hourly_1118_1125_raw.json'): MH[r['date']][int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2])] = (z(r['cost']), z(r['impressions']), z(r['link_clicks']))
w7 = [d for d in sorted(SH) if d < T]; assert len(w7) == 7
P('■ ② 時間ごと: 今日 ↔ 11/18〜24 の同じ時間（最小〜最大・中央値）。★＝7日の最小より低い')
low = collections.Counter()
for h in range(0, H + 2):
    s7 = [SH[d].get(h, (0, 0, 0))[0] for d in w7]; a7 = [MH[d].get(h, (0, 0, 0))[0] for d in w7]; c7 = [MH[d].get(h, (0, 0, 0))[2] for d in w7 if d >= '2026-11-19']; o7 = [OH[d].get(h, 0) for d in w7]
    s, a, c, o = SH[T].get(h, (0, 0, 0))[0], MH[T].get(h, (0, 0, 0))[0], MH[T].get(h, (0, 0, 0))[2], OH[T].get(h, 0)
    fs, fa = ('★' if s < min(s7) else ''), ('★' if a < min(a7) else '')
    if h <= H: low['s'] += s < min(s7); low['a'] += a < min(a7)
    P(f"  {h:02d}時台{'（途中）' if h > H else ''}: 来訪 {s}{fs}（{min(s7)}〜{max(s7)}・{st.median(s7):.0f}）｜広告費 {a:,.0f}{fa}（{min(a7):,.0f}〜{max(a7):,.0f}・{st.median(a7):,.0f}）｜クリック {c:.0f}（{min(c7):.0f}〜{max(c7):.0f}）｜注文 {o}（{min(o7)}〜{max(o7)}）")
P(f"  0〜17時台の18時間のうち、7日の最小より低い時間: 来訪 {low['s']}時間・広告費 {low['a']}時間")
for a, b, lab in ((0, 10, '0〜10時台'), (11, 16, '11〜16時台'), (17, 17, '17時台')):
    hs = range(a, b + 1); t_s = sum(SH[T].get(h, (0,))[0] for h in hs); t_a = sum(MH[T].get(h, (0,))[0] for h in hs)
    p_s = [sum(SH[d].get(h, (0,))[0] for h in hs) for d in w7]; p_a = [sum(MH[d].get(h, (0,))[0] for h in hs) for d in w7]
    P(f"  {lab}: 来訪 今日 {t_s:,}｜7日 {min(p_s):,}〜{max(p_s):,}（中央値 {st.median(p_s):,.0f}・今日÷中央値 {t_s / st.median(p_s):.0%}）｜広告費 今日 {t_a:,.0f}｜7日 {min(p_a):,.0f}〜{max(p_a):,.0f}（中央値 {st.median(p_a):,.0f}・{t_a / st.median(p_a):.0%}）")
# ---- ③ キャンペーン別: 0〜17時台の広告費・CPM・クリック率 今日 ↔ 7日の同じ時刻。日予算に対する割合 ----
bud = {}
for r in csv.DictReader(open('data/budget-snapshots.csv', encoding='utf-8')): bud[(r['campaign'], r['adset'])] = (r['snapshot_date'], float(r['daily_budget']))
full = max(d for d, _ in bud.values() if len(d) == 10); cb = collections.Counter()
for (c, a), (d, b) in bud.items():
    if d >= full: cb[c] += b
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '快適マジックインソール v3': '快適マジックインソール'}
P(f'■ ③ キャンペーン別（0〜17時台）: 今日 ↔ 11/18〜24 の同じ時刻の平均（広告費があった日だけ）｜日予算（{full} の記録＋当日の変更）に対する割合')
tc = {r['adcampaign_name']: r for r in camp if r['date'] == T}
tot_t = tot_p = 0
for c, r in sorted(tc.items(), key=lambda x: -z(x[1]['cost'])):
    if z(r['cost']) < 100: continue
    ps = [x for x in camp if x['adcampaign_name'] == c and '2026-11-18' <= x['date'] <= '2026-11-24' and z(x['cost']) > 500]
    b = cb.get(c) or cb.get(REN.get(c, ''), 0)
    t_cpm = z(r['cost']) / z(r['impressions']) * 1000; t_ctr = z(r['link_clicks']) / z(r['impressions']) * 100
    if len(ps) >= 5:
        pc, pi, pk = (sum(z(x[k]) for x in ps) for k in ('cost', 'impressions', 'link_clicks')); tot_t += z(r['cost']); tot_p += pc / len(ps)
        P(f"  {c}: 広告費 {z(r['cost']):,.0f}（7日平均 {pc / len(ps):,.0f}・{z(r['cost']) / (pc / len(ps)):.0%}）・日予算 {b:,.0f} の {z(r['cost']) / b:.0%}｜CPM {t_cpm:,.0f}（7日 {pc / pi * 1000:,.0f}）・クリック率 {t_ctr:.2f}%（7日 {pk / pi * 100:.2f}%）・クリック {z(r['link_clicks']):.0f}（7日平均 {pk / len(ps):.0f}）")
    else:
        P(f"  {c}: 広告費 {z(r['cost']):,.0f}・日予算 {b:,.0f} の {z(r['cost']) / b:.0%}｜CPM {t_cpm:,.0f}・クリック率 {t_ctr:.2f}%・クリック {z(r['link_clicks']):.0f}（出して7日未満）")
P(f"  7日の実績があるキャンペーンの合計: 今日 {tot_t:,.0f} ↔ 7日平均 {tot_p:,.0f}（{tot_t / tot_p:.0%}）")
sh = [sum(MH[d].get(h, (0,))[0] for h in range(H + 1)) / sum(v[0] for v in MH[d].values()) for d in w7]
P(f"  ふだん 0〜17時台までに使う割合（その日の広告費に対して・11/18〜24）: {min(sh):.0%}〜{max(sh):.0%}（中央値 {st.median(sh):.0%}）｜今日 0〜17時台 {R[T]['ad']:,.0f} ÷ 日予算の合計 {sum(cb.values()):,.0f} ＝ {R[T]['ad'] / sum(cb.values()):.0%}")
# ---- ④ 17時台: キャンペーンごとの 16時台 → 17時台 ----
ch = collections.defaultdict(dict)
for r in table('meta_camp_hourly_1125_raw.json'): ch[r['adcampaign_name']][int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2])] = z(r['cost'])
P('■ ④ 今日の 16時台 → 17時台の広告費（キャンペーンごと）: ' + '・'.join(f"{c} {v.get(16, 0):,.0f}→{v.get(17, 0):,.0f}" for c, v in sorted(ch.items(), key=lambda x: -x[1].get(16, 0)) if v.get(16, 0) > 0))
dn = sum(1 for v in ch.values() if v.get(16, 0) > 0 and v.get(17, 0) < v.get(16, 0)); al = sum(1 for v in ch.values() if v.get(16, 0) > 0)
P(f"  下がったキャンペーン {dn}/{al}｜過去7日の 16時台 → 17時台（アカウント）: " + '・'.join(f"{d[5:]} {MH[d][16][0]:,.0f}→{MH[d][17][0]:,.0f}" for d in w7) + f"｜今日 {MH[T][16][0]:,.0f}→{MH[T][17][0]:,.0f}")
# ---- ⑤ 今日の変更履歴（Meta・UTC の 11/25＝日本時間 9時〜） ----
hist = json.load(open(B + 'meta_history_1125_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
ops = collections.Counter((h['operation'], h['campaign_name']) for h in hist)
jst = lambda t: (datetime.datetime.fromisoformat(t.replace('+0000', '+00:00')) + datetime.timedelta(hours=9)).strftime('%H:%M')
P(f'■ ⑤ Meta の変更履歴（日本時間 11/25 9時〜・{len(hist)}件）: ' + '・'.join(sorted({f"{jst(h['timestamp'])} {h['operation']}（{h['campaign_name']}）" for h in hist if h['operation'] in ('CREATE_CAMPAIGN_GROUP', 'AD_ACCOUNT_BILLING_CHARGE', 'FIRST_DELIVERY_EVENT') or 'BUDGET' in h['operation'] and 'SCHEDUL' not in h['operation'] and 'FLEX' not in h['operation'] or 'PAUSE' in h['operation']})))
other = sorted({h['operation'] for h in hist})
P('  出てきた操作の種類: ' + '・'.join(other))
P(f"  予算の金額の変更・停止の操作: {sum(1 for h in hist if h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET') or (h['operation'].endswith('RUN_STATUS') and h['change_values'].get('new_value') in ('オフ', '停止')))}件")
open(B + 'hourly_h17.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
