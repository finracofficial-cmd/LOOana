# -*- coding: utf-8 -*-
"""9/15広告費を確定値で上書き（アカウント合計235,596と差0円。暫定234,391から+1,205円）"""
import csv
FINAL={'ナノガラス脱毛パッド':77682,'W固定スマホ車載ホルダー':33078,'快適マジックインソール':29791,
'伸縮ガラスクリーナー':23010,'高見えレザーヘッドレストフック':15236,'バランスケアスリッパ':12170,
'カタログ全部（テスト）':12123,'ムダ毛シェーバー':11604,'もちふわ肉球サンダル':9270,
'姿勢サポートチェア':8046,'電動温熱カッサ':3586}
assert sum(FINAL.values())==235596, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-15' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-15')
print('updated',n,'rows / 9/15合計',tot); assert tot==235596
