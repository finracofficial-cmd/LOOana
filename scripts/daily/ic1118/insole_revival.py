# -*- coding: utf-8 -*-
"""11/18 23時台 「いやーそれは復活してるよ」: 旧キャンペーン 11/3〜15 と v3 11/16〜18（18日は0〜20時台）の 注文÷広告費 を比べ、偶然で起きるかを注文数で見る
注文: Shopify FROM sales SHOW orders WHERE product_title CONTAINS 'インソール' GROUP BY day（11/18 取得・下に転記）。11/18 は h20/raw.txt の S 行（0〜20時台）
広告費: data/daily/daily_ad.csv（インソールのキャンペーン全部）・11/18 は h20/raw.txt の T 行（0〜20時台）"""
import csv, math
ORD = {'2026-11-03': 6, '2026-11-04': 4, '2026-11-05': 3, '2026-11-06': 1, '2026-11-07': 4, '2026-11-08': 2, '2026-11-09': 6, '2026-11-10': 3, '2026-11-11': 3, '2026-11-12': 4, '2026-11-13': 6, '2026-11-14': 2, '2026-11-15': 2, '2026-11-16': 8, '2026-11-17': 4}
AD = {}
for r in csv.DictReader(open('../../../data/daily/daily_ad.csv')):
    if r['campaign'].startswith('快適マジックインソール') and '2026-11-03' <= r['date'] <= '2026-11-17': AD[r['date']] = AD.get(r['date'], 0) + float(r['cost'])
for l in open('h20/raw.txt'):
    p = l.strip().split(',')
    if p[0] == 'T' and p[1].startswith('快適マジックインソール'): AD['2026-11-18'] = AD.get('2026-11-18', 0) + float(p[3])
    if p[0] == 'S' and p[1] == '2026-11-18' and p[2] == '快適マジックインソール': ORD['2026-11-18'] = ORD.get('2026-11-18', 0) + int(p[5])
old = [d for d in AD if d <= '2026-11-15']; new = [d for d in AD if d >= '2026-11-16']
oo, oa = sum(ORD[d] for d in old), sum(AD[d] for d in old); no, na = sum(ORD[d] for d in new), sum(AD[d] for d in new)
lam = oo / oa * na; p = 1 - sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(no))
print(f'旧 11/3〜15: 注文 {oo}・広告費 {oa:,.0f}・1万円あたり {oo/oa*1e4:.2f}')
print(f'v3 11/16〜18（18日は0〜20時台）: 注文 {no}・広告費 {na:,.0f}・1万円あたり {no/na*1e4:.2f}（旧の {no/na/(oo/oa):.1f}倍）')
print(f'旧の効率のままなら期待 {lam:.1f}件 → {no}件以上になる確率 {p:.2%}')
