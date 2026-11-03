# -*- coding: utf-8 -*-
"""2026-11-03(火・文化の日) をCSVへ追記。11/04 06時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: 11:30頃 ファスナー修理キット 8,000新規／13:30頃 フック停止／14:00頃 毛玉クリーナー 8,000新規／21時頃 ファスナー・毛玉 停止、ドアクッション 19,000→23,000／
23時頃 かかと冬停止・ナノA 16,000→20,000・加湿器 8,000再開 → 終日の最終 13セット・189,000円。
VIP特典の無料優先配送13件（7+6・gross 0円）は売上行に入れない。返品0件。有料の優先配送1件 790円。
広告なしで売れた商品: 高見えレザードアポケット1（666）。"""
import csv
D='2026-11-03'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 'マグネットドアクッション':3980,'ファスナー修理キット':3980,'高見えレザードアポケット':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 450670, 13140, 88, 120
VIP_GIFT_QTY, RETURNED_QTY = 13, 0
SALES=[('伸縮ガラスクリーナー',103480,3184),('マグネットドアクッション',71640,1592),('伸縮ワックス洗車ブラシ',59760,1992),
 ('W固定スマホ車載ホルダー',55720,0),('ナノガラス脱毛パッド',51740,0),('快適マジックインソール',39800,3184),
 ('姿勢サポートチェア',29900,2392),('ポータブルヒートシーラー',15920,796),('4-in-1マルチクリーナー',13960,0),
 ('ファスナー修理キット',3980,0),('高見えレザードアポケット',3980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト15,920＋セージグリーン3,980＝白緑／マットブラック19,900＋ベイビーピンク11,940＝黒桃。フックは販売0
VAR=[('ナノガラス脱毛パッド','白緑',19900),('ナノガラス脱毛パッド','黒桃',31840)]
AD={'W固定スマホ車載ホルダー':30776,'カタログ全部（テスト）':9700,'コードレスダブルミスト加湿器':815,'コードレス毛玉クリーナー':3783,
 'ナノガラス脱毛パッド':24522,'ファスナー修理キット':4476,'ポータブルヒートシーラー':12901,'マグネットドアクッション':22160,
 '伸縮ガラスクリーナー':39956,'伸縮ワックス洗車ブラシ':20901,'姿勢サポートチェア':9714,'快適マジックインソール':15318,
 '高見えレザーヘッドレストフック':6801,'4-in-1マルチクリーナー':10691}
BANDS=(88,18,5,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==212514, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==107 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
assert sum(a for m,a,_ in SALES if m=='ナノガラス脱毛パッド')==sum(a for m,_,a in VAR if m=='ナノガラス脱毛パッド')
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
