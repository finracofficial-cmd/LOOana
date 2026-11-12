# -*- coding: utf-8 -*-
"""2026-11-12(木) をCSVへ追記。11/13 01時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1112/meta_camp_1111_1112_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 09時台 レインガード12,000→10,000（12d）／09時台 UV歯ブラシ除菌器 再開10,000（12e）／10時ごろ すき間収納シートポケット停止（12f）／
10時台 バランスケアスリッパ 再開8,000（12g）／11時台 レインガード 元のセット停止・コピー5,000（12h）／11時台 高見えレザーヘッドレストフック 1112複製 再開8,000（12i）／14時台 UV歯ブラシに広告B追加（予算そのまま）／
19時台 レインガード キャンペーン停止（12j）／22時台 バランスケアスリッパ停止（12k）／22時台 UV歯ブラシ停止（12l）／23時台 フック停止（12m）→ 終日の最終 12セット・145,000円。
VIP特典の無料優先配送11件（gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし（returns 0）。
広告なしで売れた商品: コードレスダブルミスト加湿器2個（11/12 16:50・ワイド水切りワイパーの広告から来訪・customerJourneySummary）・有料の優先配送2。
広告費ありで売上0: UV歯ブラシ除菌器・バランスケアスリッパ・すき間収納シートポケット・クリアビューレインガードフィルム。
バリエーション別原価: 裏起毛パンツ ブラック/L（1,219）5個・グレー/XL（1,338）1個／フック ブラック（1,275→10/7以降のCJ原価732）1個。"""
import csv, json, re, collections
D='2026-11-12'
PRICE={'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'防風あったか裏起毛パンツ':3980,
 'マグネットドアクッション':3980,'快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'コードレスダブルミスト加湿器':4980,'伸縮ワックス洗車ブラシ':4980,
 '高見えレザーヘッドレストフック':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 336940, 10746, 68, 95
VIP_GIFT_QTY, RETURNED_QTY = 11, 0
SALES=[('伸縮ガラスクリーナー',71640,2388),('ナノガラス脱毛パッド',55720,796),('ワイド水切りワイパー',55720,796),('W固定スマホ車載ホルダー',51740,2587),
 ('防風あったか裏起毛パンツ',23880,2587),('マグネットドアクッション',23880,796),('快適マジックインソール',19900,796),('4-in-1マルチクリーナー',13960,0),
 ('コードレスダブルミスト加湿器',9960,0),('伸縮ワックス洗車ブラシ',4980,0),('高見えレザーヘッドレストフック',3980,0),('優先配送',1580,0)]
# ナノ: ピュアホワイト23,880＋セージグリーン11,940＝白緑／マットブラック15,920＋ベイビーピンク3,980＝黒桃。裏起毛パンツ: ブラック/L 19,900＝L・グレー/XL 3,980＝XL灰。フック: ブラック3,980＝黒
VAR=[('ナノガラス脱毛パッド','白緑',35820),('ナノガラス脱毛パッド','黒桃',19900),('防風あったか裏起毛パンツ','L',19900),('防風あったか裏起毛パンツ','XL灰',3980),
     ('高見えレザーヘッドレストフック','黒',3980)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
_raw=json.load(open('scripts/daily/o1112/sales_1112_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, '取得ファイルと一致しない'
assert all(int(r[4])==0 for r in _raw), '返品あり'
_st=json.load(open('scripts/daily/o1112/store_1112_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open('scripts/daily/o1112/var_1112_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':23880,'マットブラック':15920,'セージグリーン':11940,'ベイビーピンク':3980}, _var['ナノガラス脱毛パッド']
assert _var['防風あったか裏起毛パンツ']=={'ブラック / L':19900,'グレー / XL':3980}, _var['防風あったか裏起毛パンツ']
assert _var['高見えレザーヘッドレストフック']=={'ブラック':3980}, _var['高見えレザーヘッドレストフック']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open('scripts/daily/o1112/meta_camp_1111_1112_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(68,13,3,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
_b=json.load(open('scripts/daily/o1112/bands_1112_raw.json'))['result']['data']
assert BANDS==(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count'])
ACCT=sum(AD.values()); assert ACCT==183140, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==84 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for _m in ('ナノガラス脱毛パッド','防風あったか裏起毛パンツ','高見えレザーヘッドレストフック'):
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
