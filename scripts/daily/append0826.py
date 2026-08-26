# -*- coding: utf-8 -*-
"""2026-08-26 の実測をCSVへ追記。値引は正の値。冪等。"""
import csv, os
B = '/home/user/LOOana/data/daily/'
SALES = [
    ('ナノガラス脱毛パッド',       147260, 3383),
    ('快適マジックインソール',       95520, 6368),
    ('ムダ毛シェーバー',            90740, 1396),
    ('W固定スマホ車載ホルダー',      71640,    0),
    ('2WAYシートボックス',         39840, 2241),
    ('むくみ取りかっさ',            27860,  796),
    ('バランスケアスリッパ',         24900,    0),
    ('完全遮光・接触冷感UVハット',   14940,  996),
    ('ナノバブルシャワーヘッド',      13960,    0),
    ('ヘアドライタオル',             7960,  796),
    ('偏光・調光サングラス',          7960,    0),
    ('姿勢サポートチェア',            5980,    0),
    ('4WAY',                       4980,    0),
    ('3D足臭リセットブラシ',          3980,    0),
    ('優先配送',                      790,    0),
]
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 558310, 15976, 105, 125
assert sum(g for _, g, _ in SALES) == STORE_GROSS, ('縦照合(売上)', sum(g for _, g, _ in SALES))
assert sum(d for _, _, d in SALES) == STORE_DISC,  ('縦照合(値引)', sum(d for _, _, d in SALES))

AD = [   # ナノガラスは広告セット2本（60,000+20,000）をキャンペーンで合算
    ('ナノガラス脱毛パッド', 53259 + 17214), ('W固定スマホ車載ホルダー', 33005),
    ('快適マジックインソール', 19084), ('ムダ毛シェーバー', 15223),
    ('カタログ全部（テスト）', 13778), ('2WAYシートボックス', 11592),
    ('姿勢サポートチェア', 11317), ('むくみ取りかっさ', 10496),
    ('バランスケアスリッパ', 10073), ('3D足臭リセットブラシ', 9676),
    ('完全遮光・接触冷感UVハット', 7874), ('ナノバブルシャワーヘッド', 7627),
    ('偏光・調光サングラス', 7287), ('カタログ全部（テスト） 夏以外', 4010),
]
AD_TOTAL = 231515   # アカウントレベル実測。Σキャンペーンと差0円
assert sum(c for _, c in AD) == AD_TOTAL, ('広告費 縦照合', sum(c for _, c in AD))

VARIANT = [   # ピュアホワイト95,520＋セージグリーン15,920 / マットブラック27,860＋ベイビーピンク7,960
    ('ナノガラス脱毛パッド', '白緑', 95520 + 15920),
    ('ナノガラス脱毛パッド', '黒桃', 27860 + 7960),
]
assert sum(g for _, _, g in VARIANT) == 147260, 'ナノガラスのバリアント合計'
# むくみ取りかっさ 8/26: シルバー6個(1,149円) + ピンク1個(858円) → 加重原価 (6*1149+858)/7 = 1,107.4円

D = '2026-08-26'

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
print(f'8/26 全店 gross {STORE_GROSS:,} / 値引 {STORE_DISC:,} / 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS}')
print(f'8/26 Meta広告費 {AD_TOTAL:,}（日予算250,000の{AD_TOTAL/250000*100:.1f}%）')
print('★形状記憶日傘は CAMPAIGN_PAUSED（消化0円）。8/25に停止済みで確定')
print('★ヘアドライタオル（3,980円・原価985円）が広告ゼロで2個。8/16以来2回目')
