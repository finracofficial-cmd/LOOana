# -*- coding: utf-8 -*-
import pickle,csv,collections,datetime,statistics
R=pickle.load(open('/tmp/rep0812.pkl','rb')); FEE=0.03452
S=collections.defaultdict(float); A=collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['date']]+=float(r['gross'])-float(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['date']]+=float(r['cost'])
HOL={'2026-07-20','2026-08-11'}
tue=[d for d in S if d>='2026-07-13' and d<'2026-08-11' and datetime.date.fromisoformat(d).weekday()==1 and d not in HOL]
print(f"■ 8/11(火・山の日) 実売 {S['2026-08-11']:,.0f}円")
print(f"  平常火曜平均（{', '.join(tue)}）= {statistics.mean(S[d] for d in tue):,.0f}円 → 対同曜日 {S['2026-08-11']/statistics.mean(S[d] for d in tue)*100:.1f}%")
print(f"  祝日 7/20(海の日) 1,572,336円 → 対祝日 {S['2026-08-11']/1572336*100:.1f}%")
print(f"  直近7日平均/日 {sum(R['N7'].values())/7:,.0f}円 → {S['2026-08-11']/(sum(R['N7'].values())/7)*100:.1f}%")
print("\n■ 日次利益（近似原価）と3日移動平均")
COST=dict(R['COST']); PRICE=dict(R['PRICE'])
COST['ナノガラス脱毛パッド']=(855*757+373*740)/1228; COST['壁掛けディスペンサー']=(41*2528+13*1981)/54
PRICE['壁掛けディスペンサー']=363920/54
Sd=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    Sd[r['name']][r['date']][0]+=int(r['gross']); Sd[r['name']][r['date']][1]+=int(r['disc'])
days=sorted(S); pr={}
for d in days:
    s=c=0
    for n,v in Sd.items():
        if n=='' or d not in v: continue
        g,dc=v[d]; s+=g-dc
        if g and n in PRICE and n in COST: c+=g/PRICE[n]*COST[n]
    pr[d]=s-c-A[d]
for i,d in enumerate(days[-7:],len(days)-7):
    ma=sum(pr[x] for x in days[i-2:i+1])/3
    print(f"  {d}  利益 {pr[d]:>9,.0f}  3日移動平均 {ma:>9,.0f}  {'🚨非常ブレーキ' if ma<130000 else ''}")
print("\n■ 頑健性チェック（限界MER=平均×0.6/0.7/0.8で符号が変わらないか）")
N7,K7,A7=R['N7'],R['K7'],R['A7']
def chk(n,act):
    s,k,a=N7[n],K7[n],A7[n]; mer=s/a; be=1/(1-k/s); v=[mer*f for f in (.6,.7,.8)]
    ok=[x<be for x in v] if act=='減額' else [x>be for x in v]
    print(f"  {n[:22]:22}{act}  MER {mer:.2f} 分岐 {be:.2f} → {v[0]:.2f}/{v[1]:.2f}/{v[2]:.2f}  {'✅3端すべて正しい' if all(ok) else '⚠️端で逆転'}")
for n in ['携帯電動シェーバー','害虫ブロッカー','4WAY','完全遮光・形状記憶','卓上冷感クーラー']: chk(n,'減額')
for n in ['W固定スマホ車載ホルダー','ナノガラス脱毛パッド','完全遮光・接触冷感UVハット']: chk(n,'増額')
print("\n■ 打ち手の効果（限界MER=平均×0.7）")
PLAN=[('卓上冷感クーラー',7500,5500,'トリガー発動'),('携帯電動シェーバー',4000,2000,'3窓すべて分岐割れ'),
      ('4WAY',21000,15750,'3窓すべて余裕<0.30'),('完全遮光・形状記憶',15750,11800,'3窓すべて余裕<0.30'),
      ('害虫ブロッカー',45000,33750,'3窓すべて余裕<0.30・8/13の判定と同時'),
      ('W固定スマホ車載ホルダー',32500,40000,'3窓すべて目標超え'),
      ('完全遮光・接触冷感UVハット',12000,15000,'3窓すべて目標超え'),
      ('ナノガラス脱毛パッド',80000,100000,'3窓すべて目標超え')]
TS=sum(N7.values()); TK=sum(K7.values()); TA=R['ACCT7']; ds=dk=da=0
for n,b0,b1,why in PLAN:
    s,k,a=N7[n],K7[n],A7[n]; cr=k/s; mm=(s/a)*0.7; d=(b1-b0)*7
    Δs=mm*d; Δk=Δs*cr; ds+=Δs; dk+=Δk; da+=d
    print(f"  {n[:22]:22}{b0:>7,}→{b1:>7,}  週{Δs-Δk-d:>+9,.0f}円  {why}")
NS,NK,NA=TS+ds,TK+dk,TA+da
print(f"  {'合計':22}{'':>16}  週{ds-dk-da:>+9,.0f}円")
print(f"\n  週利益 {TS-TK-TA:,.0f} → {NS-NK-NA:,.0f}／利益率 {(TS-TK-TA)/TS*100:.2f}% → {(NS-NK-NA)/NS*100:.2f}%")
print(f"  1日利益 {(TS-TK-TA)/7:,.0f} → {(NS-NK-NA)/7:,.0f}円／日予算 404,500 → {404500+sum(b1-b0 for _,b0,b1,_ in PLAN):,}円")
