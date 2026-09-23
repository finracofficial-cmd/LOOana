# -*- coding: utf-8 -*-
"""9/22広告費を確定値で上書き（アカウント合計240,589と差0円。暫定240,094から+495円）"""
import csv
FINAL={'ナノガラス脱毛パッド':73990,'伸縮ガラスクリーナー':34509,'快適マジックインソール':32499,
'W固定スマホ車載ホルダー':29286,'高見えレザーヘッドレストフック':18918,'カタログ全部（テスト）':9143,
'UV歯ブラシ除菌器':9041,'姿勢サポートチェア':8742,'もちふわ肉球サンダル':8433,
'バランスケアスリッパ':8208,'携帯電動シェーバー':7820}
assert sum(FINAL.values())==240589, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-22' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-22')
print('updated',n,'rows / 9/22合計',tot); assert tot==240589
