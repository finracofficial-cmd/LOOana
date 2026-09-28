# -*- coding: utf-8 -*-
"""2026-09-28(月) をCSVへ追記。広告費は9/29 01時取得の暫定（日付変更直後）・次回確定。"""
import csv
D='2026-09-28'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 569860, 15921, 117, 138
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,'携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980,
 '電動眉シェーバー':3980,'もちふわ肉球サンダル':3980,'形状記憶日傘':4980,'バランスケアスリッパ':4980,
 '完全遮光・接触冷感UVハット':4980,'むくみ取りかっさ':3980,'優先配送':790}
SALES=[('ナノガラス脱毛パッド',171140,2587),('W固定スマホ車載ホルダー',107460,2388),('伸縮ガラスクリーナー',75620,1592),
 ('快適マジックインソール',59700,3383),('高見えレザーヘッドレストフック',47760,4179),('姿勢サポートチェア',29900,0),
 ('携帯電動シェーバー',19920,996),('UV歯ブラシ除菌器',17960,0),('電動眉シェーバー',11940,0),('もちふわ肉球サンダル',7960,796),
 ('形状記憶日傘',4980,0),('バランスケアスリッパ',4980,0),('完全遮光・接触冷感UVハット',4980,0),('むくみ取りかっさ',3980,0),
 ('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',95520+27860),('ナノガラス脱毛パッド','黒桃',31840+15920),
 ('高見えレザーヘッドレストフック','黒',35820),('高見えレザーヘッドレストフック','茶灰',11940)]
AD={'UV歯ブラシ除菌器':10457,'W固定スマホ車載ホルダー':32630,'もちふわ肉球サンダル':9517,'カタログ全部（テスト）':8923,
 'ナノガラス脱毛パッド':73017,'バランスケアスリッパ':8445,'伸縮ガラスクリーナー':28272,'姿勢サポートチェア':8469,
 '快適マジックインソール':36108,'携帯電動シェーバー':8799,'電動眉シェーバー':8732,'高見えレザーヘッドレストフック':20618}
ACCT=253987
assert '\n2026-09-28,' not in open('data/daily/daily_sales.csv').read()
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)==STORE_ITEMS
assert sum(g for n,_,g in VARIANT if n=='ナノガラス脱毛パッド')==171140 and sum(g for n,_,g in VARIANT if n.startswith('高見え'))==47760
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VARIANT]
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2))
