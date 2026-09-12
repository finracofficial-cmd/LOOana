# -*- coding: utf-8 -*-
"""2026-09-12 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0912_ad.py で追記。
   ★伸縮ガラスクリーナーが **32点127,360円** と最高。累計99点。
   ★返品3点14,940円（ムダ毛6,980 + 害虫3,980 + サングラス3,980）。A案どおり売上・利益から控除しない。
     全店の returns は調整行(+10,960)と相殺されて −3,980 と出るが、商品別の実額は 14,940円。"""
import csv
D = '2026-09-12'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 587200, 18310, 117, 137, 14940
SALES = [
 ('ナノガラス脱毛パッド', 191040, 3383),
 ('伸縮ガラスクリーナー', 127360, 5572),
 ('快適マジックインソール', 91540, 4776),
 ('W固定スマホ車載ホルダー', 55720, 796),
 ('姿勢サポートチェア', 35880, 0),
 ('バランスケアスリッパ', 34860, 1992),
 ('高見えレザーヘッドレストフック', 19900, 1791),
 ('ムダ毛シェーバー', 13960, 0),
 ('ナノバブルシャワーヘッド', 6980, 0),
 ('スマートノーズEMS美顔器', 5980, 0),
 ('接触冷感UVパーカー', 3980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 107460 + 27860),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 51740 + 3980),     # マットブラック + ベイビーピンク
 ('伸縮ガラスクリーナー', 'ブルー', 79600),
 ('伸縮ガラスクリーナー', 'グリーン', 19900),
 ('伸縮ガラスクリーナー', 'グレー', 19900),
 ('伸縮ガラスクリーナー', 'レッド', 7960),
 ('高見えレザーヘッドレストフック', 'ブラック', 15920),
 ('高見えレザーヘッドレストフック', 'グレー', 3980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 191040), ('伸縮ガラスクリーナー', 127360),
               ('高見えレザーヘッドレストフック', 19900)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '伸縮ガラスクリーナー': 3980, '快適マジックインソール': 3980,
     'W固定スマホ車載ホルダー': 3980, '姿勢サポートチェア': 5980, 'バランスケアスリッパ': 4980,
     '高見えレザーヘッドレストフック': 3980, 'ムダ毛シェーバー': 6980, 'ナノバブルシャワーヘッド': 6980,
     'スマートノーズEMS美顔器': 5980, '接触冷感UVパーカー': 3980}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品3点（ムダ毛1・害虫1・サングラス1）
assert tot == STORE_NETITEMS + 3, (tot, STORE_NETITEMS)


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/12 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,132 / '
      f'カート追加率 {212/3132:.2%} / チェックアウト到達 195 / 返品 {RETURNS:,}円(3点)')
