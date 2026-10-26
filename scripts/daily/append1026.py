# -*- coding: utf-8 -*-
"""2026-10-26(月) をCSVへ追記。10/27 00時台に取得。広告費はキャンペーン合算（暫定）。
当日: 00:15-19 ユーザーが 車載A 22,000→14,000・フック 10,000→8,000・洗車ブラシ 15,000→18,000・シーラー 12,000→15,000・ナノバブル停止、00:31 スリッパ v2 再開（7,000）、15:16 ナノ新BCセットの B・C 停止（Dのみ）。
夜20時台以降に購入率が急落（20〜22時台 購入4件・60日最低6件）。原因未特定（decisions.md 参照）。
VIP特典の無料優先配送19件（10+9・gross 0円）は売上行に入れない。返品 0。
広告なし商品: ネックマッサージャー1・偏光・調光サングラス1（自然購入）。"""
import csv
D='2026-10-26'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,
 'コードレスダブルミスト加湿器':4980,'伸縮ワックス洗車ブラシ':4980,'ネックマッサージャー':8980,'バランスケアスリッパ':4980,'偏光・調光サングラス':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 492640, 19304, 95, 137
VIP_GIFT_QTY, RETURNED_QTY = 19, 0
SALES=[('ナノガラス脱毛パッド',59700+47760+31840+3980,796+796+398+398),('W固定スマホ車載ホルダー',79600,6766),
 ('伸縮ガラスクリーナー',43780+23880+15920,2985+796+1194),('快適マジックインソール',11940+7960*3+3980*4,796+398+398),
 ('伸縮ワックス洗車ブラシ',34860+9960,996),('ポータブルヒートシーラー',19900+7960,0),('高見えレザーヘッドレストフック',19900,2587),
 ('4-in-1マルチクリーナー',13960,0),('バランスケアスリッパ',4980+4980,0),('ネックマッサージャー',8980,0),
 ('コードレスダブルミスト加湿器',4980,0),('偏光・調光サングラス',3980,0)]
# ナノ: ピュアホワイト59,700＋セージ31,840＝白緑／マットブラック47,760＋ベイビーピンク3,980＝黒桃 ／ フック: ブラウン19,900＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',59700+31840),('ナノガラス脱毛パッド','黒桃',47760+3980),
 ('高見えレザーヘッドレストフック','茶灰',19900)]
AD={'W固定スマホ車載ホルダー':32304,'カタログ全部（テスト）':8735,'コードレスダブルミスト加湿器':8239,
 'ナノガラス脱毛パッド':79159,'ナノバブルシャワーヘッド':134,'バランスケアスリッパ':9681,'ポータブルヒートシーラー':16820,
 '伸縮ガラスクリーナー':38171,'伸縮ワックス洗車ブラシ':18854,'快適マジックインソール':28484,'高見えレザーヘッドレストフック':8451,'4-in-1マルチクリーナー':8466}
ACCT=sum(AD.values()); assert ACCT==257498, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==118 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
