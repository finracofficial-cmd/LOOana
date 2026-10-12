# -*- coding: utf-8 -*-
"""2026-10-12(月) をCSVへ追記。10/13 00時台取得。広告費はキャンペーン合算272,708円（暫定）。
当日: ネック停止（朝）・4-in-1 8,000→10,000・18時台にヒートシーラー新規8,000円・クリーナーsabu 8,000→11,000・車載/フック/クリーナー主力の広告が再審査。
VIP特典の無料優先配送26件（商品名2種 12+14・gross 0円）は売上行に入れない。有料の優先配送2件（790円×2）。返品1点（ナノガラス3,980円・A案で売上から引かない）。"""
import csv
D='2026-10-12'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'姿勢サポートチェア':5980,
 'ナノバブルシャワーヘッド':6980,'温感EMSフェイシャルワンド':5980,'姿勢サポートベルト':5980,'バランスケアスリッパ':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 629560, 28258, 114, 178
VIP_GIFT_QTY, RETURNED_QTY = 26, 1
SALES=[('ナノガラス脱毛パッド',183080,2388),('伸縮ガラスクリーナー',123380,8159),('快適マジックインソール',95520,9353),
 ('W固定スマホ車載ホルダー',71640,1791),('高見えレザーヘッドレストフック',63680,4776),('4-in-1マルチクリーナー',34900,0),
 ('ポータブルヒートシーラー',19900,1791),('姿勢サポートチェア',11960,0),('ナノバブルシャワーヘッド',6980,0),
 ('温感EMSフェイシャルワンド',5980,0),('姿勢サポートベルト',5980,0),('バランスケアスリッパ',4980,0),('優先配送',1580,0)]
# ナノガラス: ピュアホワイト87,560＋セージグリーン27,860＝白緑 ／ マットブラック63,680＋ベイビーピンク3,980＝黒桃
# フック: ブラック31,840＝黒 ／ ブラウン23,880＋グレー7,960＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',87560+27860),('ナノガラス脱毛パッド','黒桃',63680+3980),
 ('高見えレザーヘッドレストフック','黒',31840),('高見えレザーヘッドレストフック','茶灰',23880+7960)]
AD={'W固定スマホ車載ホルダー':33396,'カタログ全部（テスト）':10823,'ナノガラス脱毛パッド':94733,'ネックマッサージャー2':1116,
 'バランスケアスリッパ':8172,'ポータブルヒートシーラー':2520,'伸縮ガラスクリーナー':39282,'姿勢サポートチェア':9611,
 '快適マジックインソール':39981,'携帯電動シェーバー':6934,'高見えレザーヘッドレストフック':16385,'4-in-1マルチクリーナー':9755}
ACCT=272708
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
