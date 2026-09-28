# -*- coding: utf-8 -*-
"""9/24広告費を確定値で上書き（アカウント合計216,753と差0円。暫定216,715から+38円）"""
import csv
FINAL={'ナノガラス脱毛パッド':66832,'快適マジックインソール':31923,'伸縮ガラスクリーナー':27609,
'W固定スマホ車載ホルダー':26639,'高見えレザーヘッドレストフック':16592,'もちふわ肉球サンダル':9377,
'UV歯ブラシ除菌器':8280,'姿勢サポートチェア':7799,'バランスケアスリッパ':7681,
'カタログ全部（テスト）':7298,'携帯電動シェーバー':6723}
assert sum(FINAL.values())==216753, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-24' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-24')
print('updated',n,'rows / 9/24合計',tot); assert tot==216753
