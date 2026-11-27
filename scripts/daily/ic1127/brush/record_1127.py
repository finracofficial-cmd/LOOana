# -*- coding: utf-8 -*-
"""11/27 14:1x「ブラシ停止した」: 変更履歴（meta_history_1127_1418_raw.json）で停止を確かめ、
①budget-snapshots.csv に 2026-11-27b（ブラシ 8,000 → 0）②relaunch-log.csv のブラシの行に 1〜2日目の倍率と停止を書く。
金額・時刻・倍率は取得ファイルから読む（このスクリプトに数字は書かない）"""
import csv, os, json, io, collections, datetime, contextlib
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../../'; os.chdir(R)
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1126.py').read(), g)
NM = '伸縮ワックス洗車ブラシ'; COST, PRICE = g['COST'][NM], g['PRICE'][NM]
H = json.load(open(D + 'meta_history_1127_1418_raw.json'))['data']['data']['results']['platform_change_list']
off = [h for h in H if h['operation'] == 'UPDATE_CAMPAIGN_RUN_STATUS' and h['campaign_name'] == NM and h['change_values']['new_value'] == 'オフ']; assert len(off) == 1
t_off = (datetime.datetime.strptime(off[0]['timestamp'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)); assert off[0]['actor_name'] != 'Meta'
other = [h for h in H if h is not off[0] and h['operation'] != 'AD_ACCOUNT_BILLING_CHARGE']; assert not other, other   # 11/27 9時〜14:18 の操作はブラシの停止と課金だけ
raw = json.load(open(D + 'brush_meta_1126_1127_1418_raw.json'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
M = [dict(zip(cols, r)) for r in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]; z = lambda x: 0.0 if x in ('null', '') else float(x)
cost = sum(z(r['cost']) for r in M); clk = sum(z(r['link_clicks']) for r in M); imp = sum(z(r['impressions']) for r in M); atc = sum(z(r['offsite_conversions_fb_pixel_add_to_cart']) for r in M)
S = json.load(open(D + 'brush_sales_1126_1127_1419_raw.json'))['rows']; orders = sum(int(r[1]) for r in S); q = sum(round(float(r[2]) / PRICE) for r in S); gp = sum(float(r[2]) + float(r[3]) for r in S) - q * COST
start = datetime.datetime(2026, 11, 26, 17, 21); hours = (t_off - start).total_seconds() / 3600
txt = f"{t_off:%m/%d %H:%M} に停止（再開から約{hours:.0f}時間）: 広告費 {cost:,.0f}（14:18 の取得・取り込み途中）・{clk:.0f}クリック（クリック率 {clk/imp:.2%}・クリック1回 {cost/clk:.0f}円）・カート（Meta）{atc:.0f}・注文 {orders}件・{q}個・倍率 {gp/cost:.2f}・利益 {gp-cost:+,.0f}"
print(txt)
# ---- ① 予算 ----
F = 'data/budget-snapshots.csv'; LAB = '2026-11-27b'; rows = list(csv.DictReader(open(F)))
if not any(r['snapshot_date'] == LAB for r in rows):
    st = collections.OrderedDict(((r['campaign'], r['adset']), int(r['daily_budget'])) for r in rows if r['snapshot_date'] == '2026-11-27')
    for r in rows:
        if r['snapshot_date'] == '2026-11-27a': st[(r['campaign'], r['adset'])] = int(r['daily_budget'])
    k = (NM, NM); before = sum(st.values()); old = st[k]; assert old > 0
    with open(F, 'a', newline='') as f: csv.writer(f, lineterminator='\r\n').writerow([LAB, k[0], k[1], 0])
    st[k] = 0; print(LAB, f"{NM}: {old:,} → 0・合計 {before:,} → {sum(st.values()):,}・配信中のキャンペーン {len({a for (a, b), v in st.items() if v > 0})}")
# ---- ② 出し直しの記録 ----
G = 'data/relaunch-log.csv'; L = list(csv.reader(open(G, encoding='utf-8', newline=''))); hd = L[0]; i12, i7, im = hd.index('1〜2日目の倍率'), hd.index('7日の倍率'), hd.index('メモ')
idx = [n for n, r in enumerate(L) if r and r[0] == NM and r[hd.index('開始日')] == '2026-11-26']; assert len(idx) == 1; r = L[idx[0]]
if not r[i12]:
    r[i12] = f"{gp/cost:.2f}"; r[i7] = '—'; r[im] = r[im] + '｜' + txt + '。判定（11/28 朝）の前の停止・一覧にない'
    with open(G, 'w', newline='', encoding='utf-8') as f: csv.writer(f, lineterminator='\r\n').writerows(L)
    print('relaunch-log: ブラシの行を更新', r[i12], r[i7])
open(D + 'record_1127.txt', 'w', encoding='utf-8').write(txt + '\n')
