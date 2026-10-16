# -*- coding: utf-8 -*-
"""2026-10-16(金) をCSVへ追記。10/17 02時台取得。広告費はキャンペーン合算235,731円（暫定）。
当日: プライム感謝祭 本番1日目。新商品ロングニトリル家事手袋 出稿（8,000円・13時台〜・消化4,039円・販売0）。シーラー16,000→12,000・かっさ停止・フック-sub停止（いずれもユーザー）。
VIP特典の無料優先配送17件（商品名2種 9+8・gross 0円）は売上行に入れない。有料の優先配送1件（790円）。返品0。"""
import csv
D='2026-10-16'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'4-in-1マルチクリーナー':6980,
 'W固定スマホ車載ホルダー':3980,'高見えレザーヘッドレストフック':3980,'ナノバブルシャワーヘッド':6980,
 'ポータブルヒートシーラー':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 455610, 19502, 85, 127
VIP_GIFT_QTY, RETURNED_QTY = 17, 0
SALES=[('ナノガラス脱毛パッド',119400,2388),('W固定スマホ車載ホルダー',83580,3184),('快適マジックインソール',71640,6368),
 ('伸縮ガラスクリーナー',67660,1592),('高見えレザーヘッドレストフック',35820,4179),('4-in-1マルチクリーナー',34900,0),
 ('ポータブルヒートシーラー',27860,1791),('ナノバブルシャワーヘッド',13960,0),('優先配送',790,0)]
# ナノガラス: ピュアホワイト55,720＋セージグリーン11,940＝白緑 ／ マットブラック43,780＋ベイビーピンク7,960＝黒桃
# フック: ブラック27,860＝黒 ／ ブラウン3,980＋グレー3,980＝茶灰（10/7以降は原価732円一律）
VAR=[('ナノガラス脱毛パッド','白緑',55720+11940),('ナノガラス脱毛パッド','黒桃',43780+7960),
 ('高見えレザーヘッドレストフック','黒',27860),('高見えレザーヘッドレストフック','茶灰',3980+3980)]
AD={'W固定スマホ車載ホルダー':35368,'むくみ取りかっさ':120,'カタログ全部（テスト）':8434,'ナノガラス脱毛パッド':79312,
 'ナノバブルシャワーヘッド':7606,'ポータブルヒートシーラー':11108,'ロングニトリル家事手袋':4039,'伸縮ガラスクリーナー':37169,
 '快適マジックインソール':33191,'高見えレザーヘッドレストフック':7700,'4-in-1マルチクリーナー':11684}
ACCT=235731
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
