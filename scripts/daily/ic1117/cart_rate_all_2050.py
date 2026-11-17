# -*- coding: utf-8 -*-
"""11/17(火) 20:5x 「もっと全期間で見てみてカート入れる割合」
店全体（Shopify）の 来訪→カート→決済画面→購入 を月別・週別（終日・11/16まで）に並べる。今日（11/17）は 0〜19時台なので、同じ時刻で切った過去と比べる（funnel_2040.txt）
入力: cart_rate_all_raw.json（2026-03 以前は来訪が月1万未満のため省く）"""
import json
J = json.load(open(__file__.rsplit('/', 1)[0] + '/cart_rate_all_raw.json'))
def line(lab, v):
    s, c, k, p = [int(x) for x in v]
    return f"  {lab}: 来訪 {s:,}・カート÷来訪 {c/s*100:.1f}%・決済画面÷カート {k/c*100:.0f}%・購入÷決済画面 {p/k*100:.0f}%・購入÷来訪 {p/s*100:.2f}%"
print('■ 月別（終日）')
for r in J['month']['rows']: print(line(r[0][:7] + ('（1〜16日）' if r[0] == '2026-11-01' else ''), r[1:]))
print('■ 週別（月曜はじまり・終日）')
for r in J['week']['rows']: print(line(r[0][5:] + '〜' + ('（11/16 の1日だけ）' if r[0] == '2026-11-16' else ''), r[1:]))
