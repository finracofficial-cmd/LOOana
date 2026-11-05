# -*- coding: utf-8 -*-
"""2026-11-05(木) をCSVへ追記。11/06 00時台に取得。広告費はキャンペーン合算（data_query fresh・暫定。scripts/daily/o1105/meta_camp_1104_1105_raw.txt）。
当日: 01:10確認 毛玉停止・加湿器13,000→16,000・クリーナー主力18,000→16,000・インソール13,000→10,000／01時台 ナノバブル再開8,000 → 11:1x 停止／
12:56 ワイパー8,000→12,000／22時台 新商品クリアビューレインガードフィルム8,000（審査通過後に1,091円）→ 終日の最終 15セット・192,000円。
VIP特典の無料優先配送19件（16+3・gross 0円）は売上行に入れない。返品0件。有料の優先配送0件。
広告なしで売れた商品: 5WAY腰掛けファン2・ネックマッサージャー1・壁掛けディスペンサー1（3本）・携帯電動シェーバー1・4WAY 1・完全遮光・形状記憶 1・毛玉1（停止中）。"""
import csv
D='2026-11-05'
PRICE={'伸縮ガラスクリーナー':3980,'4-in-1マルチクリーナー':6980,'W固定スマホ車載ホルダー':3980,'ナノガラス脱毛パッド':3980,'伸縮ワックス洗車ブラシ':4980,
 'ワイド水切りワイパー':3980,'マグネットドアクッション':3980,'コードレスダブルミスト加湿器':4980,'快適マジックインソール':3980,'姿勢サポートチェア':5980,
 'ポータブルヒートシーラー':3980,'5WAY腰掛けファン':4980,'ネックマッサージャー':8980,'壁掛けディスペンサー':6980,'携帯電動シェーバー':4980,'4WAY':4980,
 'コードレス毛玉クリーナー':4980,'完全遮光・形状記憶':4980}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 461960, 19069, 80, 121
VIP_GIFT_QTY, RETURNED_QTY = 19, 0
SALES=[('伸縮ガラスクリーナー',75620,3184),('4-in-1マルチクリーナー',55840,4537),('W固定スマホ車載ホルダー',51740,796),('ナノガラス脱毛パッド',51740,2388),
 ('伸縮ワックス洗車ブラシ',49800,996),('ワイド水切りワイパー',43780,2388),('マグネットドアクッション',27860,796),('コードレスダブルミスト加湿器',19920,996),
 ('快適マジックインソール',15920,796),('姿勢サポートチェア',11960,1196),('ポータブルヒートシーラー',11940,0),('5WAY腰掛けファン',9960,996),
 ('ネックマッサージャー',8980,0),('壁掛けディスペンサー',6980,0),('携帯電動シェーバー',4980,0),('4WAY',4980,0),('コードレス毛玉クリーナー',4980,0),('完全遮光・形状記憶',4980,0)]
# ナノ: ピュアホワイト19,900＋セージグリーン15,920＝白緑／マットブラック7,960＋ベイビーピンク7,960＝黒桃。ディスペンサー: シルバー3本セット6,980
VAR=[('ナノガラス脱毛パッド','白緑',35820),('ナノガラス脱毛パッド','黒桃',15920),('壁掛けディスペンサー','3本',6980)]
AD={}
for l in open('scripts/daily/o1105/meta_camp_1104_1105_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
BANDS=(80,20,7,4)   # 注文数・7,000円以上・8,000円以上・10,000円以上（ordersCount current_total_price・EXACT）
ACCT=sum(AD.values()); assert ACCT==203228, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==102 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
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
