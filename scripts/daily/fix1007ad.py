# -*- coding: utf-8 -*-
"""10/7広告費を確定値で上書き（アカウント合計251,228と差0円。暫定250,127から+1,101円）"""
import csv
FINAL={'UV歯ブラシ除菌器':80,'W固定スマホ車載ホルダー':32631,'カタログ全部（テスト）':9565,
'ナノガラス脱毛パッド':77000,'ネックマッサージャー2':11169,'バランスケアスリッパ':8807,'伸縮ガラスクリーナー':30816,
'姿勢サポートチェア':8759,'快適マジックインソール':37690,'携帯電動シェーバー':8776,'高見えレザーヘッドレストフック':19419,
'4-in-1マルチクリーナー':6516}
assert sum(FINAL.values())==251228, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-07' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-07')
print('updated',n,'rows / 10/7合計',tot); assert tot==251228
