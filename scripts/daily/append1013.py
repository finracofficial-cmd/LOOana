# -*- coding: utf-8 -*-
"""2026-10-13(火) をCSVへ追記。10/14 02時台取得。広告費はキャンペーン合算228,072円（暫定）。
当日: 朝に携帯シェーバー停止・ヒートシーラー 10,000→13,000（日中）。消化は日予算247,000に対して低め。
VIP特典の無料優先配送12件（商品名2種 10+2・gross 0円）は売上行に入れない。有料の優先配送2件（790円×2）。返品0件。"""
import csv
D='2026-10-13'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'ポータブルヒートシーラー':3980,
 '4-in-1マルチクリーナー':6980,'快適マジックインソール':3980,'姿勢サポートチェア':5980,'バランスケアスリッパ':4980,
 'UV歯ブラシ除菌器':8980,'高見えレザーヘッドレストフック':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 475300, 10348, 100, 128
VIP_GIFT_QTY, RETURNED_QTY = 12, 0
SALES=[('ナノガラス脱毛パッド',151240,796),('W固定スマホ車載ホルダー',103480,3980),('伸縮ガラスクリーナー',87560,3184),
 ('ポータブルヒートシーラー',55720,1592),('4-in-1マルチクリーナー',20940,0),('快適マジックインソール',15920,796),
 ('姿勢サポートチェア',11960,0),('バランスケアスリッパ',9960,0),('UV歯ブラシ除菌器',8980,0),
 ('高見えレザーヘッドレストフック',7960,0),('優先配送',1580,0)]
# ナノガラス: ピュアホワイト51,740＋セージグリーン23,880＝白緑 ／ マットブラック67,660＋ベイビーピンク7,960＝黒桃
# フック: ブラック3,980＝黒 ／ グレー3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',51740+23880),('ナノガラス脱毛パッド','黒桃',67660+7960),
 ('高見えレザーヘッドレストフック','黒',3980),('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'W固定スマホ車載ホルダー':29073,'カタログ全部（テスト）':8525,'ナノガラス脱毛パッド':74143,'バランスケアスリッパ':6097,
 'ポータブルヒートシーラー':13488,'伸縮ガラスクリーナー':34723,'姿勢サポートチェア':8444,'快適マジックインソール':31912,
 '携帯電動シェーバー':21,'高見えレザーヘッドレストフック':13379,'4-in-1マルチクリーナー':8267}
ACCT=228072
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
