# -*- coding: utf-8 -*-
"""2026-09-05 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0905_ad.py で追記。

★新商品「4-in-1マルチクリーナー」が初売れ（2点）。キャンペーンも9/05に新設された。
  売価6,980円 / 原価2,961円（マッドブラック・シルバーパープルとも同額）→ 原価率42.4%・分岐MER1.74。
  バリアント間で原価が同じなので VARC 扱いは不要。
★返品2件（ナノガラス3,980 + インソール3,980 = 7,960円）。A案どおり売上・利益から控除しない。
★停止済みキャンペーンの商品（形状記憶日傘・卓上冷感クーラー・5WAY・ビジュアル耳かき）が
  オーガニックで売れている。
"""
import csv
D = '2026-09-05'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 543620, 9155, 106, 117, 7960
SALES = [
 ('ナノガラス脱毛パッド', 187060, 2388),
 ('快適マジックインソール', 83580, 4975),
 ('ムダ毛シェーバー', 48860, 0),
 ('バランスケアスリッパ', 44820, 996),
 ('ナノバブルシャワーヘッド', 27920, 0),
 ('W固定スマホ車載ホルダー', 27860, 0),
 ('姿勢サポートチェア', 23920, 0),
 ('むくみ取りかっさ', 23880, 796),
 ('2WAYシートボックス', 14940, 0),
 ('4-in-1マルチクリーナー', 13960, 0),
 ('温感EMSフェイシャルワンド', 11960, 0),
 ('形状記憶日傘', 9960, 0),
 ('卓上冷感クーラー', 5980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('ビジュアル耳かき', 4980, 0),
 ('5WAY腰掛けファン', 4980, 0),
 ('偏光・調光サングラス', 3980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 107460 + 23880),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 39800 + 15920),    # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'シルバー', 11960),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 187060), ('温感EMSフェイシャルワンド', 11960)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, '快適マジックインソール': 3980, 'ムダ毛シェーバー': 6980,
     'バランスケアスリッパ': 4980, 'ナノバブルシャワーヘッド': 6980, 'W固定スマホ車載ホルダー': 3980,
     '姿勢サポートチェア': 5980, 'むくみ取りかっさ': 3980, '2WAYシートボックス': 4980,
     '4-in-1マルチクリーナー': 6980, '温感EMSフェイシャルワンド': 5980, '形状記憶日傘': 4980,
     '卓上冷感クーラー': 5980, '携帯電動シェーバー': 4980, 'ビジュアル耳かき': 4980,
     '5WAY腰掛けファン': 4980, '偏光・調光サングラス': 3980}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品数（ナノガラス1 + インソール1）
assert tot == STORE_NETITEMS + 2, (tot, STORE_NETITEMS)


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/5 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,217 / '
      f'カート追加率 {198/3217:.2%} / チェックアウト到達 172 / 返品 {RETURNS:,}円(2件)')
