# -*- coding: utf-8 -*-
"""2026-08-28 の実測をCSVへ追記。Shopify=ShopifyQL実測 / Meta=確定値。"""
import csv, os
D = '2026-08-28'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 431890, 8359, 85, 96

SALES = [  # (商品名, gross, discounts)
 ('ナノガラス脱毛パッド', 119400, 4179),
 ('W固定スマホ車載ホルダー', 67660, 1592),
 ('ムダ毛シェーバー', 48860, 0),
 ('姿勢サポートチェア', 41860, 0),
 ('快適マジックインソール', 35820, 796),
 ('バランスケアスリッパ', 24900, 0),
 ('むくみ取りかっさ', 23880, 0),
 ('ビジュアル耳かき', 9960, 996),
 ('4WAY 取り付けOK 小型瞬間冷却ハンディファン', 9960, 0),
 ('2WAYシートボックス', 9960, 0),
 ('完全遮光・接触冷感UVハット', 9960, 0),
 ('偏光・調光サングラス', 7960, 796),
 ('ナノバブルシャワーヘッド', 6980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('ジェットウォッシャー', 4980, 0),
 ('3D足臭リセットブラシ', 3980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [  # ナノガラスはバリアントで原価が違う（白緑757 / 黒桃740）
 ('ナノガラス脱毛パッド', '白緑', 87560 + 19900),    # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 7960 + 3980),      # マットブラック + ベイビーピンク
]
AD = [  # Meta確定値（8/28終日）
 ('ナノガラス脱毛パッド', 76178),
 ('W固定スマホ車載ホルダー', 33892),
 ('快適マジックインソール', 24420),
 ('カタログ全部（テスト）', 18914),
 ('ムダ毛シェーバー', 16582),
 ('2WAYシートボックス', 12602),
 ('姿勢サポートチェア', 12306),
 ('バランスケアスリッパ', 10080),
 ('むくみ取りかっさ', 8089),
 ('完全遮光・接触冷感UVハット', 7808),
 ('3D足臭リセットブラシ', 7742),
 ('ナノバブルシャワーヘッド', 6849),
 ('偏光・調光サングラス', 6498),
 ('ビジュアル耳かき', 3328),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC
assert sum(g for _, _, g in VARIANT) == 119400
AD_TOTAL = sum(c for _, c in AD)
print(f'Σキャンペーン広告費 = {AD_TOTAL:,}円')

def append(path, rows, key=D):
    have = set()
    with open(path, encoding='utf-8') as f:
        for r in csv.reader(f):
            if r and r[0] == key: have.add(tuple(r))
    assert not have, f'{path} に {key} が既にある（{len(have)}行）'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')

append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_ad.csv',      [[D, c, v] for c, v in AD])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n8/28 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 広告 {AD_TOTAL:,} → MER {(STORE_GROSS-STORE_DISC)/AD_TOTAL:.2f}')
