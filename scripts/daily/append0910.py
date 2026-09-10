# -*- coding: utf-8 -*-
"""2026-09-10(木) をCSVへ追記。全数値はShopify/Metaの当日実測。"""
import csv
D='2026-09-10'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 598990, 20854, 116, 141
SALES=[('ナノガラス脱毛パッド',210940,3184),('快適マジックインソール',103480,7761),
 ('W固定スマホ車載ホルダー',75620,1592),('伸縮ガラスクリーナー',67660,2388),('4-in-1マルチクリーナー',41880,3141),
 ('姿勢サポートチェア',35880,1196),('高見えレザーヘッドレストフック',23880,1592),('バランスケアスリッパ',19920,0),
 ('ナノバブルシャワーヘッド',6980,0),('ムダ毛シェーバー',6980,0),('2WAYシートボックス',4980,0),('優先配送',790,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',123380+3980),('ナノガラス脱毛パッド','黒桃',67660+15920),
 ('高見えレザーヘッドレストフック','黒',11940),('高見えレザーヘッドレストフック','茶灰',7960+3980)]
AD={'ナノガラス脱毛パッド':76917+18071,'快適マジックインソール':36637,'W固定スマホ車載ホルダー':36078,
 'ムダ毛シェーバー':19866,'伸縮ガラスクリーナー':17520,'バランスケアスリッパ':16425,
 'ナノバブルシャワーヘッド':16152,'カタログ全部（テスト）':15837,'高見えレザーヘッドレストフック':10965,
 '姿勢サポートチェア':9190,'4-in-1マルチクリーナー':9126,'2WAYシートボックス':153,'むくみ取りかっさ':74}
ACCT=283011   # adset合算＝アカウントレベルと差0円（それでも明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'W固定スマホ車載ホルダー':3980,
 '伸縮ガラスクリーナー':3980,'4-in-1マルチクリーナー':6980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'バランスケアスリッパ':4980,'ナノバブルシャワーヘッド':6980,
 'ムダ毛シェーバー':6980,'2WAYシートボックス':4980,'優先配送':790}
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
