# -*- coding: utf-8 -*-
"""2026-08-11 定例（昨日=8/10 月実績）。実測のみ・毎回ゼロから積み直す。"""
import csv, collections, datetime, json, pickle
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ネックマッサージャー':3034,
'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
'スマートノーズEMS美顔器':2453,'W固定スマホ車載ホルダー':1182,'ジェットウォッシャー':1259,'姿勢サポートチェア':1811,
'2WAYシートボックス':1943}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':4980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536,
'ナノガラス脱毛パッド':3980,'ムダ毛シェーバー':6980,'壁掛けディスペンサー':6980,
'スマートノーズEMS美顔器':5980,'W固定スマホ車載ホルダー':3980,'ジェットウォッシャー':4980,'姿勢サポートチェア':5980,
'2WAYシートボックス':4980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
# バリアント別実測（2026-08-07にShopifyへ4窓それぞれクエリして取得）
VAR={'ナノガラス脱毛パッド':{'d1':(35,10),'d3':(94,45),'d7':(233,99),'d30':(835,364),'cum':(351,146)},
     '壁掛けディスペンサー':{'d1':(0,0),'d3':(1,0),'d7':(2,0),'d30':(45,13),'cum':(3,0)}}
VARC={'ナノガラス脱毛パッド':(757,740),'壁掛けディスペンサー':(2528,1981)}
# 窓内で売価が動いた商品はvariant別net_items_sold（返品0を実測確認済）を販売数として使用
MIXQ={'ムダ毛シェーバー':{'d30':202},'湯上がりガーゼワンピース':{'d30':52},
      '3WAYサーキュレーター':{'d30':166,'cum':26},'姿勢サポートチェア':{'d30':26,'cum':26},
      '完全遮光・接触冷感UVハット':{'d30':56}}
HOL={'2026-07-20'}
WD=['月','火','水','木','金','土','日']; wd=lambda d: WD[datetime.date(*map(int,d.split('-'))).weekday()]
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
ALLD=sorted({d for v in S.values() for d in v})
D1=ALLD[-1:]; D3=ALLD[-3:]; D7=ALLD[-7:]; D30=[d for d in ALLD if d>='2026-07-12']
assert D1==['2026-08-10'] and D3[0]=='2026-08-08' and D7[0]=='2026-08-04', (D1,D3[0],D7[0])
assert len(D30)==30 and D30[0]=='2026-07-12', (len(D30),D30[0])
STORE={d: sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in ALLD}
GROSSD={d: sum(v[d][0] for v in S.values() if d in v) for d in ALLD}
base=[d for d in ALLD[-30:] if d not in HOL]
byw=collections.defaultdict(list)
for d in base: byw[wd(d)].append(STORE[d])
avg=sum(STORE[d] for d in base)/len(base)
IDX={k: sum(v)/len(v)/avg*100 for k,v in byw.items()}
WIN={}
def qty(n,days,key):
    assert key in WIN and days==WIN[key], f'窓キー取り違え key={key}'
    g=sum(S[n][d][0] for d in days if d in S[n])
    if g==0: return 0,0
    if n in VAR:
        a,b=VAR[n][key]; c1,c2=VARC[n]
        if n=='ナノガラス脱毛パッド': assert (a+b)*3980==g,(n,key,a,b,g)
        if n=='壁掛けディスペンサー': assert a*6980+b*5980==g,(n,key,a,b,g)
        return a+b, a*c1+b*c2
    if n in MIXQ and key in MIXQ[n]:
        q=MIXQ[n][key]; return q, q*COST[n]
    q=g/PRICE[n]; assert abs(q-round(q))<1e-6,(n,key,g,PRICE[n]); q=round(q)
    return q, q*COST[n]
def agg(days,key):
    sal={};dsc={};qt={};cst={}
    for n,v in S.items():
        if n=='': continue
        g=sum(v[d][0] for d in days if d in v); dc=sum(v[d][1] for d in days if d in v)
        if g==0 and dc==0: continue
        sal[n]=g-dc; dsc[n]=dc; qt[n],cst[n]=qty(n,days,key)
    return sal,dsc,qt,cst
CUM=[d for d in ALLD if d>='2026-08-01']
assert len(CUM)==10 and CUM[0]=='2026-08-01' and CUM[-1]=='2026-08-10'
WIN.update(d1=D1,d3=D3,d7=D7,d30=D30,cum=CUM)
N1,DC1,Q1,K1=agg(D1,'d1'); N3,DC3,Q3,K3=agg(D3,'d3')
N7,DC7,Q7,K7=agg(D7,'d7'); N30,DC30,Q30,K30=agg(D30,'d30')
NC,DCC,QC,KC=agg(CUM,'cum')
for lbl,N,days in [('前日',N1,D1),('3日',N3,D3),('7日',N7,D7),('30日',N30,D30),('当月累積',NC,CUM)]:
    assert sum(N.values())==sum(STORE[d] for d in days),(lbl,)
def A(days,n): return sum(AD[MAP.get(n,n)].get(d,0) for d in days)
def CAT(days): return sum(AD['カタログ全部（テスト）'].get(d,0) for d in days)
def ACCT(days): return sum(sum(AD[c].get(d,0) for c in AD) for d in days)
assert sum(v[0] for n in S for d in CUM for v in [S[n][d]] if d in S[n])==10296944
pickle.dump(dict(D1=D1,D3=D3,D7=D7,D30=D30,CUM=CUM,NC=NC,DCC=DCC,QC=QC,KC=KC,ACCTC=ACCT(CUM),CATC=CAT(CUM),AC={n:A(CUM,n) for n in NC},STORE=STORE,GROSSD=GROSSD,IDX=IDX,
  N1=N1,N3=N3,N7=N7,N30=N30,DC1=DC1,DC7=DC7,DC30=DC30,Q1=Q1,Q3=Q3,Q7=Q7,Q30=Q30,
  K1=K1,K3=K3,K7=K7,K30=K30,COST=COST,PRICE=PRICE,MAP=MAP,
  A1={n:A(D1,n) for n in N1},A3={n:A(D3,n) for n in N3},A7={n:A(D7,n) for n in N7},A30={n:A(D30,n) for n in N30},
  CAT1=CAT(D1),CAT3=CAT(D3),CAT7=CAT(D7),CAT30=CAT(D30),
  ACCT1=ACCT(D1),ACCT3=ACCT(D3),ACCT7=ACCT(D7),ACCT30=ACCT(D30)),open('/tmp/rep0811.pkl','wb'))
print('窓 D1',D1,'D3',D3[0],'D7',D7[0],'D30',D30[0],'-',D30[-1])
print('全店 実売 前日',f"{sum(N1.values()):,}",'3日',f"{sum(N3.values()):,}",'7日',f"{sum(N7.values()):,}",'30日',f"{sum(N30.values()):,}")
print('広告 前日',f"{ACCT(D1):,.0f}",'7日',f"{ACCT(D7):,.0f}",'30日',f"{ACCT(D30):,.0f}")
print('曜日指数', {k:round(v,1) for k,v in sorted(IDX.items(),key=lambda x:-x[1])})
