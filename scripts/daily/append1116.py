# -*- coding: utf-8 -*-
"""2026-11-16(月) をCSVへ追記。11/17 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1116/meta_camp_1115_1116_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認）: 00時台 ノーズ v2 8,000→12,000・シェーバー v2 →11,000・インソール旧 停止（16a）／インソール v2 8,000（16b）→ 01時台に停止、
フック v2 停止・フック v3 8,000（16d）／インソール v3 8,000 で再開（16f）／11時台 新商品 360°マルチクリップ 8,000（16g・広告A→B 作り直し）／
フック v3 停止・v4 8,000（16h・昼から配信）→ 22時台 v4 停止（16i）→ 終日の最終 15セット・182,600円。
VIP特典の無料優先配送15件（gross 0円）は売上行に入れない。有料の優先配送1件（790円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）・高見えレザーヘッドレストフック（v2 234・v4 6,136）。広告なしで売れた: 2WAYシートボックス・クリアビューレインガードフィルム・ファスナー修理キット・すき間収納シートポケット 各1個。
バリエーション別原価: ナノ 白緑（ピュアホワイト1・セージグリーン2）／黒桃（マットブラック2・ベイビーピンク1）。すき間収納シートポケットはブラック＝標準（760）。"""
import csv, json, re, collections
D='2026-11-16'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'伸縮ワックス洗車ブラシ':4980,'3WAY着る電気ブランケット':5980,'スマートノーズEMS美顔器':6980,
 '携帯電動シェーバー':4980,'360°マルチクリップ車載スマホホルダー':3980,'2WAYシートボックス':4980,'クリアビューレインガードフィルム':3980,
 'ファスナー修理キット':3980,'すき間収納シートポケット':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 446830, 15724, 76, 114
VIP_GIFT_QTY, RETURNED_QTY = 15, 0
SALES=[('伸縮ガラスクリーナー',103480,5174),('快適マジックインソール',63680,5970),('4-in-1マルチクリーナー',62820,1396),('スマートノーズEMS美顔器',48860,0),
 ('W固定スマホ車載ホルダー',35820,796),('ナノガラス脱毛パッド',23880,1592),('マグネットドアクッション',23880,0),('ワイド水切りワイパー',19900,0),
 ('360°マルチクリップ車載スマホホルダー',15920,796),('伸縮ワックス洗車ブラシ',14940,0),('携帯電動シェーバー',9960,0),('3WAY着る電気ブランケット',5980,0),
 ('2WAYシートボックス',4980,0),('クリアビューレインガードフィルム',3980,0),('ファスナー修理キット',3980,0),('すき間収納シートポケット',3980,0),('優先配送',790,0)]
VAR=[('ナノガラス脱毛パッド','白緑',11940),('ナノガラス脱毛パッド','黒桃',11940),('すき間収納シートポケット','標準',3980)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1116/'
_raw=json.load(open(O+'sales_1116_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1116_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1116_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':3980,'セージグリーン':7960,'マットブラック':7960,'ベイビーピンク':3980}, _var['ナノガラス脱毛パッド']
assert _var['すき間収納シートポケット']=={'ブラック / 運転席＋助手席の2ペアセット':3980}
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1115_1116_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1116_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(76,19,6,5), BANDS
ACCT=sum(AD.values()); assert ACCT==184018, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==99 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for p in ('ナノガラス脱毛パッド','すき間収納シートポケット'):
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
