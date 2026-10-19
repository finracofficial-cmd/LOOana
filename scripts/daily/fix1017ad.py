# -*- coding: utf-8 -*-
"""10/17広告費を確定値で上書き（暫定237,446円→確定）"""
import csv
FINAL={'W固定スマホ車載ホルダー':39329,'カタログ全部（テスト）':7675,'ディスペンサー':3530,'ナノガラス脱毛パッド':77573,
'ナノバブルシャワーヘッド':9339,'ポータブルヒートシーラー':11963,'ロングニトリル家事手袋':326,'伸縮ガラスクリーナー':38363,
'快適マジックインソール':32264,'高見えレザーヘッドレストフック':7984,'4-in-1マルチクリーナー':9829}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-17' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-17')
print('updated',n,'rows / 10/17合計',tot,'(暫定237,446)'); assert tot==TOT
