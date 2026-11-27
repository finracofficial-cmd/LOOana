# -*- coding: utf-8 -*-
"""11/28 06:5x「広告変えたよ」: Meta の変更履歴（UTC 11/27＝日本時間 11/27 09:00〜）から、11/28 のスナップショット（04:35 の確認）より後の予算の変更を読み、
data/budget-snapshots.csv に 2026-11-28a として足す。入力: meta_history_1127utc_0653_raw.json・data/budget-snapshots.csv"""
import json, os, csv, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
H = json.load(open(D0 + 'meta_history_1127utc_0653_raw.json'))['data']['data']['results']['platform_change_list']
jst = lambda t: (datetime.datetime.strptime(t[:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9))
SN = {}; rows = list(csv.reader(open('data/budget-snapshots.csv', newline='')))
for r in rows[1:]:
    if r and r[0] == '2026-11-28': SN[r[2]] = (r[1], int(r[3]))
assert len(SN) == 26 and not any(r and r[0] == '2026-11-28a' for r in rows)
out = []; add = []
def P(s): print(s); out.append(s)
user = [h for h in H if h['actor_name'] != 'Meta' and jst(h['timestamp']) > datetime.datetime(2026, 11, 28, 4, 35)]
P(f"変更履歴（取得 11/28 06:53・いちばん新しい操作 {jst(H[0]['timestamp']):%m/%d %H:%M}）: 11/28 04:35 より後のユーザーの操作 {len(user)}件")
for h in sorted(user, key=lambda x: x['timestamp']):
    if h['operation'] != 'UPDATE_AD_SET_BUDGET': P(f"  {jst(h['timestamp']):%H:%M:%S} {h['campaign_name']}: {h['operation']}（{h['change_values'].get('old_value')} → {h['change_values'].get('new_value')}）"); continue
    o = h['change_values']['old_value']['old_value']; n = h['change_values']['new_value']['new_value']; camp, was = SN[h['campaign_name']]; assert was == o, (h['campaign_name'], was, o)
    P(f"  {jst(h['timestamp']):%H:%M:%S} {camp}／{h['campaign_name']}: 日予算 {o:,} → {n:,}（{n/o-1:+.1%}）"); add.append(['2026-11-28a', camp, h['campaign_name'], str(n)])
assert len(add) == 2
tot = sum(v for _, v in SN.values()); new = tot + sum(int(a[3]) - SN[a[2]][1] for a in add)
P(f"日予算の合計 {tot:,} → {new:,}")
with open('data/budget-snapshots.csv', 'a', newline='') as f: csv.writer(f, lineterminator='\r\n').writerows(add)
open(D0 + 'record_moves_1128.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
