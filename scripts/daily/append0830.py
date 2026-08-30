# -*- coding: utf-8 -*-
"""2026-08-30 の実測をCSVへ追記（Shopifyのみ）。
   ★広告費は本スクリプトでは書かない。health_check の last_30_days が **UTC基準**で、
     JST 09:00 を回るまで 8/30 を含まないため（詳細は下の DISCOVERY）。
     広告費は scripts/daily/append0830_ad.py で別途追記する。"""
import csv
D = '2026-08-30'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 607150, 12743, 114, 133

SALES = [  # (商品名, gross, discounts) — ShopifyQL GROUP BY product_title 実測
 ('ナノガラス脱毛パッド', 167160, 4776),
 ('W固定スマホ車載ホルダー', 95520, 1592),
 ('ムダ毛シェーバー', 69800, 0),
 ('姿勢サポートチェア', 53820, 1196),
 ('むくみ取りかっさ', 47760, 1791),
 ('バランスケアスリッパ', 39840, 0),
 ('2WAYシートボックス', 34860, 996),
 ('快適マジックインソール', 27860, 0),
 ('ナノバブルシャワーヘッド', 20940, 1396),
 ('1秒折り畳みチェア', 9960, 996),
 ('携帯電動シェーバー', 9960, 0),
 ('ビジュアル耳かき', 9960, 0),
 ('完全遮光・接触冷感UVハット', 9960, 0),
 ('完全遮光・形状記憶', 4980, 0),
 ('瞬間冷感ポンチョ', 3980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [  # ナノガラスは原価がバリアントで違う（白緑757 / 黒桃740）
 ('ナノガラス脱毛パッド', '白緑', 111440 + 39800),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 7960 + 7960),      # ベイビーピンク + マットブラック
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
assert sum(g for n, _, g in VARIANT if n == 'ナノガラス脱毛パッド') == 167160

def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')

append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n8/30 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円')
print('  ※広告費は未追記（health_checkの窓がUTC基準でまだ8/30を含まないため）')
