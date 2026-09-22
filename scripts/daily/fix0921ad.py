# -*- coding: utf-8 -*-
"""9/21広告費を確定値で上書き（アカウント合計279,349と差0円。暫定279,264から+85円）"""
import csv
FINAL={'ナノガラス脱毛パッド':87533,'快適マジックインソール':37360,'W固定スマホ車載ホルダー':36343,
'伸縮ガラスクリーナー':34358,'高見えレザーヘッドレストフック':23783,'UV歯ブラシ除菌器':12215,
'もちふわ肉球サンダル':11155,'カタログ全部（テスト）':9711,'姿勢サポートチェア':9514,
'バランスケアスリッパ':9352,'携帯電動シェーバー':8025}
assert sum(FINAL.values())==279349, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-21' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-21')
print('updated',n,'rows / 9/21合計',tot); assert tot==279349
