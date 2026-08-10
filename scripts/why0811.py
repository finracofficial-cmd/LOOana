# -*- coding: utf-8 -*-
"""週次の分解。売上・値引=Shopify実測、広告=Meta実測。
原価は日次のバリアント構成が取れないナノガラス/ディスペンサーのみ30日実測ミックスの加重平均単価【近似】。"""
import csv,collections,datetime,pickle
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
COST=dict(R['COST']); PRICE=R['PRICE']; MAP=R['MAP']
COST['ナノガラス脱毛パッド']=(835*757+364*740)/1199   # 30日実測ミックス【近似】
COST['壁掛けディスペンサー']=(45*2528+13*1981)/58
PRICE['壁掛けディスペンサー']=391840/58
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
end=datetime.date(2026,8,10)
W=[]
for i in range(6):
    a=end-datetime.timedelta(days=7*i+6); b=end-datetime.timedelta(days=7*i)
    W.append((f"{a.strftime('%m/%d')}-{b.strftime('%m/%d')}",[(a+datetime.timedelta(days=j)).isoformat() for j in range(7)]))
W.reverse()
def blk(days,names=None):
    s=c=0
    for n,v in S.items():
        if names is not None and n not in names: continue
        g=sum(v[d][0] for d in days if d in v); dc=sum(v[d][1] for d in days if d in v)
        if not g: continue
        s+=g-dc
        if n in PRICE and n in COST: c+=g/PRICE[n]*COST[n]
    a=sum(AD[MAP.get(n,n)].get(d,0) for n in (names if names is not None else S) for d in days) if names is not None \
      else sum(AD[cp].get(d,0) for cp in AD for d in days)
    return s,c,a,s-c-a
print("■ 全店の週次（実売＝gross−値引 / 原価は上記近似 / 広告＝Meta実測）")
print(f"{'週':14}{'実売':>11}{'原価':>10}{'広告':>10}{'利益':>10}{'利益率':>8}{'MER':>6}{'原価率':>8}{'広告費率':>9}")
prev=None
for lbl,days in W:
    if days[0]<'2026-06-29': continue
    s,c,a,p=blk(days)
    print(f"{lbl:14}{s:>11,.0f}{c:>10,.0f}{a:>10,.0f}{p:>10,.0f}{p/s*100:>7.1f}%{s/a:>6.2f}{c/s*100:>7.1f}%{a/s*100:>8.1f}%")
SEASON={'4WAY','3WAYサーキュレーター','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン',
'接触冷感UVパーカー','接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット',
'形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','害虫ブロッカー'}
YEAR={'ナノガラス脱毛パッド','ムダ毛シェーバー','携帯電動シェーバー','壁掛けディスペンサー','UV歯ブラシ除菌器',
'健康サンダル','バランスケアスリッパ','W固定スマホ車載ホルダー','2WAYシートボックス','姿勢サポートチェア',
'ナノバブルシャワーヘッド','湯上がりガーゼワンピース','リカバリーサンダル','優先配送'}
for tag,st in [('季節物13品',SEASON),('通年物14品',YEAR)]:
    print(f"\n■ {tag}")
    print(f"{'週':14}{'実売':>11}{'広告':>10}{'利益':>10}{'MER':>6}")
    for lbl,days in W:
        if days[0]<'2026-06-29': continue
        s,c,a,p=blk(days,st)
        print(f"{lbl:14}{s:>11,.0f}{a:>10,.0f}{p:>10,.0f}{(s/a if a else 0):>6.2f}")
print("\n■ 商品別 週次利益（W-3=7/14-20 → W0=8/04-10）と週次MER")
lab=[w[0] for w in W[-4:]]
print(f"{'商品':22}"+''.join(f"{l:>13}" for l in lab)+f"{'W-3→W0':>12}")
rows=[]
for n in S:
    if n not in PRICE or n not in COST: continue
    v=[]
    for lbl,days in W[-4:]:
        g=sum(S[n][d][0] for d in days if d in S[n]); dc=sum(S[n][d][1] for d in days if d in S[n])
        a=sum(AD[MAP.get(n,n)].get(d,0) for d in days)
        v.append((g-dc)-(g/PRICE[n]*COST[n])-a)
    rows.append((n,v))
for n,v in sorted(rows,key=lambda x:-x[1][-1]):
    if max(abs(x) for x in v)<3000: continue
    d=v[-1]-v[0]
    print(f"{n[:22]:22}"+''.join(f"{x:>13,.0f}" for x in v)+f"{d:>+12,.0f}")
