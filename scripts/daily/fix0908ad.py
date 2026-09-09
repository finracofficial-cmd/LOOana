# -*- coding: utf-8 -*-
"""9/8広告費を確定値で上書き（adset合算・アカウント合計241,510と差0円）"""
import csv
FINAL={'ナノガラス脱毛パッド':58207+16727,'W固定スマホ車載ホルダー':29359,'快適マジックインソール':26914,
'カタログ全部（テスト）':18312,'ムダ毛シェーバー':16447,'バランスケアスリッパ':14722,'4-in-1マルチクリーナー':9918,
'伸縮ガラスクリーナー':9703,'温感EMSフェイシャルワンド':9656,'姿勢サポートチェア':8267,
'ナノバブルシャワーヘッド':7920,'2WAYシートボックス':8004,'むくみ取りかっさ':7354}
assert sum(FINAL.values())==241510, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-08' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-08')
print('updated',n,'rows / 9/8合計',tot); assert tot==241510
