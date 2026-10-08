# -*- coding: utf-8 -*-
"""2026-10-08(木) をCSVへ追記。10/9 00時台取得。広告費はキャンペーン合算245,136＝アカウント（差0円・暫定）。
まとめ買いアプリを当日10:19にBundler→Pumperへ切替。VIP特典の無料優先配送1件（商品名が「VIP特典（無料優先配送＋次回1,000円OFFクーポン）_」に変更・gross 0円）は売上行に入れない。
姿勢サポートチェアは4個販売（gross 23,920÷5,980）・うち1個が当日返品扱い（net_items 3）。A案のため売上・原価は販売数4で計上。"""
import csv
D='2026-10-08'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'姿勢サポートチェア':5980,'4-in-1マルチクリーナー':6980,'バランスケアスリッパ':4980,
 '携帯電動シェーバー':4980,'ネックマッサージャー':8980,'ナノバブルシャワーヘッド':6980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 491510, 15323, 92, 115
VIP_GIFT_QTY, RETURNED_QTY = 1, 1
SALES=[('ナノガラス脱毛パッド',143280,1592),('快適マジックインソール',119400,8955),('伸縮ガラスクリーナー',59700,2388),
 ('高見えレザーヘッドレストフック',31840,1592),('W固定スマホ車載ホルダー',31840,796),('姿勢サポートチェア',23920,0),
 ('4-in-1マルチクリーナー',20940,0),('携帯電動シェーバー',19920,0),('ネックマッサージャー',17960,0),
 ('バランスケアスリッパ',14940,0),('ナノバブルシャワーヘッド',6980,0),('優先配送',790,0)]
# ナノガラス: ピュアホワイト51,740＋セージグリーン11,940＝白緑 ／ マットブラック71,640＋ベイビーピンク7,960＝黒桃
# フック: ブラック23,880＝黒 ／ グレー7,960＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',51740+11940),('ナノガラス脱毛パッド','黒桃',71640+7960),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',7960)]
AD={'W固定スマホ車載ホルダー':32694,'カタログ全部（テスト）':9291,'ナノガラス脱毛パッド':77288,'ネックマッサージャー2':10778,
 'バランスケアスリッパ':8644,'伸縮ガラスクリーナー':30008,'姿勢サポートチェア':8729,'快適マジックインソール':33083,
 '携帯電動シェーバー':7556,'高見えレザーヘッドレストフック':20088,'4-in-1マルチクリーナー':6977}
ACCT=245136
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY
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
