# -*- coding: utf-8 -*-
"""2026-09-16(水) をCSVへ追記。全数値はShopify/Metaの当日実測（広告費は9/17 00:1x取得の暫定・明朝確定）。"""
import csv
D='2026-09-16'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 465530, 10547, 99, 114
SALES=[('ナノガラス脱毛パッド',139300,2388),('快適マジックインソール',95520,3184),
 ('伸縮ガラスクリーナー',79600,1791),('W固定スマホ車載ホルダー',43780,796),
 ('高見えレザーヘッドレストフック',35820,796),('もちふわ肉球サンダル',27860,1592),
 ('ムダ毛シェーバー',20940,0),('電動温熱カッサ',6980,0),('姿勢サポートチェア',5980,0),
 ('バランスケアスリッパ',4980,0),('接触冷感UVアームカバー',3980,0),('優先配送',790,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',91540+15920),('ナノガラス脱毛パッド','黒桃',19900+11940),
 ('高見えレザーヘッドレストフック','黒',27860),('高見えレザーヘッドレストフック','茶灰',3980+3980)]
AD={'ナノガラス脱毛パッド':76994,'快適マジックインソール':33047,'W固定スマホ車載ホルダー':32149,
 '伸縮ガラスクリーナー':25787,'高見えレザーヘッドレストフック':16513,'カタログ全部（テスト）':14079,
 'ムダ毛シェーバー':11424,'バランスケアスリッパ':10684,'電動温熱カッサ':9025,
 'もちふわ肉球サンダル':8311,'姿勢サポートチェア':8189}
ACCT=246202   # キャンペーン合算＝アカウントレベルと差0円（明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'もちふわ肉球サンダル':3980,
 'ムダ毛シェーバー':6980,'電動温熱カッサ':6980,'姿勢サポートチェア':5980,'バランスケアスリッパ':4980,
 '接触冷感UVアームカバー':3980,'優先配送':790}
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
