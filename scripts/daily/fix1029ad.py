# -*- coding: utf-8 -*-
"""10/28・10/29 広告費を確定値で上書き（暫定 10/28 232,675円・10/29 253,187円 → 確定）。10/31 01時台に data_query(fresh) で再取得"""
import csv
FINAL={'2026-10-28':{'W固定スマホ車載ホルダー':26179,'カタログ全部（テスト）':7813,'コードレスダブルミスト加湿器':268,'ナノガラス脱毛パッド':69874,
  'ポータブルヒートシーラー':13943,'伸縮ガラスクリーナー':34510,'伸縮ワックス洗車ブラシ':17105,'姿勢サポートチェア':14081,'快適マジックインソール':33986,
  '高見えレザーヘッドレストフック':7577,'4-in-1マルチクリーナー':7341},
 '2026-10-29':{'W固定スマホ車載ホルダー':30027,'カタログ全部（テスト）':9464,'ナノガラス脱毛パッド':78173,'ポータブルヒートシーラー':13445,
  '伸縮ガラスクリーナー':39073,'伸縮ワックス洗車ブラシ':20023,'姿勢サポートチェア':13454,'快適マジックインソール':29293,
  '高見えレザーヘッドレストフック':7744,'2WAYシートボックス':5687,'4-in-1マルチクリーナー':7334}}
TOT={'2026-10-28':232677,'2026-10-29':253717}
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
