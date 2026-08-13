# -*- coding: utf-8 -*-
"""「もっと儲ける」ための機会を金額順に並べる。売上/個数=Shopify実測、広告費/配信=Meta実測。"""
import pickle, csv, collections
R=pickle.load(open('/tmp/rep0814.pkl','rb')); N7,K7,Q7,A7=R['N7'],R['K7'],R['Q7'],R['A7']
PRICE,COST=R['PRICE'],R['COST']
# 窓内の日次予算で消化率を出す（予算変更を反映）
BUD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/budget-snapshots.csv')): BUD[r['campaign']][r['snapshot_date']]+=float(r['daily_budget'])
MAP=R['MAP']; D7=R['D7']
TODAY={'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':36000,'形状記憶日傘':35000,'接触冷感UVパーカー':30000,
'害虫ブロッカー':37000,'4WAY':11800,'ムダ毛シェーバー':20000,'偏光・調光サングラス':16500,'5WAY腰掛けファン':14000,
'完全遮光・形状記憶':15750,'2WAYシートボックス':18000,'快適マジックインソール':12000,'完全遮光・接触冷感UVハット':12000,
'姿勢サポートチェア':10000,'接触冷感UVアームカバー':8000,'卓上冷感クーラー':5000,'バランスケアスリッパ':5000}
SEASON={'4WAY','5WAY腰掛けファン','卓上冷感クーラー','形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス',
        '接触冷感UVパーカー','接触冷感UVアームカバー','完全遮光・接触冷感UVハット','害虫ブロッカー'}
rows=[]
for n,bud in TODAY.items():
    rev,c,ad=N7[n],K7[n],A7[n]
    if not ad: continue
    mer=rev/ad; gr=1-c/rev; lim=mer*0.7
    per=lim*gr-1                                    # 増額1円あたりの利益
    b7=sum(BUD[MAP.get(n,n)].get(d,0) for d in D7)
    sh=ad/b7 if b7 else None
    inc_rate=(lim*gr-1)/lim if lim else None        # 増分の利益率
    rows.append((n,bud,mer,gr,per,sh,inc_rate,rev-c-ad,n in SEASON))
tot_rev=sum(N7.values()); tot_c=sum(K7.values()); tot_ad=R['ACCT7']
store_rate=(tot_rev-tot_c-tot_ad)/tot_rev
print(f"全店7日 利益率 {store_rate*100:.1f}% ／ 1日利益 {(tot_rev-tot_c-tot_ad)/7:,.0f}円\n")
print("■ 増額の期待値（+25%したときの週次利益・限界MER=平均×0.7）")
print(f"{'商品':22}{'日予算':>8}{'MER':>6}{'1円あたり':>9}{'週消化率':>8}{'増分利益率':>9}{'+25%で/週':>11}  通年/季節")
for n,bud,mer,gr,per,sh,ir,pf,seas in sorted(rows,key=lambda x:-x[4]*x[1]):
    if per<=0: continue
    wk=per*bud*0.25*7
    flag='🚀' if (sh and sh>=0.95 and not seas) else ('⏸消化不足' if (sh and sh<0.95) else '季節')
    print(f"{n:22}{bud:8,}{mer:6.2f}{per:+9.3f}{(sh or 0)*100:7.0f}%{(ir or 0)*100:8.1f}%{wk:+11,.0f}  {'季節' if seas else '通年'} {flag}")
print(f"\n※ 増分利益率が全店 {store_rate*100:.1f}% を上回る商品は、増額すると利益額も利益率も上がる")

print("\n"+"="*78)
print("■ 広告費ゼロのレバー（実測）")
# 1) 優先配送
o7_all=1110; ps=25
for tgt in (0.05,0.10,0.15):
    print(f"  優先配送 {ps/o7_all*100:.2f}% → {tgt*100:.0f}%  週 +{(tgt*o7_all-ps)*536:,.0f}円（原価0＝全額利益）")
print(f"    ＋590円への値上げが実課金に反映されれば 1件+54円（現ペースで週+1,350円、10%到達なら+5,994円）")
# 2) 値上げ余地（改善ライン＝許容数量減）
print("\n  値上げの改善ライン（この%まで数量が落ちても粗利総額は減らない）")
CAND=[('姿勢サポートチェア',5980,7980,1811,29,164749,69393),
      ('姿勢サポートチェア',5980,6980,1811,29,164749,69393),
      ('W固定スマホ車載ホルダー',3980,4480,1182,164,638989,205538),
      ('快適マジックインソール',3980,4480,677,22,82784,25611),
      ('2WAYシートボックス',4980,5480,1943,68,325443,94057)]
for n,old,new,c,q,rev,ad in CAND:
    y=1-(old-c)/(new-c); z=1-ad/(q*(new-c))
    same=q*new*(1-(q*old-rev)/(q*old))-q*c-ad if q*old else 0
    print(f"    {n:18} {old:,}→{new:,}円  粗利 {old-c:,}→{new-c:,}  改善ライン {y*100:5.1f}%  黒字化ライン {z*100:5.1f}%  "
          f"同数量なら週 +{q*(new-old)*0.97:,.0f}円")
print("\n"+"="*78)
print("■ 9月末の崖（季節が抜けたあとに残る利益）")
S7={'季節':0,'通年':0}
for n,bud,mer,gr,per,sh,ir,pf,seas in rows: S7['季節' if seas else '通年']+=pf
cat=R['CAT7']
print(f"  7日利益  季節 {S7['季節']:>10,.0f} ／ 通年 {S7['通年']:>10,.0f} ／ カタログ広告 −{cat:,.0f}")
print(f"  → 季節が全部消えると 1日利益は {(S7['通年']-cat)/7:,.0f}円（最低ライン100,000円を{'割る' if (S7['通年']-cat)/7<100000 else '維持'}）")
