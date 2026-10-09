# -*- coding: utf-8 -*-
"""2026-10-09(金) をCSVへ追記。10/10 00時台取得。広告費はキャンペーン合算249,096＝アカウント（差0円・暫定）。
当日: 車載・クリーナーに新CRの検証セット（各8,000円）開始、ナノ主力60,000→54,000・BC検証20,000→26,000、16:30にVIP特典を8,000→7,000円へ。
VIP特典の無料優先配送8件（商品名2種・gross 0円）は売上行に入れない。返品0。"""
import csv
D='2026-10-09'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'携帯電動シェーバー':4980,'ネックマッサージャー':8980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 439920, 15926, 85, 112
VIP_GIFT_QTY, RETURNED_QTY = 8, 0
SALES=[('ナノガラス脱毛パッド',147260,796),('快適マジックインソール',79600,4179),('伸縮ガラスクリーナー',67660,4179),
 ('W固定スマホ車載ホルダー',47760,796),('高見えレザーヘッドレストフック',39800,3184),('ネックマッサージャー',26940,1796),
 ('4-in-1マルチクリーナー',20940,0),('携帯電動シェーバー',9960,996)]
# ナノガラス: ピュアホワイト71,640＋セージグリーン15,920＝白緑 ／ マットブラック51,740＋ベイビーピンク7,960＝黒桃
# フック: ブラック31,840＝黒 ／ ブラウン3,980＋グレー3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',71640+15920),('ナノガラス脱毛パッド','黒桃',51740+7960),
 ('高見えレザーヘッドレストフック','黒',31840),('高見えレザーヘッドレストフック','茶灰',3980+3980)]
AD={'W固定スマホ車載ホルダー':33869,'カタログ全部（テスト）':8685,'ナノガラス脱毛パッド':72907,'ネックマッサージャー2':8954,
 'バランスケアスリッパ':8890,'伸縮ガラスクリーナー':39130,'姿勢サポートチェア':8826,'快適マジックインソール':35440,
 '携帯電動シェーバー':7660,'高見えレザーヘッドレストフック':18371,'4-in-1マルチクリーナー':6364}
ACCT=249096
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
