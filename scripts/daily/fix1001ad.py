# -*- coding: utf-8 -*-
"""10/1広告費を確定値で上書き（アカウント合計294,082と差0円。暫定292,810から+1,272円）"""
import csv
FINAL={'UV歯ブラシ除菌器':10699,'W固定スマホ車載ホルダー':38331,'もちふわ肉球サンダル':11289,'カタログ全部（テスト）':9895,
'ナノガラス脱毛パッド':95507,'バランスケアスリッパ':10104,'伸縮ガラスクリーナー':37949,'姿勢サポートチェア':9360,
'快適マジックインソール':39164,'携帯電動シェーバー':6933,'電動眉シェーバー':1683,'高見えレザーヘッドレストフック':23168}
assert sum(FINAL.values())==294082, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-01' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-01')
print('updated',n,'rows / 10/1合計',tot); assert tot==294082
