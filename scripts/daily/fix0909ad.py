# -*- coding: utf-8 -*-
"""9/9広告費を確定値で上書き（adset合算・アカウント合計240,454と差0円）"""
import csv
FINAL={'ナノガラス脱毛パッド':55964+16118,'W固定スマホ車載ホルダー':31399,'快適マジックインソール':26922,
'ムダ毛シェーバー':16565,'カタログ全部（テスト）':15754,'伸縮ガラスクリーナー':14470,
'バランスケアスリッパ':14485,'ナノバブルシャワーヘッド':11372,'4-in-1マルチクリーナー':10280,
'姿勢サポートチェア':8601,'むくみ取りかっさ':7167,'2WAYシートボックス':7306,
'高見えレザーヘッドレストフック':3933,'温感EMSフェイシャルワンド':118}
assert sum(FINAL.values())==240454, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-09' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-09')
print('updated',n,'rows / 9/9合計',tot); assert tot==240454
