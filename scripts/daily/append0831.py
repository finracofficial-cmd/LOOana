# -*- coding: utf-8 -*-
"""2026-08-31 の実測をCSVへ追記（Shopify・Meta とも当日終了直後に取得）。
   ⚠️ Meta は JST 00:10 の取得。確定まで +0.1% 程度上振れするので、翌朝の定例で再取得して上書きする。"""
import csv
D = '2026-08-31'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 400180, 5971, 84, 91
SALES = [('ナノガラス脱毛パッド',175120,2587),('W固定スマホ車載ホルダー',51740,1592),
 ('快適マジックインソール',43780,796),('ムダ毛シェーバー',34900,0),('ナノバブルシャワーヘッド',27920,0),
 ('バランスケアスリッパ',19920,0),('むくみ取りかっさ',15920,0),('姿勢サポートチェア',11960,0),
 ('完全遮光・接触冷感UVハット',9960,996),('2WAYシートボックス',4980,0),('偏光・調光サングラス',3980,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',119400+27860),('ナノガラス脱毛パッド','黒桃',19900+7960)]
AD = {'ナノガラス脱毛パッド':70183,'W固定スマホ車載ホルダー':32494,'快適マジックインソール':26103,
 'カタログ全部（テスト）':17040,'ムダ毛シェーバー':15940,'むくみ取りかっさ':11508,'姿勢サポートチェア':10935,
 'バランスケアスリッパ':10076,'2WAYシートボックス':9956,'ナノバブルシャワーヘッド':7454,
 'ビジュアル耳かき':5849,'完全遮光・接触冷感UVハット':5484,'偏光・調光サングラス':152}
ACCT = 223174
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC
assert sum(g for n,_,g in VARIANT) == 175120
assert sum(AD.values()) == ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σキャンペーン = アカウント {ACCT:,} ✓')

def append(path, rows):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == D for r in csv.reader(f)), f'{path} に {D} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} +{len(rows)}行')
append('data/daily/daily_sales.csv',   [[D,n,g,d] for n,g,d in SALES])
append('data/daily/daily_variant.csv', [[D,n,g,v] for n,g,v in VARIANT])
append('data/daily/daily_ad.csv',      [[D,c,v] for c,v in AD.items()])
print(f'\n8/31 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 / 広告 {ACCT:,} / MER {(STORE_GROSS-STORE_DISC)/ACCT:.2f}')
