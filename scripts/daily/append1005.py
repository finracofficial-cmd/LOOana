# -*- coding: utf-8 -*-
"""2026-10-05(月) をCSVへ追記。10/6 00時台取得。広告費はキャンペーン合算225,565（アカウント225,490と+75円=0.03%・暫定）。
「優先配送 (VIP特典)」2件はgross 0円のため売上行に入れない（販売数の検算で+2）。"""
import csv
D='2026-10-05'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,'4-in-1マルチクリーナー':6980,'バランスケアスリッパ':4980,
 'ネックマッサージャー':8980,'2WAYシートボックス':4980,'完全遮光・形状記憶':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 527310, 17912, 102, 127
VIP_GIFT_QTY = 2
SALES=[('ナノガラス脱毛パッド',147260,3184),('伸縮ガラスクリーナー',99500,3184),('W固定スマホ車載ホルダー',83580,4179),
 ('高見えレザーヘッドレストフック',55720,5373),('快適マジックインソール',47760,796),('姿勢サポートチェア',23920,1196),
 ('4-in-1マルチクリーナー',20940,0),('バランスケアスリッパ',19920,0),('ネックマッサージャー',17960,0),
 ('2WAYシートボックス',4980,0),('完全遮光・形状記憶',4980,0),('優先配送',790,0)]
# ナノガラス: ピュアホワイト83,580＋セージグリーン15,920＝白緑 ／ マットブラック43,780＋ベイビーピンク3,980＝黒桃
# フック: ブラック31,840＝黒 ／ グレー11,940＋ブラウン11,940＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',83580+15920),('ナノガラス脱毛パッド','黒桃',43780+3980),
 ('高見えレザーヘッドレストフック','黒',31840),('高見えレザーヘッドレストフック','茶灰',11940+11940)]
AD={'UV歯ブラシ除菌器':8811,'W固定スマホ車載ホルダー':29388,'もちふわ肉球サンダル':17,'カタログ全部（テスト）':7271,
 'ナノガラス脱毛パッド':65345,'ネックマッサージャー2':8038,'バランスケアスリッパ':7499,'伸縮ガラスクリーナー':27551,
 '姿勢サポートチェア':7969,'快適マジックインソール':28467,'携帯電動シェーバー':6937,'高見えレザーヘッドレストフック':18561,
 '4-in-1マルチクリーナー':9711}
ACCT=225565
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS
assert sum(AD.values())==ACCT, sum(AD.values())
assert abs(ACCT-225490)/225490<0.001
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
