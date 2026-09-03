# -*- coding: utf-8 -*-
"""2026-09-03 の実測をCSVへ追記（Shopifyのみ）。広告費は09:00 JST以降に append0903_ad.py で追記。

★4WAY に返品1件（4,233円）が発生。A案どおり売上からも利益からも控除しない（月次の返品累計で管理）。
  そのため 販売数118 ＞ 全店 net_items_sold 117 となる（差＝返品数1）。
★温感EMSフェイシャルワンドが2日目。9/02はシルバー1点だけだったが、9/03はピンク3点＋シルバー1点。
★壁掛けディスペンサーが久々に3点（すべてブラック3本セット）。広告はゼロなのでオーガニック。
"""
import csv
D = '2026-09-03'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_NETITEMS, RETURNS = 530260, 11304, 103, 117, 4233
SALES = [
 ('ナノガラス脱毛パッド', 175120, 1592),
 ('W固定スマホ車載ホルダー', 71640, 2587),
 ('快適マジックインソール', 67660, 796),
 ('ムダ毛シェーバー', 48860, 0),
 ('ナノバブルシャワーヘッド', 34900, 0),
 ('2WAYシートボックス', 29880, 1992),
 ('バランスケアスリッパ', 24900, 0),
 ('温感EMSフェイシャルワンド', 23920, 1196),
 ('壁掛けディスペンサー', 20940, 3141),
 ('むくみ取りかっさ', 7960, 0),
 ('偏光・調光サングラス', 7960, 0),
 ('姿勢サポートチェア', 5980, 0),
 ('携帯電動シェーバー', 4980, 0),
 ('ヘアドライタオル', 3980, 0),
 ('優先配送', 1580, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 127360 + 7960),    # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 31840 + 7960),     # マットブラック + ベイビーピンク
 ('温感EMSフェイシャルワンド', 'シルバー', 5980),
 ('温感EMSフェイシャルワンド', 'ピンク', 17940),
 ('壁掛けディスペンサー', '3本', 20940),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC, sum(d for _, _, d in SALES)
for n, tgt in [('ナノガラス脱毛パッド', 175120), ('温感EMSフェイシャルワンド', 23920), ('壁掛けディスペンサー', 20940)]:
    assert sum(g for m, _, g in VARIANT if m == n) == tgt, n

# 販売数 = gross ÷ 売価 が全商品で割り切れることを確認（丸め誤差ゼロ）
P = {'ナノガラス脱毛パッド': 3980, 'W固定スマホ車載ホルダー': 3980, '快適マジックインソール': 3980,
     'ムダ毛シェーバー': 6980, 'ナノバブルシャワーヘッド': 6980, '2WAYシートボックス': 4980,
     'バランスケアスリッパ': 4980, '温感EMSフェイシャルワンド': 5980, '壁掛けディスペンサー': 6980,
     'むくみ取りかっさ': 3980, '偏光・調光サングラス': 3980, '姿勢サポートチェア': 5980,
     '携帯電動シェーバー': 4980, 'ヘアドライタオル': 3980, '優先配送': 790}
tot = 0
for n, g, _ in SALES:
    x = g / P[n]; assert abs(x - round(x)) < 1e-6, (n, g, P[n]); tot += round(x)
# 販売数(gross基準) = net_items_sold + 返品数。4WAYの返品1件ぶん多い
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
print(f'\n9/3 全店(Shopify実測): 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 販売数 {tot} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / セッション 3,340 / '
      f'カート追加率 {197/3340:.2%} / チェックアウト到達 179 / 返品 {RETURNS:,}円(4WAY 1件)')
