# -*- coding: utf-8 -*-
"""11/27 20:2x「新商品うれないねー」（2WAY防眩サンバイザー・11/27 14:42 出稿・最初の配信 14:57・8,000円/日）
入力: visor_meta_hourly_1127_2027_raw.json（Meta・時間別。取り込みは1時間ほど遅れる）／visor_sales_1127_2027_raw.json（Shopify・注文）／
      visor_sess_hourly_1127_2027_raw.json（Shopify・サンバイザーのページに着いた来訪）／../products_recent_1445_raw.json（売価・原価）／
      ../../../ic1126/breakout/early_1126.txt（10/1 以降の新商品23本の 1日目・2日目までの 個数・広告費）／../../../o1126/sess_mobile_social_1105_1126_raw.json（店のスマホ・social のカート率）
見るもの: いまの数字と、0個が偶然の範囲か。日中の数字なので判定・予算の提案には使わない"""
import json, csv, io, math, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D + '../../../../..')
out = []
def P(s=''): print(s); out.append(s)
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
pr = [p for p in json.load(open(D + '../products_recent_1445_raw.json', encoding='utf-8'))['data']['products']['nodes'] if p['handle'] == 'car-day-and-night-sun-goggles'][0]
PRICE = int(float(pr['variants']['nodes'][0]['price'])); COST = int(float(pr['variants']['nodes'][0]['inventoryItem']['unitCost']['amount'])); GP = PRICE - COST; BUD = 8000
raw = json.load(open(D + 'visor_meta_hourly_1127_2027_raw.json', encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
M = [{k: (v if k in ('hourly_stats_aggregated_by_advertiser_time_zone', 'adcampaign_name', 'ad_name') else (0.0 if v in ('null', '') else float(v))) for k, v in zip(cols, r)} for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
assert all(r['adcampaign_name'] == '2WAY防眩サンバイザー' and r['ad_name'] == 'A' for r in M)
S = json.load(open(D + 'visor_sales_1127_2027_raw.json', encoding='utf-8'))['rows']; orders = sum(int(r[1]) for r in S); units = sum(round(float(r[2]) / PRICE) for r in S)
SS = {}
for h, src, s, c, ck, dn in json.load(open(D + 'visor_sess_hourly_1127_2027_raw.json', encoding='utf-8'))['rows']:
    hh = (int(h[11:13]) + 9) % 24; x = SS.setdefault(hh, [0, 0, 0, 0, 0]); x[0] += int(s); x[1] += int(c); x[2] += int(ck); x[3] += int(dn); x[4] += int(s) if src == 'social' else 0
P('■ ① 今日ここまで（Meta は 20:27 の取得・Shopify は 20:27。最初の配信は 14:57）')
for r in M:
    h = int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2]); s = SS.get(h, [0] * 5); k = r['link_clicks']
    P(f"  {h}時台: 広告費 {r['cost']:,.0f}・表示 {r['impressions']:.0f}・クリック {k:.0f}・来訪（Meta）{r['landing_page_views']:.0f}・カート（Meta）{r['offsite_conversions_fb_pixel_add_to_cart']:.0f}・購入（Meta）{r['offsite_conversions_fb_pixel_purchase']:.0f}｜Shopify: ページの来訪 {s[0]}（social {s[4]}）・カート {s[1]}・決済画面 {s[2]}・購入 {s[3]}")
c = sum(r['cost'] for r in M); i = sum(r['impressions'] for r in M); k = sum(r['link_clicks'] for r in M); lpv = sum(r['landing_page_views'] for r in M); atc = sum(r['offsite_conversions_fb_pixel_add_to_cart'] for r in M); v3 = sum(r['action_video_view'] for r in M)
ts = [sum(x[j] for x in SS.values()) for j in range(5)]
P(f"  計: 広告費 {c:,.0f}（日予算 {BUD:,} の {c/BUD:.0%}）・表示 {i:,.0f}・クリック {k:.0f}（クリック率 {k/i:.2%}）・クリック1回 {c/k:.0f}円・CPM {c/i*1000:,.0f}・3秒まで見た÷表示 {v3/i:.0%}・来訪÷クリック {lpv/k:.2f}・カート（Meta）{atc:.0f}｜Shopify: ページの来訪 {ts[0]}（social {ts[4]}）・カート {ts[1]}・決済画面 {ts[2]}・注文 {orders}件・{units}個")
s2 = 2 / math.sqrt(k); P(f"  {k:.0f}クリックだと、クリック率・クリック1回の値段は ×{math.exp(-s2):.2f}〜{math.exp(s2):.2f} の幅（±2σ）＝クリック1回 {c/k*math.exp(-s2):.0f}〜{c/k*math.exp(s2):.0f}円")
P(f"■ ② クリックの値段から見た「要る買われ方」（1個の粗利 {GP:,}円・クリック1回 {c/k:.0f}円のままとして）")
for m_ in (1.25, 1.5, 1.94):
    need = c / k * m_ / GP; e = k * need
    P(f"  倍率 {m_}: 注文÷クリック {need:.1%}（{1/need:.0f}クリックに1個）が要る → {k:.0f}クリックなら {e:.1f}個の見込み・0個になる確率 {math.exp(-e):.0%}")
st = [r for r in json.load(open('scripts/daily/o1126/sess_mobile_social_1105_1126_raw.json', encoding='utf-8'))['rows'] if '2026-11-20' <= r[0][:10] <= '2026-11-26']
cr = sum(int(r[2]) for r in st) / sum(int(r[1]) for r in st); br = sum(int(r[4]) for r in st) / sum(int(r[1]) for r in st)
P(f"  店のスマホ・social の来訪（11/20〜26）: カートに入れる割合 {cr:.2%}・買う率 {br:.2%} → サンバイザーの social の来訪 {ts[4]} なら カート {ts[4]*cr:.1f}・購入 {ts[4]*br:.1f} の見込み → 実際 カート {ts[1]}（{ts[1]}以下 {ple(ts[1], ts[4]*cr):.0%}）・購入 {ts[3]}（0 になる確率 {math.exp(-ts[4]*br):.0%}）")
# ---- 過去の新商品の1日目 ----
E = {}; grp = None
for l in open('scripts/daily/ic1126/breakout/early_1126.txt', encoding='utf-8'):
    if l.startswith('■ 当たり'): grp = 'hit'
    elif l.startswith('■ それ以外'): grp = 'oth'
    elif l.startswith('■'): grp = None
    m = re.match(r'^  (.+?)（(\d\d-\d\d)〜）: (\d+)個・([\d,]+)円・[\d.]+｜(\d+)個・([\d,]+)円・([\d.]+)｜', l)
    if grp and m: E[m.group(1)] = dict(g=grp, q1=int(m.group(3)), c1=int(m.group(4).replace(',', '')), q2=int(m.group(5)), c2=int(m.group(6).replace(',', '')), m2=float(m.group(7)))
assert sum(1 for e in E.values() if e['g'] == 'hit') == 6 and len(E) == 23
P(f"■ ③ 過去の新商品23本の1日目と並べる（個数。まとめ買いがあるので注文数より多めに出る）")
for g_, lab in (('hit', '当たり6本'), ('oth', 'それ以外17本')):
    xs = [e for e in E.values() if e['g'] == g_]; q = sum(e['q1'] for e in xs); cc = sum(e['c1'] for e in xs); lam = c * q / cc
    big = [e for e in xs if e['c1'] >= 2400]; z = sum(1 for e in big if e['q1'] == 0)
    P(f"  {lab}の1日目: {q}個／{cc:,}円＝広告費1万円あたり {q/cc*10000:.1f}個 → {c:,.0f}円なら {lam:.1f}個の見込み・0個になる確率 {math.exp(-lam):.0%}（個数で数えた目安）｜1日目に 2,400円以上使った {len(big)}本のうち 0個 {z}本")
ph = math.exp(-c * sum(e['q1'] for e in E.values() if e['g'] == 'hit') / sum(e['c1'] for e in E.values() if e['g'] == 'hit')); po = math.exp(-c * sum(e['q1'] for e in E.values() if e['g'] == 'oth') / sum(e['c1'] for e in E.values() if e['g'] == 'oth'))
for prior, lab in ((6 / 23, '新商品ぜんぶの当たりの割合 6/23'), (4 / 7, '車まわりの当たりの割合 4/7')):
    P(f"  もともと {lab}＝{prior:.0%} → いま 0個を見たあと {prior*ph/(prior*ph+(1-prior)*po):.0%}（上の2つの確率で割り引いた目安。{c:,.0f}円ぶんの情報しかない）")
z0 = sorted([(n, e) for n, e in E.items() if e['q1'] == 0 and e['c1'] >= 2400], key=lambda x: -x[1]['m2'])
P('  1日目 2,400円以上で 0個だった10本の「2日目までの通算」: ' + '・'.join(f"{n} {e['q2']}個／{e['c2']:,}円（{e['m2']:.2f}）" for n, e in z0))
P(f"  → 2日目までに 1.5 以上へ戻したのは {sum(1 for n, e in z0 if e['m2'] >= 1.5)}本／{len(z0)}本（当たりになった商品は無い）")
# ---- 見る線 ----
hrs = [r for r in M if r['cost'] >= 100 and int(r['hourly_stats_aggregated_by_advertiser_time_zone'][:2]) < 20]; ph_ = sum(r['cost'] for r in hrs) / len(hrs)
lo, hi = c + 3 * BUD / 24, min(BUD, c + 4 * ph_)
P(f"■ ④ 見る線（基準どおり。日中の数字では動かさない）")
P(f"  今日の終わりの広告費の見込み: {lo:,.0f}〜{hi:,.0f}円（15〜19時台は1時間 {ph_:,.0f}円。残り3〜4時間ぶん）")
for m_ in (1.25, 1.5, 1.94):
    P(f"  2日目（11/28）の終日までの通算で倍率 {m_}: 広告費 {lo+BUD:,.0f}〜{hi+BUD:,.0f}円 → {(lo+BUD)*m_/GP:.1f}〜{(hi+BUD)*m_/GP:.1f}個（1個の粗利 {GP:,}円。まとめ買いの値引きがあると少し増える）")
stop = GP * 3
P(f"  事故停止（基準6）: 購入0のまま {stop:,}円。今日の終わりが {lo:,.0f}〜{hi:,.0f}円なら、明日あと {stop-hi:,.0f}〜{stop-lo:,.0f}円で届く＝日予算 {BUD:,} の {(stop-hi)/BUD:.0%}〜{(stop-lo)/BUD:.0%} を使ったころ")
P(f"  2日目の確認は 11/29 朝（基準5: クリック率 4.5%超で延長／2.5%未満かつカート0で停止。いまのクリック率 {k/i:.2%}・カート {ts[1]}）")
hist = json.load(open(D + 'meta_history_1127_2027_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
late = [x for x in hist if x['timestamp'][:19] > '2026-11-27T05:57:42']
P('■ ⑤ 変更履歴（14:57 の最初の配信より後）: ' + ('・'.join(f"{(int(x['timestamp'][11:13])+9)%24}:{x['timestamp'][14:16]} {x['operation']}（{x['campaign_name']} {x['campaign_id']}）" for x in late) or 'なし') + '｜停止・予算の変更は ' + str(sum(1 for x in late if 'RUN_STATUS' in x['operation'] or 'BUDGET' in x['operation'])) + '件')
open(D + 'visor_h20.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
