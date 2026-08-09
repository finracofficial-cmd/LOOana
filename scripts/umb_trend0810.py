# -*- coding: utf-8 -*-
"""日傘2種の週次推移（最新週まで）。「やばいのか」を数字で。"""
import csv, collections
S=collections.defaultdict(lambda: collections.defaultdict(int)); G=collections.defaultdict(lambda: collections.defaultdict(int))
A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['name']][r['date']]+=int(r['gross'])-int(r['disc']); G[r['name']][r['date']]+=int(r['gross'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['campaign']][r['date']]+=float(r['cost'])
NG={'短(形状記憶)':('形状記憶日傘','形状記憶日傘'),'長(完全遮光)':('完全遮光・形状記憶','完全遮光・形状記憶・晴雨兼用・UV日傘')}
W=[('W-4 7/13-19',[f'2026-07-{d}' for d in range(13,20)]),('W-3 7/20-26',[f'2026-07-{d}' for d in range(20,27)]),
   ('W-2 7/27-8/02',[f'2026-07-{d}' for d in range(27,32)]+['2026-08-01','2026-08-02']),
   ('W-1 8/03-09',['2026-08-0%d'%d for d in range(3,10)])]
print('=== 日傘2種 週次推移（分岐1.37・売価4,980・原価1,309） ===')
for k,(sn,an) in NG.items():
    print(f"\n  【{k}】")
    print(f"    {'週':16}{'広告':>10}{'実売':>11}{'個':>5}{'MER':>6}{'余裕':>7}{'週利益':>11}{'1円利益':>8}")
    prev=None
    for lbl,ds in W:
        c=sum(A[an][d] for d in ds); s=sum(S[sn][d] for d in ds); q=round(sum(G[sn][d] for d in ds)/4980)
        if c==0: continue
        p=s-q*1309-c; mer=s/c; gm=1-q*1309/s
        ch=f'{mer/prev-1:+.1%}' if prev else '—'
        print(f"    {lbl:16}{c:>10,.0f}{s:>11,}{q:>5}{mer:>6.2f}{mer-1/gm:>+7.2f}{p:>11,.0f}{mer*gm-1:>+8.3f}   前週比 {ch}")
        prev=mer
print()
print('=== 2本合算 ===')
print(f"    {'週':16}{'広告':>10}{'実売':>11}{'MER':>6}{'週利益':>11}")
for lbl,ds in W:
    c=sum(A[an][d] for _,(sn,an) in NG.items() for d in ds)
    s=sum(S[sn][d] for _,(sn,an) in NG.items() for d in ds)
    q=round(sum(G[sn][d] for _,(sn,an) in NG.items() for d in ds)/4980)
    if c==0: continue
    print(f"    {lbl:16}{c:>10,.0f}{s:>11,}{s/c:>6.2f}{s-q*1309-c:>11,.0f}")
