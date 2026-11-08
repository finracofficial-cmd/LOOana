# -*- coding: utf-8 -*-
"""2026-11-08(日) をCSVへ追記。11/09 03時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1108/meta_camp_1107_1108_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 12:43確認 クリーナー主力19,000→16,000・ドア10,000→8,000・ワイパー21,000→23,000・レインガード16,000→21,000／
17:51確認 新商品 膝サポーター8,000（審査通過後に2,858円）／12:43以降（時刻は未確認・11/09 03時の直読で判明）加湿器10,000→8,000 → 終日の最終 16セット・212,000円。
VIP特典の無料優先配送19件（11+8・gross 0円）は売上行に入れない。有料の優先配送1件（790円）。
返品: 姿勢サポートチェア1個（returns −5,980・net_items_sold 1＝販売2−返品1）。同額+5,980が商品名空欄の行に入り、全店のreturnsは0。原価は販売数2個で計上（A案）。
広告なしで売れた商品: 壁掛けディスペンサー（3本セット）1・優先配送（有料）1。"""
import csv
D='2026-11-08'
PRICE={'クリアビューレインガードフィルム':3980,'ワイド水切りワイパー':3980,'伸縮ガラスクリーナー':3980,'W固定スマホ車載ホルダー':3980,'伸縮ワックス洗車ブラシ':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'ポータブルヒートシーラー':3980,'快適マジックインソール':3980,'マグネットドアクッション':3980,
 'コードレスダブルミスト加湿器':4980,'姿勢サポートチェア':5980,'壁掛けディスペンサー':6980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 598010, 17913, 114, 158
VIP_GIFT_QTY, RETURNED_QTY = 19, 1
SALES=[('クリアビューレインガードフィルム',119400,7761),('ワイド水切りワイパー',87560,2388),('伸縮ガラスクリーナー',67660,796),('W固定スマホ車載ホルダー',67660,0),
 ('伸縮ワックス洗車ブラシ',64740,2988),('4-in-1マルチクリーナー',48860,0),('ナノガラス脱毛パッド',47760,1592),('ポータブルヒートシーラー',27860,0),
 ('快適マジックインソール',15920,1592),('マグネットドアクッション',15920,796),('コードレスダブルミスト加湿器',14940,0),('姿勢サポートチェア',11960,0),
 ('壁掛けディスペンサー',6980,0),('優先配送',790,0)]
# ナノ: ピュアホワイト11,940＋セージグリーン7,960＝白緑／マットブラック19,900＋ベイビーピンク7,960＝黒桃。ディスペンサー: ブラック3本セット6,980
VAR=[('ナノガラス脱毛パッド','白緑',19900),('ナノガラス脱毛パッド','黒桃',27860),('壁掛けディスペンサー','3本',6980)]
AD={}
for l in open('scripts/daily/o1108/meta_camp_1107_1108_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(114,22,8,5)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==240848, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==140 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
