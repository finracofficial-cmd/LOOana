# -*- coding: utf-8 -*-
"""budget-snapshots.csv に 2026-11-27 の全体スナップショットを足す（11/27 00:2x）。
もと＝2026-11-26 の全体＋途中の記録 a（00:23〜00:25 ナノ２・ワイパー・インソール v3 の変更と v2 3本の停止）＋ b（17:18 洗車ブラシの再開）。
確かめ方: ①直読（campaign_and_resource_get・00:2x）ナノ２・ワイパー・インソール v3（data_query の日予算が 11/26 00時台の変更の前の値のままだったので、この3本を直読した）
②data_query（budgets_1127.txt）: ①の3本は「変更の前の値」で出ていること、キャンペーンを止めた3本は広告セットが ACTIVE のまま出ること、それ以外は記録と同じであること
③変更履歴: 11/26 00:25（meta_history_1125utc_0020_raw.json のいちばん新しい操作）〜 17:16（ic1126/brush/meta_history_1126_1724_raw.json）〜 11/27 00:1x（meta_history_1126_1127_0015_raw.json）に、記録していない予算の変更・停止が無いこと
④配信中のキャンペーンの一覧（campaigns_enabled_1127_raw.json）と同じであること"""
import csv, os, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-27'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict(); prev = {}
for r in rows:
    if r['snapshot_date'] == '2026-11-26': state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
assert len(state) == 23 and sum(state.values()) == 202000, (len(state), sum(state.values()))
for lab in ('2026-11-26a', '2026-11-26b'):
    for r in rows:
        if r['snapshot_date'] == lab: k = (r['campaign'], r['adset']); prev[k] = state.get(k, 0); state[k] = int(r['daily_budget'])
H = lambda f: json.load(open(f))['data']['data']['results']['platform_change_list']
# ① 直読
direct = {}
for f in ('direct_nano_0020_raw.json', 'direct_wiper_0020_raw.json', 'direct_insole_0020_raw.json'):
    c = json.load(open(D + f))['data']['data']['results'][0]; assert c['status'] == 'ENABLED', c['name']
    for a in c['ad_groups']:
        if a['status'] == 'ENABLED': direct[(REN.get(c['name'], c['name']), a['name'])] = a['daily_budget']
assert len(direct) == 3
for k, v in direct.items(): assert state[k] == v, ('直読と記録が違う', k, state[k], v)
# ④ 配信中の一覧（②で使うので先に読む）
enabled = {REN.get(c['name'], c['name']) for c in json.load(open(D + 'campaigns_enabled_1127_raw.json'))['data']['data']['results']}
assert {k[0] for k, v in state.items() if v > 0} == enabled, (enabled ^ {k[0] for k, v in state.items() if v > 0})
# ② data_query
seen = set(); stale = []; off = []
for l in open(D + 'budgets_1127.txt'):
    if l[0] == '#': continue
    c, a, st, b, cost = l.strip().split(','); k = (REN.get(c, c), a); seen.add(k); assert k in state, ('記録にない広告セット', k)
    if k in direct and int(b) != state[k]: assert int(b) == prev[k], ('data_query が変更の前の値でもない', k, b, prev[k]); stale.append(k[1])
    elif k[0] not in enabled: assert state[k] == 0 and st == 'ACTIVE', (k, state[k], st); off.append(k[1])
    else: assert state[k] == (int(b) if st == 'ACTIVE' else 0), ('data_query と記録が違う', k, state[k], st, b)
assert {k for k, v in state.items() if v > 0} <= seen, '予算のある広告セットが data_query に無い'
# ③ 変更履歴
h0 = H(D + 'meta_history_1125utc_0020_raw.json'); assert max(h['timestamp'] for h in h0) == '2026-11-25T15:25:49+0000'   # 00:26 に読んだ履歴（o1125/meta_history_1126_0026_raw.json）のいちばん新しい操作と同じ＝00:26〜09:00 は 0件
assert max(h['timestamp'] for h in H(D + '../o1125/meta_history_1126_0026_raw.json')) == '2026-11-25T15:25:49+0000'
h1 = H(D + '../ic1126/brush/meta_history_1126_1724_raw.json'); h2 = H(D + 'meta_history_1126_1127_0015_raw.json')
assert min(h['timestamp'] for h in h2) <= max(h['timestamp'] for h in h1), '履歴の間があいている'
assert any(h['operation'] == 'AD_ACCOUNT_BILLING_CHARGE' for h in h1), '9時〜17時の分が入っていない'   # 11/26 10:37 の課金（その日の UTC の最初の操作）まで読めている
new = [h for h in h2 if h['timestamp'] > max(x['timestamp'] for x in h1)]
bad = [h for h in new if h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET') or h['operation'].endswith('RUN_STATUS')]; assert not bad, bad
with open(F, 'a', newline='') as f:
    w = csv.writer(f, lineterminator='\r\n'); [w.writerow([LAB, k[0], k[1], v]) for k, v in state.items()]
print(LAB, len(state), '行・合計', sum(state.values()), '・配信中', len(enabled), 'キャンペーン・直読', len(direct), '本・data_query が古い値', stale, '・キャンペーン停止で広告セットは ACTIVE', off, '・17:21 のあとの操作', [h['operation'] for h in new])
