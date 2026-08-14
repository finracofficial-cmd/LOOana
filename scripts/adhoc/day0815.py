# -*- coding: utf-8 -*-
"""2026-08-14 の実績と、8/15の今時点。あわせて 8/15 が判定日の2件（害虫・インソール）。"""
import csv, collections, datetime, sys
B = '/home/user/LOOana/data/daily/'
sys.path.insert(0, '/home/user/LOOana/scripts/daily')
COST = {'瞬間冷却ハンディファン':2053,'ネックマッサージャー':3034,'リカバリーサンダル':1309,
 'ナノバブルシャワーヘッド':2255,'姿勢サポートベルト':1429,'癒しの指圧マット':1648,
 'スマートノーズEMS美顔器':2453,'ジェットウォッシャー':1259,'スタイルアップインナー':1202,
 '保温プレート':3703,'オートソープディスペンサー':3191,'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
 '接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
 '接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
 '携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,'UV歯ブラシ除菌器':3240,
 '優先配送':0,'完全遮光・接触冷感UVハット':1411,'W固定スマホ車載ホルダー':1182,'姿勢サポートチェア':1811,
 '2WAYシートボックス':1943,'快適マジックインソール':677,'ナノガラス脱毛パッド':750,'壁掛けディスペンサー':2400}
PRICE = {'瞬間冷却ハンディファン':5980,'ネックマッサージャー':9980,'リカバリーサンダル':3980,
 'ナノバブルシャワーヘッド':6980,'姿勢サポートベルト':5980,'癒しの指圧マット':5980,
 'スマートノーズEMS美顔器':5980,'ジェットウォッシャー':4980,'スタイルアップインナー':3980,
 '保温プレート':7980,'オートソープディスペンサー':5980,'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
 '接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':6980,
 '接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'ムダ毛シェーバー':6980,
 '携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,'UV歯ブラシ除菌器':8980,
 '優先配送':536,'完全遮光・接触冷感UVハット':4980,'W固定スマホ車載ホルダー':3980,'姿勢サポートチェア':5980,
 '2WAYシートボックス':4980,'快適マジックインソール':3980,'ナノガラス脱毛パッド':3980,'壁掛けディスペンサー':6980}
MAP = {'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
 '3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open(B + 'daily_sales.csv', encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B + 'daily_ad.csv', encoding='utf-8')):
    AD[r['campaign']][r['date']] += float(r['cost'])
ad = lambda n, ds: sum(AD[MAP.get(n, n)].get(d, 0) for d in ds)

WD = '月火水木金土日'
def wd(d): return WD[datetime.date(*map(int, d.split('-'))).weekday()]
HOL = {'2026-07-20', '2026-08-11'}
ALL = sorted({d for v in S.values() for d in v})
STORE = {d: sum(v[d][0] - v[d][1] for v in S.values() if d in v) for d in ALL}

print('■ 直近7日の全体（実売＝gross−値引 / 広告＝Meta実測）')
print(f"{'日付':<12}{'曜':<3}{'実売':>10}{'広告費':>9}{'MER':>6}{'原価':>9}{'利益':>10}{'利益率':>8}{'vs同曜日':>9}")
base = [d for d in ALL[-31:-1] if d not in HOL]
byw = collections.defaultdict(list)
for d in base: byw[wd(d)].append(STORE[d])
for d in ALL[-7:]:
    q = {}
    for n, v in S.items():
        if n == '' or d not in v or v[d][0] == 0: continue
        g = v[d][0]
        if n not in PRICE: continue
        q[n] = round(g / PRICE[n])
    cst = sum(q[n] * COST[n] for n in q)
    c = sum(sum(AD[cp].get(d, 0) for cp in AD) for d in [d])
    net = STORE[d]; prof = net - cst - c
    avg = sum(byw[wd(d)]) / len(byw[wd(d)])
    print(f"{d:<12}{wd(d):<3}{net:>10,}{c:>9,.0f}{net/c:>6.2f}{cst:>9,}{prof:>+10,.0f}"
          f"{prof/net:>8.1%}{net/avg-1:>+9.1%}")

print('\n■ 2026-08-14 の商品別（広告を出している商品）')
d = '2026-08-14'
print(f"{'商品':<22}{'実売':>9}{'個':>4}{'広告費':>9}{'MER':>6}{'分岐':>6}{'余裕':>7}{'利益':>9}{'CPA':>7}")
rows = []
for n, v in S.items():
    if n == '' or d not in v or v[d][0] == 0: continue
    g, dc = v[d]; qn = round(g / PRICE[n]); c = ad(n, [d])
    net = g - dc; prof = net - qn * COST[n] - c
    br = 1 / (1 - COST[n] / PRICE[n])
    rows.append((n, net, qn, c, prof, br))
for n, net, qn, c, prof, br in sorted(rows, key=lambda x: -x[4]):
    if c < 500:
        print(f"{n:<22}{net:>9,}{qn:>4}{'—':>9}{'—':>6}{'—':>6}{'—':>7}{prof:>+9,.0f}{'—':>7}")
    else:
        print(f"{n:<22}{net:>9,}{qn:>4}{c:>9,.0f}{net/c:>6.2f}{br:>6.2f}{net/c-br:>+7.2f}{prof:>+9,.0f}{c/qn:>7,.0f}")
tot_net = sum(r[1] for r in rows); tot_c = sum(r[3] for r in rows); tot_p = sum(r[4] for r in rows)
cat = AD['カタログ全部（テスト）'].get(d, 0)
print(f"{'カタログ全部（テスト）':<22}{'—':>9}{'—':>4}{cat:>9,.0f}")
print(f"\n  Σ商品利益 {tot_p:+,.0f} − カタログ {cat:,.0f} = 全体利益 {tot_p-cat:+,.0f}（利益率 {(tot_p-cat)/tot_net:.1%}）")
print(f"  広告費合計 {tot_c+cat:,.0f}  全店実売 {STORE[d]:,}  MER {STORE[d]/(tot_c+cat):.2f}")

print('\n■ 8/15 が判定日の2件')
h3 = ['2026-08-12', '2026-08-13', '2026-08-14']
for n, note in [('害虫ブロッカー', '3日MER≥1.58で据え置き / 1.28-1.58で−25% / <1.28で停止・−50%'),
                ('快適マジックインソール', '中間: 外部CTR<2.2% または RPM/CPM<0.7 で停止')]:
    g = sum(S[n][x][0] for x in h3 if x in S[n]); dc = sum(S[n][x][1] for x in h3 if x in S[n])
    qn = round(g / PRICE[n]); c = ad(n, h3); net = g - dc
    br = 1 / (1 - COST[n] / PRICE[n]); prof = net - qn * COST[n] - c
    print(f"  {n}  3日(8/12-14)  実売{net:,} / {qn}個 / 広告{c:,.0f} / MER {net/c:.2f}（分岐{br:.2f}）/ 利益{prof:+,.0f}")
    print(f"    基準: {note}")
