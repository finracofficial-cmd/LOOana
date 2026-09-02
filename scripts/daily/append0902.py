# -*- coding: utf-8 -*-
"""2026-09-03 朝: ① 9/1広告費を確定値で上書き（229,722 → 230,778・+1,056円/+0.46%）② 9/2実測を追記。"""
import csv
B = 'data/daily/'

AD0901 = {'ナノガラス脱毛パッド':77047,'W固定スマホ車載ホルダー':33770,'快適マジックインソール':30140,
 'カタログ全部（テスト）':17273,'ムダ毛シェーバー':16418,'バランスケアスリッパ':11882,'姿勢サポートチェア':11958,
 'むくみ取りかっさ':11825,'2WAYシートボックス':7411,'ナノバブルシャワーヘッド':7194,
 '完全遮光・接触冷感UVハット':5678,'偏光・調光サングラス':126,'ビジュアル耳かき':56}
assert sum(AD0901.values()) == 230778, sum(AD0901.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-01']
assert len(old) == 13 and abs(sum(float(r[2]) for r in old) - 229722) < 1
out = [r for r in rows if not (r and r[0]=='2026-09-01')]
out += [['2026-09-01', c, str(v)] for c, v in AD0901.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/1 広告費を上書き: 229,722 → {sum(AD0901.values()):,}（+{sum(AD0901.values())-229722}円）')

D = '2026-09-02'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 448710, 9951, 92, 105
SALES = [('ナノガラス脱毛パッド',155220,1592),('快適マジックインソール',75620,4975),
 ('W固定スマホ車載ホルダー',67660,2388),('バランスケアスリッパ',34860,0),('ムダ毛シェーバー',27920,0),
 ('むくみ取りかっさ',23880,0),('2WAYシートボックス',19920,0),('完全遮光・接触冷感UVハット',14940,996),
 ('ナノバブルシャワーヘッド',13960,0),('偏光・調光サングラス',7960,0),
 ('温感EMSフェイシャルワンド',5980,0),('優先配送',790,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',103480+15920),('ナノガラス脱毛パッド','黒桃',31840+3980)]
AD = {'ナノガラス脱毛パッド':79337,'快適マジックインソール':38300,'W固定スマホ車載ホルダー':31203,
 'カタログ全部（テスト）':18748,'ムダ毛シェーバー':18230,'むくみ取りかっさ':13499,
 'バランスケアスリッパ':12487,'姿勢サポートチェア':12045,'2WAYシートボックス':8247,
 'ナノバブルシャワーヘッド':6997,'完全遮光・接触冷感UVハット':5519,'温感EMSフェイシャルワンド':4545,
 '偏光・調光サングラス':3758}
ACCT = 252915
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC
assert sum(g for _,_,g in VARIANT) == 155220
assert sum(AD.values()) == ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σキャンペーン = アカウント {ACCT:,} ✓')

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
print(f'\n9/2 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f} / 広告 {ACCT:,} / MER {(STORE_GROSS-STORE_DISC)/ACCT:.2f}')
