# -*- coding: utf-8 -*-
import pickle, json, csv, collections, datetime
d=pickle.load(open('rep0731.pkl','rb'))
rows=d['rows']; N1,N3,N7,N30=d['N1'],d['N3'],d['N7'],d['N30']; K1,K3,K7,K30=d['K1'],d['K3'],d['K7'],d['K30']
cat=d['cat']; acct=d['acct']; RET30=d['RET30']; IDX=d['IDX']; STORE=d['STORE']
B='/home/user/LOOana/data/daily/'
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
ALLD=sorted(STORE); ACCT={x: sum(AD[c].get(x,0) for c in AD) for x in ALLD}
def T(days,N,K): s=sum(N.values()); c=sum(K.values()); a=sum(ACCT[x] for x in days); return s,c,a,s-c-a
D1,D3,D7,D30=d['D1'],d['D3'],d['D7'],d['D30']
s1,c1,a1,p1=T(D1,N1,K1); s3,c3,a3,p3=T(D3,N3,K3); s7,c7,a7,p7=T(D7,N7,K7); s30,c30,a30,p30=T(D30,N30,K30)
THU=[x for x in ALLD[-30:] if datetime.date(*map(int,x.split('-'))).weekday()==3 and x!='2026-07-30']
thu=sum(STORE[x] for x in THU)/len(THU)
CUM=[x for x in ALLD if x>='2026-07-18']
cs=sum(STORE[x] for x in CUM); cc=sum(sum(K30.values()) for _ in [0])  # 原価は後述
# 累積の原価は日次からは分解できないため30日の原価率で按分せず、構成日の商品別実測を積む
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
FEE=0.0349
out={}
out['date']='2026-07-31(金) 定例（昨日=7/30 木実績）'
out['headline']=[
 ['売上(gross−値引)',s1,round(thu),round(s3/3),round(s7/7),round(s30/30),f'{(s1/(s7/7)-1)*100:+.1f}%'],
 ['原価(販売数ベース)',c1,'',round(c3/3),round(c7/7),round(c30/30),f'{(c1/(c7/7)-1)*100:+.1f}%'],
 ['広告費(カタログ含む)',round(a1),'',round(a3/3),round(a7/7),round(a30/30),f'{(a1/(a7/7)-1)*100:+.1f}%'],
 ['利益',round(p1),'',round(p3/3),round(p7/7),round(p30/30),f'{(p1/(p7/7)-1)*100:+.1f}%'],
 ['利益率',f'{p1/s1*100:.1f}%','',f'{p3/s3*100:.1f}%',f'{p7/s7*100:.1f}%',f'{p30/s30*100:.1f}%',f'{(p1/s1-p7/s7)*100:+.1f}pt'],
 ['手数料控除後利益',round(p1-s1*FEE),'',round((p3-s3*FEE)/3),round((p7-s7*FEE)/7),round((p30-s30*FEE)/30),''],
 ['値引(内数)',sum(v[1] for v in [[0,44555]]),'',0,0,0,'—'],
 ['返品(別窓・原価に影響させない)',5933,'','','','','当月累計237,201円(0.61%)'],
]
out['headline'][6]=['値引(内数)',44555,'',round(sum(S[n][x][1] for n in S for x in D3)/3),
                    round(sum(S[n][x][1] for n in S for x in D7)/7),round(sum(S[n][x][1] for n in S for x in D30)/30),'—']
out['summary']=[
 ['前日(7/30 木)',s1,c1,round(a1),round(p1),round(p1/s1,4),round(s1*FEE),round(p1-s1*FEE),round((p1-s1*FEE)/s1,4)],
 ['3日(7/28-30)',s3,c3,round(a3),round(p3),round(p3/s3,4),round(s3*FEE),round(p3-s3*FEE),round((p3-s3*FEE)/s3,4)],
 ['7日(7/24-30)',s7,c7,round(a7),round(p7),round(p7/s7,4),round(s7*FEE),round(p7-s7*FEE),round((p7-s7*FEE)/s7,4)],
 ['30日(7/01-30)',s30,c30,round(a30),round(p30),round(p30/s30,4),round(s30*FEE),round(p30-s30*FEE),round((p30-s30*FEE)/s30,4)],
]
cum_a=sum(ACCT[x] for x in CUM)
out['summary'].append([f'📅7/18〜7/30累積({len(CUM)}日)',cs,'—',round(cum_a),'—','—','—','—','—'])
# 商品別
prod=[]
for (n,S7,C7,A7,P7,S3,P3,Sd,Pd,S30,P30,mer,br,tg,bud,q7,q1) in rows:
    prod.append([n,S7,C7,round(A7),round(P7),round(P7/S7,4) if S7 else '',
                 S3,round(P3),round(P3/S3,4) if S3 else '',
                 Sd,round(Pd),round(Pd/Sd,4) if Sd else '',
                 round(P30),round(mer,2) if mer else '—',br or '—',tg or '—',
                 round(mer-br,2) if mer and br else '—',q7,q1,bud or '—'])
prod.append(['カタログ全部（テスト）※全商品横断','—','—',round(cat['d7']),'—','—','—','—','—','—','—','—','—','—','—','—','—','—','—',30000])
out['products']=prod
json.dump(out,open('/home/user/LOOana/data/report-data-2026-07-31.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('json ok')
print(f'前日 売上{s1:,} 原価{c1:,} 広告費{a1:,.0f} 利益{p1:,.0f} ({p1/s1*100:.1f}%)')
print(f'7日  売上{s7:,} 原価{c7:,} 広告費{a7:,.0f} 利益{p7:,.0f} ({p7/s7*100:.1f}%) MER{s7/a7:.3f}')
print(f'7/18累積 {len(CUM)}日 売上{cs:,} 広告費{cum_a:,.0f} MER{cs/cum_a:.3f}')
