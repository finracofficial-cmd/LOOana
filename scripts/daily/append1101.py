# -*- coding: utf-8 -*-
"""2026-11-01(日) をCSVへ追記。11/02 04時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: 00:43 ナノA 20,000→16,000／00:51 マグネットドアクッション 8,000→12,000／01時台 インソール主力16,000→13,000＋新セット「快適マジックインソール4」8,000・
フック主力8,000→6,000＋新セット「高見えレザーヘッドレストフック２」6,000／09:07 ドアクッション12,000→15,000／21:20頃 ふわとろ高密度ブランケット停止 → 終日の最終 16セット・204,000円。
VIP特典の無料優先配送26件（17+9・gross 0円）は売上行に入れない。返品0件。有料の優先配送1件 790円。
広告なしで売れた商品: 2WAYシートボックス1（4,980）・携帯電動シェーバー1（ブラック・1,764）・壁掛けディスペンサー1（3本セット）。ブランケットは販売0（広告8,523円）。"""
import csv
D='2026-11-01'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'マグネットドアクッション':3980,'携帯電動シェーバー':4980,'2WAYシートボックス':4980,'壁掛けディスペンサー':6980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 657750, 31352, 112, 179
VIP_GIFT_QTY, RETURNED_QTY = 26, 0
SALES=[('伸縮ガラスクリーナー',159200,11343),('W固定スマホ車載ホルダー',99500,2388),('マグネットドアクッション',63680,2388),
 ('伸縮ワックス洗車ブラシ',59760,996),('姿勢サポートチェア',59800,5083),('ポータブルヒートシーラー',47760,2587),
 ('ナノガラス脱毛パッド',43780,796),('高見えレザーヘッドレストフック',39800,3184),('4-in-1マルチクリーナー',34900,0),
 ('快適マジックインソール',31840,2587),('壁掛けディスペンサー',6980,0),('2WAYシートボックス',4980,0),('携帯電動シェーバー',4980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト7,960＋セージグリーン7,960＝白緑／マットブラック27,860＝黒桃。フック: ブラウン7,960＝茶灰／ブラック31,840＝黒。ディスペンサー: 3本セット6,980
VAR=[('ナノガラス脱毛パッド','白緑',15920),('ナノガラス脱毛パッド','黒桃',27860),
     ('高見えレザーヘッドレストフック','茶灰',7960),('高見えレザーヘッドレストフック','黒',31840),
     ('壁掛けディスペンサー','3本',6980)]
AD={'W固定スマホ車載ホルダー':33483,'ふわとろ高密度ブランケット':8523,'カタログ全部（テスト）':9606,'ナノガラス脱毛パッド':26280,
 'ポータブルヒートシーラー':16028,'マグネットドアクッション':16416,'伸縮ガラスクリーナー':40490,'伸縮ワックス洗車ブラシ':26290,
 '姿勢サポートチェア':10038,'快適マジックインソール':22815,'高見えレザーヘッドレストフック':12155,'4-in-1マルチクリーナー':7652}
BANDS=(112,27,11,9)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==229776, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==153 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for n in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック','壁掛けディスペンサー'):
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
