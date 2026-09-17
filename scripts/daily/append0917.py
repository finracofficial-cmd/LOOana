# -*- coding: utf-8 -*-
"""2026-09-17(木) をCSVへ追記。全数値はShopify/Metaの当日実測（広告費は9/18 00:1x取得の暫定・明朝確定）。"""
import csv
D='2026-09-17'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 506160, 18412, 100, 123
SALES=[('ナノガラス脱毛パッド',131340,2388),('W固定スマホ車載ホルダー',91540,1592),
 ('快適マジックインソール',79600,4378),('高見えレザーヘッドレストフック',43780,3383),
 ('伸縮ガラスクリーナー',43780,2388),('姿勢サポートチェア',35880,2691),
 ('もちふわ肉球サンダル',35820,1592),('バランスケアスリッパ',19920,0),('ムダ毛シェーバー',6980,0),
 ('電動温熱カッサ',6980,0),('完全遮光・接触冷感UVハット',4980,0),('リカバリーサンダル',3980,0),('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',83580+7960),('ナノガラス脱毛パッド','黒桃',31840+7960),
 ('高見えレザーヘッドレストフック','黒',19900),('高見えレザーヘッドレストフック','茶灰',15920+7960)]
AD={'ナノガラス脱毛パッド':77122,'快適マジックインソール':32395,'W固定スマホ車載ホルダー':31937,
 '伸縮ガラスクリーナー':26207,'高見えレザーヘッドレストフック':13147,'ムダ毛シェーバー':12646,
 'カタログ全部（テスト）':12484,'もちふわ肉球サンダル':12304,'バランスケアスリッパ':9830,
 '姿勢サポートチェア':9605,'電動温熱カッサ':7451}
ACCT=245128   # キャンペーン合算＝アカウントレベルと差0円（明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'伸縮ガラスクリーナー':3980,'姿勢サポートチェア':5980,
 'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980,'ムダ毛シェーバー':6980,
 '電動温熱カッサ':6980,'完全遮光・接触冷感UVハット':4980,'リカバリーサンダル':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS, items
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
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
