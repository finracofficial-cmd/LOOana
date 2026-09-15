# -*- coding: utf-8 -*-
"""2026-09-15(火) をCSVへ追記。全数値はShopify/Metaの当日実測（広告費は9/16 00:1x取得の暫定・明朝確定）。"""
import csv
D='2026-09-15'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 542580, 20897, 103, 133
SALES=[('ナノガラス脱毛パッド',175120,5771),('伸縮ガラスクリーナー',75620,2388),
 ('快適マジックインソール',67660,4975),('W固定スマホ車載ホルダー',67660,1592),
 ('高見えレザーヘッドレストフック',55720,4179),('姿勢サポートチェア',29900,1196),
 ('ムダ毛シェーバー',20940,0),('もちふわ肉球サンダル',19900,796),('バランスケアスリッパ',14940,0),
 ('電動温熱カッサ',6980,0),('完全遮光・形状記憶',4980,0),('優先配送',3160,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',115420+19900),('ナノガラス脱毛パッド','黒桃',31840+7960),
 ('高見えレザーヘッドレストフック','黒',31840),('高見えレザーヘッドレストフック','茶灰',15920+7960)]
AD={'ナノガラス脱毛パッド':77419,'W固定スマホ車載ホルダー':32961,'快適マジックインソール':29641,
 '伸縮ガラスクリーナー':22905,'高見えレザーヘッドレストフック':15177,'バランスケアスリッパ':12044,
 'カタログ全部（テスト）':12025,'ムダ毛シェーバー':11579,'もちふわ肉球サンダル':9093,
 '姿勢サポートチェア':8002,'電動温熱カッサ':3545}
ACCT=234391   # キャンペーン合算。アカウントレベルは234,409（差18円=0.008%・取得時刻差のドリフト。明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,
 'ムダ毛シェーバー':6980,'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980,
 '電動温熱カッサ':6980,'完全遮光・形状記憶':4980,'優先配送':790}
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
