# -*- coding: utf-8 -*-
"""2026-09-16 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0916_ad.py で追記。

★もちふわ肉球サンダルが7点27,860円で初めて2桁近くまで伸びた（累計15点）。
  41-42サイズが3点入ったのでバリアント原価の加重が効いてくる。
★電動温熱カッサは2日連続で1点（広告は9/15に3,586円から開始）。
★接触冷感UVアームカバーが1点。夏物の残りで広告ゼロのオーガニック。
"""
import csv
D = '2026-09-16'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 465530, 10547, 99, 114, 0
SALES = [
 ('ナノガラス脱毛パッド', 139300, 2388),
 ('快適マジックインソール', 95520, 3184),
 ('伸縮ガラスクリーナー', 79600, 1791),
 ('W固定スマホ車載ホルダー', 43780, 796),
 ('高見えレザーヘッドレストフック', 35820, 796),
 ('もちふわ肉球サンダル', 27860, 1592),
 ('ムダ毛シェーバー', 20940, 0),
 ('電動温熱カッサ', 6980, 0),
 ('姿勢サポートチェア', 5980, 0),
 ('バランスケアスリッパ', 4980, 0),
 ('接触冷感UVアームカバー', 3980, 0),
 ('優先配送', 790, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 91540 + 15920),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 19900 + 11940),   # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 55720),
 ('伸縮ガラスクリーナー', 'グレー', 15920),
 ('伸縮ガラスクリーナー', 'グリーン', 7960),
 ('高見えレザーヘッドレストフック', 'ブラック', 27860),
 ('高見えレザーヘッドレストフック', 'グレー', 3980),
 ('高見えレザーヘッドレストフック', 'ブラウン', 3980),
 ('もちふわ肉球サンダル', '37-38', 11940 + 3980),   # ライトグリーン + レッド
 ('もちふわ肉球サンダル', '41-42', 7960 + 3980),    # ブラウン + ブラック
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 139300), ('伸縮ガラスクリーナー', 79600),
               ('高見えレザーヘッドレストフック', 35820), ('もちふわ肉球サンダル', 27860)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

# 販売数 = gross ÷ 売価 が全商品で割り切れることを確認（丸め誤差ゼロ）
P = {'ナノガラス脱毛パッド': 3980, '快適マジックインソール': 3980, '伸縮ガラスクリーナー': 3980,
     'W固定スマホ車載ホルダー': 3980, '高見えレザーヘッドレストフック': 3980, 'もちふわ肉球サンダル': 3980,
     'ムダ毛シェーバー': 6980, '電動温熱カッサ': 6980, '姿勢サポートチェア': 5980,
     'バランスケアスリッパ': 4980, '接触冷感UVアームカバー': 3980, '優先配送': 790}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品数。9/16は返品ゼロ
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
print(f'\n9/16 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,348 / '
      f'カート追加率 {187/3348:.2%} / チェックアウト到達 173 / 返品なし')
