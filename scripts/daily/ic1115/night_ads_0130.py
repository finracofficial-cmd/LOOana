# -*- coding: utf-8 -*-
"""夜中に広告を止めるべきか（2026-11-15 01:3x ユーザー「夜中ってどうせ売れないじゃん？だから広告切るのはどう？」）
入力（どちらも実測・JST）: ic1114/meta_hourly_1031_1114.txt（Meta 時間帯別 広告費・表示・クリック・購入）、ic1114/sales_hour_1024_1114.json（Shopify 時間帯別 注文・売上〔値引前〕）
期間: 10/31〜11/13 の14日（11/14 は Meta が21時台途中までなので除く）。日ごとの広告費は data/daily と 1% 以内を assert。注文の合計 1,153 は daily_order_bands の同じ14日の合計と一致（01:35 確認）"""
import csv, json, collections
R = __file__.rsplit('/scripts/', 1)[0] + '/'
D = R + 'scripts/daily/ic1114/'
DAYS = [f'2026-10-31'] + [f'2026-11-{d:02d}' for d in range(1, 14)]
M = collections.defaultdict(lambda: [0, 0, 0, 0])   # hour -> cost, imp, clicks, purchases
MD = collections.defaultdict(float)
for l in open(D + 'meta_hourly_1031_1114.txt'):
    if l[0] == '#': continue
    d, rest = l.split(',', 1); h = int(rest[1:3]); v = rest.split('",')[1].strip().split(',')
    if d not in DAYS: continue
    for i in range(4): M[h][i] += int(v[i]) if v[i] != 'null' else 0
    MD[d] += int(v[0])
AD = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
for d in DAYS: assert abs(MD[d] - AD[d]) / AD[d] < 0.01, (d, MD[d], AD[d])
S = collections.defaultdict(lambda: [0, 0])
for d, h, o, g in json.load(open(D + 'sales_hour_1024_1114.json'))['rows']:
    if d in DAYS: S[int(h)][0] += int(o); S[int(h)][1] += int(g)
TC = sum(M[h][0] for h in range(24)); TO = sum(S[h][0] for h in range(24)); TG = sum(S[h][1] for h in range(24))
print('時台  広告費(14日)  取り分  クリック率  Meta購入  Shopify注文  注文/広告費1万円  売上(値引前)÷広告費')
for h in range(24):
    c, im, cl, pu = M[h]; o, g = S[h]
    print(f'{h:2d}   {c:9,}   {c/TC*100:4.1f}%   {cl/im*100:4.2f}%   {pu:4d}     {o:4d}        {o/c*10000:5.2f}          {g/c:5.2f}')
print(f'計   {TC:9,}           {sum(M[h][2] for h in range(24))/sum(M[h][1] for h in range(24))*100:4.2f}%   {sum(M[h][3] for h in range(24)):4d}     {TO:4d}        {TO/TC*10000:5.2f}          {TG/TC:5.2f}')
for name, hs in (('夜中 1〜6時台', range(1, 7)), ('0〜6時台', range(0, 7)), ('7〜23時台', range(7, 24))):
    c = sum(M[h][0] for h in hs); pu = sum(M[h][3] for h in hs); o = sum(S[h][0] for h in hs); g = sum(S[h][1] for h in hs)
    print(f'{name}: 広告費 {c:,}（{c/TC*100:.1f}%・1日 {c/14:,.0f}円）・Meta購入 {pu}（1万円あたり {pu/c*10000:.2f}）・Shopify注文 {o}（{o/TO*100:.1f}%・1万円あたり {o/c*10000:.2f}）・売上(値引前)÷広告費 {g/c:.2f}')
