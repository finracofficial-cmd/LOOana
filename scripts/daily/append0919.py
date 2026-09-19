# -*- coding: utf-8 -*-
"""2026-09-19(土・楽天マラソン初日20時〜) をCSVへ追記。広告費は9/20 07時取得の暫定・明朝確定。"""
import csv
D='2026-09-19'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 647460, 27768, 122, 158
SALES=[('ナノガラス脱毛パッド',191040,3980),('伸縮ガラスクリーナー',107460,4179),
 ('W固定スマホ車載ホルダー',87560,2388),('高見えレザーヘッドレストフック',83580,7363),
 ('快適マジックインソール',63680,3184),('もちふわ肉球サンダル',31840,1791),
 ('姿勢サポートチェア',29900,3887),('UV歯ブラシ除菌器',17960,0),
 ('携帯電動シェーバー',14940,0),('バランスケアスリッパ',9960,996),
 ('リカバリーサンダル',3980,0),('3D足臭リセットブラシ',3980,0),('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',123380+11940),('ナノガラス脱毛パッド','黒桃',51740+3980),
 ('高見えレザーヘッドレストフック','黒',71640),('高見えレザーヘッドレストフック','茶灰',7960+3980)]
AD={'ナノガラス脱毛パッド':81324,'W固定スマホ車載ホルダー':31750,'快適マジックインソール':29274,
 '伸縮ガラスクリーナー':27659,'UV歯ブラシ除菌器':16857,'高見えレザーヘッドレストフック':14642,
 'もちふわ肉球サンダル':12462,'バランスケアスリッパ':8036,'カタログ全部（テスト）':7865,
 '姿勢サポートチェア':7517,'携帯電動シェーバー':7046}
ACCT=244432   # アカウントレベルと差0円（9/20 07時取得の暫定・明朝確定）
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'快適マジックインソール':3980,'もちふわ肉球サンダル':3980,
 '姿勢サポートチェア':5980,'UV歯ブラシ除菌器':8980,'携帯電動シェーバー':4980,
 'バランスケアスリッパ':4980,'リカバリーサンダル':3980,'3D足臭リセットブラシ':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS, items
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==191040+83580
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
