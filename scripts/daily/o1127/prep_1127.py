# -*- coding: utf-8 -*-
"""11/28 定例: Meta・Shopify の取得結果（*_raw.json・会話の記録からそのまま保存）を、毎日のスクリプトが読む形のテキストにする。
Meta は 11/28 04時台に data_query（fresh・1日ずつ）で取得: 11/26＝確定・11/27＝暫定（04時台の取得。確定値は翌日に取り直す）"""
import json, os, re, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; P = D + '../o1126/'
def table(f):
    t = json.load(open(D + f))['data']['data']; rows = []
    for l in t.split('\n')[1:]:
        l = l.strip()
        if not l: continue
        if l.startswith('"'): h, rest = l[1:].split('",', 1); rows.append([h] + rest.split(','))
        else: rows.append(l.split(','))
    return rows
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
ads = {d: [(r[1], r[2], r[3], z(r[4]), z(r[5]), z(r[6]), z(r[7]), z(r[8]), z(r[9])) for r in table(f) if r[0] == d and z(r[4])] for d, f in (('2026-11-26', 'meta_ad_1126_raw.json'), ('2026-11-27', 'meta_ad_1127_raw.json'))}
# キャンペーン別
out = ['# data_query FA fresh・11/28 04時台取得（1日ずつ・広告別を足したもの）・11/26（確定）と11/27（暫定）のキャンペーン別 date,campaign,cost,imp,link_clicks,LPV,ATC,purchase（null→0・広告費0の行は除いた）']
camp = {}
for d in ads:
    c = collections.OrderedDict()
    for r in ads[d]:
        x = c.setdefault(r[0], [0] * 6)
        for i in range(6): x[i] += r[3 + i]
    camp[d] = c
    for k in sorted(c): out.append(','.join([d, k] + [str(v) for v in c[k]]))
open(D + 'meta_camp_1126_1127_raw.txt', 'w').write('\n'.join(out) + '\n')
# 広告別（購入つき）
out = ['# data_query FA fresh・11/28 04時台取得（1日ずつ）。広告費0の行は除いた。date,campaign,adset,ad,cost,imp,link_clicks,purchase（Meta 計上・null→0）。11/26 は確定・11/27 は暫定']
for d in ads:
    for r in ads[d]: out.append(','.join([d, r[0], r[1], r[2], str(r[3]), str(r[4]), str(r[5]), str(r[8])]))
open(D + 'ad_purchase_1126_1127.txt', 'w').write('\n'.join(out) + '\n')
# 広告別の積み上げ（10/26〜）: 11/26 を確定値に置き換え、11/27 を足す
old = [l.rstrip('\n') for l in open(P + 'ad_level_1026_1126.txt') if l[0] != '#' and not l.startswith('2026-11-26,')]
out = ['# data_query FA・10/26〜11/22 は o1126/ad_level_1026_1126.txt から、11/26（確定）・11/27（暫定）は 11/28 04時台の取得（1日ずつ）で置き換え。date,campaign,adset,ad,cost,imp,link_clicks（購入は o1127/ad_purchase_1126_1127.txt）'] + old
for d in ads:
    for r in ads[d]: out.append(','.join([d, r[0], r[1], r[2], str(r[3]), str(r[4]), str(r[5])]))
open(D + 'ad_level_1026_1127.txt', 'w').write('\n'.join(out) + '\n')
# アカウントの日別（10/4〜）: date,cost,imp,reach(0),link_clicks,LPV,ATC,purchase
old = [l.rstrip('\n') for l in open(P + 'meta_acct_daily_1004_1126.txt') if l[0] != '#' and not l.startswith('2026-11-26,')]
out = ['# o1126/meta_acct_daily_1004_1126.txt の 11/26 を確定値に置き換え、11/27（暫定）を足したもの。o1127/meta_camp_1126_1127_raw.txt の合計（reach は足せないので 0）'] + old
for d in ads:
    t = [sum(c[i] for c in camp[d].values()) for i in range(6)]; out.append(','.join([d, str(t[0]), str(t[1]), '0'] + [str(x) for x in t[2:]]))
open(D + 'meta_acct_daily_1004_1127.txt', 'w').write('\n'.join(out) + '\n')
# 予算（data_query・取り込みが数時間遅れることがある）
out = ['# data_query FA fresh・11/28 04時台取得（11/27 の広告セット別・日予算は取得時点の値）campaign,adset,status,daily_budget,cost（11/27）',
       '# data_query の日予算は 11/28 04時台には今の値が出ている（11/27 00:17 の変更後の ガラス主力 21000・W固定 -sab 8500・4-in-1 11000 と、新しい2本の 8000）。伸縮ワックス洗車ブラシは CAMPAIGN_PAUSED（11/27 14:18 停止・広告費は停止までの分）。予算の正は変更履歴から作った記録（2026-11-27＋a＋b＋c＋d）',
       '# 同じ時刻に campaign_and_resource_get（status ENABLED）で直読: 配信中は ' + str(len(json.load(open(D + 'campaigns_enabled_1128_raw.json'))['data']['data']['results'])) + 'キャンペーン（11/27 00時台の12本 − 伸縮ワックス洗車ブラシ〔14:18 停止〕＋ 2WAY防眩サンバイザー〔14:42 出稿〕＋ クリア仕上げガラスクロス〔21:52 出稿〕）。変更履歴（meta_history_1127utc_0435_raw.json）のいちばん新しい操作は 11/27 22:37 のガラスクロスの配信開始＝21:52 の出稿のあと、予算の変更・停止は 0件（11/28 04:35 まで）']
for r in table('budgets_1128_raw.json'): out.append(','.join([r[0], r[1], r[2], str(z(r[3])), str(z(r[4]))]))
open(D + 'budgets_1128.txt', 'w').write('\n'.join(out) + '\n')
# 時間別
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
out = ['# 11/28 04時台取得。11/27 の時間別', '# V＝Shopify FROM sales SHOW orders, gross_sales, discounts GROUP BY hour_of_day: hour,orders,gross,disc（行のない時間は注文0）',
       '# T＝Shopify FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, sessions_that_completed_checkout GROUP BY hour_of_day: hour,sessions,cart,checkout,done',
       '# MH＝Meta data_query アカウント・時間別（fresh）: hour,cost,imp,LPV,ATC,purchase,link_click']
for h, o, g, dc in json.load(open(D + 'hourly_sales_1127_raw.json'))['rows']: out.append(f'V,{h},{o},{g},{-int(dc)}')
for r in json.load(open(D + 'hourly_sess_1127_raw.json'))['rows']: out.append('T,' + ','.join(r))
for r in table('meta_hourly_1127_raw.json'): out.append(f'MH,{int(r[0][:2])},{z(r[1])},{z(r[2])},{z(r[4])},{z(r[5])},{z(r[6])},{z(r[3])}')
open(D + 'hourly_1127_raw.txt', 'w').write('\n'.join(out) + '\n')
# 商品別・日別の注文
out = ['# 11/28 04時台取得。FROM sales SHOW orders, gross_sales, discounts, net_items_sold GROUP BY product_title, day SINCE 2026-11-26 UNTIL 2026-11-27。date,name,orders,gross,disc,items（VIP特典の行は除いた）']
for t, d, o, g, dc, q in json.load(open(D + 'orders_by_product_1126_1127_raw.json'))['rows']:
    if not t or t.startswith('VIP特典'): continue
    if int(o) == 0 and int(g) == 0: continue   # 返品だけの行（11/26 コードレスダブルミスト加湿器 −1個）は注文の表に入れない
    out.append(','.join([d, nm(t), o, g, str(-int(dc)), q]))
open(D + 'orders_by_product_1126_1127.txt', 'w').write('\n'.join(out) + '\n')
# VIP特典の行（対象＝2個以上または7,000円以上）。11/27 は 7,000円以上の注文だけを graphql で取り（bands_vip_1127_raw.json の vip）、2個以上の注文は ShopifyQL（multi_orders_1127_raw.json）で数えた
import datetime
VIP = {'15420006727922', '15412971831538'}; SHIP = '8934499582194'
bv = json.load(open(D + 'bands_vip_1127_raw.json'))['data']; nodes = bv['vip']['nodes']; assert len(nodes) == bv['b7']['count'] and not bv['vip']['pageInfo']['hasNextPage']
multi = json.load(open(D + 'multi_orders_1127_raw.json'))['rows']
assert all(int(g) + int(dc) >= 7000 for _, q, g, dc in multi), '2個以上で7,000円未満の注文がある→その注文の行を別に取ること'
out = [f'# 11/28 04時台取得。graphql orders（created_at 11/27 00:00〜24:00 JST・current_total_price>=7000・{len(nodes)}件）。2個以上の注文は ShopifyQL で {len(multi)}件・どれも値引後 7,000円以上＝上の {len(nodes)}件に含まれる（対象＝2個以上または7,000円以上）: name,JSTの時刻,個数（VIP特典を除く）,合計,VIP特典の行（1=あり）,行の形']
for o in nodes:
    li = [(l['product']['id'].split('/')[-1], l['quantity']) for l in o['lineItems']['nodes']]
    real = [(p, q) for p, q in li if p not in VIP and p != SHIP]; q = sum(x[1] for x in real); tot = float(o['currentTotalPriceSet']['shopMoney']['amount'])
    t = (datetime.datetime.fromisoformat(o['createdAt'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)); assert t.strftime('%Y-%m-%d') == '2026-11-27', t
    shape = f'{q}個の1行' if len(real) == 1 else ('同じ商品を' + '・'.join(str(x[1]) for x in real) + '個ずつ' + f'{len(real)}行' if len({p for p, _ in real}) == 1 else f'別の商品 {len(real)}行')
    out.append(f"{o['name']},{t.strftime('%H:%M')},{q},{tot:.0f},{int(any(p in VIP for p, _ in li))},{shape}")
open(D + 'vip_line_1127_raw.txt', 'w').write('\n'.join(out) + '\n')
# 日別の来訪（10/4〜）: o1126 の表に 11/27 の1行を足す
sd = json.load(open(P + 'sess_daily_1004_1126.json')); r = json.load(open(D + 'sess_1127_raw.json'))['rows'][0]
assert sd['rows'][-1][0] == '2026-11-26'; sd['rows'].append(['2026-11-27'] + r); json.dump(sd, open(D + 'sess_daily_1004_1127.json', 'w'), ensure_ascii=False)
for d in ads: print(d, '広告費', sum(c[0] for c in camp[d].values()), 'キャンペーン', len(camp[d]))
print(open(D + 'vip_line_1127_raw.txt').read())
