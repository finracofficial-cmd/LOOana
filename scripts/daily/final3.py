# -*- coding: utf-8 -*-
"""2026-07-29 レポート v3: 商品別売上 = gross − その商品の値引（2026-07-29ユーザー承認）"""
import json, sys, collections, csv
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('v2.py').read())
_f=open('final0729.py').read()
exec(_f.split('rows=[]; trace=[]')[0].split("exec(open('calc0729.py').read())")[1])
exec('def action'+_f.split('def action')[1].split('# S2b（機会費用）')[0])
BUD['ナノガラス脱毛パッド']=76000
TODAY={'害虫ブロッカー','偏光・調光サングラス'}      # ナノガラスは本日の増額を実施済み → 次回判定8/2
NEXT['ナノガラス脱毛パッド']='8/2'

DC3={'害虫ブロッカー':59700,'4WAY':21663,'形状記憶日傘':17430,'ナノガラス脱毛パッド':9154,'接触冷感UVパーカー':7363,
'完全遮光・形状記憶':8964,'卓上冷感クーラー':8372,'5WAY腰掛けファン':12450,'ムダ毛シェーバー':1396,
'偏光・調光サングラス':4975,'3WAYサーキュレーター':5980,'瞬間冷感ポンチョ':6766,'UV歯ブラシ除菌器':1796,
'接触冷感UVアームカバー':1592,'携帯電動シェーバー':0,'健康サンダル':2241,'バランスケアスリッパ':996,
'壁掛けディスペンサー':1196,'湯上がりガーゼワンピース':1196,'優先配送':0,'瞬間冷却ハンディファン':0}
DC30={'害虫ブロッカー':664859,'4WAY':318969,'形状記憶日傘':171561,'ナノガラス脱毛パッド':56516,
'完全遮光・形状記憶':74202,'接触冷感UVパーカー':56914,'偏光・調光サングラス':46964,'卓上冷感クーラー':44551,
'接触冷感UVアームカバー':43780,'3WAYサーキュレーター':43654,'UV歯ブラシ除菌器':14817,'壁掛けディスペンサー':38581,
'健康サンダル':36105,'携帯電動シェーバー':12948,'ムダ毛シェーバー':4984,'湯上がりガーゼワンピース':40889,
'5WAY腰掛けファン':38595,'瞬間冷感ポンチョ':34427,'バランスケアスリッパ':13197,'優先配送':0,
'瞬間冷却ハンディファン':3588,'ナノバブルシャワーヘッド':0,'完全遮光・接触冷感UVハット':0,
'リカバリーサンダル':0,'ネックマッサージャー':0,'姿勢サポートベルト':0,'癒しの指圧マット':0}
# 検算: 商品別値引の合計 = 全店の値引（1円まで一致すること）
for lbl,DC,days in [('7日',DC7,D7),('3日',DC3,D3),('前日',DC1,D1),('30日',DC30,[d for d,_,_,_ in DAILY])]:
    tot=sum(dc for d,_,dc,_ in DAILY if d in days)
    assert sum(DC.values())==tot, (lbl,sum(DC.values()),tot)
    print(f'  値引検算 {lbl}: 商品別合計 {sum(DC.values()):,} = 全店 {tot:,} ✓')

# 売上 = gross − 値引
N7={n:S7[n]-DC7.get(n,0) for n in S7}
N3={n:S3[n]-DC3.get(n,0) for n in S3}
N1={n:S1[n]-DC1.get(n,0) for n in S1}
N30={n:S30[n]-DC30.get(n,0) for n in S30}
for lbl,N,days in [('7日',N7,D7),('3日',N3,D3),('前日',N1,D1),('30日',N30,[d for d,_,_,_ in DAILY])]:
    assert sum(N.values())==sum(STORE[d] for d in days), lbl
    print(f'  売上検算 {lbl}: Σ商品売上 {sum(N.values()):,} = 全店売上 {sum(STORE[d] for d in days):,} ✓')

# 商品×日別の値引き（実測 7/22-28）。増分MERも値引後ベースで測る
DD={
'害虫ブロッカー':[18109,12338,21691,16716,27462,16915,15323],
'ナノガラス脱毛パッド':[796,2587,1592,3383,3383,3383,2388],
'4WAY':[15438,20169,7221,18675,10209,6225,5229],
'形状記憶日傘':[15438,3984,4233,4980,8217,4233,4980],
'完全遮光・形状記憶':[2988,2988,1992,0,2988,2988,2988],
'接触冷感UVパーカー':[2587,796,3184,2388,796,2388,4179],
'卓上冷感クーラー':[3588,8372,4784,0,4784,1196,2392],
'5WAY腰掛けファン':[7470,1992,2241,2988,1992,4233,6225],
'偏光・調光サングラス':[0,796,796,0,796,1592,2587],
'接触冷感UVアームカバー':[1791,1592,796,796,796,0,796],
'3WAYサーキュレーター':[4784,1196,0,0,3588,2392,0],
'瞬間冷感ポンチョ':[796,3582,5373,1791,796,5174,796],
'UV歯ブラシ除菌器':[0,0,0,1796,0,1796,0],
'健康サンダル':[996,1992,3237,0,0,2241,0],
'携帯電動シェーバー':[0,0,0,0,0,0,0],
'バランスケアスリッパ':[996,0,0,996,996,0,0],
'壁掛けディスペンサー':[0,1196,0,0,1196,0,0],
'ムダ毛シェーバー':[0,0,0,0,0,1396,0],
'湯上がりガーゼワンピース':[1196,0,0,0,1196,0,0],
}
for n,v in DD.items(): assert sum(v)==DC7[n], (n,sum(v),DC7[n])
def nsales(n,ds): return sum(DS[n][DATES.index(d)]-DD[n][DATES.index(d)] for d in ds)
INCA={}
for n,(p1,p2,chg,ob,nb,dirn) in EXP.items():
    s1_=nsales(n,p1)/len(p1); s2_=nsales(n,p2)/len(p2)
    a1_=A(p1,n)/len(p1);      a2_=A(p2,n)/len(p2)
    i1=sum(IDX[wd(d)] for d in p1)/len(p1); i2=sum(IDX[wd(d)] for d in p2)/len(p2)
    o1=sum(STORE[d] for d in p1)/len(p1)-s1_; o2=sum(STORE[d] for d in p2)/len(p2)-s2_
    INCA[n]={'曜日':round((s2_*i1/i2-s1_)/(a2_-a1_),2), '全店':round((s2_*o1/o2-s1_)/(a2_-a1_),2)}
    EXPMETA[n]['Δ広告費/日']=round(a2_-a1_)
print('\n■ 増分MER（値引後ベースに変更）')
for n,v in INCA.items(): print(f'  {n:22s} 曜日{v["曜日"]:+6.2f} / 全店{v["全店"]:+6.2f}')

rows=[]; trace=[]
for n in sorted(set(list(S30)+list(S7)), key=lambda k:-N7.get(k,0)):
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
        SEASON.get(n,26) if n in S7 else '',
        DC7.get(n,0), RET7.get(n,0),
        BUD.get(n,'') if BUD.get(n) else ('停止中' if n=='湯上がりガーゼワンピース' else ''), '', '', (ia,split)])

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
       '転用が有利':False,'転用不可理由':NOREDEPLOY,'転用利益':0,'P1凍結':P1GUARD}
    path,concl,prop=flow.judge(p)
    if n=='湯上がりガーゼワンピース':
        r[30]='⏹ 停止済み'; r[31]='【広告】停止中（0円/日）'; rows2.append(r); continue
    if n=='ナノガラス脱毛パッド': concl='✅ 本日実施済み（68,000→76,000）'
    r[30]=concl; r[31]=action(n,[r[i] for i in list(range(28))+[29]],prop,im,ia,split)
    rows2.append(r)
    trace.append([r[0],round(upd,1),r[4],r[19],r[21],r[20],r[22],UTIL.get(n) or 0,
                  im if im is not None else ('割れ %.2f/%.2f'%(lo,hi) if split else '未測定/保留'),
                  '○' if n in TODAY else NEXT.get(n,''), cur,prop,concl,path])
rows2.append(['カタログ全部（テスト）※全商品横断','—','—',round(CAT7),'—','—','—','—','—','—',round(CAT3),'—','—',
  '—','—',round(CAT1),'—','—','—','—','—','—','—','—','—','—','—','—','—',CATBUD,'📢 全店横断',
  f'Shopify側で商品に紐づかないため売上・利益は分解不能。Meta計上の実績のみ: 7日 消化{CAT7:,.0f}円/購入98件/CPA{CAT7/98:,.0f}円・'
  f'30日 消化{CAT30:,}円/計上売上2,621,222円/Meta基準ROAS{2621222/CAT30:.2f}。この行を含めると広告費列のSUMがMetaアカウント消化と一致'])

FEE=0.0349
def blk(days,N,K,cat):
    g=sum(N.values()); cost=sum(K.values()); ad=sum(A(days,n) for n in N)+cat
    pr=g-cost-ad
    return dict(日数=len(days),売上=g,原価=cost,広告費=round(ad),利益=round(pr),利益率=pr/g,
                手数料=round(g*FEE),手数料後利益=round(pr-g*FEE),手数料後利益率=(pr-g*FEE)/g)
SUM={'前日(7/28 火)':blk(D1,N1,K1,CAT1),'3日(7/26-28)':blk(D3,N3,K3,CAT3),'7日(7/22-28)':blk(D7,N7,K7,CAT7)}
SUM['30日(6/29-7/28)']=blk([d for d,_,_,_ in DAILY],N30,K30,0)
SUM['30日(6/29-7/28)']['広告費']=sum(AD30.values())+CAT30
g30=sum(N30.values()); c30=sum(K30.values()); a30=sum(AD30.values())+CAT30
SUM['30日(6/29-7/28)'].update(利益=g30-c30-a30,利益率=(g30-c30-a30)/g30,手数料=round(g30*FEE),
  手数料後利益=round(g30-c30-a30-g30*FEE),手数料後利益率=(g30-c30-a30-g30*FEE)/g30,日数=30)
CUMD=['2026-07-%02d'%d for d in range(18,29)]
UCUM2={'4WAY':631,'害虫ブロッカー':564,'形状記憶日傘':435,'ナノガラス脱毛パッド':388,'完全遮光・形状記憶':223,
'卓上冷感クーラー':179,'接触冷感UVパーカー':249,'5WAY腰掛けファン':115,'偏光・調光サングラス':119,
'3WAYサーキュレーター':77,'ムダ毛シェーバー':65,'接触冷感UVアームカバー':94,'瞬間冷感ポンチョ':84,
'健康サンダル':54,'UV歯ブラシ除菌器':28,'携帯電動シェーバー':49,'壁掛けディスペンサー':21,
'バランスケアスリッパ':28,'湯上がりガーゼワンピース':17,'瞬間冷却ハンディファン':10,'優先配送':109,
'完全遮光・接触冷感UVハット':2,'ネックマッサージャー':1,'リカバリーサンダル':2}
NANO['cum']=(201+59,92+36); DISP['cum']=(14,7)
CCUM=costs(UCUM2,'cum')
CS=sum(STORE[d] for d in CUMD); CA=sum(ACCT[d] for d in CUMD); CC=sum(CCUM.values()); CP=CS-CC-CA
CUM={'日数':11,'売上':CS,'原価':CC,'広告費':CA,'利益':CP,'利益率':CP/CS,'手数料':round(CS*FEE),
 '手数料後利益':round(CP-CS*FEE),'手数料後利益率':(CP-CS*FEE)/CS}
# 収益算定の照合（値引を商品に配賦したので「全店値引」の調整が不要になる）
prod_profit=sum(N7[n]-K7.get(n,0)-A(D7,n) for n in N7)
print(f"\n  照合 Σ商品利益(7日) {prod_profit:,.0f} − カタログ広告 {CAT7:,.0f} = {prod_profit-CAT7:,.0f} / 全体利益 {SUM['7日(7/22-28)']['利益']:,} → 差 {prod_profit-CAT7-SUM['7日(7/22-28)']['利益']:+,.0f}円")
p1p=sum(N1[n]-K1.get(n,0)-A(D1,n) for n in N1)
print(f"  照合 Σ商品利益(前日) {p1p:,.0f} − カタログ広告 {CAT1:,.0f} = {p1p-CAT1:,.0f} / 全体利益 {SUM['前日(7/28 火)']['利益']:,} → 差 {p1p-CAT1-SUM['前日(7/28 火)']['利益']:+,.0f}円")
print('\n■ 全体サマリー')
for k,v in list(SUM.items())+[('📅7/18〜7/28累積(11日)',CUM)]:
    print(f"{k:22s} 売上{v['売上']:>11,} 原価{v['原価']:>10,} 広告{v['広告費']:>10,} 利益{v['利益']:>10,} ({v['利益率']*100:>4.1f}%) 手数料後{v['手数料後利益']:>10,} ({v['手数料後利益率']*100:>4.1f}%)")
print(f"\n{'商品':24s}{'7日利益':>10s}{'率':>7s}{'MER':>6s}{'分岐':>6s}{'目標':>6s}{'余裕':>6s}")
for r in rows2:
    if not isinstance(r[19],float): continue
    print(f"{r[0][:22]:24s}{r[4]:>10,}{r[5]*100:>6.1f}%{r[19]:>6.2f}{r[20]:>6.2f}{(r[21] or 0):>6.2f}{r[22]:>6.2f}")
print('\n=== 判定（値引後ベース）===')
for t in trace:
    mk=' ★変更' if t[10]!=t[11] else ''
    print(f'{t[0][:24]:26s}{t[10]:>8,}→{t[11]:>8,} {t[12]}{mk}')
json.dump({'rows':rows2,'trace':trace,'SUM':SUM,'CUM':CUM},open('rows3_0729.json','w'),ensure_ascii=False)
