# -*- coding: utf-8 -*-
"""9/10広告費を確定値で上書き（adset合算・アカウント合計283,189と差0円）"""
import csv
FINAL={'ナノガラス脱毛パッド':76932+18071,'快適マジックインソール':36653,'W固定スマホ車載ホルダー':36083,
'ムダ毛シェーバー':19867,'伸縮ガラスクリーナー':17558,'バランスケアスリッパ':16430,
'ナノバブルシャワーヘッド':16158,'カタログ全部（テスト）':15907,'高見えレザーヘッドレストフック':10970,
'姿勢サポートチェア':9204,'4-in-1マルチクリーナー':9129,'2WAYシートボックス':153,'むくみ取りかっさ':74}
assert sum(FINAL.values())==283189, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-10' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-10')
print('updated',n,'rows / 9/10合計',tot); assert tot==283189
