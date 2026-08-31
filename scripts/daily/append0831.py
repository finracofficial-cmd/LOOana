# -*- coding: utf-8 -*-
"""2026-08-31 の実測をCSVへ追記（Shopifyのみ）。
   広告費は health_check の窓（UTC基準）が JST 09:00 を回ってから append0831_ad.py で追記する。"""
import csv
D = '2026-08-31'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 400180, 5971, 84, 91

SALES = [
 ('ナノガラス脱毛パッド', 175120, 2587),
 ('W固定スマホ車載ホルダー', 51740, 1592),
 ('快適マジックインソール', 43780, 796),
 ('ムダ毛シェーバー', 34900, 0),
 ('ナノバブルシャワーヘッド', 27920, 0),
 ('バランスケアスリッパ', 19920, 0),
 ('むくみ取りかっさ', 15920, 0),
 ('姿勢サポートチェア', 11960, 0),
 ('完全遮光・接触冷感UVハット', 9960, 996),
 ('2WAYシートボックス', 4980, 0),
 ('偏光・調光サングラス', 3980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 119400 + 27860),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 19900 + 7960),     # マットブラック + ベイビーピンク
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
assert sum(g for n, _, g in VARIANT if n == 'ナノガラス脱毛パッド') == 175120

def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')

append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n8/31 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 2,761')
print('  ※広告費は未追記（health_checkの窓がUTC基準でまだ8/31を含まないため・09:00 JST以降に追記）')
