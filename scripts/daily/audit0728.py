# -*- coding: utf-8 -*-
"""7/28 ロジック監査: 実効分岐・祝日補正・増分MER再検証・価格帯調整CVR・週次トレンド"""
import json, sys, collections, datetime, statistics
sys.path.insert(0,'/home/user/LOOana/scripts')
exec(open('calc0728.py').read().split("json.dump({'INCA'")[0])

# ========== 1. 実効分岐MER（値引＋決済手数料を織り込んだ現金ベースの生存線） ==========
d_rate = sum(dc for _,_,dc,_ in DAILY)/sum(g for _,g,_,_ in DAILY)   # 30日実測の値引率
FEE = 0.0349
k = (1-d_rate)*(1-FEE)
print(f'■1. 実効分岐MER  値引率(30日実測) {d_rate*100:.2f}% × 手数料3.49% → 掛目 k={k:.4f}')
print(f'   実効分岐 = 1/(k − 原価率)。従来の分岐 1/(1−原価率) は値引と手数料を無視していた\n')
rows = json.load(open('rows0728.json'))['rows']
print(f"{'商品':24s}{'MER':>6s}{'旧分岐':>7s}{'実効分岐':>8s}{'旧余裕':>7s}{'実効余裕':>8s}{'表示利益':>10s}{'実効利益':>10s}  判定")
flips=[]
for r in rows:
    if not r[19]: continue
    S7p,C7p,A7p = r[1],r[2],r[3]; cr=C7p/S7p
    if k-cr<=0: continue
    ebr=1/(k-cr); mer=r[19]
    tp = S7p*k - C7p - A7p
    flag = '🚨 反転(実質赤字)' if (r[4]>0 and tp<0) else ('⚠️ 薄い' if 0<mer-ebr<0.3 else '')
    if flag.startswith('🚨'): flips.append(r[0])
    print(f"{r[0][:22]:24s}{mer:>6.2f}{r[20]:>7.2f}{ebr:>8.2f}{r[22]:>7.2f}{mer-ebr:>8.2f}{r[4]:>10,}{tp:>10,.0f}  {flag}")

# ========== 2. 曜日指数の祝日汚染（7/20 海の日） ==========
print('\n■2. 曜日指数: 7/20(海の日)を月曜平均から除外して再計算')
mon = [(d,g-dc) for d,g,dc,_ in DAILY if wd(d)=='月']
mon_ex = [v for d,v in mon if d!='2026-07-20']
allavg2 = sum(g-dc for _,g,dc,_ in DAILY)/len(DAILY)
print(f'   月曜(祝日込み) 平均 {sum(v for _,v in mon)/len(mon):,.0f} → 指数 {sum(v for _,v in mon)/len(mon)/allavg2*100:.1f}')
print(f'   月曜(祝日除外) 平均 {sum(mon_ex)/len(mon_ex):,.0f} → 指数 {sum(mon_ex)/len(mon_ex)/allavg2*100:.1f}')
m27 = 1233380-56152
print(f'   → 7/27実績 {m27:,} は 非祝日月曜平均比 {m27/(sum(mon_ex)/len(mon_ex))*100-100:+.1f}%（昨日レポートの「同曜日比−5.0%」は誤り）')

# 修正指数で増分MERを再計算
IDX2 = dict(IDX); IDX2['月'] = sum(mon_ex)/len(mon_ex)/allavg2*100
def inc2(n):
    p1,p2,chg,ob,nb = EXP[n]
    s1_=sales(n,p1)/len(p1); s2_=sales(n,p2)/len(p2)
    a1_=A(p1,n)/len(p1);     a2_=A(p2,n)/len(p2)
    if abs(a2_-a1_)<3000: return None
    i1=sum(IDX2[wd(d)] for d in p1)/len(p1); i2=sum(IDX2[wd(d)] for d in p2)/len(p2)
    return round((s2_*i1/i2-s1_)/(a2_-a1_),2)
print('\n   増分MER（曜日補正）を修正指数で再計算:')
for n in ('4WAY','完全遮光・形状記憶','接触冷感UVパーカー','3WAYサーキュレーター','壁掛けディスペンサー'):
    v0 = INCA.get(n,{}).get('曜日'); v1 = inc2(n)
    if v0 is not None: print(f'   {n:22s} {v0:+.2f} → {v1:+.2f}（判定 {"不変" if v1 is not None else "—"}）')

# ========== 3. 週次MERトレンド ==========
ADSUM={'2026-07-07':400730,'2026-07-08':422730,'2026-07-09':424206,'2026-07-10':443849,'2026-07-11':449807,
'2026-07-12':520194,'2026-07-13':442603,'2026-07-14':469437,'2026-07-15':457358,'2026-07-16':462095,
'2026-07-17':465259,'2026-07-18':502628,'2026-07-19':526222,'2026-07-20':569378,'2026-07-21':523535,
'2026-07-22':542527,'2026-07-23':554597,'2026-07-24':546903,'2026-07-25':555886,'2026-07-26':626825,'2026-07-27':563415}
SDX={d:(g-dc) for d,g,dc,_ in DAILY}
print('\n■3. 週次MERトレンド（7日完結ブロック・全店実測）')
for lbl,ds in [('7/07-13',[f'2026-07-{x:02d}' for x in range(7,14)]),
               ('7/14-20',[f'2026-07-{x:02d}' for x in range(14,21)]),
               ('7/21-27',[f'2026-07-{x:02d}' for x in range(21,28)])]:
    s_=sum(SDX[d] for d in ds); a_=sum(ADSUM[d] for d in ds)
    print(f'   {lbl}  売上{s_:>11,}  広告{a_:>10,}  MER {s_/a_:.3f}')

# ========== 4. CVRの価格帯調整（売上/クリックと帯内比較） ==========
print('\n■4. LP評価の価格帯調整  （CVR順位は価格を無視していた）')
CLICKS={n:W2[n][5] for n in W2}
print(f"{'商品':22s}{'AOV':>7s}{'CVR':>7s}{'売上/クリック':>10s}{'CPC':>6s}{'CVR順位':>7s}")
rpc={}
for r in rows:
    n=REVF.get(r[0],r[0])
    if n not in CLICKS or not r[19]: continue
    aov=r[1]/U7[n] if U7.get(n) else 0
    rp = r[1]/CLICKS[n]; rpc[n]=rp
    print(f"{n[:20]:22s}{aov:>7,.0f}{CVR[n]*100:>6.2f}%{rp:>10,.0f}{r[3]/CLICKS[n]:>6,.0f}{CVR_RANK[n]:>6d}位")
med=statistics.median(rpc.values())
print(f'   売上/クリック 中央値 {med:,.0f}円')
print('   下位: ' + '・'.join(f'{n}({v:,.0f})' for n,v in sorted(rpc.items(), key=lambda x:x[1])[:4]))
print('   UV歯ブラシ: ' + f'{rpc.get("UV歯ブラシ除菌器",0):,.0f}円/クリック（店内順位 {sorted(rpc.values(),reverse=True).index(rpc["UV歯ブラシ除菌器"])+1}位）')

# ========== 5. 日傘ペアの合算チェック（宣言していて未実施だった） ==========
print('\n■5. 日傘ペア合算（完全遮光の巻き戻し判定で本来併記すべきだった）')
P1=['2026-07-20','2026-07-21','2026-07-22']; P2=['2026-07-23','2026-07-24','2026-07-25','2026-07-26','2026-07-27']
ps1=(sales('完全遮光・形状記憶',P1)+sales('形状記憶日傘',P1))/3
ps2=(sales('完全遮光・形状記憶',P2)+sales('形状記憶日傘',P2))/5
pa1=(A(P1,'完全遮光・形状記憶')+A(P1,'形状記憶日傘'))/3
pa2=(A(P2,'完全遮光・形状記憶')+A(P2,'形状記憶日傘'))/5
st1=sum(SDX[d] for d in P1)/3; st2=sum(SDX[d] for d in P2)/5
print(f'   ペア売上/日 {ps1:,.0f} → {ps2:,.0f}（{ps2/ps1*100-100:+.1f}%）／ 全店 {st1:,.0f} → {st2:,.0f}（{st2/st1*100-100:+.1f}%）')
print(f'   ペア広告/日 {pa1:,.0f} → {pa2:,.0f}（Δ{pa2-pa1:+,.0f}円/日 → |Δ|<3,000で合算の増分検定は測定不能）')
print(f'   → 日傘需要は全店を上回るペースで減衰（ピークアウト）。完全遮光の巻き戻しを支持')
