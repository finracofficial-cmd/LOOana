# -*- coding: utf-8 -*-
"""2026-10-14(水) をCSVへ追記。10/15 00時台取得。広告費はキャンペーン合算260,607円（暫定）。
当日: 03時に チェア・スリッパ停止／フック11,000・インソール32,000・シーラー16,000／かっさ・サンダル再開（サンダルは昼前に再停止）。
昼に クリーナー主力24,000・sabu14,000／ナノ主力48,000・BC32,000／車載-sab再開(新CR B)・フック-sub新設8,000＋主力8,000／ナノバブル再開8,000。
VIP特典の無料優先配送16件（商品名2種 8+8・gross 0円）は売上行に入れない。返品1点（形状記憶日傘4,980円・A案で売上から引かない）。"""
import csv
D='2026-10-14'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 'ポータブルヒートシーラー':3980,'むくみ取りかっさ':3980,'高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,
 'ナノバブルシャワーヘッド':6980,'健康サンダル':4980,'バランスケアスリッパ':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 461720, 16915, 91, 129
VIP_GIFT_QTY, RETURNED_QTY = 16, 1
SALES=[('ナノガラス脱毛パッド',171140,4179),('快適マジックインソール',59700,4378),('伸縮ガラスクリーナー',55720,2587),
 ('W固定スマホ車載ホルダー',51740,796),('ポータブルヒートシーラー',47760,1592),('むくみ取りかっさ',27860,796),
 ('高見えレザーヘッドレストフック',23880,2587),('4-in-1マルチクリーナー',6980,0),('ナノバブルシャワーヘッド',6980,0),
 ('健康サンダル',4980,0),('バランスケアスリッパ',4980,0)]
# ナノガラス: ピュアホワイト79,600＋セージグリーン31,840＝白緑 ／ マットブラック51,740＋ベイビーピンク7,960＝黒桃
# フック: ブラック3,980＝黒 ／ グレー15,920＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',79600+31840),('ナノガラス脱毛パッド','黒桃',51740+7960),
 ('高見えレザーヘッドレストフック','黒',3980),('高見えレザーヘッドレストフック','茶灰',15920+3980)]
AD={'W固定スマホ車載ホルダー':34634,'むくみ取りかっさ':13585,'もちふわ肉球サンダル':5839,'カタログ全部（テスト）':8597,
 'ナノガラス脱毛パッド':78193,'ナノバブルシャワーヘッド':3453,'バランスケアスリッパ':545,'ポータブルヒートシーラー':18201,
 '伸縮ガラスクリーナー':37570,'姿勢サポートチェア':421,'快適マジックインソール':35061,'高見えレザーヘッドレストフック':14660,
 '4-in-1マルチクリーナー':9848}
ACCT=260607
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
