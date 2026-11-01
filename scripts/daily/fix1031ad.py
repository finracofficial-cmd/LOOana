# -*- coding: utf-8 -*-
"""10/31 広告費を確定値で上書き（暫定 203,474円 → 確定 203,524円）。11/02 04時台に data_query(fresh) で再取得"""
import csv
FINAL={'2026-10-31':{'W固定スマホ車載ホルダー':32098,'ふわとろ高密度ブランケット':1838,'カタログ全部（テスト）':8544,'ナノガラス脱毛パッド':26058,
  'ポータブルヒートシーラー':16133,'マグネットドアクッション':3844,'伸縮ガラスクリーナー':36892,'伸縮ワックス洗車ブラシ':23251,'健康サンダル':5033,
  '姿勢サポートチェア':15513,'快適マジックインソール':17530,'高見えレザーヘッドレストフック':8111,'4-in-1マルチクリーナー':8679}}
TOT={'2026-10-31':203524}
for d,v in FINAL.items(): assert sum(v.values())==TOT[d],(d,sum(v.values()))
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0] in FINAL:
        assert r[1] in FINAL[r[0]], ('CSVにあって確定値にないキャンペーン', r)
        if int(r[2])!=FINAL[r[0]][r[1]]: r[2]=str(FINAL[r[0]][r[1]]); n+=1
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
for d in FINAL:
    keys=[r[1] for r in rows if r and r[0]==d]; assert sorted(keys)==sorted(FINAL[d]), d
    tot=sum(int(r[2]) for r in rows if r and r[0]==d); assert tot==TOT[d], (d,tot)
    print(d,'確定',tot)
print('updated rows',n)
