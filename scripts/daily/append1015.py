# -*- coding: utf-8 -*-
"""2026-10-15(木) をCSVへ追記。10/16 00時台取得。広告費はキャンペーン合算240,777円（暫定）。
当日: 9時台に新商品ハイウエストシェイプパンツ出稿（8,000円）→ 当日中にキャンペーン停止（Meta直読でPAUSED・消化4,913円・購入0）。
VIP特典の無料優先配送19件（商品名2種 10+9・gross 0円）は売上行に入れない。返品0。"""
import csv
D='2026-10-15'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'4-in-1マルチクリーナー':6980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'ナノバブルシャワーヘッド':6980,'むくみ取りかっさ':3980,
 'ポータブルヒートシーラー':3980,'偏光・調光サングラス':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 534480, 19903, 100, 145
VIP_GIFT_QTY, RETURNED_QTY = 19, 0
SALES=[('ナノガラス脱毛パッド',163180,2388),('快適マジックインソール',99500,8756),('伸縮ガラスクリーナー',91540,3184),
 ('4-in-1マルチクリーナー',55840,1396),('W固定スマホ車載ホルダー',47760,1592),('高見えレザーヘッドレストフック',27860,2587),
 ('ナノバブルシャワーヘッド',20940,0),('むくみ取りかっさ',11940,0),('ポータブルヒートシーラー',11940,0),('偏光・調光サングラス',3980,0)]
# ナノガラス: ピュアホワイト67,660＋セージグリーン15,920＝白緑 ／ マットブラック75,620＋ベイビーピンク3,980＝黒桃
# フック: ブラック23,880＝黒 ／ グレー3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',67660+15920),('ナノガラス脱毛パッド','黒桃',75620+3980),
 ('高見えレザーヘッドレストフック','黒',23880),('高見えレザーヘッドレストフック','茶灰',3980)]
AD={'W固定スマホ車載ホルダー':36096,'むくみ取りかっさ':12075,'カタログ全部（テスト）':7940,'ナノガラス脱毛パッド':74190,
 'ナノバブルシャワーヘッド':6365,'ハイウエストシェイプパンツ':4913,'ポータブルヒートシーラー':12727,'伸縮ガラスクリーナー':35432,
 '快適マジックインソール':27079,'高見えレザーヘッドレストフック':14913,'4-in-1マルチクリーナー':9047}
ACCT=240777
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
