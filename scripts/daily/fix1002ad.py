# -*- coding: utf-8 -*-
"""10/2広告費を確定値で上書き（アカウント合計253,193と差0円。暫定252,736から+457円）"""
import csv
FINAL={'UV歯ブラシ除菌器':9627,'W固定スマホ車載ホルダー':32741,'もちふわ肉球サンダル':10287,'カタログ全部（テスト）':9053,
'ナノガラス脱毛パッド':75821,'バランスケアスリッパ':9131,'伸縮ガラスクリーナー':31755,'姿勢サポートチェア':8772,
'快適マジックインソール':37695,'携帯電動シェーバー':7863,'高見えレザーヘッドレストフック':20448}
assert sum(FINAL.values())==253193, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-02' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-02')
print('updated',n,'rows / 10/2合計',tot); assert tot==253193
