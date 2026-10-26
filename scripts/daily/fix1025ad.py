# -*- coding: utf-8 -*-
"""10/25広告費を確定値で上書き（暫定303,851円→確定）。10/27 00時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':44906,'カタログ全部（テスト）':10367,'コードレスダブルミスト加湿器':9937,
'ナノガラス脱毛パッド':95555,'ナノバブルシャワーヘッド':9867,'ポータブルヒートシーラー':13632,'伸縮ガラスクリーナー':42933,
'伸縮ワックス洗車ブラシ':14515,'快適マジックインソール':35673,'高見えレザードアポケット':7224,'高見えレザーヘッドレストフック':11643,'4-in-1マルチクリーナー':8457}
TOT=sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-25' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-25')
print('updated',n,'rows / 10/25合計',tot,'(暫定303,851)'); assert tot==TOT
