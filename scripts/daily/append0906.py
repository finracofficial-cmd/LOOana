# -*- coding: utf-8 -*-
"""2026-09-07 08:30 : 9/6(日)実測を追記。広告費はキャンペーン単位で取得（adset単位だと停止済みセットの残消化が欠落する）。
   ⚠️ 9/6広告費は 9/7 08:2x 取得の暫定値。確定まで+0.1%程度動く → 翌朝再取得で上書き判断する。
   （9/5広告費は 9/6 17:00 に 218,217 で確定済み・fix0905ad.py 実施済み）"""
import csv
B = 'data/daily/'
D = '2026-09-06'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 614260, 12537, 122, 136
SALES = [('ナノガラス脱毛パッド',218900,1592),('W固定スマホ車載ホルダー',107460,3980),
 ('快適マジックインソール',75620,6965),('ムダ毛シェーバー',69800,0),('バランスケアスリッパ',29880,0),
 ('温感EMSフェイシャルワンド',23920,0),('4-in-1マルチクリーナー',20940,0),('むくみ取りかっさ',15920,0),
 ('ナノバブルシャワーヘッド',13960,0),('姿勢サポートチェア',11960,0),('携帯電動シェーバー',9960,0),
 ('スマートノーズEMS美顔器',5980,0),('ジェットウォッシャー',4980,0),('2WAYシートボックス',4980,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',155220+19900),('ナノガラス脱毛パッド','黒桃',39800+3980)]
AD = {'ナノガラス脱毛パッド':96940,'W固定スマホ車載ホルダー':35941,'快適マジックインソール':32916,
 'カタログ全部（テスト）':20445,'ムダ毛シェーバー':19789,'バランスケアスリッパ':18949,
 'むくみ取りかっさ':12626,'姿勢サポートチェア':11663,'温感EMSフェイシャルワンド':11379,
 '4-in-1マルチクリーナー':11348,'ナノバブルシャワーヘッド':10282,'2WAYシートボックス':9551,
 '完全遮光・接触冷感UVハット':16}
ACCT = 291845
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC, sum(d for _,_,d in SALES)
assert sum(g for _,_,g in VARIANT) == 218900
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
S = STORE_GROSS - STORE_DISC
QK = [(44,757),(11,740),(27,1069),(19,677),(10,2798),(6,1304),(4,2079),(3,2961),(4,1120),
      (2,2255),(2,1811),(2,1743),(1,2453),(1,1259),(1,1943)]
K = sum(q*c for q,c in QK); QTY = sum(q for q,_ in QK)
assert QTY >= STORE_ITEMS, (QTY, STORE_ITEMS)   # 販売数 ≥ net_items_sold（差=返品数1点）
print(f'\n9/6 全店: 実売 {S:,} / 注文 {STORE_ORDERS} / 販売数 {QTY}（返品1点・点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f}）'
      f'/ 原価 {K:,} / 広告 {ACCT:,} / 利益 {S-K-ACCT:,} ({(S-K-ACCT)/S:.1%}) / MER {S/ACCT:.2f}')
print(f'手数料後利益 {S-K-ACCT-S*0.03436:,.0f}円 / セッション 3,752 / 全店CVR {STORE_ORDERS/3752:.2%}')
