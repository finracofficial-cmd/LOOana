# -*- coding: utf-8 -*-
"""2026-08-17（月）16:17 JST 時点の日中実測。

SKILL 7h に従い**着地予測は出さない**。同時点どうしの実測比較のみ。
売上・注文数 = Shopify実測（ShopifyQL・GROUP BY hour / product_title）
広告費・クリック = Meta実測（Supermetrics・当日分）
"""
import csv, collections, runpy

g = runpy.run_path('/home/user/LOOana/scripts/daily/w0816.py')
AD, COST, PRICE, MAP = dict(g['AD']), dict(g['COST']), dict(g['PRICE']), g['MAP']
# ナノガラスはバリアントで原価が違う。当日のバリアント構成は未取得なので
# 直近7日実測の加重平均 242,981円 ÷ 323個 = 752.3円 を使う（当日限りの近似・その旨を明記）
COST['ナノガラス脱毛パッド'] = 242981/323

# ── 同時点比較（JST 00:00–15:59。ShopifyQL GROUP BY hour をUTC→JSTで畳んだ実測）──
CMP = {  # 日: (gross, disc, orders)
 '2026-08-17(月)': (334480, 12046, 62),
 '2026-08-16(日)': (407140,  8809, 83),
 '2026-08-10(月)': (453012, 10201, 91),
}
print('■ ① 同時点比較（JST 00:00–15:59・Shopify実測）')
print(f'  {"日":<16}{"実売":>11}{"注文":>6}{"客単価":>9}')
for k, (gr, dc, o) in CMP.items():
    print(f'  {k:<16}{gr-dc:>11,}{o:>6}{(gr-dc)/o:>9,.0f}')
b = CMP['2026-08-17(月)']; y = CMP['2026-08-16(日)']; m = CMP['2026-08-10(月)']
bn, yn, mn = b[0]-b[1], y[0]-y[1], m[0]-m[1]
print(f'\n  vs 昨日8/16(日): 実売 {bn/yn-1:+.1%} / 注文 {b[2]/y[2]-1:+.1%}')
print(f'    ※ 曜日指数は 日110.5 → 月88.1 なので、同じ実力でも {88.1/110.5-1:+.1%} は落ちる。'
      f'実績はそれより{"良い" if bn/yn > 88.1/110.5 else "悪い"}')
print(f'  vs 先週の月曜8/10: 実売 {bn/mn-1:+.1%} / 注文 {b[2]/m[2]-1:+.1%}  ← 曜日をそろえた比較')

# ── 全店の当日実測 ──
SPEND_NOW = 168601      # Meta実測・16:17時点
BUDGET = 332200         # 8/17の日予算（Meta直読の合計）
GROSS_NOW, DISC_NOW, ORD_NOW = 342440, 12046, 64   # 16:17時点（16時台の途中を含む）
net = GROSS_NOW - DISC_NOW
print(f'\n■ ② 全店の当日実測（16:17時点）')
print(f'  実売 {net:,}円 / 注文 {ORD_NOW}件 / 広告消化 {SPEND_NOW:,}円（日予算 {BUDGET:,}円の {SPEND_NOW/BUDGET:.1%}）')
print(f'  MER(同時点) {net/SPEND_NOW:.2f}  ※ クリック→購入のラグを無視した近似。順位の目安としてのみ読む')
prev = [('8/16(日)', 714403, 382657), ('8/15(土)', 769897, 364579), ('8/10(月)', None, None)]
d10 = [d for d in ['2026-08-10']]
ad10 = sum(sum(AD[c].get(d, 0) for c in AD) for d in d10)
import csv as _c
S10 = 0
for r in _c.DictReader(open('/home/user/LOOana/data/daily/daily_sales.csv', encoding='utf-8')):
    if r['date'] == '2026-08-10': S10 += int(r['gross']) - int(r['disc'])
print(f'  参考（終日確定値）: 8/16 MER {714403/382657:.2f} ／ 8/15 {769897/364579:.2f} ／ 8/10(月) {S10/ad10:.2f}')

# ── 商品別の当日実測 ──
SH = {  # Shopify実測 16:17時点: (gross, disc, orders)
 'ナノガラス脱毛パッド': (71640, 796, 17), 'W固定スマホ車載ホルダー': (63680, 1592, 14),
 '形状記憶日傘': (49800, 4233, 6), '2WAYシートボックス': (39840, 2241, 6),
 '快適マジックインソール': (31840, 2388, 5), 'ムダ毛シェーバー': (20940, 0, 3),
 '接触冷感UVパーカー': (15920, 0, 4), '偏光・調光サングラス': (15920, 796, 3),
 '4WAY': (9960, 0, 2), 'バランスケアスリッパ': (9960, 0, 2),
 '接触冷感UVアームカバー': (7960, 0, 2), '完全遮光・接触冷感UVハット': (4980, 0, 1),
 '完全遮光・形状記憶': (0, 0, 0), '姿勢サポートチェア': (0, 0, 0),
 'ヘアドライタオル': (0, 0, 0), '5WAY腰掛けファン': (0, 0, 0),
}
MC = {  # Meta実測 16:17時点: (cost, clicks)
 'ナノガラス脱毛パッド': (40995, 627), 'W固定スマホ車載ホルダー': (19325, 302),
 '形状記憶日傘': (17365, 143), '2WAYシートボックス': (8186, 105),
 '快適マジックインソール': (6103, 93), 'ムダ毛シェーバー': (8929, 75),
 '接触冷感UVパーカー': (11555, 96), '偏光・調光サングラス': (6463, 74),
 '4WAY': (5152, 29), 'バランスケアスリッパ': (2765, 32),
 '接触冷感UVアームカバー': (4484, 38), '完全遮光・接触冷感UVハット': (6015, 89),
 '完全遮光・形状記憶': (6912, 58), '姿勢サポートチェア': (4883, 73),
 'ヘアドライタオル': (4935, 28), '5WAY腰掛けファン': (3289, 47),
}
assert sum(c for c, _ in MC.values()) + 11245 == SPEND_NOW, sum(c for c, _ in MC.values()) + 11245
print(f'\n■ ③ 商品別の当日実測（16:17時点・カタログ11,245円は商品に配賦しない）')
print(f'  {"商品":<24}{"実売":>9}{"注文":>5}{"広告費":>9}{"MER":>7}{"分岐":>6}{"余裕":>7}{"CVR":>7}{"CPA":>8}')
rows = []
for n in sorted(SH, key=lambda x: -MC[x][0]):
    gr, dc, o = SH[n]; c, ck = MC[n]
    ns = gr - dc; be = 1 / (1 - COST[n] / PRICE[n])
    mer = ns / c if c else 0
    rows.append((n, ns, o, c, mer, be))
    print(f'  {n:<24}{ns:>9,}{o:>5}{c:>9,}{mer:>7.2f}{be:>6.2f}{mer-be:>+7.2f}'
          f'{o/ck if ck else 0:>7.2%}{c/o if o else 0:>8,.0f}')
bad = [r for r in rows if r[4] < r[5]]
print(f'\n  分岐割れ {len(bad)}件')
loss = sum(r[1] - r[1] * COST[r[0]] / PRICE[r[0]] - r[3] for r in bad)
print(f'  分岐割れ商品の当日利益合計: {loss:+,.0f}円（実売−原価−広告費）')
for r in bad:
    n = r[0]; pr = r[1] - r[1] * COST[n] / PRICE[n] - r[3]
    print(f'    {n:<24}{pr:>+10,.0f}円')
