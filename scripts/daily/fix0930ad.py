# -*- coding: utf-8 -*-
"""9/30広告費を確定値で上書き（アカウント合計250,963と差0円。暫定250,891から+72円）"""
import csv
FINAL={'UV歯ブラシ除菌器':10236,'W固定スマホ車載ホルダー':32708,'もちふわ肉球サンダル':8649,'カタログ全部（テスト）':8388,
'ナノガラス脱毛パッド':74964,'バランスケアスリッパ':7968,'伸縮ガラスクリーナー':30792,'姿勢サポートチェア':8740,
'快適マジックインソール':33379,'携帯電動シェーバー':8668,'電動眉シェーバー':7036,'高見えレザーヘッドレストフック':19435}
assert sum(FINAL.values())==250963, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-30' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-30')
print('updated',n,'rows / 9/30合計',tot); assert tot==250963
