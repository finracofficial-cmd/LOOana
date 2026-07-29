# -*- coding: utf-8 -*-
"""2026-07-30 定例（昨日=7/29 水実績）。日次CSV（Shopify/Meta実測）から毎回ゼロから積み直す。
   売上=gross−その商品の値引 ／ 原価=販売数(gross÷売価)ベース・返品は別窓 ／ カタログ広告は1行で持つ"""
import csv, collections, datetime, statistics, json

COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ネックマッサージャー':3034,
'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':5980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536}
# 窓内で売価が変動（返品ゼロを確認済みのため net_items_sold を販売数として代用）
MIXPRICE={'ムダ毛シェーバー','湯上がりガーゼワンピース'}
FULL={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
      '3WAYサーキュレーター':'3WAYサーキュレーター扇風機'}
REVF={v:k for k,v in FULL.items()}
MAP=dict(FULL); MAP['壁掛けディスペンサー']='ディスペンサー'
HOLIDAYS={'2026-07-20'}
WD=['月','火','水','木','金','土','日']
def wd(d): return WD[datetime.date(*map(int,d.split('-'))).weekday()]

# ===== 日次CSV（実測）=====
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
BUDS=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv',encoding='utf-8')):
    BUDS[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])

ALLD=sorted({d for v in S.values() for d in v})
D30=ALLD[-30:]; D7=ALLD[-7:]; D3=ALLD[-3:]; D1=ALLD[-1:]
assert D1==['2026-07-29'] and D7[0]=='2026-07-23' and D30[0]=='2026-06-30', (D1,D7[0],D30[0])
STORE={d: sum(v[d][0]-v[d][1] for v in S.values() if d in v) for d in ALLD}
GROSS={d: sum(v[d][0] for v in S.values() if d in v) for d in ALLD}
DISC={d: sum(v[d][1] for v in S.values() if d in v) for d in ALLD}
# 曜日指数（祝日除外・30日）
base=[d for d in D30 if d not in HOLIDAYS]
byw=collections.defaultdict(list)
for d in base: byw[wd(d)].append(STORE[d])
avg=sum(STORE[d] for d in base)/len(base)
IDX={k: sum(v)/len(v)/avg*100 for k,v in byw.items()}

# ===== 数量（gross÷売価。返品を引かない）=====
# バリエーション別 gross（実測）→ 販売数
NANOV={'d7':(557200+135320, 246760+99500),'d3':(274620+31840, 95520+31840),
       'd1':(119400+11940, 27860+11940),'d30':(2268600+696500, 1002960+362180)}
DISPV={'d7':(27920+6980+6980, 17940+11960+5980),'d3':(6980, 5980),'d1':(0,0),
       'd30':(300140+167520+76780+55840, 71760+47840+41860+41860)}
NANOQ={k:(round(a/3980), round(b/3980)) for k,(a,b) in NANOV.items()}
DISPQ={k:(round(a/6980), round(b/5980)) for k,(a,b) in DISPV.items()}
# net_items_sold（実測・代用用）
NET={'d7':{'ムダ毛シェーバー':47,'湯上がりガーゼワンピース':4},
     'd3':{'ムダ毛シェーバー':23,'湯上がりガーゼワンピース':0},
     'd1':{'ムダ毛シェーバー':10,'湯上がりガーゼワンピース':0},
     'd30':{'ムダ毛シェーバー':116,'湯上がりガーゼワンピース':120}}
def agg(days,key):
    """期間の 売上(gross−値引)・値引・販売数・原価 を返す"""
    sal={}; dsc={}; qty={}; cst={}
    for n,v in S.items():
        if n=='': continue
        g=sum(v[d][0] for d in days if d in v); dc=sum(v[d][1] for d in days if d in v)
        if g==0 and dc==0: continue
        sal[n]=g-dc; dsc[n]=dc
        if n=='ナノガラス脱毛パッド':
            a,b=NANOQ[key]; qty[n]=a+b; cst[n]=a*757+b*740
        elif n=='壁掛けディスペンサー':
            a,b=DISPQ[key]; qty[n]=a+b; cst[n]=a*2528+b*1981
        elif n in MIXPRICE:
            qty[n]=NET[key][n]; cst[n]=qty[n]*COST[n]
        else:
            q=g/PRICE[n]; assert abs(q-round(q))<1e-6,(n,key,g); qty[n]=round(q); cst[n]=qty[n]*COST[n]
    return sal,dsc,qty,cst
N7,DC7,Q7,K7=agg(D7,'d7'); N3,DC3,Q3,K3=agg(D3,'d3')
N1,DC1,Q1,K1=agg(D1,'d1'); N30,DC30,Q30,K30=agg(D30,'d30')
# 検算: Σ商品売上 = 全店売上
for lbl,N,days in [('7日',N7,D7),('3日',N3,D3),('前日',N1,D1),('30日',N30,D30)]:
    assert sum(N.values())==sum(STORE[d] for d in days),(lbl,sum(N.values()),sum(STORE[d] for d in days))

def A(days,n): return sum(AD[MAP.get(n,n)].get(d,0) for d in days)
CAT7=sum(AD['カタログ全部（テスト）'].get(d,0) for d in D7)
CAT3=sum(AD['カタログ全部（テスト）'].get(d,0) for d in D3)
CAT1=AD['カタログ全部（テスト）'].get(D1[0],0)
CAT30=sum(AD['カタログ全部（テスト）'].get(d,0) for d in D30)
# 30日のキャンペーン別実測（Meta 6/30-7/29）
AD30={'害虫ブロッカー':1903576,'4WAY':1865187,'形状記憶日傘':1794292,'ナノガラス脱毛パッド':1593159,
'完全遮光・形状記憶':939903,'接触冷感UVパーカー':818469,'偏光・調光サングラス':660219,'接触冷感UVアームカバー':501217,
'壁掛けディスペンサー':480354,'卓上冷感クーラー':409308,'健康サンダル':388900,'携帯電動シェーバー':369597,
'3WAYサーキュレーター':365965,'UV歯ブラシ除菌器':357464,'湯上がりガーゼワンピース':297825,'バランスケアスリッパ':292464,
'ムダ毛シェーバー':262083,'瞬間冷感ポンチョ':240577,'5WAY腰掛けファン':134664}
# 検算: 日次CSVの30日合計 = Metaのキャンペーン別30日合計
for n,v in AD30.items():
    c=A(D30,n); assert abs(c-v)/v<0.005,(n,c,v)
ACCT30=sum(sum(AD[c].get(d,0) for c in AD) for d in D30)
