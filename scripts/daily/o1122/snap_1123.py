# -*- coding: utf-8 -*-
"""budget-snapshots.csv に 2026-11-23 の全体スナップショットを足す（11/23 00時台・data_query fresh の広告セット別日予算＝budgets_1123.txt。止まっている広告セットは 0）。
名前は記録の形に合わせる（ノーズ v2・シェーバー v2・インソール v3 は元の商品名のキャンペーン名で持っている）。"""
import csv, os, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-23'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict()
for r in rows:
    if r['snapshot_date'] == '2026-11-22': state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
assert len(state) == 17
for r in rows:
    if r['snapshot_date'] in ('2026-11-22a', '2026-11-22b', '2026-11-22c'): state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
now = {}
for l in open(D + 'budgets_1123.txt'):
    if l[0] == '#': continue
    c, a, st, b, cost = l.strip().split(','); assert st == 'ACTIVE'; now[(REN.get(c, c), a)] = int(b)
new = collections.OrderedDict((k, now.get(k, 0)) for k in state)
assert set(now) <= set(state), set(now) - set(state)
diff = {k: (state[k], new[k]) for k in state if state[k] != new[k]}
print('11/22c までの記録との違い:', diff or 'なし')
with open(F, 'a', newline='') as f:
    w = csv.writer(f); [w.writerow([LAB, k[0], k[1], v]) for k, v in new.items()]
print(LAB, len(new), '行・合計', sum(new.values()))
