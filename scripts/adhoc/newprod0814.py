# -*- coding: utf-8 -*-
"""次に何を出すべきか: 自店の実測から「勝ちパターン」を数字で抽出する。
売上/個数/注文 = Shopify実測、広告費 = Meta実測（daily CSVは検証済みの正）。
"""
import csv, collections, sys
sys.path.insert(0,'/home/user/LOOana/scripts/daily')
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
'瞬間冷却ハンディファン':2053,'完全遮光・接触冷感UVハット':1411,'ナノバブルシャワーヘッド':2255,
'リカバリーサンダル':1309,'スマートノーズEMS美顔器':2453,'W固定スマホ車載ホルダー':1182,
'ジェットウォッシャー':1259,'姿勢サポートチェア':1811,'2WAYシートボックス':1943,'快適マジックインソール':677,
'ナノガラス脱毛パッド':750,'壁掛けディスペンサー':2400}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'携帯電動シェーバー':4980,
'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,'瞬間冷却ハンディファン':5980,
'完全遮光・接触冷感UVハット':4980,'ナノバブルシャワーヘッド':6980,'リカバリーサンダル':3980,
'スマートノーズEMS美顔器':5980,'W固定スマホ車載ホルダー':3980,'ジェットウォッシャー':4980,
'姿勢サポートチェア':5980,'2WAYシートボックス':4980,'快適マジックインソール':3980,
'ナノガラス脱毛パッド':3980,'ムダ毛シェーバー':6980,'壁掛けディスペンサー':6980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
# Shopify実測の注文数（8/01-13, GROUP BY product_title で1本取得）
ORD={'ナノガラス脱毛パッド':580,'4WAY':181,'害虫ブロッカー':185,'形状記憶日傘':185,'接触冷感UVパーカー':201,
'W固定スマホ車載ホルダー':200,'ムダ毛シェーバー':99,'完全遮光・形状記憶':114,'5WAY腰掛けファン':81,
'偏光・調光サングラス':100,'卓上冷感クーラー':50,'2WAYシートボックス':56,'完全遮光・接触冷感UVハット':57,
'姿勢サポートチェア':35,'接触冷感UVアームカバー':51,'携帯電動シェーバー':38,'3WAYサーキュレーター':21,
'瞬間冷感ポンチョ':26,'バランスケアスリッパ':20,'健康サンダル':17,'快適マジックインソール':16,
'UV歯ブラシ除菌器':6,'壁掛けディスペンサー':4,'湯上がりガーゼワンピース':3,'ナノバブルシャワーヘッド':2,
'ジェットウォッシャー':2,'リカバリーサンダル':1,'瞬間冷却ハンディファン':1,'スマートノーズEMS美顔器':1}
SEASON=set('4WAY 害虫ブロッカー 形状記憶日傘 完全遮光・形状記憶 卓上冷感クーラー 接触冷感UVパーカー '
 '5WAY腰掛けファン 偏光・調光サングラス 3WAYサーキュレーター 接触冷感UVアームカバー 健康サンダル '
 '瞬間冷感ポンチョ 湯上がりガーゼワンピース 瞬間冷却ハンディファン 完全遮光・接触冷感UVハット'.split())
DAYS=[f'2026-08-{i:02d}' for i in range(1,14)]
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
rows=[]
for n in ORD:
    g=sum(S[n][d][0] for d in DAYS if d in S[n]); dc=sum(S[n][d][1] for d in DAYS if d in S[n])
    if not g: continue
    c=sum(AD[MAP.get(n,n)].get(d,0) for d in DAYS)
    q=round(g/PRICE[n]); net=g-dc; prof=net-q*COST[n]-c
    rows.append(dict(n=n,net=net,q=q,od=ORD[n],c=c,prof=prof,
        rate=COST[n]/PRICE[n], p=PRICE[n], ipo=q/ORD[n],
        mer=net/c if c else None, roi=prof/c if c else None,
        gp_ord=(PRICE[n]-COST[n])*q/ORD[n], season=n in SEASON))
print('【8/01-13 実測】広告を出している商品を「広告1円あたり利益」で並べる')
h=f"{'商品':<22}{'季/通':<5}{'売価':>6}{'原価率':>7}{'点/注':>6}{'粗利/注文':>9}{'広告費':>9}{'実売':>10}{'MER':>6}{'利益':>10}{'利益率':>7}{'広1円利益':>9}"
print(h); print('='*118)
for r in sorted([x for x in rows if x['c']>3000], key=lambda x:-x['roi']):
    print(f"{r['n']:<22}{'季' if r['season'] else '通':<5}{r['p']:>6,}{r['rate']:>7.1%}{r['ipo']:>6.2f}"
          f"{r['gp_ord']:>9,.0f}{r['c']:>9,.0f}{r['net']:>10,}{r['mer']:>6.2f}{r['prof']:>+10,.0f}"
          f"{r['prof']/r['net']:>7.1%}{r['roi']:>+9.2f}")
print()
adv=[x for x in rows if x['c']>3000]
for lbl,sel in [('季節（9月に消える）',[x for x in adv if x['season']]),('通年（9月も残る）',[x for x in adv if not x['season']])]:
    c=sum(x['c'] for x in sel); p=sum(x['prof'] for x in sel); n=sum(x['net'] for x in sel)
    print(f"{lbl:<20} {len(sel)}品  広告{c:>9,.0f}  実売{n:>10,}  利益{p:>+10,.0f} ({p/n:>5.1%})  週あたり利益 {p/13*7:>+9,.0f}円")
print()
print('【新商品の立ち上がり】配信開始からの日別利益（値引・原価・広告費を引いた実額）')
LAUNCH={'5WAY腰掛けファン':'2026-07-19','完全遮光・接触冷感UVハット':'2026-07-31',
        'W固定スマホ車載ホルダー':'2026-08-01','姿勢サポートチェア':'2026-08-04',
        '2WAYシートボックス':'2026-08-06','快適マジックインソール':'2026-08-11'}
ALL=sorted({d for v in S.values() for d in v})
for n,st in LAUNCH.items():
    ds=[d for d in ALL if d>=st][:13]
    cum=0; seq=[]
    for d in ds:
        g=S[n][d][0] if d in S[n] else 0; dc=S[n][d][1] if d in S[n] else 0
        c=AD[MAP.get(n,n)].get(d,0); q=round(g/PRICE[n])
        cum+=(g-dc)-q*COST[n]-c; seq.append(cum)
    print(f"  {n:<22}({st[5:]}開始, {len(ds):>2}日) 累積利益 " + ' '.join(f'{v/1000:>+6.0f}k' for v in seq))

print()
print('【CPAで並べ直す】勝敗を決めているのは「粗利/注文 ÷ CPA」（＝1注文あたり何倍取れているか）')
h2=f"{'商品':<22}{'季/通':<5}{'原価率':>7}{'粗利/注文':>9}{'CPA':>8}{'倍率':>7}{'広1円利益':>9}"
print(h2); print('='*70)
for r in sorted(adv, key=lambda x:-(x['gp_ord']/(x['c']/x['od']))):
    cpa=r['c']/r['od']
    print(f"{r['n']:<22}{'季' if r['season'] else '通':<5}{r['rate']:>7.1%}{r['gp_ord']:>9,.0f}"
          f"{cpa:>8,.0f}{r['gp_ord']/cpa:>7.2f}{r['roi']:>+9.2f}")
print()
print('【9月の崖を埋めるのに何品必要か】新商品の「直近7日」の利益ペース')
for n,st in LAUNCH.items():
    ds=[d for d in ALL if d>=st][-7:]
    p=0
    for d in ds:
        g=S[n][d][0] if d in S[n] else 0; dc=S[n][d][1] if d in S[n] else 0
        c=AD[MAP.get(n,n)].get(d,0); p+=(g-dc)-round(g/PRICE[n])*COST[n]-c
    print(f"  {n:<22} 直近{len(ds)}日 {p:>+9,.0f}円 → 週換算 {p/len(ds)*7:>+9,.0f}円")
seas=sum(x['prof'] for x in adv if x['season'])/13*7
print(f"\n  9月に消える季節13品の週利益 = {seas:>+,.0f}円")
med=98000
print(f"  新商品1品の週利益（上のレンジの中央値めやす）≒ {med:,}円 → 埋めるのに必要な品数 ≒ {seas/med:.1f}品")
