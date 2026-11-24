# -*- coding: utf-8 -*-
"""budget-snapshots.csv に 2026-11-25 の全体スナップショットを足す（11/25 00:1x）。
もと＝2026-11-24 の全体＋途中の記録 a〜d（ナノ２ 25,000・ノーズ v2 10,000・UV v2／毛玉 v2 停止 0・チェア v2 8,000）。
確かめ方: ①直読（campaign_and_resource_get・00:1x）ナノ２・ノーズ v2・ガラス2本・ワイパー・インソール v3・フィルム v2 ②それ以外は data_query（budgets_1125.txt）と同じであること。
data_query の日予算は取り込みが遅れていて、ナノ２ 21,000・ノーズ v2 12,000・UV v2 ACTIVE 8,000 と出る（直読と記録を正とする）"""
import csv, os, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-25'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict()
for r in rows:
    if r['snapshot_date'] == '2026-11-24': state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
assert len(state) == 20, len(state)
for lab in ('2026-11-24a', '2026-11-24b', '2026-11-24c', '2026-11-24d'):
    for r in rows:
        if r['snapshot_date'] == lab: state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
# ① 直読
direct = {}
for f in ('direct_nano_0012_raw.json', 'direct_nose_0012_raw.json', 'direct_glass_0012_raw.json', 'direct_wiper_0012_raw.json', 'direct_insole_0012_raw.json', 'direct_film_0012_raw.json'):
    c = json.load(open(D + f))['data']['data']['results'][0]; assert c['status'] == 'ENABLED', c['name']
    for a in c['ad_groups']:
        if a['status'] == 'ENABLED': direct[(REN.get(c['name'], c['name']), a['name'])] = a['daily_budget']
for k, v in direct.items(): assert state[k] == v, ('直読と記録が違う', k, state[k], v)
# ② data_query（遅れている3行を除く）
STALE = {('ナノガラス脱毛パッド', 'ナノガラス脱毛パッド２'), ('スマートノーズEMS美顔器', 'スマートノーズEMS美顔器v2'), ('UV歯ブラシ除菌器 v2', 'UV歯ブラシ除菌器v2')}
for l in open(D + 'budgets_1125.txt'):
    if l[0] == '#': continue
    c, a, st, b, cost = l.strip().split(','); k = (REN.get(c, c), a)
    assert k in state, ('記録にない広告セット', k)
    if k in STALE: continue
    assert state[k] == (int(b) if st == 'ACTIVE' else 0), ('data_query と記録が違う', k, state[k], st, b)
enabled = {REN.get(c['name'], c['name']) for c in json.load(open(D + 'campaigns_enabled_1125_raw.json'))['data']['data']['results']}
assert {k[0] for k, v in state.items() if v > 0} == enabled, (enabled ^ {k[0] for k, v in state.items() if v > 0})
with open(F, 'a', newline='') as f:
    w = csv.writer(f); [w.writerow([LAB, k[0], k[1], v]) for k, v in state.items()]
print(LAB, len(state), '行・合計', sum(state.values()), '・直読で確かめた', len(direct), '本')
