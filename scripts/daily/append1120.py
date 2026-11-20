# -*- coding: utf-8 -*-
"""2026-11-20(金) をCSVへ追記。11/21 01時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1120/meta_camp_1119_1120_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認。budget-snapshots 2026-11-20a）: 00時台 フック v5 8,000→12,000・ノーズ v2 16,000→12,000・シェーバー v2 キャンペーン停止。日中の変更なし（11/21 01時台の直読で 178,600 のまま）。
VIP特典の無料優先配送11件（gross 0円）は売上行に入れない。有料の優先配送なし。返品なし。
広告費ありで売上0: カタログ全部（テスト）・携帯電動シェーバー v2（43円・00時台の停止前）。
広告なしで売れた商品: ファスナー修理キット 1（フックと同じ注文 #32395）。
バリエーション別原価: ナノ 白緑（ピュアホワイト5・セージグリーン2）／黒桃（マットブラック3）・フック 黒（ブラック3）／茶灰（ブラウン1）。
充電式ダブルミスト卓上加湿器は初めての販売（ホワイト1・ベージュ1。原価 1,954 は 11/19 に確認した値）。"""
import csv, json, re, collections
D='2026-11-20'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'スマートノーズEMS美顔器':6980,'360°マルチクリップ車載スマホホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'充電式ダブルミスト卓上加湿器':5980,'ファスナー修理キット':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 346400, 8955, 67, 91
VIP_GIFT_QTY, RETURNED_QTY = 11, 0
SALES=[('伸縮ガラスクリーナー',91540,3383),('W固定スマホ車載ホルダー',43780,796),('ナノガラス脱毛パッド',39800,796),('快適マジックインソール',31840,1592),
 ('スマートノーズEMS美顔器',27920,0),('4-in-1マルチクリーナー',27920,0),('ワイド水切りワイパー',27860,796),('高見えレザーヘッドレストフック',15920,796),
 ('充電式ダブルミスト卓上加湿器',11960,0),('360°マルチクリップ車載スマホホルダー',11940,796),('マグネットドアクッション',11940,0),('ファスナー修理キット',3980,0)]
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',11940),('高見えレザーヘッドレストフック','黒',11940),('高見えレザーヘッドレストフック','茶灰',3980)]
O='scripts/daily/o1120/'
_raw=json.load(open(O+'sales_1120_raw.json'))['rows']
_rs={t:(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1120_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1120_raw.json'))['rows']:
    if int(g): _var[t][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':19900,'マットブラック':11940,'セージグリーン':7960}, _var['ナノガラス脱毛パッド']
assert _var['高見えレザーヘッドレストフック']=={'ブラック':11940,'ブラウン':3980}, _var['高見えレザーヘッドレストフック']
assert _var['充電式ダブルミスト卓上加湿器']=={'ホワイト':5980,'ベージュ':5980}
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1119_1120_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1120_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(67,12,2,2), BANDS
ACCT=sum(AD.values()); assert ACCT==167012, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==80 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for p in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック'):
    assert sum(a for m,a,_ in SALES if m==p)==sum(a for m,_,a in VAR if m==p)
assert BANDS[0]==STORE_ORDERS
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
with open('data/daily/daily_order_bands.csv','a',newline='\n') as f:
    f.write(','.join([D]+[str(x) for x in BANDS])+'\n')
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS, '広告キャンペーン', sorted(AD))
