# -*- coding: utf-8 -*-
"""2026-11-02(月) をCSVへ追記。11/03 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: 09:07頃 ドアクッション 15,000→19,000／20:49 クリーナー主力 26,000→22,000・sabu 12,000→16,000 → 終日の最終 16セット・208,000円。
VIP特典の無料優先配送10件（7+3・gross 0円）は売上行に入れない。返品0件。有料の優先配送1件 790円。
広告なしで売れた商品: 2WAYシートボックス1（1,547）。"""
import csv
D='2026-11-02'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'マグネットドアクッション':3980,'2WAYシートボックス':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 378030, 9154, 75, 99
VIP_GIFT_QTY, RETURNED_QTY = 10, 0
SALES=[('W固定スマホ車載ホルダー',67660,3383),('伸縮ガラスクリーナー',59700,796),('ナノガラス脱毛パッド',55720,796),
 ('マグネットドアクッション',47760,1592),('伸縮ワックス洗車ブラシ',44820,0),('4-in-1マルチクリーナー',34900,0),
 ('快適マジックインソール',23880,796),('ポータブルヒートシーラー',15920,0),('高見えレザーヘッドレストフック',15920,1791),
 ('姿勢サポートチェア',5980,0),('2WAYシートボックス',4980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト19,900＋セージグリーン7,960＝白緑／マットブラック15,920＋ベイビーピンク11,940＝黒桃。フック: グレー11,940＝茶灰／ブラック3,980＝黒
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',27860),
     ('高見えレザーヘッドレストフック','茶灰',11940),('高見えレザーヘッドレストフック','黒',3980)]
AD={'W固定スマホ車載ホルダー':30277,'カタログ全部（テスト）':9698,'ナノガラス脱毛パッド':24693,'ポータブルヒートシーラー':16712,
 'マグネットドアクッション':20727,'伸縮ガラスクリーナー':39505,'伸縮ワックス洗車ブラシ':22207,'姿勢サポートチェア':9290,
 '快適マジックインソール':21204,'高見えレザーヘッドレストフック':12664,'4-in-1マルチクリーナー':9111}
BANDS=(75,12,2,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==216088, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==89 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
