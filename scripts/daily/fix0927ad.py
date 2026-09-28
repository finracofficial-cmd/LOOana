# -*- coding: utf-8 -*-
"""9/27広告費を確定値で上書き（アカウント合計301,322と差0円。暫定301,289から+33円）"""
import csv
FINAL={'UV歯ブラシ除菌器':12194,'W固定スマホ車載ホルダー':36114,'もちふわ肉球サンダル':12014,'カタログ全部（テスト）':10576,
'ナノガラス脱毛パッド':93001,'バランスケアスリッパ':11248,'伸縮ガラスクリーナー':36124,'姿勢サポートチェア':11219,
'快適マジックインソール':44160,'携帯電動シェーバー':10009,'電動眉シェーバー':2685,'高見えレザーヘッドレストフック':21978}
assert sum(FINAL.values())==301322, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-27' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-27')
print('updated',n,'rows / 9/27合計',tot); assert tot==301322
