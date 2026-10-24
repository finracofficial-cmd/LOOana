# -*- coding: utf-8 -*-
"""10/23広告費を確定値で上書き（暫定263,641円→確定）。10/25 00時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':36155,'カタログ全部（テスト）':8362,'コードレスダブルミスト加湿器':12926,'ディスペンサー':13266,
'ナノガラス脱毛パッド':78284,'ナノバブルシャワーヘッド':6828,'ポータブルヒートシーラー':11919,'伸縮ガラスクリーナー':35209,
'伸縮ワックス洗車ブラシ':4173,'快適マジックインソール':28815,'高見えレザードアポケット':10501,'高見えレザーヘッドレストフック':9646,'4-in-1マルチクリーナー':7757}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-23' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-23')
print('updated',n,'rows / 10/23合計',tot,'(暫定263,641)'); assert tot==TOT
