# -*- coding: utf-8 -*-
"""2026-08-30 の広告費を health_check（30日実測）− CSV（8/01-8/29実測）で導出する。
   ★推計ではなく「2つの実測の差」。窓の当て方は耳かき（8/28開始）で検証する:
     耳かきは 8/01-8/29 の CSV 合計 = 10,675 なので、HC − 10,675 が 8/30 の消化になる。
   使い方: HC の値を下の HC 辞書に貼って実行する。"""
import csv, collections, sys, json

HC = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
if HC is None:
    print('usage: python3 derive0830.py hc.json   （{"キャンペーン名": spend, ...}）'); sys.exit(1)

AD = collections.defaultdict(dict)
for r in csv.reader(open('data/daily/daily_ad.csv')):
    if not r or r[0] == 'date': continue
    AD[r[1]][r[0]] = AD[r[1]].get(r[0], 0) + float(r[2])
ALLD = sorted({d for c in AD for d in AD[c]})
assert ALLD[-1] == '2026-08-29', f'CSVの最終日が8/29ではない: {ALLD[-1]}'
W = [d for d in ALLD if '2026-08-01' <= d <= '2026-08-29']
assert len(W) == 29, len(W)
print(f'CSV窓 {W[0]}〜{W[-1]}（{len(W)}日）／ health_check窓 = 8/01-8/30（30日・UTC基準）')

# 窓の検証: 8/28開始のビジュアル耳かきは CSV合計 = 8/28+8/29 の2日分のはず
ear_csv = sum(AD['ビジュアル耳かき'].get(d, 0) for d in W)
print(f'\n■ 窓の検証（ビジュアル耳かき・8/28開始）: CSV(8/01-8/29) = {ear_csv:,.0f}円'
      f' ／ HC = {HC.get("ビジュアル耳かき", 0):,}円 → 8/30 = {HC.get("ビジュアル耳かき",0)-ear_csv:,.0f}円')

print(f'\n{"キャンペーン":<28}{"HC(30日)":>12}{"CSV(29日)":>12}{"→ 8/30":>10}')
OUT, tot = [], 0
for c, hc in sorted(HC.items(), key=lambda x: -x[1]):
    base = sum(AD[c].get(d, 0) for d in W)
    v = round(hc - base)
    assert v >= 0, f'{c}: 導出値が負（{v}）。窓の当て方が違う'
    OUT.append((c, v)); tot += v
    print(f'{c:<28}{hc:>12,}{base:>12,.0f}{v:>10,}')
print(f'{"合計":<28}{sum(HC.values()):>12,}{sum(sum(AD[c].get(d,0) for d in W) for c in HC):>12,.0f}{tot:>10,}')
print('\nAD = ' + repr([(c, v) for c, v in OUT if v > 0]))
