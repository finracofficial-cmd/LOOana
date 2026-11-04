# -*- coding: utf-8 -*-
"""2026-11-04(水) をCSVへ追記。11/05 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1104/meta_camp_1103_1104_raw.txt）。
当日: 09:50 ドアクッション23,000→19,000／〜11:2x 洗車ブラシ20,000→23,000・4-in-1 10,000→8,000・車載A 14,000→10,000／B 16,000→19,000／
13:xx 毛玉再開8,000／13:44 加湿器8,000→13,000／14:4x ワイパー出稿8,000／17:28 ナノA 20,000→15,000／19:48 クリーナー20,000/14,000→18,000/12,000／
20:29 ドアクッション19,000→15,000・シーラー13,000→10,000 → 終日の最終 15セット・190,000円。
VIP特典の無料優先配送15件（8+7・gross 0円）は売上行に入れない。返品: 店全体0円（商品別はナノ−3,980円・商品名なしの行+3,980円で相殺。ナノ1個が返品数に入る）。有料の優先配送0件。
広告費ありで売上0: 毛玉 3,974円。フックは0円（停止中）。"""
import csv
D='2026-11-04'
PRICE={'伸縮ワックス洗車ブラシ':4980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'コードレスダブルミスト加湿器':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'マグネットドアクッション':3980,'姿勢サポートチェア':5980,
 '快適マジックインソール':3980,'ポータブルヒートシーラー':3980,'ワイド水切りワイパー':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 418140, 20162, 70, 107
VIP_GIFT_QTY, RETURNED_QTY = 15, 1
SALES=[('伸縮ワックス洗車ブラシ',79680,2988),('W固定スマホ車載ホルダー',71640,1592),('伸縮ガラスクリーナー',59700,3383),
 ('コードレスダブルミスト加湿器',44820,5229),('4-in-1マルチクリーナー',34900,1396),('ナノガラス脱毛パッド',31840,1791),
 ('マグネットドアクッション',31840,1791),('姿勢サポートチェア',23920,1196),('快適マジックインソール',19900,796),
 ('ポータブルヒートシーラー',11940,0),('ワイド水切りワイパー',7960,0)]
# ナノ: ピュアホワイト11,940＋セージグリーン7,960＝白緑／マットブラック7,960＋ベイビーピンク3,980＝黒桃
VAR=[('ナノガラス脱毛パッド','白緑',19900),('ナノガラス脱毛パッド','黒桃',11940)]
AD={}
for l in open('scripts/daily/o1104/meta_camp_1103_1104_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(70,18,14,8)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==186751, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==93 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
