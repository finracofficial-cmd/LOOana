# -*- coding: utf-8 -*-
"""10/18広告費を確定値で上書き（暫定263,325円→確定）"""
import csv
FINAL={'W固定スマホ車載ホルダー':35786,'カタログ全部（テスト）':10400,'ディスペンサー':6514,'ナノガラス脱毛パッド':89124,
'ナノバブルシャワーヘッド':10238,'ポータブルヒートシーラー':11306,'伸縮ガラスクリーナー':38121,
'快適マジックインソール':41338,'高見えレザーヘッドレストフック':8095,'4-in-1マルチクリーナー':12431}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-18' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-18')
print('updated',n,'rows / 10/18合計',tot,'(暫定263,325)'); assert tot==TOT
