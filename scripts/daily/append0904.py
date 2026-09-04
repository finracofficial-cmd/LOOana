# -*- coding: utf-8 -*-
"""2026-09-04 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0904_ad.py で追記。

★偏光・調光サングラスの販売が0点。広告は出ている（前日4,768円）ので注視。
★優先配送が0件。前日2件・7日6件だったので、アタッチ率の低下が続いている。
★癒しの指圧マットが久々に1点（広告ゼロ＝オーガニック）。
"""
import csv
D = '2026-09-04'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS = 381300, 8560, 74, 85
SALES = [
 ('ナノガラス脱毛パッド', 139300, 3184),
 ('W固定スマホ車載ホルダー', 47760, 1592),
 ('快適マジックインソール', 43780, 1592),
 ('バランスケアスリッパ', 29880, 0),
 ('ムダ毛シェーバー', 27920, 0),
 ('姿勢サポートチェア', 23920, 1196),
 ('2WAYシートボックス', 14940, 996),
 ('ナノバブルシャワーヘッド', 13960, 0),
 ('温感EMSフェイシャルワンド', 11960, 0),
 ('むくみ取りかっさ', 11940, 0),
 ('癒しの指圧マット', 5980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('完全遮光・接触冷感UVハット', 4980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 67660 + 23880),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 35820 + 11940),   # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'シルバー', 5980),
 ('温感EMSフェイシャルワンド', 'ピンク', 5980),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 139300), ('温感EMSフェイシャルワンド', 11960)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

P = {'ナノガラス脱毛パッド': 3980, 'W固定スマホ車載ホルダー': 3980, '快適マジックインソール': 3980,
     'バランスケアスリッパ': 4980, 'ムダ毛シェーバー': 6980, '姿勢サポートチェア': 5980,
     '2WAYシートボックス': 4980, 'ナノバブルシャワーヘッド': 6980, '温感EMSフェイシャルワンド': 5980,
     'むくみ取りかっさ': 3980, '癒しの指圧マット': 5980, '携帯電動シェーバー': 4980,
     '完全遮光・接触冷感UVハット': 4980}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
assert tot == STORE_NETITEMS, (tot, STORE_NETITEMS)   # 返品なしなので 販売数 = net_items_sold


def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')


append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n9/4 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,293 / '
      f'カート追加率 {166/3293:.2%} / チェックアウト到達 149 / 返品なし')
