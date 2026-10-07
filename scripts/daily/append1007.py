# -*- coding: utf-8 -*-
"""2026-10-07(水) をCSVへ追記。10/8 00時台取得。広告費はキャンペーン合算250,127（アカウント250,373と−246円=0.098%・暫定）。
「優先配送 (VIP特典)」5件はgross 0円のため売上行に入れない（販売数の検算で+5）。UV歯ブラシは10/7未明に停止（80円のみ）。
サンダル（10/5広告停止）・ナノバブル・2WAYシートボックスは広告なしの自然購入。"""
import csv
D='2026-10-07'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,'4-in-1マルチクリーナー':6980,'バランスケアスリッパ':4980,
 '携帯電動シェーバー':4980,'ネックマッサージャー':8980,'ナノバブルシャワーヘッド':6980,'2WAYシートボックス':4980,
 'もちふわ肉球サンダル':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 503070, 10351, 100, 123
VIP_GIFT_QTY = 5
SALES=[('ナノガラス脱毛パッド',135320,0),('W固定スマホ車載ホルダー',99500,2388),('快適マジックインソール',67660,4179),
 ('伸縮ガラスクリーナー',67660,796),('4-in-1マルチクリーナー',34900,0),('姿勢サポートチェア',29900,1196),
 ('ネックマッサージャー',17960,0),('携帯電動シェーバー',14940,996),('高見えレザーヘッドレストフック',11940,796),
 ('ナノバブルシャワーヘッド',6980,0),('2WAYシートボックス',4980,0),('バランスケアスリッパ',4980,0),
 ('もちふわ肉球サンダル',3980,0),('優先配送',2370,0)]
# ナノガラス: ピュアホワイト103,480＋セージグリーン15,920＝白緑 ／ ベイビーピンク7,960＋マットブラック7,960＝黒桃
# フック: ブラック3,980＝黒 ／ グレー7,960＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',103480+15920),('ナノガラス脱毛パッド','黒桃',7960+7960),
 ('高見えレザーヘッドレストフック','黒',3980),('高見えレザーヘッドレストフック','茶灰',7960)]
AD={'UV歯ブラシ除菌器':80,'W固定スマホ車載ホルダー':32555,'カタログ全部（テスト）':9451,
 'ナノガラス脱毛パッド':76783,'ネックマッサージャー2':11094,'バランスケアスリッパ':8759,'伸縮ガラスクリーナー':30683,
 '姿勢サポートチェア':8617,'快適マジックインソール':37543,'携帯電動シェーバー':8750,'高見えレザーヘッドレストフック':19328,
 '4-in-1マルチクリーナー':6484}
ACCT=250127
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS
assert sum(AD.values())==ACCT, sum(AD.values())
assert abs(ACCT-250373)/250373<0.001
for n in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック'):
    assert sum(a for m,a,_ in SALES if m==n)==sum(a for m,_,a in VAR if m==n), n
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
