# -*- coding: utf-8 -*-
"""2026-09-02 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0902_ad.py で追記。

★新商品「温感EMSフェイシャルワンド」が初売れ（1点・広告なし）。
  売価5,980円 / 原価は シルバー1,866・ピンク2,079 とバリアントで違うため VARC 扱いにする。
"""
import csv
D = '2026-09-02'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 448710, 9951, 92, 105
SALES = [
 ('ナノガラス脱毛パッド', 155220, 1592),
 ('快適マジックインソール', 75620, 4975),
 ('W固定スマホ車載ホルダー', 67660, 2388),
 ('バランスケアスリッパ', 34860, 0),
 ('ムダ毛シェーバー', 27920, 0),
 ('むくみ取りかっさ', 23880, 0),
 ('2WAYシートボックス', 19920, 0),
 ('完全遮光・接触冷感UVハット', 14940, 996),
 ('ナノバブルシャワーヘッド', 13960, 0),
 ('偏光・調光サングラス', 7960, 0),
 ('温感EMSフェイシャルワンド', 5980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 103480 + 15920),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 31840 + 3980),     # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'シルバー', 5980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
assert sum(g for n, _, g in VARIANT if n == 'ナノガラス脱毛パッド') == 155220
assert sum(g for n, _, g in VARIANT if n == '温感EMSフェイシャルワンド') == 5980

# 販売数 = gross ÷ 売価 が全商品で割り切れることを確認（丸め誤差ゼロ）
P = {'ナノガラス脱毛パッド': 3980, '快適マジックインソール': 3980, 'W固定スマホ車載ホルダー': 3980,
     'バランスケアスリッパ': 4980, 'ムダ毛シェーバー': 6980, 'むくみ取りかっさ': 3980,
     '2WAYシートボックス': 4980, '完全遮光・接触冷感UVハット': 4980, 'ナノバブルシャワーヘッド': 6980,
     '偏光・調光サングラス': 3980, '温感EMSフェイシャルワンド': 5980, '優先配送': 790}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
assert tot == STORE_ITEMS, (tot, STORE_ITEMS)


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/2 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,142 / '
      f'カート追加率 {176/3142:.2%} / チェックアウト到達 156')
