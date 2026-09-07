# -*- coding: utf-8 -*-
"""2026-09-08 00:30 : 9/7(月)実測を追記。
   ⚠️ 広告費は今回「広告セット合算」を採用した。data_query のキャンペーン単位集計は丸めで
      アカウント合計と27円ズレたが、adset合算だと差0円で一致したため。
      （姿勢チェア 9,019→9,042 / ナノバブル 6,812→6,813 / 2WAY 6,807→6,810 が丸めの差）
   9/6広告費は 9/8 00:2x に 291,924 で確定済み（fix0906ad.py 実施済み）。"""
import csv
B = 'data/daily/'
D = '2026-09-07'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 487840, 9405, 96, 108
SALES = [('ナノガラス脱毛パッド',187060,3184),('快適マジックインソール',55720,3184),
 ('W固定スマホ車載ホルダー',47760,796),('バランスケアスリッパ',44820,2241),('ムダ毛シェーバー',34900,0),
 ('4-in-1マルチクリーナー',27920,0),('温感EMSフェイシャルワンド',17940,0),('2WAYシートボックス',14940,0),
 ('壁掛けディスペンサー',13960,0),('姿勢サポートチェア',11960,0),('伸縮ガラスクリーナー',11940,0),
 ('むくみ取りかっさ',11940,0),('ナノバブルシャワーヘッド',6980,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',115420+23880),('ナノガラス脱毛パッド','黒桃',35820+11940),
 ('壁掛けディスペンサー','3本',13960)]
# 広告セット合算（アカウント 217,183 と差0円）
AD = {'ナノガラス脱毛パッド':52740+15394,'W固定スマホ車載ホルダー':24711,'快適マジックインソール':21861,
 'カタログ全部（テスト）':17112,'ムダ毛シェーバー':15071,'バランスケアスリッパ':13421,
 '4-in-1マルチクリーナー':12386,'温感EMSフェイシャルワンド':10385,'むくみ取りかっさ':9360,
 '姿勢サポートチェア':9042,'ナノバブルシャワーヘッド':6813,'2WAYシートボックス':6810,
 '伸縮ガラスクリーナー':2077}
ACCT = 217183
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC, sum(d for _,_,d in SALES)
assert sum(g for n,_,g in VARIANT if n=='ナノガラス脱毛パッド') == 187060
assert sum(AD.values()) == ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σ広告セット = アカウント {ACCT:,} ✓')

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
QK = [(35,757),(12,740),(14,677),(12,1069),(9,1304),(5,2798),(4,2961),(3,2079),(3,1943),
      (2,2528),(2,1811),(3,1143),(3,1120),(1,2255)]
K = sum(q*c for q,c in QK); QTY = sum(q for q,_ in QK)
assert QTY == STORE_ITEMS, (QTY, STORE_ITEMS)   # 返品0なので一致するはず
print(f'\n9/7 全店: 実売 {S:,} / 注文 {STORE_ORDERS} / 販売数 {QTY}（点数/注文 {QTY/STORE_ORDERS:.3f}）'
      f'/ 原価 {K:,} / 広告 {ACCT:,} / 利益 {S-K-ACCT:,} ({(S-K-ACCT)/S:.1%}) / MER {S/ACCT:.2f}')
print(f'手数料後利益 {S-K-ACCT-S*0.03436:,.0f}円 / セッション 2,787 / 全店CVR {STORE_ORDERS/2787:.2%}')
print('※ 伸縮ガラスクリーナーの原価は保守側の1,143円（グレー）で計上。実際はブルー1,120×2＋グレー1,143×1＝3,383円で46円の過大')
