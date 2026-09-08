# -*- coding: utf-8 -*-
"""2026-09-09 00:15 : 9/8(火)実測を追記。広告費は広告セット合算（アカウント照合 差0円）。
   ⚠️ 9/8広告費は暫定。翌朝に再取得して確認する（9/7は 217,551 で確定済み・fix0907ad.py）。"""
import csv
B='data/daily/'
D='2026-09-08'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 505590, 10550, 95, 110
SALES=[('ナノガラス脱毛パッド',95520,796),('W固定スマホ車載ホルダー',79600,1592),('ムダ毛シェーバー',62820,0),
 ('快適マジックインソール',59700,796),('伸縮ガラスクリーナー',51740,3383),('ナノバブルシャワーヘッド',27920,0),
 ('バランスケアスリッパ',19920,0),('姿勢サポートチェア',17940,1196),('むくみ取りかっさ',15920,0),
 ('2WAYシートボックス',14940,996),('3D足臭リセットブラシ',11940,1791),('完全遮光・形状記憶',9960,0),
 ('UV歯ブラシ除菌器',8980,0),('4-in-1マルチクリーナー',6980,0),('温感EMSフェイシャルワンド',5980,0),
 ('湯上がりガーゼワンピース',5980,0),('ジェットウォッシャー',4980,0),('偏光・調光サングラス',3980,0),
 ('優先配送',790,0)]
VARIANT=[('ナノガラス脱毛パッド','白緑',63680+19900),('ナノガラス脱毛パッド','黒桃',7960+3980)]
AD={'ナノガラス脱毛パッド':58061+16711,'W固定スマホ車載ホルダー':29328,'快適マジックインソール':26845,
 'カタログ全部（テスト）':18251,'ムダ毛シェーバー':16434,'バランスケアスリッパ':14681,'4-in-1マルチクリーナー':9898,
 '伸縮ガラスクリーナー':9629,'温感EMSフェイシャルワンド':9589,'姿勢サポートチェア':8241,
 'ナノバブルシャワーヘッド':7909,'2WAYシートボックス':7993,'むくみ取りかっさ':7337}
ACCT=240907
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert sum(g for _,_,g in VARIANT)==95520
assert sum(AD.values())==ACCT, sum(AD.values())
print(f'検算 Σ商品gross = 全店 {STORE_GROSS:,} ✓ / Σ値引 = {STORE_DISC:,} ✓ / Σ広告セット = アカウント {ACCT:,} ✓')
def append(path, rows_):
    with open(path, encoding='utf-8') as f:
        assert not any(r and r[0]==D for r in csv.reader(f)), f'{path} に {D} が既にある'
    with open(path,'a',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        for r in rows_: w.writerow(r)
    print(f'  {path} +{len(rows_)}行')
append(B+'daily_sales.csv',[[D,n,g,d] for n,g,d in SALES])
append(B+'daily_variant.csv',[[D,n,g,v] for n,g,v in VARIANT])
append(B+'daily_ad.csv',[[D,c,v] for c,v in AD.items()])
S=STORE_GROSS-STORE_DISC
QK=[(21,757),(3,740),(20,1069),(9,2798),(15,677),(13,1143),(4,2255),(4,1304),(3,1811),(4,1120),
    (3,1943),(3,609),(2,1309),(1,3240),(1,2961),(1,2079),(1,1968),(1,1259),(1,893),(1,0)]
K=sum(q*c for q,c in QK); QTY=sum(q for q,_ in QK)
assert QTY==STORE_ITEMS+1, (QTY,)   # 販売数111 = net_items_sold 110 + W固定の返品1点
print(f'\n9/8 全店: 実売 {S:,} / 注文 {STORE_ORDERS} / 販売数 {QTY}（返品1点・点数/注文 {QTY/STORE_ORDERS:.3f}）'
      f'/ 原価 {K:,} / 広告 {ACCT:,} / 利益 {S-K-ACCT:,} ({(S-K-ACCT)/S:.1%}) / MER {S/ACCT:.2f}')
print(f'手数料後利益 {S-K-ACCT-S*0.03436:,.0f}円 / セッション 2,739 / 全店CVR {STORE_ORDERS/2739:.2%}')
print('※ ガラスクリーナー原価は保守側1,143円×13。実測はブルー/レッド1,120×11＋グレー1,143＋グリーン1,123＝14,586円で273円の過大')
