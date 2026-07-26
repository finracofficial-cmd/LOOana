# -*- coding: utf-8 -*-
import json, collections, datetime, sys
sys.path.insert(0,'/home/user/LOOana/scripts')
import decision_flow as flow
exec(open('build0727.py').read().split("json.dump({'IDX'")[0])

FULL = {'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
        '3WAYサーキュレーター':'3WAYサーキュレーター扇風機'}
# ===== 週次（W1 7/13-19 → W2 7/20-26）: 完全週どうしなので曜日補正が不要 =====
SW1={'4WAY':1942200,'害虫ブロッカー':1289520,'形状記憶日傘':1180260,'ナノガラス脱毛パッド':855700,
'完全遮光・形状記憶':607560,'接触冷感UVパーカー':465660,'卓上冷感クーラー':448500,'偏光・調光サングラス':374120,
'3WAYサーキュレーター':293020,'接触冷感UVアームカバー':238800,'UV歯ブラシ除菌器':233480,'壁掛けディスペンサー':217360,
'ムダ毛シェーバー':185380,'瞬間冷感ポンチョ':183080,'携帯電動シェーバー':174300,'健康サンダル':164340,
'バランスケアスリッパ':129480,'湯上がりガーゼワンピース':121520,'瞬間冷却ハンディファン':53820,'優先配送':26264,
'5WAY腰掛けファン':19920,'完全遮光・接触冷感UVハット':11960}
AW1={n:v[0] for n,v in W1.items()}; AW2={n:v[0] for n,v in W2.items()}
STORE = {ds: g-dc for ds,g,dc,*_ in DAILY}
STORE_W1 = sum(STORE[d] for d in STORE if '2026-07-13'<=d<='2026-07-19')
STORE_W2 = sum(STORE[d] for d in STORE if '2026-07-20'<=d<='2026-07-26')

def incr_all(n):
    """3通りの測り方で増分MERを出す。①週次(補正不要) ②P1/P2×曜日指数 ③P1/P2×全店コントロール"""
    out = {}
    if n in SW1 and n in AW1 and n in AW2 and abs(AW2[n]-AW1[n]) >= 3000*7:
        out['週次'] = round((S['d7'][n]-SW1[n])/(AW2[n]-AW1[n]), 2)
    if n in EXP:
        p1,p2,chg,ob,nb = EXP[n]
        s1=sales(n,p1)/len(p1); s2=sales(n,p2)/len(p2); a1=A(p1,n)/len(p1); a2=A(p2,n)/len(p2)
        if abs(a2-a1) >= 3000:
            i1=sum(IDX[wd(d)] for d in p1)/len(p1); i2=sum(IDX[wd(d)] for d in p2)/len(p2)
            out['曜日'] = round((s2*i1/i2-s1)/(a2-a1), 2)
            o1=sum(STORE[d] for d in p1)/len(p1)-s1; o2=sum(STORE[d] for d in p2)/len(p2)-s2
            out['全店'] = round((s2*o1/o2-s1)/(a2-a1), 2)
    return out
INCA = {n: incr_all(n) for n in S['d7']}

# ===== 商品テーブル =====
COST30 = dict(C['d30'])
rows=[]; ctx={}
for n in sorted(set(list(S['d30'])+list(S['d7'])), key=lambda k: -S['d7'].get(k,0)):
    full = FULL.get(n,n)
    S7p,C7p,A7p = S['d7'].get(n,0), C['d7'].get(n,0), A(D7,n)
    S3p,C3p,A3p = S['d3'].get(n,0), C['d3'].get(n,0), A(D3,n)
    S1p,C1p,A1p = S['d1'].get(n,0), C['d1'].get(n,0), A(D1,n)
    P7,P3,P1_ = S7p-C7p-A7p, S3p-C3p-A3p, S1p-C1p-A1p
    P30 = S['d30'].get(n,0) - COST30.get(n,0) - AD30.get(n,0)
    cr = C7p/S7p if S7p else ''
    tgt = round(1/(1-cr-0.35),2) if (cr!='' and 1-cr-0.35>0) else ''
    mer = round(S7p/A7p,2) if A7p else ''
    br  = round(S7p/(S7p-C7p),2) if (A7p and S7p>C7p) else ''
    ia = INCA.get(n,{})
    # 3手法が同符号・同判定なら採用、割れたら保留
    im = None; imtxt = ''
    if ia:
        vals = list(ia.values())
        im = round(sum(vals)/len(vals),2)
        agree = (len(vals)==1) or (all(v < br for v in vals) or all(v >= tgt for v in vals)
                 or all(br <= v < tgt for v in vals if br!='' and tgt!=''))
        imtxt = ' / '.join(f'{k}{v:+.2f}' for k,v in ia.items())
        if not agree: im = None
    ctx[full] = {'ia':ia,'agree':im is not None,'imtxt':imtxt}
    rows.append([full, S7p,C7p,round(A7p),round(P7), round(P7/S7p,4) if S7p else '',
        round(cr,4) if cr!='' else '', round(A7p/S7p,4) if S7p else '',
        S3p,C3p,round(A3p),round(P3), round(P3/S3p,4) if S3p else '',
        S1p,C1p,round(A1p),round(P1_), round(P1_/S1p,4) if S1p else '',
        round(P30), mer, br, tgt, round(mer-br,2) if (mer!='' and br!='') else '',
        im if im is not None else '', BUD.get(n,'') if BUD.get(n) else ('停止中' if n=='湯上がりガーゼワンピース' else ''),
        '', ''])
json.dump({'rows':rows,'ctx':ctx,'INCA':INCA}, open('rows0727.json','w'), ensure_ascii=False, indent=1)
print(f"{'商品':26s}{'7日利益':>10s}{'率':>7s}{'MER':>6s}{'分岐':>6s}{'目標':>6s}{'余裕':>6s}  増分MER")
for r in rows:
    if not r[19]: continue
    print(f"{r[0][:24]:26s}{r[4]:>10,}{r[5]*100:>6.1f}%{r[19]:>6.2f}{r[20]:>6.2f}{r[21] if r[21]!='' else 0:>6.2f}{r[22]:>6.2f}  {ctx[r[0]]['imtxt']}")
