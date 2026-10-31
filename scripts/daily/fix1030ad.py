# -*- coding: utf-8 -*-
"""10/30 広告費を確定値で上書き（暫定 205,429円 → 確定 205,839円）。11/01 00時台に data_query(fresh) で再取得"""
import csv
FINAL={'2026-10-30':{'W固定スマホ車載ホルダー':30043,'カタログ全部（テスト）':10012,'ナノガラス脱毛パッド':39197,'ポータブルヒートシーラー':14611,
  '伸縮ガラスクリーナー':37080,'伸縮ワックス洗車ブラシ':22320,'姿勢サポートチェア':13835,'快適マジックインソール':21665,
  '高見えレザーヘッドレストフック':8510,'4-in-1マルチクリーナー':8566}}
TOT={'2026-10-30':205839}
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
