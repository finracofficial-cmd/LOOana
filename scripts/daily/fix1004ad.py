# -*- coding: utf-8 -*-
"""10/4広告費を確定値で上書き（アカウント合計294,000と差0円。暫定292,833から+1,167円）"""
import csv
FINAL={'UV歯ブラシ除菌器':11453,'W固定スマホ車載ホルダー':32819,'もちふわ肉球サンダル':11222,'カタログ全部（テスト）':10658,
'ナノガラス脱毛パッド':93447,'ネックマッサージャー2':10440,'バランスケアスリッパ':9879,'伸縮ガラスクリーナー':30694,
'姿勢サポートチェア':9898,'快適マジックインソール':40920,'携帯電動シェーバー':8972,'高見えレザーヘッドレストフック':19862,
'4-in-1マルチクリーナー':3736}
assert sum(FINAL.values())==294000, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-04' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-04')
print('updated',n,'rows / 10/4合計',tot); assert tot==294000
