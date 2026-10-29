# -*- coding: utf-8 -*-
"""2026-10-29(木) をCSVへ追記。10/30 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定）。
当日: 08:46 クリーナー主力30,000→26,000・sabu 8,000→12,000／インソール３停止／08:55 2WAYシートボックス再開8,000→17:45停止／
ナノD（エラー回避用）12:50 32,000→25,000→13:00頃停止／ナノ旧D（BC検証用）13:00再稼働32,000→19:25停止。終日の最終 12セット・211,000円。
ナノ商品名を 08:00・17:20・翌00:08 に変更（「本日終了」→「30日間返金保証」→「在庫限りセール中」→「顧客満足度4.9⭐️」）。
VIP特典の無料優先配送13件（6+7・gross 0円）は売上行に入れない。返品 0。優先配送（有料）1件 790円。
広告なし商品: UV歯ブラシ除菌器1・5WAY腰掛けファン1・ロングニトリル家事手袋1（ブルー/キャラなし/L・unitCost 700）・ヘアドライタオル1（自然購入）。"""
import csv
D='2026-10-29'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '高見えレザーヘッドレストフック':3980,'UV歯ブラシ除菌器':8980,'5WAY腰掛けファン':4980,'ロングニトリル家事手袋':3980,'ヘアドライタオル':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 458690, 14930, 84, 119
VIP_GIFT_QTY, RETURNED_QTY = 13, 0
SALES=[('伸縮ガラスクリーナー',87560,2388),('ナノガラス脱毛パッド',83580,796),('伸縮ワックス洗車ブラシ',69720,2988),
 ('W固定スマホ車載ホルダー',55720,796),('ポータブルヒートシーラー',31840,796),('4-in-1マルチクリーナー',27920,0),
 ('快適マジックインソール',27860,2587),('高見えレザーヘッドレストフック',27860,3383),('姿勢サポートチェア',23920,1196),
 ('UV歯ブラシ除菌器',8980,0),('5WAY腰掛けファン',4980,0),('ロングニトリル家事手袋',3980,0),('ヘアドライタオル',3980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト39,800＋セージグリーン11,940＝白緑／マットブラック27,860＋ベイビーピンク3,980＝黒桃。フック: ブラック19,900＝黒／ブラウン7,960＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',39800+11940),('ナノガラス脱毛パッド','黒桃',27860+3980),
     ('高見えレザーヘッドレストフック','黒',19900),('高見えレザーヘッドレストフック','茶灰',7960)]
AD={'W固定スマホ車載ホルダー':30013,'カタログ全部（テスト）':9376,'ナノガラス脱毛パッド':78139,'ポータブルヒートシーラー':13428,
 '伸縮ガラスクリーナー':38885,'伸縮ワックス洗車ブラシ':20012,'姿勢サポートチェア':13396,'快適マジックインソール':29247,
 '高見えレザーヘッドレストフック':7691,'2WAYシートボックス':5669,'4-in-1マルチクリーナー':7331}
ACCT=sum(AD.values()); assert ACCT==253187, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==106 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
