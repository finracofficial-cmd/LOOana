# -*- coding: utf-8 -*-
"""2026-10-02(金) をCSVへ追記。売上・広告費とも10/3 00時台の取得（広告費はキャンペーン合算＝アカウント252,736で差0円・暫定、次回確定値で上書き）。"""
import csv
D='2026-10-02'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980,'姿勢サポートチェア':5980,
 'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 575220, 22893, 113, 139
SALES=[('ナノガラス脱毛パッド',151240,1592),('高見えレザーヘッドレストフック',99500,9353),('快適マジックインソール',87560,4776),
 ('伸縮ガラスクリーナー',75620,1592),('W固定スマホ車載ホルダー',63680,796),('もちふわ肉球サンダル',27860,796),
 ('携帯電動シェーバー',19920,0),('バランスケアスリッパ',19920,996),('UV歯ブラシ除菌器',17960,1796),('姿勢サポートチェア',11960,1196)]
# ナノガラス: ピュアホワイト91,540＋セージグリーン19,900＝白緑 ／ マットブラック31,840＋ベイビーピンク7,960＝黒桃
# フック: ブラック55,720＝黒 ／ グレー27,860＋ブラウン15,920＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',91540+19900),('ナノガラス脱毛パッド','黒桃',31840+7960),
 ('高見えレザーヘッドレストフック','黒',55720),('高見えレザーヘッドレストフック','茶灰',27860+15920)]
AD={'UV歯ブラシ除菌器':9591,'W固定スマホ車載ホルダー':32715,'もちふわ肉球サンダル':10248,'カタログ全部（テスト）':9016,
 'ナノガラス脱毛パッド':75730,'バランスケアスリッパ':9104,'伸縮ガラスクリーナー':31685,'姿勢サポートチェア':8746,
 '快適マジックインソール':37648,'携帯電動シェーバー':7851,'高見えレザーヘッドレストフック':20402}
ACCT=252736   # アカウントレベルと差0円（10/3 00時台取得の暫定）
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)==STORE_ITEMS   # 返品0
assert sum(AD.values())==ACCT, sum(AD.values())
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
