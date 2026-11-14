# -*- coding: utf-8 -*-
"""2026-11-14(土) をCSVへ追記。11/15 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1114/meta_camp_1113_1114_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認）: 00時台 クリーナー 13,000→15,000・sabu 16,000→19,000／ワイパー 22,000→25,000／ナノ２ 16,000→18,000／インソール 10,000→11,000（14a・14b）／
16:51 スマートノーズEMS美顔器 5,980→6,980 に値上げ・17時台 新キャンペーン「スマートノーズEMS美顔器v2」8,000（14c）／17時台「携帯電動シェーバーv2」8,000（14d）・21時台 シェーバー広告Aの動画差し替え（予算そのまま）
→ 終日の最終 15セット・182,600円（11/15 00時台 data_query fresh の日予算・o1114/budgets_dq_1115.txt。14d と一致）。
VIP特典の無料優先配送10件（gross 0円）は売上行に入れない。有料の優先配送1件（790円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）（全商品横断）・携帯電動シェーバーv2（0個）。
バリエーション別原価: ナノ 白緑（ピュアホワイト3・セージグリーン2）／黒桃（マットブラック6）。裏起毛パンツ ブラック/L（1,219）1個・ブラック/S（1,140）1個。3WAY着る電気ブランケットは3色とも2,152。"""
import csv, json, re, collections
D='2026-11-14'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'防風あったか裏起毛パンツ':3980,
 'マグネットドアクッション':3980,'快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'伸縮ワックス洗車ブラシ':4980,'3WAY着る電気ブランケット':5980,
 'スマートノーズEMS美顔器':6980,'クリアビューレインガードフィルム':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 328270, 8759, 64, 87
VIP_GIFT_QTY, RETURNED_QTY = 10, 0
SALES=[('伸縮ガラスクリーナー',91540,3184),('ナノガラス脱毛パッド',43780,796),('W固定スマホ車載ホルダー',35820,0),('ワイド水切りワイパー',35820,0),
 ('伸縮ワックス洗車ブラシ',24900,996),('3WAY着る電気ブランケット',23920,1196),('4-in-1マルチクリーナー',20940,0),('快適マジックインソール',19900,2587),
 ('マグネットドアクッション',11940,0),('防風あったか裏起毛パンツ',7960,0),('スマートノーズEMS美顔器',6980,0),('クリアビューレインガードフィルム',3980,0),('優先配送',790,0)]
VAR=[('ナノガラス脱毛パッド','白緑',19900),('ナノガラス脱毛パッド','黒桃',23880),('防風あったか裏起毛パンツ','L',3980),('防風あったか裏起毛パンツ','S',3980)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1114/'
_raw=json.load(open(O+'sales_1114_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1114_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1114_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'マットブラック':23880,'ピュアホワイト':11940,'セージグリーン':7960}, _var['ナノガラス脱毛パッド']
assert _var['防風あったか裏起毛パンツ']=={'ブラック / L':3980,'ブラック / S':3980}, _var['防風あったか裏起毛パンツ']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1113_1114_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1114_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(64,11,3,2), BANDS
ACCT=sum(AD.values()); assert ACCT==163528, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==77 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS, '広告キャンペーン', sorted(AD))
