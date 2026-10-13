# -*- coding: utf-8 -*-
"""10/12広告費を確定値で上書き（キャンペーン合算273,820円。暫定272,708から+1,112円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':33506,'カタログ全部（テスト）':10955,'ナノガラス脱毛パッド':95088,'ネックマッサージャー2':1116,
'バランスケアスリッパ':8195,'ポータブルヒートシーラー':2569,'伸縮ガラスクリーナー':39454,'姿勢サポートチェア':9684,
'快適マジックインソール':40124,'携帯電動シェーバー':6950,'高見えレザーヘッドレストフック':16418,'4-in-1マルチクリーナー':9761}
assert sum(FINAL.values())==273820, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-12' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-12')
print('updated',n,'rows / 10/12合計',tot); assert tot==273820
