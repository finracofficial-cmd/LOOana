# -*- coding: utf-8 -*-
"""budget-snapshots.csv に 2026-11-26 の全体スナップショットを足す（11/26 00:1x）。
もと＝2026-11-25 の全体＋途中の記録 a〜c（ワイパー 24,000・ドア 8,000・卓上加湿器 停止 0・フィルム v2 12,000・ブランケット v2 8,000・シートボックス v2 8,000）。
確かめ方: ①直読（campaign_and_resource_get・00:1x）ガラス2本・ナノ２ ②data_query（budgets_1126.txt）と全部の行が同じであること
③変更履歴（meta_history_1125_1126_0015_raw.json・日本時間 11/25 9時〜11/26 00:1x）に予算の金額の変更・停止が無いこと ④配信中のキャンペーンの一覧（campaigns_enabled_1126_raw.json）と同じであること"""
import csv, os, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-26'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict()
for r in rows:
    if r['snapshot_date'] == '2026-11-25': state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
assert len(state) == 21, len(state)
for lab in ('2026-11-25a', '2026-11-25b', '2026-11-25c'):
    for r in rows:
        if r['snapshot_date'] == lab: state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
# ① 直読
direct = {}
for f in ('direct_glass_0010_raw.json', 'direct_nano_0010_raw.json'):
    c = json.load(open(D + f))['data']['data']['results'][0]; assert c['status'] == 'ENABLED', c['name']
    for a in c['ad_groups']:
        if a['status'] == 'ENABLED': direct[(REN.get(c['name'], c['name']), a['name'])] = a['daily_budget']
for k, v in direct.items(): assert state[k] == v, ('直読と記録が違う', k, state[k], v)
# ② data_query
seen = set()
for l in open(D + 'budgets_1126.txt'):
    if l[0] == '#': continue
    c, a, st, b, cost = l.strip().split(','); k = (REN.get(c, c), a); seen.add(k)
    assert k in state, ('記録にない広告セット', k)
    assert state[k] == (int(b) if st == 'ACTIVE' else 0), ('data_query と記録が違う', k, state[k], st, b)
assert {k for k, v in state.items() if v > 0} <= seen, '予算のある広告セットが data_query に無い'
# ③ 変更履歴
hist = json.load(open(D + 'meta_history_1125_1126_0015_raw.json'))['data']['data']['results']['platform_change_list']
bad = [h for h in hist if h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET') or (h['operation'].endswith('RUN_STATUS') and h['change_values'].get('new_value') in ('オフ', '停止', '一時停止'))]
assert not bad, bad
# ④ 配信中の一覧
enabled = {REN.get(c['name'], c['name']) for c in json.load(open(D + 'campaigns_enabled_1126_raw.json'))['data']['data']['results']}
assert {k[0] for k, v in state.items() if v > 0} == enabled, (enabled ^ {k[0] for k, v in state.items() if v > 0})
with open(F, 'a', newline='') as f:
    w = csv.writer(f, lineterminator='\r\n'); [w.writerow([LAB, k[0], k[1], v]) for k, v in state.items()]
print(LAB, len(state), '行・合計', sum(state.values()), '・直読で確かめた', len(direct), '本・変更履歴', len(hist), '件（予算の変更・停止 0件）')
