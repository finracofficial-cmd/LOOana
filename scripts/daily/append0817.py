# -*- coding: utf-8 -*-
"""2026-08-17 の実測を daily_sales.csv / daily_ad.csv へ追記する（冪等）。

Shopify: FROM sales SHOW gross_sales, discounts, net_items_sold, returns, orders
         GROUP BY product_title SINCE 2026-08-17 UNTIL 2026-08-17（graphql_query 経由）
Meta   : ds_id=FA / act_1124340806289175 / timezone=Asia/Tokyo / date=2026-08-17

縦照合: Σ商品gross = 全店1クエリ 508,216円 ／ Σ値引 = 15,430円
横照合: Σキャンペーン = アカウントレベル 275,961円
"""
import csv, os
B = '/home/user/LOOana/data/daily/'
D = '2026-08-17'

SALES = {
 'ナノガラス脱毛パッド': (131340, 1592), 'W固定スマホ車載ホルダー': (83580, 1592),
 '形状記憶日傘': (64740, 4233), '快適マジックインソール': (43780, 3184),
 '2WAYシートボックス': (39840, 2241), 'ムダ毛シェーバー': (27920, 0),
 '偏光・調光サングラス': (27860, 1592), '接触冷感UVパーカー': (23880, 0),
 '4WAY': (14940, 0), 'バランスケアスリッパ': (14940, 0),
 '完全遮光・接触冷感UVハット': (14940, 996), '姿勢サポートチェア': (11960, 0),
 '接触冷感UVアームカバー': (7960, 0), '優先配送': (536, 0),
}
assert sum(g for g, _ in SALES.values()) == 508216, sum(g for g, _ in SALES.values())
assert sum(d for _, d in SALES.values()) == 15430, sum(d for _, d in SALES.values())
print('縦照合OK: Σ商品gross = 全店 508,216円 ／ Σ値引 = 15,430円（ともに差0円）')

AD = {
 'ナノガラス脱毛パッド': 65938, 'W固定スマホ車載ホルダー': 31879, '形状記憶日傘': 28625,
 '接触冷感UVパーカー': 19402, 'カタログ全部（テスト）': 19128, 'ムダ毛シェーバー': 16591,
 '偏光・調光サングラス': 13467, '2WAYシートボックス': 12377,
 '完全遮光・形状記憶・晴雨兼用・UV日傘': 10474, '快適マジックインソール': 10345,
 '完全遮光・接触冷感UVハット': 9895, '姿勢サポートチェア': 8567,
 '4WAY 取り付けOK 小型瞬間冷却ハンディファン': 7488, '接触冷感UVアームカバー': 6908,
 '高吸水・速乾ヘアドライタオル': 6571, 'バランスケアスリッパ': 4947,
 '5WAY腰掛けファン': 3359,
}
ACCOUNT = 275961
assert sum(AD.values()) == ACCOUNT, (sum(AD.values()), ACCOUNT)
print(f'横照合OK: Σキャンペーン {sum(AD.values()):,}円 = アカウント {ACCOUNT:,}円（差0円）')
print('  ※ 5WAY腰掛けファンは8/17日中に停止したため 3,359円の残消化あり。')
print('  ※ 完全遮光日傘は 10,474円 消化して注文ゼロ。ヘアドライタオルも 6,571円で注文ゼロ。')

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
