# -*- coding: utf-8 -*-
"""10/22広告費を確定値で上書き（暫定274,766円→確定）。10/24 03時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':40269,'カタログ全部（テスト）':8894,'コードレスダブルミスト加湿器':11092,'ディスペンサー':9609,
'ナノガラス脱毛パッド':82896,'ナノバブルシャワーヘッド':8492,'ポータブルヒートシーラー':13220,'伸縮ガラスクリーナー':43417,
'快適マジックインソール':35552,'高見えレザードアポケット':4373,'高見えレザーヘッドレストフック':9824,'4-in-1マルチクリーナー':8120}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-22' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-22')
print('updated',n,'rows / 10/22合計',tot,'(暫定274,766)'); assert tot==TOT
