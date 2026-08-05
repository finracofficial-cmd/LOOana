# -*- coding: utf-8 -*-
"""2026-08-06 レポートJSON構築（products 32列・診断・CVR・シグナル・ネクストアクション）"""
import pickle, json, csv, collections, datetime
SC='/tmp/claude-0/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/scratchpad/'
d=pickle.load(open(SC+'rep0806.pkl','rb')); aux=json.load(open(SC+'aux0806.json',encoding='utf-8'))
rows=d['rows']; SUM=d['SUM']; IDX=d['IDX']; STORE=d['STORE']; BR=d['BR']; TG=d['TG']
D1,D3,D7,D30,CUM=d['D1'],d['D3'],d['D7'],d['D30'],d['CUM']
N1,N3,N7,N30=d['N1'],d['N3'],d['N7'],d['N30']; K1,K3,K7,K30=d['K1'],d['K3'],d['K7'],d['K30']
DC7=d['DC7']; Q7=d['Q7']; cat=d['cat']; acct=d['acct']; cum=d['cum']; sat=d['sat']
W1,W2,ORD7,RET7,SEASON,BUD=aux['W1'],aux['W2'],aux['ORD7'],aux['RET7'],aux['SEASON'],aux['BUD']
FEE=0.03452
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
A=lambda days,n: sum(AD[MAP.get(n,n)].get(x,0) for x in days)

# ===== ① CVR（Shopify注文 ÷ Metaクリック）=====
cvr={}; rpc={}
for n,(c,i,cpm,ctr,cl,fq) in W2.items():
    if cl and n in ORD7: cvr[n]=ORD7[n]/cl; rpc[n]=N7.get(n,0)/cl
order=sorted(cvr,key=lambda x:-cvr[x]); rank={n:i+1 for i,n in enumerate(order)}
med=sorted(cvr.values())[len(cvr)//2]
CVR=[['商品','CVR(Shopify注文÷Metaクリック)','順位','売上/クリック']]+\
    [[n,f'{cvr[n]*100:.2f}%',rank[n],round(rpc[n])] for n in order]

# ===== ② 診断（週次・配信指標のみ）=====
DIAG=[['商品','消化(7/30-8/5)','CPM前週比','CTR前週比','頻度','インプ前週比','診断（配信指標のみ）']]
diagmap={}
for n in sorted(W2,key=lambda x:-W2[x][0]):
    if n not in W1: continue
    c2,i2,m2,t2,cl2,f2=W2[n]; c1,i1,m1,t1,cl1,f1=W1[n]
    dm,dt,di,df=m2/m1-1,t2/t1-1,i2/i1-1,f2/f1-1
    cpa2=c2/ORD7[n] if ORD7.get(n) else None
    if di>=0.30 and abs(df)<=0.10: dg='D1a 配信面の拡大（予算起因・CRでは直らない）'
    elif dt<=-0.15: dg='D1 素材疲弊 → CR追加（予算据置）'
    elif f2>2.5: dg='D2 頻度過多'
    elif dm>=0.15: dg='D4 CPM上昇'
    elif dt>=0 and dm<0.15: dg='—（配信は健全）'
    else: dg='—'
    diagmap[n]=dg
    DIAG.append([n,round(c2),f'{dm*100:+.1f}%',f'{dt*100:+.1f}%',round(f2,2),f'{di*100:+.1f}%',dg])

# ===== ③ 変化型3日シグナル =====
P3=D7[-3:]; P7=[x for x in STORE if '2026-07-23'<=x<='2026-07-29']
def cmer(days,n):
    s=sum((d['N7'].get(n,0),)[0] for _ in [0])  # placeholder
    return None
def wmer(days,n):
    s=sum(sum(v[x][0]-v[x][1] for x in days if x in v) for k,v in [(n,SALES[n])]) if n in SALES else 0
    a=A(days,n); 
    if not a: return None
    w=sum(IDX[WD[datetime.date(*map(int,x.split('-'))).weekday()]] for x in days)/len(days)/100
    return (s/a)/w
WD=['月','火','水','木','金','土','日']
SALES=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv',encoding='utf-8')):
    SALES[r['name']][r['date']][0]+=int(r['gross']); SALES[r['name']][r['date']][1]+=int(r['disc'])
SIG={}
for n in W2:
    a,b=wmer(P3,n),wmer(P7,n)
    if a and b: SIG[n]=a/b

# ===== ④ products 32列 =====
STATE={}; ACTION={}
def st(n,s7,p7,p3,mer,br,tg,pace):
    if p7<0 or (mer and br and mer<br): return '🚨縮小・停止'
    if mer and br and (mer<br+0.30): return '🔧改善'
    if mer and tg and mer>=tg and pace and pace>=0.95: return '🚀伸ばす候補'
    return '✅維持'
WKD=['2026-08-02','2026-08-03','2026-08-04','2026-08-05']  # 暦週(日〜土)の経過4日
PACE={}
for n,*_ in rows:
    c=MAP.get(n,n); b=BUD.get(c,0)
    if b>0: PACE[n]=sum(AD[c].get(x,0) for x in WKD)/(b*4)
PROD=[]
for (n,s7,c7,a7,p7,s3,p3,s1,p1,s30,p30,mer,br,tg,bud,q7,q1,q3,q30,dc7) in rows:
    c3=K3.get(n,0); a3=A(D3,n); c1=K1.get(n,0); a1=A(D1,n)
    state=st(n,s7,p7,p3,mer,br,tg,PACE.get(n)) if a7>0 else '📦広告なし'
    PROD.append([n,s7,c7,round(a7),round(p7),p7/s7 if s7 else 0, c7/s7 if s7 else 0, a7/s7 if s7 else 0,
      s3,c3,round(a3),round(p3),p3/s3 if s3 else 0, s1,c1,round(a1),round(p1),p1/s1 if s1 else 0,
      round(p30), round(mer,2) if mer else '—', br or '—', tg or '—', round(mer-br,2) if (mer and br) else '—','—',
      round(cvr[n],4) if n in cvr else '—', rank.get(n,'—'), SEASON.get(n,'通年'),
      dc7, RET7.get(n,0), bud or 0, state, ''])
STATE={r[0]:r[30] for r in PROD}
json.dump(dict(PROD=PROD,CVR=CVR,DIAG=DIAG,SIG={k:round(v,3) for k,v in SIG.items()},
  med=med,PACE={k:round(v,3) for k,v in PACE.items()},diagmap=diagmap),
  open(SC+'b0806.json','w'),ensure_ascii=False)
print(f'CVR中央値 {med*100:.2f}%  / products {len(PROD)}行')
print('\n■ 変化型3日シグナル（直近3日の曜日補正MER ÷ 7/23-29ベースライン）')
for n,v in sorted(SIG.items(),key=lambda x:x[1]):
    m='🔻減額圏' if v<=0.75 else ('🔺増額圏' if v>=1.25 else '')
    if m: print(f'  {n:<22}{v:.2f}  {m}')
print('\n■ 週消化率（暦週8/02-08の経過4日）')
for n,v in sorted(PACE.items(),key=lambda x:-x[1])[:8]: print(f'  {n:<22}{v*100:5.0f}%')
print('\n■ 状態')
c=collections.Counter(r[30] for r in PROD)
for k,v in c.most_common(): print(f'  {k}: {v}')
for r in PROD:
    if r[30] in ('🚨縮小・停止','🔧改善'): print(f'   {r[30]} {r[0]}  7日利益{r[4]:+,} MER{r[19]} 分岐{r[20]} 余裕{r[22]}')
