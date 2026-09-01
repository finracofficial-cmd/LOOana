# -*- coding: utf-8 -*-
"""2026-09-01 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0901_ad.py で追記。"""
import csv
D = '2026-09-01'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 444410, 9008, 88, 101
SALES = [
 ('ナノガラス脱毛パッド', 155220, 2587),
 ('快適マジックインソール', 59700, 2388),
 ('W固定スマホ車載ホルダー', 59700, 796),
 ('ムダ毛シェーバー', 48860, 0),
 ('バランスケアスリッパ', 29880, 996),
 ('ナノバブルシャワーヘッド', 20940, 0),
 ('2WAYシートボックス', 19920, 2241),
 ('完全遮光・接触冷感UVハット', 14940, 0),
 ('むくみ取りかっさ', 11940, 0),
 ('ネックマッサージャー', 9980, 0),
 ('姿勢サポートチェア', 5980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('優先配送', 2370, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 95520 + 19900),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 31840 + 7960),    # マットブラック + ベイビーピンク
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
assert sum(g for n, _, g in VARIANT if n == 'ナノガラス脱毛パッド') == 155220

def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')

append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/1 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 2,936 / カート追加率 5.93%')
