# -*- coding: utf-8 -*-
"""2026-09-05 00:10: ① 9/3広告費を確定値で上書き（264,759 → 264,897・+138円）② 9/4実測を追記。
   ⚠️ 9/4広告費は 9/5 00:08 取得。確定まで+0.1%程度動く → 明朝再取得で上書き。"""
import csv
B = 'data/daily/'

AD0903 = {'ナノガラス脱毛パッド':79007,'快適マジックインソール':37117,'W固定スマホ車載ホルダー':32484,
 'カタログ全部（テスト）':19560,'ムダ毛シェーバー':17730,'むくみ取りかっさ':14149,'バランスケアスリッパ':12237,
 '姿勢サポートチェア':11997,'温感EMSフェイシャルワンド':11230,'ナノバブルシャワーヘッド':10034,
 '2WAYシートボックス':8432,'完全遮光・接触冷感UVハット':6152,'偏光・調光サングラス':4768}
assert sum(AD0903.values()) == 264897, sum(AD0903.values())
rows = list(csv.reader(open(B+'daily_ad.csv', encoding='utf-8')))
old = [r for r in rows if r and r[0]=='2026-09-03']
assert len(old) == 13 and abs(sum(float(r[2]) for r in old) - 264759) < 1
out = [r for r in rows if not (r and r[0]=='2026-09-03')]
out += [['2026-09-03', c, str(v)] for c, v in AD0903.items()]
with open(B+'daily_ad.csv', 'w', encoding='utf-8', newline='') as f:
    csv.writer(f).writerows(out)
print(f'9/3 広告費を上書き: 264,759 → {sum(AD0903.values()):,}（+{sum(AD0903.values())-264759}円）')

D = '2026-09-04'
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 381300, 8560, 74, 85
SALES = [('ナノガラス脱毛パッド',139300,3184),('W固定スマホ車載ホルダー',47760,1592),
 ('快適マジックインソール',43780,1592),('バランスケアスリッパ',29880,0),('ムダ毛シェーバー',27920,0),
 ('姿勢サポートチェア',23920,1196),('2WAYシートボックス',14940,996),('ナノバブルシャワーヘッド',13960,0),
 ('温感EMSフェイシャルワンド',11960,0),('むくみ取りかっさ',11940,0),('癒しの指圧マット',5980,0),
 ('携帯電動シェーバー',4980,0),('完全遮光・接触冷感UVハット',4980,0)]
VARIANT = [('ナノガラス脱毛パッド','白緑',67660+23880),('ナノガラス脱毛パッド','黒桃',35820+11940)]
AD = {'ナノガラス脱毛パッド':92882,'W固定スマホ車載ホルダー':29645,'快適マジックインソール':27846,
 'カタログ全部（テスト）':18448,'ムダ毛シェーバー':18109,'バランスケアスリッパ':13851,
 '温感EMSフェイシャルワンド':10757,'姿勢サポートチェア':9175,'むくみ取りかっさ':8501,
 'ナノバブルシャワーヘッド':8373,'2WAYシートボックス':8280,'完全遮光・接触冷感UVハット':6263,
 '偏光・調光サングラス':4995}
ACCT = 257125
assert sum(g for _,g,_ in SALES) == STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES) == STORE_DISC
assert sum(g for _,_,g in VARIANT) == 139300
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
K = 23*757+12*740 + 12*1069 + 11*677 + 6*1304 + 4*2798 + 4*1811 + 3*1943 + 2*2255 + 2*2079 + 3*1120 + 1648 + 1743 + 1411
S = STORE_GROSS-STORE_DISC
print(f'\n9/4 全店: 実売 {S:,} / 注文 {STORE_ORDERS} / 点数 {STORE_ITEMS}（点数/注文 {STORE_ITEMS/STORE_ORDERS:.3f}）'
      f'/ 原価 {K:,} / 広告 {ACCT:,} / 利益 {S-K-ACCT:,} ({(S-K-ACCT)/S:.1%}) / MER {S/ACCT:.2f} / 分岐 {1/(1-K/S):.2f}')
print(f'手数料後利益 {S-K-ACCT-S*0.03436:,.0f}円 / セッション3,293 / 全店CVR {74/3293:.2%}')
