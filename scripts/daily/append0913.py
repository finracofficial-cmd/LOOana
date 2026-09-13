# -*- coding: utf-8 -*-
"""2026-09-13 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0913_ad.py で追記。
   ★セッション **4,246**（直近で最多）・実売658,520円。伸縮ガラスクリーナーは累計128点。
   ★返品なし。"""
import csv
D = '2026-09-13'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 670860, 12340, 140, 157
SALES = [
 ('ナノガラス脱毛パッド', 195020, 1592),
 ('伸縮ガラスクリーナー', 115420, 2388),
 ('W固定スマホ車載ホルダー', 99500, 796),
 ('快適マジックインソール', 91540, 3980),
 ('ムダ毛シェーバー', 48860, 0),
 ('高見えレザーヘッドレストフック', 35820, 2388),
 ('バランスケアスリッパ', 24900, 0),
 ('姿勢サポートチェア', 23920, 1196),
 ('壁掛けディスペンサー', 6980, 0),
 ('4-in-1マルチクリーナー', 6980, 0),
 ('ナノバブルシャワーヘッド', 6980, 0),
 ('癒しの指圧マット', 5980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('3D足臭リセットブラシ', 3980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 119400 + 15920),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 43780 + 15920),    # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 71640),
 ('伸縮ガラスクリーナー', 'グレー', 31840),
 ('伸縮ガラスクリーナー', 'グリーン', 7960),
 ('伸縮ガラスクリーナー', 'レッド', 3980),
 ('高見えレザーヘッドレストフック', 'ブラック', 27860),
 ('高見えレザーヘッドレストフック', 'グレー', 7960),
 ('壁掛けディスペンサー', '3本', 6980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 195020), ('伸縮ガラスクリーナー', 115420),
               ('高見えレザーヘッドレストフック', 35820), ('壁掛けディスペンサー', 6980)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '伸縮ガラスクリーナー': 3980, 'W固定スマホ車載ホルダー': 3980,
     '快適マジックインソール': 3980, 'ムダ毛シェーバー': 6980, '高見えレザーヘッドレストフック': 3980,
     'バランスケアスリッパ': 4980, '姿勢サポートチェア': 5980, '壁掛けディスペンサー': 6980,
     '4-in-1マルチクリーナー': 6980, 'ナノバブルシャワーヘッド': 6980, '癒しの指圧マット': 5980,
     '携帯電動シェーバー': 4980, '3D足臭リセットブラシ': 3980}
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
print(f'\n9/13 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 4,246 / '
      f'カート追加率 {244/4246:.2%} / チェックアウト到達 220 / 返品なし')
