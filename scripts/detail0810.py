# -*- coding: utf-8 -*-
"""①減額候補の日次トリガー検証 ②数量割引の測定状況"""
import csv, collections, datetime, pickle
R=pickle.load(open('/tmp/rep0810.pkl','rb'))
S=collections.defaultdict(lambda: collections.defaultdict(int)); G=collections.defaultdict(lambda: collections.defaultdict(int))
A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['name']][r['date']]+=int(r['gross'])-int(r['disc']); G[r['name']][r['date']]+=int(r['gross'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['campaign']][r['date']]+=float(r['cost'])
MAP=R['MAP']; PRICE=R['PRICE']; COST=R['COST']
WD=['月','火','水','木','金','土','日']
CAND=[('瞬間冷感ポンチョ',1.37),('携帯電動シェーバー',1.54),('4WAY',1.58),('完全遮光・形状記憶',1.37),('接触冷感UVアームカバー',1.25)]
print('=== ① 減額候補の日次トリガー検証（MER<分岐が3日連続→即−25%） ===')
for n,be in CAND:
    an=MAP.get(n,n); run=0; hist=[]
    for d in sorted(S[n]):
        if d<'2026-08-03': continue
        ad=A[an][d]; s=S[n][d]
        if ad<500: hist.append((d,None,None)); continue
        m=s/ad; q=round(G[n][d]/PRICE[n]); p=s-q*COST[n]-ad
        run = run+1 if m<be else 0
        hist.append((d,m,p))
    print(f"\n  【{n}】分岐 {be}  7日利益 {R['N7'][n]-R['K7'][n]-R['A7'].get(n,0):+,.0f}円")
    print('   ' + '  '.join(f"{d[5:]}({WD[datetime.date(*map(int,d.split('-'))).weekday()]}) {('—' if m is None else f'{m:.2f}')}{'▼' if m and m<be else ''}" for d,m,p in hist))
    print(f"   → MER<分岐の連続日数: {run}日 → {'🚨 該当（即−25%）' if run>=3 else '未該当'}")
print()
print('=== ② 数量割引: 点数/注文の日次（コピー掲載は8/07朝） ===')
ORD={'2026-08-01':232,'2026-08-02':267,'2026-08-03':187,'2026-08-04':188,'2026-08-05':152,
     '2026-08-06':157,'2026-08-07':168,'2026-08-08':184,'2026-08-09':None}
print(f"{'日付':12}{'曜':>3}{'商品点数':>9}{'全店注文':>9}{'点数/注文':>10}")
for d in sorted(ORD):
    q=0
    for n,v in G.items():
        if n=='優先配送' or d not in v or v[d]==0: continue
        if n in PRICE: q+=round(v[d]/PRICE[n])
    o=ORD[d]
    print(f"{d:12}{WD[datetime.date(*map(int,d.split('-'))).weekday()]:>3}{q:>9}{(o if o else '—'):>9}{(f'{q/o:.3f}' if o else '—'):>10}")
print("\n  掲載前(8/01-06)平均 と 掲載後(8/07-08)平均 を比較する。8/09の注文数は要取得")
