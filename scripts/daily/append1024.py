# -*- coding: utf-8 -*-
"""2026-10-24(土) をCSVへ追記。10/25 00時台に取得。広告費はキャンペーン合算（暫定）。
当日: 朝ディスペンサー停止（326円）・車載 A 28,000→22,000／B 10,000→16,000（ユーザー）。ナノ「BC検証用」の広告3本が Meta の「信頼できる広告主」確認で約9時〜16時台に停止→ユーザーが再開。
VIP特典の無料優先配送20件（13+7・gross 0円）は売上行に入れない。返品: 車載2個（7,164円・A案で売上から控除しない）。
広告なし商品: むくみ取りかっさ2・2WAYシートボックス1（自然購入）。"""
import csv
D='2026-10-24'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 'コードレスダブルミスト加湿器':4980,'伸縮ワックス洗車ブラシ':4980,'むくみ取りかっさ':3980,'2WAYシートボックス':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 542400, 21299, 105, 148
VIP_GIFT_QTY, RETURNED_QTY = 20, 2
SALES=[('ナノガラス脱毛パッド',139300,2388),('快適マジックインソール',91540,7363),('W固定スマホ車載ホルダー',83580,1592),
 ('伸縮ガラスクリーナー',71640,4184),('高見えレザーヘッドレストフック',31840,2388),('ポータブルヒートシーラー',31840,1592),
 ('ナノバブルシャワーヘッド',27920,0),('コードレスダブルミスト加湿器',24900,996),('伸縮ワックス洗車ブラシ',19920,0),
 ('むくみ取りかっさ',7960,796),('4-in-1マルチクリーナー',6980,0),('2WAYシートボックス',4980,0)]
# ナノ: ピュアホワイト55,720＋セージ23,880＝白緑／マットブラック55,720＋ベイビーピンク3,980＝黒桃 ／ フック: ブラック27,860＝黒・グレー3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',55720+23880),('ナノガラス脱毛パッド','黒桃',55720+3980),
 ('高見えレザーヘッドレストフック','黒',27860),('高見えレザーヘッドレストフック','茶灰',3980)]
VARP={'3本':6980,'2本':5980}
AD={'W固定スマホ車載ホルダー':37593,'カタログ全部（テスト）':7968,'コードレスダブルミスト加湿器':12301,'ディスペンサー':326,
 'ナノガラス脱毛パッド':79163,'ナノバブルシャワーヘッド':6834,'ポータブルヒートシーラー':13468,'伸縮ガラスクリーナー':40473,
 '伸縮ワックス洗車ブラシ':6951,'快適マジックインソール':30916,'高見えレザードアポケット':9923,'高見えレザーヘッドレストフック':8801,'4-in-1マルチクリーナー':8099}
ACCT=sum(AD.values()); assert ACCT==262816, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES if n!='壁掛けディスペンサー')
qty=sum(g//PRICE[n] for n,g,_ in SALES if n!='壁掛けディスペンサー')+sum(g//VARP[v] for n,v,g in VAR if n=='壁掛けディスペンサー')
assert qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
