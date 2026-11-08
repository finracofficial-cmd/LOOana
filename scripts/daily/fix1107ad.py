# -*- coding: utf-8 -*-
"""11/07 広告費を確定値で上書き（暫定 198,195円 → 確定 198,251円）。11/09 03時台に data_query(fresh) で再取得（scripts/daily/o1108/meta_camp_1107_1108_raw.txt）"""
import csv
FINAL={'2026-11-07':{'W固定スマホ車載ホルダー':26051,
  'カタログ全部（テスト）':8044,
  'クリアビューレインガードフィルム':11043,
  'コードレスダブルミスト加湿器':15406,
  'ナノガラス脱毛パッド':17151,
  'ポータブルヒートシーラー':8167,
  'マグネットドアクッション':14367,
  'ワイド水切りワイパー':18996,
  '伸縮ガラスクリーナー':33684,
  '伸縮ワックス洗車ブラシ':17404,
  '姿勢サポートチェア':8299,
  '快適マジックインソール':9056,
  '4-in-1マルチクリーナー':10583}}
TOT={'2026-11-07':198251}
RAW={}
for l in open('scripts/daily/o1108/meta_camp_1107_1108_raw.txt'):
    if l.startswith('2026-11-07,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-07'], '取得ファイルと一致しない'
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
