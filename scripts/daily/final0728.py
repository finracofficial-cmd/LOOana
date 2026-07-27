# -*- coding: utf-8 -*-
import json, sys, collections, statistics
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('calc0728.py').read().split("json.dump({'INCA'")[0])

BUD={'4WAY':95000,'害虫ブロッカー':85000,'ナノガラス脱毛パッド':68000,'形状記憶日傘':60000,'完全遮光・形状記憶':41000,
'接触冷感UVパーカー':34000,'卓上冷感クーラー':30000,'偏光・調光サングラス':22000,'接触冷感UVアームカバー':17000,
'3WAYサーキュレーター':16000,'ムダ毛シェーバー':13000,'5WAY腰掛けファン':13000,'健康サンダル':13000,
'瞬間冷感ポンチョ':13000,'携帯電動シェーバー':11000,'UV歯ブラシ除菌器':10000,'壁掛けディスペンサー':6000,
'バランスケアスリッパ':5000,'湯上がりガーゼワンピース':0}
BUDDAY={'卓上冷感クーラー':{'2026-07-26':38000,'2026-07-27':30000}}
def util(n):
    if not BUD.get(n): return ''
    t=b=0
    for d in ['2026-07-26','2026-07-27']:
        b+=BUDDAY.get(n,{}).get(d,BUD[n]); t+=A([d],n)
    return round(t/b,3) if b else ''
UTIL={n:util(n) for n in BUD}
TODAY={'4WAY','完全遮光・形状記憶','接触冷感UVパーカー','5WAY腰掛けファン'}
NEXT={'偏光・調光サングラス':'7/29','バランスケアスリッパ':'7/29','接触冷感UVアームカバー':'7/29','3WAYサーキュレーター':'7/29',
'携帯電動シェーバー':'7/29','害虫ブロッカー':'7/30','ナノガラス脱毛パッド':'7/30','UV歯ブラシ除菌器':'7/30',
'卓上冷感クーラー':'7/31','ムダ毛シェーバー':'8/3','瞬間冷感ポンチョ':'8/1','壁掛けディスペンサー':'8/1',
'形状記憶日傘':'なし(健全)','健康サンダル':'なし(健全)'}
PREV={'4WAY':85000,'完全遮光・形状記憶':34000,'接触冷感UVパーカー':28000}
CYCLE2={'壁掛けディスペンサー','UV歯ブラシ除菌器'}
SEASON={'卓上冷感クーラー':5,'4WAY':5,'5WAY腰掛けファン':5,'3WAYサーキュレーター':5,'瞬間冷却ハンディファン':5,
'接触冷感UVパーカー':6,'接触冷感UVアームカバー':6,'瞬間冷感ポンチョ':6,'完全遮光・接触冷感UVハット':6,
'形状記憶日傘':7,'完全遮光・形状記憶':7,'偏光・調光サングラス':7,'害虫ブロッカー':9}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'ムダ毛シェーバー':6980,
'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980}
SINGLE_CR={'4WAY':'4WAY（95,000円）'}
NOREDEPLOY=('転用先候補はいずれも直近の増額分の増分MERが未測定または分岐割れ。平均MERで転用益を見積もらない')

def adopt(n,br,tgt):
    ia=INCA.get(n,{})
    if len(ia)<2 or br=='' or tgt=='': return None,ia
    z=lambda v: 0 if v<br else (1 if v<tgt else 2)
    if z(ia['曜日'])!=z(ia['全店']): return None,ia
    return round((ia['曜日']+ia['全店'])/2,2), ia

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
    im,ia=adopt(n,br,tgt)
    rows.append([full, s7,c7,round(a7),round(P7), round(P7/s7,4) if s7 else '',
        round(cr,4) if cr!='' else '', round(a7/s7,4) if s7 else '',
        s3,c3,round(a3),round(P3), round(P3/s3,4) if s3 else '',
        s1,c1,round(a1),round(P1_), round(P1_/s1,4) if s1 else '',
        round(P30), mer, br, tgt, round(mer-br,2) if (mer!='' and br!='') else '',
        im if im is not None else '',
        round(CVR[n],4) if n in CVR else '', f'{CVR_RANK[n]}位/19' if n in CVR_RANK else '',
        SEASON.get(n,26) if n in S7 else '',
        BUD.get(n,'') if BUD.get(n) else ('停止中' if n=='湯上がりガーゼワンピース' else ''), '', '', ia])

def action(n,r,prop,im,ia):
    a=[]; cur=r[27] if isinstance(r[27],int) else 0
    if prop!=cur and isinstance(prop,int) and cur: a.append(f'【広告】{cur:,}→{prop:,}円/日')
    elif n in TODAY: a.append(f'【広告】{cur:,}円/日 据置')
    else: a.append(f'【広告】据置（次回判定 {NEXT.get(n,"—")}）')
    dr,dev=DIAG.get(n,([],[]))
    if dr: a.append('【診断】'+'・'.join(dr)+'（'+' / '.join(dev)+'）')
    if n in SINGLE_CR: a.append(f'【CR】{SINGLE_CR[n]}は配信CR1本。ただし劣化原因が需要減衰のためCRでは直らない→予算で対処')
    cv,rk=CVR.get(n),CVR_RANK.get(n)
    if cv is not None:
        a.append(f'【LP】CVR {cv*100:.2f}%＝自店{rk}位/19' + ('（下位25%→商品ページに改善余地）' if rk>=15 else '（中央値以上→LPは触らない）'))
    if 'D4 CPM上昇' in dr: a.append('【配信】Advantage+全開放と配信面の偏りを確認')
    cr=r[6]; wk=SEASON.get(n,26)
    if isinstance(cr,float) and cr>0.33:
        p_,c_=PRICE.get(n),COST.get(n)
        if p_ and c_:
            y=1-(p_-c_)/(p_+1000-c_)
            a.append((f'【原価】原価率{cr*100:.1f}%>33%。通年なのでCJ数量交渉が有効' if wk>=8
                      else f'【価格】原価率{cr*100:.1f}%>33%。残{wk}週で原価交渉は間に合わない→値上げのみ')
                     + f'／+1,000円で数量−{y*100:.1f}%まで許容')
    if isinstance(r[7],float) and r[7]>0.40: a.append('【広告費率】40%超（率のために黒字は削らない）')
    if ia:
        tail='（曜日・全店の2手法が一致→採用）' if im is not None else '（2手法で結論が割れる→判定保留）'
        a.append('【増分MER実測】'+' / '.join(f'{k}{v:+.2f}' for k,v in ia.items())+tail)
    return ' ／ '.join(a)

rows2=[]
for r in rows:
    ia=r.pop(); n=REVF.get(r[0],r[0])
    if not r[19]:
        r[28]='📦広告なし'; r[29]='広告費ゼロ。利益=売上−原価'; r[27]='—'; rows2.append(r); continue
    im=r[23] if r[23]!='' else None
    upd=U7.get(n,0)/7; cur=r[27] if isinstance(r[27],int) else 0
    p={'判定日':n in TODAY,'次回判定日':NEXT.get(n,'未設定'),'日販':upd,'利益7':r[4],'MER':r[19],
       '目標MER':r[21],'分岐':r[20],'余裕':r[22],'消化率':UTIL.get(n) or 0,'増分MER':im,
       '予算':cur,'元予算':PREV.get(n),'赤字比率':abs((r[4]/7)/cur) if cur else 0,'2巡目':n in CYCLE2,
       '転用が有利':False,'転用不可理由':NOREDEPLOY,'転用利益':0}
    path,concl,prop=flow.judge(p)
    if n=='湯上がりガーゼワンピース':
        path,concl,prop='S-1:7/26に停止済み。以後は判定対象外','⏹ 停止済み',0
        r[28]=concl; r[29]='【広告】停止中（0円/日）。再開は8月の秋物枠選定とあわせて検討'; rows2.append(r); continue
    r[28]=concl; r[29]=action(n,r,prop,im,ia); rows2.append(r)
    trace.append([r[0],round(upd,1),r[4],r[19],r[21],r[20],r[22],UTIL.get(n) or 0,
                  im if im is not None else '未測定/保留','○' if n in TODAY else NEXT.get(n,''),
                  cur,prop,concl,path])
json.dump({'rows':rows2,'trace':trace},open('rows0728.json','w'),ensure_ascii=False)
print(f"{'商品':24s}{'7日利益':>10s}{'率':>7s}{'MER':>6s}{'分岐':>6s}{'目標':>6s}{'余裕':>6s}{'CVR':>7s}{'順位':>7s}")
for r in rows2:
    if not r[19]: continue
    print(f"{r[0][:22]:24s}{r[4]:>10,}{r[5]*100:>6.1f}%{r[19]:>6.2f}{r[20]:>6.2f}{(r[21] or 0):>6.2f}{r[22]:>6.2f}{r[24]*100:>6.2f}%{r[25]:>7s}")
print('\n=== 判定 ===')
for t in trace:
    mk=' ★変更' if t[10]!=t[11] else ''
    print(f'{t[0][:24]:26s}{t[10]:>8,}→{t[11]:>8,} {t[12]}{mk}')
    if t[9]=='○': print(f'    {t[13]}')
