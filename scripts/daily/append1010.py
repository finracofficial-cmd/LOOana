# -*- coding: utf-8 -*-
"""2026-10-10(土) をCSVへ追記。10/11 06時台取得。広告費はキャンペーン合算261,209円（暫定・予算261,000の100.1%）。
当日00時台: フック20,000→15,000・スリッパ9,000→7,000・携帯シェーバー8,000→6,000（減額テスト）。
VIP特典の無料優先配送17件（商品名2種 8+9・gross 0円）は売上行に入れない。返品0。チェアの値引1,000円はVIP1000クーポン。"""
import csv
D='2026-10-10'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'携帯電動シェーバー':4980,'ネックマッサージャー':8980,
 'バランスケアスリッパ':4980,'姿勢サポートチェア':5980,'ナノバブルシャワーヘッド':6980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 662980, 22453, 127, 168
VIP_GIFT_QTY, RETURNED_QTY = 17, 0
SALES=[('ナノガラス脱毛パッド',163180,796),('快適マジックインソール',103480,6766),('W固定スマホ車載ホルダー',99500,796),
 ('伸縮ガラスクリーナー',95520,3980),('4-in-1マルチクリーナー',83760,4537),('高見えレザーヘッドレストフック',39800,3582),
 ('バランスケアスリッパ',24900,996),('ネックマッサージャー',17960,0),('姿勢サポートチェア',17940,1000),
 ('携帯電動シェーバー',9960,0),('ナノバブルシャワーヘッド',6980,0)]
# ナノガラス: ピュアホワイト75,620＋セージグリーン23,880＝白緑 ／ マットブラック55,720＋ベイビーピンク7,960＝黒桃
# フック: ブラック23,880＝黒 ／ グレー11,940＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',75620+23880),('ナノガラス脱毛パッド','黒桃',55720+7960),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',11940+3980)]
AD={'W固定スマホ車載ホルダー':41177,'カタログ全部（テスト）':10253,'ナノガラス脱毛パッド':78217,'ネックマッサージャー2':10212,
 'バランスケアスリッパ':6961,'伸縮ガラスクリーナー':37901,'姿勢サポートチェア':9179,'快適マジックインソール':38853,
 '携帯電動シェーバー':5768,'高見えレザーヘッドレストフック':14413,'4-in-1マルチクリーナー':8275}
ACCT=261209
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
