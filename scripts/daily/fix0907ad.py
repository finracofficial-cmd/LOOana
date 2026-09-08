# -*- coding: utf-8 -*-
"""2026-09-09 00:15: 9/7広告費を確定値で上書き（217,183 → 217,551・+368円/+0.17%）。広告セット合算・アカウント照合 差0円。"""
import csv
B='data/daily/'
AD={'ナノガラス脱毛パッド':52750+15455,'W固定スマホ車載ホルダー':24777,'快適マジックインソール':21926,
'カタログ全部（テスト）':17193,'ムダ毛シェーバー':15083,'バランスケアスリッパ':13424,'4-in-1マルチクリーナー':12402,
'温感EMSフェイシャルワンド':10385,'むくみ取りかっさ':9360,'姿勢サポートチェア':9066,
'ナノバブルシャワーヘッド':6828,'2WAYシートボックス':6816,'伸縮ガラスクリーナー':2086}
assert sum(AD.values())==217551, sum(AD.values())
rows=list(csv.reader(open(B+'daily_ad.csv',encoding='utf-8')))
old=[r for r in rows if r and r[0]=='2026-09-07']
assert len(old)==13 and abs(sum(float(r[2]) for r in old)-217183)<1
out=[r for r in rows if not (r and r[0]=='2026-09-07')]
out+=[['2026-09-07',c,str(v)] for c,v in AD.items()]
with open(B+'daily_ad.csv','w',encoding='utf-8',newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/7 広告費を上書き: 217,183 → {sum(AD.values()):,}（+{sum(AD.values())-217183}円）')
