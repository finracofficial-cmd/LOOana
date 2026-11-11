# -*- coding: utf-8 -*-
"""11/10 広告費を確定値で上書き（暫定 165,063円 → 確定 165,869円）。11/12 00時台に data_query(fresh) で再取得（scripts/daily/o1111/meta_camp_1110_1111_raw.txt）"""
import csv
FINAL={'2026-11-10':{'W固定スマホ車載ホルダー':21870,
  'アーチフィット逆ヒールサンダル':3879,
  'カタログ全部（テスト）':7923,
  'クリアビューレインガードフィルム':18491,
  'ナノガラス脱毛パッド':13120,
  'ポータブルヒートシーラー':7,
  'マグネットドアクッション':6746,
  'ワイド水切りワイパー':27393,
  '伸縮ガラスクリーナー':24555,
  '伸縮ワックス洗車ブラシ':15622,
  '姿勢サポートチェア':7938,
  '快適マジックインソール':8450,
  '4-in-1マルチクリーナー':9875}}
TOT={'2026-11-10':165869}
RAW={}
for l in open('scripts/daily/o1111/meta_camp_1110_1111_raw.txt'):
    if l.startswith('2026-11-10,'):
        p=l.strip().split(',')
        if int(p[2]): RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-10'], '取得ファイルと一致しない'
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
