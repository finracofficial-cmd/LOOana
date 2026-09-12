# -*- coding: utf-8 -*-
"""9/11広告費を確定値で上書き（adset合算・アカウント合計229,184と差0円）"""
import csv
FINAL={'ナノガラス脱毛パッド':58512+16538,'W固定スマホ車載ホルダー':31140,'快適マジックインソール':30967,
'伸縮ガラスクリーナー':14697,'カタログ全部（テスト）':13039,'ナノバブルシャワーヘッド':12746,
'バランスケアスリッパ':12438,'ムダ毛シェーバー':12129,'高見えレザーヘッドレストフック':9821,
'姿勢サポートチェア':9058,'4-in-1マルチクリーナー':8099}
assert sum(FINAL.values())==229184, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-11' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-11')
print('updated',n,'rows / 9/11合計',tot); assert tot==229184
