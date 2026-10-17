# -*- coding: utf-8 -*-
"""2026-10-17(土) をCSVへ追記。10/18 00時台取得。広告費はキャンペーン合算（暫定）。
当日: プライム感謝祭本番2日目。02時に家事手袋停止（326円）。午後にディスペンサー再開（10,000）・インソール主力28,000＋新セット8,000。
VIP特典の無料優先配送18件（13+5・gross 0円）は売上行に入れない。携帯電動シェーバー1点は当日返品（返品額4,980・A案で売上から引かない）。"""
import csv
D='2026-10-17'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'4-in-1マルチクリーナー':6980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'ナノバブルシャワーヘッド':6980,
 'ポータブルヒートシーラー':3980,'壁掛けディスペンサー':5980,'携帯電動シェーバー':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 585220, 20701, 114, 156
VIP_GIFT_QTY, RETURNED_QTY = 18, 1
SALES=[('ナノガラス脱毛パッド',206960,4776),('快適マジックインソール',95520,6567),('W固定スマホ車載ホルダー',79600,1592),
 ('伸縮ガラスクリーナー',71640,1592),('4-in-1マルチクリーナー',41880,1396),('高見えレザーヘッドレストフック',35820,3582),
 ('ナノバブルシャワーヘッド',20940,0),('ポータブルヒートシーラー',15920,0),('壁掛けディスペンサー',11960,1196),('携帯電動シェーバー',4980,0)]
# ナノ: ピュアホワイト99,500＋セージ43,780＝白緑／マットブラック51,740＋ピンク11,940＝黒桃
# フック: ブラック15,920＝黒／グレー11,940＋ブラウン7,960＝茶灰 ／ ディスペンサー: シルバー2本5,980＋ブラック2本5,980＝2本
VAR=[('ナノガラス脱毛パッド','白緑',99500+43780),('ナノガラス脱毛パッド','黒桃',51740+11940),
 ('高見えレザーヘッドレストフック','黒',15920),('高見えレザーヘッドレストフック','茶灰',11940+7960),
 ('壁掛けディスペンサー','2本',5980+5980)]
AD={'W固定スマホ車載ホルダー':39154,'カタログ全部（テスト）':7646,'ディスペンサー':3528,'ナノガラス脱毛パッド':77455,
 'ナノバブルシャワーヘッド':9291,'ポータブルヒートシーラー':11880,'ロングニトリル家事手袋':326,'伸縮ガラスクリーナー':38279,
 '快適マジックインソール':32205,'高見えレザーヘッドレストフック':7932,'4-in-1マルチクリーナー':9750}
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
