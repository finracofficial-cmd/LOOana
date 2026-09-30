# -*- coding: utf-8 -*-
"""9/28広告費を確定値で上書き（アカウント合計254,409と差0円。暫定253,987から+422円）"""
import csv
FINAL={'UV歯ブラシ除菌器':10477,'W固定スマホ車載ホルダー':32648,'もちふわ肉球サンダル':9555,'カタログ全部（テスト）':8961,
'ナノガラス脱毛パッド':73100,'バランスケアスリッパ':8473,'伸縮ガラスクリーナー':28311,'姿勢サポートチェア':8501,
'快適マジックインソール':36143,'携帯電動シェーバー':8822,'電動眉シェーバー':8741,'高見えレザーヘッドレストフック':20677}
assert sum(FINAL.values())==254409, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-28' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-28')
print('updated',n,'rows / 9/28合計',tot); assert tot==254409
