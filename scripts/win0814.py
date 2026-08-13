# -*- coding: utf-8 -*-
"""3窓判定（3日/5日/7日・すべて 2026-08-12 終端）。CSV実測のみ。"""
import csv, collections, sys
sys.path.insert(0,'scripts/daily')
B='data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,'携帯電動シェーバー':1743,
'バランスケアスリッパ':1304,'優先配送':0,'完全遮光・接触冷感UVハット':1411,'W固定スマホ車載ホルダー':1182,
'姿勢サポートチェア':1811,'2WAYシートボックス':1943,'快適マジックインソール':677,'ナノガラス脱毛パッド':752}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':4980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
'接触冷感UVアームカバー':3980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,
'完全遮光・接触冷感UVハット':4980,'優先配送':536,'ナノガラス脱毛パッド':3980,'ムダ毛シェーバー':6980,
'W固定スマホ車載ホルダー':3980,'姿勢サポートチェア':5980,'2WAYシートボックス':4980,'快適マジックインソール':3980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機'}
BUD={'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':36000,'形状記憶日傘':35000,'接触冷感UVパーカー':30000,
'害虫ブロッカー':37000,'4WAY':11800,'ムダ毛シェーバー':20000,'偏光・調光サングラス':16500,'5WAY腰掛けファン':14000,
'完全遮光・形状記憶':15750,'2WAYシートボックス':18000,'快適マジックインソール':12000,
'完全遮光・接触冷感UVハット':12000,'姿勢サポートチェア':10000,'接触冷感UVアームカバー':8000,
'卓上冷感クーラー':5000,'バランスケアスリッパ':5000}
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv')): AD[r['campaign']][r['date']]+=float(r['cost'])
ALLD=sorted({d for v in S.values() for d in v}); assert ALLD[-1]=='2026-08-13', ALLD[-1]
WINS={'3日':ALLD[-3:],'5日':ALLD[-5:],'7日':ALLD[-7:]}
print(f"窓: 3日={WINS['3日'][0]}〜{WINS['3日'][-1]} / 5日={WINS['5日'][0]}〜 / 7日={WINS['7日'][0]}〜\n")
def calc(n,days):
    g=sum(S[n][d][0] for d in days if d in S[n]); di=sum(S[n][d][1] for d in days if d in S[n])
    ad=sum(AD[MAP.get(n,n)][d] for d in days)
    q=round(g/PRICE[n]) if PRICE.get(n) else 0; c=q*COST[n]; rev=g-di
    return dict(rev=rev,ad=ad,c=c,q=q,pr=rev-c-ad,
        mer=rev/ad if ad else None, be=rev/(rev-c) if rev>c else None,
        tg=1/(1-c/rev-0.35) if rev and (1-c/rev-0.35)>0 else None,
        sh=ad/(BUD[n]*len(days)) if n in BUD else None)
def judge(n):
    r={k:calc(n,d) for k,d in WINS.items()}
    be=[r[k]['mer']<r[k]['be'] for k in WINS if r[k]['mer'] and r[k]['be']]
    mg=[(r[k]['mer']-r[k]['be'])<0.30 for k in WINS if r[k]['mer'] and r[k]['be']]
    up=[r[k]['tg'] and r[k]['mer']>=r[k]['tg'] for k in WINS]
    if all(be) and len(be)==3: v='🚨 3窓すべて分岐割れ → 停止/−50%'
    elif all(mg) and len(mg)==3: v='⚠️ 3窓すべて余裕<0.30 → −25%'
    elif all(up) and r['7日']['sh'] and r['7日']['sh']>=0.95: v='✅ 3窓すべて目標超＋消化95%↑ → +25%'
    else: v='➖ 窓で割れる → 据え置き'
    return r,v
TARGETS=['ナノガラス脱毛パッド','接触冷感UVアームカバー','形状記憶日傘','完全遮光・形状記憶','ムダ毛シェーバー','4WAY','5WAY腰掛けファン',
'偏光・調光サングラス','ナノガラス脱毛パッド','2WAYシートボックス','快適マジックインソール','姿勢サポートチェア',
'害虫ブロッカー','W固定スマホ車載ホルダー','完全遮光・接触冷感UVハット','卓上冷感クーラー',
'バランスケアスリッパ']
for n in TARGETS:
    r,v=judge(n)
    print(f"■ {n}   日予算 {BUD.get(n,0):,}円   {v}")
    print(f"   {'窓':4}{'売上':>10}{'広告費':>10}{'利益':>10}{'利益率':>8}{'MER':>7}{'分岐':>6}{'目標':>6}{'余裕':>7}{'消化':>7}")
    for k in ['3日','5日','7日']:
        x=r[k]; m=f"{x['mer']:.2f}" if x['mer'] else '—'; b=f"{x['be']:.2f}" if x['be'] else '—'
        t=f"{x['tg']:.2f}" if x['tg'] else '—'
        mar=f"{x['mer']-x['be']:+.2f}" if x['mer'] and x['be'] else '—'
        sh=f"{x['sh']*100:.0f}%" if x['sh'] else '—'
        pct=f"{x['pr']/x['rev']*100:6.1f}%" if x['rev'] else '     —'
        print(f"   {k:4}{x['rev']:10,.0f}{x['ad']:10,.0f}{x['pr']:10,.0f}{pct}{m:>7}{b:>6}{t:>6}{mar:>7}{sh:>7}")
    print()
