# -*- coding: utf-8 -*-
"""2026-10-25(日) をCSVへ追記。10/26 00時台に取得。広告費はキャンペーン合算（暫定）。
当日: 洗車ブラシ 8,000→11,000→15,000・ドアポケット 10,000→8,000→停止・加湿器 10,000→8,000（ユーザー）。
ナノ「BC検証用」が17:17・19:16・20時台に再停止 → 21:23 新セット「エラ-回避用」作成・旧BC 21:24 停止・21:33 初回配信。
VIP特典の無料優先配送25件（15+10・gross 0円）は売上行に入れない。返品 0。
広告なし商品: 電動温熱カッサ1・完全遮光日傘1・優先配送2（自然購入）。"""
import csv
D='2026-10-25'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 'コードレスダブルミスト加湿器':4980,'伸縮ワックス洗車ブラシ':4980,'電動温熱カッサ':6980,'完全遮光・形状記憶':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 664460, 24881, 125, 183
VIP_GIFT_QTY, RETURNED_QTY = 25, 0
SALES=[('ナノガラス脱毛パッド',179100,2388),('伸縮ガラスクリーナー',119400,4776),('W固定スマホ車載ホルダー',91540,3184),
 ('伸縮ワックス洗車ブラシ',74700,5976),('ポータブルヒートシーラー',55720,4378),('快適マジックインソール',39800,1592),
 ('4-in-1マルチクリーナー',27920,0),('コードレスダブルミスト加湿器',24900,0),('高見えレザーヘッドレストフック',23880,2587),
 ('ナノバブルシャワーヘッド',13960,0),('電動温熱カッサ',6980,0),('完全遮光・形状記憶',4980,0),('優先配送',1580,0)]
# ナノ: ピュアホワイト87,560＋セージ19,900＝白緑／マットブラック55,720＋ベイビーピンク15,920＝黒桃 ／ フック: ブラック15,920＝黒・グレー3,980＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',87560+19900),('ナノガラス脱毛パッド','黒桃',55720+15920),
 ('高見えレザーヘッドレストフック','黒',15920),('高見えレザーヘッドレストフック','茶灰',3980+3980)]
AD={'W固定スマホ車載ホルダー':44712,'カタログ全部（テスト）':10302,'コードレスダブルミスト加湿器':9930,
 'ナノガラス脱毛パッド':95350,'ナノバブルシャワーヘッド':9840,'ポータブルヒートシーラー':13583,'伸縮ガラスクリーナー':42845,
 '伸縮ワックス洗車ブラシ':14460,'快適マジックインソール':35598,'高見えレザードアポケット':7183,'高見えレザーヘッドレストフック':11595,'4-in-1マルチクリーナー':8453}
ACCT=sum(AD.values()); assert ACCT==303851, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==158 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
