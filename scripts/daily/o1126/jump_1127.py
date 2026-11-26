# -*- coding: utf-8 -*-
"""11/27 「商品を選ぶ ▼」の固定ボタン（11/19 15:15ごろ〜）の前後の判定（途中経過は ic1125/cvrkit/jump_interim.txt）。
スマホ・広告から来た人（session_device_type=mobile・referrer_source=social）だけ。前＝11/12〜18（7日）・後＝11/20〜26（7日。11/19 は入れた日なので除く）・その前の週＝11/5〜11
同じ日に VIP特典の配送設定・カートの文も変えた。11/19〜24 は試しの商品（UV・毛玉・卓上加湿器・チェア）も走っていた＝どれの分かは分けられない
11/22〜 は「social の来訪 ÷ Meta のクリック」が下がっている（広告のクリックが direct に数えられる分が増えた可能性・未確認）ので、social だけの数は分母が前と同じ人たちとは限らない"""
import json, math, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'; out = []
def P(s): print(s); out.append(s)
rows = {r[0][:10]: [int(x) for x in r[1:]] for r in json.load(open(D + 'sess_mobile_social_1105_1126_raw.json', encoding='utf-8'))['rows']}
old = {r[0][:10]: [int(x) for x in r[1:]] for r in json.load(open(D + '../ic1125/cvrkit/sess_mobile_social_1105_1124_raw.json', encoding='utf-8'))['rows']}
assert all(rows[d] == old[d] for d in old if d <= '2026-11-23'), '前に取った数字と違う日がある'
def blk(a, b): ds = [d for d in rows if a <= d <= b]; return len(ds), [sum(rows[d][i] for d in ds) for i in range(4)]
def ratio(x1, n1, x2, n2): r = (x1 / n1) / (x2 / n2); s = math.sqrt(1 / x1 + 1 / x2); return f"{r:.2f}倍（幅 {r * math.exp(-2 * s):.2f}〜{r * math.exp(2 * s):.2f}）"
(nb, B), (na, A), (n0, P0) = blk('2026-11-12', '2026-11-18'), blk('2026-11-20', '2026-11-26'), blk('2026-11-05', '2026-11-11')
P('■ 「商品を選ぶ ▼」の前後（スマホ・social）')
for nm, n, x in (('その前の週 11/5〜11', n0, P0), ('前 11/12〜18', nb, B), ('後 11/20〜26', na, A)):
    P(f"  {nm}（{n}日）: 来訪 {x[0]:,}・カートに入れた {x[1]}（{x[1] / x[0] * 100:.2f}%）・決済画面 {x[2]}（{x[2] / x[0] * 100:.2f}%）・購入 {x[3]}（{x[3] / x[0] * 100:.2f}%）｜決済画面÷カート {x[2] / x[1] * 100:.0f}%・購入÷決済画面 {x[3] / x[2] * 100:.1f}%")
P(f"  後 ÷ 前: カートに入れる割合 {ratio(A[1], A[0], B[1], B[0])}・決済画面まで {ratio(A[2], A[0], B[2], B[0])}・買う率 {ratio(A[3], A[0], B[3], B[0])}・購入÷決済画面 {ratio(A[3], A[2], B[3], B[2])}")
P(f"  後 ÷ その前の週: カートに入れる割合 {ratio(A[1], A[0], P0[1], P0[0])}・買う率 {ratio(A[3], A[0], P0[3], P0[0])}")
P(f"  前 ÷ その前の週（何も変えていない週どうしのぶれ）: カートに入れる割合 {ratio(B[1], B[0], P0[1], P0[0])}・買う率 {ratio(B[3], B[0], P0[3], P0[0])}")
P('  日ごと（後）: ' + '・'.join(f"{d[5:]} カート {rows[d][1]/rows[d][0]:.1%}・購入 {rows[d][3]/rows[d][0]:.1%}" for d in sorted(rows) if d >= '2026-11-20'))
open(D + 'jump_1127.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
