# -*- coding: utf-8 -*-
"""10/8広告費を確定値で上書き（アカウント合計246,061と差0円。暫定245,136から+925円）"""
import csv
FINAL={'W固定スマホ車載ホルダー':32811,'カタログ全部（テスト）':9346,'ナノガラス脱毛パッド':77458,'ネックマッサージャー2':10853,
'バランスケアスリッパ':8725,'伸縮ガラスクリーナー':30190,'姿勢サポートチェア':8758,'快適マジックインソール':33187,
'携帯電動シェーバー':7573,'高見えレザーヘッドレストフック':20182,'4-in-1マルチクリーナー':6978}
assert sum(FINAL.values())==246061, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]=='2026-10-08' and r[1] in FINAL:
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]=='2026-10-08')
print('updated',n,'rows / 10/8合計',tot); assert tot==246061
