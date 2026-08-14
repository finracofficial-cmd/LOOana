# -*- coding: utf-8 -*-
"""2026-08-14 の実測を daily_sales.csv / daily_ad.csv に追記する（冪等）。

Shopify: FROM sales SHOW gross_sales, discounts GROUP BY product_title SINCE/UNTIL 2026-08-14
Meta   : ds_id=FA act_1124340806289175, date=2026-08-14, timezone=Asia/Tokyo
広告費は四捨五入で書き込む（SKILL 2026-08-01 の決定）。
"""
import csv, os
B = '/home/user/LOOana/data/daily/'
D = '2026-08-14'

SALES = {  # 商品: (gross, discounts)  ※CSVの短縮名に合わせる
 'ナノガラス脱毛パッド': (167160, 796), 'W固定スマホ車載ホルダー': (91540, 1592),
 '害虫ブロッカー': (63680, 4975), '形状記憶日傘': (54780, 1992), '4WAY': (39840, 4233),
 '完全遮光・接触冷感UVハット': (34860, 0), 'ムダ毛シェーバー': (27920, 0),
 '偏光・調光サングラス': (23880, 796), '接触冷感UVパーカー': (19920, 0),
 '姿勢サポートチェア': (17940, 0), '快適マジックインソール': (15920, 0),
 '接触冷感UVアームカバー': (15920, 796), '2WAYシートボックス': (9960, 0),
 'バランスケアスリッパ': (9960, 0), '5WAY腰掛けファン': (4980, 0),
 '完全遮光・形状記憶': (4980, 0), '優先配送': (2144, 0),
}
AD = {  # キャンペーン名はMetaの表記のまま
 'W固定スマホ車載ホルダー': 34215, 'カタログ全部（テスト）': 20672, 'ナノガラス脱毛パッド': 76197,
 'バランスケアスリッパ': 4629, 'ムダ毛シェーバー': 18347, '偏光・調光サングラス': 14857,
 '卓上冷感クーラー': 735, '姿勢サポートチェア': 9621, '完全遮光・形状記憶・晴雨兼用・UV日傘': 16390,
 '完全遮光・接触冷感UVハット': 13366, '害虫ブロッカー': 35314, '形状記憶日傘': 36507,
 '快適マジックインソール': 10182, '接触冷感UVアームカバー': 7985, '接触冷感UVパーカー': 30141,
 '2WAYシートボックス': 16049, '4WAY 取り付けOK 小型瞬間冷却ハンディファン': 9148,
 '5WAY腰掛けファン': 8969,
}
# 全店1クエリの実測と突き合わせる（縦照合）
assert sum(g for g, _ in SALES.values()) == 605384, sum(g for g, _ in SALES.values())
assert sum(d for _, d in SALES.values()) == 15180, sum(d for _, d in SALES.values())

def append(path, rows, key_cols):
    existing = list(csv.reader(open(path, encoding='utf-8')))
    header, body = existing[0], existing[1:]
    have = {tuple(r[:2]) for r in body}
    added = 0
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for r in rows:
            if tuple(r[:2]) in have:      # 同じ日付×名前が既にあれば書かない（冪等）
                continue
            w.writerow(r); added += 1
    return added, len(body)

n1, before1 = append(B + 'daily_sales.csv', [[D, n, g, dc] for n, (g, dc) in SALES.items()], 2)
n2, before2 = append(B + 'daily_ad.csv',    [[D, c, v] for c, v in AD.items()], 2)
print(f'daily_sales.csv  +{n1}行（既存{before1}行）')
print(f'daily_ad.csv     +{n2}行（既存{before2}行）')
print(f'\n{D} 全店 gross {sum(g for g,_ in SALES.values()):,} / 値引 {sum(d for _,d in SALES.values()):,} '
      f'/ 実売 {sum(g-d for g,d in SALES.values()):,}')
print(f'{D} 広告費合計 {sum(AD.values()):,}')
