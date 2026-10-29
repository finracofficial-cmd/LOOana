# -*- coding: utf-8 -*-
"""2026-10-28(水) をCSVへ追記。10/30 00時台に取得（10/29の定例を作らなかったため2日分をまとめて追記）。広告費はキャンペーン合算（data_query fresh・ほぼ確定）。
当日: 03:10 加湿器停止・03:11 姿勢サポートチェア再開(9,000)・10:37 インソール主力32,000→28,000＋新セット「快適マジックインソール３」8,000。終日 14セット・251,000円。
VIP特典の無料優先配送11件（5+6・gross 0円）は売上行に入れない。返品 0。優先配送（有料）0件。
広告なし商品: 完全遮光・形状記憶 UV日傘 1（自然購入）。"""
import csv
D='2026-10-28'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'姿勢サポートチェア':5980,
 '完全遮光・形状記憶':4980,'高見えレザーヘッドレストフック':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 429980, 15725, 83, 112
VIP_GIFT_QTY, RETURNED_QTY = 11, 0
SALES=[('ナノガラス脱毛パッド',131340,2388),('伸縮ワックス洗車ブラシ',69720,1992),('W固定スマホ車載ホルダー',63680,3383),
 ('快適マジックインソール',55720,5174),('伸縮ガラスクリーナー',47760,796),('姿勢サポートチェア',29900,1196),
 ('ポータブルヒートシーラー',15920,796),('4-in-1マルチクリーナー',6980,0),('完全遮光・形状記憶',4980,0),('高見えレザーヘッドレストフック',3980,0)]
# ナノ: ピュアホワイト63,680＋セージグリーン19,900＝白緑／マットブラック35,820＋ベイビーピンク11,940＝黒桃。フック: ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',63680+19900),('ナノガラス脱毛パッド','黒桃',35820+11940),('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'W固定スマホ車載ホルダー':26179,'カタログ全部（テスト）':7813,'コードレスダブルミスト加湿器':268,'ナノガラス脱毛パッド':69874,
 'ポータブルヒートシーラー':13943,'伸縮ガラスクリーナー':34508,'伸縮ワックス洗車ブラシ':17105,'姿勢サポートチェア':14081,
 '快適マジックインソール':33986,'高見えレザーヘッドレストフック':7577,'4-in-1マルチクリーナー':7341}
ACCT=sum(AD.values()); assert ACCT==232675, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==101 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
