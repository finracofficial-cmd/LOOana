# -*- coding: utf-8 -*-
"""2026-11-13(金) をCSVへ追記。11/14 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1113/meta_camp_1112_1113_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認）: 09時台までに W固定 -sab 13,000→15,600（13a）／15時台 3WAY着る電気ブランケット 新規8,000（13c）／
15時台 伸縮ワックス洗車ブラシ・マグネットドアクッションに広告B（予算そのまま）→ 終日の最終 13セット・155,600円（11/14 00時台 Meta直読で一致・o1113/budgets_direct_1114.txt）。
VIP特典の無料優先配送7件（gross 0円）は売上行に入れない。有料の優先配送1件（790円）。
返品: コードレスダブルミスト加湿器1個（net_items_sold −1・商品行の returns −4,980／商品名なしの行 +4,980・全店の returns は0）。A案どおり売上・利益から引かない。
広告費ありで売上0: カタログ全部（テスト）（全商品横断）。
バリエーション別原価: 裏起毛パンツ グレー/M（1,148）1個・グレー/L（1,219）1個。3WAY着る電気ブランケットは3色とも2,152（ベージュ2・グリーン1）。"""
import csv, json, re, collections
D='2026-11-13'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'防風あったか裏起毛パンツ':3980,
 'マグネットドアクッション':3980,'快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'伸縮ワックス洗車ブラシ':4980,'3WAY着る電気ブランケット':5980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 291450, 8963, 58, 74
VIP_GIFT_QTY, RETURNED_QTY = 7, 1
SALES=[('伸縮ガラスクリーナー',51740,1592),('W固定スマホ車載ホルダー',43780,796),('快適マジックインソール',35820,2587),('ワイド水切りワイパー',35820,796),
 ('伸縮ワックス洗車ブラシ',29880,1996),('4-in-1マルチクリーナー',27920,0),('ナノガラス脱毛パッド',19900,0),('マグネットドアクッション',19900,0),
 ('3WAY着る電気ブランケット',17940,1196),('防風あったか裏起毛パンツ',7960,0),('優先配送',790,0)]
# ナノ: ピュアホワイト11,940＋セージグリーン3,980＝白緑／マットブラック3,980＝黒桃。裏起毛パンツ: グレー/M 3,980＝M・グレー/L 3,980＝L
VAR=[('ナノガラス脱毛パッド','白緑',15920),('ナノガラス脱毛パッド','黒桃',3980),('防風あったか裏起毛パンツ','M',3980),('防風あったか裏起毛パンツ','L',3980)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1113/'
_raw=json.load(open(O+'sales_1113_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, '取得ファイルと一致しない'
_ret={nm(t):(int(q),int(r)) for t,g,dc,q,r in _raw if int(r)}
assert _ret=={'':(0,4980),'コードレスダブルミスト加湿器':(-1,-4980)}, _ret   # 返品は加湿器1個だけ
_st=json.load(open(O+'store_1113_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1113_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':11940,'セージグリーン':3980,'マットブラック':3980}, _var['ナノガラス脱毛パッド']
assert _var['防風あったか裏起毛パンツ']=={'グレー / M':3980,'グレー / L':3980}, _var['防風あったか裏起毛パンツ']
assert _var['3WAY着る電気ブランケット']=={'ベージュ / 150x80CM':11960,'グリーン / 150x80CM':5980}, _var['3WAY着る電気ブランケット']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1112_1113_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(58,8,2,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
_b=json.load(open(O+'bands_1113_raw.json'))['result']['data']
assert BANDS==(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count'])
ACCT=sum(AD.values()); assert ACCT==145662, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==68 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for _m in ('ナノガラス脱毛パッド','防風あったか裏起毛パンツ'):
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
