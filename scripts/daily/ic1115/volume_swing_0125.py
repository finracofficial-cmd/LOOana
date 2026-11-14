# -*- coding: utf-8 -*-
"""広告費が減ったから来訪が減り、ぶれが大きくなったのか（2026-11-15 01:2x ユーザー「広告費減りまくってるから流入少ないのか。だからブレが大きくなるのか」）
入力: data/daily（実売・広告費・注文数）、meta_acct_daily_1004_1114.txt（表示・クリック）、sess_daily_1004_1114.json（来訪）
①週ごとの 広告費/日・来訪/日・注文/日 と 来訪÷広告費 ②日ごとの売上÷広告費のぶれ（対数の標準偏差）を期間で比べ、注文数から出る偶然のぶれ（1/√注文）と並べる"""
import csv, json, math, datetime, statistics as st, collections
R = __file__.rsplit('/scripts/', 1)[0] + '/'
H = R + 'scripts/daily/ic1115/'
HOL = {'2026-07-20', '2026-08-11', '2026-09-21', '2026-09-22', '2026-09-23', '2026-10-12', '2026-11-03', '2026-11-23'}
MA = {}
for l in open(H + 'meta_acct_daily_1004_1114.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
SE = {r[0]: int(r[1]) for r in json.load(open(H + 'sess_daily_1004_1114.json'))['rows']}
NET = collections.defaultdict(int); AD = collections.defaultdict(float); OR = {}
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv')): OR[r['date']] = int(r['orders'])
END = datetime.date(2026, 11, 14)
W = lambda w: [(END - datetime.timedelta(7 * w + k)).isoformat() for k in range(6, -1, -1)]
print('週（7日）       広告費/日  表示/日  クリック/日  来訪/日  注文/日  来訪÷広告費1万円  1日の注文の偶然のぶれ')
for w in range(5, -1, -1):
    ds = W(w); a = sum(AD[d] for d in ds) / 7; im = sum(MA[d][1] for d in ds) / 7; cl = sum(MA[d][3] for d in ds) / 7; s = sum(SE[d] for d in ds) / 7; o = sum(OR[d] for d in ds) / 7
    print(f'{ds[0][5:]}〜{ds[-1][5:]}   {a:8,.0f}  {im:7,.0f}   {cl:6,.0f}    {s:6,.0f}   {o:5.1f}      {s/a*10000:5.1f}          ±{100/math.sqrt(o):.1f}%')
dd = sorted(d for d in AD if '2026-10-04' <= d <= '2026-11-14' and d in SE)
xs = [AD[d] for d in dd]; ys = [SE[d] for d in dd]
mx, my = st.mean(xs), st.mean(ys); cor = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
print(f'\n日ごとの 広告費 と 来訪 の相関（10/4〜11/14・{len(dd)}日）: {cor:.2f}')
print('\n日ごとの 売上÷広告費 のぶれ（祝日除く・対数の標準偏差）と、注文数だけから出る偶然のぶれ')
for a_, b_ in (('2026-08-16', '2026-09-14'), ('2026-09-15', '2026-10-14'), ('2026-10-16', '2026-11-14')):
    ds = sorted(d for d in AD if a_ <= d <= b_ and d not in HOL and AD[d] and d in OR)
    lv = [math.log(NET[d] / AD[d]) for d in ds]; o = st.mean(OR[d] for d in ds)
    print(f'  {a_[5:]}〜{b_[5:]}（{len(ds)}日）: 注文 {o:.0f}/日・ぶれ ±{(math.exp(st.stdev(lv))-1)*100:.0f}%（注文数だけなら ±{100/math.sqrt(o):.0f}%）')
