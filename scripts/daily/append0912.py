# -*- coding: utf-8 -*-
"""2026-09-12(土) をCSVへ追記。全数値はShopify/Metaの当日実測。"""
import csv
D='2026-09-12'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 587200, 18310, 117, 140  # 販売数140 = net137+返品3
SALES=[('ナノガラス脱毛パッド',191040,3383),('伸縮ガラスクリーナー',127360,5572),
 ('快適マジックインソール',91540,4776),('W固定スマホ車載ホルダー',55720,796),('姿勢サポートチェア',35880,0),
 ('バランスケアスリッパ',34860,1992),('高見えレザーヘッドレストフック',19900,1791),('ムダ毛シェーバー',13960,0),
 ('ナノバブルシャワーヘッド',6980,0),('スマートノーズEMS美顔器',5980,0),('接触冷感UVパーカー',3980,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',107460+27860),('ナノガラス脱毛パッド','黒桃',51740+3980),
 ('高見えレザーヘッドレストフック','黒',15920),('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'ナノガラス脱毛パッド':61362+16301,'W固定スマホ車載ホルダー':30861,'快適マジックインソール':27798,
 '伸縮ガラスクリーナー':17077,'ムダ毛シェーバー':11169,'カタログ全部（テスト）':10866,
 'バランスケアスリッパ':10063,'高見えレザーヘッドレストフック':9370,'ナノバブルシャワーヘッド':9108,
 '4-in-1マルチクリーナー':8563,'姿勢サポートチェア':7029}
ACCT=219567   # adset合算（アカウントレベル219,576と9円差=0.004%・明朝確定再取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 'W固定スマホ車載ホルダー':3980,'姿勢サポートチェア':5980,'バランスケアスリッパ':4980,
 '高見えレザーヘッドレストフック':3980,'ムダ毛シェーバー':6980,'ナノバブルシャワーヘッド':6980,
 'スマートノーズEMS美顔器':5980,'接触冷感UVパーカー':3980}
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
