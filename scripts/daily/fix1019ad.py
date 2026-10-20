# -*- coding: utf-8 -*-
"""10/19広告費を確定値で上書き（暫定231,938円→確定232,120円）。10/21 00時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':36279,'カタログ全部（テスト）':8604,'ディスペンサー':6615,'ナノガラス脱毛パッド':74886,
'ナノバブルシャワーヘッド':8126,'ポータブルヒートシーラー':11032,'伸縮ガラスクリーナー':36986,
'快適マジックインソール':32651,'高見えレザーヘッドレストフック':7652,'4-in-1マルチクリーナー':9289}
TOT=sum(FINAL.values()); assert TOT==232120, TOT
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-19' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-19')
print('updated',n,'rows / 10/19合計',tot,'(暫定231,938)'); assert tot==TOT
