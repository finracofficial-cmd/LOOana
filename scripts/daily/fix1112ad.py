# -*- coding: utf-8 -*-
"""11/12 広告費を確定値で上書き（暫定 183,140円 → 確定 183,496円）。11/14 00時台に data_query(fresh) で再取得（scripts/daily/o1113/meta_camp_1112_1113_raw.txt）"""
import csv
FINAL={'2026-11-12':{'UV歯ブラシ除菌器':5660,'W固定スマホ車載ホルダー':24209,'すき間収納シートポケット':4270,'カタログ全部（テスト）':9761,
  'クリアビューレインガードフィルム':7519,'コードレスダブルミスト加湿器':136,'ナノガラス脱毛パッド':17952,'バランスケアスリッパ':4287,
  'マグネットドアクッション':8699,'ワイド水切りワイパー':24696,'伸縮ガラスクリーナー':30782,'伸縮ワックス洗車ブラシ':13413,'快適マジックインソール':10233,
  '防風あったか裏起毛パンツ':8675,'高見えレザーヘッドレストフック':4716,'4-in-1マルチクリーナー':8488}}
TOT={'2026-11-12':183496}
RAW={}
for l in open('scripts/daily/o1113/meta_camp_1112_1113_raw.txt'):
    if l.startswith('2026-11-12,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-12'], '取得ファイルと一致しない'
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
