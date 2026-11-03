# -*- coding: utf-8 -*-
"""11/02 広告費を確定値で上書き（暫定 216,088円 → 確定 216,365円）。11/04 06時台に data_query(fresh) で再取得"""
import csv
FINAL={'2026-11-02':{'W固定スマホ車載ホルダー':30321,'カタログ全部（テスト）':9709,'ナノガラス脱毛パッド':24703,'ポータブルヒートシーラー':16723,
  'マグネットドアクッション':20789,'伸縮ガラスクリーナー':39535,'伸縮ワックス洗車ブラシ':22258,'姿勢サポートチェア':9306,
  '快適マジックインソール':21235,'高見えレザーヘッドレストフック':12665,'4-in-1マルチクリーナー':9121}}
TOT={'2026-11-02':216365}
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
