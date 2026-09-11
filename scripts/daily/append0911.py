# -*- coding: utf-8 -*-
"""2026-09-11 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0911_ad.py で追記。
   ★伸縮ガラスクリーナーが21点・**累計67点**で50点を突破（宣言済みの増額判定ライン）。
   ★高見えレザーヘッドレストフックが14点55,720円と急伸（累計23点）。
   ★返品なし。"""
import csv
D = '2026-09-11'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 530250, 25076, 96, 128
SALES = [
 ('ナノガラス脱毛パッド', 131340, 3184),
 ('W固定スマホ車載ホルダー', 103480, 4179),
 ('伸縮ガラスクリーナー', 83580, 5970),
 ('快適マジックインソール', 71640, 3980),
 ('高見えレザーヘッドレストフック', 55720, 5771),
 ('姿勢サポートチェア', 17940, 1196),
 ('4-in-1マルチクリーナー', 13960, 0),
 ('ムダ毛シェーバー', 13960, 0),
 ('バランスケアスリッパ', 9960, 0),
 ('偏光・調光サングラス', 7960, 796),
 ('ナノバブルシャワーヘッド', 6980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('リカバリーサンダル', 3980, 0),
 ('むくみ取りかっさ', 3980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 75620 + 3980),     # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 39800 + 11940),    # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 39800),
 ('伸縮ガラスクリーナー', 'グリーン', 19900),
 ('伸縮ガラスクリーナー', 'グレー', 15920),
 ('伸縮ガラスクリーナー', 'レッド', 7960),
 ('高見えレザーヘッドレストフック', 'グレー', 27860),
 ('高見えレザーヘッドレストフック', 'ブラック', 23880),
 ('高見えレザーヘッドレストフック', 'ブラウン', 3980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 131340), ('伸縮ガラスクリーナー', 83580),
               ('高見えレザーヘッドレストフック', 55720)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, 'W固定スマホ車載ホルダー': 3980, '伸縮ガラスクリーナー': 3980,
     '快適マジックインソール': 3980, '高見えレザーヘッドレストフック': 3980, '姿勢サポートチェア': 5980,
     '4-in-1マルチクリーナー': 6980, 'ムダ毛シェーバー': 6980, 'バランスケアスリッパ': 4980,
     '偏光・調光サングラス': 3980, 'ナノバブルシャワーヘッド': 6980, '携帯電動シェーバー': 4980,
     'リカバリーサンダル': 3980, 'むくみ取りかっさ': 3980, '優先配送': 790}
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
print(f'\n9/11 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,014 / '
      f'カート追加率 {168/3014:.2%} / チェックアウト到達 165 / 返品なし')
