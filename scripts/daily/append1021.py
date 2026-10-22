# -*- coding: utf-8 -*-
"""2026-10-21(水) をCSVへ追記。10/22 10時台に取得（Shopify接続切れのため遅延）。広告費はキャンペーン合算（暫定）。
当日の予算変更: 朝に車載 -sab 10,000/主力28,000・クリーナー sabu 8,000/主力30,000・インソール新セット停止/主力32,000・4-in-1 8,000・加湿器一時停止→再開（2026-10-21b〜d・最終255,000）。
VIP特典の無料優先配送20件（12+8・gross 0円）は売上行に入れない。返品0。広告なし商品: オートソープディスペンサー1・スマートノーズEMS美顔器1・偏光・調光サングラス1・優先配送1（自然購入）。"""
import csv
D='2026-10-21'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 '壁掛けディスペンサー':6980,'コードレスダブルミスト加湿器':4980,'オートソープディスペンサー':7980,'スマートノーズEMS美顔器':5980,
 '偏光・調光サングラス':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 571110, 22090, 104, 155
VIP_GIFT_QTY, RETURNED_QTY = 20, 0
SALES=[('ナノガラス脱毛パッド',218900,6368),('伸縮ガラスクリーナー',91540,3980),('W固定スマホ車載ホルダー',71640,2388),
 ('快適マジックインソール',67660,6766),('ナノバブルシャワーヘッド',27920,0),('壁掛けディスペンサー',20940,0),
 ('コードレスダブルミスト加湿器',19920,996),('4-in-1マルチクリーナー',13960,0),('高見えレザーヘッドレストフック',11940,796),
 ('オートソープディスペンサー',7980,0),('ポータブルヒートシーラー',7960,796),('スマートノーズEMS美顔器',5980,0),
 ('偏光・調光サングラス',3980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト83,580＋セージ51,740＝白緑／マットブラック71,640＋ベイビーピンク11,940＝黒桃 ／ フック: ブラック11,940＝黒 ／ ディスペンサー: 3本×3（透明・シルバー・ブラック）
VAR=[('ナノガラス脱毛パッド','白緑',83580+51740),('ナノガラス脱毛パッド','黒桃',71640+11940),
 ('高見えレザーヘッドレストフック','黒',11940),('壁掛けディスペンサー','3本',20940)]
AD={'W固定スマホ車載ホルダー':36059,'カタログ全部（テスト）':9823,'コードレスダブルミスト加湿器':8749,'ディスペンサー':8360,
 'ナノガラス脱毛パッド':77836,'ナノバブルシャワーヘッド':7371,'ポータブルヒートシーラー':11223,'伸縮ガラスクリーナー':34221,
 '快適マジックインソール':32091,'高見えレザーヘッドレストフック':9898,'4-in-1マルチクリーナー':7514}
ACCT=sum(AD.values()); assert ACCT==243145, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY
for n in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック','壁掛けディスペンサー'):
    assert sum(a for m,a,_ in SALES if m==n)==sum(a for m,_,a in VAR if m==n), n
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
