# -*- coding: utf-8 -*-
"""11/18 定例「昨日の実績分析して。特にパフォ悪かった理由を細かく」: 11/17 の購入率の低さを、①店全体の段（来訪→カート→決済画面→購入）を過去30日と比べ、②入口ページ（＝広告の商品）別に 11/3〜16 の率から期待を出して分ける。
入力: o1117/funnel_daily_1018_1117.json・o1117/landing_1117_raw.json"""
import json, math, statistics as st
D = __file__.rsplit('/', 1)[0] + '/'
def ple(k, l): return sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
F = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'funnel_daily_1018_1117.json'))['rows']}
T = '2026-11-17'; P = [d for d in sorted(F) if d < T and d != '2026-11-03'][-30:]
print(f'■ 店全体の段（過去30日・祝日11/3除く・{P[0][5:]}〜{P[-1][5:]}）')
for lab, f in [('カート÷来訪', lambda v: v[1] / v[0]), ('決済画面÷カート', lambda v: v[2] / v[1]), ('購入÷決済画面', lambda v: v[3] / v[2]), ('購入÷来訪', lambda v: v[3] / v[0])]:
    t = f(F[T]); xs = [f(F[d]) for d in P]
    print(f"  {lab}: {t*100:.2f}%・過去30日 {min(xs)*100:.2f}〜{max(xs)*100:.2f}%（中央値 {st.median(xs)*100:.2f}%）・今日より低い日 {sum(x < t for x in xs)}/30")
L = json.load(open(D + 'landing_1117_raw.json'))
A = {r[0]: [int(x) for x in r[1:]] for r in L['rows17']}; B = {r[0]: [int(x) for x in r[1:]] for r in L['rowsb']}
NM = {'glass': 'ガラスクリーナー', 'W': 'W固定', 'nano': 'ナノガラス', 'nose': 'ノーズ', 'clip': 'マルチクリップ', 'wiper': 'ワイパー', 'door': 'ドア', '4in1': '4-in-1', 'insole': 'インソール', 'blanket': 'ブランケット', 'home': 'トップページ', 'shaver': 'シェーバー', 'brush': '洗車ブラシ', 'glove': 'グローブ'}
print('■ 入口ページ別（11/17 と 11/3〜16 の率から出した期待。購入＝決済完了の来訪）')
dc = dp = 0
for k, v in A.items():
    if k not in B or B[k][0] < 200:
        print(f"  {NM[k]}: 来訪 {v[0]}・カート {v[1]}（{v[1]/v[0]*100:.1f}%）・購入 {v[3]}（{v[3]/v[0]*100:.1f}%）（比べる過去が短い）"); continue
    b = B[k]; ec = b[1] / b[0] * v[0]; ep = b[3] / b[0] * v[0]; dc += v[1] - ec; dp += v[3] - ep
    pc = ple(v[1], ec) if v[1] < ec else 1 - ple(v[1] - 1, ec); pp = ple(v[3], ep) if v[3] < ep else 1 - ple(v[3] - 1, ep)
    print(f"  {NM[k]}: 来訪 {v[0]}・カート {v[1]}（{v[1]/v[0]*100:.1f}%・ふだん {b[1]/b[0]*100:.1f}%・期待 {ec:.1f}・{'少ない' if v[1] < ec else '多い'}側 {pc*100:.0f}%）・購入 {v[3]}（{v[3]/v[0]*100:.1f}%・ふだん {b[3]/b[0]*100:.1f}%・期待 {ep:.1f}・{'少ない' if v[3] < ep else '多い'}側 {pp*100:.0f}%）")
print(f'  過去のあるページの合計: カート 期待との差 {dc:+.1f}・購入 期待との差 {dp:+.1f}')
