# -*- coding: utf-8 -*-
"""2026-09-14 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0914_ad.py で追記。
   ★新商品「もちふわ肉球サンダル」が初売れ（3点）。キャンペーンも9/14に新設。
     売価3,980円 / 原価はサイズで違う（37-38:1,117 / 39-40:1,134 / 41-42:1,148 / 43-44:1,165）→ VARC 扱い。
   ★返品なし。"""
import csv
D = '2026-09-14'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 503580, 16321, 102, 121
SALES = [
 ('ナノガラス脱毛パッド', 179100, 5771),
 ('伸縮ガラスクリーナー', 83580, 1592),
 ('快適マジックインソール', 63680, 3383),
 ('W固定スマホ車載ホルダー', 59700, 796),
 ('高見えレザーヘッドレストフック', 31840, 1791),
 ('姿勢サポートチェア', 29900, 1196),
 ('バランスケアスリッパ', 29880, 996),
 ('ムダ毛シェーバー', 13960, 0),
 ('もちふわ肉球サンダル', 11940, 796),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 115420 + 27860),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 23880 + 11940),    # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 51740),
 ('伸縮ガラスクリーナー', 'グレー', 23880),
 ('伸縮ガラスクリーナー', 'レッド', 7960),
 ('高見えレザーヘッドレストフック', 'ブラック', 23880),
 ('高見えレザーヘッドレストフック', 'グレー', 7960),
 ('もちふわ肉球サンダル', '37-38', 11940),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 179100), ('伸縮ガラスクリーナー', 83580),
               ('高見えレザーヘッドレストフック', 31840), ('もちふわ肉球サンダル', 11940)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '伸縮ガラスクリーナー': 3980, '快適マジックインソール': 3980,
     'W固定スマホ車載ホルダー': 3980, '高見えレザーヘッドレストフック': 3980, '姿勢サポートチェア': 5980,
     'バランスケアスリッパ': 4980, 'ムダ毛シェーバー': 6980, 'もちふわ肉球サンダル': 3980}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
assert tot == STORE_NETITEMS, (tot, STORE_NETITEMS)   # 返品なし


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/14 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,592 / '
      f'カート追加率 {176/3592:.2%} / チェックアウト到達 168 / 返品なし')
