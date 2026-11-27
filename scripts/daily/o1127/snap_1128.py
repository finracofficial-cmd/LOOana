# -*- coding: utf-8 -*-
"""budget-snapshots.csv に 2026-11-28 の全体スナップショットを足す（11/28 04:3x）。
もと＝2026-11-27 の全体＋途中の記録 a（00:17 W固定 -sab・ガラス主力・4-in-1）＋ b（14:18 洗車ブラシの停止）＋ c（14:42 サンバイザーの出稿）＋ d（21:52 ガラスクロスの出稿）。
確かめ方: ①data_query（budgets_1128.txt・04:3x。今回は今の値が出ている）: 配信中の広告セットは記録と同じ・止めたブラシは CAMPAIGN_PAUSED で記録は 0
②配信中のキャンペーンの一覧（campaigns_enabled_1128_raw.json）と同じであること
③変更履歴: 11/27 00:32（o1126/meta_history_1127_0032_raw.json）から 11/28 04:35（meta_history_1127utc_0435_raw.json）まで、読んだ履歴がつながっていて、記録していない予算の変更・停止が無いこと"""
import csv, os, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-28'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict()
for r in rows:
    if r['snapshot_date'] == '2026-11-27': state[(r['campaign'], r['adset'])] = int(r['daily_budget'])
assert len(state) == 24 and sum(state.values()) == 175000, (len(state), sum(state.values()))
for lab in ('2026-11-27a', '2026-11-27b', '2026-11-27c', '2026-11-27d'):
    n = 0
    for r in rows:
        if r['snapshot_date'] == lab: state[(r['campaign'], r['adset'])] = int(r['daily_budget']); n += 1
    assert n, lab
H = lambda f: json.load(open(f))['data']['data']['results']['platform_change_list']
# ② 配信中の一覧
enabled = {REN.get(c['name'], c['name']) for c in json.load(open(D + 'campaigns_enabled_1128_raw.json'))['data']['data']['results']}
assert {k[0] for k, v in state.items() if v > 0} == enabled, (enabled ^ {k[0] for k, v in state.items() if v > 0})
# ① data_query
seen = set(); off = []
for l in open(D + 'budgets_1128.txt'):
    if l[0] == '#': continue
    c, a, st, b, cost = l.strip().split(','); k = (REN.get(c, c), a); seen.add(k); assert k in state, ('記録にない広告セット', k)
    if k[0] not in enabled: assert state[k] == 0 and st == 'CAMPAIGN_PAUSED', (k, state[k], st); off.append(k[1])
    else: assert st == 'ACTIVE' and state[k] == int(b), ('data_query と記録が違う', k, state[k], st, b)
assert {k for k, v in state.items() if v > 0} <= seen, '予算のある広告セットが data_query に無い'
# ③ 変更履歴（読んだ順につながっているか・記録していない予算の変更や停止が無いか）
chain = ['../o1126/meta_history_1127_0032_raw.json', '../ic1127/brush/meta_history_1127_1403_raw.json', '../ic1127/brush/meta_history_1127_1418_raw.json', '../ic1127/visor/meta_history_1127_1443_raw.json',
         '../ic1127/visor/meta_history_1127_1505_raw.json', '../ic1127/visor/h20/meta_history_1127_2027_raw.json', '../ic1127/cloth/meta_history_1127_2155_raw.json', 'meta_history_1127utc_0435_raw.json']
hs = [H(D + f) for f in chain]; gaps = []
for f, a, b in zip(chain[1:], hs, hs[1:]):
    if min(h['timestamp'] for h in b) > max(h['timestamp'] for h in a): gaps.append(f)
allh = {(h['timestamp'], h['operation'], h['campaign_id']): h for x in hs for h in x}
t0 = max(h['timestamp'] for h in hs[0])   # 11/27 00:17 の変更のあと
later = [h for k, h in sorted(allh.items()) if h['timestamp'] > t0]
chg = [h for h in later if h['operation'] in ('UPDATE_AD_SET_BUDGET', 'UPDATE_CAMPAIGN_BUDGET', 'CREATE_AD_SET') or (h['operation'].endswith('RUN_STATUS') and h['actor_name'] != 'Meta' and h['change_values'].get('old_value') != '処理待ち')]
jst = lambda t: f"{(int(t[11:13]) + 9) % 24:02d}:{t[14:16]}"
desc = [f"{jst(h['timestamp'])} {h['operation']} {h['campaign_name']}" for h in chg]
known = {('UPDATE_CAMPAIGN_RUN_STATUS', '伸縮ワックス洗車ブラシ'), ('CREATE_AD_SET', '2WAY防眩サンバイザー'), ('CREATE_AD_SET', 'クリア仕上げガラスクロス')}
assert {(h['operation'], h['campaign_name']) for h in chg} == known, desc
with open(F, 'a', newline='') as f:
    w = csv.writer(f, lineterminator='\r\n'); [w.writerow([LAB, k[0], k[1], v]) for k, v in state.items()]
print(LAB, len(state), '行・合計', sum(state.values()), '・配信中', len(enabled), 'キャンペーン・data_query で止まっている広告セット', off, '・11/27 00:17 のあとの予算の変更／停止／出稿', desc, '・履歴の読み取りの間があいた所', gaps or 'なし', '・いちばん新しい操作', jst(max(h['timestamp'] for h in hs[-1])))
