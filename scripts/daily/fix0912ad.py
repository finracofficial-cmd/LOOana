# -*- coding: utf-8 -*-
"""9/12広告費を確定値で上書き（adset合算・アカウント合計219,731と差0円）"""
import csv
FINAL={'ナノガラス脱毛パッド':61389+16305,'W固定スマホ車載ホルダー':30870,'快適マジックインソール':27819,
'伸縮ガラスクリーナー':17093,'ムダ毛シェーバー':11189,'カタログ全部（テスト）':10881,
'バランスケアスリッパ':10076,'高見えレザーヘッドレストフック':9375,'ナノバブルシャワーヘッド':9113,
'4-in-1マルチクリーナー':8590,'姿勢サポートチェア':7031}
assert sum(FINAL.values())==219731, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-09-12' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-09-12')
print('updated',n,'rows / 9/12合計',tot); assert tot==219731
