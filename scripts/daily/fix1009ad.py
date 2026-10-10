# -*- coding: utf-8 -*-
"""10/9広告費を確定値で上書き（キャンペーン合算249,934と差0円。暫定249,096から+838円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':33978,'カタログ全部（テスト）':8749,'ナノガラス脱毛パッド':73054,'ネックマッサージャー2':8985,
'バランスケアスリッパ':8929,'伸縮ガラスクリーナー':39258,'姿勢サポートチェア':8843,'快適マジックインソール':35578,
'携帯電動シェーバー':7680,'高見えレザーヘッドレストフック':18481,'4-in-1マルチクリーナー':6399}
assert sum(FINAL.values())==249934, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-09' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-09')
print('updated',n,'rows / 10/9合計',tot); assert tot==249934
