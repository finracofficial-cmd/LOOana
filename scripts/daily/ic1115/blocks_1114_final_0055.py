# -*- coding: utf-8 -*-
"""11/14 の朝・昼・夜を終日で確定（2026-11-15 00:5x ユーザー「夜と朝のCVR低かったのは結局なんだったん？」）
入力: Shopify FROM sessions SHOW sessions, sessions_with_cart_additions, sessions_that_reached_checkout, sessions_that_completed_checkout TIMESERIES hour SINCE 2026-11-14 UNTIL 2026-11-15（00:3x 取得・時刻は UTC 表示 → +9時間で JST）
帯は ic1114/block_swing_2150 と同じ（朝 0〜8時台・昼 9〜17時台・夜 18〜23時台）"""
import math
# JST 時台: (来訪, カート, 決済画面, 払い終えた)
H = {0: (65, 5, 6, 3), 1: (44, 2, 2, 1), 2: (33, 1, 1, 0), 3: (37, 1, 0, 0), 4: (50, 2, 1, 0), 5: (51, 3, 2, 1), 6: (80, 5, 4, 1), 7: (178, 10, 9, 4), 8: (160, 12, 10, 1),
     9: (174, 13, 12, 7), 10: (161, 11, 10, 6), 11: (122, 8, 9, 6), 12: (116, 5, 5, 2), 13: (114, 3, 3, 3), 14: (99, 7, 7, 5), 15: (107, 17, 15, 9), 16: (118, 6, 5, 3), 17: (129, 3, 5, 2),
     18: (118, 4, 4, 1), 19: (125, 7, 7, 1), 20: (136, 5, 5, 2), 21: (132, 6, 5, 3), 22: (134, 7, 7, 1), 23: (87, 4, 4, 1)}
assert sum(v[0] for v in H.values()) == 2570 and sum(v[3] for v in H.values()) == 63   # 日別の取得（sess_daily_1004_1114.json の 11/14: 2570・63）と一致
B = {'朝 0〜8時台': range(0, 9), '昼 9〜17時台': range(9, 18), '夜 18〜23時台': range(18, 24)}
r = {}
for k, hs in B.items():
    s, c, ck, cp = (sum(H[h][i] for h in hs) for i in range(4)); r[k] = cp / s
    exp = ck * 0.57; p = sum(math.comb(ck, j) * 0.57 ** j * 0.43 ** (ck - j) for j in range(cp + 1))
    print(f'{k}: 来訪 {s}・カート {c}（{c/s*100:.1f}%）・決済画面 {ck}（カートの{ck/c*100:.0f}%）・払い終えた {cp}（決済画面の {cp/ck*100:.0f}%・ふだん57%なら {exp:.1f}・これ以下になる確率 {p*100:.1f}%）・購入率 {cp/s*100:.2f}%')
print(f'一番高い帯÷一番低い帯 = {max(r.values())/min(r.values()):.2f}倍（過去29日の中央値 1.36倍・最大 2.09倍＝ic1114/block_swing_2150）')
s = sum(v[0] for v in H.values()); cp = sum(v[3] for v in H.values()); ck = sum(v[2] for v in H.values())
print(f'1日: 来訪 {s}・決済画面 {ck}・払い終えた {cp}（決済画面の {cp/ck*100:.0f}%）・購入率 {cp/s*100:.2f}%')
