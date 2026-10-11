# -*- coding: utf-8 -*-
"""2026-10-11(日) をCSVへ追記。10/12 06時台取得。広告費はキャンペーン合算260,383円（暫定）。
当日07時台: 車載 主力33,000→25,000→30,000・新CR(-sab)停止／クリーナー 主力32,000→27,000（日予算261,000→245,000）。
VIP特典の無料優先配送20件（商品名2種 9+11・gross 0円）は売上行に入れない。有料の優先配送1件（790円）。返品0。"""
import csv
D='2026-10-11'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'携帯電動シェーバー':4980,'ネックマッサージャー':8980,
 'バランスケアスリッパ':4980,'姿勢サポートチェア':5980,'偏光・調光サングラス':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 569090, 18309, 112, 156
VIP_GIFT_QTY, RETURNED_QTY = 20, 0
SALES=[('ナノガラス脱毛パッド',183080,5970),('伸縮ガラスクリーナー',119400,3184),('W固定スマホ車載ホルダー',75620,2388),
 ('快適マジックインソール',67660,2388),('高見えレザーヘッドレストフック',35820,3383),('4-in-1マルチクリーナー',27920,0),
 ('携帯電動シェーバー',19920,996),('ネックマッサージャー',17960,0),('姿勢サポートチェア',11960,0),
 ('バランスケアスリッパ',4980,0),('偏光・調光サングラス',3980,0),('優先配送',790,0)]
# ナノガラス: ピュアホワイト91,540＋セージグリーン23,880＝白緑 ／ マットブラック51,740＋ベイビーピンク15,920＝黒桃
# フック: ブラック15,920＝黒 ／ グレー19,900＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',91540+23880),('ナノガラス脱毛パッド','黒桃',51740+15920),
 ('高見えレザーヘッドレストフック','黒',15920),('高見えレザーヘッドレストフック','茶灰',19900)]
AD={'W固定スマホ車載ホルダー':31165,'カタログ全部（テスト）':10245,'ナノガラス脱毛パッド':81048,'ネックマッサージャー2':11707,
 'バランスケアスリッパ':7860,'伸縮ガラスクリーナー':38194,'姿勢サポートチェア':10161,'快適マジックインソール':36487,
 '携帯電動シェーバー':7225,'高見えレザーヘッドレストフック':17476,'4-in-1マルチクリーナー':8815}
ACCT=260383
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
