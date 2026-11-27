# -*- coding: utf-8 -*-
"""11/27 21:5x「ガラスクロスを日予算8千円でだした」: 変更履歴（meta_history_1127_2155_raw.json）・直読（direct_cloth_2156_raw.json）・
商品（products_recent_2156_raw.json）から、①budget-snapshots.csv に 2026-11-27d ②判定の線 を出す。金額・ID は取得ファイルから読む"""
import csv, os, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D + '../../../..')
out = []
def P(s): print(s); out.append(s)
H = json.load(open(D + 'meta_history_1127_2155_raw.json'))['data']['data']['results']['platform_change_list']
c = json.load(open(D + 'direct_cloth_2156_raw.json'))['data']['data']['results'][0]; assert len(c['ad_groups']) == 1; ag = c['ad_groups'][0]; assert len(ag['ads']) == 1; ad = ag['ads'][0]; cr = ad['creative']
mk = [h for h in H if h['operation'] == 'CREATE_AD_SET' and h['campaign_name'] == c['name']]; assert len(mk) == 1 and mk[0]['change_values']['new_value']['new_value'] == ag['daily_budget']
t0 = datetime.datetime.strptime(mk[0]['timestamp'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)
assert any(h['operation'] == 'CREATE_CAMPAIGN_GROUP' and h['campaign_id'] == c['campaign_id'] for h in H) and any(h['operation'] == 'CREATE_AD' and h['campaign_id'] == ad['id'] for h in H)   # キャンペーンも広告も新規（複製ではない）
later = [h for h in H if h['timestamp'][:19] > '2026-11-27T09:09:27' and h['campaign_name'] not in (c['name'], ad['name'])]; assert not later   # 18:09 より後は、ガラスクロスの出稿のほかに操作なし
pr = [p for p in json.load(open(D + 'products_recent_2156_raw.json'))['data']['products']['nodes'] if p['handle'] == cr['final_urls'][0].split('/')[-1]]; assert len(pr) == 1; pr = pr[0]
v = pr['variants']['nodes']; prices = {int(float(x['price'])) for x in v}; assert len(prices) == 1; price = prices.pop(); costs = {x['title']: int(float(x['inventoryItem']['unitCost']['amount'])) for x in v}; lo, hi = min(costs.values()), max(costs.values())
f = cr['degrees_of_freedom_spec']['creative_features_spec']; txt = cr['headlines'] + cr['descriptions']
oth = [w for w in ('ノーズ', 'フック', 'インソール', 'ワイパー', 'ガラスクリーナー', 'スマホホルダー', 'ブラシ', 'クッション', 'サンバイザー', 'レンズ', 'フィルム') if any(w in t for t in txt)]
own = sum(1 for t in cr['descriptions'] if any(w in t for w in ('ガラスクロス', '拭き跡', '拭くだけ', '吸水')))
P(f"■ 出稿（変更履歴・{t0:%m/%d %H:%M}）: キャンペーン {c['name']}（{c['campaign_id']}・新規）・広告セット {ag['ad_group_id']}・日予算 {ag['daily_budget']:,}円・広告{ad['name']}（{ad['id']}・新規）")
P(f"  直読（21:56）: 審査 {ad['review']['status']}・配信 {ad['delivery_status']}・ボタン {cr['call_to_action']}・リンク先 /products/{pr['handle'][:40]}…・動画 {cr['video_title']}（素材 {cr['asset_id']}）・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本（拭き掃除の言葉を含む本文 {own}本・他の商品の言葉 {oth or 'なし'}）・商品の拡張 {f['product_extensions']['enroll_status']}・商品閲覧 {f['product_browsing']['enroll_status']}")
P(f"  見出し: " + '／'.join(cr['headlines']))
P(f"■ 商品: {pr['id'].split('/')[-1]}・テンプレート {pr['templateSuffix']}・売価 {price:,}円（5枚入り1セット）・原価 " + '・'.join(f'{k} {x:,}' for k, x in costs.items()) + f"（原価の割合 {lo/price:.1%}〜{hi/price:.1%}・1セットの粗利 {price-hi:,}〜{price-lo:,}円）・登録 {pr['createdAt'][:10]}・公開 {pr['publishedAt']}・在庫 {pr['totalInventory']:,}")
P(f"■ 判定の線（原価はいちばん高い組み合わせ {hi:,}円で計算）: 事故停止（基準6・購入0のまま）{(price-hi)*3:,}円｜倍率 1.25 ＝ 広告費1万円あたり {10000*1.25/(price-hi):.1f}セット・1.5 ＝ {10000*1.5/(price-hi):.1f}セット・1.94 ＝ {10000*1.94/(price-hi):.1f}セット｜2日目の確認 11/29 朝（11/28 の終日まで。11/27 は出稿が {t0:%H:%M} で、審査が通ってからの配信は2時間に満たない）・7日 12/4 朝（11/27〜12/3）")
F = 'data/budget-snapshots.csv'; LAB = '2026-11-27d'; rows = list(csv.DictReader(open(F)))
if not any(r['snapshot_date'] == LAB for r in rows):
    st = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-27')
    for lab in ('2026-11-27a', '2026-11-27b', '2026-11-27c'):
        for r in rows:
            if r['snapshot_date'] == lab: st[(r['campaign'], r['adset'])] = int(r['daily_budget'])
    k = (c['name'], ag['name']); assert k not in st; before = sum(st.values())
    with open(F, 'a', newline='') as fo: csv.writer(fo, lineterminator='\r\n').writerow([LAB, k[0], k[1], ag['daily_budget']])
    st[k] = ag['daily_budget']; P(f"■ 予算の記録 {LAB}: {k[1]} {ag['daily_budget']:,}・合計 {before:,} → {sum(st.values()):,}・配信中のキャンペーン {len({a for (a, b), x in st.items() if x > 0})}")
    open(D + 'record_cloth.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
