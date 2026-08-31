# -*- coding: utf-8 -*-
"""2026-08-31: 「今日のパフォーマンスが悪い」の切り分け。
   月曜の弱さが needs(需要) なのか delivery(配信ペーシング) なのかを分ける。

   結論: 配信。月曜の消化率は平均92.1%（日曜106.8%）で、MER は1.93と中位。
         日曜の消化率と翌月曜の消化率は r=−0.76 で負に相関する＝暦週(日〜土)の帳尻合わせ。

   ★日中比較の注意: 午前(0-11時)に消化する割合は曜日で違う（月曜38.5% / 7日平均45.6%）。
     7日平均の割合を月曜に当てると、正常な日を「23%未達」と誤判定する。
"""
import csv, collections, datetime, statistics

def budgets():
    raw = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in list(csv.reader(open('data/budget-snapshots.csv', encoding='utf-8')))[1:]:
        if r: raw[r[1]][r[0]] = raw[r[1]].get(r[0], 0) + int(r[3])
    out = collections.defaultdict(int)
    for cp, byk in raw.items():
        byday = collections.defaultdict(dict)
        for k, v in byk.items(): byday[k[:10]][k] = v
        for d, sn in byday.items(): out[d] += sn[max(sn)]   # その日の最後のスナップショット
    return out

def series(path, key, val):
    o = collections.defaultdict(float)
    for r in csv.DictReader(open(path, encoding='utf-8')): o[r[key]] += float(r[val])
    return o

BUD = budgets()
AD = series('data/daily/daily_ad.csv', 'date', 'cost')
S = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open('data/daily/daily_sales.csv', encoding='utf-8')):
    S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])

WD = ['月', '火', '水', '木', '金', '土', '日']
days = [d for d in sorted(BUD) if d in AD and BUD[d] > 0 and '2026-08-01' <= d <= '2026-08-30']
pace, mer = collections.defaultdict(list), collections.defaultdict(list)
for d in days:
    w = WD[datetime.date.fromisoformat(d).weekday()]
    pace[w].append(AD[d] / BUD[d]); mer[w].append((S[d][0] - S[d][1]) / AD[d])

print('① 消化率（実消化÷日予算）曜日別 — 配信側')
for w in sorted(pace, key=lambda k: -statistics.mean(pace[k])):
    print(f'  {w}  n={len(pace[w])}  {statistics.mean(pace[w]):.1%}')
print('\n② MER 曜日別 — 需要側')
for w in sorted(mer, key=lambda k: -statistics.mean(mer[k])):
    print(f'  {w}  n={len(mer[w])}  {statistics.mean(mer[w]):.2f}')
print('\n③ 日曜の消化率 → 翌月曜の消化率（暦週=日〜土の帳尻合わせ）')
xs, ys = [], []
for d in days:
    dt = datetime.date.fromisoformat(d)
    if dt.weekday() != 6: continue
    nx = (dt + datetime.timedelta(days=1)).isoformat()
    if nx not in BUD or nx not in AD or not BUD[nx]: continue
    a, b = AD[d] / BUD[d], AD[nx] / BUD[nx]; xs.append(a); ys.append(b)
    print(f'  {d}(日) {a:6.1%} → {nx}(月) {b:6.1%}')
if len(xs) >= 3:
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    sxx = sum((x-mx)**2 for x in xs); syy = sum((y-my)**2 for y in ys)
    print(f'  相関 r = {sxy/(sxx*syy)**0.5:+.2f}（n={len(xs)}）'
          '  ★日曜に押し込むほど翌月曜が深く絞られる')
