# -*- coding: utf-8 -*-
"""10/20広告費を確定値で上書き（暫定247,707円→確定）。10/22 10時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':38729,'カタログ全部（テスト）':8523,'コードレスダブルミスト加湿器':4046,'ディスペンサー':8243,
'ナノガラス脱毛パッド':77608,'ナノバブルシャワーヘッド':7987,'ポータブルヒートシーラー':11412,'伸縮ガラスクリーナー':36598,
'快適マジックインソール':36266,'高見えレザーヘッドレストフック':10176,'4-in-1マルチクリーナー':8928}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-20' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-20')
print('updated',n,'rows / 10/20合計',tot,'(暫定247,707)'); assert tot==TOT
