# -*- coding: utf-8 -*-
"""2026-10-27(火) をCSVへ追記。10/28 02時台に取得。広告費はキャンペーン合算（暫定）。
当日: 00:07 スリッパ停止（13セット・246,000円）。予算変更なし。インソール新素材は未投入（10/27は広告A 1本のみ）。
朝0〜9時台はMetaの配信が先週比−30%で売上が出遅れ、10時台以降は平常。20〜22時台は購入16件で前夜（4件）の落ち込みは再発せず。
VIP特典の無料優先配送13件（9+4・gross 0円）は売上行に入れない。返品 0。優先配送（有料）2件 1,580円（790円×2）。
広告なし商品: 携帯電動シェーバー1（自然購入）。フック・加湿器は広告費あり（7,548・8,263）で売上0。"""
import csv
D='2026-10-27'
PRICE={'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,
 '4-in-1マルチクリーナー':6980,'ポータブルヒートシーラー':3980,'伸縮ワックス洗車ブラシ':4980,'携帯電動シェーバー':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 463380, 13135, 94, 125
VIP_GIFT_QTY, RETURNED_QTY = 13, 0
SALES=[('ナノガラス脱毛パッド',143280,1592),('快適マジックインソール',67660,5771),('W固定スマホ車載ホルダー',67660,796),
 ('伸縮ガラスクリーナー',63680,3184),('伸縮ワックス洗車ブラシ',54780,996),('ポータブルヒートシーラー',31840,796),
 ('4-in-1マルチクリーナー',27920,0),('携帯電動シェーバー',4980,0),('優先配送',1580,0)]
# ナノ: ピュアホワイト59,700＋セージグリーン31,840＝白緑／マットブラック43,780＋ベイビーピンク7,960＝黒桃。フックは販売0
VAR=[('ナノガラス脱毛パッド','白緑',59700+31840),('ナノガラス脱毛パッド','黒桃',43780+7960)]
AD={'W固定スマホ車載ホルダー':28933,'カタログ全部（テスト）':7870,'コードレスダブルミスト加湿器':8263,
 'ナノガラス脱毛パッド':80407,'バランスケアスリッパ':89,'ポータブルヒートシーラー':14599,'伸縮ガラスクリーナー':33062,
 '伸縮ワックス洗車ブラシ':14759,'快適マジックインソール':32337,'高見えレザーヘッドレストフック':7548,'4-in-1マルチクリーナー':7096}
ACCT=sum(AD.values()); assert ACCT==234963, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==112 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
