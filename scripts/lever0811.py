# -*- coding: utf-8 -*-
import pickle,csv,collections
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
N7,K7,A7,Q7=R['N7'],R['K7'],R['A7'],R['Q7']
BUD={'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':32500,'形状記憶日傘':35000,'4WAY':28000,
'害虫ブロッカー':45000,'接触冷感UVパーカー':30000,'ムダ毛シェーバー':20000,'完全遮光・形状記憶':21000,
'偏光・調光サングラス':22000,'5WAY腰掛けファン':16250,'完全遮光・接触冷感UVハット':12000,
'2WAYシートボックス':15000,'姿勢サポートチェア':10000,'携帯電動シェーバー':8250,'瞬間冷感ポンチョ':9000,
'接触冷感UVアームカバー':8000,'卓上冷感クーラー':7500,'バランスケアスリッパ':5000}
SPEND={'ナノガラス脱毛パッド':69232,'W固定スマホ車載ホルダー':34926,'形状記憶日傘':30819,'4WAY':27969,
'害虫ブロッカー':45470,'接触冷感UVパーカー':26442,'ムダ毛シェーバー':19551,'完全遮光・形状記憶':18942,
'偏光・調光サングラス':18535,'5WAY腰掛けファン':14273,'完全遮光・接触冷感UVハット':12571,
'2WAYシートボックス':12340,'姿勢サポートチェア':8687,'携帯電動シェーバー':8082,'瞬間冷感ポンチョ':7721,
'接触冷感UVアームカバー':7338,'卓上冷感クーラー':7128,'バランスケアスリッパ':4513}
SEA={'4WAY','卓上冷感クーラー','5WAY腰掛けファン','接触冷感UVパーカー','接触冷感UVアームカバー',
'瞬間冷感ポンチョ','完全遮光・接触冷感UVハット','形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','害虫ブロッカー'}
print("■ P-1ガード（新基準: 直近3日 vs その前3日の全店MER）")
S=collections.defaultdict(float); A=collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['date']]+=float(r['gross'])-float(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['date']]+=float(r['cost'])
p2=['2026-08-08','2026-08-09','2026-08-10']; p1=['2026-08-05','2026-08-06','2026-08-07']
m2=sum(S[d] for d in p2)/sum(A[d] for d in p2); m1=sum(S[d] for d in p1)/sum(A[d] for d in p1)
print(f"  8/05-07 MER {m1:.3f} → 8/08-10 MER {m2:.3f}  = {(m2/m1-1)*100:+.1f}%  → {'⚠️発動' if m2/m1-1<=-0.05 else '✅解除（未測定の増額を禁止しない）'}\n")
rows=[]
for n,b in BUD.items():
    s,k,a=N7[n],K7[n],A7[n]
    gm=1-k/s; mer=s/a; mm=mer*0.7
    cut=(1-mm*gm)*b*0.25*7      # −25%で増える週利益
    up =(mm*gm-1)*b*0.25*7      # +25%で増える週利益
    rows.append((n,b,SPEND[n]/b,mer,1/gm,mer-1/gm,mm*gm-1,cut,up,s-k-a,n in SEA))
print("■ 全商品の『動かしたときの週あたり変化量』（限界MER=平均MER×0.7・実測レンジ0.6〜0.8の中央）")
print(f"{'商品':22}{'区分':5}{'日予算':>8}{'消化率':>7}{'MER':>6}{'分岐':>6}{'余裕':>7}{'1円利益':>8}{'−25%で':>10}{'+25%で':>10}{'7日利益':>10}")
for r in sorted(rows,key=lambda x:-max(x[7],x[8])):
    n,b,u,mer,be,yo,per,cut,up,p7,sea=r
    print(f"{n[:22]:22}{'季節' if sea else '通年':5}{b:>8,}{u*100:>6.1f}%{mer:>6.2f}{be:>6.2f}{yo:>+7.2f}{per:>+8.3f}{cut:>+10,.0f}{up:>+10,.0f}{p7:>10,.0f}")
print("\n■ 削減で利益が増える（1円あたり利益が負）")
for r in sorted(rows,key=lambda x:-x[7]):
    if r[6]<0: print(f"  {r[0][:22]:22} −25%で 週{r[7]:+,.0f}円  余裕{r[5]:+.2f}  {'季節' if r[10] else '通年'}")
print("\n■ 増額で利益が増える（1円あたり利益が正・かつ消化率95%以上）")
for r in sorted(rows,key=lambda x:-x[8]):
    if r[6]>0 and r[2]>=0.95: print(f"  {r[0][:22]:22} +25%で 週{r[8]:+,.0f}円  消化{r[2]*100:.0f}%  {'季節' if r[10] else '通年'}")
print("\n■ 増額したいが消化率が足りない（増やしても使われない）")
for r in sorted(rows,key=lambda x:-x[8]):
    if r[6]>0 and r[2]<0.95: print(f"  {r[0][:22]:22} 消化{r[2]*100:.0f}%  +25%なら週{r[8]:+,.0f}円だが空振りの恐れ")
tc=sum(r[7] for r in rows if r[6]<0); tu=sum(r[8] for r in rows if r[6]>0 and r[2]>=0.95)
print(f"\n  減額側の合計 週{tc:+,.0f}円 ／ 増額側（消化率95%以上のみ）合計 週{tu:+,.0f}円 ／ 両方やると 週{tc+tu:+,.0f}円")
