# -*- coding: utf-8 -*-
"""11/18 「1日単位で3割近くのブレは偶然で処理できる？」
①理屈: カートの件数がポアソンなら、1日のぶれ（1σ）は 1/√期待件数。②実際: 10/18〜11/16 の30日の日別カート率が、その直前14日の率からどれだけずれたかを数え、
ポアソンで出るぶれ（z の標準偏差＝1）と比べる（実際の z の標準偏差が1より大きければ、偶然以外の日ごとの動きもある）。入力: o1117/cart_daily_pages_raw.json・o1117/funnel_daily_1018_1117.json・o1117/landing_1117_raw.json"""
import json, math, statistics as st, collections, datetime
D = __file__.rsplit('/', 1)[0] + '/'
print('■ 理屈（ポアソン）: 期待のカート件数ごとの1日のぶれ（1σ・2σ）')
for e in (5, 10, 20, 30, 60, 140):
    print(f'  期待 {e}件: ±{100/math.sqrt(e):.0f}%（1σ・3日に1日はこれ以上ずれる）・±{200/math.sqrt(e):.0f}%（2σ・20日に1日）')
L = json.load(open(D + 'landing_1117_raw.json')); A = {r[0]: [int(x) for x in r[1:]] for r in L['rows17']}; B = {r[0]: [int(x) for x in r[1:]] for r in L['rowsb']}
NM = {'glass': 'ガラスクリーナー', 'W': 'W固定', 'nano': 'ナノガラス', 'nose': 'ノーズ', 'wiper': 'ワイパー', 'door': 'ドア', '4in1': '4-in-1', 'brush': '洗車ブラシ'}
print('■ 11/17 の下がり幅を、そのページの期待件数のぶれで割る')
for k in NM:
    a, b = A[k], B[k]; e = b[1] / b[0] * a[0]; dv = a[1] / e - 1; z = (a[1] - e) / math.sqrt(e)
    print(f'  {NM[k]}: {dv:+.0%}・期待 {e:.1f}件（1σ ±{100/math.sqrt(e):.0f}%）→ {z:+.1f}σ')
R = collections.defaultdict(dict)
for d, k, s, c in json.load(open(D + 'cart_daily_pages_raw.json'))['rows']: R[k][d] = (int(s), int(c))
F = {r[0]: [int(x) for x in r[1:3]] for r in json.load(open(D + 'funnel_daily_1018_1117.json'))['rows']}
R['店全体'] = {d: tuple(v) for d, v in F.items()}
print('■ 実際の日ごとのぶれ（各日を、その直前14日の率から出した期待と比べる・10/18〜11/16）')
for k in ['glass', 'W', 'nano', '店全体']:
    ds = sorted(R[k]); zs = []; devs = []
    for i, d in enumerate(ds):
        if d >= '2026-11-17' or i < 14: continue
        prev = ds[i - 14:i]; r = sum(R[k][x][1] for x in prev) / sum(R[k][x][0] for x in prev)
        e = r * R[k][d][0]; zs.append((R[k][d][1] - e) / math.sqrt(e)); devs.append(R[k][d][1] / e - 1)
    big = sum(abs(x) >= 0.25 for x in devs)
    d = '2026-11-17'; i = ds.index(d); prev = ds[i - 14:i]; r = sum(R[k][x][1] for x in prev) / sum(R[k][x][0] for x in prev); e = r * R[k][d][0]
    z17 = (R[k][d][1] - e) / math.sqrt(e)
    print(f"  {NM.get(k, k)}: {len(zs)}日・z の標準偏差 {st.pstdev(zs):.2f}（偶然だけなら1.0）・±25%以上ずれた日 {big}/{len(devs)}・11/17 {R[k][d][1]/e-1:+.0%}（{z17:+.1f}σ・期待 {e:.1f}件）・それより下にずれた日 {sum(x < z17 for x in zs)}/{len(zs)}")
