# -*- coding: utf-8 -*-
"""11/03 広告費を確定値で上書き（暫定 212,514円 → 確定 212,735円）。11/05 00時台に data_query(fresh) で再取得（scripts/daily/o1104/meta_camp_1103_1104_raw.txt）"""
import csv
FINAL={'2026-11-03':{'W固定スマホ車載ホルダー':30792,'カタログ全部（テスト）':9728,'コードレスダブルミスト加湿器':815,'コードレス毛玉クリーナー':3783,
  'ナノガラス脱毛パッド':24532,'ファスナー修理キット':4481,'ポータブルヒートシーラー':12909,'マグネットドアクッション':22182,
  '伸縮ガラスクリーナー':40010,'伸縮ワックス洗車ブラシ':20938,'姿勢サポートチェア':9740,'快適マジックインソール':15322,
  '高見えレザーヘッドレストフック':6806,'4-in-1マルチクリーナー':10697}}
TOT={'2026-11-03':212735}
RAW={}
for l in open('scripts/daily/o1104/meta_camp_1103_1104_raw.txt'):
    if l.startswith('2026-11-03,'): p=l.strip().split(','); RAW[p[1]]=int(p[2])
assert RAW==FINAL['2026-11-03'], '取得ファイルと一致しない'
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
