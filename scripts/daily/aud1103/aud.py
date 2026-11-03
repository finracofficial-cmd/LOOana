import collections,re,io,contextlib,os
D=os.path.dirname(os.path.abspath(__file__))+'/'
def load(fn,keyidx):
    T=collections.defaultdict(lambda:[0]*5)
    for line in open(D+fn):
        p=line.strip().split(',')
        if len(p)<8: continue
        v=[0 if x=='null' else int(x) for x in p[-5:]]; k=(p[0],)+tuple(p[i] for i in keyidx)
        for i in range(5): T[k][i]+=v[i]
    return T
P=load('placement.txt',(1,2)); A=load('age.txt',(1,))
def agg(T,sel,days):
    out=collections.defaultdict(lambda:[0]*5)
    for k,v in T.items():
        if k[0] in days:
            for i in range(5): out[sel(k)][i]+=v[i]
    return out
prev=[f'2026-10-{d}' for d in range(27,32)]+['2026-11-01','2026-11-02']; today=['2026-11-03']
def show(T,sel,label,order=None):
    a=agg(T,sel,prev); b=agg(T,sel,today); ia=sum(v[1] for v in a.values()); ib=sum(v[1] for v in b.values()); la=sum(v[3] for v in a.values()); lb=sum(v[3] for v in b.values())
    print(f'\n{label}: 表示シェア 直近7日→今日 | LPVシェア | 7日の CPM / Meta購入÷LPV / Meta購入1件あたり広告')
    keys=order or sorted(a,key=lambda k:-a[k][1])
    for k in keys:
        x=a.get(k,[0]*5); y=b.get(k,[0]*5)
        if x[1]<1000: continue
        print(f"  {k}: {x[1]/ia:5.1%}→{y[1]/ib:5.1%} | {x[3]/la:5.1%}→{(y[3]/lb if lb else 0):5.1%} | CPM{x[0]/x[1]*1000:5,.0f} 率{(x[4]/x[3] if x[3] else 0):.1%} CPA{(x[0]/x[4] if x[4] else 0):6,.0f} | 今日 CPM{(y[0]/y[1]*1000 if y[1] else 0):5,.0f} 率{(y[4]/y[3] if y[3] else 0):.1%}")
    print(f"  合計7日: CPM{sum(v[0] for v in a.values())/ia*1000:,.0f} 率{sum(v[4] for v in a.values())/la:.1%} CPA{sum(v[0] for v in a.values())/sum(v[4] for v in a.values()):,.0f} | 今日 CPM{sum(v[0] for v in b.values())/ib*1000:,.0f} 率{sum(v[4] for v in b.values())/lb:.1%}")
    return a,b,ia,ib,la,lb
a,b,ia,ib,la,lb=show(P,lambda k:k[1]+'/'+k[2].replace('instagram_','').replace('facebook_',''),'配置')
# mix effect of placement on LPV->purchase: today's LPV mix with 7-day placement rates
rate7={k:(v[4]/v[3] if v[3] else 0) for k,v in a.items()}
mix_rate=sum((b[k][3]/lb)*rate7.get(k,0) for k in b)/1; base=sum(v[4] for v in a.values())/la
print(f"配置構成の効果: 7日の配置別購入率に今日のLPV構成を当てると {mix_rate:.2%}（7日実績 {base:.2%}）→ 構成変化による差 {mix_rate-base:+.2%}pt")
show(A,lambda k:k[1],'年齢',order=['18-24','25-34','35-44','45-54','55-64','65+'])
# excluding threads CPM today vs 7 days
nt=lambda T,days:[sum(v[i] for k,v in T.items() if k[0] in days and k[1]!='threads') for i in range(5)]
x=nt(P,prev); y=nt(P,today); print(f"\nThreads除くCPM: 7日 {x[0]/x[1]*1000:,.0f} → 今日 {y[0]/y[1]*1000:,.0f} ({(y[0]/y[1])/(x[0]/x[1])-1:+.0%})")
