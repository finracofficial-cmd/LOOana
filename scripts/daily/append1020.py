# -*- coding: utf-8 -*-
"""2026-10-20(火) をCSVへ追記。10/21 00時台に取得。広告費はキャンペーン合算（暫定）。
当日: プライム感謝祭明け初日。予算変更: フック8,000→10,000（10/20b）・加湿器10,000新規（10/20c）→ 合計261,000。
0〜13時にInstagram経由だけカート率が落ちた日（詳細は decisions.md 10/20）。実売369,069円は8/1以降81日で最低。
VIP特典の無料優先配送10件（5+5・gross 0円）は売上行に入れない。返品0。広告なし商品: 姿勢サポートチェア1・完全遮光日傘1（自然購入）。"""
import csv
D='2026-10-20'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'ナノバブルシャワーヘッド':6980,
 '姿勢サポートチェア':5980,'完全遮光・形状記憶':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 379220, 10151, 76, 99
VIP_GIFT_QTY, RETURNED_QTY = 10, 0
SALES=[('ナノガラス脱毛パッド',135320,796),('W固定スマホ車載ホルダー',75620,2388),('伸縮ガラスクリーナー',35820,796),
 ('快適マジックインソール',31840,2388),('ポータブルヒートシーラー',31840,2587),('ナノバブルシャワーヘッド',20940,0),
 ('壁掛けディスペンサー',18940,1196),('4-in-1マルチクリーナー',13960,0),('姿勢サポートチェア',5980,0),
 ('完全遮光・形状記憶',4980,0),('高見えレザーヘッドレストフック',3980,0)]
# ナノ: ピュアホワイト83,580＋セージ11,940＝白緑／マットブラック35,820＋ベイビーピンク3,980＝黒桃 ／ フック: グレー3,980＝茶灰 ／ ディスペンサー: シルバー2本11,960（5,980×2）・ブラック3本6,980
VAR=[('ナノガラス脱毛パッド','白緑',83580+11940),('ナノガラス脱毛パッド','黒桃',35820+3980),
 ('高見えレザーヘッドレストフック','茶灰',3980),
 ('壁掛けディスペンサー','2本',11960),('壁掛けディスペンサー','3本',6980)]
VARP={'2本':5980,'3本':6980}
AD={'W固定スマホ車載ホルダー':38659,'カタログ全部（テスト）':8441,'コードレスダブルミスト加湿器':4030,'ディスペンサー':8210,
 'ナノガラス脱毛パッド':77448,'ナノバブルシャワーヘッド':7944,'ポータブルヒートシーラー':11237,'伸縮ガラスクリーナー':36454,
 '快適マジックインソール':36241,'高見えレザーヘッドレストフック':10154,'4-in-1マルチクリーナー':8889}
ACCT=sum(AD.values()); assert ACCT==247707, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES if n!='壁掛けディスペンサー')
qty=sum(g//PRICE[n] for n,g,_ in SALES if n!='壁掛けディスペンサー')
for n,v,g in VAR:
    if n=='壁掛けディスペンサー': assert g%VARP[v]==0; qty+=g//VARP[v]
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
