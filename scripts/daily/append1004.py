# -*- coding: utf-8 -*-
"""2026-10-04(日) をCSVへ追記。10/5 00時台取得。広告費はキャンペーン合算＝アカウント292,833（差0円・暫定）。
「優先配送 (VIP特典)」7件はgross 0円のため売上行に入れない（販売数の検算で+7）。"""
import csv
D='2026-10-04'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980,'姿勢サポートチェア':5980,
 'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980,'ネックマッサージャー':8980,'4-in-1マルチクリーナー':6980,
 'リカバリーサンダル':3980,'電動温熱カッサ':6980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 706550, 26072, 129, 170
VIP_GIFT_QTY = 7
SALES=[('ナノガラス脱毛パッド',214920,7562),('快適マジックインソール',91540,4975),('W固定スマホ車載ホルダー',79600,796),
 ('高見えレザーヘッドレストフック',71640,5572),('伸縮ガラスクリーナー',71640,3184),('ネックマッサージャー',44900,0),
 ('携帯電動シェーバー',34860,0),('姿勢サポートチェア',23920,1196),('4-in-1マルチクリーナー',20940,0),
 ('バランスケアスリッパ',19920,996),('リカバリーサンダル',11940,1791),('UV歯ブラシ除菌器',8980,0),
 ('電動温熱カッサ',6980,0),('もちふわ肉球サンダル',3980,0),('優先配送',790,0)]
# ナノガラス: ピュアホワイト123,380＋セージグリーン27,860＝白緑 ／ マットブラック51,740＋ベイビーピンク11,940＝黒桃
# フック: ブラック63,680＝黒 ／ グレー3,980＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',123380+27860),('ナノガラス脱毛パッド','黒桃',51740+11940),
 ('高見えレザーヘッドレストフック','黒',63680),('高見えレザーヘッドレストフック','茶灰',3980+3980)]
AD={'UV歯ブラシ除菌器':11439,'W固定スマホ車載ホルダー':32707,'もちふわ肉球サンダル':11188,'カタログ全部（テスト）':10593,
 'ナノガラス脱毛パッド':93037,'ネックマッサージャー2':10366,'バランスケアスリッパ':9839,'伸縮ガラスクリーナー':30619,
 '姿勢サポートチェア':9874,'快適マジックインソール':40723,'携帯電動シェーバー':8936,'高見えレザーヘッドレストフック':19808,
 '4-in-1マルチクリーナー':3704}
ACCT=292833
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS
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
