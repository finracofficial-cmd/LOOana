# -*- coding: utf-8 -*-
"""2026-08-16 の定例。前日=2026-08-15。

⚠️ Meta（Supermetrics）が全エンドポイントで応答しないため、8/15の広告費は取得不可。
   → 8/15を終端とする利益・MER・CPAは一切算出しない。
   → 意思決定に使う窓は 8/14終端（広告費が揃っている最後の日）に据え置く。
   8/15について出せるのは Shopify実測（売上・販売数・注文・粗利）まで。

売上・値引 = data/daily/daily_sales.csv（Shopify実測）
広告費     = data/daily/daily_ad.csv（Meta実測・8/14まで）
"""
import csv, collections, datetime, runpy

B = '/home/user/LOOana/data/daily/'
COST = {'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,
 '卓上冷感クーラー':1996,'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,
 '3WAYサーキュレーター':2485,'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,
 'ムダ毛シェーバー':2798,'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'湯上がりガーゼワンピース':1968,
 'UV歯ブラシ除菌器':3240,'完全遮光・接触冷感UVハット':1411,'W固定スマホ車載ホルダー':1182,
 '姿勢サポートチェア':1811,'2WAYシートボックス':1943,'快適マジックインソール':677,
 'ナノバブルシャワーヘッド':2255,'瞬間冷却ハンディファン':2053,'リカバリーサンダル':1309,
 'スマートノーズEMS美顔器':2453,'ジェットウォッシャー':1259,'優先配送':0}
PRICE = {'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,
 '卓上冷感クーラー':5980,'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,
 '3WAYサーキュレーター':6980,'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,
 'ムダ毛シェーバー':6980,'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'湯上がりガーゼワンピース':5980,
 'UV歯ブラシ除菌器':8980,'完全遮光・接触冷感UVハット':4980,'W固定スマホ車載ホルダー':3980,
 '姿勢サポートチェア':5980,'2WAYシートボックス':4980,'快適マジックインソール':3980,
 'ナノバブルシャワーヘッド':6980,'瞬間冷却ハンディファン':5980,'リカバリーサンダル':3980,
 'スマートノーズEMS美顔器':5980,'ジェットウォッシャー':4980,'優先配送':536}
# 2026-08-15 のバリアント別 gross（ShopifyQL実測・product_type='脱毛器'）
NANO0815 = {'白緑': 151240 + 31840, '黒桃': 27860 + 11940}
NANOC = (757, 740)
assert sum(NANO0815.values()) == 222880

HOL = {'2026-07-20', '2026-08-11'}
WD = ['月','火','水','木','金','土','日']
wd = lambda d: WD[datetime.date(*map(int, d.split('-'))).weekday()]

S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open(B + 'daily_sales.csv', encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B + 'daily_ad.csv', encoding='utf-8')):
    AD[r['campaign']][r['date']] += float(r['cost'])

ALLD = sorted({d for v in S.values() for d in v})
NET = {d: sum(v[d][0] - v[d][1] for v in S.values() if d in v) for d in ALLD}
ADD = {d: sum(AD[c].get(d, 0) for c in AD) for d in ALLD}
LAST = ALLD[-1]
print(f'■ データの状態')
print(f'  Shopify売上   〜 {LAST}（8/15を追記済み）')
print(f'  Meta広告費    〜 {max(d for d in ALLD if ADD[d] > 0)}（8/15は取得不可）')

# ── 曜日指数（直近30日・祝日除外） ────────────────────────────────────────
base = [d for d in ALLD if d <= '2026-08-15'][-30:]
byw = collections.defaultdict(list)
for d in base:
    if d not in HOL: byw[wd(d)].append(NET[d])
avg = sum(sum(v) for v in byw.values()) / sum(len(v) for v in byw.values())
IDX = {k: sum(v) / len(v) / avg * 100 for k, v in byw.items()}
print(f'\n■ 曜日指数（直近30日 {base[0]}〜{base[-1]}・祝日除外・全体平均=100）')
print('  ' + ' / '.join(f'{k}{v:.1f}' for k, v in sorted(IDX.items(), key=lambda x: -x[1])))

# ── 8/15 の全店（Shopifyのみ） ────────────────────────────────────────────
D0 = '2026-08-15'
sat = [d for d in base if wd(d) == '土' and d not in HOL and d != D0]
d7 = [d for d in ALLD if '2026-08-08' <= d <= '2026-08-14']
d30 = [d for d in ALLD if d >= '2026-07-17'][-30:]
print(f'\n■ 8/15（土）の全店 ── Shopify実測のみ')
print(f'  {"":<22}{"実売(gross−値引)":>18}{"販売点数":>10}{"注文":>8}')
print(f'  {"8/15（土）":<22}{NET[D0]:>18,}{183:>10}{142:>8}')
print(f'  {"非祝日の土曜平均":<22}{sum(NET[d] for d in sat)/len(sat):>18,.0f}{"":>10}{"":>8}   n={len(sat)}')
print(f'  {"直近7日平均/日":<22}{sum(NET[d] for d in d7)/7:>18,.0f}')
print(f'  {"直近30日平均/日":<22}{sum(NET[d] for d in d30)/30:>18,.0f}')
sa = sum(NET[d] for d in sat) / len(sat)
print(f'\n  同曜日比 {NET[D0]/sa-1:+.1%} ／ 7日平均比 {NET[D0]/(sum(NET[d] for d in d7)/7)-1:+.1%}')

# ── 8/15 商品別（粗利まで。広告費が無いので利益は出さない） ──────────────
print(f'\n■ 8/15 商品別（Shopify実測）── 広告費が取れないため利益・MERは出さない')
rows = []
for n in S:
    if D0 not in S[n]: continue
    g, dc = S[n][D0]
    if n == 'ナノガラス脱毛パッド':
        q = sum(v / 3980 for v in NANO0815.values())
        cost = NANO0815['白緑'] / 3980 * NANOC[0] + NANO0815['黒桃'] / 3980 * NANOC[1]
    else:
        p = PRICE[n]; q = g / p
        assert abs(q - round(q)) < 1e-6, f'{n}: gross {g} が売価 {p} で割り切れない'
        q = round(q); cost = q * COST[n]
    rows.append(dict(n=n, net=g - dc, q=q, cost=cost, gp=(g - dc) - cost))
print(f'  {"商品":<26}{"実売":>10}{"販売数":>7}{"原価":>10}{"粗利":>10}{"粗利率":>8}')
for r in sorted(rows, key=lambda x: -x['net']):
    print(f'  {r["n"]:<26}{r["net"]:>10,}{r["q"]:>7.0f}{r["cost"]:>10,.0f}{r["gp"]:>10,.0f}{r["gp"]/r["net"]:>8.1%}')
tg, tc = sum(r['net'] for r in rows), sum(r['cost'] for r in rows)
print(f'  {"合計":<26}{tg:>10,}{sum(r["q"] for r in rows):>7.0f}{tc:>10,.0f}{tg-tc:>10,.0f}{(tg-tc)/tg:>8.1%}')
assert tg == NET[D0], (tg, NET[D0])
print(f'  ※ 縦照合OK（Σ商品 = 全店 {NET[D0]:,}円）')

# ── 参考: 直近7日（8/09-15）の粗利。広告費が無いので"粗利まで" ────────────
W = [d for d in ALLD if '2026-08-09' <= d <= '2026-08-15']
print(f'\n■ 参考: 8/09-15 の7日（Shopify実測・粗利まで）')
tot_net = sum(NET[d] for d in W)
prev = [d for d in ALLD if '2026-08-02' <= d <= '2026-08-08']
print(f'  実売 {tot_net:,}円（前週 8/02-08 {sum(NET[d] for d in prev):,}円 / {tot_net/sum(NET[d] for d in prev)-1:+.1%}）')
print(f'  1日あたり {tot_net/7:,.0f}円')

# ── 8/14終端の窓（意思決定はここを使う） ──────────────────────────────────
print(f'\n■ 意思決定に使う窓（8/14終端・広告費が揃っている最後の日）')
g = runpy.run_path('scripts/daily/w0814.py')

N1, N3, N7, N30 = g['N1'], g['N3'], g['N7'], g['N30']
K1, K3, K7, K30 = g['K1'], g['K3'], g['K7'], g['K30']
A, ACCT, CAT = g['A'], g['ACCT'], g['CAT']
A7 = {n: A(g['D7'], n) for n in N7}

def blk(N, K, days, lbl):
    net = sum(N.values()); cost = sum(K.values()); ad = ACCT(days)
    pr = net - cost - ad
    print(f"  {lbl:<10}{net:>12,}{cost:>12,.0f}{ad:>12,.0f}{pr:>+12,.0f}{pr/net:>8.1%}"
          f"{net/ad:>7.2f}{1/(1-cost/net):>7.2f}{net/ad-1/(1-cost/net):>+7.2f}")
print(f'  {"窓":<10}{"実売":>12}{"原価":>12}{"広告費":>12}{"利益":>12}{"利益率":>8}{"MER":>7}{"分岐":>7}{"余裕":>7}')
blk(N1, K1, g['D1'], '前日8/14')
blk(N3, K3, g['D3'], '3日')
blk(N7, K7, g['D7'], '7日')
blk(N30, K30, g['D30'], '30日')

print(f"\n■ 商品別（7日 8/08-14・Shopify実測 × Meta実測）")
print(f'  {"商品":<26}{"実売":>10}{"原価":>9}{"広告費":>10}{"利益":>10}{"MER":>6}{"分岐":>6}{"余裕":>7}{"1円利益":>8}')
out = []
for n in sorted(N7, key=lambda x: -N7[x]):
    net = N7[n]; cost = K7.get(n, 0); ad = A7.get(n, 0)
    if net <= 0: continue
    be = 1 / (1 - cost / net) if net > cost else float('inf')
    if ad > 0:
        mer = net / ad; per = 1 - mer * 0.7 * (1 - cost / net)
        out.append((n, net, cost, ad, net - cost - ad, mer, be, mer - be, -per))
    else:
        out.append((n, net, cost, 0, net - cost, None, be, None, None))
for n, net, cost, ad, pr, mer, be, yo, per in out:
    m = f'{mer:>6.2f}' if mer else '     —'
    y = f'{yo:>+7.2f}' if yo is not None else '      —'
    pp = f'{per:>+8.3f}' if per is not None else '       —'
    print(f'  {n:<26}{net:>10,}{cost:>9,.0f}{ad:>10,.0f}{pr:>+10,.0f}{m}{be:>6.2f}{y}{pp}')
print(f'  {"カタログ全部（テスト）":<26}{"—":>10}{"—":>9}{CAT(g["D7"]):>10,.0f}{"—":>10}')
