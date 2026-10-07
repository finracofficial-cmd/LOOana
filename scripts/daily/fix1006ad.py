# -*- coding: utf-8 -*-
"""10/6広告費を確定値で上書き（アカウント合計275,691と差0円。暫定275,337から+354円）"""
import csv
FINAL={'UV歯ブラシ除菌器':9969,'W固定スマホ車載ホルダー':34063,'カタログ全部（テスト）':6616,
'ナノガラス脱毛パッド':86763,'ネックマッサージャー2':10190,'バランスケアスリッパ':9575,'伸縮ガラスクリーナー':34551,
'姿勢サポートチェア':9459,'快適マジックインソール':37263,'携帯電動シェーバー':7689,'高見えレザーヘッドレストフック':20792,
'4-in-1マルチクリーナー':8761}
assert sum(FINAL.values())==275691, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-06' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-06')
print('updated',n,'rows / 10/6合計',tot); assert tot==275691
