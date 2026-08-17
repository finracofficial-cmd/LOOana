# -*- coding: utf-8 -*-
"""2026-08-16 の実測を daily_sales.csv / daily_ad.csv へ追記する（冪等）。

Shopify: FROM sales SHOW gross_sales, discounts, net_items_sold, returns, orders
         GROUP BY product_title SINCE 2026-08-16 UNTIL 2026-08-16（graphql_query 経由）
Meta   : ds_id=FA / act_1124340806289175 / timezone=Asia/Tokyo / date=2026-08-16

縦照合: Σ商品gross = 全店1クエリ 728,388円 ／ Σ値引 = 13,985円
横照合: Σキャンペーン = アカウントレベル 382,657円
どちらも1円まで一致すること（SKILL 5e）。
"""
import csv, os
B = '/home/user/LOOana/data/daily/'
D = '2026-08-16'

SALES = {  # 商品: (gross, discounts) ※CSVの短縮名に合わせる
 'ナノガラス脱毛パッド': (191040, 1592), 'W固定スマホ車載ホルダー': (99500, 3980),
 'ムダ毛シェーバー': (90740, 0), '2WAYシートボックス': (49800, 1992),
 '形状記憶日傘': (44820, 0), '快適マジックインソール': (39800, 2388),
 '4WAY': (29880, 2241), '完全遮光・形状記憶': (29880, 0),
 '接触冷感UVパーカー': (27860, 0), '偏光・調光サングラス': (27860, 0),
 '完全遮光・接触冷感UVハット': (19920, 0), '接触冷感UVアームカバー': (15920, 0),
 '姿勢サポートチェア': (11960, 0), 'ヘアドライタオル': (11940, 796),
 'ジェットウォッシャー': (9960, 996), 'バランスケアスリッパ': (9960, 0),
 '姿勢サポートベルト': (5980, 0), '携帯電動シェーバー': (4980, 0),
 '健康サンダル': (4980, 0), '優先配送': (1608, 0),
}
assert sum(g for g, _ in SALES.values()) == 728388, sum(g for g, _ in SALES.values())
assert sum(d for _, d in SALES.values()) == 13985, sum(d for _, d in SALES.values())
print('縦照合OK: Σ商品gross = 全店 728,388円 ／ Σ値引 = 13,985円（ともに差0円）')

AD = {  # キャンペーン名はMetaの表記のまま
 'ナノガラス脱毛パッド': 87770, 'W固定スマホ車載ホルダー': 45135, '形状記憶日傘': 36915,
 '接触冷感UVパーカー': 26189, 'カタログ全部（テスト）': 25687, 'ムダ毛シェーバー': 22798,
 '偏光・調光サングラス': 20201, '完全遮光・形状記憶・晴雨兼用・UV日傘': 18139,
 '2WAYシートボックス': 17485, '完全遮光・接触冷感UVハット': 13548,
 '快適マジックインソール': 13386, '姿勢サポートチェア': 11641,
 '4WAY 取り付けOK 小型瞬間冷却ハンディファン': 10823, '接触冷感UVアームカバー': 9020,
 '5WAY腰掛けファン': 9001, 'バランスケアスリッパ': 6313,
 'ナノバブルシャワーヘッド': 4513, '高吸水・速乾ヘアドライタオル': 4093,
}
ACCOUNT = 382657
assert sum(AD.values()) == ACCOUNT, (sum(AD.values()), ACCOUNT)
print(f'横照合OK: Σキャンペーン {sum(AD.values()):,}円 = アカウント {ACCOUNT:,}円（差0円）')
print('  ※ 害虫ブロッカー・卓上冷感クーラーは消化ゼロ（停止済み）。')
print('  ※ ナノバブルシャワーヘッドは8/16日中に停止したため 4,513円の残消化あり。')

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
append(B + 'daily_ad.csv', [[D, c, v] for c, v in AD.items()])
