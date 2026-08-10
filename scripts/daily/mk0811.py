# -*- coding: utf-8 -*-
import pickle, datetime, collections, json
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
FEE=0.03452
D1,D3,D7,D30=R['D1'],R['D3'],R['D7'],R['D30']
def blk(N,K,A,cat,acct,label,days):
    s=sum(N.values()); c=sum(K.values()); a=acct
    pf=s-c-a
    return dict(label=label,days=len(days),sales=s,cogs=c,ad=a,profit=pf,
        rate=pf/s,mer=s/a,be=1/(1-c/s),cost_rate=c/s,fee=s*FEE,net=pf-s*FEE)
SUM={}
for k,(N,K,A,cat,acct,days) in {
 'd1':(R['N1'],R['K1'],R['A1'],R['CAT1'],R['ACCT1'],D1),
 'd3':(R['N3'],R['K3'],R['A3'],R['CAT3'],R['ACCT3'],D3),
 'd7':(R['N7'],R['K7'],R['A7'],R['CAT7'],R['ACCT7'],D7),
 'd30':(R['N30'],R['K30'],R['A30'],R['CAT30'],R['ACCT30'],D30)}.items():
    SUM[k]=blk(N,K,A,cat,acct,k,days)
print('=== 全体サマリー（実測） ===')
print(f"{'窓':>5}{'実売':>12}{'原価':>12}{'広告':>12}{'利益':>12}{'利益率':>8}{'MER':>7}{'分岐':>7}{'手数料後':>12}")
for k in ['d1','d3','d7','d30']:
    b=SUM[k]
    print(f"{k:>5}{b['sales']:>12,}{b['cogs']:>12,}{b['ad']:>12,.0f}{b['profit']:>12,.0f}{b['rate']*100:>7.2f}%{b['mer']:>7.2f}{b['be']:>7.2f}{b['net']:>12,.0f}")
# 商品別
rows=[]
for n in sorted(R['N7'], key=lambda x:-R['N7'][x]):
    s7=R['N7'][n]; c7=R['K7'][n]; a7=R['A7'].get(n,0)
    s1=R['N1'].get(n,0); c1=R['K1'].get(n,0); a1=R['A1'].get(n,0)
    s3=R['N3'].get(n,0); c3=R['K3'].get(n,0); a3=R['A3'].get(n,0)
    s30=R['N30'].get(n,0); c30=R['K30'].get(n,0); a30=R['A30'].get(n,0)
    p7=s7-c7-a7; p1=s1-c1-a1; p3=s3-c3-a3; p30=s30-c30-a30
    gm=1-c7/s7 if s7 else 0
    mer=s7/a7 if a7 else None; be=1/gm if gm else None
    rows.append(dict(name=n,s7=s7,c7=c7,a7=a7,p7=p7,s1=s1,p1=p1,r1=(p1/s1 if s1 else None),
        p3=p3,p30=p30,mer=mer,be=be,yo=(mer-be if mer and be else None),
        q7=R['Q7'].get(n,0),per=(mer*gm-1 if mer else None),cut=(1-mer*0.7*gm if mer else None)))
print()
print('=== 商品別（7日=判定単位・実測） ===')
print(f"{'商品':16}{'7日売上':>11}{'原価':>10}{'広告':>10}{'7日利益':>10}{'MER':>6}{'分岐':>6}{'余裕':>7}{'前日利益':>10}{'30日利益':>11}")
for r in rows:
    m=f"{r['mer']:.2f}" if r['mer'] else '—'; b=f"{r['be']:.2f}" if r['be'] else '—'
    y=f"{r['yo']:+.2f}" if r['yo'] is not None else '—'
    print(f"{r['name'][:16]:16}{r['s7']:>11,}{r['c7']:>10,}{r['a7']:>10,.0f}{r['p7']:>10,.0f}{m:>6}{b:>6}{y:>7}{r['p1']:>10,.0f}{r['p30']:>11,.0f}")
print(f"{'カタログ全部（テスト）':16}{'—':>11}{'—':>10}{R['CAT7']:>10,.0f}{'—':>10}{'—':>6}{'—':>6}{'—':>7}{'—':>10}{'—':>11}")
# 照合
sp=sum(r['p7'] for r in rows)
print()
print('=== 照合 ===')
print('Σ商品利益 − カタログ広告費 =', f"{sp-R['CAT7']:,.0f}", ' vs 全店7日利益', f"{SUM['d7']['profit']:,.0f}",
      ' 差', f"{sp-R['CAT7']-SUM['d7']['profit']:,.0f}")
print('Σ商品広告費 + カタログ =', f"{sum(r['a7'] for r in rows)+R['CAT7']:,.0f}", ' vs アカウント7日', f"{R['ACCT7']:,.0f}")
json.dump(dict(SUM={k:{kk:(vv if not isinstance(vv,float) else round(vv,4)) for kk,vv in v.items()} for k,v in SUM.items()},
  rows=rows,CAT7=R['CAT7'],IDX=R['IDX'],STORE=R['STORE']),open('/tmp/rep0810.json','w'),ensure_ascii=False)
