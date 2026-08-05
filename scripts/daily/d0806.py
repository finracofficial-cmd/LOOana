# -*- coding: utf-8 -*-
"""2026-08-06 定例（昨日=8/05 水実績）。実測のみ・毎回ゼロから積み直す。"""
import csv, collections, datetime, json, pickle
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ネックマッサージャー':3034,
'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
'スマートノーズEMS美顔器':2453,'W固定スマホ車載ホルダー':1182,'ジェットウォッシャー':1259,'姿勢サポートチェア':1811}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':4980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536,
'ナノガラス脱毛パッド':3980,'ムダ毛シェーバー':6980,'壁掛けディスペンサー':6980,
'スマートノーズEMS美顔器':5980,'W固定スマホ車載ホルダー':3980,'ジェットウォッシャー':4980,'姿勢サポートチェア':5980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
# バリアント別実測（Shopify variant別クエリ 2026-08-02取得・4窓それぞれ）
VAR={'ナノガラス脱毛パッド':{'d1':(30,8),'d3':(95,33),'d7':(238,95),'d30':(776,341),'cum':(176,68)},   # (白/緑757, 黒/桃740)
     '壁掛けディスペンサー':{'d1':(1,0),'d3':(1,0),'d7':(6,0),'d30':(55,19),'cum':(2,0)}}              # (3本2528, 2本1981)
VARC={'ナノガラス脱毛パッド':(757,740),'壁掛けディスペンサー':(2528,1981)}
# 窓内で売価が動いた商品はvariant別net_items_sold（返品0を確認済）を販売数として使用
MIXQ={'ムダ毛シェーバー':{'d30':183},                # 7/27に5,980→6,980（30日窓のみ新旧混在）
      '湯上がりガーゼワンピース':{'d30':82},            # 30日窓に4,980期がある
      '完全遮光・接触冷感UVハット':{'d30':25},          # 7/31に5,980→4,980
      '3WAYサーキュレーター':{'d7':35,'d30':182,'cum':25},           # 8/2に5,980→6,980
      '姿勢サポートチェア':{'d7':9,'d30':9,'cum':9}}                 # 8/4に7,980→5,980（8/2に7,980が1個）
HOL={'2026-07-20'}
WD=['月','火','水','木','金','土','日']; wd=lambda d: WD[datetime.date(*map(int,d.split('-'))).weekday()]
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
BUD=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv',encoding='utf-8')):
    BUD[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])
ALLD=sorted({d for v in S.values() for d in v})
D1=ALLD[-1:]; D3=ALLD[-3:]; D7=ALLD[-7:]
D30=[d for d in ALLD if d>='2026-07-07']
assert D1==['2026-08-05'] and D7[0]=='2026-07-30' and D3[0]=='2026-08-03', (D1,D7[0],D3[0])
assert len(D30)==30 and D30[0]=='2026-07-07', (len(D30),D30[0])
STORE={d: sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in ALLD}
D30C=ALLD[-30:]; base=[d for d in D30C if d not in HOL]
byw=collections.defaultdict(list)
for d in base: byw[wd(d)].append(STORE[d])
avg=sum(STORE[d] for d in base)/len(base)
IDX={k: sum(v)/len(v)/avg*100 for k,v in byw.items()}
WIN={}   # key → その窓の日付リスト（qty内で不一致をassertし、窓キーの取り違えを機械的に防ぐ）
def qty(n,days,key):
    assert key in WIN and days==WIN[key], f'窓キーの取り違え: key={key} の日付リストと引数daysが不一致'
    g=sum(S[n][d][0] for d in days if d in S[n])
    if g==0: return 0,0
    if n in VAR:
        a,b=VAR[n][key]; c1,c2=VARC[n]; return a+b, a*c1+b*c2
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
WIN.update(d1=D1,d3=D3,d7=D7,d30=D30)
N1,DC1,Q1,K1=agg(D1,'d1'); N3,DC3,Q3,K3=agg(D3,'d3')
N7,DC7,Q7,K7=agg(D7,'d7'); N30,DC30,Q30,K30=agg(D30,'d30')
for lbl,N,days in [('前日',N1,D1),('3日',N3,D3),('7日',N7,D7),('30日',N30,D30)]:
    assert sum(N.values())==sum(STORE[d] for d in days),(lbl,sum(N.values()),sum(STORE[d] for d in days))
def A(days,n): return sum(AD[MAP.get(n,n)].get(d,0) for d in days)
def CAT(days): return sum(AD['カタログ全部（テスト）'].get(d,0) for d in days)
def ACCT(days): return sum(sum(AD[c].get(d,0) for c in AD) for d in days)
for lbl,days in [('前日',D1),('3日',D3),('7日',D7),('30日',D30)]:
    s=sum(A(days,n) for n in set(PRICE)) + CAT(days)
    assert abs(s-ACCT(days))<1,(lbl,s,ACCT(days))
print('✅ 検算OK: Σ商品売上=全店売上／Σ商品広告費+カタログ=Metaアカウント消化（4期間すべて）')
print('曜日指数(祝日7/20除外・直近30日):', {k:round(v,1) for k,v in sorted(IDX.items(),key=lambda x:-x[1])})
FEE=0.03452
def blk(days,N,K): s=sum(N.values()); c=sum(K.values()); a=ACCT(days); return s,c,a,s-c-a
print()
SUM={}
for lbl,days,N,K in [('前日(8/05 水)',D1,N1,K1),('3日(8/03-8/05)',D3,N3,K3),
                     ('7日(7/30-8/05)',D7,N7,K7),('30日(7/07-8/05)',D30,N30,K30)]:
    s,c,a,p=blk(days,N,K); fee=s*FEE; SUM[lbl]=(s,c,a,p,fee)
    print(f'{lbl:<17} 売上{s:>11,} 原価{c:>10,} 広告費{a:>10,.0f} 利益{p:>10,.0f} 率{p/s*100:5.1f}% '
          f'手数料後{p-fee:>10,.0f} ({(p-fee)/s*100:4.1f}%) MER{s/a:.3f}')
# 当月累積(8/1〜)
CUM=[d for d in ALLD if d>='2026-08-01']
WIN['cum']=CUM
NC,DCC,QC,KC=agg(CUM,'cum')
cs,cc,ca,cp=blk(CUM,NC,KC)
print(f'{"📅当月累積(8/01)":<17} 売上{cs:>11,} 原価{cc:>10,} 広告費{ca:>10,.0f} 利益{cp:>10,.0f} 率{cp/cs*100:5.1f}% '
      f'手数料後{cp-cs*FEE:>10,.0f} ({(cp-cs*FEE)/cs*100:4.1f}%) MER{cs/ca:.3f}')
# 同曜日平均（土曜・祝日除外）
SAT=[d for d in D30C if wd(d)=='水' and d not in HOL]
sat=sum(STORE[d] for d in SAT)/len(SAT)
print(f'\n水曜平均(直近30日 n={len(SAT)}): {sat:,.0f}円 / 8/05実績 {STORE["2026-08-05"]:,}円 = {STORE["2026-08-05"]/sat*100:.1f}%')
BR={};TG={}
for n in set(list(N30)+list(N7)):
    if N30.get(n,0)>0 and K30.get(n,0)>0:
        cr=K30[n]/N30[n]
        BR[n]=round(1/(1-cr),2) if cr<1 else None
        TG[n]=round(1/(1-cr-0.35),2) if 1-cr-0.35>0 else None
print('\n'+'='*128)
print('■ 商品別（7日=7/30-8/05 / 3日=8/03-8/05 / 前日=8/05 / 30日=7/07-8/05。すべて実測）')
print('='*128)
print(f"{'商品':<22}{'7日売上':>10}{'7日原価':>9}{'7日広告':>9}{'7日利益':>9}{'率':>6}{'MER':>6}{'分岐':>5}{'目標':>5}{'余裕':>6}{'3日利益':>9}{'前日利益':>9}{'前日率':>7}{'30日利益':>10}{'予算':>8}")
rows=[]
for n in sorted(N7, key=lambda x:-N7[x]):
    s7=N7[n]; c7=K7[n]; a7=A(D7,n); p7=s7-c7-a7
    s3=N3.get(n,0); p3=s3-K3.get(n,0)-A(D3,n)
    s1=N1.get(n,0); p1=s1-K1.get(n,0)-A(D1,n)
    s30=N30.get(n,0); p30=s30-K30.get(n,0)-A(D30,n)
    br=BR.get(n); tg=TG.get(n); mer=s7/a7 if a7 else None
    bud=BUD.get(MAP.get(n,n),{}).get('2026-08-06')
    print(f'{n:<22}{s7:>10,}{c7:>9,}{a7:>9,.0f}{p7:>9,.0f}{p7/s7*100:>5.1f}%'
          f'{(mer if mer else 0):>6.2f}{(br or 0):>5.2f}{(tg or 0):>5.2f}{(mer-br if mer and br else 0):>+6.2f}'
          f'{p3:>9,.0f}{p1:>9,.0f}{(p1/s1*100 if s1 else 0):>6.1f}%{p30:>10,.0f}{(bud or 0):>8,}')
    rows.append((n,s7,c7,a7,p7,s3,p3,s1,p1,s30,p30,mer,br,tg,bud,Q7.get(n,0),Q1.get(n,0),Q3.get(n,0),Q30.get(n,0),DC7.get(n,0)))
print(f"{'カタログ全部（テスト）':<22}{'—':>10}{'—':>9}{CAT(D7):>9,.0f}{'—':>9}")
t7=sum(N7.values()); tc=sum(K7.values()); ta=ACCT(D7)
print(f"{'合計':<22}{t7:>10,}{tc:>9,}{ta:>9,.0f}{t7-tc-ta:>9,.0f}{(t7-tc-ta)/t7*100:>5.1f}%{t7/ta:>6.2f}")
pickle.dump(dict(rows=rows,N1=N1,N3=N3,N7=N7,N30=N30,K1=K1,K3=K3,K7=K7,K30=K30,Q1=Q1,Q7=Q7,
  DC1=DC1,DC3=DC3,DC7=DC7,DC30=DC30,D1=D1,D3=D3,D7=D7,D30=D30,CUM=CUM,IDX=IDX,STORE=STORE,BR=BR,TG=TG,SUM=SUM,
  cum=(cs,cc,ca,cp),sat=sat,
  cat=dict(d1=CAT(D1),d3=CAT(D3),d7=CAT(D7),d30=CAT(D30)),
  acct=dict(d1=ACCT(D1),d3=ACCT(D3),d7=ACCT(D7),d30=ACCT(D30))),
  open('/tmp/claude-0/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/scratchpad/rep0806.pkl','wb'))
