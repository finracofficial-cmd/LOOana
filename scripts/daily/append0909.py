# -*- coding: utf-8 -*-
"""2026-09-09(水) をCSVへ追記。全数値はShopify/Metaの当日実測。"""
import csv
D='2026-09-09'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 563140, 21807, 98, 124
SALES=[('ナノガラス脱毛パッド',119400,2388),('W固定スマホ車載ホルダー',79600,2388),
 ('快適マジックインソール',71640,5174),('姿勢サポートチェア',65780,6578),('伸縮ガラスクリーナー',51740,796),
 ('ナノバブルシャワーヘッド',48860,0),('バランスケアスリッパ',39840,996),('4-in-1マルチクリーナー',27920,0),
 ('壁掛けディスペンサー',17940,2691),('ムダ毛シェーバー',13960,0),('高見えレザーヘッドレストフック',11940,796),
 ('2WAYシートボックス',4980,0),('むくみ取りかっさ',3980,0),('偏光・調光サングラス',3980,0),('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',63680+19900),('ナノガラス脱毛パッド','黒桃',31840+3980),
 ('高見えレザーヘッドレストフック','茶灰',7960),('高見えレザーヘッドレストフック','黒',3980)]
AD={'ナノガラス脱毛パッド':55722+16093,'W固定スマホ車載ホルダー':31286,'快適マジックインソール':26852,
 'ムダ毛シェーバー':16525,'カタログ全部（テスト）':15671,'伸縮ガラスクリーナー':14428,
 'バランスケアスリッパ':14465,'ナノバブルシャワーヘッド':11361,'4-in-1マルチクリーナー':10265,
 '姿勢サポートチェア':8562,'むくみ取りかっさ':7129,'2WAYシートボックス':7278,
 '高見えレザーヘッドレストフック':3908,'温感EMSフェイシャルワンド':118}
ACCT=239663   # adset合算（アカウントレベル239,687と24円差=0.010%・明朝確定再取得）
# 検算1: Σ商品gross = 全店gross
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
# 検算2: Σ商品値引 = 全店値引
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
# 検算3: Σキャンペーン広告費 = アカウント（adset合算）
assert sum(AD.values())==ACCT, sum(AD.values())
# 販売数検算: Σ(gross÷売価)=全店販売数124（返品0なのでnet_itemsと一致）
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'快適マジックインソール':3980,
 '姿勢サポートチェア':5980,'伸縮ガラスクリーナー':3980,'ナノバブルシャワーヘッド':6980,
 'バランスケアスリッパ':4980,'4-in-1マルチクリーナー':6980,'壁掛けディスペンサー':5980,
 'ムダ毛シェーバー':6980,'高見えレザーヘッドレストフック':3980,'2WAYシートボックス':4980,
 'むくみ取りかっさ':3980,'偏光・調光サングラス':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS, items
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f)
    for n,g,d in SALES: w.writerow([D,n,g,d])
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f)
    for n,c in AD.items(): w.writerow([D,n,c])
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f)
    for n,v,g in VARIANT: w.writerow([D,n,v,g])
net=STORE_GROSS-STORE_DISC
print('appended', D, '実売', net, '広告', ACCT, 'MER', round(net/ACCT,2))
