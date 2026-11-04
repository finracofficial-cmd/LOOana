# -*- coding: utf-8 -*-
"""11/04(水) 13:00カット（Shopify 0〜12時台・Meta 0〜12時台）。Shopifyは 10/19〜11/4 の時間別を1本で取り直したもの、Metaは時間フィルタ付き data_query（fresh）。ordersCount(13:00) で検算"""
import json, datetime as dt, statistics as st, os, collections, csv
D = os.path.dirname(os.path.abspath(__file__)) + '/'; H = 13; T = dt.date(2026, 11, 4)
def jst(ts): return dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ') + dt.timedelta(hours=9)
S = collections.defaultdict(dict); V = collections.defaultdict(dict)
for ts, o, g, d in json.load(open(D + 'sales_h_1019_1104.json')): t = jst(ts); S[t.date()][t.hour] = (int(o), int(g), int(d))
for r in json.load(open(D + 'sess_h_1019_1104.json')): t = jst(r[0]); V[t.date()][t.hour] = tuple(int(x) for x in r[1:])
oc = json.load(open(D + 'ordcount13.json'))
M = {}
for ln in open(D + 'meta_day_0012.txt'):
    p = ln.strip().split(',')
    if len(p) == 7: M[dt.date.fromisoformat(p[0])] = [int(x) for x in p[1:]]
days = sorted(d for d in S if dt.date(2026, 10, 19) <= d <= T)
# 終日の注文（全日の時間別合計）と CSV の日次実売で検算
full = {d: sum(v[0] for v in S[d].values()) for d in days if d < T}
G = collections.defaultdict(int)
for r in csv.DictReader(open(D + '../../../data/daily/daily_sales.csv')): G[r['date']] += int(r['gross'])
for d in days:
    if d < T: assert sum(v[1] for v in S[d].values()) == G[d.isoformat()], (d, sum(v[1] for v in S[d].values()), G[d.isoformat()])
rows = {}
for d in days:
    o = sum(S[d].get(h, (0, 0, 0))[0] for h in range(H)); net = sum(S[d].get(h, (0, 0, 0))[1] + S[d].get(h, (0, 0, 0))[2] for h in range(H))
    v = [sum(V[d].get(h, (0, 0, 0, 0))[i] for h in range(H)) for i in range(4)]
    k = 'd' + d.strftime('%m%d')
    if k in oc: assert o == oc[k], (d, o, oc[k])
    rows[d] = (o, net, v, M[d])
print('assert OK: 時間別gross合計 == daily_sales.csv（10/19〜11/3 全日）／0〜12時台の注文 == ordersCount(13:00)（11/4・11/3・10/28・10/21）')
WD = '月火水木金土日'; past = [d for d in days if d < T]
print('日付 曜 | 注文 実売 | 来訪 カート 到達 完了 | 広告 CPM CTR 1LPV LPV | 実売/広告 | 終日注文')
for d in days:
    o, n, v, m = rows[d]
    print(f"{d.strftime('%m/%d')} {WD[d.weekday()]} | {o:3d} {n:8,} | {v[0]:5d} {v[1]:3d} {v[2]:3d} {v[3]:3d} | {m[0]:7,} {m[0]/m[1]*1000:5,.0f} {m[2]/m[1]:5.2%} {m[0]/m[3]:5.1f} {m[3]:5d} | {n/m[0]:.2f} | {full.get(d, '')}")
def rk(f, lab, fm='{:,.0f}'):
    t = f(T); xs = [f(d) for d in past]
    print(f"{lab}: 今日 {fm.format(t)} ／ 過去{len(xs)}日 {fm.format(min(xs))}〜{fm.format(max(xs))}・中央値 {fm.format(st.median(xs))}・今日より低い日 {sum(1 for x in xs if x < t)}")
rk(lambda d: rows[d][0], '注文'); rk(lambda d: rows[d][1], '実売'); rk(lambda d: rows[d][2][0], '来訪')
rk(lambda d: rows[d][3][0], '広告費'); rk(lambda d: rows[d][3][0] / rows[d][3][1] * 1000, 'CPM'); rk(lambda d: rows[d][3][2] / rows[d][3][1] * 100, 'CTR(%)', '{:.2f}')
rk(lambda d: rows[d][3][0] / rows[d][3][3], '1LPVあたり広告費', '{:.1f}')
rk(lambda d: rows[d][1] / rows[d][3][0], '実売÷広告費【参考】', '{:.2f}'); rk(lambda d: rows[d][0] / rows[d][2][0] * 100, '注文/来訪(%)【参考】', '{:.2f}')
rk(lambda d: rows[d][2][1] / rows[d][2][0] * 100, 'カート/来訪(%)【参考】', '{:.2f}')
# 11〜12時台だけ
blk = lambda d: (sum(S[d].get(h, (0, 0, 0))[0] for h in (11, 12)), sum(V[d].get(h, (0, 0, 0, 0))[0] for h in (11, 12)))
xs = [blk(d)[0] for d in past]; print('11〜12時台の注文: 今日', blk(T)[0], '来訪', blk(T)[1], '／過去', min(xs), '〜', max(xs), '中央値', st.median(xs), '今日以下の日', sum(1 for x in xs if x <= blk(T)[0]))
# 13時の注文 vs 終日
sh = [rows[d][0] / full[d] for d in past]; r = st.correlation([rows[d][0] for d in past], [full[d] for d in past])
print(f'13時までの割合 中央値{st.median(sh):.1%}（{min(sh):.1%}〜{max(sh):.1%}）・13時注文と終日注文の相関 r={r:.2f}')
print('13時の注文が今日に近い日（28〜35件）の終日:', [(d.strftime('%m/%d'), rows[d][0], full[d]) for d in past if 28 <= rows[d][0] <= 35])
C = collections.defaultdict(dict)
for ln in open(D + 'meta_camp_0012.txt'):
    p = ln.strip().split(',')
    if len(p) == 8: C[p[0]][p[1]] = [0 if x == 'null' else int(x) for x in p[2:]]
f = lambda a: f"{a[0]:6,} CPM{a[0]/a[1]*1000 if a[1] else 0:5,.0f} CTR{a[2]/a[1] if a[1] else 0:5.1%} LPV{a[3]:4d} Metaカート{a[4]:3d}"
print('\nキャンペーン別 0〜12時台   今日 | 11/3同時刻')
for k in sorted(C['2026-11-04'], key=lambda k: -C['2026-11-04'][k][0]):
    a = C['2026-11-04'][k]
    if a[0]: print(f"  {k[:13]:13} {f(a)} | {f(C['2026-11-03'].get(k, [0]*6))}")
for d in ['2026-11-02', '2026-11-03', '2026-11-04']:
    t = [sum(v[i] for v in C[d].values()) for i in range(4)]; m = M[dt.date.fromisoformat(d)]
    assert all(abs(t[i] - m[i]) <= max(2, m[i] * (0.03 if d == '2026-11-04' else 0)) for i in range(4)), (d, t, m[:4])
print('照合OK: キャンペーン合計 ≒ アカウント合計')
