# -*- coding: utf-8 -*-
"""9/19広告費を確定値で上書き（アカウント合計244,503と差0円。暫定244,432から+71円）"""
import csv
FINAL={'ナノガラス脱毛パッド':81325,'W固定スマホ車載ホルダー':31758,'快適マジックインソール':29275,
'伸縮ガラスクリーナー':27664,'UV歯ブラシ除菌器':16874,'高見えレザーヘッドレストフック':14643,
'もちふわ肉球サンダル':12462,'バランスケアスリッパ':8038,'カタログ全部（テスト）':7899,
'姿勢サポートチェア':7519,'携帯電動シェーバー':7046}
assert sum(FINAL.values())==244503, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-19' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-19')
print('updated',n,'rows / 9/19合計',tot); assert tot==244503
