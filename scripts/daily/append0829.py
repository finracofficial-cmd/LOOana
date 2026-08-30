# -*- coding: utf-8 -*-
"""2026-08-29 の実測をCSVへ追記。
   Shopify = ShopifyQL実測。
   Meta = data_query がハーネス側でブロックされたため、通る方の campaign_and_resource_get
          （health_check / last_30_days = 7/31-8/29 の実測）から
          CSV確定済み 7/31-8/28（29日）を引いて 8/29 を導出した。
          ★推計ではなく「2つの実測の差」。14キャンペーン全てで
            「8/29 19:06時点の実測 ≤ 導出値」を満たすことを検証済み（scripts/daily/derive0829.py）。"""
import csv
D = '2026-08-29'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 599260, 16121, 115, 137

SALES = [
 ('ナノガラス脱毛パッド', 210940, 3980),
 ('W固定スマホ車載ホルダー', 91540, 4179),
 ('快適マジックインソール', 87560, 4975),
 ('姿勢サポートチェア', 53820, 1196),
 ('ムダ毛シェーバー', 41880, 0),
 ('むくみ取りかっさ', 31840, 1791),
 ('バランスケアスリッパ', 19920, 0),
 ('ナノバブルシャワーヘッド', 13960, 0),
 ('ビジュアル耳かき', 9960, 0),
 ('完全遮光・接触冷感UVハット', 9960, 0),
 ('偏光・調光サングラス', 7960, 0),
 ('壁掛けディスペンサー', 6980, 0),
 ('2WAYシートボックス', 4980, 0),
 ('3D足臭リセットブラシ', 3980, 0),
 ('接触冷感UVパーカー', 3980, 0),
]
VARIANT = [
 ('ナノガラス脱毛パッド', '白緑', 131340 + 23880),   # ピュアホワイト + セージグリーン
 ('ナノガラス脱毛パッド', '黒桃', 31840 + 23880),    # マットブラック + ベイビーピンク
 ('壁掛けディスペンサー', '3本', 6980),
]
AD = [  # health_check30日実測 − CSV29日実測 で導出（上のdocstring参照）
 ('ナノガラス脱毛パッド', 77616),
 ('W固定スマホ車載ホルダー', 34988),
 ('快適マジックインソール', 25642),
 ('ムダ毛シェーバー', 15530),
 ('カタログ全部（テスト）', 15157),
 ('2WAYシートボックス', 12577),
 ('姿勢サポートチェア', 10897),
 ('むくみ取りかっさ', 8224),
 ('バランスケアスリッパ', 8121),
 ('ビジュアル耳かき', 7347),
 ('完全遮光・接触冷感UVハット', 7109),
 ('ナノバブルシャワーヘッド', 6948),
 ('偏光・調光サングラス', 6164),
 ('3D足臭リセットブラシ', 5126),
]
assert sum(g for _, g, _ in SALES) == STORE_GROSS, sum(g for _, g, _ in SALES)
assert sum(d for _, _, d in SALES) == STORE_DISC
assert sum(g for n, _, g in VARIANT if n == 'ナノガラス脱毛パッド') == 210940
AD_TOTAL = sum(c for _, c in AD)
print(f'Σキャンペーン広告費 = {AD_TOTAL:,}円（8/29 19:06実測の合計190,813円 → 夜間+{AD_TOTAL-190813:,}円）')

def append(path, rows, key=D):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == key for r in csv.reader(f)), f'{path} に {key} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} に {len(rows)}行 追記')

append('data/daily/daily_sales.csv',   [[D, n, g, d] for n, g, d in SALES])
append('data/daily/daily_ad.csv',      [[D, c, v] for c, v in AD])
append('data/daily/daily_variant.csv', [[D, n, g, v] for n, g, v in VARIANT])
print(f'\n8/29 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 広告 {AD_TOTAL:,} → MER {(STORE_GROSS-STORE_DISC)/AD_TOTAL:.2f}')
