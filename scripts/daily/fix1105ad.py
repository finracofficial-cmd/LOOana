# -*- coding: utf-8 -*-
"""11/05 広告費を確定値で上書き（暫定 203,228円 → 確定 203,877円）。11/07 02時台に data_query(fresh) で再取得（scripts/daily/o1106/meta_camp_1105_1106_raw.txt）"""
import csv
FINAL={'2026-11-05':{'W固定スマホ車載ホルダー':31546,
  'カタログ全部（テスト）':9673,
  'クリアビューレインガードフィルム':1144,
  'コードレスダブルミスト加湿器':17855,
  'コードレス毛玉クリーナー':231,
  'ナノガラス脱毛パッド':16643,
  'ナノバブルシャワーヘッド':4100,
  'ポータブルヒートシーラー':10384,
  'マグネットドアクッション':16654,
  'ワイド水切りワイパー':11310,
  '伸縮ガラスクリーナー':29941,
  '伸縮ワックス洗車ブラシ':25103,
  '姿勢サポートチェア':8991,
  '快適マジックインソール':11622,
  '4-in-1マルチクリーナー':8680}}
TOT={'2026-11-05':203877}
RAW={}
for l in open('scripts/daily/o1106/meta_camp_1105_1106_raw.txt'):
    if l.startswith('2026-11-05,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-05'], '取得ファイルと一致しない'
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
