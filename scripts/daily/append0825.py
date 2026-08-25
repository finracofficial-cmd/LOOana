# -*- coding: utf-8 -*-
"""2026-08-25 の実測をCSVへ追記。値引は正の値。冪等。"""
import csv, os
B = '/home/user/LOOana/data/daily/'
SALES = [
    ('ナノガラス脱毛パッド',       171140, 7363),
    ('W固定スマホ車載ホルダー',     75620, 1592),
    ('快適マジックインソール',       43780, 1592),
    ('2WAYシートボックス',         39840,  996),
    ('姿勢サポートチェア',          35880, 1196),
    ('ムダ毛シェーバー',            34900,    0),
    ('完全遮光・接触冷感UVハット',   29880,  996),
    ('むくみ取りかっさ',            15920,    0),
    ('形状記憶日傘',               14940,    0),
    ('湯上がりガーゼワンピース',      11960, 1196),
    ('偏光・調光サングラス',         11940,    0),
    ('バランスケアスリッパ',          9960,    0),
    ('3D足臭リセットブラシ',          7960,    0),
    ('4WAY',                       4980,    0),
    ('接触冷感UVアームカバー',        3980,    0),
    ('優先配送',                     790,    0),
]
STORE_GROSS, STORE_DISC, STORE_ORDERS = 513470, 14931, 99
assert sum(g for _, g, _ in SALES) == STORE_GROSS, ('縦照合(売上)', sum(g for _, g, _ in SALES))
assert sum(d for _, _, d in SALES) == STORE_DISC,  ('縦照合(値引)', sum(d for _, _, d in SALES))

AD = [
    ('ナノガラス脱毛パッド', 81250), ('W固定スマホ車載ホルダー', 32968),
    ('快適マジックインソール', 22161), ('カタログ全部（テスト）', 17337),
    ('ムダ毛シェーバー', 15211), ('2WAYシートボックス', 14297),
    ('姿勢サポートチェア', 12929), ('形状記憶日傘', 11988),
    ('むくみ取りかっさ', 11772), ('3D足臭リセットブラシ', 11709),
    ('完全遮光・接触冷感UVハット', 8527), ('偏光・調光サングラス', 8273),
    ('バランスケアスリッパ', 7318), ('ナノバブルシャワーヘッド', 2043),
    ('カタログ全部（テスト） 夏以外', 155),
]
AD_TOTAL = 257938
assert sum(c for _, c in AD) == AD_TOTAL, ('広告費合計', sum(c for _, c in AD))

VARIANT = [   # ピュアホワイト99,500+セージグリーン43,780 / マットブラック15,920+ベイビーピンク11,940
    ('ナノガラス脱毛パッド', '白緑', 99500 + 43780),
    ('ナノガラス脱毛パッド', '黒桃', 15920 + 11940),
]
assert sum(g for _, _, g in VARIANT) == 171140, 'ナノガラスのバリアント合計'
# むくみ取りかっさ 8/25 は シルバー 15,920 のみ（4個）→ 原価は加重1,120円ではなくシルバー1,149円

D = '2026-08-25'

def append(path, header, rows):
    exists = os.path.exists(path)
    if exists:
        with open(path, encoding='utf-8') as f:
            if any(l.startswith(D + ',') for l in f):
                print(f'  skip (既に{D}あり): {os.path.basename(path)}'); return 0
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if not exists: w.writerow(header)
        for r in rows: w.writerow(r)
    return len(rows)

n1 = append(B + 'daily_sales.csv',   ['date','name','gross','disc'],      [[D,n,g,d] for n,g,d in SALES])
n2 = append(B + 'daily_ad.csv',      ['date','campaign','cost'],          [[D,c,v] for c,v in AD])
n3 = append(B + 'daily_variant.csv', ['date','name','cost_group','gross'],[[D,n,cg,g] for n,cg,g in VARIANT])
print(f'追記: sales {n1}行 / ad {n2}行 / variant {n3}行')
print(f'8/25 全店 gross {STORE_GROSS:,} / 値引 {STORE_DISC:,} / 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS}')
print(f'8/25 Meta広告費 {AD_TOTAL:,}（当時の日予算258,000の{AD_TOTAL/258000*100:.1f}%）')
print('★新規キャンペーン2本を daily_ad.csv に追加: ナノバブルシャワーヘッド / カタログ全部（テスト） 夏以外')
