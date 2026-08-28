# -*- coding: utf-8 -*-
"""2026-08-27 の実測をCSVへ追記。値引は正の値。冪等。
広告費は 2026-08-28 07時に再取得した確定値（01:44の速報 283,155 から +187円 / +0.066%）。"""
import csv, os
B = '/home/user/LOOana/data/daily/'
SALES = [
    ('ナノガラス脱毛パッド',       179100, 3980),
    ('W固定スマホ車載ホルダー',    115420, 1592),
    ('快適マジックインソール',      75620, 1592),
    ('ムダ毛シェーバー',           69800, 1396),
    ('2WAYシートボックス',        64740, 1992),
    ('ナノバブルシャワーヘッド',     34900,    0),
    ('バランスケアスリッパ',        29880,  996),
    ('偏光・調光サングラス',        23880, 1592),
    ('姿勢サポートチェア',         17940, 1196),
    ('形状記憶日傘',              14940,  996),
    ('完全遮光・接触冷感UVハット',  14940,  996),
    ('むくみ取りかっさ',           11940,    0),
    ('3D足臭リセットブラシ',        11940,    0),
    ('4WAY',                     4980,    0),
]
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 670020, 16328, 130, 149
assert sum(g for _, g, _ in SALES) == STORE_GROSS, ('縦照合(売上)', sum(g for _, g, _ in SALES))
assert sum(d for _, _, d in SALES) == STORE_DISC,  ('縦照合(値引)', sum(d for _, _, d in SALES))
# ★8/27は優先配送の売上がゼロ（アタッチ率0%）

AD = [   # ナノガラスは広告セット2本（71,861+21,383）をキャンペーンで合算
    ('ナノガラス脱毛パッド', 71861 + 21383), ('W固定スマホ車載ホルダー', 40955),
    ('快適マジックインソール', 28288), ('ムダ毛シェーバー', 19839),
    ('カタログ全部（テスト）', 18336), ('2WAYシートボックス', 14374),
    ('姿勢サポートチェア', 12527), ('バランスケアスリッパ', 10527),
    ('ナノバブルシャワーヘッド', 9860), ('むくみ取りかっさ', 9553),
    ('完全遮光・接触冷感UVハット', 8480), ('3D足臭リセットブラシ', 8253),
    ('偏光・調光サングラス', 7194), ('カタログ全部（テスト） 夏以外', 1912),
]
AD_TOTAL = 283342   # アカウントレベル実測。Σキャンペーンと差0円
assert sum(c for _, c in AD) == AD_TOTAL, ('広告費 縦照合', sum(c for _, c in AD))

VARIANT = [   # ピュアホワイト119,400＋セージグリーン31,840 / マットブラック23,880＋ベイビーピンク3,980
    ('ナノガラス脱毛パッド', '白緑', 119400 + 31840),
    ('ナノガラス脱毛パッド', '黒桃', 23880 + 3980),
]
assert sum(g for _, _, g in VARIANT) == 179100, 'ナノガラスのバリアント合計'
# むくみ取りかっさ 8/27: シルバー3個のみ（原価1,149円）。CSVは加重平均1,120円で計上（差 −87円）

D = '2026-08-27'

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
print(f'8/27 全店 gross {STORE_GROSS:,} / 値引 {STORE_DISC:,} / 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS}')
print(f'8/27 Meta広告費 {AD_TOTAL:,}（日予算253,000の{AD_TOTAL/253000*100:.1f}%）')
print('★速報(01:44) 283,155 → 確定 283,342（+187円 / +0.066%）。許容±0.1%内')
print('★形状記憶日傘は CAMPAIGN_PAUSED（消化0円）。優先配送は8/27の売上ゼロ')
