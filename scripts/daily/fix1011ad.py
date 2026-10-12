# -*- coding: utf-8 -*-
"""10/11広告費を確定値で上書き（キャンペーン合算260,530円。暫定260,383から+147円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':31180,'カタログ全部（テスト）':10247,'ナノガラス脱毛パッド':81053,'ネックマッサージャー2':11747,
'バランスケアスリッパ':7862,'伸縮ガラスクリーナー':38225,'姿勢サポートチェア':10168,'快適マジックインソール':36504,
'携帯電動シェーバー':7228,'高見えレザーヘッドレストフック':17476,'4-in-1マルチクリーナー':8840}
assert sum(FINAL.values())==260530, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-11' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-11')
print('updated',n,'rows / 10/11合計',tot); assert tot==260530
