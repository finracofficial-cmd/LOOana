# -*- coding: utf-8 -*-
"""11/26 19時台「ぶらしうれないねー」（再開は 17:21）
入力: brush_meta_1126_1928_raw.json（Meta・11/26・広告別。19:28 の取得）／brush_sess_hourly_1126_1930_raw.json（Shopify・ブラシのページに着いた来訪・時間×入口）／
      brush_sales_1124_1126_1930_raw.json（Shopify・ブラシの注文 11/24〜26）／meta_history_1126_1930_raw.json（変更履歴の新しい4件）／
      ../brush_daily_1023_1126_raw.json・../brush_sales_daily_1023_1126_raw.json（過去の 注文÷クリック）
見るもの: いまの量で「注文0」が偶然の範囲か。日中の数字なので、判定・予算の提案には使わない"""
import json, csv, io, math, os, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'
out = []
def P(s=''): print(s); out.append(s)
def meta(f):
    raw = json.load(open(f, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    return [{k: (v if k in ('date', 'adcampaign_name', 'ad_name') else (0.0 if v in ('null', '') else float(v))) for k, v in zip(cols, r)} for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
T = meta(D + 'brush_meta_1126_1928_raw.json'); assert len(T) == 1 and T[0]['ad_name'] == 'A'; t = T[0]
c, i, k, l, v3, a, p = (t[x] for x in ('cost', 'impressions', 'link_clicks', 'landing_page_views', 'action_video_view', 'offsite_conversions_fb_pixel_add_to_cart', 'offsite_conversions_fb_pixel_purchase'))
P(f"■ ① いま（Meta・19:28 の取得。取り込みは1時間ほど遅れる）: 広告A だけ・広告費 {c:,.0f}円・表示 {i:,.0f}・クリック {k:.0f}（クリック率 {k/i:.2%}）・クリック1回 {c/k:.0f}円・CPM {c/i*1000:,.0f}・3秒まで見た÷表示 {v3/i:.0%}・来訪（Meta）{l:.0f}・カート {a:.0f}・購入 {p:.0f}")
S = json.load(open(D + 'brush_sales_1124_1126_1930_raw.json', encoding='utf-8')); o_today = sum(int(r[1]) for r in S['rows'] if r[0][:10] == '2026-11-26')
P(f"  Shopify（19:30）: ブラシの注文 11/24〜26 は {S['rowCount']}行＝今日 {o_today}件")
ss = json.load(open(D + 'brush_sess_hourly_1126_1930_raw.json', encoding='utf-8'))['rows']
aft = [r for r in ss if int(r[0]) >= 17]; bef = [r for r in ss if int(r[0]) < 17]
f = lambda rs, s=None: sum(int(r[2]) for r in rs if s is None or r[1] == s)
P(f"  ブラシのページに着いた来訪（Shopify）: 17時台から {f(aft)}（social {f(aft,'social')}・direct {f(aft,'direct')}）・カート {sum(int(r[3]) for r in aft)}・決済画面 {sum(int(r[4]) for r in aft)}・購入 {sum(int(r[5]) for r in aft)}｜0〜16時台 {f(bef)}（広告なし）")
H = json.load(open(D + 'meta_history_1126_1930_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
last = max(h['timestamp'] for h in H); jst = (datetime.datetime.strptime(last[:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)).strftime('%H:%M')
P(f"  変更履歴（19:30）: いちばん新しい操作は {jst}（{[h for h in H if h['timestamp']==last][0]['change_values']['new_value']}）＝再開のあと何も変えていない")
# ---- 過去の 注文÷クリック ----
M = {}
for r in meta(D + '../brush_daily_1023_1126_raw.json'):
    x = M.setdefault(r['date'], dict(c=0, i=0, k=0)); x['c'] += r['cost']; x['i'] += r['impressions']; x['k'] += r['link_clicks']
O = {r[0][:10]: int(r[1]) for r in json.load(open(D + '../brush_sales_daily_1023_1126_raw.json', encoding='utf-8'))['rows']}
def rng(a, b):
    a, b = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b); return [(a + datetime.timedelta(n)).isoformat() for n in range((b - a).days + 1)]
def per(ds): kk = sum(M[d]['k'] for d in ds if d in M); return sum(O.get(d, 0) for d in ds) / kk, sum(M[d]['c'] for d in ds if d in M) / kk, kk / sum(M[d]['i'] for d in ds if d in M)
P('■ ② 注文0 は偶然の範囲か（クリック数 × 過去の 注文÷クリック ＝ 見込みの注文数。0件になる確率はポアソン）')
for nm, ds in (('最初の2週（10/23〜11/5）', rng('2026-10-23', '2026-11-05')), ('止める前の12日（11/6〜17）', rng('2026-11-06', '2026-11-17'))):
    r, cpc, ctr = per(ds); e = k * r
    P(f"  {nm}: 注文÷クリック {r:.2%}（クリック1回 {cpc:.0f}円・クリック率 {ctr:.2%}）→ {k:.0f}クリックの見込み {e:.2f}件・0件になる確率 {math.exp(-e):.0%}｜1件を見込めるクリック数 {1/r:.0f}・いまのクリック1回 {c/k:.0f}円なら広告費 {c/k/r:,.0f}円")
s = 2 / math.sqrt(k); P(f"  クリック率・クリック1回の値段は {k:.0f}クリックだと幅が ×{math.exp(-s):.2f}〜{math.exp(s):.2f}（±2σ）＝良し悪しは言えない")
d1 = M['2026-10-23']; P(f"  ブラシの最初の日（10/23）: 広告費 {d1['c']:,.0f}・{d1['k']:.0f}クリック・クリック1回 {d1['c']/d1['k']:.0f}円・注文 {O['2026-10-23']}件（何円めで最初の注文が入ったかは日別の数字では分からない）")
P('■ ③ 線（どれも「使った広告費」で見る。時刻では見ない）')
P('  過去の当たり6本の1日目（ic1126/breakout/early_1126.txt・新商品の数字）: 5本は 2,569〜4,682円 で 2〜5個、1本は 1,144円 で 0個')
P(f"  事故停止（基準6）: 購入0のまま 10,140円｜いま {c:,.0f}円（{c/10140:.0%}）")
P('  2日目の確認: 11/28 朝（11/27 の終日まで）。通算の倍率 1.5 ＝ 広告費1万円あたり注文 3.8件')
open(D + 'brush_h19.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
