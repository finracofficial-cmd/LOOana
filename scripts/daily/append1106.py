# -*- coding: utf-8 -*-
"""2026-11-06(金) をCSVへ追記。11/07 02時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1106/meta_camp_1105_1106_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 00:20 加湿器16,000→12,000・ナノA 15,000→18,000・ワイパー12,000→15,000／00:22 シーラー10,000→8,000／
06:11 クリーナー主力16,000→19,000・sabu 12,000→15,000／07:33 加湿器12,000→15,000／09:15 洗車ブラシ23,000→15,000・4-in-1 8,000→11,000・車載A 10,000→12,000・B 19,000→15,000／
09:39 レインガード8,000→11,000／13:45 ワイパー15,000→18,000／14:2x 洗車ブラシ15,000→18,000 → 終日の最終 15セット・203,000円。
VIP特典の無料優先配送22件（14+8・gross 0円）は売上行に入れない。返品0件。有料の優先配送0件。
加湿器はShopifyの商品名が「コードレスパワーミスト加湿器」に変わっている（Product/15447824498930・同じ商品・売価4,980・原価1,686）。CSVはMetaのキャンペーン名と同じ「コードレスダブルミスト加湿器」で続ける。
広告なしで売れた商品: ネックマッサージャー1・ムダ毛シェーバー1・バランスケアスリッパ1。"""
import csv
D='2026-11-06'
PRICE={'伸縮ガラスクリーナー':3980,'伸縮ワックス洗車ブラシ':4980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'ナノガラス脱毛パッド':3980,
 'クリアビューレインガードフィルム':3980,'姿勢サポートチェア':5980,'4-in-1マルチクリーナー':6980,'マグネットドアクッション':3980,'コードレスダブルミスト加湿器':4980,
 'ネックマッサージャー':8980,'快適マジックインソール':3980,'ポータブルヒートシーラー':3980,'ムダ毛シェーバー':6980,'バランスケアスリッパ':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 530580, 20707, 98, 143
VIP_GIFT_QTY, RETURNED_QTY = 22, 0
SALES=[('伸縮ガラスクリーナー',127360,5771),('伸縮ワックス洗車ブラシ',64740,4980),('ワイド水切りワイパー',63680,796),('W固定スマホ車載ホルダー',47760,1592),
 ('ナノガラス脱毛パッド',47760,1592),('クリアビューレインガードフィルム',31840,1592),('姿勢サポートチェア',29900,1196),('4-in-1マルチクリーナー',27920,1396),
 ('マグネットドアクッション',27860,0),('コードレスダブルミスト加湿器',24900,996),('ネックマッサージャー',8980,0),('快適マジックインソール',7960,796),
 ('ポータブルヒートシーラー',7960,0),('ムダ毛シェーバー',6980,0),('バランスケアスリッパ',4980,0)]
# ナノ: ピュアホワイト27,860＋セージグリーン3,980＝白緑／マットブラック11,940＋ベイビーピンク3,980＝黒桃。ディスペンサーは販売0
VAR=[('ナノガラス脱毛パッド','白緑',31840),('ナノガラス脱毛パッド','黒桃',15920)]
AD={}
for l in open('scripts/daily/o1106/meta_camp_1105_1106_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(98,23,10,3)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==188509, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==121 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
