# -*- coding: utf-8 -*-
"""2026-09-10 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0910_ad.py で追記。
   ★4-in-1マルチクリーナーが **累計20点** に到達（宣言済みの中間判定ライン）。
   ★伸縮ガラスクリーナーが17点・累計46点。50点まであと4点。
   ★返品なし。"""
import csv
D = '2026-09-10'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 598990, 20854, 116, 141
SALES = [
 ('ナノガラス脱毛パッド', 210940, 3184),
 ('快適マジックインソール', 103480, 7761),
 ('W固定スマホ車載ホルダー', 75620, 1592),
 ('伸縮ガラスクリーナー', 67660, 2388),
 ('4-in-1マルチクリーナー', 41880, 3141),
 ('姿勢サポートチェア', 35880, 1196),
 ('高見えレザーヘッドレストフック', 23880, 1592),
 ('バランスケアスリッパ', 19920, 0),
 ('ナノバブルシャワーヘッド', 6980, 0),
 ('ムダ毛シェーバー', 6980, 0),
 ('2WAYシートボックス', 4980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 123380 + 3980),    # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 67660 + 15920),    # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 27860),
 ('伸縮ガラスクリーナー', 'グリーン', 19900),
 ('伸縮ガラスクリーナー', 'レッド', 11940),
 ('伸縮ガラスクリーナー', 'グレー', 7960),
 ('高見えレザーヘッドレストフック', 'ブラック', 11940),
 ('高見えレザーヘッドレストフック', 'グレー', 7960),
 ('高見えレザーヘッドレストフック', 'ブラウン', 3980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 210940), ('伸縮ガラスクリーナー', 67660),
               ('高見えレザーヘッドレストフック', 23880)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '快適マジックインソール': 3980, 'W固定スマホ車載ホルダー': 3980,
     '伸縮ガラスクリーナー': 3980, '4-in-1マルチクリーナー': 6980, '姿勢サポートチェア': 5980,
     '高見えレザーヘッドレストフック': 3980, 'バランスケアスリッパ': 4980,
     'ナノバブルシャワーヘッド': 6980, 'ムダ毛シェーバー': 6980, '2WAYシートボックス': 4980, '優先配送': 790}
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
print(f'\n9/10 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,514 / '
      f'カート追加率 {195/3514:.2%} / チェックアウト到達 189 / 返品なし')
