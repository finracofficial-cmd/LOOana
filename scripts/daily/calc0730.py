# -*- coding: utf-8 -*-
import json, sys, collections, statistics
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('d0730.py').read())

# ===== 予算変更の実験（budget-snapshots.csv の日次差分から導出）=====
def budhist(n):
    c=MAP.get(n,n); s=BUDS.get(c,{})
    return {d:s[d] for d in ALLD if d in s}
def diffs(n):
    h=budhist(n); ks=sorted(h); out=[]
    for i in range(1,len(ks)):
        if h[ks[i]]!=h[ks[i-1]]: out.append((ks[i],h[ks[i-1]],h[ks[i]]))
    return out
# 各商品の直近1段の実験を自動抽出（P1=変更前・P2=変更後。祝日除外・最大4日）
EXP={}
for n in list(PRICE)+['壁掛けディスペンサー']:
    if n not in N7 or not A(D7,n): continue
    dd=[x for x in diffs(n) if x[0]<=D1[0]]
    if not dd: continue
    chg,ob,nb=dd[-1]
    p2=[d for d in ALLD if chg<=d<=D1[0] and d not in HOLIDAYS][:4]
    prev=[x[0] for x in dd[:-1]]
    lo=max(prev) if prev else ALLD[0]
    p1=[d for d in ALLD if lo<=d<chg and d not in HOLIDAYS][-4:]
    if len(p1)<2 or len(p2)<2: continue          # 各2日未満は測定しない
    EXP[n]=(p1,p2,chg,ob,nb,'増額' if nb>ob else '減額')
INCA={}; EXPMETA={}
for n,(p1,p2,chg,ob,nb,dirn) in EXP.items():
    s1=sum(N7.get(n,0) and 0 for _ in [0])       # placeholder
    def sal(days): return sum(S[n][d][0]-S[n][d][1] for d in days if d in S[n])
    s1=sal(p1)/len(p1); s2=sal(p2)/len(p2)
    a1=A(p1,n)/len(p1); a2=A(p2,n)/len(p2)
    i1=sum(IDX[wd(d)] for d in p1)/len(p1); i2=sum(IDX[wd(d)] for d in p2)/len(p2)
    o1=sum(STORE[d] for d in p1)/len(p1)-s1; o2=sum(STORE[d] for d in p2)/len(p2)-s2
    EXPMETA[n]={'変更日':chg[5:].replace('-','/'),'旧':ob,'新':nb,'方向':dirn,'Δ広告費/日':round(a2-a1),
                'P1':f'{p1[0][5:]}〜{p1[-1][5:]}','P2':f'{p2[0][5:]}〜{p2[-1][5:]}'}
    if abs(a2-a1)<3000: INCA[n]={}; EXPMETA[n]['判定']='測定不可（Δ広告費<3,000円/日）'; continue
    INCA[n]={'曜日':round((s2*i1/i2-s1)/(a2-a1),2),'全店':round((s2*o1/o2-s1)/(a2-a1),2)}

# ===== 週次診断 W2(7/23-29) vs W1(7/16-22) 実測 =====
# (cost, impressions, link_CTR, CPM, frequency, outbound_clicks, purchases, reach)
W2={'4WAY':(634248,151939,.0422,4174.3594,1.5122,6282,245,100473),
'害虫ブロッカー':(554271,231712,.0279,2392.0686,1.1585,6061,197,200017),
'ナノガラス脱毛パッド':(442005,247875,.0276,1783.177,1.2758,6608,223,194291),
'形状記憶日傘':(406339,165614,.0419,2453.5305,1.0839,6715,199,152794),
'完全遮光・形状記憶':(266298,76424,.0512,3484.4813,1.2167,3665,110,62810),
'接触冷感UVパーカー':(227026,71684,.0446,3167.0387,1.2351,3100,142,58039),
'卓上冷感クーラー':(224198,127831,.036,1753.8625,1.2097,4497,82,105675),
'偏光・調光サングラス':(150527,92726,.023,1623.3527,1.1909,2002,54,77864),
'接触冷感UVアームカバー':(125716,53495,.0229,2350.0514,1.3278,1162,50,40288),
'3WAYサーキュレーター':(109014,30477,.0401,3576.9269,1.231,1187,29,24757),
'5WAY腰掛けファン':(94771,31495,.054,3009.0808,1.2563,1631,51,25070),
'健康サンダル':(91806,26692,.0267,3439.4575,1.3509,689,22,19759),
'瞬間冷感ポンチョ':(90637,17367,.0584,5218.9209,1.3418,964,43,12943),
'ムダ毛シェーバー':(87597,78275,.0168,1119.0929,1.3598,1267,48,57565),
'携帯電動シェーバー':(78603,38505,.0223,2041.3713,1.3786,795,28,27930),
'UV歯ブラシ除菌器':(68413,21342,.0209,3205.5571,1.222,404,15,17465),
'壁掛けディスペンサー':(58278,18880,.028,3086.7585,1.2521,513,10,15079),
'バランスケアスリッパ':(34624,17745,.0212,1951.1975,1.1896,355,10,14917),
'湯上がりガーゼワンピース':(22087,2856,.0721,7733.5434,1.2332,197,3,2316)}
W1={'4WAY':(480695,95388,.052,5039.3655,1.6186,4869,280,58931),
'害虫ブロッカー':(477681,222904,.0273,2142.9898,1.1791,5579,164,189053),
'形状記憶日傘':(421416,186920,.0415,2254.526,1.1728,7555,203,159376),
'ナノガラス脱毛パッド':(355067,214095,.0288,1658.4554,1.1215,5977,200,190894),
'完全遮光・形状記憶':(221093,65887,.0559,3355.6392,1.214,3413,112,54273),
'接触冷感UVパーカー':(191830,75373,.0395,2545.0758,1.2928,2893,107,58301),
'偏光・調光サングラス':(154400,102348,.0237,1508.5786,1.1665,2231,66,87742),
'卓上冷感クーラー':(150102,111711,.0371,1343.6636,1.2684,4047,87,88075),
'接触冷感UVアームカバー':(119013,44759,.0246,2658.9736,1.3445,1034,45,33291),
'壁掛けディスペンサー':(103523,30273,.0331,3419.6479,1.2504,981,16,24211),
'ムダ毛シェーバー':(99606,64698,.0164,1539.553,1.3858,993,35,46685),
'UV歯ブラシ除菌器':(90380,42453,.0178,2128.9426,1.136,696,14,37371),
'健康サンダル':(90116,33348,.0237,2702.291,1.3206,775,23,25253),
'瞬間冷感ポンチョ':(89817,20766,.0555,4325.195,1.2971,1089,22,16010),
'3WAYサーキュレーター':(84808,28499,.0419,2975.8237,1.2879,1167,36,22129),
'携帯電動シェーバー':(81874,28716,.0352,2851.1631,1.3008,923,29,22075),
'湯上がりガーゼワンピース':(68268,11646,.0433,5861.9268,1.252,474,12,9302),
'バランスケアスリッパ':(66681,29777,.0202,2239.3458,1.279,579,21,23281),
'5WAY腰掛けファン':(39893,14047,.0478,2839.9658,1.1607,638,31,12102)}
CVR={n:W2[n][6]/W2[n][5] for n in W2}
RPC={n:N7[n]/W2[n][5] for n in W2 if n in N7}
CVR_RANK={n:i+1 for i,n in enumerate(sorted(CVR,key=lambda k:-CVR[k]))}
RPC_RANK={n:i+1 for i,n in enumerate(sorted(RPC,key=lambda k:-RPC[k]))}
CVR_MED=statistics.median(CVR.values()); RPC_MED=statistics.median(RPC.values()); NP=len(CVR)
DIAG={}
for n in W2:
    if n not in W1 or W1[n][0]<20000: DIAG[n]=([],[]); continue
    c2,i2,ct2,cpm2,f2,oc2,p2_,r2=W2[n]; c1,i1,ct1,cpm1,f1,oc1,p1_,r1=W1[n]
    cv2,cv1=p2_/oc2,p1_/oc1; cpa2,cpa1=(c2/p2_ if p2_ else 0),(c1/p1_ if p1_ else 0)
    dct,dcv,dcpm=(ct2-ct1)/ct1,(cv2-cv1)/cv1,(cpm2-cpm1)/cpm1
    dcpa=(cpa2-cpa1)/cpa1 if cpa1 else 0
    r,ev=[],[]
    expand = dcpa>=0.15 and i2/i1>=1.30 and abs(f2/f1-1)<=0.10
    if expand:
        r.append('D1a 配信面の拡大（予算増が原因・CRでは直らない）')
        ev.append(f'CPA{dcpa*100:+.0f}% / インプ{(i2/i1-1)*100:+.0f}%・リーチ{(r2/r1-1)*100:+.0f}%・頻度{(f2/f1-1)*100:+.0f}%・CPM{(cpm2/cpm1-1)*100:+.0f}%・CTR{dct*100:+.0f}%')
    if dct<=-0.15 and not expand:
        r.append('D1 素材疲弊'); ev.append(f'CTR {ct1*100:.2f}%→{ct2*100:.2f}% ({dct*100:+.0f}%)')
    if f2>2.5: r.append('D2 頻度過多'); ev.append(f'頻度 {f2:.2f}')
    if dcv<=-0.15 and CVR_RANK[n]>=NP-4 and RPC_RANK.get(n,0)>=NP-4:
        r.append('D3 LP/オファー'); ev.append(f'CVR {cv1*100:.1f}%→{cv2*100:.1f}% ({dcv*100:+.0f}%)・自店CVR{CVR_RANK[n]}位/{NP}・売上/クリック{RPC[n]:,.0f}円({RPC_RANK[n]}位)')
    if dcpm>=0.15: r.append('D4 CPM上昇'); ev.append(f'CPM {cpm1:,.0f}→{cpm2:,.0f} ({dcpm*100:+.0f}%)')
    if not r and dcpa>=0.15: r.append('D5 需要減衰'); ev.append(f'CTR/CVR/CPM横ばいでCPAのみ {dcpa*100:+.0f}%')
    DIAG[n]=(r,ev)

# ===== P-1 ポートフォリオ・ガード（7日窓の全店MER・2週連続−5%で増額凍結）=====
def win(a,b): return ALLD[a:b]
WINS=[('7/02-08',ALLD[3:10]),('7/09-15',ALLD[10:17]),('7/16-22',ALLD[17:24]),('7/23-29',ALLD[24:31])]
ACCTD={d: sum(AD[c].get(d,0) for c in AD) for d in ALLD}
MERW=[(l,sum(STORE[d] for d in ds)/sum(ACCTD[d] for d in ds)) for l,ds in WINS]
_ch=[(MERW[i+1][1]-MERW[i][1])/MERW[i][1] for i in range(len(MERW)-1)]
# P-1（2026-07-30ユーザー承認で改定）: ①2週連続−5%以上 または ②単週−8%以上 で発動
P1_A=_ch[-1]<=-0.05 and _ch[-2]<=-0.05
P1_B=_ch[-1]<=-0.08
P1GUARD=P1_A or P1_B
P1REASON=(('全店の週次MERが2週連続で−5%以上（%+.1f%%→%+.1f%%）'%(_ch[-2]*100,_ch[-1]*100)) if P1_A else '') \
        + (('' if not P1_A else ' かつ ')+('全店の週次MERが単週で−8%%以上（%+.1f%%）'%(_ch[-1]*100)) if P1_B else '')
# 曜日を揃えた比較（月曜を両週から外す）
def merx(ds,skip):
    d2=[d for d in ds if wd(d)!=skip]
    return sum(STORE[d] for d in d2)/sum(ACCTD[d] for d in d2)
MERW_EXMON=[(l,merx(ds,'月')) for l,ds in WINS[-2:]]
