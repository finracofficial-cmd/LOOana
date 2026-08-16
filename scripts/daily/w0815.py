# -*- coding: utf-8 -*-
"""[8/15終端の窓ビルダー] 2026-08-16 定例（昨日=8/15 土 実績）。実測のみ・毎回ゼロから積み直す。

w0814.py からの変更点:
  - END を 2026-08-15 へ（Metaが復旧し 8/15 の広告費を取得できたため）
  - ナノガラス脱毛パッドのバリアント別を「窓ごとの手入力」から「日別実測」へ変更。
    日ごとに (a+b)*3980 == その日のgross を assert するので、1日でも取り違えたら止まる。
  - 壁掛けディスペンサーは日ごとに 3本6,980/2本5,980 の2価分解を解いて積む（手入力しない）。
"""
import csv, collections, datetime, pickle
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ネックマッサージャー':3034,
'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
'スマートノーズEMS美顔器':2453,'W固定スマホ車載ホルダー':1182,'ジェットウォッシャー':1259,'姿勢サポートチェア':1811,
'2WAYシートボックス':1943,'快適マジックインソール':677}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':4980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536,
'ナノガラス脱毛パッド':3980,'ムダ毛シェーバー':6980,'壁掛けディスペンサー':6980,
'スマートノーズEMS美顔器':5980,'W固定スマホ車載ホルダー':3980,'ジェットウォッシャー':4980,'姿勢サポートチェア':5980,
'2WAYシートボックス':4980,'快適マジックインソール':3980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}

# ── ナノガラス脱毛パッド 日別バリアント実測（2026-08-16 Shopify実測・product_type='脱毛器'）
#    値は (白系=ピュアホワイト+セージグリーン@757, 黒桃系=マットブラック+ベイビーピンク@740)
NANO={'2026-07-17':(23,10),'2026-07-18':(35,9),'2026-07-19':(18,13),'2026-07-20':(22,9),'2026-07-21':(17,7),
'2026-07-22':(27,13),'2026-07-23':(22,10),'2026-07-24':(17,10),'2026-07-25':(26,15),'2026-07-26':(32,20),
'2026-07-27':(25,10),'2026-07-28':(19,12),'2026-07-29':(33,10),'2026-07-30':(33,12),'2026-07-31':(29,15),
'2026-08-01':(41,14),'2026-08-02':(40,21),'2026-08-03':(37,12),'2026-08-04':(28,13),'2026-08-05':(30,8),
'2026-08-06':(36,12),'2026-08-07':(45,21),'2026-08-08':(34,13),'2026-08-09':(25,22),'2026-08-10':(35,10),
'2026-08-11':(48,23),'2026-08-12':(18,11),'2026-08-13':(21,11),'2026-08-14':(30,12),'2026-08-15':(46,10)}
NANOC=(757,740)
DISP=(6980,5980); DISPC=(2528,1981)   # 3本セット / 2本セット

PRICEBYDATE={'優先配送':[('0000-00-00',536)],                       # 商品ページは590円だが実課金は536円のまま
 '接触冷感UVパーカー':[('0000-00-00',3980),('2026-08-14',4980),('2026-08-16',3980)],  # 8/13 09:58 値上げ → 8/15 07:10 戻し
 'ムダ毛シェーバー':[('0000-00-00',5980),('2026-07-28',6980)],     # 7/27 値上げ
 '3WAYサーキュレーター':[('0000-00-00',5980),('2026-08-03',6980)], # 8/02 値上げ
 '完全遮光・接触冷感UVハット':[('0000-00-00',5980),('2026-07-24',4980)],
 '姿勢サポートチェア':[('0000-00-00',7980),('2026-08-03',5980)],   # 8/04に5,980で広告再開
 '湯上がりガーゼワンピース':[('0000-00-00',4980),('2026-07-20',5980)]}
MIXEDDAY={'接触冷感UVパーカー':{'2026-08-13':(3980,4980),'2026-08-15':(4980,3980)},
 'ムダ毛シェーバー':{'2026-07-27':(5980,6980)},
 '3WAYサーキュレーター':{'2026-08-02':(5980,6980)},
 '湯上がりガーゼワンピース':{'2026-07-19':(4980,5980)}}
def price_on(n,d):
    r=None
    for since,p in PRICEBYDATE[n]:
        if d>=since: r=p
    return r
def mixed_qty(g,p_old,p_new):
    for b in range(0, g//p_new + 1):
        rem=g-b*p_new
        if rem%p_old==0: return rem//p_old+b
    raise AssertionError(('混在日を分解できない',g,p_old,p_new))
def two_price(g,p1,p2):
    """gross を p1/p2 の2価に分解し (n1,n2) を返す。解が一意でなければ止める。"""
    sol=[(a,(g-a*p1)//p2) for a in range(0,g//p1+1) if (g-a*p1)%p2==0]
    assert len(sol)==1,('2価分解が一意でない',g,p1,p2,sol)
    return sol[0]

HOL={'2026-07-20','2026-08-11'}  # 海の日・山の日
WD=['月','火','水','木','金','土','日']; wd=lambda d: WD[datetime.date(*map(int,d.split('-'))).weekday()]
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
ALLD=sorted({d for v in S.values() for d in v})
END='2026-08-15'; ALLD=[d for d in ALLD if d<=END]
assert ALLD[-1]==END, ('売上CSVが8/15まで無い',ALLD[-1])
ADD=sorted({d for v in AD.values() for d in v})
assert ADD[-1]>=END, ('広告CSVが8/15まで無い',ADD[-1])
D1=ALLD[-1:]; D3=ALLD[-3:]; D7=ALLD[-7:]; D30=[d for d in ALLD if d>='2026-07-17']
assert D1==['2026-08-15'] and D3[0]=='2026-08-13' and D7[0]=='2026-08-09', (D1,D3[0],D7[0])
assert len(D30)==30 and D30[0]=='2026-07-17', (len(D30),D30[0])
CUM=[d for d in ALLD if d>='2026-08-01']
assert len(CUM)==15 and CUM[0]=='2026-08-01' and CUM[-1]==END
STORE={d: sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in ALLD}
GROSSD={d: sum(v[d][0] for v in S.values() if d in v) for d in ALLD}
base=[d for d in ALLD[-30:] if d not in HOL]
byw=collections.defaultdict(list)
for d in base: byw[wd(d)].append(STORE[d])
avg=sum(STORE[d] for d in base)/len(base)
IDX={k: sum(v)/len(v)/avg*100 for k,v in byw.items()}

# ナノガラスの日別実測をその日のgrossで1日ずつ検算する（窓の取り違えも転記ミスもここで止まる）
for d,(a,b) in NANO.items():
    g=S['ナノガラス脱毛パッド'][d][0] if d in S['ナノガラス脱毛パッド'] else 0
    assert (a+b)*3980==g, ('ナノガラス 日別バリアントがgrossと不一致',d,a,b,g)

WIN={}
def qty(n,days,key):
    assert key in WIN and days==WIN[key], f'窓キー取り違え key={key}'
    g=sum(S[n][d][0] for d in days if d in S[n])
    if g==0: return 0,0
    if n=='ナノガラス脱毛パッド':
        a=sum(NANO[d][0] for d in days if d in NANO); b=sum(NANO[d][1] for d in days if d in NANO)
        assert (a+b)*3980==g,(n,key,a,b,g)
        return a+b, a*NANOC[0]+b*NANOC[1]
    if n=='壁掛けディスペンサー':
        q=k=0
        for d in days:
            gd=S[n][d][0] if d in S[n] else 0
            if not gd: continue
            n1,n2=two_price(gd,*DISP); q+=n1+n2; k+=n1*DISPC[0]+n2*DISPC[1]
        return q,k
    if n in PRICEBYDATE:
        q=0
        for d in days:
            gd=S[n][d][0] if d in S[n] else 0
            if not gd: continue
            if n in MIXEDDAY and d in MIXEDDAY[n]:
                q+=mixed_qty(gd,*MIXEDDAY[n][d]); continue
            pd=price_on(n,d); x=gd/pd
            assert abs(x-round(x))<1e-6,(n,d,gd,pd)
            q+=round(x)
        return q, q*COST[n]
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
WIN.update(d1=D1,d3=D3,d7=D7,d30=D30,cum=CUM)
N1,DC1,Q1,K1=agg(D1,'d1'); N3,DC3,Q3,K3=agg(D3,'d3')
N7,DC7,Q7,K7=agg(D7,'d7'); N30,DC30,Q30,K30=agg(D30,'d30')
NC,DCC,QC,KC=agg(CUM,'cum')
for lbl,N,days in [('前日',N1,D1),('3日',N3,D3),('7日',N7,D7),('30日',N30,D30),('当月累積',NC,CUM)]:
    assert sum(N.values())==sum(STORE[d] for d in days),(lbl,)
# 日次の原価も同じ qty() で厳密に積む（7日平均の原価率で近似しない）
KDAY={}
for d in D30:   # ナノガラスの日別バリアント実測がある範囲＝7/17以降に限る
    WIN['day_'+d]=[d]
    KDAY[d]=sum(qty(n,[d],'day_'+d)[1] for n in S if n!='' and d in S[n] and S[n][d][0])
def A(days,n): return sum(AD[MAP.get(n,n)].get(d,0) for d in days)
def CAT(days): return sum(AD['カタログ全部（テスト）'].get(d,0) for d in days)
def ACCT(days): return sum(sum(AD[c].get(d,0) for c in AD) for d in days)
ALLN=set(N1)|set(N3)|set(N7)|set(N30)|set(NC)|{n for n in PRICE}
ALLN={n for n in ALLN if n!=''}
pickle.dump(dict(D1=D1,D3=D3,D7=D7,D30=D30,CUM=CUM,NC=NC,DCC=DCC,QC=QC,KC=KC,ACCTC=ACCT(CUM),CATC=CAT(CUM),
  AC={n:A(CUM,n) for n in ALLN},STORE=STORE,GROSSD=GROSSD,IDX=IDX,KDAY=KDAY,
  N1=N1,N3=N3,N7=N7,N30=N30,DC1=DC1,DC3=DC3,DC7=DC7,DC30=DC30,Q1=Q1,Q3=Q3,Q7=Q7,Q30=Q30,
  K1=K1,K3=K3,K7=K7,K30=K30,COST=COST,PRICE=PRICE,MAP=MAP,
  A1={n:A(D1,n) for n in ALLN},A3={n:A(D3,n) for n in ALLN},A7={n:A(D7,n) for n in ALLN},A30={n:A(D30,n) for n in ALLN},
  CAT1=CAT(D1),CAT3=CAT(D3),CAT7=CAT(D7),CAT30=CAT(D30),
  ACCT1=ACCT(D1),ACCT3=ACCT(D3),ACCT7=ACCT(D7),ACCT30=ACCT(D30)),open('/tmp/rep0815w.pkl','wb'))
print('窓 D1',D1,'D3',D3[0],'D7',D7[0],'D30',D30[0],'-',D30[-1],'CUM',CUM[0],'-',CUM[-1])
for lbl,N,K,dd in [('前日',N1,K1,D1),('3日',N3,K3,D3),('7日',N7,K7,D7),('30日',N30,K30,D30),('当月',NC,KC,CUM)]:
    s=sum(N.values()); k=sum(K.values()); a=ACCT(dd)
    print(f'{lbl:4} 売上{s:>11,} 原価{k:>10,} 広告{a:>11,.0f} 利益{s-k-a:>10,.0f} 利益率{(s-k-a)/s*100:5.1f}%')
print('曜日指数', {k:round(v,1) for k,v in sorted(IDX.items(),key=lambda x:-x[1])})
