# -*- coding: utf-8 -*-
"""2026-10-30(金) をCSVへ追記。10/31 01時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: ナノの商品名を 00:08 に第3版（「在庫限りセール中⏰…顧客満足度4.9⭐️」）→ 15:06 に元の商品名へ戻す（Shopify直読）。
21:23 ナノA 48,000→30,000（Meta直読）。終日の最終 12セット・190,000円。
VIP特典の無料優先配送21件（17+4・gross 0円）は売上行に入れない。返品1件（5WAY腰掛けファン 4,980円・A案で売上から引かない）。優先配送（有料）1件 790円。
広告なし商品: 1秒折り畳みチェア3（ブラック2・レインボーレッド1・全色unitCost 1,455）。"""
import csv
D='2026-10-30'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'1秒折り畳みチェア':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 479610, 33844, 72, 130
VIP_GIFT_QTY, RETURNED_QTY = 21, 1
SALES=[('伸縮ワックス洗車ブラシ',104580,7221),('伸縮ガラスクリーナー',95520,6965),('W固定スマホ車載ホルダー',59700,3383),
 ('ポータブルヒートシーラー',51740,4378),('快適マジックインソール',47760,6169),('ナノガラス脱毛パッド',43780,796),
 ('姿勢サポートチェア',35880,2691),('4-in-1マルチクリーナー',20940,0),('1秒折り畳みチェア',14940,2241),
 ('高見えレザーヘッドレストフック',3980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト15,920＋セージグリーン3,980＝白緑／マットブラック23,880＝黒桃。フック: ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',15920+3980),('ナノガラス脱毛パッド','黒桃',23880),
     ('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'W固定スマホ車載ホルダー':30008,'カタログ全部（テスト）':9967,'ナノガラス脱毛パッド':39175,'ポータブルヒートシーラー':14610,
 '伸縮ガラスクリーナー':36902,'伸縮ワックス洗車ブラシ':22293,'姿勢サポートチェア':13785,'快適マジックインソール':21644,
 '高見えレザーヘッドレストフック':8481,'4-in-1マルチクリーナー':8564}
BANDS=(72,25,17,12)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==205429, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==110 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for n in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック'):
    assert sum(a for m,a,_ in SALES if m==n)==sum(a for m,_,a in VAR if m==n), n
assert BANDS[0]==STORE_ORDERS
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
with open('data/daily/daily_order_bands.csv','a',newline='\n') as f:
    f.write(','.join([D]+[str(x) for x in BANDS])+'\n')
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
