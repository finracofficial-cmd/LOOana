# -*- coding: utf-8 -*-
"""2026-08-24 の実測をCSVへ追記する。値引は正の値で書く（既存の慣習）。冪等: 既に8/24があれば何もしない。"""
import csv, io, os
B = '/home/user/LOOana/data/daily/'

# --- Shopify 実測 2026-08-24（GROUP BY product_title・1クエリの結果をそのまま転記）---
SALES = [  # (短縮名, gross, discounts>0)
    ('ナノガラス脱毛パッド',      131340, 4179),
    ('W固定スマホ車載ホルダー',   107460, 3980),
    ('快適マジックインソール',     67660, 5174),
    ('姿勢サポートチェア',         47840, 3887),
    ('2WAYシートボックス',         39840, 3237),
    ('むくみ取りかっさ',           39800, 1592),
    ('偏光・調光サングラス',       23880,  796),
    ('バランスケアスリッパ',       19920,    0),
    ('完全遮光・接触冷感UVハット', 19920,  996),
    ('3D足臭リセットブラシ',       15920,  796),
    ('ムダ毛シェーバー',           13960,    0),
    ('形状記憶日傘',                9960,    0),
    ('4WAY',                        9960,    0),
    ('携帯電動シェーバー',          4980,    0),
    ('優先配送',                    1580,    0),
]
STORE_GROSS, STORE_DISC, STORE_ORDERS = 554020, 24637, 100   # 全店1クエリの実測
assert sum(g for _, g, _ in SALES) == STORE_GROSS, ('縦照合(売上)', sum(g for _, g, _ in SALES))
assert sum(d for _, _, d in SALES) == STORE_DISC,  ('縦照合(値引)', sum(d for _, _, d in SALES))

# --- Meta 実測 2026-08-24（キャンペーン別）---
AD = [
    ('ナノガラス脱毛パッド', 76320), ('W固定スマホ車載ホルダー', 34537),
    ('快適マジックインソール', 22266), ('形状記憶日傘', 18767),
    ('ムダ毛シェーバー', 17768), ('カタログ全部（テスト）', 17133),
    ('姿勢サポートチェア', 12112), ('2WAYシートボックス', 11667),
    ('むくみ取りかっさ', 11102), ('偏光・調光サングラス', 10962),
    ('3D足臭リセットブラシ', 10408), ('完全遮光・接触冷感UVハット', 8200),
    ('バランスケアスリッパ', 5699), ('4WAY 取り付けOK 小型瞬間冷却ハンディファン', 0),
]
AD_TOTAL = 256941
assert sum(c for _, c in AD) == AD_TOTAL, ('広告費合計', sum(c for _, c in AD))

# --- バリアント別（原価が色で違う商品のみ）---
VARIANT = [  # ピュアホワイト71640+セージグリーン31840 / マットブラック15920+ベイビーピンク11940
    ('ナノガラス脱毛パッド', '白緑', 71640 + 31840),
    ('ナノガラス脱毛パッド', '黒桃', 15920 + 11940),
]
assert sum(g for _, _, g in VARIANT) == 131340, 'ナノガラスのバリアント合計'
# 壁掛けディスペンサーは 8/24 の売上ゼロ（商品別クエリに出現せず）→ 行なし

D = '2026-08-24'

def append(path, header, rows):
    exists = os.path.exists(path)
    if exists:
        with open(path, encoding='utf-8') as f:
            if any(l.startswith(D + ',') for l in f):
                print(f'  skip (既に{D}あり): {os.path.basename(path)}')
                return 0
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(header)
        for r in rows:
            w.writerow(r)
    return len(rows)

n1 = append(B + 'daily_sales.csv',   ['date', 'name', 'gross', 'disc'],
            [[D, n, g, d] for n, g, d in SALES])
n2 = append(B + 'daily_ad.csv',      ['date', 'campaign', 'cost'],
            [[D, c, v] for c, v in AD])
n3 = append(B + 'daily_variant.csv', ['date', 'name', 'cost_group', 'gross'],
            [[D, n, cg, g] for n, cg, g in VARIANT])
print(f'追記: sales {n1}行 / ad {n2}行 / variant {n3}行')
print(f'8/24 全店 gross {STORE_GROSS:,} / 値引 {STORE_DISC:,} / 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS}')
print(f'8/24 Meta広告費 {AD_TOTAL:,}（日予算256,000の{AD_TOTAL/256000*100:.1f}%）')
