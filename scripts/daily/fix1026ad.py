# -*- coding: utf-8 -*-
"""10/26広告費を確定値で上書き（暫定257,498円→確定258,792円）。10/28 02時台に data_query で再取得"""
import csv
FINAL={'W固定スマホ車載ホルダー':32448,'カタログ全部（テスト）':8865,'コードレスダブルミスト加湿器':8271,
'ナノガラス脱毛パッド':79493,'ナノバブルシャワーヘッド':134,'バランスケアスリッパ':9746,'ポータブルヒートシーラー':16852,
'伸縮ガラスクリーナー':38302,'伸縮ワックス洗車ブラシ':18944,'快適マジックインソール':28785,'高見えレザーヘッドレストフック':8467,'4-in-1マルチクリーナー':8485}
TOT=sum(FINAL.values()); assert TOT==258792, TOT
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-26' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-26')
print('updated',n,'rows / 10/26合計',tot,'(暫定257,498)'); assert tot==TOT
