# -*- coding: utf-8 -*-
"""2026-11-07(土) をCSVへ追記。11/08 06時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1107/meta_camp_1106_1107_raw.txt）。
当日の予算変更（ユーザー・Meta直読で確認）: 18:50確認 クリーナーsabu 15,000→18,000・ワイパー18,000→21,000・レインガード11,000→16,000・加湿器15,000→10,000・ドア15,000→10,000 → 終日の最終 15セット・204,000円。
VIP特典の無料優先配送21件（12+9・gross 0円）は売上行に入れない。有料の優先配送2件（790円×2）。
返品: 加湿器が returns −4,980（1個・net_items_sold 4＝販売5−返品1）。同額 +4,980 が商品名空欄の行に入り、全店の returns は0。原価は販売数（gross÷売価＝5個）で計上（A案）。
加湿器のShopify商品名は「コードレスパワーミスト加湿器」。CSVはMetaのキャンペーン名「コードレスダブルミスト加湿器」で続ける。
広告なしで売れた商品: 優先配送（有料）2のみ。"""
import csv
D='2026-11-07'
PRICE={'伸縮ガラスクリーナー':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'クリアビューレインガードフィルム':3980,'伸縮ワックス洗車ブラシ':4980,
 '4-in-1マルチクリーナー':6980,'ナノガラス脱毛パッド':3980,'ポータブルヒートシーラー':3980,'コードレスダブルミスト加湿器':4980,'快適マジックインソール':3980,
 '姿勢サポートチェア':5980,'マグネットドアクッション':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 501240, 18512, 94, 139
VIP_GIFT_QTY, RETURNED_QTY = 21, 1
SALES=[('伸縮ガラスクリーナー',95520,3980),('ワイド水切りワイパー',75620,2388),('W固定スマホ車載ホルダー',67660,2388),('クリアビューレインガードフィルム',51740,3980),
 ('伸縮ワックス洗車ブラシ',39840,996),('4-in-1マルチクリーナー',34900,0),('ナノガラス脱毛パッド',31840,0),('ポータブルヒートシーラー',27860,796),
 ('コードレスダブルミスト加湿器',24900,1992),('快適マジックインソール',19900,796),('姿勢サポートチェア',17940,1196),('マグネットドアクッション',11940,0),('優先配送',1580,0)]
# ナノ: ピュアホワイト23,880＋セージグリーン3,980＝白緑／マットブラック3,980＝黒桃。ディスペンサーは販売0
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',3980)]
AD={}
for l in open('scripts/daily/o1107/meta_camp_1106_1107_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(94,23,5,2)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==198195, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==119 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
