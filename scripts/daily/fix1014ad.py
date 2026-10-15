# -*- coding: utf-8 -*-
"""10/14広告費を確定値で上書き（キャンペーン合算261,069円。暫定260,607から+462円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':34740,'むくみ取りかっさ':13597,'もちふわ肉球サンダル':5869,'カタログ全部（テスト）':8701,
'ナノガラス脱毛パッド':78283,'ナノバブルシャワーヘッド':3457,'バランスケアスリッパ':545,'ポータブルヒートシーラー':18223,
'伸縮ガラスクリーナー':37612,'姿勢サポートチェア':421,'快適マジックインソール':35080,'高見えレザーヘッドレストフック':14693,
'4-in-1マルチクリーナー':9848}
assert sum(FINAL.values())==261069, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-14' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-14')
print('updated',n,'rows / 10/14合計',tot); assert tot==261069
