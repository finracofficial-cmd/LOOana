# -*- coding: utf-8 -*-
"""11/25 「商品を選ぶ ▼」の固定ボタン（11/19 15:15ごろ〜）の途中経過。正式な判定は 11/27 朝（11/20〜26 の7日）。
スマホ・広告から来た人（referrer_source=social）だけ。前＝11/12〜18（7日）・後＝11/20〜24（5日。11/19 は入れた日なので除く）
同じ日に VIP特典の配送設定・カートの文も変えた。11/19〜24 は試しの商品（UV・毛玉・卓上加湿器）も走っていた＝どれの分かは分けられない"""
import json, math
rows = {r[0][:10]: [int(x) for x in r[1:]] for r in json.load(open('scripts/daily/ic1125/cvrkit/sess_mobile_social_1105_1124_raw.json', encoding='utf-8'))['rows']}
def blk(a, b): ds = [d for d in rows if a <= d <= b]; return len(ds), [sum(rows[d][i] for d in ds) for i in range(4)]
def ratio(x1, n1, x2, n2): r = (x1 / n1) / (x2 / n2); s = math.sqrt(1 / x1 + 1 / x2); return f"{r:.2f}倍（幅 {r * math.exp(-2 * s):.2f}〜{r * math.exp(2 * s):.2f}）"
(nb, B), (na, A), (n0, P) = blk('2026-11-12', '2026-11-18'), blk('2026-11-20', '2026-11-24'), blk('2026-11-05', '2026-11-11')
for nm, n, x in (('その前の週 11/5〜11', n0, P), ('前 11/12〜18', nb, B), ('後 11/20〜24', na, A)):
    print(f"  {nm}（{n}日）: 来訪 {x[0]:,}・カートに入れた {x[1]}（{x[1] / x[0] * 100:.2f}%）・決済画面 {x[2]}（{x[2] / x[0] * 100:.2f}%）・購入 {x[3]}（{x[3] / x[0] * 100:.2f}%）｜決済画面÷カート {x[2] / x[1] * 100:.0f}%・購入÷決済画面 {x[3] / x[2] * 100:.1f}%")
print(f"  後 ÷ 前: カートに入れる割合 {ratio(A[1], A[0], B[1], B[0])}・決済画面まで {ratio(A[2], A[0], B[2], B[0])}・買う率 {ratio(A[3], A[0], B[3], B[0])}・購入÷決済画面 {ratio(A[3], A[2], B[3], B[2])}")
print(f"  前 ÷ その前の週（何も変えていない週どうしのぶれ）: カートに入れる割合 {ratio(B[1], B[0], P[1], P[0])}・買う率 {ratio(B[3], B[0], P[3], P[0])}")
