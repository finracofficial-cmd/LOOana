# -*- coding: utf-8 -*-
"""10/5広告費を確定値で上書き（アカウント合計225,927と差0円。暫定225,565から+362円）"""
import csv
FINAL={'UV歯ブラシ除菌器':8813,'W固定スマホ車載ホルダー':29423,'もちふわ肉球サンダル':17,'カタログ全部（テスト）':7308,
'ナノガラス脱毛パッド':65462,'ネックマッサージャー2':8067,'バランスケアスリッパ':7509,'伸縮ガラスクリーナー':27601,
'姿勢サポートチェア':7982,'快適マジックインソール':28500,'携帯電動シェーバー':6952,'高見えレザーヘッドレストフック':18575,
'4-in-1マルチクリーナー':9718}
assert sum(FINAL.values())==225927, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-05' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-05')
print('updated',n,'rows / 10/5合計',tot); assert tot==225927
