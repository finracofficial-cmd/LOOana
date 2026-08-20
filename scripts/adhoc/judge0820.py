# -*- coding: utf-8 -*-
"""2026-08-18 の判定。すべて Shopify実測 × Meta実測（8/17まで）。

・W固定スマホ車載ホルダーの週次ランプ判定（本日が判定日）
・3窓判定（3日/5日/7日・すべて8/14終端）
・8/15の広告費が取れないため、8/15を含む窓は「取得不可」として扱う
"""
import csv, collections

B = '/home/user/LOOana/data/daily/'
COST = {'W固定スマホ車載ホルダー': 1182, 'ナノガラス脱毛パッド': 750, '害虫ブロッカー': 867,
 '形状記憶日傘': 1309, '完全遮光・形状記憶': 1309, 'ヘアドライタオル': 985, '接触冷感UVパーカー': 1434, 'ムダ毛シェーバー': 2798,
 '2WAYシートボックス': 1943, '4WAY': 1730, '偏光・調光サングラス': 893, '5WAY腰掛けファン': 1848,
 '完全遮光・接触冷感UVハット': 1411, '姿勢サポートチェア': 1811, '接触冷感UVアームカバー': 784,
 '快適マジックインソール': 677, '1秒折り畳みチェア': 1584, '卓上冷感クーラー': 1996, 'バランスケアスリッパ': 1304,
 '携帯電動シェーバー': 1743, '瞬間冷感ポンチョ': 987, 'ナノバブルシャワーヘッド': 2255}
PRICE = {'W固定スマホ車載ホルダー': 3980, 'ナノガラス脱毛パッド': 3980, '害虫ブロッカー': 3980,
 '形状記憶日傘': 4980, '完全遮光・形状記憶': 4980, 'ヘアドライタオル': 3980, '接触冷感UVパーカー': 3980, 'ムダ毛シェーバー': 6980,
 '2WAYシートボックス': 4980, '4WAY': 4980, '偏光・調光サングラス': 3980, '5WAY腰掛けファン': 4980,
 '完全遮光・接触冷感UVハット': 4980, '姿勢サポートチェア': 5980, '接触冷感UVアームカバー': 3980,
 '快適マジックインソール': 3980, '1秒折り畳みチェア': 4980, '卓上冷感クーラー': 5980, 'バランスケアスリッパ': 4980,
 '携帯電動シェーバー': 4980, '瞬間冷感ポンチョ': 3980, 'ナノバブルシャワーヘッド': 6980}
MAP = {'4WAY': '4WAY 取り付けOK 小型瞬間冷却ハンディファン',
       '完全遮光・形状記憶': '完全遮光・形状記憶・晴雨兼用・UV日傘',
       'ヘアドライタオル': '高吸水・速乾ヘアドライタオル'}

S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open(B + 'daily_sales.csv', encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B + 'daily_ad.csv', encoding='utf-8')):
    AD[r['campaign']][r['date']] += float(r['cost'])

def rng(a, b): return [f'2026-08-{i:02d}' for i in range(a, b + 1)]
def net(n, days): return sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
def ad(n, days): return sum(AD[MAP.get(n, n)].get(d, 0) for d in days)
def storenet(days): return sum(v[d][0] - v[d][1] for v in S.values() for d in days if d in v)

# ── ① W固定スマホ車載ホルダー 週次ランプ判定（本日が判定日） ───────────────
n = 'W固定スマホ車載ホルダー'
W1, W0 = rng(4, 10), rng(13, 19)
s1, s0 = net(n, W1), net(n, W0)
a1 = ad(n, W1); a0 = ad(n, W0)   # 8/15 も揃った（Supermetrics復旧）
gm = 1 - COST[n] / PRICE[n]; be = 1 / gm
print('■ ① W固定スマホ車載ホルダー ── 週次ランプ判定（宣言済み: 増分MER ≥ 2.88）')
print(f'  粗利率 {gm:.1%} / 分岐MER {be:.2f} / 目標MER 2.83')
print(f'  {"窓":<16}{"実売":>11}{"広告費":>11}{"MER":>7}')
print(f'  {"W-1 8/02-08":<16}{s1:>11,}{a1:>11,.0f}{s1/a1:>7.2f}')
print(f'  {"W0  8/09-15":<16}{s0:>11,}{a0:>11,.0f}{s0/a0:>7.2f}')
da, ds = a0 - a1, s0 - s1
im = ds / da
v = '🚀増額(≥2.88)' if im >= 2.88 else ('⏸据置(1.43-2.88)' if im >= be else '🔻巻き戻し(<1.43)')
print(f'\n  Δ広告費 {da:+,.0f}円 / Δ売上 {ds:+,}円 → 増分MER {im:.2f}   → {v}')
print(f'  ※ 本日が W固定の週次ランプ判定日（8/16に宣言済み）。')

# ── ② 3窓判定（3日/5日/7日・すべて8/14終端） ─────────────────────────────
print('\n■ ② 3窓判定（3日 8/17-19 / 5日 8/15-19 / 7日 8/13-19・すべて前日終端）')
print('   3窓すべてMER<分岐→停止 ／ 3窓すべて余裕<0.30→−25% ／ 3窓すべてMER≥目標→+25% ／ 割れたら据え置き')
WINS = [('3日', rng(17, 19)), ('5日', rng(15, 19)), ('7日', rng(13, 19))]
print(f'  {"商品":<26}{"分岐":>6}{"目標":>6}' + ''.join(f'{w:>16}' for w, _ in WINS) + '   判定')
res = []
for n in sorted(COST, key=lambda x: -net(x, rng(13, 19))):
    if ad(n, rng(13, 19)) < 20000: continue
    r = COST[n] / PRICE[n]; be = 1 / (1 - r); tg = 1 / (1 - r - 0.35)
    ms = []
    for _, days in WINS:
        a = ad(n, days)
        ms.append(net(n, days) / a if a > 0 else None)
    if any(m is None for m in ms): continue
    if all(m < be for m in ms): v = '🚨停止/−50%'
    elif all(m - be < 0.30 for m in ms): v = '🔻−25%'
    elif all(m >= tg for m in ms): v = '🚀+25%'
    else: v = '⏸据え置き'
    cells = ''.join(f'{m:>9.2f}({m-be:>+5.2f})' for m in ms)
    print(f'  {n:<26}{be:>6.2f}{tg:>6.2f}{cells}   {v}')
    res.append((n, v, ms, be))

print('\n■ ③ 頑健性チェック（判定が出た商品のみ・限界MER = 平均×0.6/0.7/0.8）')
print('   削減1円あたり利益 = 1 − 限界MER × 粗利率。3端すべて同符号でなければ動かさない')
for n, v, ms, be in res:
    if v == '⏸据え置き': continue
    gm = 1 - COST[n] / PRICE[n]; m7 = ms[2]
    e = [1 - m7 * k * gm for k in (0.6, 0.7, 0.8)]
    ok = all(x > 0 for x in e) or all(x < 0 for x in e)
    print(f'  {n:<26}{v:<12}' + ''.join(f'{x:>+9.3f}' for x in e)
          + ('   ✅3端一致' if ok else '   ⚠️端で符号が割れる → 動かさない'))
