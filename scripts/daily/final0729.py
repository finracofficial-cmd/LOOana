# -*- coding: utf-8 -*-
import json, sys, collections, statistics, csv
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('calc0729.py').read())

# ===== 現在の日予算（2026-07-29 時点・Meta実測） =====
# パーカーは7/28に28,000へ落としたが誤指示につき7/29に34,000へ復元（Meta APIで daily_budget=340 を確認）
BUD={'4WAY':85000,'害虫ブロッカー':85000,'ナノガラス脱毛パッド':68000,'形状記憶日傘':60000,'完全遮光・形状記憶':34000,
'接触冷感UVパーカー':34000,'卓上冷感クーラー':30000,'偏光・調光サングラス':22000,'接触冷感UVアームカバー':17000,
'5WAY腰掛けファン':16250,'3WAYサーキュレーター':16000,'ムダ毛シェーバー':13000,'健康サンダル':13000,
'瞬間冷感ポンチョ':13000,'携帯電動シェーバー':11000,'UV歯ブラシ除菌器':10000,'壁掛けディスペンサー':6000,
'バランスケアスリッパ':5000,'湯上がりガーゼワンピース':0}
CATBUD=30000

# 消化率: 直近2日(7/27,7/28)。ただし予算が7/26以降据え置きの広告セットのみ評価（SKILL規定）
SNAP=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv',encoding='utf-8')):
    SNAP[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])
def util(n):
    cn=MAP.get(n,n); s=SNAP.get(cn,{})
    v=[s.get('2026-07-%02d'%d) for d in (26,27,28)]
    if not BUD.get(n) or None in v or len(set(v))!=1: return ''      # 変更直後は評価しない
    b=v[0]; return round((A(['2026-07-27'],n)+A(['2026-07-28'],n))/(b*2),3)
UTIL={n:util(n) for n in BUD}

# ===== 本日(7/29)の判定日と、宣言済みの合格基準 =====
TODAY={'害虫ブロッカー','ナノガラス脱毛パッド','偏光・調光サングラス'}
PREV={'害虫ブロッカー':73000,'ナノガラス脱毛パッド':60000}
NEXT={'UV歯ブラシ除菌器':'7/30','5WAY腰掛けファン':'7/31','4WAY':'7/31','完全遮光・形状記憶':'7/31',
'卓上冷感クーラー':'7/31','接触冷感UVパーカー':'7/31','瞬間冷感ポンチョ':'8/1','ムダ毛シェーバー':'8/3',
'壁掛けディスペンサー':'8/4','接触冷感UVアームカバー':'8/5','携帯電動シェーバー':'8/5',
'形状記憶日傘':'なし(健全)','健康サンダル':'なし(健全)','バランスケアスリッパ':'なし(健全)',
'3WAYサーキュレーター':'なし(据置確定)'}
CYCLE2={'壁掛けディスペンサー','UV歯ブラシ除菌器'}
SEASON={'卓上冷感クーラー':5,'4WAY':5,'5WAY腰掛けファン':5,'3WAYサーキュレーター':5,'瞬間冷却ハンディファン':5,
'接触冷感UVパーカー':6,'接触冷感UVアームカバー':6,'瞬間冷感ポンチョ':6,'完全遮光・接触冷感UVハット':6,
'形状記憶日傘':7,'完全遮光・形状記憶':7,'偏光・調光サングラス':7,'害虫ブロッカー':9}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'ムダ毛シェーバー':6980,
'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980}
SINGLE_CR={'4WAY':'4WAY（85,000円）は配信CR1本'}
NOREDEPLOY='転用先の増分MERが実測で目標超えなのはナノガラスのみ。ナノガラスは本日増額するため二重に充てない'

def adopt(n,br,tgt):
    """曜日補正と全店補正が同じゾーン（<分岐／分岐〜目標／≥目標）のときのみ採用する"""
    ia=INCA.get(n,{})
    if len(ia)<2 or br=='' or tgt=='': return None,ia,False
    z=lambda v: 0 if v<br else (1 if v<tgt else 2)
    if z(ia['曜日'])!=z(ia['全店']): return None,ia,True      # 測定済だが結論が割れる
    return round((ia['曜日']+ia['全店'])/2,2), ia, False

rows=[]; trace=[]
for n in sorted(set(list(S30)+list(S7)), key=lambda k:-S7.get(k,0)):
    full=FULL.get(n,n)
    s7,c7,a7=S7.get(n,0),C7.get(n,0),A(D7,n)
    s3,c3,a3=S3.get(n,0),C3.get(n,0),A(D3,n)
    s1,c1,a1=S1.get(n,0),C1.get(n,0),A(D1,n)
    P7,P3,P1_=s7-c7-a7, s3-c3-a3, s1-c1-a1
    P30=S30.get(n,0)-C30.get(n,0)-AD30.get(n,0)
    cr=c7/s7 if s7 else ''
    tgt=round(1/(1-cr-0.35),2) if (cr!='' and 1-cr-0.35>0) else ''
    mer=round(s7/a7,2) if a7 else ''
    br=round(s7/(s7-c7),2) if (a7 and s7>c7) else ''
    im,ia,split=adopt(n,br,tgt)
    rows.append([full, s7,c7,round(a7),round(P7), round(P7/s7,4) if s7 else '',
        round(cr,4) if cr!='' else '', round(a7/s7,4) if s7 else '',
        s3,c3,round(a3),round(P3), round(P3/s3,4) if s3 else '',
        s1,c1,round(a1),round(P1_), round(P1_/s1,4) if s1 else '',
        round(P30), mer, br, tgt, round(mer-br,2) if (mer!='' and br!='') else '',
        im if im is not None else '',
        round(CVR[n],4) if n in CVR else '', f'{CVR_RANK[n]}位/{NP}' if n in CVR_RANK else '',
        SEASON.get(n,26) if n in S7 else '',
        BUD.get(n,'') if BUD.get(n) else ('停止中' if n=='湯上がりガーゼワンピース' else ''), '', '', (ia,split)])

def action(n,r,prop,im,ia,split):
    a=[]; cur=r[27] if isinstance(r[27],int) else 0
    if isinstance(prop,int) and cur and prop!=cur: a.append(f'【広告】{cur:,}→{prop:,}円/日')
    elif n in TODAY: a.append(f'【広告】{cur:,}円/日 据置')
    else: a.append(f'【広告】据置（次回判定 {NEXT.get(n,"—")}）')
    dr,dev=DIAG.get(n,([],[]))
    if dr: a.append('【診断】'+'・'.join(dr)+'（'+' / '.join(dev)+'）')
    if n in SINGLE_CR: a.append(f'【CR】{SINGLE_CR[n]}。予備を1本足しておく（予算・既存CRは触らない）')
    cv,rk=CVR.get(n),CVR_RANK.get(n)
    if cv is not None:
        rp=RPC.get(n,0); rr=RPC_RANK.get(n,0)
        bad = rk>=NP-4 and rr>=NP-4
        a.append(f'【LP】CVR {cv*100:.2f}%＝自店{rk}位/{NP}・売上/クリック{rp:,.0f}円（中央値{RPC_MED:,.0f}円・{rr}位）'
                 + ('→単価も考慮して下位＝商品ページに改善余地' if bad else '→価格帯を考慮すると健全。LPは触らない'))
    if 'D4 CPM上昇' in dr: a.append('【配信】Advantage+全開放と配信面の偏りを確認')
    crr=r[6]; wk=SEASON.get(n,26)
    if isinstance(crr,float) and crr>0.33:
        p_,c_=PRICE.get(n),COST.get(n)
        if p_ and c_:
            y=1-(p_-c_)/(p_+1000-c_)
            a.append((f'【原価】原価率{crr*100:.1f}%>33%。通年なのでCJ数量交渉が有効' if wk>=8
                      else f'【価格】原価率{crr*100:.1f}%>33%。残{wk}週で原価交渉は間に合わない→値上げのみ')
                     + f'／+1,000円で数量−{y*100:.1f}%まで許容')
    if isinstance(r[7],float) and r[7]>0.40: a.append('【広告費率】40%超（率のために黒字は削らない）')
    if ia:
        tail=('（曜日・全店の2手法が一致→採用）' if im is not None else
              ('（2手法が分岐〜目標の帯をまたぐ→増額は見送り、次回判定へ）' if split else '（2手法で結論が割れる→判定保留）'))
        a.append('【増分MER実測】'+' / '.join(f'{k}{v:+.2f}' for k,v in ia.items())+tail)
    return ' ／ '.join(a)

# S2b（機会費用）: 偏光・調光サングラスの枠をナノガラスへ回すか
SANG_S2B=False   # ナノガラスは本日自ら増額するため、同じ枠を二重に充てない（下のNOREDEPLOY）

rows2=[]
for r in rows:
    ia,split=r.pop(); n=REVF.get(r[0],r[0])
    if not r[19]:
        r[28]='📦広告なし'; r[29]='広告費ゼロ。利益=売上−原価'; r[27]='—'; rows2.append(r); continue
    im=r[23] if r[23]!='' else None
    lo=min(ia.values()) if ia else None; hi=max(ia.values()) if ia else None
    upd=U7.get(n,0)/7; cur=r[27] if isinstance(r[27],int) else 0
    p={'判定日':n in TODAY,'次回判定日':NEXT.get(n,'未設定'),'日販':upd,'利益7':r[4],'MER':r[19],
       '目標MER':r[21],'分岐':r[20],'余裕':r[22],'消化率':UTIL.get(n) or 0,'増分MER':im,
       '増分MER下限':lo,'増分MER上限':hi,'増分MER両論':split,'変更方向':EXPMETA.get(n,{}).get('方向','増額'),
       '予算':cur,'元予算':PREV.get(n),'赤字比率':abs((r[4]/7)/cur) if cur else 0,'2巡目':n in CYCLE2,
       '転用が有利':False,'転用不可理由':NOREDEPLOY,'転用利益':0,'P1凍結':P1GUARD}
    path,concl,prop=flow.judge(p)
    if n=='湯上がりガーゼワンピース':
        path,concl,prop='S-1:7/26に停止済み。以後は判定対象外','⏹ 停止済み',0
        r[28]=concl; r[29]='【広告】停止中（0円/日）。再開は8月の秋物枠選定とあわせて検討'; rows2.append(r); continue
    r[28]=concl; r[29]=action(n,r,prop,im,ia,split); rows2.append(r)
    trace.append([r[0],round(upd,1),r[4],r[19],r[21],r[20],r[22],UTIL.get(n) or 0,
                  im if im is not None else ('割れ %.2f/%.2f'%(lo,hi) if split else '未測定/保留'),
                  '○' if n in TODAY else NEXT.get(n,''), cur,prop,concl,path])

# ===== 全体サマリー =====
FEE=0.0349
def blk(days,S,C,AD30_=None,cat=0):
    g=sum(STORE[d] for d in days)                 # 全店 gross−値引（直接取得）
    cost=sum(C.values()); ad=sum(A(days,n) for n in S)+cat
    pr=g-cost-ad
    return dict(日数=len(days),売上=g,原価=cost,広告費=round(ad),利益=round(pr),
                利益率=pr/g, 手数料=round(g*FEE), 手数料後利益=round(pr-g*FEE), 手数料後利益率=(pr-g*FEE)/g)
SUM={'前日(7/28)':blk(D1,S1,C1,cat=CAT1),'直近3日(7/26-28)':blk(D3,S3,C3,cat=CAT3),
     'ç7日(7/22-28)':blk(D7,S7,C7,cat=CAT7)}
# 30日は日別広告費を持たないためキャンペーン別実測合計を使う
g30=sum(STORE[d] for d,_,_,_ in DAILY); c30=sum(C30.values()); a30=sum(AD30.values())+CAT30
SUM['30日(6/29-7/28)']=dict(日数=30,売上=g30,原価=c30,広告費=a30,利益=g30-c30-a30,利益率=(g30-c30-a30)/g30,
    手数料=round(g30*FEE),手数料後利益=round(g30-c30-a30-g30*FEE),手数料後利益率=(g30-c30-a30-g30*FEE)/g30)
SUM['7日(7/22-28)']=SUM.pop('ç7日(7/22-28)')

# ===== 7/18からの累積（毎回ゼロから積み直す。アキュムレータ・ファイルは使わない） =====
CUMD=['2026-07-%02d'%d for d in range(18,29)]
UCUM={'4WAY':629,'害虫ブロッカー':561,'形状記憶日傘':435,'ナノガラス脱毛パッド':388,'完全遮光・形状記憶':221,
'卓上冷感クーラー':179,'接触冷感UVパーカー':249,'5WAY腰掛けファン':115,'偏光・調光サングラス':119,
'3WAYサーキュレーター':77,'ムダ毛シェーバー':65,'接触冷感UVアームカバー':94,'瞬間冷感ポンチョ':84,
'健康サンダル':52,'UV歯ブラシ除菌器':28,'携帯電動シェーバー':48,'壁掛けディスペンサー':19,
'バランスケアスリッパ':28,'湯上がりガーゼワンピース':17,'瞬間冷却ハンディファン':10,'優先配送':109,
'完全遮光・接触冷感UVハット':2,'ネックマッサージャー':1,'リカバリーサンダル':2}
NANO['cum']=(201+59, 92+36); DISP['cum']=(6+5+1, 3+2+1+1)
assert sum(NANO['cum'])==UCUM['ナノガラス脱毛パッド']
assert sum(DISP['cum'])==UCUM['壁掛けディスペンサー']
CCUM=costs(UCUM,'cum')
CUM_SALES=sum(STORE[d] for d in CUMD)          # 全店 gross−値引（直接取得）
CUM_COST=sum(CCUM.values())
CUM_AD=sum(ACCT[d] for d in CUMD)              # Metaアカウント全体の実測消化（カタログ含む）
CUM_PROFIT=CUM_SALES-CUM_COST-CUM_AD
# 検算: 累積は構成日の実測の和であること
assert abs(CUM_SALES-sum(STORE[d] for d in CUMD))<1
assert abs(CUM_AD-sum(ACCT[d] for d in CUMD))<1
CUM={'日数':len(CUMD),'売上':CUM_SALES,'原価':CUM_COST,'広告費':CUM_AD,'利益':CUM_PROFIT,
     '利益率':CUM_PROFIT/CUM_SALES,'手数料':round(CUM_SALES*FEE),
     '手数料後利益':round(CUM_PROFIT-CUM_SALES*FEE),'手数料後利益率':(CUM_PROFIT-CUM_SALES*FEE)/CUM_SALES}

# 当月(7月)の返品累計
RET_M=sum(rt for d,_,_,rt in DAILY if d.startswith('2026-07'))
SALES_M=sum(g-dc for d,g,dc,_ in DAILY if d.startswith('2026-07'))
RET_RATE=RET_M/SALES_M

# 前日の曜日比較
YDAY='2026-07-28'; YWD=wd(YDAY)
YDAY_SALES=STORE[YDAY]
SAMEWD=[g-dc for d,g,dc,_ in DAILY if wd(d)==YWD and d not in HOLIDAYS]
SAMEWD_AVG=sum(SAMEWD)/len(SAMEWD)

# ===== 5e. 収益算定の照合（毎回実施） =====
REC={}
g7_gross=sum(g for d,g,_,_ in DAILY if d in D7)
REC['①Σ商品gross = 全店gross']=(sum(S7.values()), g7_gross, sum(S7.values())-g7_gross)
disc7=sum(dc for d,_,dc,_ in DAILY if d in D7)
prod_profit=sum(S7[n]-C7.get(n,0)-A(D7,n) for n in S7)
REC['②Σ商品利益−全店値引−カタログ広告 = 全体利益']=(round(prod_profit-disc7-CAT7), SUM['7日(7/22-28)']['利益'],
                                       round(prod_profit-disc7-CAT7)-SUM['7日(7/22-28)']['利益'])
REC['③キャンペーン別広告費合計 = アカウント消化(7日)']=(round(sum(A(D7,n) for n in S7)+CAT7),
                                       sum(ACCT[d] for d in D7), round(sum(A(D7,n) for n in S7)+CAT7)-sum(ACCT[d] for d in D7))
# 既知バイアス: 返品分の原価が控除され利益が過大に出る（A案・ユーザー了承済み）
RETBIAS=sum(rt for d,_,_,rt in DAILY if d.startswith('2026-07'))

# ===== 6. 突合サニティチェック（30日・Meta計上売上 ÷ Shopify gross） =====
METAV30={'害虫ブロッカー':5987257,'4WAY':5449861,'形状記憶日傘':4869387,'ナノガラス脱毛パッド':4061022,
'完全遮光・形状記憶':2549467,'接触冷感UVパーカー':2223221,'偏光・調光サングラス':1421725,
'接触冷感UVアームカバー':1019805,'壁掛けディスペンサー':763520,'健康サンダル':732228,'卓上冷感クーラー':1200890,
'携帯電動シェーバー':844354,'3WAYサーキュレーター':832233,'UV歯ブラシ除菌器':875343,'湯上がりガーゼワンピース':556541,
'バランスケアスリッパ':527209,'ムダ毛シェーバー':625316,'瞬間冷感ポンチョ':470425,'5WAY腰掛けファン':514331}
MATCH={n:METAV30[n]/S30[n] for n in METAV30 if S30.get(n)}
MATCH_FLAG={n:v for n,v in MATCH.items() if v>1.05 or v<0.70}

json.dump({'rows':rows2,'trace':trace,'SUM':SUM,'CUM':CUM,'EXPMETA':EXPMETA,'INCA':INCA,
           'REC':REC,'MATCH':MATCH,'MATCH_FLAG':MATCH_FLAG,'RETBIAS':RETBIAS,
           'MERW':MERW,'P1':P1GUARD,'RET':[RET_M,RET_RATE],'IDX':IDX,'UTIL':UTIL,
           'CVR':CVR,'RANK':CVR_RANK,'RPC':RPC,'RPCRANK':RPC_RANK,'MED':[CVR_MED,RPC_MED],
           'DIAG':{k:list(v) for k,v in DIAG.items()},
           'YDAY':{'売上':YDAY_SALES,'曜日':YWD,'同曜日平均':round(SAMEWD_AVG),
                   'vs同曜日':YDAY_SALES/SAMEWD_AVG-1}},
          open('rows0729.json','w'),ensure_ascii=False)

print('=== 全体サマリー（1日あたり） ===')
for k,v in SUM.items():
    n=v['日数']
    print(f"{k:18s} 売上{v['売上']/n:>10,.0f} 原価{v['原価']/n:>9,.0f} 広告{v['広告費']/n:>9,.0f} "
          f"利益{v['利益']/n:>9,.0f} ({v['利益率']*100:>5.1f}%) 手数料後{v['手数料後利益']/n:>9,.0f} ({v['手数料後利益率']*100:>5.1f}%)")
print(f"\n7/18-28累積({CUM['日数']}日) 売上{CUM['売上']:,} 原価{CUM['原価']:,} 広告{CUM['広告費']:,} "
      f"利益{CUM['利益']:,} ({CUM['利益率']*100:.1f}%) 手数料後{CUM['手数料後利益']:,} ({CUM['手数料後利益率']*100:.1f}%)")
print(f"当月返品累計 {RET_M:,}円（返品率 {RET_RATE*100:.2f}%）")
print(f"\n昨日 7/28({YWD}) 売上 {YDAY_SALES:,} / 同曜日平均 {SAMEWD_AVG:,.0f} → {(YDAY_SALES/SAMEWD_AVG-1)*100:+.1f}%")

print(f"\n{'商品':24s}{'7日利益':>10s}{'率':>7s}{'MER':>6s}{'分岐':>6s}{'目標':>6s}{'余裕':>6s}{'消化':>7s}")
for r in rows2:
    if not r[19]: continue
    n=REVF.get(r[0],r[0]); u=UTIL.get(n)
    print(f"{r[0][:22]:24s}{r[4]:>10,}{r[5]*100:>6.1f}%{r[19]:>6.2f}{r[20]:>6.2f}{(r[21] or 0):>6.2f}{r[22]:>6.2f}"
          + (f"{u*100:>6.0f}%" if u!='' else f"{'—':>7s}"))
print('\n=== 判定 ===')
for t in trace:
    mk=' ★変更' if t[10]!=t[11] else ''
    print(f'{t[0][:24]:26s}{t[10]:>8,}→{t[11]:>8,} {t[12]}{mk}')
    if t[9]=='○': print(f'    {t[13]}')

print('\n=== 収益算定の照合 ===')
for k,(a,b,d) in REC.items(): print(f'  {k}: {a:,} vs {b:,} → 差 {d:+,}円')
print(f'  既知バイアス: 返品の原価がCOGSから外れ利益が過大（当月返品 {RETBIAS:,}円）')
print('\n=== 突合（30日 Meta計上売上÷Shopify gross・正常帯75-105%） ===')
print('  逸脱:', MATCH_FLAG if MATCH_FLAG else 'なし')
print('  ', ' '.join(f'{n[:6]}{v*100:.0f}%' for n,v in sorted(MATCH.items(),key=lambda x:x[1])))
print('\n=== 全店週次MER ===')
for i,(lbl,m) in enumerate(MERW):
    print(f'  {lbl}: {m:.3f}' + (f'  ({_ch[i-1]*100:+.1f}%)' if i else ''))
print(f'  P-1（2週連続−5%で増額凍結）= {"発動" if P1GUARD else "未発動"}')
