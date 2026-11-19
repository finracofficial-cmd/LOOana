# -*- coding: utf-8 -*-
"""2026-11-19(木) をCSVへ追記。11/20 00時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1119/meta_camp_1118_1119_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認。budget-snapshots 2026-11-19a〜d）: 00時台 インソール v3 12,000→15,000・マルチクリップ 12,000→10,000・ドア 12,000→9,600・4-in-1 8,000→9,600（19a）／
11時台 シーラー v2 停止（19b）／17時台 ディスペンサー v2 停止（19c）・新商品「充電式ダブルミスト卓上加湿器」開始 8,000（19d）。
お店の変更（data/site-events.csv）: 14:37 VIP特典・優先配送の「配送が必要」を外す／15:05 までにカートの文を変更／15:15ごろ スマホの商品ページに「商品を選ぶ」の固定ボタン。
VIP特典の無料優先配送14件（gross 0円）は売上行に入れない。有料の優先配送なし。返品なし。
広告費ありで売上0: カタログ全部（テスト）・ポータブルヒートシーラー v2（4,785）・ディスペンサー v2（4,552）・充電式ダブルミスト卓上加湿器（2,907・新商品）。
広告なしで売れた商品: 裏起毛タッチ防寒グローブ 1・アーチフィット逆ヒールサンダル 1・防風あったか裏起毛パンツ 1・すき間収納シートポケット 1。
バリエーション別原価: ナノ 白緑（ピュアホワイト3・セージグリーン2）／黒桃（マットブラック3・ベイビーピンク1）・フック 黒（ブラック5）／茶灰（グレー3・ブラウン2）・裏起毛パンツ XL（ブラック/XL 1）・シートポケット 標準（ブラック1）。
アーチフィット逆ヒールサンダルは初めての販売（21.0〜22.5cm / ベージュ・Shopify unitCost 1,176）。"""
import csv, json, re, collections
D='2026-11-19'
PRICE={'裏起毛タッチ防寒グローブ':3980,'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'スマートノーズEMS美顔器':6980,'携帯電動シェーバー':4980,'360°マルチクリップ車載スマホホルダー':3980,
 '高見えレザーヘッドレストフック':3980,'アーチフィット逆ヒールサンダル':3980,'防風あったか裏起毛パンツ':3980,'すき間収納シートポケット':3980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 361300, 16520, 65, 99
VIP_GIFT_QTY, RETURNED_QTY = 14, 0
SALES=[('伸縮ガラスクリーナー',71640,4378),('ワイド水切りワイパー',55720,3184),('高見えレザーヘッドレストフック',39800,5174),('ナノガラス脱毛パッド',35820,796),
 ('4-in-1マルチクリーナー',34900,1396),('快適マジックインソール',27860,796),('W固定スマホ車載ホルダー',27860,796),('360°マルチクリップ車載スマホホルダー',15920,0),
 ('スマートノーズEMS美顔器',13960,0),('マグネットドアクッション',11940,0),('携帯電動シェーバー',9960,0),('裏起毛タッチ防寒グローブ',3980,0),
 ('アーチフィット逆ヒールサンダル',3980,0),('防風あったか裏起毛パンツ',3980,0),('すき間収納シートポケット',3980,0)]
VAR=[('ナノガラス脱毛パッド','白緑',19900),('ナノガラス脱毛パッド','黒桃',15920),('高見えレザーヘッドレストフック','黒',19900),('高見えレザーヘッドレストフック','茶灰',19900),
 ('防風あったか裏起毛パンツ','XL',3980),('すき間収納シートポケット','標準',3980)]
O='scripts/daily/o1119/'
_raw=json.load(open(O+'sales_1119_raw.json'))['rows']
_rs={t:(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1119_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1119_raw.json'))['rows']:
    if int(g): _var[t][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':11940,'マットブラック':11940,'セージグリーン':7960,'ベイビーピンク':3980}, _var['ナノガラス脱毛パッド']
assert _var['高見えレザーヘッドレストフック']=={'ブラック':19900,'グレー':11940,'ブラウン':7960}, _var['高見えレザーヘッドレストフック']
assert _var['防風あったか裏起毛パンツ']=={'ブラック / XL':3980} and _var['すき間収納シートポケット']=={'ブラック / 運転席＋助手席の2ペアセット':3980}
assert _var['アーチフィット逆ヒールサンダル']=={'21.0〜22.5cm / ベージュ':3980}
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1118_1119_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1119_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(65,16,5,5), BANDS
ACCT=sum(AD.values()); assert ACCT==190365, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==85 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for p in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック','防風あったか裏起毛パンツ','すき間収納シートポケット'):
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
