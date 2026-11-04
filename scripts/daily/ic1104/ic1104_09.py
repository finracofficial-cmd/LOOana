# -*- coding: utf-8 -*-
"""11/04(水) 09:00カット（Shopify 0〜8時台・Meta 0〜8時台）。過去日の値は ic1103/ の保存済み実測（10/18〜11/3）、今日は ic1104/ の実測"""
import json, datetime as dt, statistics as st, os, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; P = D + '../ic1103/'
def jst(ts): return dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ') + dt.timedelta(hours=9)
S = collections.defaultdict(dict); V = collections.defaultdict(dict)
for fn in ['sales_1018_1029.json', 'sales_1030_1103.json', 'sales_1103.json']:
    for ts, o, g, d in json.load(open(P + fn)): t = jst(ts); S[t.date()][t.hour] = (int(o), int(g), int(d))
for fn in ['sess_1018_1029.json', 'sess_1030_1103.json', 'sess_1103.json']:
    for r in json.load(open(P + fn)): t = jst(r[0]); V[t.date()][t.hour] = tuple(int(x) for x in r[1:])
for ts, o, g, d in json.load(open(D + 'sales_1104.json')): t = jst(ts); S[t.date()][t.hour] = (int(o), int(g), int(d))
for r in json.load(open(D + 'sess_1104.json')): t = jst(r[0]); V[t.date()][t.hour] = tuple(int(x) for x in r[1:])
oc = json.load(open(P + 'ordcount09.json')); oc.update({k: v for k, v in json.load(open(D + 'ordcount09.json')).items() if k.startswith('d') and len(k) == 5})
M = {}
for ln in open(D + 'meta_day_0008.txt'):
    p = ln.strip().split(','); M[dt.date.fromisoformat(p[0])] = [int(x) for x in p[1:]]
WD = '月火水木金土日'; T = dt.date(2026, 11, 4)
days = sorted(d for d in S if d >= dt.date(2026, 10, 19))
rows = {}
for d in days:
    o = sum(S[d].get(h, (0, 0, 0))[0] for h in range(9)); g = sum(S[d].get(h, (0, 0, 0))[1] for h in range(9)) + sum(S[d].get(h, (0, 0, 0))[2] for h in range(9))
    v = [sum(V[d].get(h, (0, 0, 0, 0))[i] for h in range(9)) for i in range(4)]
    k = 'd' + d.strftime('%m%d'); assert o == oc[k], (d, o, oc[k])
    rows[d] = (o, g, v, M.get(d))
print('assert OK: 0〜8時台の時間別注文合計 == ordersCount(09:00) 全日')
print('日付 曜 | 注文 実売 | 来訪 カート 到達 完了 | 広告 表示 CPM CTR 1LPV LPV Metaカート Meta購入')
for d in days:
    o, g, v, m = rows[d]
    ms = f"{m[0]:6,} {m[1]:6,} {m[0]/m[1]*1000:5,.0f} {m[2]/m[1]:5.2%} {m[0]/m[3]:5.1f} {m[3]:4d} {m[4]:3d} {m[5]:3d}" if m else ''
    print(f"{d.strftime('%m/%d')} {WD[d.weekday()]} | {o:3d} {g:8,} | {v[0]:4d} {v[1]:3d} {v[2]:3d} {v[3]:3d} | {ms}")
past = [d for d in days if d < T]
def rk(key, label, fmt='{:,.0f}'):
    t = key(T); xs = [key(d) for d in past]
    print(f"{label}: 今日 {fmt.format(t)} ／ 過去{len(xs)}日 {fmt.format(min(xs))}〜{fmt.format(max(xs))}・中央値 {fmt.format(st.median(xs))}・今日より低い日 {sum(1 for x in xs if x < t)}")
rk(lambda d: rows[d][0], '注文')
rk(lambda d: rows[d][1], '実売')
rk(lambda d: rows[d][2][0], '来訪')
rk(lambda d: rows[d][3][0], '広告費')
rk(lambda d: rows[d][3][1], '表示')
rk(lambda d: rows[d][3][0] / rows[d][3][1] * 1000, 'CPM')
rk(lambda d: rows[d][3][2] / rows[d][3][1] * 100, 'CTR(%)', '{:.2f}')
rk(lambda d: rows[d][3][0] / rows[d][3][3], '1LPVあたり広告費', '{:.1f}')
rk(lambda d: rows[d][3][3], 'LPV')
rk(lambda d: rows[d][0] / rows[d][2][0] * 100, '注文/来訪(%)【参考・日中は判定に使わない】', '{:.2f}')
print('水曜:', [(d.strftime('%m/%d'), rows[d][0], rows[d][3][0]) for d in days if d.weekday() == 2])
# キャンペーン別
C = collections.defaultdict(dict)
for ln in open(D + 'meta_camp_0008.txt'):
    p = ln.strip().split(','); C[p[0]][p[1]] = [0 if x == 'null' else int(x) for x in p[2:]]
print('\nキャンペーン別 0〜8時台: 広告 / CPM / CTR / LPV   今日 | 11/3 | 11/2')
f = lambda a: f"{a[0]:6,} {a[0]/a[1]*1000 if a[1] else 0:5,.0f} {a[2]/a[1] if a[1] else 0:5.1%} {a[3]:4d}"
for k in sorted(C['2026-11-04'], key=lambda k: -C['2026-11-04'][k][0]):
    a = C['2026-11-04'][k]
    if not a[0]: continue
    print(f"  {k[:14]:14} {f(a)} | {f(C['2026-11-03'].get(k, [0]*6))} | {f(C['2026-11-02'].get(k, [0]*6))}")
for d in ['2026-11-02', '2026-11-03', '2026-11-04']:
    t = [sum(v[i] for v in C[d].values()) for i in range(6)]; m = M[dt.date.fromisoformat(d)]
    # 11/4は2本の fresh 読み込みの時刻差で当日8時台の取り込みがずれる（キャンペーン側が+393円・+126表示）。2%以内なら同じデータとみなす
    assert all(abs(t[i] - m[i]) <= max(0, m[i] * (0.02 if d == '2026-11-04' else 0)) for i in range(4)), (d, t, m); print('照合', d, 'キャンペーン合計', t[:4], 'アカウント', m[:4])
up = [k for k, a in C['2026-11-04'].items() if a[1] and C['2026-11-03'].get(k, [0, 0])[1] and a[0] / a[1] > C['2026-11-03'][k][0] / C['2026-11-03'][k][1]]
both = [k for k, a in C['2026-11-04'].items() if a[1] and C['2026-11-03'].get(k, [0, 0])[1]]
print(f'CPMが11/3同時刻より上がったキャンペーン {len(up)}/{len(both)}:', [k for k in both if k not in up], 'だけ下がった')
