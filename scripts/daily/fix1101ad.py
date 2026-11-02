# -*- coding: utf-8 -*-
"""11/01 広告費を確定値で上書き（暫定 229,776円 → 確定 230,113円）。11/03 00時台に data_query(fresh) で再取得"""
import csv
FINAL={'2026-11-01':{'W固定スマホ車載ホルダー':33576,'ふわとろ高密度ブランケット':8528,'カタログ全部（テスト）':9630,'ナノガラス脱毛パッド':26281,
  'ポータブルヒートシーラー':16033,'マグネットドアクッション':16487,'伸縮ガラスクリーナー':40563,'伸縮ワックス洗車ブラシ':26305,
  '姿勢サポートチェア':10053,'快適マジックインソール':22841,'高見えレザーヘッドレストフック':12163,'4-in-1マルチクリーナー':7653}}
TOT={'2026-11-01':230113}
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
