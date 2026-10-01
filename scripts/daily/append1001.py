# -*- coding: utf-8 -*-
"""2026-10-01(木) をCSVへ追記。売上は日付変更直後(10/2 00:0x)取得。広告費は同時刻取得の暫定（キャンペーン合算292,810・アカウント292,858で差−48円=0.016%、取り込み途中）。次回確定値で上書き。"""
import csv
D='2026-10-01'
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'伸縮ガラスクリーナー':3980,'快適マジックインソール':3980,
 '高見えレザーヘッドレストフック':3980,'携帯電動シェーバー':4980,'UV歯ブラシ除菌器':8980,'姿勢サポートチェア':5980,
 'もちふわ肉球サンダル':3980,'バランスケアスリッパ':4980,'偏光・調光サングラス':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 712990, 24185, 141, 172
SALES=[('伸縮ガラスクリーナー',179100,8159),('ナノガラス脱毛パッド',175120,1592),('W固定スマホ車載ホルダー',87560,796),
 ('快適マジックインソール',67660,4179),('姿勢サポートチェア',47840,3887),('高見えレザーヘッドレストフック',47760,3184),
 ('もちふわ肉球サンダル',39800,2388),('UV歯ブラシ除菌器',26940,0),('バランスケアスリッパ',19920,0),
 ('携帯電動シェーバー',14940,0),('偏光・調光サングラス',3980,0),('優先配送',2370,0)]
# ナノガラス: ピュアホワイト131,340＋セージグリーン7,960＝白緑 ／ マットブラック31,840＋ベイビーピンク3,980＝黒桃
# フック: ブラック27,860＝黒 ／ ブラウン11,940＋グレー7,960＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',131340+7960),('ナノガラス脱毛パッド','黒桃',31840+3980),
 ('高見えレザーヘッドレストフック','黒',27860),('高見えレザーヘッドレストフック','茶灰',11940+7960)]
AD={'ナノガラス脱毛パッド':95258,'快適マジックインソール':38944,'W固定スマホ車載ホルダー':38043,'伸縮ガラスクリーナー':37776,
 '高見えレザーヘッドレストフック':23126,'もちふわ肉球サンダル':11242,'UV歯ブラシ除菌器':10689,'バランスケアスリッパ':10020,
 'カタログ全部（テスト）':9802,'姿勢サポートチェア':9320,'携帯電動シェーバー':6907,'電動眉シェーバー':1683}
ACCT=292810   # キャンペーン合算（暫定）。アカウント直取得292,858（差−48円・0.016%＝許容0.1%内）
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
assert sum(g//PRICE[n] for n,g,_ in SALES)==STORE_ITEMS   # 返品0
assert sum(AD.values())==ACCT, sum(AD.values())
assert abs(ACCT-292858)/292858 < 0.001
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
