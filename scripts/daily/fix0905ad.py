# -*- coding: utf-8 -*-
"""2026-09-06 17:00: 9/5広告費を確定値で上書き（217,623 → 218,217・+594円/+0.27%）。
   9/6 00:02 取得の暫定値を、同日17:00取得のキャンペーン別実測で置換。"""
import csv
B = 'data/daily/'
AD = {'ナノガラス脱毛パッド':74037,'W固定スマホ車載ホルダー':26038,'快適マジックインソール':24536,
 'カタログ全部（テスト）':16382,'ムダ毛シェーバー':15384,'バランスケアスリッパ':13020,
 'むくみ取りかっさ':10170,'姿勢サポートチェア':7660,'2WAYシートボックス':7458,
 'ナノバブルシャワーヘッド':7369,'温感EMSフェイシャルワンド':6777,'完全遮光・接触冷感UVハット':5920,
 '4-in-1マルチクリーナー':3417,'偏光・調光サングラス':49}
assert sum(AD.values()) == 218217, sum(AD.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-05']
assert len(old) == 14 and abs(sum(float(r[2]) for r in old) - 217623) < 1
out = [r for r in rows if not (r and r[0]=='2026-09-05')]
out += [['2026-09-05', c, str(v)] for c, v in AD.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/5 広告費を上書き: 217,623 → {sum(AD.values()):,}（+{sum(AD.values())-217623}円 / +0.27%）')
