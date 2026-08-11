# -*- coding: utf-8 -*-
"""3日/5日/7日の3窓で商品を判定する。窓はすべて2026-08-10終端（8/11は未完了なので除外）。
原価はナノガラス/ディスペンサーのみ30日実測ミックスの加重平均単価【近似】。他は実売価から正確に算出。"""
import csv,collections,pickle,datetime
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
COST=dict(R['COST']); PRICE=dict(R['PRICE']); MAP=R['MAP']
COST['ナノガラス脱毛パッド']=(835*757+364*740)/1199
COST['壁掛けディスペンサー']=(45*2528+13*1981)/58; PRICE['壁掛けディスペンサー']=391840/58
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['campaign']][r['date']]+=float(r['cost'])
B=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('data/budget-snapshots.csv')): B[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])
end=datetime.date(2026,8,10)
W={n:[(end-datetime.timedelta(days=i)).isoformat() for i in range(n-1,-1,-1)] for n in (3,5,7)}
BUD={'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':32500,'形状記憶日傘':35000,'4WAY':21000,
'害虫ブロッカー':45000,'接触冷感UVパーカー':30000,'ムダ毛シェーバー':20000,'完全遮光・形状記憶':21000,
'偏光・調光サングラス':22000,'5WAY腰掛けファン':16250,'完全遮光・接触冷感UVハット':12000,
'2WAYシートボックス':15000,'姿勢サポートチェア':10000,'携帯電動シェーバー':8250,'瞬間冷感ポンチョ':9000,
'接触冷感UVアームカバー':8000,'卓上冷感クーラー':7500,'バランスケアスリッパ':5000}
def blk(n,days):
    g=sum(S[n][d][0] for d in days if d in S[n]); dc=sum(S[n][d][1] for d in days if d in S[n])
    a=sum(AD[MAP.get(n,n)].get(d,0) for d in days)
    k=g/PRICE[n]*COST[n] if (g and n in PRICE and n in COST) else 0
    return g-dc,k,a
out=[]
for n in BUD:
    r={}
    for w,days in W.items():
        s,k,a=blk(n,days)
        r[w]=(s,k,a,s-k-a,(s/a if a else 0),(1/(1-k/s) if s and k<s else 0),((s-k-a)/s if s else 0))
    cp=MAP.get(n,n); d7=[d for d in W[7] if d in B[cp]]
    wu=(r[7][2]/sum(B[cp][d] for d in d7)) if len(d7)==7 and sum(B[cp][d] for d in d7) else None
    be=r[7][5]; gm=1-r[7][1]/r[7][0] if r[7][0] else 0
    tg=1/(gm-0.35) if gm-0.35>0 else None
    below=sum(1 for w in (3,5,7) if r[w][4]<r[w][5])            # 分岐割れの窓数
    thin =sum(1 for w in (3,5,7) if r[w][4]-r[w][5]<0.30)       # 余裕<0.30の窓数
    above=sum(1 for w in (3,5,7) if tg and r[w][4]>=tg)         # 目標超えの窓数
    if below==3:   act,why='🚨 停止 or −50%','3窓すべて分岐割れ'
    elif thin==3:  act,why='🔻 −25%','3窓すべて余裕<0.30'
    elif above==3 and wu and wu>=0.95: act,why='🚀 +25%','3窓すべて目標超え＆週消化95%↑'
    elif below>=1: act,why='⏸ 据え置き','窓で割れる（判定日を待つ）'
    else:          act,why='✅ 維持','—'
    out.append((n,r,be,tg,wu,act,why,below,above))
print("■ 3窓判定（すべて8/10終端・8/11は未完了のため除外）  原価はナノガラス/ディスペンサーのみ【近似】")
print(f"{'商品':22}{'3日MER':>8}{'5日MER':>8}{'7日MER':>8}{'分岐':>6}{'目標':>6}{'方向':>6}{'週消化':>8}{'7日利益':>10}{'処置':>16}")
for n,r,be,tg,wu,act,why,bl,ab in sorted(out,key=lambda x:-x[1][7][3]):
    dirn='↑' if r[3][4]>r[7][4]*1.05 else ('↓' if r[3][4]<r[7][4]*0.95 else '→')
    print(f"{n[:22]:22}{r[3][4]:>8.2f}{r[5][4]:>8.2f}{r[7][4]:>8.2f}{be:>6.2f}{tg if tg else 0:>6.2f}{dirn:>6}"
          f"{(f'{wu*100:.0f}%' if wu else '—'):>8}{r[7][3]:>10,.0f}{act:>16}")
print("\n■ 処置別のまとめ")
for a in ['🚨 停止 or −50%','🔻 −25%','🚀 +25%','⏸ 据え置き','✅ 維持']:
    g=[(n,r,why) for n,r,be,tg,wu,act,why,bl,ab in out if act==a]
    if not g: continue
    print(f"\n {a}（{len(g)}件）")
    for n,r,why in sorted(g,key=lambda x:x[1][7][3]):
        print(f"   {n[:22]:22} 3日{r[3][4]:.2f} / 5日{r[5][4]:.2f} / 7日{r[7][4]:.2f}  7日利益 {r[7][3]:>9,.0f}円  {why}")
print("\n■ 全店の3窓")
for w,days in W.items():
    s=sum(sum(S[n][d][0]-S[n][d][1] for d in days if d in S[n]) for n in S)
    a=sum(AD[c].get(d,0) for c in AD for d in days)
    k=sum(blk(n,days)[1] for n in S if n in PRICE and n in COST)
    print(f"  {w}日({days[0]}〜{days[-1]})  実売 {s:>10,.0f} 原価 {k:>9,.0f} 広告 {a:>10,.0f} 利益 {s-k-a:>9,.0f} 利益率 {(s-k-a)/s*100:>5.2f}% MER {s/a:.2f}")
