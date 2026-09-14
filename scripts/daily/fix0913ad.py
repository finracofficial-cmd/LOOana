# -*- coding: utf-8 -*-
"""9/13広告費を確定値で上書き（アカウント合計282,634と差0円。暫定281,588から+1,046円）"""
import csv
FINAL={'ナノガラス脱毛パッド':97385,'快適マジックインソール':40046,'W固定スマホ車載ホルダー':39319,
'伸縮ガラスクリーナー':30588,'カタログ全部（テスト）':17365,'バランスケアスリッパ':14090,
'ムダ毛シェーバー':14020,'姿勢サポートチェア':11565,'高見えレザーヘッドレストフック':10730,
'4-in-1マルチクリーナー':7405,'ナノバブルシャワーヘッド':121}
assert sum(FINAL.values())==282634, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-13' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-13')
print('updated',n,'rows / 9/13合計',tot); assert tot==282634
