# -*- coding: utf-8 -*-
"""2026-11-11(水) をCSVへ追記。11/12 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1111/meta_camp_1110_1111_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 00:15 ワイパー26,000→23,000・レインガード21,000→18,000・ブラシ18,000→15,000・ドア8,000→11,000・アーチフィット停止（11b）／00:24 フック・シートボックス再開 各8,000（11c）／
09:48 フック・シートボックス停止・ワイパー→26,000・クリーナー主力10,000→13,000・ナノ13,000→16,000（11d）／12:08 レインガード→15,000（11e）／16:11 新商品 防風あったか裏起毛パンツ 8,000（11f）／
17:24 加湿器 再開8,000（11g）／20:28 レインガード→12,000・ワイパー→22,000・ブラシ→12,000・4-in-1 11,000→8,000・チェア停止（11h）／22:30 新商品 すき間収納シートポケット 8,000（11i）→ 終日の最終 15セット・176,000円。
VIP特典の無料優先配送9件（gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし（returns 0）。
広告なしで売れた商品: ムダ毛シェーバー1個・有料の優先配送2。アーチフィットの広告費34円は停止直後の残り。
バリエーション別原価: 裏起毛パンツ ブラック/S（1,140）・ブラック/XXL（1,251）各1個／すき間ポケット ベージュ（760）1個。"""
import csv, json, re, collections
D='2026-11-11'
PRICE={'クリアビューレインガードフィルム':3980,'ワイド水切りワイパー':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,'伸縮ワックス洗車ブラシ':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'マグネットドアクッション':3980,
 '防風あったか裏起毛パンツ':3980,'ムダ毛シェーバー':6980,'2WAYシートボックス':4980,'すき間収納シートポケット':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 346920, 8756, 72, 94
VIP_GIFT_QTY, RETURNED_QTY = 9, 0
SALES=[('伸縮ガラスクリーナー',75620,3184),('ワイド水切りワイパー',67660,2388),('ナノガラス脱毛パッド',51740,0),('W固定スマホ車載ホルダー',47760,1592),
 ('伸縮ワックス洗車ブラシ',24900,0),('クリアビューレインガードフィルム',15920,796),('4-in-1マルチクリーナー',13960,0),('快適マジックインソール',11940,0),
 ('マグネットドアクッション',11940,0),('防風あったか裏起毛パンツ',7960,796),('ムダ毛シェーバー',6980,0),('2WAYシートボックス',4980,0),('すき間収納シートポケット',3980,0),('優先配送',1580,0)]
# ナノ: ピュアホワイト23,880＋セージグリーン7,960＝白緑／マットブラック15,920＋ベイビーピンク3,980＝黒桃。裏起毛パンツ: ブラック/S・ブラック/XXL 各3,980。すき間ポケット: ベージュ3,980＝標準（赤以外）
VAR=[('ナノガラス脱毛パッド','白緑',31840),('ナノガラス脱毛パッド','黒桃',19900),('防風あったか裏起毛パンツ','S',3980),('防風あったか裏起毛パンツ','XXL',3980),('すき間収納シートポケット','標準',3980)]
# --- 取得ファイルとの突合（Shopify） ---
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
_raw=json.load(open('scripts/daily/o1111/sales_1111_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, '取得ファイルと一致しない'
_st=json.load(open('scripts/daily/o1111/store_1111_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open('scripts/daily/o1111/var_1111_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':23880,'マットブラック':15920,'セージグリーン':7960,'ベイビーピンク':3980}, _var['ナノガラス脱毛パッド']
assert _var['防風あったか裏起毛パンツ']=={'ブラック / S':3980,'ブラック / XXL':3980}, _var['防風あったか裏起毛パンツ']
assert _var['すき間収納シートポケット']=={'ベージュ / 運転席＋助手席の2ペアセット':3980}, _var['すき間収納シートポケット']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open('scripts/daily/o1111/meta_camp_1110_1111_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(72,11,0,0)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
_b=json.load(open('scripts/daily/o1111/bands_1111_raw.json'))['result']['data']
assert BANDS==(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count'])
ACCT=sum(AD.values()); assert ACCT==189643, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==85 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for _m in ('ナノガラス脱毛パッド','防風あったか裏起毛パンツ','すき間収納シートポケット'):
    assert sum(a for m,a,_ in SALES if m==_m)==sum(a for m,_,a in VAR if m==_m), _m
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
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
