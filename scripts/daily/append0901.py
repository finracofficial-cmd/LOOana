# -*- coding: utf-8 -*-
"""2026-09-02 朝の定例追記。
   ① 8/31 の広告費を data_query 再取得値で上書き（00:10取得の223,174 → 確定223,671・+497円/+0.22%）
   ② 9/1 の実測（Shopify・Meta）を追記
   ③ 予算スナップショット 2026-09-02 を追記（9/1b と同一・変更なし・244,000円/日）"""
import csv
B = 'data/daily/'

# ---------- ① 8/31 広告費の上書き（宣言済みタスク: 翌朝再取得で上書き） ----------
AD0831 = {'ナノガラス脱毛パッド':70257,'W固定スマホ車載ホルダー':32613,'快適マジックインソール':26157,
 'カタログ全部（テスト）':17082,'ムダ毛シェーバー':15945,'むくみ取りかっさ':11511,'姿勢サポートチェア':10974,
 'バランスケアスリッパ':10126,'2WAYシートボックス':9966,'ナノバブルシャワーヘッド':7555,
 'ビジュアル耳かき':5849,'完全遮光・接触冷感UVハット':5484,'偏光・調光サングラス':152}
assert sum(AD0831.values()) == 223671, sum(AD0831.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old31 = [r for r in rows if r and r[0]=='2026-08-31']
assert len(old31) == 13 and abs(sum(float(r[2]) for r in old31) - 223174) < 1
out = [r for r in rows if not (r and r[0]=='2026-08-31')]
out += [['2026-08-31', c, str(v)] for c, v in AD0831.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'8/31 広告費を上書き: 223,174 → {sum(AD0831.values()):,}（+{sum(AD0831.values())-223174}円）')

# ---------- ② 9/1 実測の追記 ----------
D = '2026-09-01'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 444410, 9008, 88, 101
SALES = [('ナノガラス脱毛パッド',155220,2587),('快適マジックインソール',59700,2388),
 ('W固定スマホ車載ホルダー',59700,796),('ムダ毛シェーバー',48860,0),('バランスケアスリッパ',29880,996),
 ('ナノバブルシャワーヘッド',20940,0),('2WAYシートボックス',19920,2241),
 ('完全遮光・接触冷感UVハット',14940,0),('むくみ取りかっさ',11940,0),('ネックマッサージャー',9980,0),
 ('姿勢サポートチェア',5980,0),('携帯電動シェーバー',4980,0),('優先配送',2370,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',95520+19900),('ナノガラス脱毛パッド','黒桃',31840+7960)]
AD = {'ナノガラス脱毛パッド':76767,'W固定スマホ車載ホルダー':33634,'快適マジックインソール':30009,
 'カタログ全部（テスト）':17106,'ムダ毛シェーバー':16377,'バランスケアスリッパ':11843,
 '姿勢サポートチェア':11820,'むくみ取りかっさ':11738,'2WAYシートボックス':7402,
 'ナノバブルシャワーヘッド':7186,'完全遮光・接触冷感UVハット':5658,'偏光・調光サングラス':126,
 'ビジュアル耳かき':56}
ACCT = 229722
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC
assert sum(g for _,_,g in VARIANT) == 155220
assert sum(AD.values()) == ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σキャンペーン = アカウント {ACCT:,} ✓')

def append(path, rows):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0] == D for r in csv.reader(f)), f'{path} に {D} が既にある'
    with open(path, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        for r in rows: w.writerow(r)
    print(f'  {path} +{len(rows)}行')
append(B+'daily_sales.csv',   [[D,n,g,d] for n,g,d in SALES])
append(B+'daily_variant.csv', [[D,n,g,v] for n,g,v in VARIANT])
append(B+'daily_ad.csv',      [[D,c,v] for c,v in AD.items()])

# ---------- ③ 予算スナップショット 9/2（変更なし・9/1b と同一） ----------
SNAP = [('ナノガラス脱毛パッド','ナノガラス脱毛パッド２',60000),
 ('ナノガラス脱毛パッド','ナノガラス脱毛パッド３（BC検証用）',20000),
 ('W固定スマホ車載ホルダー','W固定スマホ車載ホルダー',35000),
 ('快適マジックインソール','快適マジックインソール',30000),
 ('カタログ全部（テスト）','カタログ全部（テスト）',18000),
 ('ムダ毛シェーバー','ムダ毛シェーバー',17000),
 ('むくみ取りかっさ','むくみ取りかっさ',13000),
 ('姿勢サポートチェア','姿勢サポートチェア',12000),
 ('バランスケアスリッパ','バランスケアスリッパ v2',12000),
 ('2WAYシートボックス','2WAYシートボックス',8000),
 ('ナノバブルシャワーヘッド','ナノバブルシャワーヘッド - コピー',8000),
 ('完全遮光・接触冷感UVハット','完全遮光・接触冷感UVハット 0731',6000),
 ('偏光・調光サングラス','偏光・調光サングラス',5000)]
assert sum(b for _,_,b in SNAP) == 244000
p = 'data/budget-snapshots.csv'
with open(p, encoding='utf-8') as f:
    assert not any(r and r[0]=='2026-09-02' for r in csv.reader(f))
with open(p, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    for c,a,b in SNAP: w.writerow(['2026-09-02',c,a,b])
print(f'  {p} +13行（244,000円/日・変更なし。耳かきは CAMPAIGN_PAUSED のため除外）')
print(f'\n9/1 全店: 実売 {STORE_GROSS-STORE_DISC:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS} '
      f'/ 点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f} / 客単価 {(STORE_GROSS-STORE_DISC)/STORE_ORDERS:,.0f}円 '
      f'/ 広告 {ACCT:,} / MER {(STORE_GROSS-STORE_DISC)/ACCT:.2f}')
