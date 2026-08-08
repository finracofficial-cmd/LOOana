# -*- coding: utf-8 -*-
"""4WAY: 今日(8/08 12:21)は本当に売れているのか。配信=Meta / 売上=Shopify(CSV+当日実測)"""
import csv, collections, datetime
M=[('2026-08-02',76045,17770,719),('2026-08-03',56209,14706,450),('2026-08-04',68806,15043,534),
   ('2026-08-05',58305,12825,425),('2026-08-06',46280,12234,381),('2026-08-07',35642,7840,253),
   ('2026-08-08',17690,4158,126)]
S=collections.defaultdict(lambda:[0,0])
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    if r['name']=='4WAY': S[r['date']][0]+=int(r['gross']); S[r['date']][1]+=int(r['disc'])
S['2026-08-08']=[34860,3237]   # 8/08 12:21時点のShopify実測（途中）
ORD={'2026-08-08':4}
WD=['月','火','水','木','金','土','日']
print('=== 4WAY 日次（8/08は12:21時点の途中） ===')
print(f"{'日付':11}{'曜':>3}{'広告':>8}{'CTR':>7}{'CPM':>7}{'CPC':>6}{'実売':>9}{'個':>4}{'MER':>6}{'個/CL':>7}{'売上/CL':>8}")
for d,c,i,cl in M:
    g=S[d][0]; s=g-S[d][1]; q=round(g/4980)
    print(f"{d:11}{WD[datetime.date(*map(int,d.split('-'))).weekday()]:>3}{c:>8,}{cl/i*100:>6.2f}%{c/i*1000:>7,.0f}{c/cl:>6,.0f}{s:>9,}{q:>4}{s/c:>6.2f}{q/cl*100:>6.2f}%{s/cl:>8,.0f}")
print()
A=[m for m in M if '2026-08-02'<=m[0]<='2026-08-07']
ac=sum(x[1] for x in A); ai=sum(x[2] for x in A); acl=sum(x[3] for x in A)
ag=sum(S[x[0]][0] for x in A); as_=ag-sum(S[x[0]][1] for x in A); aq=round(ag/4980)
c,i,cl=17690,4158,126; g=34860; s=g-3237; q=round(g/4980)
print('=== 8/02-07（6日平均） vs 8/08（12:21時点） ===')
print(f"{'':14}{'6日平均/日':>12}{'8/08 12:21':>12}{'進捗率':>9}")
for lbl,a6,t in [('広告費',ac/6,c),('クリック',acl/6,cl),('実売',as_/6,s),('販売数',aq/6,q)]:
    print(f"  {lbl:12}{a6:>12,.0f}{t:>12,.0f}{t/a6*100:>8.0f}%")
print(f"\n  → 広告費の進捗 {c/(ac/6)*100:.0f}% に対し、実売の進捗 {s/(as_/6)*100:.0f}%")
print(f"  MER: 6日平均 {as_/ac:.2f} → 8/08 {s/c:.2f}  （分岐1.59）")
print(f"  売上/クリック: 6日平均 {as_/acl:,.0f}円 → 8/08 {s/cl:,.0f}円  ({(s/cl)/(as_/acl)-1:+.0%})")
print(f"  個/クリック: 6日平均 {aq/acl*100:.2f}% → 8/08 {q/cl*100:.2f}%  ({(q/cl)/(aq/acl)-1:+.0%})")
print(f"  点数/注文: 7日平均 1.35 → 8/08 {q/4:.2f}  ({(q/4)/1.35-1:+.0%})")
print(f"\n  CTRは {acl/ai*100:.2f}% → {cl/i*100:.2f}% でほぼ横ばい（{(cl/i)/(acl/ai)-1:+.1%}）")
