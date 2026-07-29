# -*- coding: utf-8 -*-
"""2026-07-29 レポート（設計変更反映版）
   ①原価は販売数ベース（返品数を引かない）。返品は別窓のみ
   ②カタログ全部（テスト）を商品テーブルの1行に
   ③商品別の値引・返品を情報列として表示（売上定義は gross のまま据え置き）"""
import json, sys, collections, csv
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('v2.py').read())
_f=open('final0729.py').read()
exec(_f.split('rows=[]; trace=[]')[0].split("exec(open('calc0729.py').read())")[1])
exec('def action'+_f.split('def action')[1].split('# S2b（機会費用）')[0])
BUD['ナノガラス脱毛パッド']=76000   # 7/29 ユーザー実施済（メインセット55,000→63,000。Meta実測 daily_budget=630）

RET3={'4WAY':9960,'壁掛けディスペンサー':11866}          # 3日窓の返品（販売日基準）
RET1={'4WAY':9960}                                      # 前日窓の返品

rows=[]; trace=[]
for n in sorted(set(list(S30)+list(S7)), key=lambda k:-S7.get(k,0)):
    full=FULL.get(n,n)
    s7,c7,a7=S7.get(n,0),K7.get(n,0),A(D7,n)
    s3,c3,a3=S3.get(n,0),K3.get(n,0),A(D3,n)
    s1,c1,a1=S1.get(n,0),K1.get(n,0),A(D1,n)
    P7,P3,P1_=s7-c7-a7, s3-c3-a3, s1-c1-a1
    P30=S30.get(n,0)-K30.get(n,0)-AD30.get(n,0)
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
        path,concl,prop='S-1:7/26に停止済み。以後は判定対象外','⏹ 停止済み',0
        r[30]=concl; r[31]='【広告】停止中（0円/日）'; rows2.append(r); continue
    if n in ('害虫ブロッカー','ナノガラス脱毛パッド'):
        concl='✅ 本日実施済み' if n=='ナノガラス脱毛パッド' else concl
    r[30]=concl
    r[31]=action(n,[r[i] for i in list(range(28))+[29]],prop,im,ia,split)
    rows2.append(r)
    trace.append([r[0],round(upd,1),r[4],r[19],r[21],r[20],r[22],UTIL.get(n) or 0,
                  im if im is not None else ('割れ %.2f/%.2f'%(lo,hi) if split else '未測定/保留'),
                  '○' if n in TODAY else NEXT.get(n,''), cur,prop,concl,path])

# カタログ全部（テスト）を1行として追加（商品には配賦しないが、広告費のSUMが合うようにテーブルに載せる）
rows2.append(['カタログ全部（テスト）※全商品横断', '—','—',round(CAT7),'—','—','—','—',
  '—','—',round(CAT3),'—','—', '—','—',round(CAT1),'—','—', '—',
  '—','—','—','—','—', '—','—','—','—','—', CATBUD, '📢 全店横断',
  f'Shopify側で商品に紐づかないため売上・利益は分解不能。Meta計上の実績のみ: 7日 消化{CAT7:,.0f}円/購入98件/CPA{CAT7/98:,.0f}円・'
  f'30日 消化{CAT30:,}円/計上売上2,621,222円/Meta基準ROAS{2621222/CAT30:.2f}。この行を含めると広告費列のSUMがMetaアカウント消化と一致する'])

FEE=0.0349
def blk(days,S,K,cat):
    g=sum(STORE[d] for d in days); cost=sum(K.values()); ad=sum(A(days,n) for n in S)+cat
    pr=g-cost-ad
    return dict(日数=len(days),売上=g,原価=cost,広告費=round(ad),利益=round(pr),利益率=pr/g,
                手数料=round(g*FEE),手数料後利益=round(pr-g*FEE),手数料後利益率=(pr-g*FEE)/g)
SUM={'前日(7/28 火)':blk(D1,S1,K1,CAT1),'3日(7/26-28)':blk(D3,S3,K3,CAT3),'7日(7/22-28)':blk(D7,S7,K7,CAT7)}
g30=sum(STORE[d] for d,_,_,_ in DAILY); c30=sum(K30.values()); a30=sum(AD30.values())+CAT30
SUM['30日(6/29-7/28)']=dict(日数=30,売上=g30,原価=c30,広告費=a30,利益=g30-c30-a30,利益率=(g30-c30-a30)/g30,
  手数料=round(g30*FEE),手数料後利益=round(g30-c30-a30-g30*FEE),手数料後利益率=(g30-c30-a30-g30*FEE)/g30)
# 7/18-28 の販売数（gross÷売価。返品を引かない）
UCUM2={'4WAY':631,'害虫ブロッカー':564,'形状記憶日傘':435,'ナノガラス脱毛パッド':261+59+92+36,
'完全遮光・形状記憶':223,'卓上冷感クーラー':179,'接触冷感UVパーカー':249,'5WAY腰掛けファン':115,
'偏光・調光サングラス':119,'3WAYサーキュレーター':77,'ムダ毛シェーバー':65,'接触冷感UVアームカバー':94,
'瞬間冷感ポンチョ':84,'健康サンダル':54,'UV歯ブラシ除菌器':28,'携帯電動シェーバー':49,
'壁掛けディスペンサー':7+6+1+1+3+2+1,'バランスケアスリッパ':28,'湯上がりガーゼワンピース':17,
'瞬間冷却ハンディファン':10,'優先配送':109,'完全遮光・接触冷感UVハット':2,'ネックマッサージャー':1,
'リカバリーサンダル':2}
# ナノ 7/18-28: 白799,980/3,980=201・黒366,160/3,980=92・緑234,820/3,980=59・桃143,280/3,980=36 = 388
# ディスペンサー 7/18-28: 3本(黒48,860/6,980=7・銀41,880/6,980=6・透6,980/6,980=1)=14 / 2本(銀17,940/5,980=3・透11,960/5,980=2・黒5,980/5,980=1・白5,980/5,980=1)=7 → 計21
UCUM2['ナノガラス脱毛パッド']=201+92+59+36
UCUM2['壁掛けディスペンサー']=14+7
NANO['cum']=(201+59,92+36); DISP['cum']=(14,7)
CCUM2=costs(UCUM2,'cum')
assert sum(NANO['cum'])==UCUM2['ナノガラス脱毛パッド'] and sum(DISP['cum'])==UCUM2['壁掛けディスペンサー']
CUMD=['2026-07-%02d'%d for d in range(18,29)]
CUM_SALES=sum(STORE[d] for d in CUMD); CUM_AD=sum(ACCT[d] for d in CUMD)
CUM_COST2=sum(CCUM2.values()); CUM_PROFIT2=CUM_SALES-CUM_COST2-CUM_AD
CUM2={'日数':11,'売上':CUM_SALES,'原価':CUM_COST2,'広告費':CUM_AD,'利益':CUM_PROFIT2,
  '利益率':CUM_PROFIT2/CUM_SALES,'手数料':round(CUM_SALES*FEE),'手数料後利益':round(CUM_PROFIT2-CUM_SALES*FEE),
  '手数料後利益率':(CUM_PROFIT2-CUM_SALES*FEE)/CUM_SALES}
print('■ 全体サマリー（返品を原価から外した後）')
for k,v in list(SUM.items())+[('📅7/18〜7/28累積(11日)',CUM2)]:
    print(f"{k:22s} 売上{v['売上']:>11,} 原価{v['原価']:>10,} 広告{v['広告費']:>10,} 利益{v['利益']:>10,} ({v['利益率']*100:>4.1f}%) 手数料後{v['手数料後利益']:>10,} ({v['手数料後利益率']*100:>4.1f}%)")
RET_M=sum(rt for d,_,_,rt in DAILY if d.startswith('2026-07'))
RET_RATE=RET_M/sum(g-dc for d,g,dc,_ in DAILY if d.startswith('2026-07'))
print(f"\n返品（別窓）: 7日 {sum(RET7.values()):,}円 / 当月累計 {RET_M:,}円（返品率 {RET_RATE*100:.2f}%）")
print('  7日の返品内訳: ' + ' / '.join(f'{n[:10]}{v:,}円' for n,v in sorted(RET7.items(),key=lambda x:-x[1])))
print(f'  30日の返品内訳: ' + ' / '.join(f'{n[:10]}{v:,}円' for n,v in sorted(RET30.items(),key=lambda x:-x[1])[:5]))
json.dump({'rows':rows2,'trace':trace,'SUM':SUM,'CUM':CUM2},open('rows2_0729.json','w'),ensure_ascii=False)
