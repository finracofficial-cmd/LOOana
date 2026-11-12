# -*- coding: utf-8 -*-
"""11/11 広告費を確定値で上書き（暫定 189,643円 → 確定 190,465円）。11/13 01時台に data_query(fresh) で再取得（scripts/daily/o1112/meta_camp_1111_1112_raw.txt）"""
import csv
FINAL={'2026-11-11':{'W固定スマホ車載ホルダー':22796,'すき間収納シートポケット':641,'アーチフィット逆ヒールサンダル':34,'カタログ全部（テスト）':9133,
  'クリアビューレインガードフィルム':17179,'コードレスダブルミスト加湿器':3650,'ナノガラス脱毛パッド':14575,'マグネットドアクッション':11651,
  'ワイド水切りワイパー':25998,'伸縮ガラスクリーナー':29969,'伸縮ワックス洗車ブラシ':15392,'姿勢サポートチェア':6999,'快適マジックインソール':10343,
  '防風あったか裏起毛パンツ':3310,'高見えレザーヘッドレストフック':2856,'2WAYシートボックス':4876,'4-in-1マルチクリーナー':11063}}
TOT={'2026-11-11':190465}
RAW={}
for l in open('scripts/daily/o1112/meta_camp_1111_1112_raw.txt'):
    if l.startswith('2026-11-11,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-11'], '取得ファイルと一致しない'
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
