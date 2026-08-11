# -*- coding: utf-8 -*-
"""季節商品の週次MERトレンドと「1円あたり利益」の窓別感度。"""
import csv,collections,pickle,datetime
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
COST=dict(R['COST']); PRICE=dict(R['PRICE']); MAP=R['MAP']
COST['ナノガラス脱毛パッド']=(835*757+364*740)/1199
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['campaign']][r['date']]+=float(r['cost'])
end=datetime.date(2026,8,10); WK=[]
for i in range(5):
    a=end-datetime.timedelta(days=7*i+6)
    WK.append((f"{a.strftime('%m/%d')}-{(a+datetime.timedelta(days=6)).strftime('%m/%d')}",
               [(a+datetime.timedelta(days=j)).isoformat() for j in range(7)]))
WK.reverse()
SEA=['5WAY腰掛けファン','卓上冷感クーラー','4WAY','接触冷感UVパーカー','接触冷感UVアームカバー',
     '完全遮光・接触冷感UVハット','形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','害虫ブロッカー']
print("■ 季節商品の週次MER（Shopify実売 ÷ Meta広告費）  ※SKILL基準: 2週連続−15%以上 かつ 残4週以下 → 前倒し縮小")
print(f"{'商品':22}"+''.join(f"{w[0]:>13}" for w in WK)+f"{'直近2週の変化':>16}{'残週':>6}{'判定':>10}")
REM={'5WAY腰掛けファン':4,'卓上冷感クーラー':4,'4WAY':4,'接触冷感UVパーカー':5,'接触冷感UVアームカバー':5,
     '完全遮光・接触冷感UVハット':5,'形状記憶日傘':6,'完全遮光・形状記憶':6,'偏光・調光サングラス':6,'害虫ブロッカー':8}
for n in SEA:
    v=[]
    for lbl,days in WK:
        g=sum(S[n][d][0] for d in days if d in S[n]); dc=sum(S[n][d][1] for d in days if d in S[n])
        a=sum(AD[MAP.get(n,n)].get(d,0) for d in days)
        v.append((g-dc)/a if a else 0)
    c1=(v[-1]/v[-2]-1)*100 if v[-2] else 0; c2=(v[-2]/v[-3]-1)*100 if v[-3] else 0
    trig='🚨前倒し縮小' if (c1<=-15 and c2<=-15 and REM[n]<=4) else '—'
    print(f"{n[:22]:22}"+''.join(f"{x:>13.2f}" for x in v)+f"{c2:>+8.1f}%{c1:>+7.1f}%{REM[n]:>6}{trig:>10}")
print("\n■ 5WAYと卓上：『広告費1円あたり利益』を窓別×限界MER係数で総当たり")
print("   （1円あたり利益 = 限界MER × 粗利率 − 1。正なら出すほど利益が増える＝削ってはいけない）")
W={3:[(end-datetime.timedelta(days=i)).isoformat() for i in range(2,-1,-1)],
   5:[(end-datetime.timedelta(days=i)).isoformat() for i in range(4,-1,-1)],
   7:[(end-datetime.timedelta(days=i)).isoformat() for i in range(6,-1,-1)]}
for n in ['5WAY腰掛けファン','卓上冷感クーラー','接触冷感UVパーカー']:
    print(f"\n  【{n}】")
    print(f"   {'窓':>6}{'MER':>7}{'分岐':>7}{'×0.6':>9}{'×0.7':>9}{'×0.8':>9}")
    for w,days in W.items():
        g=sum(S[n][d][0] for d in days if d in S[n]); dc=sum(S[n][d][1] for d in days if d in S[n])
        a=sum(AD[MAP.get(n,n)].get(d,0) for d in days); s=g-dc
        k=g/PRICE[n]*COST[n]; gm=1-k/s; mer=s/a; be=1/gm
        cells=''.join(f"{mer*f*gm-1:>+9.3f}" for f in (0.6,0.7,0.8))
        print(f"   {w:>5}日{mer:>7.2f}{be:>7.2f}{cells}")
    print(f"   → 窓・係数の9通りで符号が{'割れる＝据え置き' if True else ''}かを見る")
