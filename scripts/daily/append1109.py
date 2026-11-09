# -*- coding: utf-8 -*-
"""2026-11-09(月) をCSVへ追記。11/10 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1109/meta_camp_1108_1109_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 4-in-1 11,000→13,000・クリーナー主力16,000→13,000／sabu 18,000→21,000（2026-11-09b）／
10:12 加湿器を停止（2026-11-09c）／20時台 膝サポーターのキャンペーンが停止（11/10 00時台の直読で判明・時間別消化は20時台139円が最後）→ 終日の最終 14セット・198,000円。
VIP特典の無料優先配送15件（9+6・gross 0円）は売上行に入れない。有料の優先配送1件（790円）。返品なし（returns 0）。
加湿器は Shopify 上の商品名が「コードレスパワーミスト加湿器」（11/6に改名・同じ商品ID）。CSVはMetaのキャンペーン名「コードレスダブルミスト加湿器」で記録する。"""
import csv, json
D='2026-11-09'
PRICE={'クリアビューレインガードフィルム':3980,'ワイド水切りワイパー':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,'伸縮ワックス洗車ブラシ':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'マグネットドアクッション':3980,
 'コードレスダブルミスト加湿器':4980,'姿勢サポートチェア':5980,'シリコンホールド膝サポーター':4980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 405870, 11743, 79, 112
VIP_GIFT_QTY, RETURNED_QTY = 15, 0
SALES=[('ワイド水切りワイパー',115420,4975),('伸縮ガラスクリーナー',63680,796),('伸縮ワックス洗車ブラシ',49800,1992),('クリアビューレインガードフィルム',43780,3184),
 ('W固定スマホ車載ホルダー',39800,0),('快適マジックインソール',27860,796),('4-in-1マルチクリーナー',20940,0),('マグネットドアクッション',15920,0),
 ('ナノガラス脱毛パッド',11940,0),('姿勢サポートチェア',5980,0),('コードレスダブルミスト加湿器',4980,0),('シリコンホールド膝サポーター',4980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト11,940＝白緑のみ
VAR=[('ナノガラス脱毛パッド','白緑',11940)]
# --- 取得ファイルとの突合（Shopify） ---
import re
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
_raw=json.load(open('scripts/daily/o1109/sales_1109_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, '取得ファイルと一致しない'
_st=json.load(open('scripts/daily/o1109/store_1109_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
AD={}
for l in open('scripts/daily/o1109/meta_camp_1108_1109_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(79,15,4,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
_b=json.load(open('scripts/daily/o1109/bands_1109_raw.json'))['result']['data']
assert BANDS==(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count'])
ACCT=sum(AD.values()); assert ACCT==198846, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==97 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS)
