# -*- coding: utf-8 -*-
"""2026-09-11(金) をCSVへ追記。全数値はShopify/Metaの当日実測。"""
import csv
D='2026-09-11'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 530250, 25076, 96, 128
SALES=[('ナノガラス脱毛パッド',131340,3184),('W固定スマホ車載ホルダー',103480,4179),
 ('伸縮ガラスクリーナー',83580,5970),('快適マジックインソール',71640,3980),
 ('高見えレザーヘッドレストフック',55720,5771),('姿勢サポートチェア',17940,1196),
 ('4-in-1マルチクリーナー',13960,0),('ムダ毛シェーバー',13960,0),('バランスケアスリッパ',9960,0),
 ('偏光・調光サングラス',7960,796),('ナノバブルシャワーヘッド',6980,0),('携帯電動シェーバー',4980,0),
 ('リカバリーサンダル',3980,0),('むくみ取りかっさ',3980,0),('優先配送',790,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',75620+3980),('ナノガラス脱毛パッド','黒桃',39800+11940),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',27860+3980)]
AD={'ナノガラス脱毛パッド':58498+16520,'W固定スマホ車載ホルダー':31128,'快適マジックインソール':30963,
 '伸縮ガラスクリーナー':14697,'カタログ全部（テスト）':13023,'ナノバブルシャワーヘッド':12746,
 'バランスケアスリッパ':12431,'ムダ毛シェーバー':12129,'高見えレザーヘッドレストフック':9820,
 '姿勢サポートチェア':9054,'4-in-1マルチクリーナー':8099}
ACCT=229108   # adset合算＝アカウントレベルと差0円（明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,
 '快適マジックインソール':3980,'高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,
 '4-in-1マルチクリーナー':6980,'ムダ毛シェーバー':6980,'バランスケアスリッパ':4980,
 '偏光・調光サングラス':3980,'ナノバブルシャワーヘッド':6980,'携帯電動シェーバー':4980,
 'リカバリーサンダル':3980,'むくみ取りかっさ':3980,'優先配送':790}
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
