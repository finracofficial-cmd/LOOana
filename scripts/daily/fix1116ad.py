# -*- coding: utf-8 -*-
"""11/16 広告費を確定値で上書き（暫定 184,018円 → 確定 185,255円）。11/18 00時台に data_query(fresh・1日ずつ) で再取得（scripts/daily/o1117/meta_camp_1116_1117_raw.txt）"""
import csv
D='2026-11-16'; TOT=185255
FINAL={}
for l in open('scripts/daily/o1117/meta_camp_1116_1117_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): FINAL[p[1]]=int(p[2])
assert sum(FINAL.values())==TOT, sum(FINAL.values())
rows=list(csv.reader(open('data/daily/daily_ad.csv')))
n=0
for r in rows:
    if r and r[0]==D:
        assert r[1] in FINAL, ('CSVにあって確定値にないキャンペーン', r)
        if int(r[2])!=FINAL[r[1]]: r[2]=str(FINAL[r[1]]); n+=1
keys=[r[1] for r in rows if r and r[0]==D]; assert sorted(keys)==sorted(FINAL), (sorted(keys), sorted(FINAL))
csv.writer(open('data/daily/daily_ad.csv','w',newline='')).writerows(rows)
tot=sum(int(r[2]) for r in rows if r and r[0]==D); assert tot==TOT, tot
print(D,'確定',tot,'updated rows',n)
