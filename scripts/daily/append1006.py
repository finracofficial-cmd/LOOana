# -*- coding: utf-8 -*-
"""2026-10-06(火) をCSVへ追記。10/7 00時台取得。広告費はキャンペーン合算275,337（アカウント275,336と+1円・暫定）。
「優先配送 (VIP特典)」2件はgross 0円のため売上行に入れない（販売数の検算で+2）。ネックマッサージャーは売上0（広告費のみ）。"""
import csv
D='2026-10-06'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,'4-in-1マルチクリーナー':6980,'バランスケアスリッパ':4980,
 '携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 622080, 20007, 124, 148
VIP_GIFT_QTY = 2
SALES=[('ナノガラス脱毛パッド',183080,2388),('伸縮ガラスクリーナー',91540,3582),('W固定スマホ車載ホルダー',75620,1592),
 ('高見えレザーヘッドレストフック',67660,4975),('快適マジックインソール',63680,1791),('バランスケアスリッパ',59760,2988),
 ('姿勢サポートチェア',35880,2691),('4-in-1マルチクリーナー',20940,0),('携帯電動シェーバー',14940,0),
 ('UV歯ブラシ除菌器',8980,0)]
# ナノガラス: ピュアホワイト131,340＋セージグリーン27,860＝白緑 ／ マットブラック19,900＋ベイビーピンク3,980＝黒桃
# フック: ブラック23,880＝黒 ／ グレー23,880＋ブラウン19,900＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',131340+27860),('ナノガラス脱毛パッド','黒桃',19900+3980),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',23880+19900)]
AD={'UV歯ブラシ除菌器':9968,'W固定スマホ車載ホルダー':34003,'カタログ全部（テスト）':6565,
 'ナノガラス脱毛パッド':86699,'ネックマッサージャー2':10169,'バランスケアスリッパ':9566,'伸縮ガラスクリーナー':34509,
 '姿勢サポートチェア':9391,'快適マジックインソール':37246,'携帯電動シェーバー':7687,'高見えレザーヘッドレストフック':20775,
 '4-in-1マルチクリーナー':8759}
ACCT=275337
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS
assert sum(AD.values())==ACCT, sum(AD.values())
assert abs(ACCT-275336)/275336<0.001
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
