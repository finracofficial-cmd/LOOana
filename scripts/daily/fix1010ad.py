# -*- coding: utf-8 -*-
"""10/10広告費を確定値で上書き（キャンペーン合算261,251円。暫定261,209から+42円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':41186,'カタログ全部（テスト）':10257,'ナノガラス脱毛パッド':78218,'ネックマッサージャー2':10212,
'バランスケアスリッパ':6961,'伸縮ガラスクリーナー':37918,'姿勢サポートチェア':9187,'快適マジックインソール':38856,
'携帯電動シェーバー':5768,'高見えレザーヘッドレストフック':14413,'4-in-1マルチクリーナー':8275}
assert sum(FINAL.values())==261251, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-10' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-10')
print('updated',n,'rows / 10/10合計',tot); assert tot==261251
