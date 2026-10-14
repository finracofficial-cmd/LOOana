# -*- coding: utf-8 -*-
"""10/13広告費を確定値で上書き（キャンペーン合算228,210円。暫定228,072から+138円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':29102,'カタログ全部（テスト）':8534,'ナノガラス脱毛パッド':74170,'バランスケアスリッパ':6107,
'ポータブルヒートシーラー':13489,'伸縮ガラスクリーナー':34751,'姿勢サポートチェア':8454,'快適マジックインソール':31934,
'携帯電動シェーバー':21,'高見えレザーヘッドレストフック':13381,'4-in-1マルチクリーナー':8267}
assert sum(FINAL.values())==228210, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-13' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-13')
print('updated',n,'rows / 10/13合計',tot); assert tot==228210
