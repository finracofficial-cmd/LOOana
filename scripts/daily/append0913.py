# -*- coding: utf-8 -*-
"""2026-09-13(日) をCSVへ追記。全数値はShopify/Metaの当日実測。"""
import csv
D='2026-09-13'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 670860, 12340, 140, 157
SALES=[('ナノガラス脱毛パッド',195020,1592),('伸縮ガラスクリーナー',115420,2388),
 ('W固定スマホ車載ホルダー',99500,796),('快適マジックインソール',91540,3980),('ムダ毛シェーバー',48860,0),
 ('高見えレザーヘッドレストフック',35820,2388),('バランスケアスリッパ',24900,0),('姿勢サポートチェア',23920,1196),
 ('壁掛けディスペンサー',6980,0),('4-in-1マルチクリーナー',6980,0),('ナノバブルシャワーヘッド',6980,0),
 ('癒しの指圧マット',5980,0),('携帯電動シェーバー',4980,0),('3D足臭リセットブラシ',3980,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',119400+15920),('ナノガラス脱毛パッド','黒桃',43780+15920),
 ('高見えレザーヘッドレストフック','黒',27860),('高見えレザーヘッドレストフック','茶灰',7960),
 ('壁掛けディスペンサー','3本',6980)]
AD={'ナノガラス脱毛パッド':74217+22943,'快適マジックインソール':39921,'W固定スマホ車載ホルダー':39096,
 '伸縮ガラスクリーナー':30475,'カタログ全部（テスト）':17153,'バランスケアスリッパ':14062,
 'ムダ毛シェーバー':13979,'姿勢サポートチェア':11531,'高見えレザーヘッドレストフック':10696,
 '4-in-1マルチクリーナー':7394,'ナノバブルシャワーヘッド':121}
ACCT=281588   # adset合算＝アカウントレベルと差0円（明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '快適マジックインソール':3980,'ムダ毛シェーバー':6980,'高見えレザーヘッドレストフック':3980,
 'バランスケアスリッパ':4980,'姿勢サポートチェア':5980,'壁掛けディスペンサー':6980,
 '4-in-1マルチクリーナー':6980,'ナノバブルシャワーヘッド':6980,'癒しの指圧マット':5980,
 '携帯電動シェーバー':4980,'3D足臭リセットブラシ':3980}
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
