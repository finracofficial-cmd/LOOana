# -*- coding: utf-8 -*-
"""11/26 00:2x ユーザー「予算調整したわ」: Meta の変更履歴（campaign_and_resource_get history・meta_history_1126_0026_raw.json・新しい順に14件）を読み、
00:1x の全体スナップショット（2026-11-26）との違いを 2026-11-26a として budget-snapshots.csv に足す（途中の記録＝変わった行だけ）。
数字は履歴の old_value／new_value から読む（このスクリプトに金額は書かない）。21:17（日本時間 11/25）の課金より後の操作が全部入っていることを確かめる"""
import csv, os, json, datetime, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; F = D + '../../../data/budget-snapshots.csv'; LAB = '2026-11-26a'
REN = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
rows = list(csv.DictReader(open(F))); assert not any(r['snapshot_date'] == LAB for r in rows), '追記済み'
state = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-26'); assert len(state) == 23 and sum(state.values()) == 202000
hist = json.load(open(D + 'meta_history_1126_0026_raw.json'))['data']['data']['results']['platform_change_list']
jst = lambda t: datetime.datetime.fromisoformat(t.replace('+0000', '+00:00')) + datetime.timedelta(hours=9)
old = [h for h in hist if h['operation'] == 'AD_ACCOUNT_BILLING_CHARGE' and h['timestamp'] == '2026-11-25T12:17:56+0000']; assert old, '前回までに読んだ最後の操作（21:17 の課金）が入っていない＝取りこぼしがあるかもしれない'
new = [h for h in hist if h['timestamp'] > '2026-11-25T12:17:56+0000']; diff = collections.OrderedDict(); log = []
for h in sorted(new, key=lambda h: h['timestamp']):
    op = h['operation']; t = jst(h['timestamp']).strftime('%H:%M')
    if op == 'UPDATE_AD_SET_BUDGET':
        ks = [k for k in state if k[1] == h['campaign_name']]; assert len(ks) == 1, (h['campaign_name'], ks); k = ks[0]
        a, b = h['change_values']['old_value']['old_value'], h['change_values']['new_value']['new_value']; assert state[k] == a, ('履歴の変更前と記録が違う', k, state[k], a)
        diff[k] = (a, b); log.append(f"{t} {k[1]}: {a:,} → {b:,}（{b/a-1:+.1%}）")
    elif op == 'UPDATE_CAMPAIGN_RUN_STATUS' and h['change_values']['new_value'] == 'オフ':
        c = REN.get(h['campaign_name'], h['campaign_name']); ks = [k for k in state if k[0] == c and state[k] > 0]; assert ks, c
        for k in ks: diff[k] = (state[k], 0); log.append(f"{t} {k[1]}: キャンペーンを停止（{state[k]:,} → 0）")
    elif op == 'UPDATE_AD_SET_RUN_STATUS' and h['change_values']['new_value'] in ('処理待ち', 'アクティブ'): pass   # 予算を変えたときに出る 処理待ち → アクティブ
    else: raise AssertionError(('読み方を決めていない操作', op, h['campaign_name'], h['change_values'].get('new_value')))
with open(F, 'a', newline='') as f:
    w = csv.writer(f, lineterminator='\r\n'); [w.writerow([LAB, k[0], k[1], b]) for k, (a, b) in diff.items()]
after = {**state, **{k: b for k, (a, b) in diff.items()}}
print('\n'.join(log)); print(LAB, len(diff), '行・合計', sum(state.values()), '→', sum(after.values()), '・配信中のキャンペーン', len({k[0] for k, v in after.items() if v > 0}))
