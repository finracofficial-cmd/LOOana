# -*- coding: utf-8 -*-
"""2026-09-18(金) をCSVへ追記。全数値はShopify/Metaの実測（広告費は9/20朝取得＝確定级）。
ムダ毛シェーバーは返品1点のみ(gross 0)のため売上行なし。販売数116=net115+返品1。"""
import csv
D='2026-09-18'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 489490, 14335, 96, 115
SALES=[('ナノガラス脱毛パッド',167160,2388),('伸縮ガラスクリーナー',87560,4179),
 ('W固定スマホ車載ホルダー',55720,796),('快適マジックインソール',43780,0),
 ('高見えレザーヘッドレストフック',35820,3184),('UV歯ブラシ除菌器',26940,1796),
 ('バランスケアスリッパ',24900,996),('姿勢サポートチェア',23920,0),
 ('携帯電動シェーバー',14940,996),('もちふわ肉球サンダル',7960,0),('優先配送',790,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',119400+15920),('ナノガラス脱毛パッド','黒桃',23880+7960),
 ('高見えレザーヘッドレストフック','黒',7960),('高見えレザーヘッドレストフック','茶灰',23880+3980)]
AD={'ナノガラス脱毛パッド':78299,'W固定スマホ車載ホルダー':33666,'快適マジックインソール':31086,
 '伸縮ガラスクリーナー':27747,'もちふわ肉球サンダル':15179,'高見えレザーヘッドレストフック':14573,
 'UV歯ブラシ除菌器':12524,'カタログ全部（テスト）':9711,'バランスケアスリッパ':8987,
 '姿勢サポートチェア':8976,'携帯電動シェーバー':4584,'ムダ毛シェーバー':247,'電動温熱カッサ':28}
ACCT=245607   # アカウントレベルと差0円（9/20朝取得）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '快適マジックインソール':3980,'高見えレザーヘッドレストフック':3980,'UV歯ブラシ除菌器':8980,
 'バランスケアスリッパ':4980,'姿勢サポートチェア':5980,'携帯電動シェーバー':4980,
 'もちふわ肉球サンダル':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS+1, items   # 販売数116 ≥ net_items_sold 115（差=ムダ毛返品1点）
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==167160+35820
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
