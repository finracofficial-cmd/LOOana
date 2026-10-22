# -*- coding: utf-8 -*-
"""10/21広告費を確定値で上書き（暫定243,145円→確定）。10/23 00時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':36062,'カタログ全部（テスト）':9828,'コードレスダブルミスト加湿器':8749,'ディスペンサー':8360,
'ナノガラス脱毛パッド':77847,'ナノバブルシャワーヘッド':7378,'ポータブルヒートシーラー':11223,'伸縮ガラスクリーナー':34239,
'快適マジックインソール':32098,'高見えレザーヘッドレストフック':9941,'4-in-1マルチクリーナー':7514}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-21' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-21')
print('updated',n,'rows / 10/21合計',tot,'(暫定243,145)'); assert tot==TOT
