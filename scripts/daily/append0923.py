# -*- coding: utf-8 -*-
"""2026-09-23(水・秋分の日・連休最終日) をCSVへ追記。広告費は9/24 08時取得の暫定・明朝確定。"""
import csv
D='2026-09-23'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 636040, 17117, 128, 148
SALES=[('ナノガラス脱毛パッド',151240,1592),('伸縮ガラスクリーナー',127360,3184),
 ('W固定スマホ車載ホルダー',91540,1592),('快適マジックインソール',71640,3582),
 ('高見えレザーヘッドレストフック',51740,4975),('UV歯ブラシ除菌器',44900,0),
 ('姿勢サポートチェア',35880,1196),('バランスケアスリッパ',34860,996),
 ('携帯電動シェーバー',14940,0),('もちふわ肉球サンダル',11940,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',107460+23880),('ナノガラス脱毛パッド','黒桃',15920+3980),
 ('高見えレザーヘッドレストフック','黒',43780),('高見えレザーヘッドレストフック','茶灰',7960)]
AD={'ナノガラス脱毛パッド':78860,'快適マジックインソール':39261,'W固定スマホ車載ホルダー':37311,
 '伸縮ガラスクリーナー':32890,'高見えレザーヘッドレストフック':20680,'もちふわ肉球サンダル':10680,
 'UV歯ブラシ除菌器':10472,'カタログ全部（テスト）':9951,'バランスケアスリッパ':9755,
 '姿勢サポートチェア':9047,'携帯電動シェーバー':8881}
ACCT=267788   # アカウントレベルと差0円（9/24 08時取得の暫定・明朝確定）。予算256,000の105%
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '快適マジックインソール':3980,'高見えレザーヘッドレストフック':3980,'UV歯ブラシ除菌器':8980,
 '姿勢サポートチェア':5980,'バランスケアスリッパ':4980,'携帯電動シェーバー':4980,'もちふわ肉球サンダル':3980}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS, items
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==151240+51740
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
