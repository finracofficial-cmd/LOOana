# -*- coding: utf-8 -*-
"""2026-09-21(月・敬老の日・楽天マラソン期間中) をCSVへ追記。広告費は9/22 07時取得の暫定・明朝確定。
返品: インソール1点(-3,980)・優先配送1点(-790)。名称なし行に+4,770の返品相殺あり（返品取消とみられる・売上に影響なし）。"""
import csv
D='2026-09-21'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 782020, 30049, 150, 190
SALES=[('ナノガラス脱毛パッド',206960,1592),('伸縮ガラスクリーナー',139300,4179),
 ('高見えレザーヘッドレストフック',135320,14129),('W固定スマホ車載ホルダー',87560,796),
 ('快適マジックインソール',83580,7761),('UV歯ブラシ除菌器',35920,0),
 ('携帯電動シェーバー',24900,0),('姿勢サポートチェア',23920,0),
 ('もちふわ肉球サンダル',19900,1592),('バランスケアスリッパ',9960,0),
 ('ビジュアル耳かき',4980,0),('完全遮光・接触冷感UVハット',4980,0),('優先配送',4740,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',143280+7960),('ナノガラス脱毛パッド','黒桃',51740+3980),
 ('高見えレザーヘッドレストフック','黒',87560),('高見えレザーヘッドレストフック','茶灰',39800+7960)]
AD={'ナノガラス脱毛パッド':87527,'快適マジックインソール':37358,'W固定スマホ車載ホルダー':36326,
 '伸縮ガラスクリーナー':34342,'高見えレザーヘッドレストフック':23773,'UV歯ブラシ除菌器':12211,
 'もちふわ肉球サンダル':11149,'カタログ全部（テスト）':9710,'姿勢サポートチェア':9498,
 'バランスケアスリッパ':9351,'携帯電動シェーバー':8019}
ACCT=279264   # アカウントレベルと差0円（9/22 07時取得の暫定・明朝確定）。予算256,000の109%＝祝日上振れ
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(AD.values())==ACCT, sum(AD.values())
PRICE={'ナノガラス脱毛パッド':3980,'伸縮ガラスクリーナー':3980,'高見えレザーヘッドレストフック':3980,
 'W固定スマホ車載ホルダー':3980,'快適マジックインソール':3980,'UV歯ブラシ除菌器':8980,
 '携帯電動シェーバー':4980,'姿勢サポートチェア':5980,'もちふわ肉球サンダル':3980,
 'バランスケアスリッパ':4980,'ビジュアル耳かき':4980,'完全遮光・接触冷感UVハット':4980,'優先配送':790}
items=sum(g//PRICE[n] for n,g,_ in SALES)
assert items==STORE_ITEMS+2, items   # 販売数192 ≥ net190（差=返品2点: インソール1・優先配送1）
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g for _,_,g in VARIANT)==206960+135320
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
