# -*- coding: utf-8 -*-
"""LOOTY 直近のパフォーマンス急落 網羅診断（2026-07-30）すべて実測"""
import csv, collections, datetime, math, statistics
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'優先配送':0,'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ネックマッサージャー':3034,
'リカバリーサンダル':1309,'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
'ナノガラス脱毛パッド':751,'壁掛けディスペンサー':2318}   # 末2件は30日実測ミックスの加重平均
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':5980,'ナノバブルシャワーヘッド':6980,'ネックマッサージャー':9980,
'リカバリーサンダル':3980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,'優先配送':536,
'ナノガラス脱毛パッド':3980,'壁掛けディスペンサー':6530,'ムダ毛シェーバー':5980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
     '3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
SUMMER={'4WAY','形状記憶日傘','完全遮光・形状記憶','卓上冷感クーラー','接触冷感UVパーカー','5WAY腰掛けファン',
        '偏光・調光サングラス','3WAYサーキュレーター','接触冷感UVアームカバー','瞬間冷感ポンチョ',
        '瞬間冷却ハンディファン','完全遮光・接触冷感UVハット','湯上がりガーゼワンピース','害虫ブロッカー'}
WD=['月','火','水','木','金','土','日']
wd=lambda d: WD[datetime.date(*map(int,d.split('-'))).weekday()]

S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
BUD=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv',encoding='utf-8')):
    BUD[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])

# --- Meta アカウント日次（実測・今回取得）cost,imp,reach,freq,clicks,ctr,cpm,purch,value
MA={}
for row in """2026-07-02,406597,182452,163688,1.1146,5661,.0327,2228.5149,204,1142469
2026-07-03,414845,190302,173304,1.0981,5870,.0319,2179.9298,217,1286980
2026-07-04,396229,175244,165810,1.0569,6083,.036,2261.0132,234,1344141
2026-07-05,486773,203959,181634,1.1229,8155,.0413,2386.6218,287,1590877
2026-07-06,404154,166690,148324,1.1238,5789,.0361,2424.5846,178,1002798
2026-07-07,400730,171500,157938,1.0859,5489,.0333,2336.6181,153,843720
2026-07-08,422730,165220,150320,1.0991,5617,.0354,2558.5885,165,938553
2026-07-09,424206,164629,148645,1.1075,5428,.0342,2576.7392,173,994067
2026-07-10,443849,164194,150234,1.0929,5661,.0358,2703.1987,215,1267853
2026-07-11,449807,175252,157312,1.114,6208,.0367,2566.6298,246,1366595
2026-07-12,520194,195694,175771,1.1133,7207,.0382,2658.2011,279,1551935
2026-07-13,442603,167134,149059,1.1213,5596,.0345,2648.1925,198,1189941
2026-07-14,469437,160605,144053,1.1149,5874,.0389,2922.9289,221,1281015
2026-07-15,457358,153828,130862,1.1755,5409,.0375,2973.1778,217,1285464
2026-07-16,462095,176568,157774,1.1191,5914,.0352,2617.0937,191,1139129
2026-07-17,465259,182001,158176,1.1506,5899,.034,2556.3541,201,1170378
2026-07-18,502628,210371,199032,1.057,6912,.0343,2389.2457,236,1321593
2026-07-19,526222,214173,184653,1.1599,6847,.0334,2456.995,210,1185741
2026-07-20,569378,239536,210382,1.1386,7765,.0338,2377.0039,263,1535427
2026-07-21,523535,229146,204159,1.1224,7411,.0337,2284.7224,232,1325420
2026-07-22,542527,228273,201141,1.1349,7833,.0359,2376.6586,276,1638969
2026-07-23,554597,217612,192184,1.1323,7174,.0344,2548.5589,239,1413332
2026-07-24,546903,215702,185305,1.164,7124,.0345,2535.4563,226,1271043
2026-07-25,555886,212005,184306,1.1503,7134,.0353,2622.0419,240,1340149
2026-07-26,626832,250746,222440,1.1273,8409,.0352,2499.8684,288,1630039
2026-07-27,563922,227047,198767,1.1423,6805,.0316,2483.7236,201,1156398
2026-07-28,558399,212271,186662,1.1372,6899,.0335,2630.5949,225,1299108
2026-07-29,566293,216040,192847,1.1203,7084,.0336,2621.2414,227,1220274""".strip().split('\n'):
    v=row.split(','); MA[v[0]]=dict(cost=float(v[1]),imp=int(v[2]),reach=int(v[3]),freq=float(v[4]),
        clk=int(v[5]),ctr=float(v[6]),cpm=float(v[7]),pur=int(v[8]),val=float(v[9]))
# --- Shopify セッション・ファネル日次（実測）
FN={}
for row in """2026-07-02,6495,441,375,197|2026-07-03,6601,436,388,201|2026-07-04,6858,465,411,221
2026-07-05,8866,601,536,288|2026-07-06,6323,424,371,176|2026-07-07,5630,360,328,160
2026-07-08,5745,380,341,166|2026-07-09,5778,399,358,171|2026-07-10,6017,422,369,212
2026-07-11,6402,463,422,225|2026-07-12,7414,579,508,286|2026-07-13,5954,412,378,192
2026-07-14,6030,463,410,201|2026-07-15,5717,463,411,213|2026-07-16,6170,444,412,192
2026-07-17,6050,441,397,208|2026-07-18,7282,482,431,226|2026-07-19,7229,466,413,216
2026-07-20,7983,548,492,259|2026-07-21,7718,497,447,231|2026-07-22,8162,613,531,279
2026-07-23,7528,531,466,241|2026-07-24,7432,496,458,228|2026-07-25,7422,506,465,234
2026-07-26,8583,591,527,281|2026-07-27,7030,432,377,199|2026-07-28,7182,510,448,222
2026-07-29,7478,509,432,221""".replace('\n','|').split('|'):
    v=row.strip().split(','); FN[v[0]]=dict(ses=int(v[1]),cart=int(v[2]),chk=int(v[3]),cmp=int(v[4]))
# --- Shopify 注文・数量日次（実測）
OR={}
for row in """2026-07-02,199,261,5980|2026-07-03,213,300,18924|2026-07-04,228,316,15944|2026-07-05,294,382,16129
2026-07-06,181,234,0|2026-07-07,160,215,10149|2026-07-08,168,221,22109|2026-07-09,184,246,0
2026-07-10,216,296,0|2026-07-11,229,294,18940|2026-07-12,293,372,15744|2026-07-13,194,268,0
2026-07-14,214,279,6980|2026-07-15,224,302,3980|2026-07-16,198,271,8715|2026-07-17,217,281,14894
2026-07-18,235,307,6089|2026-07-19,227,287,0|2026-07-20,264,360,3980|2026-07-21,235,316,0
2026-07-22,286,380,9960|2026-07-23,250,332,8964|2026-07-24,233,307,0|2026-07-25,244,312,4980
2026-07-26,288,371,10103|2026-07-27,205,270,0|2026-07-28,228,290,9960|2026-07-29,222,269,5980""".replace('\n','|').split('|'):
    v=row.strip().split(','); OR[v[0]]=dict(ord=int(v[1]),items=int(v[2]),ret=int(v[3]))

ALLD=sorted(MA)
WINS=[('W1 7/02-08',ALLD[0:7]),('W2 7/09-15',ALLD[7:14]),('W3 7/16-22',ALLD[14:21]),('W4 7/23-29',ALLD[21:28])]
for l,ds in WINS: assert len(ds)==7 and sorted({wd(d) for d in ds})==sorted(WD),(l,ds)
def sal(days,n=None):
    if n: return sum(S[n][d][0]-S[n][d][1] for d in days if d in S[n])
    return sum(v[d][0]-v[d][1] for v in S.values() for d in days if d in v)
def gr(days,n=None):
    if n: return sum(S[n][d][0] for d in days if d in S[n])
    return sum(v[d][0] for v in S.values() for d in days if d in v)
def dsc(days): return sum(v[d][1] for v in S.values() for d in days if d in v)
def cst(days):
    t=0
    for n,v in S.items():
        if n=='' or n not in PRICE: continue
        g=sum(v[d][0] for d in days if d in v)
        t+=round(g/PRICE[n])*COST.get(n,0)
    return t
def ad(days,n=None):
    if n: return sum(AD[MAP.get(n,n)].get(d,0) for d in days)
    return sum(MA[d]['cost'] for d in days)
def m(days,k): return sum(MA[d][k] for d in days)
def f(days,k): return sum(FN[d][k] for d in days)
def o(days,k): return sum(OR[d][k] for d in days)

print('='*100)
print('【A】全店の推移（4窓・各7日・曜日構成は完全一致。W3に海の日7/20を含む）')
print('='*100)
hdr=['指標']+[l for l,_ in WINS]+['W1→W4']
rows=[]
def add(lbl,vals,fmt='{:,.0f}',pct=True):
    ch=(vals[-1]/vals[0]-1)*100 if vals[0] else 0
    rows.append([lbl]+[fmt.format(v) for v in vals]+[f'{ch:+.1f}%' if pct else '—'])
SAL=[sal(ds) for _,ds in WINS]; CST=[cst(ds) for _,ds in WINS]; ADC=[ad(ds) for _,ds in WINS]
PRF=[SAL[i]-CST[i]-ADC[i] for i in range(4)]
add('売上(gross−値引)',SAL); add('原価',CST); add('広告費(Metaアカウント)',ADC); add('利益',PRF)
rows.append(['利益率']+[f'{PRF[i]/SAL[i]*100:.1f}%' for i in range(4)]+[f'{(PRF[3]/SAL[3]-PRF[0]/SAL[0])*100:+.1f}pt'])
rows.append(['原価率']+[f'{CST[i]/SAL[i]*100:.1f}%' for i in range(4)]+[f'{(CST[3]/SAL[3]-CST[0]/SAL[0])*100:+.1f}pt'])
rows.append(['広告費率']+[f'{ADC[i]/SAL[i]*100:.1f}%' for i in range(4)]+[f'{(ADC[3]/SAL[3]-ADC[0]/SAL[0])*100:+.1f}pt'])
rows.append(['MER']+[f'{SAL[i]/ADC[i]:.3f}' for i in range(4)]+[f'{(SAL[3]/ADC[3])/(SAL[0]/ADC[0])*100-100:+.1f}%'])
w=[max(len(str(r[i])) for r in [hdr]+rows) for i in range(len(hdr))]
for r in [hdr]+rows: print('  '+' | '.join(str(x).rjust(w[i]) for i,x in enumerate(r)))
print(f'\n  検算: W4(7/23-29)の原価 {CST[3]:,}円 ／ 7/30レポートの実測値 2,846,704円 → 差 {CST[3]-2846704:+,}円')
print(f'  検算: W4の売上 {SAL[3]:,}円 ／ レポート 9,465,870円 → 差 {SAL[3]-9465870:+,}円')
print(f'  検算: W4の広告費 {ADC[3]:,.0f}円 ／ レポート 3,972,458円 → 差 {ADC[3]-3972458:+,.0f}円')

print()
print('='*100)
print('【B】利益率 −8.7pt の内訳（利益率 = 1 − 原価率 − 広告費率 の恒等式で完全分解）')
print('='*100)
d_c=(CST[3]/SAL[3]-CST[0]/SAL[0])*100; d_a=(ADC[3]/SAL[3]-ADC[0]/SAL[0])*100
print(f'  広告費率の上昇  {d_a:+.1f}pt  → 悪化の {d_a/(d_a+d_c)*100:.0f}%')
print(f'  原価率の上昇    {d_c:+.1f}pt  → 悪化の {d_c/(d_a+d_c)*100:.0f}%')
print(f'  合計          {-(d_a+d_c):+.1f}pt（利益率の変化と一致）')

print()
print('='*100)
print('【C】MER −15.1% の3因子分解  MER = 1000 × CTR × (売上/クリック) ÷ CPM')
print('='*100)
print('  ※ CTR・CPMはMeta実測、売上/クリックはShopify実売÷Metaアウトバウンドクリック。恒等式なので誤差なく分解できる')
FAC=[]
for l,ds in WINS:
    imp=m(ds,'imp'); clk=m(ds,'clk'); c=ad(ds); s=sal(ds)
    ctr=clk/imp; cpm=c/imp*1000; rpc=s/clk
    FAC.append((l,ctr,rpc,cpm,1000*ctr*rpc/cpm,imp,clk))
print(f"  {'窓':<12}{'CTR':>8}{'売上/クリック':>13}{'CPM':>9}{'インプ':>10}{'クリック':>9}{'MER(再計算)':>12}")
for l,ctr,rpc,cpm,mer,imp,clk in FAC:
    print(f'  {l:<12}{ctr*100:7.3f}%{rpc:>12,.0f}円{cpm:>9,.0f}{imp:>10,}{clk:>9,}{mer:>12.3f}')
l0=FAC[0]; l3=FAC[3]
lg=lambda a,b: math.log(b/a)
tot=lg(l0[4],l3[4])
parts=[('CTR',lg(l0[1],l3[1])),('売上/クリック',lg(l0[2],l3[2])),('CPM(逆符号)',-lg(l0[3],l3[3]))]
print(f'\n  W1→W4 の寄与（対数分解・合計がMER変化と一致）')
for nm,v in parts:
    print(f'    {nm:<14} {v/tot*100:>6.0f}%   （実数変化 {(math.exp(v)-1)*100 if nm!="CPM(逆符号)" else (math.exp(-v)-1)*100:+.1f}%）')
print(f'    合計 {sum(v for _,v in parts)/tot*100:.0f}% / MER変化 {(math.exp(tot)-1)*100:+.1f}%')
print()
print('  「売上/クリック」をさらに分解（Shopify実測）')
print(f"  {'窓':<12}{'注文/クリック':>13}{'客単価(売上/注文)':>18}{'売上/クリック':>13}")
for l,ds in WINS:
    clk=m(ds,'clk'); od=o(ds,'ord'); s=sal(ds)
    print(f'  {l:<12}{od/clk*100:12.2f}%{s/od:>17,.0f}円{s/clk:>12,.0f}円')

print()
print('='*100)
print('【D】Shopifyファネル（どこで落ちたか・実測）')
print('='*100)
print(f"  {'窓':<12}{'セッション':>10}{'カート投入率':>13}{'→レジ到達':>11}{'→購入完了':>11}{'ｾｯｼｮﾝ→注文':>12}{'ｸﾘｯｸ→ｾｯｼｮﾝ':>13}")
for l,ds in WINS:
    ses=f(ds,'ses'); ca=f(ds,'cart'); ck=f(ds,'chk'); cp=f(ds,'cmp'); clk=m(ds,'clk')
    print(f'  {l:<12}{ses:>10,}{ca/ses*100:12.2f}%{ck/ca*100:10.1f}%{cp/ck*100:10.1f}%{cp/ses*100:11.2f}%{ses/clk:>12.2f}')

print()
print('='*100)
print('【E】客単価・セット率・返品・優先配送（実測）')
print('='*100)
print(f"  {'窓':<12}{'注文数':>8}{'点数/注文':>10}{'値引率':>9}{'客単価':>10}{'返品':>10}{'優先配送率':>11}")
for l,ds in WINS:
    od=o(ds,'ord'); it=o(ds,'items'); g=gr(ds); dc=dsc(ds); s=sal(ds); rt=o(ds,'ret')
    pr=round(gr(ds,'優先配送')/536) if '優先配送' in S else 0
    print(f'  {l:<12}{od:>8,}{it/od:>10.3f}{dc/g*100:8.2f}%{s/od:>9,.0f}円{rt:>10,}{pr/od*100:>10.2f}%')

print()
print('='*100)
print('【F】商品別のMER寄与分解（W3 7/16-22 → W4 7/23-29。広告費ウェイト付き）')
print('='*100)
P1D=WINS[2][1]; P2D=WINS[3][1]
mer1=SAL[2]/ADC[2]; mer2=SAL[3]/ADC[3]
rec=[]
for n in PRICE:
    a1=ad(P1D,n); a2=ad(P2D,n)
    if a1<20000 and a2<20000: continue
    s1=sal(P1D,n); s2=sal(P2D,n)
    m1=s1/a1 if a1 else 0; m2=s2/a2 if a2 else 0
    # 寄与 = (この商品のMER変化) × (W4での広告費シェア) を近似せず、全店MERの差分を厳密に配賦
    contrib=(s2-s1)/ADC[3] - SAL[2]/ADC[2]*(a2-a1)/ADC[3]
    b1=sum(BUD[MAP.get(n,n)].get(d,0) for d in P1D); b2=sum(BUD[MAP.get(n,n)].get(d,0) for d in P2D)
    rec.append((n,a1,a2,m1,m2,contrib,b1,b2))
rec.sort(key=lambda x:x[5])
print(f"  {'商品':<22}{'広告費W3':>10}{'広告費W4':>10}{'Δ広告費':>9}{'MER W3':>8}{'MER W4':>8}{'ΔMER':>7}{'全店MERへの寄与':>15}{'日予算':>14}")
for n,a1,a2,m1,m2,c,b1,b2 in rec:
    bd=f'{b1//7:,}→{b2//7:,}' if b1 and b2 else '—'
    print(f'  {n:<22}{a1:>10,.0f}{a2:>10,.0f}{a2-a1:>+9,.0f}{m1:>8.2f}{m2:>8.2f}{m2-m1:>+7.2f}{c:>+15.3f}   {bd}')
print(f'  {"合計":<22}{ADC[2]:>10,.0f}{ADC[3]:>10,.0f}{ADC[3]-ADC[2]:>+9,.0f}{mer1:>8.3f}{mer2:>8.3f}{mer2-mer1:>+7.3f}{sum(r[5] for r in rec):>+15.3f}')

print()
print('='*100
      )
print('【F-2】日予算の実測推移（スナップショットは7/18開始。W3は7/18-22の5日平均・W4は7日平均）')
print('='*100)
def bavg(n,days):
    c=MAP.get(n,n); v=[sum(BUD[c][d].values()) if isinstance(BUD[c][d],dict) else BUD[c][d] for d in days if d in BUD[c]]
    return (sum(v)/len(v), len(v)) if v else (0,0)
print(f"  {'商品':<22}{'W3日予算':>10}{'W4日予算':>10}{'変化':>8}   {'W3消化率':>8}{'W4消化率':>8}")
tb1=tb2=0
for n,a1,a2,m1,m2,c,_,_ in rec:
    b1,n1=bavg(n,P1D); b2,n2=bavg(n,P2D)
    if not b1 or not b2: continue
    tb1+=b1; tb2+=b2
    print(f'  {n:<22}{b1:>10,.0f}{b2:>10,.0f}{(b2/b1-1)*100:>+7.0f}%   {a1/7/b1*100:>7.0f}%{a2/7/b2*100:>7.0f}%')
print(f'  {"合計(19商品)":<22}{tb1:>10,.0f}{tb2:>10,.0f}{(tb2/tb1-1)*100:>+7.0f}%')

print()
print('='*100)
print('【G】原価率 +2.4pt の内訳（商品ミックスの変化。W1 7/02-08 → W4 7/23-29）')
print('='*100)
def crate(days,n):
    g=gr(days,n); s=sal(days,n)
    if not s: return None,0,0
    q=round(g/PRICE[n]); return q*COST.get(n,0)/s, s, q*COST.get(n,0)
mix=[]
for n in PRICE:
    r1,s1,c1=crate(P1D:=WINS[0][1],n); r4,s4,c4=crate(WINS[3][1],n)
    if s1<100000 and s4<100000: continue
    mix.append((n,s1,s4,r1,r4,c1,c4))
P1D=WINS[2][1]
mix.sort(key=lambda x:-(x[2]/SAL[3]*(x[4] or 0)-x[1]/SAL[0]*(x[3] or 0)))
print(f"  {'商品':<22}{'W1売上':>10}{'W1構成比':>9}{'W4売上':>10}{'W4構成比':>9}{'原価率':>8}{'原価率への寄与':>14}")
tot=0
for n,s1,s4,r1,r4,c1,c4 in mix:
    ct=(s4/SAL[3]*(r4 or 0)-s1/SAL[0]*(r1 or 0))*100; tot+=ct
    print(f'  {n:<22}{s1:>10,}{s1/SAL[0]*100:8.1f}%{s4:>10,}{s4/SAL[3]*100:8.1f}%{(r4 or 0)*100:7.1f}%{ct:>+13.2f}pt')
print(f'  {"上記合計":<22}{"":>10}{"":>9}{"":>10}{"":>9}{"":>8}{tot:>+13.2f}pt   （全体の原価率変化 {d_c:+.2f}pt）')

print()
print('='*100)
print('【H】海の日(7/20)の影響を除く（月曜を W3・W4 の両方から外して再計算）')
print('='*100)
for lbl,(l3,l4) in [('月曜を除外',(  [d for d in WINS[2][1] if wd(d)!='月'], [d for d in WINS[3][1] if wd(d)!='月']))]:
    s3=sal(l3); s4=sal(l4); a3=ad(l3); a4=ad(l4)
    print(f'  W3(6日) 売上{s3:,} 広告費{a3:,.0f} MER{s3/a3:.3f}  →  W4(6日) 売上{s4:,} 広告費{a4:,.0f} MER{s4/a4:.3f}')
    print(f'  → 売上{(s4/s3-1)*100:+.1f}% 広告費{(a4/a3-1)*100:+.1f}% MER{(s4/a4)/(s3/a3)*100-100:+.1f}%')
print(f'  （7日まるごとの比較では 売上{(SAL[3]/SAL[2]-1)*100:+.1f}% 広告費{(ADC[3]/ADC[2]-1)*100:+.1f}% MER{(SAL[3]/ADC[3])/(SAL[2]/ADC[2])*100-100:+.1f}%）')

print()
print('='*100)
print('【I】予算増加率とMER悪化の関係（W3→W4・広告費2万円以上の商品）')
print('='*100)
xs=[];ys=[]
for n,a1,a2,m1,m2,c,_,_ in rec:
    b1,_=bavg(n,WINS[2][1]); b2,_=bavg(n,WINS[3][1])
    if not b1 or not b2 or not m1: continue
    xs.append((b2/b1-1)*100); ys.append((m2/m1-1)*100)
mx=statistics.mean(xs); my=statistics.mean(ys)
cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/len(xs)
r=cov/(statistics.pstdev(xs)*statistics.pstdev(ys))
slope=cov/statistics.pvariance(xs)
print(f'  n={len(xs)}商品   相関係数 r = {r:+.3f}   回帰係数 = {slope:+.3f}（予算を+10%増やすとMERが{slope*10:+.1f}%）')
print(f'  予算を増やした商品（+10%以上）: MER変化の平均 {statistics.mean([y for x,y in zip(xs,ys) if x>=10]):+.1f}%（{len([x for x in xs if x>=10])}商品）')
oth=[y for x,y in zip(xs,ys) if x<10]
print(f'  それ以外（+10%未満・減額含む）: MER変化の平均 {statistics.mean(oth):+.1f}%（{len(oth)}商品）')

print()
print('='*100)
print('【J】季節性の確認（夏物14商品 vs それ以外）')
print('='*100)
print(f"  {'グループ':<14}{'W1売上':>11}{'W4売上':>11}{'変化':>8}{'W1広告費':>11}{'W4広告費':>11}{'W1 MER':>8}{'W4 MER':>8}")
for lbl,grp in (('夏物',SUMMER),('それ以外',set(PRICE)-SUMMER)):
    s1=sum(sal(WINS[0][1],n) for n in grp); s4=sum(sal(WINS[3][1],n) for n in grp)
    a1=sum(ad(WINS[0][1],n) for n in grp); a4=sum(ad(WINS[3][1],n) for n in grp)
    print(f'  {lbl:<14}{s1:>11,}{s4:>11,}{(s4/s1-1)*100:>+7.1f}%{a1:>11,.0f}{a4:>11,.0f}{s1/a1:>8.2f}{s4/a4:>8.2f}')

print()
print('='*100)
print('【K】CPM上昇は外部要因か自分の拡大か（Meta実測）')
print('='*100)
print(f"  {'窓':<12}{'インプ':>11}{'リーチ':>11}{'頻度':>7}{'CPM':>8}{'消化':>11}{'カタログ広告':>11}")
for l,ds in WINS:
    cat=sum(AD['カタログ全部（テスト）'].get(d,0) for d in ds)
    print(f'  {l:<12}{m(ds,"imp"):>11,}{m(ds,"reach"):>11,}{m(ds,"imp")/m(ds,"reach"):>7.3f}{ad(ds)/m(ds,"imp")*1000:>8,.0f}{ad(ds):>11,.0f}{cat:>11,.0f}')
print('\n  ※ リーチは日次の単純合計（重複あり）。頻度=インプ÷リーチ')

print()
print('='*100)
print('【L】W3→W4 の利益 −540,822円 を式で完全分解（利益 = 売上 − 原価 − 広告費）')
print('='*100)
print(f'  売上の変化    {SAL[3]-SAL[2]:>+12,}円')
print(f'  原価の変化    {-(CST[3]-CST[2]):>+12,}円（原価が減った分は利益にプラス）')
print(f'  広告費の変化   {-(ADC[3]-ADC[2]):>+12,.0f}円')
print(f'  {"合計":<9}{PRF[3]-PRF[2]:>+12,.0f}円  （利益 {PRF[2]:,} → {PRF[3]:,.0f}／{(PRF[3]/PRF[2]-1)*100:+.1f}%）')
print(f'\n  ★ 広告費を +{ADC[3]-ADC[2]:,.0f}円 増やしたのに、売上は {SAL[3]-SAL[2]:+,}円 減った')

print()
print('='*100)
print('【M】主要商品の4窓推移（売上／広告費／MER・実測）')
print('='*100)
TOP=['害虫ブロッカー','4WAY','形状記憶日傘','ナノガラス脱毛パッド','完全遮光・形状記憶','接触冷感UVパーカー',
     '卓上冷感クーラー','偏光・調光サングラス','5WAY腰掛けファン','壁掛けディスペンサー','瞬間冷感ポンチョ','ムダ毛シェーバー']
print(f"  {'商品':<20}"+''.join(f'{l.split()[0]:>22}' for l,_ in WINS))
print(f"  {'':<20}"+''.join(f"{'売上/広告費/MER':>22}" for _ in WINS))
for n in TOP:
    line=f'  {n:<20}'
    for l,ds in WINS:
        s=sal(ds,n); a=ad(ds,n)
        line+=f'{s/1000:>8,.0f}k/{a/1000:>5,.0f}k/{(s/a if a else 0):>5.2f}'
    print(line)

print()
print('='*100)
print('【N】害虫ブロッカーの需要減衰チェック（Meta実測・4窓）')
print('='*100)
GW={'W2 7/09-15':(404137,167443,149818,1.1176,6021,.0386,2413.5795,208),
    'W3 7/16-22':(477681,222904,189053,1.1791,5579,.0273,2142.9898,164),
    'W4 7/23-29':(554271,231712,200017,1.1585,6061,.0279,2392.0686,197)}
print(f"  {'窓':<12}{'消化':>9}{'インプ':>9}{'CTR':>7}{'CPM':>7}{'頻度':>6}{'クリック':>8}{'Meta購入':>8}{'CVR':>7}{'CPA':>7}{'販売数':>7}{'売上':>11}{'MER':>6}")
for l,(c,i,rc,fq,ck,ct,cpm,pu) in GW.items():
    ds=dict(WINS)[l]; s=sal(ds,'害虫ブロッカー'); q=round(gr(ds,'害虫ブロッカー')/3980)
    print(f'  {l:<12}{c:>9,}{i:>9,}{ct*100:6.2f}%{cpm:>7,.0f}{fq:>6.2f}{ck:>8,}{pu:>8}{pu/ck*100:6.2f}%{c/pu:>7,.0f}{q:>7}{s:>11,}{s/c:>6.2f}')
ds=WINS[0][1]
print(f"  {'W1 7/02-08':<12}{'（キャンペーン別Metaは未取得）':<28}{'':>26}{round(gr(ds,'害虫ブロッカー')/3980):>7}{sal(ds,'害虫ブロッカー'):>11,}{sal(ds,'害虫ブロッカー')/ad(ds,'害虫ブロッカー'):>6.2f}")
print(f"\n  害虫の販売数: "+' → '.join(f"{round(gr(ds,'害虫ブロッカー')/3980)}個({l.split()[0]})" for l,ds in WINS))
print(f"  害虫の売上構成比: "+' → '.join(f"{sal(ds,'害虫ブロッカー')/SAL[i]*100:.1f}%" for i,(l,ds) in enumerate(WINS)))
