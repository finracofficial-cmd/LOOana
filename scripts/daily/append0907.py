# -*- coding: utf-8 -*-
"""2026-09-07 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0907_ad.py で追記。
   ★新商品「伸縮ガラスクリーナー」が初売れ（3点）。キャンペーンも9/07に新設された。
     売価3,980円 / 原価 ブルー1,120・グレー1,143・グリーン1,123・レッド1,120 とバリアントで違うので VARC 扱い。
   ★返品なし。"""
import csv
D = '2026-09-07'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 487840, 9405, 96, 108
SALES = [
 ('ナノガラス脱毛パッド', 187060, 3184),
 ('快適マジックインソール', 55720, 3184),
 ('W固定スマホ車載ホルダー', 47760, 796),
 ('バランスケアスリッパ', 44820, 2241),
 ('ムダ毛シェーバー', 34900, 0),
 ('4-in-1マルチクリーナー', 27920, 0),
 ('温感EMSフェイシャルワンド', 17940, 0),
 ('2WAYシートボックス', 14940, 0),
 ('壁掛けディスペンサー', 13960, 0),
 ('姿勢サポートチェア', 11960, 0),
 ('伸縮ガラスクリーナー', 11940, 0),
 ('むくみ取りかっさ', 11940, 0),
 ('ナノバブルシャワーヘッド', 6980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 115420 + 23880),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 35820 + 11940),    # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'ピンク', 17940),
 ('壁掛けディスペンサー', '3本', 13960),
 ('伸縮ガラスクリーナー', 'ブルー', 7960),
 ('伸縮ガラスクリーナー', 'グレー', 3980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 187060), ('温感EMSフェイシャルワンド', 17940),
               ('壁掛けディスペンサー', 13960), ('伸縮ガラスクリーナー', 11940)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '快適マジックインソール': 3980, 'W固定スマホ車載ホルダー': 3980,
     'バランスケアスリッパ': 4980, 'ムダ毛シェーバー': 6980, '4-in-1マルチクリーナー': 6980,
     '温感EMSフェイシャルワンド': 5980, '2WAYシートボックス': 4980, '壁掛けディスペンサー': 6980,
     '姿勢サポートチェア': 5980, '伸縮ガラスクリーナー': 3980, 'むくみ取りかっさ': 3980,
     'ナノバブルシャワーヘッド': 6980}
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
print(f'\n9/7 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 2,787 / '
      f'カート追加率 {156/2787:.2%} / チェックアウト到達 140 / 返品なし')
