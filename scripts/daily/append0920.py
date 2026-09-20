# -*- coding: utf-8 -*-
"""2026-09-20(日・連休2日目・楽天マラソン期間中) をCSVへ追記。広告費は9/21 00時取得の暫定・明朝確定。"""
import csv
D='2026-09-20'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 671340, 20100, 135, 164
SALES=[('ナノガラス脱毛パッド',147260,2388),('伸縮ガラスクリーナー',131340,2388),
 ('快適マジックインソール',95520,4179),('W固定スマホ車載ホルダー',95520,3582),
 ('高見えレザーヘッドレストフック',71640,3980),('バランスケアスリッパ',44820,996),
 ('もちふわ肉球サンダル',35820,2587),('UV歯ブラシ除菌器',17960,0),
 ('携帯電動シェーバー',14940,0),('ナノバブルシャワーヘッド',6980,0),
 ('接触冷感UVアームカバー',3980,0),('スタイルアップインナー',3980,0),('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',115420+11940),('ナノガラス脱毛パッド','黒桃',19900),
 ('高見えレザーヘッドレストフック','黒',51740),('高見えレザーヘッドレストフック','茶灰',15920+3980)]
AD={'ナノガラス脱毛パッド':90493,'快適マジックインソール':35536,'W固定スマホ車載ホルダー':34608,
 '伸縮ガラスクリーナー':28228,'高見えレザーヘッドレストフック':18027,'もちふわ肉球サンダル':16813,
 '姿勢サポートチェア':10971,'バランスケアスリッパ':10444,'カタログ全部（テスト）':10269,
 'UV歯ブラシ除菌器':9862,'携帯電動シェーバー':8410}
ACCT=273661   # アカウントレベルと差0円（9/21 00時取得の暫定・明朝確定）。予算246,000の111%＝日曜上振れ
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'バランスケアスリッパ':4980,
 'もちふわ肉球サンダル':3980,'UV歯ブラシ除菌器':8980,'携帯電動シェーバー':4980,
 'ナノバブルシャワーヘッド':6980,'接触冷感UVアームカバー':3980,'スタイルアップインナー':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS, items
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==147260+71640
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
