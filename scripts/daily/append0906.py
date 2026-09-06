# -*- coding: utf-8 -*-
"""2026-09-06 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0906_ad.py で追記。
   ★W固定スマホ車載ホルダーに返品1件(3,980円)。A案どおり売上・利益から控除しない。
   ★スマートノーズEMS美顔器・ジェットウォッシャーが久々に各1点（広告ゼロ＝オーガニック）。"""
import csv
D = '2026-09-06'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 614260, 12537, 122, 136, 3980
SALES = [
 ('ナノガラス脱毛パッド', 218900, 1592),
 ('W固定スマホ車載ホルダー', 107460, 3980),
 ('快適マジックインソール', 75620, 6965),
 ('ムダ毛シェーバー', 69800, 0),
 ('バランスケアスリッパ', 29880, 0),
 ('温感EMSフェイシャルワンド', 23920, 0),
 ('4-in-1マルチクリーナー', 20940, 0),
 ('むくみ取りかっさ', 15920, 0),
 ('ナノバブルシャワーヘッド', 13960, 0),
 ('姿勢サポートチェア', 11960, 0),
 ('携帯電動シェーバー', 9960, 0),
 ('スマートノーズEMS美顔器', 5980, 0),
 ('ジェットウォッシャー', 4980, 0),
 ('2WAYシートボックス', 4980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 155220 + 19900),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 39800 + 3980),     # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'ピンク', 23920),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 218900), ('温感EMSフェイシャルワンド', 23920)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, 'W固定スマホ車載ホルダー': 3980, '快適マジックインソール': 3980,
     'ムダ毛シェーバー': 6980, 'バランスケアスリッパ': 4980, '温感EMSフェイシャルワンド': 5980,
     '4-in-1マルチクリーナー': 6980, 'むくみ取りかっさ': 3980, 'ナノバブルシャワーヘッド': 6980,
     '姿勢サポートチェア': 5980, '携帯電動シェーバー': 4980, 'スマートノーズEMS美顔器': 5980,
     'ジェットウォッシャー': 4980, '2WAYシートボックス': 4980}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
assert tot == STORE_NETITEMS + 1, (tot, STORE_NETITEMS)   # W固定の返品1件ぶん多い


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/6 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,752 / '
      f'カート追加率 {219/3752:.2%} / チェックアウト到達 198 / 返品 {RETURNS:,}円(W固定1件)')
