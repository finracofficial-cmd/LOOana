# -*- coding: utf-8 -*-
"""2026-11-15(日) をCSVへ追記。11/16 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1115/meta_camp_1114_1115_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認）: 00時台 W固定 -sab 15,600→13,000／ドア 8,000→9,600／裏起毛パンツ 停止／ブランケット 8,000→10,000（15a）・ワイパー 25,000→20,000（15b）／
12時台 ノーズEMS v2 に広告B（審査→承認）／13時ごろ シェーバー v2 に広告B・A を編集（審査）／15時台 新キャンペーン「高見えレザーヘッドレストフックv2」8,000（15c）→ 終日の最終 15セット・178,600円。
VIP特典の無料優先配送18件（gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）・防風あったか裏起毛パンツ（停止後の残り 89円）。広告なしで売れた: 高見えレザードアポケット 1個。
バリエーション別原価: ナノ 白緑（ピュアホワイト6・セージグリーン2）／黒桃（マットブラック2）。ブランケットは3色とも2,152。"""
import csv, json, re, collections
D='2026-11-15'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'伸縮ワックス洗車ブラシ':4980,'3WAY着る電気ブランケット':5980,'スマートノーズEMS美顔器':6980,
 '携帯電動シェーバー':4980,'高見えレザーヘッドレストフック':3980,'高見えレザードアポケット':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 442620, 20010, 76, 118
VIP_GIFT_QTY, RETURNED_QTY = 18, 0
SALES=[('伸縮ガラスクリーナー',91540,3980),('W固定スマホ車載ホルダー',51740,2388),('スマートノーズEMS美顔器',41880,0),('ナノガラス脱毛パッド',39800,796),
 ('ワイド水切りワイパー',39800,1592),('3WAY着る電気ブランケット',35880,3887),('携帯電動シェーバー',34860,2988),('マグネットドアクッション',31840,1791),
 ('伸縮ワックス洗車ブラシ',24900,996),('4-in-1マルチクリーナー',20940,0),('快適マジックインソール',11940,796),('高見えレザーヘッドレストフック',11940,796),
 ('高見えレザードアポケット',3980,0),('優先配送',1580,0)]
VAR=[('ナノガラス脱毛パッド','白緑',31840),('ナノガラス脱毛パッド','黒桃',7960)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1115/'
_raw=json.load(open(O+'sales_1115_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1115_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1115_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':23880,'セージグリーン':7960,'マットブラック':7960}, _var['ナノガラス脱毛パッド']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1114_1115_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1115_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(76,20,7,3), BANDS
ACCT=sum(AD.values()); assert ACCT==180535, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==100 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
assert sum(a for m,a,_ in SALES if m=='ナノガラス脱毛パッド')==sum(a for m,_,a in VAR if m=='ナノガラス脱毛パッド')
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
