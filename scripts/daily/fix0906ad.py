# -*- coding: utf-8 -*-
"""2026-09-08 00:30: 9/6広告費を確定値で上書き（291,845 → 291,924・+79円/+0.03%）。
   9/7 08:2x取得の暫定値を、9/8 00:2x取得の確定値で置換。"""
import csv
B = 'data/daily/'
AD = {'ナノガラス脱毛パッド':96943,'W固定スマホ車載ホルダー':35959,'快適マジックインソール':32934,
 'カタログ全部（テスト）':20446,'ムダ毛シェーバー':19790,'バランスケアスリッパ':18952,
 'むくみ取りかっさ':12628,'姿勢サポートチェア':11676,'温感EMSフェイシャルワンド':11380,
 '4-in-1マルチクリーナー':11349,'ナノバブルシャワーヘッド':10282,'2WAYシートボックス':9569,
 '完全遮光・接触冷感UVハット':16}
assert sum(AD.values()) == 291924, sum(AD.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-06']
assert len(old) == 13 and abs(sum(float(r[2]) for r in old) - 291845) < 1, (len(old),)
out = [r for r in rows if not (r and r[0]=='2026-09-06')]
out += [['2026-09-06', c, str(v)] for c, v in AD.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/6 広告費を上書き: 291,845 → {sum(AD.values()):,}（+{sum(AD.values())-291845}円）')
