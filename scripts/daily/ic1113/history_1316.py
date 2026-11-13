# -*- coding: utf-8 -*-
"""11/13(金) 19:3x 「全期間の過去と比較してよ」
今日の 13〜16時台のカート投入の落ち込みを、過去の全日の 13〜16時台と比べる。
①その時間帯のカート率そのものの順位 ②その日のほかの時間帯と比べた落ち方（13〜16時台の期待＝その日の13〜16時台以外のカート率×13〜16時台の来訪）の順位
対象: Shopify は 13〜16時台の来訪 300以上の日、Meta は 13〜16時台の着地 200以上の日。今日のほかの時間帯は 0〜12時台と17〜19時台（途中）"""
import os, json, math
D = os.path.dirname(os.path.abspath(__file__)) + '/'
R = json.load(open(D + 'history_1316_raw.json')); T = '2026-11-13'
W = {r[0]: [int(x) for x in r[1:]] for r in R['shop_1316']['rows']}     # sessions, cart, checkout, completed
F = {r[0]: [int(x) for x in r[1:]] for r in R['shop_day']['rows']}      # sessions, cart, completed
iv = lambda x: 0 if x in ('null', '') else int(x)
MW = {r.split(',')[0]: [iv(x) for x in r.split(',')[1:]] for r in R['meta_1316']['rows']}   # cost, lpv, atc, purchase
MF = {r.split(',')[0]: [iv(x) for x in r.split(',')[1:]] for r in R['meta_day']['rows']}
def z(o, e): return (o - e) / math.sqrt(e) if e > 0 else 0
def show(lab, rows, key_rate, key_z):
    rows = [r for r in rows if r]
    t = next(r for r in rows if r[0] == T); past = [r for r in rows if r[0] != T]
    lower_rate = sum(r[key_rate] <= t[key_rate] for r in past); lower_z = sum(r[key_z] <= t[key_z] for r in past)
    worst = sorted(past, key=lambda r: r[key_z])[:5]
    print(f"■ {lab}: 比べた日 {len(past)}日（{past[0][0]}〜{past[-1][0]}）")
    print(f"  今日 13〜16時台のカート率 {t[key_rate]*100:.1f}%（過去 中央値 {sorted(r[key_rate] for r in past)[len(past)//2]*100:.1f}%・最低 {min(r[key_rate] for r in past)*100:.1f}%）・今日以下の日 {lower_rate}日")
    print(f"  その日のほかの時間帯と比べた落ち方: 今日 期待 {t[5]:.1f} に対し {t[4]}（ずれ {t[key_z]:.1f}）・今日と同じかそれ以上に落ちた日 {lower_z}日")
    print('  落ち方が大きかった過去の日: ' + '／'.join(f"{r[0][5:]} 期待{r[5]:.0f}→{r[4]}（{r[key_z]:.1f}）" for r in worst))
rows = []
for d, (s, c, k, b) in W.items():
    if d not in F or s < 300: continue
    fs, fc, fb = F[d]; rs, rc = fs - s, fc - c
    if rs <= 0: continue
    e = s * rc / rs; rows.append((d, s, c / s, None, c, e, z(c, e)))
show('Shopify（来訪→カート）', rows, 2, 6)
rows = []
for d, (co, lp, atc, pu) in MW.items():
    if d not in MF or lp < 200: continue
    fco, flp, fatc, fpu = MF[d]; rl, ra = flp - lp, fatc - atc
    if rl <= 0: continue
    e = lp * ra / rl; rows.append((d, lp, atc / lp, None, atc, e, z(atc, e)))
show('Meta ピクセル（着地→カート）', rows, 2, 6)
