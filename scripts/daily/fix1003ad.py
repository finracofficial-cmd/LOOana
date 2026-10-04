# -*- coding: utf-8 -*-
"""10/3広告費を確定値で上書き（アカウント合計233,636と差0円。暫定233,284から+352円）"""
import csv
FINAL={'UV歯ブラシ除菌器':8300,'W固定スマホ車載ホルダー':29143,'もちふわ肉球サンダル':9290,'カタログ全部（テスト）':7083,
'ナノガラス脱毛パッド':72297,'ネックマッサージャー2':3802,'バランスケアスリッパ':8409,'伸縮ガラスクリーナー':31207,
'姿勢サポートチェア':8468,'快適マジックインソール':31207,'携帯電動シェーバー':6507,'高見えレザーヘッドレストフック':17923}
assert sum(FINAL.values())==233636, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-03' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-03')
print('updated',n,'rows / 10/3合計',tot); assert tot==233636
