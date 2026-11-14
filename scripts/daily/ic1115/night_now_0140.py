# -*- coding: utf-8 -*-
"""今夜の0時からの広告費（Meta 01:3x 取得 5,561円・Meta購入3）と注文（Shopify 0時以降に作られた注文2件 16,128円）を、過去15日の 0時台／0〜1時台 と並べる
（2026-11-15 01:3x ユーザー「今もう六千円くらい使ってたからさ」）。日中の数字なので判定・予算には使わない
入力: ic1114/meta_hourly_1031_1114.txt・ic1114/sales_hour_1024_1114.json（10/31〜11/14 の0時台・1時台はどちらも揃っている）"""
import json, collections
D = __file__.rsplit('/scripts/', 1)[0] + '/scripts/daily/ic1114/'
C = collections.defaultdict(lambda: [0, 0]); O = collections.defaultdict(lambda: [0, 0])
for l in open(D + 'meta_hourly_1031_1114.txt'):
    if l[0] == '#': continue
    d, rest = l.split(',', 1); h = int(rest[1:3])
    if h < 2: C[d][h] += int(rest.split('",')[1].split(',')[0])
for d, h, o, g in json.load(open(D + 'sales_hour_1024_1114.json'))['rows']:
    if int(h) < 2 and d >= '2026-10-31': O[d][int(h)] += int(o)
days = sorted(C)
assert len(days) == 15 and all(d in O for d in days)
c0 = sorted(C[d][0] for d in days); c01 = sorted(sum(C[d]) for d in days)
o0 = sorted(O[d][0] for d in days); o01 = sorted(sum(O[d]) for d in days)
print(f'過去15日（10/31〜11/14）の広告費: 0時台 {c0[0]:,}〜{c0[-1]:,}円（中央値 {c0[7]:,}）／0〜1時台 {c01[0]:,}〜{c01[-1]:,}円（中央値 {c01[7]:,}）')
print(f'過去15日の注文: 0時台 {o0[0]}〜{o0[-1]}件（中央値 {o0[7]}）／0〜1時台 {o01[0]}〜{o01[-1]}件（中央値 {o01[7]}）')
print('今夜（01:3x）: 広告費 5,561円・注文 2件（16,128円）・Meta購入 3')
print(f'  0〜1時台の広告費が 5,561円より少なかった日: {sum(1 for x in c01 if x < 5561)}/15 ／ 0〜1時台の注文が2件以下の日: {sum(1 for x in o01 if x <= 2)}/15')
