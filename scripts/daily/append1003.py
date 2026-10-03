# -*- coding: utf-8 -*-
"""2026-10-03(土) をCSVへ追記。10/4 00時台取得。広告費はキャンペーン合算233,284（アカウント直取得233,369と差−85円=0.04%・取り込み途中）＝暫定、次回確定値で上書き。
VIP特典の「優先配送 (VIP特典)」1件はgross 0円（Monster Cartの無料ギフト）のため売上行に入れない（販売数の検算で+1として扱う）。"""
import csv
D='2026-10-03'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980,'姿勢サポートチェア':5980,
 'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980,'姿勢サポートベルト':5980,'むくみ取りかっさ':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 595360, 24883, 111, 145
VIP_GIFT_QTY = 1   # 優先配送 (VIP特典) gross 0
SALES=[('ナノガラス脱毛パッド',159200,2388),('W固定スマホ車載ホルダー',99500,4975),('伸縮ガラスクリーナー',95520,2587),
 ('快適マジックインソール',71640,4378),('姿勢サポートチェア',53820,4784),('高見えレザーヘッドレストフック',43780,4179),
 ('携帯電動シェーバー',19920,0),('UV歯ブラシ除菌器',17960,0),('もちふわ肉球サンダル',15920,1592),
 ('姿勢サポートベルト',5980,0),('バランスケアスリッパ',4980,0),('むくみ取りかっさ',3980,0),('優先配送',3160,0)]
# ナノガラス: ピュアホワイト91,540＋セージグリーン27,860＝白緑 ／ マットブラック35,820＋ベイビーピンク3,980＝黒桃
# フック: ブラック31,840＝黒 ／ グレー7,960＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',91540+27860),('ナノガラス脱毛パッド','黒桃',35820+3980),
 ('高見えレザーヘッドレストフック','黒',31840),('高見えレザーヘッドレストフック','茶灰',7960+3980)]
AD={'ナノガラス脱毛パッド':72268,'快適マジックインソール':31203,'伸縮ガラスクリーナー':31075,'W固定スマホ車載ホルダー':29125,
 '高見えレザーヘッドレストフック':17825,'もちふわ肉球サンダル':9274,'姿勢サポートチェア':8463,'バランスケアスリッパ':8403,
 'UV歯ブラシ除菌器':8286,'カタログ全部（テスト）':7062,'携帯電動シェーバー':6507,'ネックマッサージャー2':3793}
ACCT=233284
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS   # 返品0
assert sum(AD.values())==ACCT, sum(AD.values())
assert abs(ACCT-233369)/233369 < 0.001
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
