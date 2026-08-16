# -*- coding: utf-8 -*-
"""2026-08-15 の実測を daily_sales.csv へ追記する（冪等）。

Shopify: FROM sales SHOW gross_sales, discounts, net_items_sold, orders, returns
         GROUP BY product_title SINCE 2026-08-15 UNTIL 2026-08-15（graphql_query 経由）

⚠️ Meta（Supermetrics）は 2026-08-16 朝の時点で全エンドポイントが
   "Anthropic Proxy: Invalid content from server" を返し、広告費を取得できなかった。
   したがって daily_ad.csv には 2026-08-15 を追記していない。
   復旧したら scripts/daily/append0815_ad.py を作って追記すること。
"""
import csv, os
B = '/home/user/LOOana/data/daily/'
D = '2026-08-15'

SALES = {  # 商品: (gross, discounts) ※CSVの短縮名に合わせる
 'ナノガラス脱毛パッド': (222880, 4776), 'W固定スマホ車載ホルダー': (79600, 2587),
 '害虫ブロッカー': (71640, 6766), '形状記憶日傘': (59760, 1992),
 'ムダ毛シェーバー': (55840, 0), '姿勢サポートチェア': (47840, 2392),
 '偏光・調光サングラス': (47760, 2587), '4WAY': (39840, 996),
 '2WAYシートボックス': (34860, 1992), '接触冷感UVアームカバー': (23880, 796),
 '完全遮光・接触冷感UVハット': (19920, 0), '接触冷感UVパーカー': (19900, 0),
 '快適マジックインソール': (15920, 1791), '5WAY腰掛けファン': (14940, 996),
 'バランスケアスリッパ': (14940, 0), '完全遮光・形状記憶': (14940, 996),
 'ナノバブルシャワーヘッド': (6980, 0), '携帯電動シェーバー': (4980, 0),
 '優先配送': (2144, 0),
}

# 縦照合: 全店1クエリの実測と1円まで一致すること（SKILL 5e-①）
assert sum(g for g, _ in SALES.values()) == 798564, sum(g for g, _ in SALES.values())
assert sum(d for _, d in SALES.values()) == 28667, sum(d for _, d in SALES.values())
print('検算OK: Σ商品gross = 全店798,564円 / Σ値引 = 全店28,667円（差0円）')

def append(path, rows):
    body = list(csv.reader(open(path, encoding='utf-8')))[1:]
    have = {tuple(r[:2]) for r in body}
    added = 0
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for r in rows:
            if tuple(str(x) for x in r[:2]) in have: continue
            w.writerow(r); added += 1
    print(f'{os.path.basename(path)}: {added}行追記（既存 {len(body)}行）')

append(B + 'daily_sales.csv', [[D, n, g, d] for n, (g, d) in SALES.items()])
print('\n⚠️ daily_ad.csv は未追記（Supermetricsが応答しないため）。'
      '広告費が必要な指標は本日算出しない。')
