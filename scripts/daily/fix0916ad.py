# -*- coding: utf-8 -*-
"""9/16広告費を確定値で上書き（アカウント合計246,575と差0円。暫定246,202から+373円）"""
import csv
FINAL={'ナノガラス脱毛パッド':77054,'快適マジックインソール':33110,'W固定スマホ車載ホルダー':32178,
'伸縮ガラスクリーナー':25804,'高見えレザーヘッドレストフック':16533,'カタログ全部（テスト）':14136,
'ムダ毛シェーバー':11449,'バランスケアスリッパ':10711,'電動温熱カッサ':9062,
'もちふわ肉球サンダル':8322,'姿勢サポートチェア':8216}
assert sum(FINAL.values())==246575, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-16' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-16')
print('updated',n,'rows / 9/16合計',tot); assert tot==246575
