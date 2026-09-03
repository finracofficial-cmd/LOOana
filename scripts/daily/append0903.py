# -*- coding: utf-8 -*-
"""2026-09-04 朝: ① 9/2広告費を確定値で上書き（252,915 → 252,984・+69円/+0.03%）② 9/3実測を追記。"""
import csv
B = 'data/daily/'

AD0902 = {'ナノガラス脱毛パッド':79343,'快適マジックインソール':38327,'W固定スマホ車載ホルダー':31203+7,
 'カタログ全部（テスト）':18756,'ムダ毛シェーバー':18230,'むくみ取りかっさ':13504,'バランスケアスリッパ':12487,
 '姿勢サポートチェア':12047,'2WAYシートボックス':8253,'ナノバブルシャワーヘッド':6997,
 '完全遮光・接触冷感UVハット':5519,'温感EMSフェイシャルワンド':4551,'偏光・調光サングラス':3760}
assert sum(AD0902.values()) == 252984, sum(AD0902.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-02']
assert len(old) == 13 and abs(sum(float(r[2]) for r in old) - 252915) < 1
out = [r for r in rows if not (r and r[0]=='2026-09-02')]
out += [['2026-09-02', c, str(v)] for c, v in AD0902.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/2 広告費を上書き: 252,915 → {sum(AD0902.values()):,}（+{sum(AD0902.values())-252915}円）')

D = '2026-09-03'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 530260, 11304, 103, 117
SALES = [('ナノガラス脱毛パッド',175120,1592),('W固定スマホ車載ホルダー',71640,2587),
 ('快適マジックインソール',67660,796),('ムダ毛シェーバー',48860,0),('ナノバブルシャワーヘッド',34900,0),
 ('2WAYシートボックス',29880,1992),('バランスケアスリッパ',24900,0),
 ('温感EMSフェイシャルワンド',23920,1196),('壁掛けディスペンサー',20940,3141),
 ('むくみ取りかっさ',7960,0),('偏光・調光サングラス',7960,0),('姿勢サポートチェア',5980,0),
 ('携帯電動シェーバー',4980,0),('高吸水・速乾ヘアドライタオル',3980,0),('優先配送',1580,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',127360+7960),('ナノガラス脱毛パッド','黒桃',31840+7960),
 ('壁掛けディスペンサー','3本',20940)]
AD = {'ナノガラス脱毛パッド':78989,'快適マジックインソール':37100,'W固定スマホ車載ホルダー':32451,
 'カタログ全部（テスト）':19498,'ムダ毛シェーバー':17728,'むくみ取りかっさ':14146,
 'バランスケアスリッパ':12237,'姿勢サポートチェア':11995,'温感EMSフェイシャルワンド':11230,
 'ナノバブルシャワーヘッド':10033,'2WAYシートボックス':8432,'完全遮光・接触冷感UVハット':6152,
 '偏光・調光サングラス':4768}
ACCT = 264759
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC
assert sum(g for _,_,g in VARIANT) == 175120 + 20940
assert sum(AD.values()) == ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σキャンペーン = アカウント {ACCT:,} ✓')
# 9/3 の4WAYは返品1件のみ（gross 0）→ A案により売上行は作らない

def append(path, rows_):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == D for r in csv.reader(f)), f'{path} に {D} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows_: w.writerow(r)
    print(f'  {path} +{len(rows_)}行')
append(B+'daily_sales.csv',   [[D,n,g,d] for n,g,d in SALES])
append(B+'daily_variant.csv', [[D,n,g,v] for n,g,v in VARIANT])
append(B+'daily_ad.csv',      [[D,c,v] for c,v in AD.items()])
print(f'\n9/3 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f} / 広告 {ACCT:,} / MER {(STORE_GROSS-STORE_DISC)/ACCT:.2f}')
