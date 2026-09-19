# -*- coding: utf-8 -*-
"""9/17広告費を確定値で上書き（アカウント合計246,003と差0円。暫定245,128から+875円）"""
import csv
FINAL={'ナノガラス脱毛パッド':77346,'快適マジックインソール':32542,'W固定スマホ車載ホルダー':32037,
'伸縮ガラスクリーナー':26282,'高見えレザーヘッドレストフック':13176,'ムダ毛シェーバー':12676,
'カタログ全部（テスト）':12593,'もちふわ肉球サンダル':12329,'バランスケアスリッパ':9908,
'姿勢サポートチェア':9663,'電動温熱カッサ':7451}
assert sum(FINAL.values())==246003, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-17' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-17')
print('updated',n,'rows / 9/17合計',tot); assert tot==246003
