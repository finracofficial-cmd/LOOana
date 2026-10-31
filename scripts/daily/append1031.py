# -*- coding: utf-8 -*-
"""2026-10-31(土) をCSVへ追記。11/01 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: 商品名 第4版（00:30・ユーザー申告を正とする）／ナノA 30,000→20,000（02:28）／ナノ「かかと冬」8,000 新設（02:45）／健康サンダル再開8,000（02:59）→ 17:05停止／
マグネットドアクッション 8,000 新規（12:26）／インソール 20,000→16,000（17:05）／ふわとろ高密度ブランケット 8,000 新規（18:40）。
VIP特典の無料優先配送12件（8+4・gross 0円）は売上行に入れない。返品0件。有料の優先配送0件。
広告ありで初販売: マグネットドアクッション3（4個入り・unitCost 577）。広告なしで売れた商品: 姿勢サポートベルト1（ブラック/M・1,429）・携帯電動シェーバー1（ブラック・1,764）。
健康サンダル1（ピンク・1,162）は広告あり（5,033円・17時に停止）。ブランケットは販売0（広告1,837円）。"""
import csv
D='2026-10-31'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'マグネットドアクッション':3980,'姿勢サポートベルト':5980,'携帯電動シェーバー':4980,'健康サンダル':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 400200, 14784, 70, 102
VIP_GIFT_QTY, RETURNED_QTY = 12, 0
SALES=[('伸縮ガラスクリーナー',87560,3184),('伸縮ワックス洗車ブラシ',74700,5229),('W固定スマホ車載ホルダー',63680,796),
 ('4-in-1マルチクリーナー',48860,1396),('ポータブルヒートシーラー',39800,1592),('ナノガラス脱毛パッド',35820,796),
 ('マグネットドアクッション',11940,0),('高見えレザーヘッドレストフック',11940,1791),('姿勢サポートベルト',5980,0),
 ('姿勢サポートチェア',5980,0),('携帯電動シェーバー',4980,0),('健康サンダル',4980,0),('快適マジックインソール',3980,0)]
# ナノ: ピュアホワイト27,860＝白緑／マットブラック7,960＝黒桃。フック: グレー3,980＝茶灰／ブラック7,960＝黒
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',7960),
     ('高見えレザーヘッドレストフック','茶灰',3980),('高見えレザーヘッドレストフック','黒',7960)]
AD={'W固定スマホ車載ホルダー':32098,'ふわとろ高密度ブランケット':1837,'カタログ全部（テスト）':8543,'ナノガラス脱毛パッド':26054,
 'ポータブルヒートシーラー':16129,'マグネットドアクッション':3844,'伸縮ガラスクリーナー':36892,'伸縮ワックス洗車ブラシ':23240,
 '健康サンダル':5033,'姿勢サポートチェア':15492,'快適マジックインソール':17528,'高見えレザーヘッドレストフック':8105,'4-in-1マルチクリーナー':8679}
BANDS=(70,15,6,3)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==203474, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==90 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
