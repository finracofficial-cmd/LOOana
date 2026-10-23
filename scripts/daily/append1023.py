# -*- coding: utf-8 -*-
"""2026-10-23(金) をCSVへ追記。10/24 03時台に取得。広告費はキャンペーン合算（暫定）。
当日: 新商品 伸縮ワックス洗車ブラシ（8,000・13時台申請・審査後に配信）。ドアポケット 8,000→11,000（ユーザー実施・Meta直読で確認）。シーラーの8,000判定は未実施（12,000のまま）。
VIP特典の無料優先配送18件（12+6・gross 0円）は売上行に入れない。返品0。
広告なし商品: 形状記憶日傘1・優先配送1（自然購入）。"""
import csv
D='2026-10-23'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 'コードレスダブルミスト加湿器':4980,'高見えレザードアポケット':3980,'伸縮ワックス洗車ブラシ':4980,'形状記憶日傘':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 549210, 23043, 102, 148
VIP_GIFT_QTY, RETURNED_QTY = 18, 0
SALES=[('ナノガラス脱毛パッド',151240,1592),('伸縮ガラスクリーナー',87560,3383),('W固定スマホ車載ホルダー',51740,796),
 ('4-in-1マルチクリーナー',48860,3141),('快適マジックインソール',43780,2388),('高見えレザードアポケット',39800,3383),
 ('高見えレザーヘッドレストフック',35820,3184),('ポータブルヒートシーラー',35820,3184),('伸縮ワックス洗車ブラシ',24900,996),
 ('コードレスダブルミスト加湿器',9960,996),('ナノバブルシャワーヘッド',6980,0),('壁掛けディスペンサー',6980,0),
 ('形状記憶日傘',4980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト59,700＋セージ23,880＝白緑／マットブラック63,680＋ベイビーピンク3,980＝黒桃 ／ フック: ブラック35,820＝黒 ／ ディスペンサー: 3本（ブラック）6,980
VAR=[('ナノガラス脱毛パッド','白緑',59700+23880),('ナノガラス脱毛パッド','黒桃',63680+3980),
 ('高見えレザーヘッドレストフック','黒',35820),('壁掛けディスペンサー','3本',6980)]
VARP={'3本':6980,'2本':5980}
AD={'W固定スマホ車載ホルダー':36154,'カタログ全部（テスト）':8349,'コードレスダブルミスト加湿器':12922,'ディスペンサー':13257,
 'ナノガラス脱毛パッド':78265,'ナノバブルシャワーヘッド':6828,'ポータブルヒートシーラー':11900,'伸縮ガラスクリーナー':35194,
 '伸縮ワックス洗車ブラシ':4173,'快適マジックインソール':28739,'高見えレザードアポケット':10473,'高見えレザーヘッドレストフック':9636,'4-in-1マルチクリーナー':7751}
ACCT=sum(AD.values()); assert ACCT==263641, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES if n!='壁掛けディスペンサー')
qty=sum(g//PRICE[n] for n,g,_ in SALES if n!='壁掛けディスペンサー')+sum(g//VARP[v] for n,v,g in VAR if n=='壁掛けディスペンサー')
assert qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
