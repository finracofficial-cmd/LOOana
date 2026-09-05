# -*- coding: utf-8 -*-
"""2026-09-05 13:15: 9/4広告費を確定値で上書き（257,125 → 257,498・+373円/+0.15%）。
   9/5 00:08取得の暫定値を、13:06取得のadset別実測で置換（ナノガラス=２+３の合算、サングラス=コピー含む）。
   9/1(+9円)・9/2(+1円)にも微小ドリフトがあるが、凍結済み日は触らない（決定記録に明記）。"""
import csv
B = 'data/daily/'
AD0904 = {'ナノガラス脱毛パッド':68297+24640,'W固定スマホ車載ホルダー':29699,'快適マジックインソール':27909,
 'カタログ全部（テスト）':18504,'ムダ毛シェーバー':18131,'バランスケアスリッパ':13864,
 '温感EMSフェイシャルワンド':10760,'姿勢サポートチェア':9231,'むくみ取りかっさ':8503,
 'ナノバブルシャワーヘッド':8381,'2WAYシートボックス':8296,'完全遮光・接触冷感UVハット':6267,
 '偏光・調光サングラス':5016}
assert sum(AD0904.values()) == 257498, sum(AD0904.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-04']
assert len(old) == 13 and abs(sum(float(r[2]) for r in old) - 257125) < 1
out = [r for r in rows if not (r and r[0]=='2026-09-04')]
out += [['2026-09-04', c, str(v)] for c, v in AD0904.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/4 広告費を上書き: 257,125 → {sum(AD0904.values()):,}（+{sum(AD0904.values())-257125}円）')
