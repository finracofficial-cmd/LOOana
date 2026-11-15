# -*- coding: utf-8 -*-
"""今朝（11/15 0〜8時台）の注文÷来訪を、過去21日の同じ時間帯と並べる（2026-11-15 09:0x ユーザー「セッション600だから CVR 3% が平均値だと思うので18ないとおかしい。今は14だからブレの範囲内。こんな感じ？」）
入力: 来訪＝ic1114/sess_hourly_1015_1113.json（〜11/13）・blocks_1114_final_0055.py の 11/14・sess_hour_1115_0907.json（今日）／注文＝ic1114/sales_hour_1024_1114.json（〜11/14）と今日の6行（09:07 取得の FROM sales SHOW orders GROUP BY day, hour_of_day を下に貼る）
今日の9時台は始まったばかり（来訪19・注文0）なので 0〜8時台で切る。日中の数字なので判定・予算には使わない"""
import json, math, collections
D = __file__.rsplit('/scripts/', 1)[0] + '/scripts/daily/'
SE = collections.defaultdict(int); OR = collections.defaultdict(int)
for d, h, s, *_ in json.load(open(D + 'ic1114/sess_hourly_1015_1113.json'))['rows']:
    if int(h) <= 8: SE[d] += int(s)
SE['2026-11-14'] = 65 + 44 + 33 + 37 + 50 + 51 + 80 + 178 + 160   # blocks_1114_final_0055.py の 0〜8時台
for h, s, *_ in json.load(open(D + 'ic1115/sess_hour_1115_0907.json'))['rows']:
    if int(h) <= 8: SE['2026-11-15'] += int(s)
for d, h, o, g in json.load(open(D + 'ic1114/sales_hour_1024_1114.json'))['rows']:
    if int(h) <= 8: OR[d] += int(o)
TODAY = {0: 2, 1: 1, 5: 2, 6: 3, 7: 1, 8: 5}   # 09:07 取得
OR['2026-11-15'] = sum(TODAY.values())
assert OR['2026-11-13'] == 18 and OR['2026-11-14'] == 12   # 09:07 の取り直し（11/13: 1+1+2+1+2+2+2+7・11/14: 3+1+2+4+2）と一致
DAYS = [d for d in sorted(SE) if '2026-10-25' <= d <= '2026-11-14']
assert len(DAYS) == 21
s21 = sum(SE[d] for d in DAYS); o21 = sum(OR[d] for d in DAYS); p = o21 / s21
r = {d: OR[d] / SE[d] for d in DAYS}
T = OR['2026-11-15'] / SE['2026-11-15']; exp = SE['2026-11-15'] * p
pr = sum(math.exp(-exp) * exp ** k / math.factorial(k) for k in range(OR['2026-11-15'] + 1))
z = (OR['2026-11-15'] - exp) / math.sqrt(exp * 1.32)
print(f"今日 0〜8時台: 来訪 {SE['2026-11-15']}・注文 {OR['2026-11-15']}・注文÷来訪 {T*100:.2f}%")
print(f'過去21日（10/25〜11/14）の 0〜8時台: 来訪 {s21:,}・注文 {o21}・{p*100:.2f}%／日ごとに {min(r.values())*100:.2f}%〜{max(r.values())*100:.2f}%・今日より低い日 {sum(1 for x in r.values() if x < T)}/21')
print(f'ふだんの {p*100:.2f}% なら期待 {exp:.1f}件。14件以下になる確率 {pr*100:.0f}%・日ごとのぶれ（φ=1.32）込みで z {z:+.2f}')
print('日ごと:', ' '.join(f'{d[5:]} {OR[d]}/{SE[d]}' for d in DAYS))
# 段階別（今日 0〜8時台・Shopify の時間帯別）
H = [r for r in json.load(open(D + 'ic1115/sess_hour_1115_0907.json'))['rows'] if int(r[0]) <= 8]
s, c, ck, cp = (sum(int(r[i]) for r in H) for i in range(1, 5))
pb = sum(math.comb(ck, j) * 0.57 ** j * 0.43 ** (ck - j) for j in range(cp + 1))
print(f'段階: カート {c}（{c/s*100:.1f}%）・決済画面 {ck}・払い終えた {cp}（決済画面の {cp/ck*100:.0f}%・ふだん57%なら {ck*0.57:.1f}・これ以下の確率 {pb*100:.0f}%）')
print(f'Shopify の CVR（払い終えたセッション÷セッション・9時台の途中まで）: {cp}/{s+19} = {cp/(s+19)*100:.2f}%（注文14のうち 00:00 の #31992 は 23:59 に始まったセッションなので前日に数えられる）')
