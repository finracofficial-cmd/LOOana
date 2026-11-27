# -*- coding: utf-8 -*-
"""11/27 14:4x「サンバイザーを新たに日予算8千円でやった」: 変更履歴（meta_history_1127_1443_raw.json）・直読（direct_visor_1445_raw.json）・
商品（products_recent_1445_raw.json）から、①budget-snapshots.csv に 2026-11-27c ②判定の線 を出す。金額・ID は取得ファイルから読む"""
import csv, os, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D + '../../../..')
out = []
def P(s): print(s); out.append(s)
H = json.load(open(D + 'meta_history_1127_1443_raw.json'))['data']['data']['results']['platform_change_list']
c = json.load(open(D + 'direct_visor_1445_raw.json'))['data']['data']['results'][0]; ag = c['ad_groups'][0]; ad = ag['ads'][0]; cr = ad['creative']
mk = [h for h in H if h['operation'] == 'CREATE_AD_SET' and h['campaign_name'] == c['name']]; assert len(mk) == 1 and mk[0]['change_values']['new_value']['new_value'] == ag['daily_budget']
t0 = datetime.datetime.strptime(mk[0]['timestamp'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)
assert any(h['operation'] == 'CREATE_CAMPAIGN_GROUP' and h['campaign_id'] == c['campaign_id'] for h in H) and any(h['operation'] == 'CREATE_AD' and h['campaign_id'] == ad['id'] for h in H)   # キャンペーンも広告も新規（複製ではない）
pr = [p for p in json.load(open(D + 'products_recent_1445_raw.json'))['data']['products']['nodes'] if p['handle'] == cr['final_urls'][0].split('/')[-1]]; assert len(pr) == 1; pr = pr[0]
v = pr['variants']['nodes']; assert len(v) == 1; price = int(float(v[0]['price'])); cost = int(float(v[0]['inventoryItem']['unitCost']['amount']))
f = cr['degrees_of_freedom_spec']['creative_features_spec']; txt = cr['headlines'] + cr['descriptions']
oth = [w for w in ('ノーズ', 'フック', 'インソール', 'ワイパー', 'ガラスクリーナー', 'スマホホルダー', 'ブラシ', 'クッション') if any(w in t for t in txt)]
P(f"■ 出稿（変更履歴・{t0:%m/%d %H:%M}）: キャンペーン {c['name']}（{c['campaign_id']}・新規）・広告セット {ag['ad_group_id']}・日予算 {ag['daily_budget']:,}円・広告{ad['name']}（{ad['id']}・新規）")
P(f"  直読（14:45）: 審査 {ad['review']['status']}・配信 {ad['delivery_status']}・ボタン {cr['call_to_action']}・リンク先 /products/{pr['handle']}・動画素材 {cr['asset_id']}・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本（本文は6本とも「サンバイザー」か「レンズ」を含む={all(any(w in t for w in ('サンバイザー','レンズ')) for t in cr['descriptions'])}・他の商品の言葉 {oth or 'なし'}）・商品の拡張 {f['product_extensions']['enroll_status']}・商品閲覧 {f['product_browsing']['enroll_status']}")
P(f"■ 商品: {pr['id'].split('/')[-1]}・売価 {price:,}円・原価 {cost:,}円（原価の割合 {cost/price:.1%}・1個の粗利 {price-cost:,}円）・登録 {pr['createdAt'][:10]}・公開 {pr['publishedAt']}")
P(f"■ 判定の線: 事故停止（基準6・購入0のまま）{(price-cost)*3:,}円｜倍率 1.25 ＝ 広告費1万円あたり {10000*1.25/(price-cost):.1f}個・1.5 ＝ {10000*1.5/(price-cost):.1f}個・1.94 ＝ {10000*1.94/(price-cost):.1f}個｜2日目の確認 11/29 朝（11/28 の終日まで）・7日 12/4 朝（11/27〜12/3）")
F = 'data/budget-snapshots.csv'; LAB = '2026-11-27c'; rows = list(csv.DictReader(open(F)))
if not any(r['snapshot_date'] == LAB for r in rows):
    st = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-27')
    for lab in ('2026-11-27a', '2026-11-27b'):
        for r in rows:
            if r['snapshot_date'] == lab: st[(r['campaign'], r['adset'])] = int(r['daily_budget'])
    k = (c['name'], ag['name']); assert k not in st; before = sum(st.values())
    with open(F, 'a', newline='') as fo: csv.writer(fo, lineterminator='\r\n').writerow([LAB, k[0], k[1], ag['daily_budget']])
    st[k] = ag['daily_budget']; P(f"■ 予算の記録 {LAB}: {k[1]} {ag['daily_budget']:,}・合計 {before:,} → {sum(st.values()):,}・配信中のキャンペーン {len({a for (a, b), x in st.items() if x > 0})}")
open(D + 'record_visor.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
