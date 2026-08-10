# -*- coding: utf-8 -*-
import pickle,statistics
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
N7,K7,A7,Q7=R['N7'],R['K7'],R['A7'],R['Q7']
BUD={'形状記憶日傘':35000,'接触冷感UVパーカー':30000,'5WAY腰掛けファン':16250,'偏光・調光サングラス':22000,
'W固定スマホ車載ホルダー':32500,'ナノガラス脱毛パッド':80000,'完全遮光・接触冷感UVハット':12000,'4WAY':28000}
ORD={'形状記憶日傘':91,'接触冷感UVパーカー':100,'5WAY腰掛けファン':41,'偏光・調光サングラス':54,
'W固定スマホ車載ホルダー':124,'ナノガラス脱毛パッド':312,'完全遮光・接触冷感UVハット':40}
PR=dict(R['PRICE']); CO=dict(R['COST'])
CO['ナノガラス脱毛パッド']=round((835*757+364*740)/1199)   # 30日実測ミックス
print("■ 利益率の3分解（7日 8/04-10 実測）  利益率 = 1 − 原価率 − 広告費率")
print(f"{'商品':22}{'売価':>7}{'原価':>7}{'利益率':>8}{'原価率':>8}{'広告費率':>9}{'MER':>6}{'分岐':>6}{'目標':>6}{'ボトルネック':>14}")
T=['形状記憶日傘','接触冷感UVパーカー','5WAY腰掛けファン','偏光・調光サングラス','W固定スマホ車載ホルダー','ナノガラス脱毛パッド']
for n in T:
    s,k,a=N7[n],K7[n],A7[n]; cr=k/s; ar=a/s; pm=1-cr-ar; gm=1-cr
    tg=1/(gm-0.35) if gm-0.35>0 else None
    bn='原価（>33%）' if cr>0.33 else ('広告（>40%）' if ar>0.40 else '—')
    if cr>0.33 and ar>0.40: bn='両方＝赤字圏'
    print(f"{n[:22]:22}{PR[n]:>7,}{CO[n] if isinstance(CO[n],int) else round(CO[n]):>7,}{pm*100:>7.1f}%{cr*100:>7.1f}%{ar*100:>8.1f}%{s/a:>6.2f}{1/gm:>6.2f}{tg if tg else 0:>6.2f}{bn:>14}")
print("\n■ 利益率を30%にするには何が必要か（3つのレバーそれぞれ単独で）")
for n in T:
    s,k,a=N7[n],K7[n],A7[n]; cr=k/s; gm=1-cr; mer=s/a; pm=1-cr-a/s; q=Q7[n]; o=ORD.get(n)
    need_mer=1/(gm-0.30) if gm-0.30>0 else None
    need_cr=1-0.30-a/s
    mm=mer*0.7
    # 減額でMERを need_mer にする削減額（限界MER=平均×0.7で売上が減る前提）
    X=None
    if need_mer and need_mer>mer:
        X=(s-need_mer*a)/(mm-need_mer)   # (s-mm*X)/(a-X)=need_mer
    print(f"\n  【{n}】現 利益率 {pm*100:.1f}%／原価率 {cr*100:.1f}%／MER {mer:.2f}")
    if need_mer: print(f"   ① 広告効率で: MER {mer:.2f} → {need_mer:.2f} が必要（+{need_mer/mer*100-100:.0f}%）")
    else:        print(f"   ① 広告効率で: 原価率が高すぎて広告費ゼロでも30%に届かない")
    if need_cr>0: print(f"   ② 原価だけで: 原価率 {cr*100:.1f}% → {need_cr*100:.1f}% が必要（−{(cr-need_cr)*100:.1f}pt＝原価 {CO[n] if isinstance(CO[n],int) else round(CO[n]):,}円 → {round(need_cr*PR[n]):,}円）")
    else:        print(f"   ② 原価だけで: 広告費率が高すぎて原価ゼロでも30%に届かない")
    if X and 0<X<a:
        ns=s-mm*X; na=a-X; nk=ns*cr; np_=ns-nk-na
        print(f"   ③ 減額だけで: 広告 {a:,.0f}→{na:,.0f}（−{X/a*100:.0f}%／日予算 {BUD[n]:,}→{round(BUD[n]*(1-X/a)/500)*500:,}）")
        print(f"      → 利益率 {pm*100:.1f}%→30.0%／週利益 {s-k-a:,.0f}→{np_:,.0f}円（{np_-(s-k-a):+,.0f}）")
    # 値上げ
    if o:
        gp=(s-k)/q; ipo=q/o
        for up in (500,1000):
            y=1-gp/(gp+up); z=1-a/(o*(gp+up)*ipo)
            print(f"   ④ +{up}円値上げ: 改善ライン −{y*100:.1f}%まで／黒字化ライン −{z*100:.1f}%まで数量減を許容"
                  f"（同数量なら週利益 {s-k-a:,.0f}→{s+q*up-k-a:,.0f}円・利益率 {(s+q*up-k-a)/(s+q*up)*100:.1f}%）")
print("\n\n■ 増額したときの利益率（ユーザーの30%制約に当てるとどうなるか）")
for n,add in [('W固定スマホ車載ホルダー',7500),('ナノガラス脱毛パッド',16000),('完全遮光・接触冷感UVハット',3000)]:
    s,k,a=N7[n],K7[n],A7[n]; cr=k/s; gm=1-cr; mer=s/a; mm=mer*0.7
    ds=mm*add*7; dk=ds*cr; ns=s+ds; nk=k+dk; na=a+add*7
    print(f"  {n[:22]:22} 現 利益率 {(s-k-a)/s*100:.1f}% / 週利益 {s-k-a:,.0f}")
    print(f"  {'':22} +{add:,}円/日 → 利益率 {(ns-nk-na)/ns*100:.1f}%（{(ns-nk-na)/ns*100-(s-k-a)/s*100:+.1f}pt）/ 週利益 {ns-nk-na:,.0f}（{ns-nk-na-(s-k-a):+,.0f}）")
    print(f"  {'':22} 増分だけの利益率 = {(mm*gm-1)/mm*100:.1f}%（全店平均19.6%と比べて{'高い＝全店の率を押し上げる' if (mm*gm-1)/mm>0.196 else '低い＝全店の率を下げる'}）")
