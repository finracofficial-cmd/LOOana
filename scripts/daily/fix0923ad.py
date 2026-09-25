# -*- coding: utf-8 -*-
"""9/23広告費を確定値で上書き（アカウント合計267,918と差0円。暫定267,788から+130円）"""
import csv
FINAL={'ナノガラス脱毛パッド':78893,'快適マジックインソール':39279,'W固定スマホ車載ホルダー':37325,
'伸縮ガラスクリーナー':32915,'高見えレザーヘッドレストフック':20698,'もちふわ肉球サンダル':10680,
'UV歯ブラシ除菌器':10475,'カタログ全部（テスト）':9963,'バランスケアスリッパ':9756,
'姿勢サポートチェア':9051,'携帯電動シェーバー':8883}
assert sum(FINAL.values())==267918, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-23' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-23')
print('updated',n,'rows / 9/23合計',tot); assert tot==267918
