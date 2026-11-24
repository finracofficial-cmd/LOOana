# -*- coding: utf-8 -*-
"""11/25 00:2x ユーザー「予算色々動かした。これで確定にしてみて」: 配信中の全キャンペーンを直読（campaign_and_resource_get・direct_*_0020_raw.json）し、
00:1x の全体スナップショット（2026-11-25）との違いを 2026-11-25a として budget-snapshots.csv に足す（途中の記録＝変わった行だけ）。"""
import csv, os, json, glob, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-25a'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-25'); assert len(state) == 21
now = {}
for f in sorted(glob.glob(D + 'direct_*_0020_raw.json')):
    c = json.load(open(f))['data']['data']['results'][0]
    for a in c['ad_groups']:
        k = (REN.get(c['name'], c['name']), a['name'])
        if k in state: now[k] = a['daily_budget'] if (c['status'] == 'ENABLED' and a['status'] == 'ENABLED') else 0
enabled = {REN.get(c['name'], c['name']) for c in json.load(open(D + 'campaigns_enabled_0020_raw.json'))['data']['data']['results']}
live = {k for k, v in state.items() if v > 0}
assert live <= set(now), ('直読していない広告セット', live - set(now))
assert {k[0] for k, v in now.items() if v > 0} == enabled, enabled ^ {k[0] for k, v in now.items() if v > 0}
diff = collections.OrderedDict((k, (state[k], now[k])) for k in state if k in now and state[k] != now[k])
for k, (a, b) in diff.items(): print(f'  {k[1]}: {a:,} → {b:,}（{(b/a-1) if a else 0:+.1%}）')
with open(F, 'a', newline='') as f:
    w = csv.writer(f); [w.writerow([LAB, k[0], k[1], b]) for k, (a, b) in diff.items()]
new = {**state, **{k: v for k, v in now.items()}}
print(LAB, len(diff), '行・合計', sum(state.values()), '→', sum(new.values()))
