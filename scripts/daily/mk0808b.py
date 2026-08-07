# -*- coding: utf-8 -*-
"""日次利益系列・同曜日比較・非常ブレーキ判定・数量割引KPI"""
import pickle, csv, collections, datetime
R=pickle.load(open('/tmp/rep0808.pkl','rb'))
B='/home/user/LOOana/data/daily/'
COST=R['COST']; PRICE=R['PRICE']; MAP=R['MAP']
WD=['月','火','水','木','金','土','日']; wd=lambda d: WD[datetime.date(*map(int,d.split('-'))).weekday()]
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(float)
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')): AD[r['date']]+=float(r['cost'])
days=sorted({d for v in S.values() for d in v})
VARC={'ナノガラス脱毛パッド':(757,740)}
NANO_MIX=749.0   # 30日実測の加重平均原価（794×757+339×740）/1133
prof={}
for d in days:
    s=c=0
    for n,v in S.items():
        if n=='' or d not in v: continue
        g,dc=v[d]; s+=g-dc
        if g==0: continue
        if n=='ナノガラス脱毛パッド': c+=round(g/3980)*NANO_MIX
        elif n in PRICE and n in COST: c+=round(g/PRICE[n])*COST[n]
    prof[d]=s-c-AD[d]
last=days[-14:]
print('=== 日次（実売−原価−広告。ナノガラスの原価は30日加重平均749円で近似=概算） ===')
print(f"{'日付':12}{'曜':>3}{'実売':>12}{'広告':>11}{'利益':>11}{'3日MA':>11}")
for i,d in enumerate(days):
    if d not in last: continue
    j=days.index(d); ma=sum(prof[x] for x in days[j-2:j+1])/3 if j>=2 else None
    st=sum(v[d][0]-v[d][1] for v in S.values() if d in v)
    print(f"{d:12}{wd(d):>3}{st:>12,.0f}{AD[d]:>11,.0f}{prof[d]:>11,.0f}{(f'{ma:,.0f}' if ma else '—'):>11}")
print()
th=[d for d in days if wd(d)=='木']
print('=== 木曜の推移 ===')
for d in th[-5:]:
    st=sum(v[d][0]-v[d][1] for v in S.values() if d in v)
    print(f"  {d} 実売 {st:>10,.0f}  広告 {AD[d]:>9,.0f}  利益 {prof[d]:>9,.0f}")
prev=[d for d in th[-5:-1]]
pa=sum(sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in prev)/len(prev)
cur=sum(v['2026-08-07'][0]-v['2026-08-07'][1] for v in S.values() if '2026-08-07' in v)
print(f"  直近4木曜平均 {pa:,.0f} → 8/06 {cur:,.0f} ({cur/pa-1:+.1%})")
print()
j=days.index('2026-08-07'); ma3=sum(prof[x] for x in days[j-2:j+1])/3
print(f"=== 非常ブレーキ（3日移動平均利益 < 130,000 で発動） ===\n  8/04-06 の3日MA = {ma3:,.0f} → {'🚨 発動' if ma3<130000 else '✅ 未発動'}")
print(f"=== 利益額の目標（最低100,000 / 目標180,000） ===\n  8/06 利益 {prof['2026-08-07']:,.0f}（手数料控除後 {prof['2026-08-07']-cur*0.03452:,.0f}）")
