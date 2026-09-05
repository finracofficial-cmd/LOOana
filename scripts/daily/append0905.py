# -*- coding: utf-8 -*-
"""2026-09-06 00:10  ※広告費はキャンペーン単位で取得（adset単位だと停止済みセットの残消化67円が欠落する）
   : 9/5実測を追記。
   ⚠️ 9/5広告費は 9/6 00:02 取得の暫定値。確定まで+0.1%程度動く → 明朝再取得で上書きする。
   （9/4広告費は 9/5 13:06 に 257,498 で確定済み・fix0904ad.py 実施済み）"""
import csv
B = 'data/daily/'
D = '2026-09-05'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 543620, 9155, 106, 117
SALES = [('ナノガラス脱毛パッド',187060,2388),('快適マジックインソール',83580,4975),
 ('ムダ毛シェーバー',48860,0),('バランスケアスリッパ',44820,996),('ナノバブルシャワーヘッド',27920,0),
 ('W固定スマホ車載ホルダー',27860,0),('姿勢サポートチェア',23920,0),('むくみ取りかっさ',23880,796),
 ('2WAYシートボックス',14940,0),('4-in-1マルチクリーナー',13960,0),('温感EMSフェイシャルワンド',11960,0),
 ('形状記憶日傘',9960,0),('卓上冷感クーラー',5980,0),('携帯電動シェーバー',4980,0),
 ('ビジュアル耳かき',4980,0),('5WAY腰掛けファン',4980,0),('偏光・調光サングラス',3980,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',107460+23880),('ナノガラス脱毛パッド','黒桃',39800+15920)]
AD = {'ナノガラス脱毛パッド':53092+20794,'W固定スマホ車載ホルダー':25975,'快適マジックインソール':24490,
 'カタログ全部（テスト）':16303,'ムダ毛シェーバー':15330,'バランスケアスリッパ':12991,
 'むくみ取りかっさ':10119,'姿勢サポートチェア':7655,'2WAYシートボックス':7446,
 'ナノバブルシャワーヘッド':7299,'温感EMSフェイシャルワンド':6777,'完全遮光・接触冷感UVハット':5887,
 '4-in-1マルチクリーナー':3416,'偏光・調光サングラス':49}
ACCT = 217623
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC, sum(d for _,_,d in SALES)
assert sum(g for _,_,g in VARIANT) == 187060
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
K = 33*757 + 14*740 + 21*677 + 7*2798 + 9*1304 + 4*2255 + 7*1069 + 4*1811 + 6*1120 \
    + 3*1943 + 2*2961 + 2*2079 + 2*1309 + 1996 + 1743 + 1655 + 1848 + 893
print(f'\n9/5 全店: 実売 {S:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS}（点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f}）'
      f'/ 原価 {K:,} / 広告 {ACCT:,} / 利益 {S-K-ACCT:,} ({(S-K-ACCT)/S:.1%}) / MER {S/ACCT:.2f}')
print(f'手数料後利益 {S-K-ACCT-S*0.03436:,.0f}円 / セッション 3,217 / 全店CVR {STORE_ORDERS/3217:.2%}')
