# -*- coding: utf-8 -*-
"""11/08 広告費を確定値で上書き（暫定 240,848円 → 確定 241,135円）。11/10 00時台に data_query(fresh) で再取得（scripts/daily/o1109/meta_camp_1108_1109_raw.txt）"""
import csv
FINAL={'2026-11-08':{'W固定スマホ車載ホルダー':30266,
  'カタログ全部（テスト）':10383,
  'クリアビューレインガードフィルム':20496,
  'コードレスダブルミスト加湿器':12421,
  'シリコンホールド膝サポーター':2860,
  'ナノガラス脱毛パッド':21645,
  'ポータブルヒートシーラー':8836,
  'マグネットドアクッション':10274,
  'ワイド水切りワイパー':26277,
  '伸縮ガラスクリーナー':40350,
  '伸縮ワックス洗車ブラシ':22346,
  '姿勢サポートチェア':10687,
  '快適マジックインソール':12243,
  '4-in-1マルチクリーナー':12051}}
TOT={'2026-11-08':241135}
RAW={}
for l in open('scripts/daily/o1109/meta_camp_1108_1109_raw.txt'):
    if l.startswith('2026-11-08,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-08'], '取得ファイルと一致しない'
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
