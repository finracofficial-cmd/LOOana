# -*- coding: utf-8 -*-
"""2026-10-18(日) をCSVへ追記。10/19 14時台取得（Supermetrics再接続後）。広告費はキャンペーン合算（暫定）。
当日: プライム感謝祭本番3日目。予算変更なし（14セット・249,000）。VIP特典の無料優先配送18件（14+4・gross 0円）は売上行に入れない。返品0。
広告なし商品: ネックマッサージャー・形状記憶日傘・サングラス 各1個（自然購入）。"""
import csv
D='2026-10-18'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'高見えレザーヘッドレストフック':3980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 'ネックマッサージャー':8980,'壁掛けディスペンサー':6980,'形状記憶日傘':4980,'偏光・調光サングラス':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 566320, 21296, 108, 152
VIP_GIFT_QTY, RETURNED_QTY = 18, 0
SALES=[('伸縮ガラスクリーナー',143280,8358),('ナノガラス脱毛パッド',135320,0),('快適マジックインソール',79600,4975),
 ('W固定スマホ車載ホルダー',75620,3184),('4-in-1マルチクリーナー',41880,1396),('高見えレザーヘッドレストフック',31840,2587),
 ('ポータブルヒートシーラー',19900,796),('ナノバブルシャワーヘッド',13960,0),('ネックマッサージャー',8980,0),
 ('壁掛けディスペンサー',6980,0),('形状記憶日傘',4980,0),('偏光・調光サングラス',3980,0)]
# ナノ: ピュアホワイト55,720＋セージ19,900＝白緑／マットブラック59,700＝黒桃 ／ フック: ブラック7,960＝黒／グレー15,920＋ブラウン7,960＝茶灰 ／ ディスペンサー: ブラック3本6,980
VAR=[('ナノガラス脱毛パッド','白緑',55720+19900),('ナノガラス脱毛パッド','黒桃',59700),
 ('高見えレザーヘッドレストフック','黒',7960),('高見えレザーヘッドレストフック','茶灰',15920+7960),
 ('壁掛けディスペンサー','3本',6980)]
AD={'W固定スマホ車載ホルダー':35773,'カタログ全部（テスト）':10400,'ディスペンサー':6514,'ナノガラス脱毛パッド':89112,
 'ナノバブルシャワーヘッド':10238,'ポータブルヒートシーラー':11306,'伸縮ガラスクリーナー':38121,'快適マジックインソール':41337,
 '高見えレザーヘッドレストフック':8093,'4-in-1マルチクリーナー':12431}
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
