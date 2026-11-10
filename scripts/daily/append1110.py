# -*- coding: utf-8 -*-
"""2026-11-10(火) をCSVへ追記。11/11 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1110/meta_camp_1109_1110_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 00:29確認 ワイパー23,000→26,000・クリーナー主力13,000→10,000／sabu 21,000→16,000・ナノ18,000→13,000・車載12,000→10,000／15,000→13,000・
4-in-1 13,000→11,000・シーラー停止（2026-11-10b・13セット174,000）／15:20確認 新商品 アーチフィット逆ヒールサンダル 8,000（審査通過後に3,849円）→ 終日の最終 14セット・182,000円。
VIP特典の無料優先配送11件（8+3・gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし（returns 0）。
広告なしで売れた商品: 高見えレザーヘッドレストフック2個（グレー1・ブラウン1＝茶灰）・有料の優先配送2。シーラーの広告費7円は停止直後の残り。"""
import csv, json, re
D='2026-11-10'
PRICE={'クリアビューレインガードフィルム':3980,'ワイド水切りワイパー':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,'伸縮ワックス洗車ブラシ':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'快適マジックインソール':3980,'マグネットドアクッション':3980,
 '姿勢サポートチェア':5980,'高見えレザーヘッドレストフック':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 375780, 10547, 75, 103
VIP_GIFT_QTY, RETURNED_QTY = 11, 0
SALES=[('伸縮ガラスクリーナー',75620,2388),('W固定スマホ車載ホルダー',67660,1592),('ワイド水切りワイパー',59700,0),('クリアビューレインガードフィルム',35820,796),
 ('伸縮ワックス洗車ブラシ',29880,0),('ナノガラス脱毛パッド',27860,2587),('マグネットドアクッション',27860,1592),('快適マジックインソール',15920,796),
 ('4-in-1マルチクリーナー',13960,0),('姿勢サポートチェア',11960,0),('高見えレザーヘッドレストフック',7960,796),('優先配送',1580,0)]
# ナノ: ピュアホワイト11,940＝白緑／ベイビーピンク7,960＋マットブラック7,960＝黒桃。フック: グレー3,980＋ブラウン3,980＝茶灰
VAR=[('ナノガラス脱毛パッド','白緑',11940),('ナノガラス脱毛パッド','黒桃',15920),('高見えレザーヘッドレストフック','茶灰',7960)]
# --- 取得ファイルとの突合（Shopify） ---
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
_raw=json.load(open('scripts/daily/o1110/sales_1110_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, '取得ファイルと一致しない'
_st=json.load(open('scripts/daily/o1110/store_1110_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_nv={r[0]:int(r[1]) for r in json.load(open('scripts/daily/o1110/nano_var_1110_raw.json'))['rows']}
assert _nv=={'ピュアホワイト':11940,'ベイビーピンク':7960,'マットブラック':7960}, _nv
_hv={r[0]:int(r[1]) for r in json.load(open('scripts/daily/o1110/hook_var_1110_raw.json'))['rows']}
assert _hv=={'グレー':3980,'ブラウン':3980}, _hv
AD={}
for l in open('scripts/daily/o1110/meta_camp_1109_1110_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(75,12,2,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
_b=json.load(open('scripts/daily/o1110/bands_1110_raw.json'))['result']['data']
assert BANDS==(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count'])
ACCT=sum(AD.values()); assert ACCT==165063, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==92 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for _m in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック'):
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
