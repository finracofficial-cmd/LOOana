# -*- coding: utf-8 -*-
"""10/16広告費を確定値で上書き（暫定235,731円→確定）"""
import csv
FINAL={'W固定スマホ車載ホルダー':35388,'むくみ取りかっさ':120,'カタログ全部（テスト）':8451,'ナノガラス脱毛パッド':79365,
'ナノバブルシャワーヘッド':7608,'ポータブルヒートシーラー':11110,'ロングニトリル家事手袋':4040,'伸縮ガラスクリーナー':37778,
'快適マジックインソール':33211,'高見えレザーヘッドレストフック':7700,'4-in-1マルチクリーナー':11699}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-16' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-16')
print('updated',n,'rows / 10/16合計',tot,'(暫定235,731)'); assert tot==TOT
