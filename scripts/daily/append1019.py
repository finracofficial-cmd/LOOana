# -*- coding: utf-8 -*-
"""2026-10-19(月) をCSVへ追記。10/20 01:50頃取得。広告費はキャンペーン合算（暫定）。
当日: プライム感謝祭最終日。予算変更なし（14セット・249,000）。VIP特典の無料優先配送18件（12+6・gross 0円）は売上行に入れない。返品0。
広告なし商品: むくみ取りかっさ 1個（停止中・自然購入）。"""
import csv
D='2026-10-19'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 '壁掛けディスペンサー':6980,'むくみ取りかっさ':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 513540, 22487, 93, 141
VIP_GIFT_QTY, RETURNED_QTY = 18, 0
SALES=[('ナノガラス脱毛パッド',151240,3184),('快適マジックインソール',87560,6766),('伸縮ガラスクリーナー',71640,1592),
 ('W固定スマホ車載ホルダー',67660,3383),('高見えレザーヘッドレストフック',51740,5771),('4-in-1マルチクリーナー',34900,0),
 ('ポータブルヒートシーラー',23880,1791),('ナノバブルシャワーヘッド',13960,0),('壁掛けディスペンサー',6980,0),('むくみ取りかっさ',3980,0)]
# ナノ: ピュアホワイト67,660＋セージ11,940＝白緑／マットブラック51,740＋ベイビーピンク19,900＝黒桃 ／ フック: ブラック19,900＝黒／ブラウン23,880＋グレー7,960＝茶灰 ／ ディスペンサー: ブラック3本6,980
VAR=[('ナノガラス脱毛パッド','白緑',67660+11940),('ナノガラス脱毛パッド','黒桃',51740+19900),
 ('高見えレザーヘッドレストフック','黒',19900),('高見えレザーヘッドレストフック','茶灰',23880+7960),
 ('壁掛けディスペンサー','3本',6980)]
AD={'W固定スマホ車載ホルダー':36238,'カタログ全部（テスト）':8600,'ディスペンサー':6612,'ナノガラス脱毛パッド':74865,
 'ナノバブルシャワーヘッド':8123,'ポータブルヒートシーラー':11015,'伸縮ガラスクリーナー':36937,'快適マジックインソール':32617,
 '高見えレザーヘッドレストフック':7642,'4-in-1マルチクリーナー':9289}
ACCT=sum(AD.values())
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY
for n in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック','壁掛けディスペンサー'):
    assert sum(a for m,a,_ in SALES if m==n)==sum(a for m,_,a in VAR if m==n), n
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
