# -*- coding: utf-8 -*-
"""10/27広告費を確定値で上書き（暫定234,963円→確定）。10/30 00時台に data_query(fresh) で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':28965,'カタログ全部（テスト）':7882,'コードレスダブルミスト加湿器':8263,
'ナノガラス脱毛パッド':80420,'バランスケアスリッパ':89,'ポータブルヒートシーラー':14651,'伸縮ガラスクリーナー':33088,
'伸縮ワックス洗車ブラシ':14814,'快適マジックインソール':32388,'高見えレザーヘッドレストフック':7550,'4-in-1マルチクリーナー':7096}
TOT=sum(FINAL.values()); assert TOT==235206, TOT
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-27' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-27')
print('updated',n,'rows / 10/27合計',tot,'(暫定234,963)'); assert tot==TOT
