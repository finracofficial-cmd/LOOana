# -*- coding: utf-8 -*-
"""2026-09-24(木・連休明け平日初日) をCSVへ追記。広告費は9/25 12時取得の暫定・明朝確定。
卓上冷感クーラーは返品1個のみ(gross 0)のためSALESに含めない(A案・販売数0)。"""
import csv
D='2026-09-24'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 507120, 12338, 107, 124
RETURN_QTY=1  # 卓上冷感クーラー 1個返品(5,980円・A案で損益には入れない)
SALES=[('伸縮ガラスクリーナー',139300,5771),('ナノガラス脱毛パッド',119400,1592),
 ('快適マジックインソール',95520,4179),('W固定スマホ車載ホルダー',63680,0),
 ('バランスケアスリッパ',19920,0),('もちふわ肉球サンダル',19900,0),
 ('携帯電動シェーバー',14940,0),('姿勢サポートチェア',11960,0),
 ('高見えレザーヘッドレストフック',11940,796),('UV歯ブラシ除菌器',8980,0),
 ('優先配送',1580,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',87560+3980),('ナノガラス脱毛パッド','黒桃',11940+15920),
 ('高見えレザーヘッドレストフック','黒',7960),('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'ナノガラス脱毛パッド':66820,'快適マジックインソール':31923,'伸縮ガラスクリーナー':27609,
 'W固定スマホ車載ホルダー':26635,'高見えレザーヘッドレストフック':16587,'もちふわ肉球サンダル':9374,
 'UV歯ブラシ除菌器':8280,'姿勢サポートチェア':7794,'バランスケアスリッパ':7681,
 'カタログ全部（テスト）':7295,'携帯電動シェーバー':6717}
ACCT=216715   # アカウントレベルと差0円（9/25 12時取得の暫定・明朝確定）。予算256,000の84.7%
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '快適マジックインソール':3980,'高見えレザーヘッドレストフック':3980,'UV歯ブラシ除菌器':8980,
 '姿勢サポートチェア':5980,'バランスケアスリッパ':4980,'携帯電動シェーバー':4980,
 'もちふわ肉球サンダル':3980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS+RETURN_QTY, items   # 販売数125 = net 124 + 卓上返品1
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==119400+11940
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
