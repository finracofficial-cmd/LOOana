# -*- coding: utf-8 -*-
"""9/20広告費を確定値で上書き（アカウント合計274,436と差0円。暫定273,661から+775円）"""
import csv
FINAL={'ナノガラス脱毛パッド':90593,'快適マジックインソール':35651,'W固定スマホ車載ホルダー':34695,
'伸縮ガラスクリーナー':28283,'高見えレザーヘッドレストフック':18061,'もちふわ肉球サンダル':16859,
'姿勢サポートチェア':11050,'バランスケアスリッパ':10505,'カタログ全部（テスト）':10381,
'UV歯ブラシ除菌器':9903,'携帯電動シェーバー':8455}
assert sum(FINAL.values())==274436, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-20' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-20')
print('updated',n,'rows / 9/20合計',tot); assert tot==274436
