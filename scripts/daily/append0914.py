# -*- coding: utf-8 -*-
"""2026-09-14(月) をCSVへ追記。全数値はShopify/Metaの当日実測（広告費は9/15 00:1x取得の暫定・明朝確定）。"""
import csv
D='2026-09-14'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 503580, 16321, 102, 121
SALES=[('ナノガラス脱毛パッド',179100,5771),('伸縮ガラスクリーナー',83580,1592),
 ('快適マジックインソール',63680,3383),('W固定スマホ車載ホルダー',59700,796),
 ('高見えレザーヘッドレストフック',31840,1791),('姿勢サポートチェア',29900,1196),
 ('バランスケアスリッパ',29880,996),('ムダ毛シェーバー',13960,0),('もちふわ肉球サンダル',11940,796)]
VARIANT=[('ナノガラス脱毛パッド','白緑',115420+27860),('ナノガラス脱毛パッド','黒桃',23880+11940),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',7960)]
AD={'ナノガラス脱毛パッド':70734,'伸縮ガラスクリーナー':30906,'W固定スマホ車載ホルダー':28789,
 '快適マジックインソール':28040,'高見えレザーヘッドレストフック':15453,'カタログ全部（テスト）':13022,
 'バランスケアスリッパ':10611,'ムダ毛シェーバー':10227,'姿勢サポートチェア':8913,
 'もちふわ肉球サンダル':4277,'4-in-1マルチクリーナー':16}
ACCT=220988   # キャンペーン合算＝アカウントレベルと差0円（明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,
 'バランスケアスリッパ':4980,'ムダ毛シェーバー':6980,'もちふわ肉球サンダル':3980}
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
