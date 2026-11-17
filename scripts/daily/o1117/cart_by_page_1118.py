# -*- coding: utf-8 -*-
"""11/18 00:3x 「カートに入れる率だけ悪かったの？平均と比較してどうなの？商品別には？」
11/17 の入口ページ別 カート÷来訪 と カート→購入 を、そのページの 11/3〜16 と比べる。入力: o1117/landing_1117_raw.json・o1117/funnel_daily_1018_1117.json"""
import json, math, statistics as st
D = __file__.rsplit('/', 1)[0] + '/'
def ple(k, l): return sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
L = json.load(open(D + 'landing_1117_raw.json'))
A = {r[0]: [int(x) for x in r[1:]] for r in L['rows17']}; B = {r[0]: [int(x) for x in r[1:]] for r in L['rowsb']}
F = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'funnel_daily_1018_1117.json'))['rows']}
P = [d for d in sorted(F) if d < '2026-11-17' and d != '2026-11-03'][-30:]
s = sum(F[d][0] for d in P); print('■ 店全体（過去30日の平均＝合計どうしの比・中央値）')
for lab, i, j in [('カート÷来訪', 1, 0), ('決済画面÷カート', 2, 1), ('購入÷決済画面', 3, 2), ('購入÷来訪', 3, 0)]:
    t = F['2026-11-17'][i] / F['2026-11-17'][j]; av = sum(F[d][i] for d in P) / sum(F[d][j] for d in P); md = st.median(F[d][i] / F[d][j] for d in P)
    print(f'  {lab}: 11/17 {t*100:.2f}%・30日平均 {av*100:.2f}%（{t/av-1:+.0%}）・中央値 {md*100:.2f}%')
NM = {'glass': 'ガラスクリーナー', 'W': 'W固定', 'nano': 'ナノガラス', 'nose': 'ノーズ', 'wiper': 'ワイパー', 'door': 'ドア', '4in1': '4-in-1', 'insole': 'インソール', 'blanket': 'ブランケット', 'shaver': 'シェーバー', 'brush': '洗車ブラシ', 'home': 'トップページ'}
NEW = {'insole', 'blanket', 'shaver', 'nose'}   # 11/13 以降に出した・出し直した商品（ノーズ v2 11/14・シェーバー v2 11/14・ブランケット 11/13・インソール v3 11/16）
print('■ 入口ページ別（ふだん＝11/3〜16 の同じページ）')
tot = {True: [0, 0.0], False: [0, 0.0]}
for k in ['glass', 'W', 'nano', 'nose', 'wiper', 'door', '4in1', 'insole', 'blanket', 'shaver', 'brush', 'home']:
    a, b = A[k], B[k]; r, rb = a[1] / a[0], b[1] / b[0]; e = rb * a[0]
    p = ple(a[1], e) if a[1] < e else 1 - ple(a[1] - 1, e)
    pc = a[3] / a[1] if a[1] else 0; pcb = b[3] / b[1]
    if k != 'home': tot[k in NEW][0] += a[1]; tot[k in NEW][1] += e
    print(f"  {NM[k]}: カート÷来訪 {r*100:.1f}%（ふだん {rb*100:.1f}%・{r/rb-1:+.0%}・カート {a[1]}／期待 {e:.1f}・{'少ない' if a[1] < e else '多い'}側 {p*100:.0f}%）・カート→購入 {pc*100:.0f}%（ふだん {pcb*100:.0f}%）")
for new, lab in ((False, '以前からある商品（ガラス・W固定・ナノ・ワイパー・ドア・4-in-1・ブラシ）'), (True, '11/13以降に出した・出し直した商品（ノーズ・インソール・ブランケット・シェーバー）')):
    o, e = tot[new]; p = ple(o, e) if o < e else 1 - ple(o - 1, e)
    print(f"  {lab}: カート {o}／期待 {e:.1f}（{o/e-1:+.0%}・{'少ない' if o < e else '多い'}側 {p*100:.1f}%）")
