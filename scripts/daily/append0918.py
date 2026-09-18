# -*- coding: utf-8 -*-
"""2026-09-18 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0918_ad.py で追記。

★ムダ毛シェーバーに **返品1件（6,980円）**。A案どおり売上からも利益からも控除しない。
  この日のムダ毛の販売は0点なので gross=0。SALESには入れず、返品額だけ別建てで記録する。
  そのため 販売数116 ＞ 全店 net_items_sold 115（差＝返品数1）。
★UV歯ブラシ除菌器が3点26,940円。広告ゼロのオーガニックで、久々に動いた（売価8,980・原価3,240）。
★携帯電動シェーバーが3点14,940円。これも広告ゼロ。
"""
import csv
D = '2026-09-18'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 489490, 14335, 96, 115, 6980
SALES = [
 ('ナノガラス脱毛パッド', 167160, 2388),
 ('伸縮ガラスクリーナー', 87560, 4179),
 ('W固定スマホ車載ホルダー', 55720, 796),
 ('快適マジックインソール', 43780, 0),
 ('高見えレザーヘッドレストフック', 35820, 3184),
 ('UV歯ブラシ除菌器', 26940, 1796),
 ('バランスケアスリッパ', 24900, 996),
 ('姿勢サポートチェア', 23920, 0),
 ('携帯電動シェーバー', 14940, 996),
 ('もちふわ肉球サンダル', 7960, 0),
 ('優先配送', 790, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 119400 + 15920),  # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 23880 + 7960),    # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 67660),
 ('伸縮ガラスクリーナー', 'グリーン', 15920),
 ('伸縮ガラスクリーナー', 'グレー', 3980),
 ('高見えレザーヘッドレストフック', 'グレー', 23880),
 ('高見えレザーヘッドレストフック', 'ブラック', 7960),
 ('高見えレザーヘッドレストフック', 'ブラウン', 3980),
 ('もちふわ肉球サンダル', '37-38', 7960),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 167160), ('伸縮ガラスクリーナー', 87560),
               ('高見えレザーヘッドレストフック', 35820), ('もちふわ肉球サンダル', 7960)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

# 販売数 = gross ÷ 売価 が全商品で割り切れることを確認（丸め誤差ゼロ）
P = {'ナノガラス脱毛パッド': 3980, '伸縮ガラスクリーナー': 3980, 'W固定スマホ車載ホルダー': 3980,
     '快適マジックインソール': 3980, '高見えレザーヘッドレストフック': 3980, 'UV歯ブラシ除菌器': 8980,
     'バランスケアスリッパ': 4980, '姿勢サポートチェア': 5980, '携帯電動シェーバー': 4980,
     'もちふわ肉球サンダル': 3980, '優先配送': 790}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品数。ムダ毛シェーバーの返品1件ぶん多い
assert tot == STORE_NETITEMS + 1, (tot, STORE_NETITEMS)


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/18 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,583 / '
      f'カート追加率 {191/3583:.2%} / チェックアウト到達 181 / 返品 {RETURNS:,}円(ムダ毛シェーバー 1件)')
