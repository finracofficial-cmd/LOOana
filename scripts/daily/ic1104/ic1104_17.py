# -*- coding: utf-8 -*-
"""11/04 17:00カット: 実売÷広告費（広告効率）を過去16日の同時刻と比較。Shopify時間別（過去日は sales_h_1019_1104.json・今日は sales_1104_17.json）、Meta 0〜16時台（時間フィルタ付き data_query fresh）"""
import json, datetime as dt, statistics as st, os, collections, csv
D = os.path.dirname(os.path.abspath(__file__)) + '/'; H = 17; T = dt.date(2026, 11, 4)
def jst(ts): return dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ') + dt.timedelta(hours=9)
S = collections.defaultdict(dict)
for f in ['sales_h_1019_1104.json', 'sales_1104_17.json']:
    for ts, o, g, d in json.load(open(D + f)): t = jst(ts); S[t.date()][t.hour] = (int(o), int(g), int(d))
M = {}
for ln in open(D + 'meta_day_0016.txt'):
    p = ln.strip().split(',')
    if len(p) == 7: M[dt.date.fromisoformat(p[0])] = [int(x) for x in p[1:]]
M14 = {}
for ln in open(D + 'meta_day_0014.txt'):
    p = ln.strip().split(',')
    if len(p) == 7: M14[dt.date.fromisoformat(p[0])] = [int(x) for x in p[1:]]
oc = json.load(open(D + 'ordcount17.json'))
days = sorted(d for d in M); past = [d for d in days if d < T]
cut = lambda d, h0, h1: (sum(S[d].get(h, (0, 0, 0))[0] for h in range(h0, h1)), sum(S[d].get(h, (0, 0, 0))[1] + S[d].get(h, (0, 0, 0))[2] for h in range(h0, h1)))
for k in ('d1104', 'd1103', 'd1028'):
    d = dt.date(2026, int(k[1:3]), int(k[3:])); assert cut(d, 0, H)[0] == oc[k], (k, cut(d, 0, H)[0], oc[k])
A = collections.defaultdict(float); Sd = collections.defaultdict(int)
for r in csv.DictReader(open(D + '../../../data/daily/daily_ad.csv')): A[r['date']] += float(r['cost'])
for r in csv.DictReader(open(D + '../../../data/daily/daily_sales.csv')): Sd[r['date']] += int(r['gross']) - int(r['disc'])
print('assert OK: 0〜16時台の注文 == ordersCount(17:00)（11/4・11/3・10/28）')
def rk(f, lab, fm='{:,.0f}'):
    t = f(T); xs = [f(d) for d in past]
    print(f"{lab}: 今日 {fm.format(t)} ／ 過去16日 {fm.format(min(xs))}〜{fm.format(max(xs))}・中央値 {fm.format(st.median(xs))}・今日より低い日 {sum(1 for x in xs if x < t)}")
rk(lambda d: cut(d, 0, H)[0], '注文 0〜16時台'); rk(lambda d: cut(d, 0, H)[1], '実売 0〜16時台'); rk(lambda d: M[d][0], '広告費 0〜16時台')
rk(lambda d: cut(d, 0, H)[1] / M[d][0], '実売÷広告費 0〜16時台', '{:.2f}')
rk(lambda d: cut(d, 15, 17)[1] / (M[d][0] - M14[d][0]), '実売÷広告費 15〜16時台だけ', '{:.2f}')
rk(lambda d: (M[d][0] - M14[d][0]) / (M[d][1] - M14[d][1]) * 1000, 'CPM 15〜16時台だけ')
x = [cut(d, 0, H)[1] / M[d][0] for d in past]; y = [Sd[d.isoformat()] / A[d.isoformat()] for d in past]
print(f'17時の実売÷広告費と終日MERの相関 r={st.correlation(x, y):.2f}')
print('17時に1.85〜2.10だった日の終日MER:', [(d.strftime('%m/%d'), round(cut(d, 0, H)[1] / M[d][0], 2), round(Sd[d.isoformat()] / A[d.isoformat()], 2)) for d in past if 1.85 <= cut(d, 0, H)[1] / M[d][0] <= 2.10])
