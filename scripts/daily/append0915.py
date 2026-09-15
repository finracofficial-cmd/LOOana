# -*- coding: utf-8 -*-
"""2026-09-15 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0915_ad.py で追記。

★新商品「電動温熱カッサ」が初売れ（1点・広告なしのオーガニック）。
  売価6,980円 / 原価2,533円（Shopify unitCost 実測 SKU CJYD266410001AZ）→ 原価率36.3%・分岐MER1.57。
  Metaキャンペーン「電動温熱カッサ」(52567391733012) は **9/15新設・日予算10,000円**。
★もちふわ肉球サンダルは2日目。9/14は37-38が3点、9/15は37-38が5点（ライトグリーン）。
★完全遮光・形状記憶（UV日傘）が久々に1点。広告ゼロなのでオーガニック。
"""
import csv
D = '2026-09-15'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 542580, 20897, 103, 133, 0
SALES = [
 ('ナノガラス脱毛パッド', 175120, 5771),
 ('伸縮ガラスクリーナー', 75620, 2388),
 ('快適マジックインソール', 67660, 4975),
 ('W固定スマホ車載ホルダー', 67660, 1592),
 ('高見えレザーヘッドレストフック', 55720, 4179),
 ('姿勢サポートチェア', 29900, 1196),
 ('ムダ毛シェーバー', 20940, 0),
 ('もちふわ肉球サンダル', 19900, 796),
 ('バランスケアスリッパ', 14940, 0),
 ('電動温熱カッサ', 6980, 0),
 ('完全遮光・形状記憶', 4980, 0),
 ('優先配送', 3160, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 115420 + 19900),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 31840 + 7960),     # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 39800),
 ('伸縮ガラスクリーナー', 'グレー', 11940),
 ('伸縮ガラスクリーナー', 'グリーン', 15920),
 ('伸縮ガラスクリーナー', 'レッド', 7960),
 ('高見えレザーヘッドレストフック', 'ブラック', 31840),
 ('高見えレザーヘッドレストフック', 'ブラウン', 7960),
 ('高見えレザーヘッドレストフック', 'グレー', 15920),
 ('もちふわ肉球サンダル', '37-38', 19900),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 175120), ('伸縮ガラスクリーナー', 75620),
               ('高見えレザーヘッドレストフック', 55720), ('もちふわ肉球サンダル', 19900)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

# 販売数 = gross ÷ 売価 が全商品で割り切れることを確認（丸め誤差ゼロ）
P = {'ナノガラス脱毛パッド': 3980, '伸縮ガラスクリーナー': 3980, '快適マジックインソール': 3980,
     'W固定スマホ車載ホルダー': 3980, '高見えレザーヘッドレストフック': 3980, '姿勢サポートチェア': 5980,
     'ムダ毛シェーバー': 6980, 'もちふわ肉球サンダル': 3980, 'バランスケアスリッパ': 4980,
     '電動温熱カッサ': 6980, '完全遮光・形状記憶': 4980, '優先配送': 790}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品数。9/15は返品ゼロ
assert tot == STORE_NETITEMS, (tot, STORE_NETITEMS)


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/15 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,358 / '
      f'カート追加率 {186/3358:.2%} / チェックアウト到達 168 / 返品なし')
