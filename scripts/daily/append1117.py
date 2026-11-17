# -*- coding: utf-8 -*-
"""2026-11-17(火) をCSVへ追記。11/18 00時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1117/meta_camp_1116_1117_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認）: 00時台 ノーズ 12,000→16,000・インソール v3 8,000→12,000・シェーバー 11,000→8,000・洗車ブラシ 12,000→9,000（17a）／ガラス sabu 19,000→22,000（17b）／
10時台 ブランケット広告A のショップ オフ（商品の拡張 OFF→ON）／18時台 新商品 裏起毛タッチ防寒グローブ 8,000（17c・配信は夜から）／マルチクリップ 8,000→10,000（17d・時刻は未確認・11/18 00時台に検知）→ 終日の最終 16セット・197,600円。
ガラスは 11/16 から広告B（新しい動画）が配信。VIP特典の無料優先配送10件（gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）・伸縮ワックス洗車ブラシ（7,583）・裏起毛タッチ防寒グローブ（2,682）。広告なしで売れた商品はなし。
バリエーション別原価: ナノ 白緑（ピュアホワイト4・セージグリーン3）／黒桃（マットブラック3）。"""
import csv, json, re, collections
D='2026-11-17'
PRICE={'裏起毛タッチ防寒グローブ':3980,'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'伸縮ワックス洗車ブラシ':4980,'3WAY着る電気ブランケット':5980,'スマートノーズEMS美顔器':6980,
 '携帯電動シェーバー':4980,'360°マルチクリップ車載スマホホルダー':3980,'2WAYシートボックス':4980,'クリアビューレインガードフィルム':3980,
 'ファスナー修理キット':3980,'すき間収納シートポケット':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 323120, 8756, 60, 85
VIP_GIFT_QTY, RETURNED_QTY = 10, 0
SALES=[('伸縮ガラスクリーナー',59700,3184),('スマートノーズEMS美顔器',41880,0),('ナノガラス脱毛パッド',39800,1592),('W固定スマホ車載ホルダー',35820,1592),
 ('ワイド水切りワイパー',31840,796),('360°マルチクリップ車載スマホホルダー',27860,0),('快適マジックインソール',23880,1592),('マグネットドアクッション',19900,0),
 ('携帯電動シェーバー',14940,0),('4-in-1マルチクリーナー',13960,0),('3WAY着る電気ブランケット',11960,0),('優先配送',1580,0)]
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',11940)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1117/'
_raw=json.load(open(O+'sales_1117_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1117_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1117_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':15920,'セージグリーン':11940,'マットブラック':11940}, _var['ナノガラス脱毛パッド']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1116_1117_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1117_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(60,12,1,1), BANDS
ACCT=sum(AD.values()); assert ACCT==195748, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==75 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for p in ('ナノガラス脱毛パッド',):
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
