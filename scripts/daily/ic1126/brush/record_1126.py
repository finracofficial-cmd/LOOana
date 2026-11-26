# -*- coding: utf-8 -*-
"""11/26 17時台のブラシの再開を記録する: ①budget-snapshots.csv に 2026-11-26b（変わった行だけ）②relaunch-log.csv に1行。
金額・ID は meta_history_1126_1724_raw.json と direct_brush_1721_raw.json から読む（このスクリプトに金額・ID は書かない）"""
import csv, os, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../../'
c = json.load(open(D + 'direct_brush_1721_raw.json', encoding='utf-8'))['data']['data']['results'][0]; ag = c['ad_groups'][0]
H = json.load(open(D + 'meta_history_1126_1724_raw.json', encoding='utf-8'))['data']['data']['results']['platform_change_list']
bud = [h for h in H if h['operation'] == 'UPDATE_AD_SET_BUDGET' and h['campaign_id'] == ag['ad_group_id']]; assert len(bud) == 1
old, new = bud[0]['change_values']['old_value']['old_value'], bud[0]['change_values']['new_value']['new_value']; assert new == ag['daily_budget'] and c['status'] == 'ENABLED' and ag['status'] == 'ENABLED'
on = [h for h in H if h['operation'] == 'UPDATE_CAMPAIGN_RUN_STATUS' and h['campaign_id'] == c['campaign_id']]; assert len(on) == 1 and on[0]['change_values']['new_value'] == 'アクティブ'
# ---- ① 予算 ----
F = R + 'data/budget-snapshots.csv'; LAB = '2026-11-26b'; rows = list(csv.DictReader(open(F)))
if not any(r['snapshot_date'] == LAB for r in rows):
    st = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-26')
    for r in rows:
        if r['snapshot_date'] == '2026-11-26a': st[(r['campaign'], r['adset'])] = int(r['daily_budget'])
    k = (c['name'], ag['name']); assert st.get(k, 0) == 0, st.get(k)
    last = [r for r in rows if (r['campaign'], r['adset']) == k]; assert int(last[-1]['daily_budget']) == 0 and int(last[-2]['daily_budget']) == old, (last[-2:], old)   # 止める直前の記録が履歴の「変更前」と同じ
    with open(F, 'a', newline='') as f: csv.writer(f, lineterminator='\r\n').writerow([LAB, k[0], k[1], new])
    before = sum(st.values()); st[k] = new
    print(LAB, f"{k[1]}: 0 → {new:,}（止める前 {old:,}）・合計 {before:,} → {sum(st.values()):,}・配信中のキャンペーン {len({a for (a, b), v in st.items() if v > 0})}")
# ---- ② 出し直しの記録 ----
G = R + 'data/relaunch-log.csv'; L = list(csv.DictReader(open(G, encoding='utf-8', newline='')))
if not any(r['商品'] == c['name'] and r['開始日'] == '2026-11-26' for r in L):
    A = [a for a in ag['ads'] if a['status'] == 'ACTIVE']; assert len(A) == 1; A = A[0]; Bp = [a for a in ag['ads'] if a['status'] == 'PAUSED']; assert len(Bp) == 1; Bp = Bp[0]
    cr = A['creative']; post = [t['post'][0] for t in A['platform_settings']['tracking_specs'] if 'post' in t][0]
    up = [h for h in H if h['operation'] == 'UPDATE_AD_CREATIVE' and h['campaign_id'] == A['id']]; assert len(up) == 1; o, n = up[0]['change_values']['old_value'], up[0]['change_values']['new_value']; assert n[-1] == A['creative_id']
    f = cr['degrees_of_freedom_spec']['creative_features_spec']
    row = [c['name'], '旧キャンペーンで再開', 'A', '2026-11-26', c['campaign_id'], f"{A['name']}（{A['id']}）だけ。{Bp['name']}（{Bp['id']}）は停止", cr['video_title'], cr['asset_id'], f"{post}（前の投稿IDは記録なし）", '8（前は 10/23〜11/17・最後の広告費は 11/17〜18）',
           f"日予算 {old:,}→{new:,}・広告B を停止（11/17 は配信のほぼ全部が B）・広告A のクリエイティブを更新（ID {o[-1]}→{n[-1]}・再審査 → 承認。見出し・本文1本目・サムネイルは前と同じ。何を変えたかは履歴から読めない）・直読で 商品閲覧 {f['product_browsing']['enroll_status']}（11/13 の記録ではオフ）・商品の拡張 {f['product_extensions']['enroll_status']}・ボタン {cr['call_to_action']}・見出し {len(cr['headlines'])}本・本文 {len(cr['descriptions'])}本（全部ブラシの文）",
           '', '', '2026-12-03', 'ic1126/brush/brush_1126.txt。止める前: 通算 1.78・最初の2週 2.06・最後の7日 0.97。17:21 から配信（11/26 は約6.5時間）。2日目の確認 11/28 朝']
    assert len(row) == len(L[0])
    with open(G, 'a', newline='', encoding='utf-8') as fo: csv.writer(fo, lineterminator='\r\n').writerow(row)
    print('relaunch-log: 1行追加', row[:5])
