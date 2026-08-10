# -*- coding: utf-8 -*-
"""2026-08-10 の実測をCSVへ追記。数値はすべて当日のShopify/Metaクエリ結果の貼付。"""
import csv
D='2026-08-10'
# Shopify: FROM sales SHOW gross_sales, net_items_sold, discounts, returns GROUP BY product_title SINCE/UNTIL 2026-08-10
SALES=[('ナノガラス脱毛パッド',179100,5572),('W固定スマホ車載ホルダー',79600,1592),('害虫ブロッカー',59700,3980),
('ムダ毛シェーバー',55840,0),('接触冷感UVパーカー',55720,0),('形状記憶日傘',49800,0),
('完全遮光・接触冷感UVハット',49800,0),('4WAY',34860,996),('偏光・調光サングラス',31840,796),
('5WAY腰掛けファン',29880,2241),('完全遮光・形状記憶',29880,2241),('接触冷感UVアームカバー',19900,796),
('バランスケアスリッパ',14940,996),('卓上冷感クーラー',11960,0),('携帯電動シェーバー',9960,0),
('2WAYシートボックス',9960,996),('ナノバブルシャワーヘッド',6980,0),('3WAYサーキュレーター',6980,0),
('姿勢サポートチェア',5980,0),('優先配送',2144,0)]
# Meta: 広告セット別を campaign へ集約（data_query 2026-08-10, Asia/Tokyo）
AD=[('ナノガラス脱毛パッド',56486+12746),('害虫ブロッカー',27639+17831),
('W固定スマホ車載ホルダー',34926),('形状記憶日傘',30819),
('4WAY 取り付けOK 小型瞬間冷却ハンディファン',27969),('接触冷感UVパーカー',26442),
('カタログ全部（テスト）',21024),('ムダ毛シェーバー',19551),
('完全遮光・形状記憶・晴雨兼用・UV日傘',18942),('偏光・調光サングラス',18535),
('5WAY腰掛けファン',14273),('完全遮光・接触冷感UVハット',12571),('2WAYシートボックス',12340),
('姿勢サポートチェア',8687),('携帯電動シェーバー',8082),('瞬間冷感ポンチョ',7721),
('接触冷感UVアームカバー',7338),('卓上冷感クーラー',7128),('バランスケアスリッパ',4513)]
assert sum(g for _,g,_ in SALES)==744824, sum(g for _,g,_ in SALES)   # 全店クエリ gross_sales
assert sum(d for _,_,d in SALES)==20206, sum(d for _,_,d in SALES)    # 全店クエリ discounts
tot=sum(c for _,c in AD); acct=395563                                  # Metaアカウントレベル実測
assert abs(tot-acct)/acct<0.001, (tot,acct,(tot-acct)/acct)
def rw(p,h,rows):
    old=[r for r in csv.reader(open(p))][1:]; old=[r for r in old if r and r[0]!=D]
    with open(p,'w',newline='') as f:
        w=csv.writer(f); w.writerow(h); w.writerows(old)
        for r in rows: w.writerow([D]+list(r))
rw('data/daily/daily_sales.csv',['date','name','gross','disc'],SALES)
rw('data/daily/daily_ad.csv',['date','campaign','cost'],AD)
print(f'appended {D}  売上gross {sum(g for _,g,_ in SALES):,}  値引 {sum(d for _,_,d in SALES):,}  実売 {744824-20206:,}')
print(f'  広告 Σキャンペーン {tot:,} vs アカウント {acct:,}  差 {tot-acct:+,}（{(tot-acct)/acct*100:+.4f}%）')
