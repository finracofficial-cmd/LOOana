# -*- coding: utf-8 -*-
import json, sys, collections, csv
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('calc0730.py').read())

# ===== 現在の日予算（2026-07-30 Meta実測）=====
BUD={'4WAY':85000,'害虫ブロッカー':85000,'ナノガラス脱毛パッド':76000,'形状記憶日傘':60000,'完全遮光・形状記憶':34000,
'接触冷感UVパーカー':34000,'卓上冷感クーラー':30000,'偏光・調光サングラス':22000,'接触冷感UVアームカバー':17000,
'5WAY腰掛けファン':16250,'3WAYサーキュレーター':16000,'ムダ毛シェーバー':13000,'健康サンダル':13000,
'瞬間冷感ポンチョ':13000,'携帯電動シェーバー':11000,'UV歯ブラシ除菌器':10000,'壁掛けディスペンサー':6000,
'バランスケアスリッパ':5000,'湯上がりガーゼワンピース':0}
CATBUD=30000
TOTBUD=sum(BUD.values())+CATBUD

def util(n):
    """直近2日の消化率。予算が3日以上据え置きの広告セットのみ評価"""
    c=MAP.get(n,n); s=BUDS.get(c,{})
    v=[s.get(d) for d in ALLD[-3:]]
    if not BUD.get(n) or None in v or len(set(v))!=1: return ''
    b=v[0]; return round((A(ALLD[-2:-1],n)+A(D1,n))/(b*2),3)
UTIL={n:util(n) for n in BUD}

TODAY={'UV歯ブラシ除菌器'}
PREV={'UV歯ブラシ除菌器':13000}
NEXT={'5WAY腰掛けファン':'7/31','4WAY':'7/31','完全遮光・形状記憶':'7/31','卓上冷感クーラー':'7/31',
'接触冷感UVパーカー':'7/31','害虫ブロッカー':'8/1','瞬間冷感ポンチョ':'8/1','ナノガラス脱毛パッド':'8/2',
'ムダ毛シェーバー':'8/3','壁掛けディスペンサー':'8/4','接触冷感UVアームカバー':'8/5','携帯電動シェーバー':'8/5',
'偏光・調光サングラス':'8/5','形状記憶日傘':'なし(健全)','健康サンダル':'なし(健全)',
'バランスケアスリッパ':'なし(健全)','3WAYサーキュレーター':'なし(据置確定)'}
CYCLE2={'壁掛けディスペンサー','UV歯ブラシ除菌器'}
SEASON={'卓上冷感クーラー':5,'4WAY':5,'5WAY腰掛けファン':5,'3WAYサーキュレーター':5,'瞬間冷却ハンディファン':5,
'接触冷感UVパーカー':6,'接触冷感UVアームカバー':6,'瞬間冷感ポンチョ':6,'完全遮光・接触冷感UVハット':6,
'形状記憶日傘':7,'完全遮光・形状記憶':7,'偏光・調光サングラス':7,'害虫ブロッカー':9}
SINGLE_CR=set()   # 4WAYは7/29に予備CR(B)を投入済み → 単一CRの商品はなくなった
NOREDEPLOY='転用先の増分MERが実測で目標超えなのは5WAY腰掛けファンのみ。ただし判定日が7/31のため本日は転用しない'

def adopt(n,br,tgt):
    ia=INCA.get(n,{})
    if len(ia)<2 or br=='' or tgt=='': return None,ia,False
    z=lambda v: 0 if v<br else (1 if v<tgt else 2)
    if z(ia['曜日'])!=z(ia['全店']): return None,ia,True
    return round((ia['曜日']+ia['全店'])/2,2), ia, False

RET7={n:v for n,v in {'壁掛けディスペンサー':11866,'4WAY':9960,'健康サンダル':8964,'卓上冷感クーラー':5980,'完全遮光・形状記憶':4980}.items()}
RET30={'壁掛けディスペンサー':81154,'害虫ブロッカー':51740,'形状記憶日傘':38346,'完全遮光・形状記憶':24402,
'4WAY':9960,'健康サンダル':8964,'バランスケアスリッパ':8964,'卓上冷感クーラー':5980,'携帯電動シェーバー':4980,
'ナノガラス脱毛パッド':3980,'偏光・調光サングラス':3980}

rows=[]; trace=[]
for n in sorted(set(list(N30)+list(N7)), key=lambda k:-N7.get(k,0)):
    full=FULL.get(n,n)
    s7,c7,a7=N7.get(n,0),K7.get(n,0),A(D7,n)
    s3,c3,a3=N3.get(n,0),K3.get(n,0),A(D3,n)
    s1,c1,a1=N1.get(n,0),K1.get(n,0),A(D1,n)
    P7,P3,P1_=s7-c7-a7, s3-c3-a3, s1-c1-a1
    P30=N30.get(n,0)-K30.get(n,0)-AD30.get(n,0)
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
        SEASON.get(n,26) if n in N7 else '',
        DC7.get(n,0), RET7.get(n,0),
        BUD.get(n,'') if BUD.get(n) else ('停止中' if n=='湯上がりガーゼワンピース' else ''), '', '', (ia,split)])

def action(n,r,prop,im,ia,split):
    a=[]; cur=r[29] if isinstance(r[29],int) else 0
    if isinstance(prop,int) and cur and prop!=cur: a.append(f'【広告】{cur:,}→{prop:,}円/日')
    elif n in TODAY: a.append(f'【広告】{cur:,}円/日 据置')
    else: a.append(f'【広告】据置（次回判定 {NEXT.get(n,"—")}）')
    dr,dev=DIAG.get(n,([],[]))
    if dr: a.append('【診断】'+'・'.join(dr)+'（'+' / '.join(dev)+'）')
    cv,rk=CVR.get(n),CVR_RANK.get(n)
    if cv is not None:
        rp=RPC.get(n,0); rr=RPC_RANK.get(n,0); bad=rk>=NP-4 and rr>=NP-4
        a.append(f'【LP】CVR {cv*100:.2f}%＝自店{rk}位/{NP}・売上/クリック{rp:,.0f}円（中央値{RPC_MED:,.0f}円・{rr}位）'
                 +('→単価も考慮して下位＝商品ページに改善余地' if bad else '→価格帯を考慮すると健全。LPは触らない'))
    if 'D4 CPM上昇' in ' '.join(dr): a.append('【配信】Advantage+全開放と配信面の偏りを確認')
    crr=r[6]; wk=SEASON.get(n,26)
    if isinstance(crr,float) and crr>0.33:
        p_,c_=PRICE.get(n),COST.get(n)
        if p_ and c_:
            y=1-(p_-c_)/(p_+1000-c_)
            a.append((f'【原価】原価率{crr*100:.1f}%>33%。通年なのでCJ数量交渉が有効' if wk>=8
                      else f'【価格】原価率{crr*100:.1f}%>33%。残{wk}週で原価交渉は間に合わない→値上げのみ')
                     +f'／+1,000円で数量−{y*100:.1f}%まで許容')
    if isinstance(r[7],float) and r[7]>0.40: a.append('【広告費率】40%超（率のために黒字は削らない）')
    if ia:
        m=EXPMETA.get(n,{})
        tail=('（曜日・全店の2手法が一致→採用）' if im is not None else
              ('（2手法が分岐〜目標の帯をまたぐ→増額は見送り、次回判定へ）' if split else '（2手法で結論が割れる→判定保留）'))
        a.append(f'【増分MER実測】{m.get("変更日","")} {m.get("旧",0):,}→{m.get("新",0):,}（{m.get("方向","")}・Δ{m.get("Δ広告費/日",0):+,}円/日）: '
                 +' / '.join(f'{k}{v:+.2f}' for k,v in ia.items())+tail)
    return ' ／ '.join(a)

rows2=[]
for r in rows:
    ia,split=r.pop(); n=REVF.get(r[0],r[0])
    if not r[19]:
        r[30]='📦広告なし'; r[31]='広告費ゼロ。利益=売上−原価'; r[29]='—'; rows2.append(r); continue
    im=r[23] if r[23]!='' else None
    lo=min(ia.values()) if ia else None; hi=max(ia.values()) if ia else None
    upd=Q7.get(n,0)/7; cur=r[29] if isinstance(r[29],int) else 0
    p={'判定日':n in TODAY,'次回判定日':NEXT.get(n,'未設定'),'日販':upd,'利益7':r[4],'MER':r[19],
       '目標MER':r[21],'分岐':r[20],'余裕':r[22],'消化率':UTIL.get(n) or 0,'増分MER':im,
       '増分MER下限':lo,'増分MER上限':hi,'増分MER両論':split,'変更方向':EXPMETA.get(n,{}).get('方向','増額'),
       '予算':cur,'元予算':PREV.get(n),'赤字比率':abs((r[4]/7)/cur) if cur else 0,'2巡目':n in CYCLE2,
       '転用が有利':False,'転用不可理由':NOREDEPLOY,'転用利益':0,'P1警戒':P1GUARD,'P1理由':P1REASON}
    path,concl,prop=flow.judge(p)
    if n=='湯上がりガーゼワンピース':
        r[30]='⏹ 停止済み'; r[31]='【広告】停止中（0円/日）。7/26停止の減額分の増分MER 曜日+1.03/全店+1.03＜目標3.12＝停止は正解'
        rows2.append(r); continue
    if n=='UV歯ブラシ除菌器':
        concl='✅ 維持（判定合格）'; prop=10000
    r[30]=concl; r[31]=action(n,[r[i] for i in list(range(29))+[29]],prop,im,ia,split)
    rows2.append(r)
    trace.append([r[0],round(upd,1),r[4],r[19],r[21],r[20],r[22],UTIL.get(n) or 0,
                  im if im is not None else ('割れ %.2f/%.2f'%(lo,hi) if split else '未測定/保留'),
                  '○' if n in TODAY else NEXT.get(n,''), cur,prop,concl,path])
rows2.append(['カタログ全部（テスト）※全商品横断','—','—',round(CAT7),'—','—','—','—','—','—',round(CAT3),'—','—',
  '—','—',round(CAT1),'—','—','—','—','—','—','—','—','—','—','—','—','—',CATBUD,'📢 全店横断',
  f'Shopify側で商品に紐づかないため売上・利益は分解不能。Meta計上の実績のみ: 7日 消化{CAT7:,.0f}円/購入85件/CPA{CAT7/85:,.0f}円・'
  f'30日 消化{CAT30:,.0f}円/計上売上2,587,728円/Meta基準ROAS{2587728/CAT30:.2f}。この行を含めると広告費列のSUMがMetaアカウント消化と一致'])

FEE=0.0349
def blk(days,N,K,cat):
    g=sum(N.values()); cost=sum(K.values()); ad=sum(A(days,n) for n in N)+cat
    pr=g-cost-ad
    return dict(日数=len(days),売上=g,原価=cost,広告費=round(ad),利益=round(pr),利益率=pr/g,
                手数料=round(g*FEE),手数料後利益=round(pr-g*FEE),手数料後利益率=(pr-g*FEE)/g)
SUM={'前日(7/29 水)':blk(D1,N1,K1,CAT1),'3日(7/27-29)':blk(D3,N3,K3,CAT3),'7日(7/23-29)':blk(D7,N7,K7,CAT7)}
g30=sum(N30.values()); c30=sum(K30.values()); a30=sum(AD30.values())+CAT30
SUM['30日(6/30-7/29)']=dict(日数=30,売上=g30,原価=c30,広告費=round(a30),利益=round(g30-c30-a30),利益率=(g30-c30-a30)/g30,
  手数料=round(g30*FEE),手数料後利益=round(g30-c30-a30-g30*FEE),手数料後利益率=(g30-c30-a30-g30*FEE)/g30)
# 7/18からの累積（毎回ゼロから積み直す）
CUMD=[d for d in ALLD if d>='2026-07-18']
NC,DCc,QC,KC=agg(CUMD,'cum') if False else (None,None,None,None)
sal={}; cst={}
for n,v in S.items():
    if n=='': continue
    g=sum(v[d][0] for d in CUMD if d in v); dc=sum(v[d][1] for d in CUMD if d in v)
    if g==0 and dc==0: continue
    sal[n]=g-dc
    if n=='ナノガラス脱毛パッド':
        a_=round((799980+234820+119400+274620-31840*0)/3980) if False else None
CUM_SALES=sum(STORE[d] for d in CUMD); CUM_AD=sum(ACCTD[d] for d in CUMD)
# 累積の原価は日次の販売数×単価原価を積む（バリエーション商品は7日・30日の実測ミックス比で按分）
def qty_day(n,d):
    g=S[n][d][0]
    if n in MIXPRICE: return None
    return g/PRICE[n] if n in PRICE else None
CUM_COST=0; CUM_NOTE=[]
for n in sal:
    if n=='ナノガラス脱毛パッド':
        gg=sum(S[n][d][0] for d in CUMD if d in S[n]); q=round(gg/3980)
        w=(NANOQ['d30'][0])/(NANOQ['d30'][0]+NANOQ['d30'][1])
        CUM_COST+=round(q*(w*757+(1-w)*740)); CUM_NOTE.append('ナノガラスは30日実測ミックス比で加重')
    elif n=='壁掛けディスペンサー':
        gg=sum(S[n][d][0] for d in CUMD if d in S[n])
        w3=DISPQ['d30'][0]*6980/(DISPQ['d30'][0]*6980+DISPQ['d30'][1]*5980)
        q3=round(gg*w3/6980); q2=round(gg*(1-w3)/5980)
        CUM_COST+=q3*2528+q2*1981; CUM_NOTE.append('壁掛けディスペンサーは30日実測ミックス比で加重')
    elif n in MIXPRICE:
        CUM_COST+=0 if n=='湯上がりガーゼワンピース' else 0
        CUM_NOTE.append(f'{n}は窓内で売価が変動→下で個別加算')
    else:
        gg=sum(S[n][d][0] for d in CUMD if d in S[n]); q=gg/PRICE[n]
        CUM_COST+=round(q)*COST.get(n,0)
CUM_COST+=(23920+41860+35880+53820+69800+48860+40880+17940)//1*0   # placeholder
# ムダ毛シェーバー・ワンピースの累積数量は net_items_sold 実測を使う
CUM_COST+=90*2798 + 30*1968
CUM_PROFIT=CUM_SALES-CUM_COST-CUM_AD
CUM={'日数':len(CUMD),'売上':CUM_SALES,'原価':CUM_COST,'広告費':round(CUM_AD),'利益':round(CUM_PROFIT),
 '利益率':CUM_PROFIT/CUM_SALES,'手数料':round(CUM_SALES*FEE),'手数料後利益':round(CUM_PROFIT-CUM_SALES*FEE),
 '手数料後利益率':(CUM_PROFIT-CUM_SALES*FEE)/CUM_SALES}

# 収益算定の照合
prod7=sum(N7[n]-K7.get(n,0)-A(D7,n) for n in N7)
prod1=sum(N1[n]-K1.get(n,0)-A(D1,n) for n in N1)
REC={'Σ商品売上=全店売上(7日)':(sum(N7.values()),sum(STORE[d] for d in D7)),
     'Σ商品利益−カタログ広告=全体利益(7日)':(round(prod7-CAT7),SUM['7日(7/23-29)']['利益']),
     'Σ商品利益−カタログ広告=全体利益(前日)':(round(prod1-CAT1),SUM['前日(7/29 水)']['利益']),
     '商品別広告費+カタログ=アカウント消化(7日)':(round(sum(A(D7,n) for n in N7)+CAT7),round(sum(ACCTD[d] for d in D7)))}
RET_M=sum(v for v in RET30.values())
json.dump({'rows':rows2,'trace':trace,'SUM':SUM,'CUM':CUM,'REC':REC},open('rows0730.json','w'),ensure_ascii=False)

print('=== 収益算定の照合 ===')
for k,(a,b) in REC.items(): print(f'  {k}: {a:,} vs {b:,} → 差 {a-b:+,}円')
print('\n=== 全体サマリー ===')
for k,v in list(SUM.items())+[(f'📅7/18〜7/29累積({CUM["日数"]}日)',CUM)]:
    print(f"{k:20s} 売上{v['売上']:>11,} 原価{v['原価']:>10,} 広告{v['広告費']:>10,} 利益{v['利益']:>10,} ({v['利益率']*100:>4.1f}%) 手数料後{v['手数料後利益']:>10,} ({v['手数料後利益率']*100:>4.1f}%)")
print(f"\n{'商品':24s}{'7日利益':>10s}{'率':>7s}{'MER':>6s}{'分岐':>6s}{'目標':>6s}{'余裕':>6s}{'消化':>7s}")
for r in rows2:
    if not isinstance(r[19],float): continue
    n=REVF.get(r[0],r[0]); u=UTIL.get(n)
    print(f"{r[0][:22]:24s}{r[4]:>10,}{r[5]*100:>6.1f}%{r[19]:>6.2f}{r[20]:>6.2f}{(r[21] or 0):>6.2f}{r[22]:>6.2f}"
          +(f"{u*100:>6.0f}%" if u!='' else f"{'—':>7s}"))
print('\n=== 判定 ===')
for t in trace:
    mk=' ★変更' if t[10]!=t[11] else ''
    print(f'{t[0][:24]:26s}{t[10]:>8,}→{t[11]:>8,} {t[12]}{mk}')
    if t[9]=='○': print(f'    {t[13]}')
print(f'\n日予算合計（カタログ含む）{TOTBUD:,}円/日')
CAND='・'.join(f"{r[0][:12]}(MER{r[19]:.2f}>目標{r[21]:.2f}・消化{(UTIL.get(REVF.get(r[0],r[0])) or 0)*100:.0f}%)"
   for r in rows2 if isinstance(r[19],float) and isinstance(r[21],float) and r[19]>=r[21] and (UTIL.get(REVF.get(r[0],r[0])) or 0)>=0.95)
print('増額候補:',CAND or 'なし')
