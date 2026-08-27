# -*- coding: utf-8 -*-
"""2026-08-27（木）の速報。01:44 JST時点で取得。
売上・値引・バリアント=Shopify実測 / 広告費=Meta実測（★確定前の速報値・翌朝に+0.1%程度動く）。
CSVへの追記はしない（朝の定例ビルドが確定値で行う）。"""
import runpy
g = runpy.run_path('scripts/daily/w0826.py')
S, AD, STORE, IDX, HOL, wd = g['S'], g['AD'], g['STORE'], g['IDX'], g['HOL'], g['wd']
COST, PRICE, VARC, VG = g['COST'], g['PRICE'], g['VARC'], g['VG']
PRICEBYDATE, MIXEDDAY, price_on, mixed_qty = g['PRICEBYDATE'], g['MIXEDDAY'], g['price_on'], g['mixed_qty']
ALLD = sorted(STORE)

# ---- 8/27 実測（Shopify 1クエリで取得した値。縦照合つき）----
SALES = [('ナノガラス脱毛パッド',179100,3980),('W固定スマホ車載ホルダー',115420,1592),
 ('快適マジックインソール',75620,1592),('ムダ毛シェーバー',69800,1396),('2WAYシートボックス',64740,1992),
 ('ナノバブルシャワーヘッド',34900,0),('バランスケアスリッパ',29880,996),('偏光・調光サングラス',23880,1592),
 ('姿勢サポートチェア',17940,1196),('形状記憶日傘',14940,996),('完全遮光・接触冷感UVハット',14940,996),
 ('むくみ取りかっさ',11940,0),('3D足臭リセットブラシ',11940,0),('4WAY',4980,0)]
GROSS, DISC, ORD, ITEMS = 670020, 16328, 130, 149
SESS, CART, DONE = 3145, 201, 118
assert sum(x[1] for x in SALES) == GROSS, sum(x[1] for x in SALES)
assert sum(x[2] for x in SALES) == DISC, sum(x[2] for x in SALES)
# ナノガラスのバリアント実測: 白緑(ピュアホワイト30+セージグリーン8)=38 / 黒桃(マットブラック6+ベイビーピンク1)=7
NANO = (38, 7); assert (NANO[0]+NANO[1])*3980 == 179100
AD27 = [('ナノガラス脱毛パッド',93213),('W固定スマホ車載ホルダー',40934),('快適マジックインソール',28282),
 ('ムダ毛シェーバー',19786),('カタログ全部（テスト）',18300),('2WAYシートボックス',14368),
 ('姿勢サポートチェア',12526),('バランスケアスリッパ',10527),('ナノバブルシャワーヘッド',9856),
 ('むくみ取りかっさ',9553),('完全遮光・接触冷感UVハット',8480),('3D足臭リセットブラシ',8224),
 ('偏光・調光サングラス',7194),('カタログ全部（テスト） 夏以外',1912)]
ACCT27 = 283155
assert sum(x[1] for x in AD27) == ACCT27, sum(x[1] for x in AD27)

def cost27(n, gr):
    if n == 'ナノガラス脱毛パッド': return NANO[0]*757 + NANO[1]*740
    if n == 'むくみ取りかっさ': return 3*1149          # シルバー3個（バリアント実測）
    q = gr/PRICE[n]; assert abs(q-round(q)) < 1e-6, (n, gr); return round(q)*COST[n]
NET = GROSS - DISC
CST = sum(cost27(n, gr) for n, gr, _ in SALES)
PRF = NET - CST - ACCT27
print('■ 2026-08-27（木）— Shopify実測 × Meta実測（★広告費は速報値）')
print(f'  {"実売(gross−値引)":<20}{NET:>12,}円')
print(f'  {"原価":<20}{CST:>12,}円   原価率 {CST/NET:.2%}')
print(f'  {"広告費":<20}{ACCT27:>12,}円   広告費率 {ACCT27/NET:.2%}  日予算253,000の {ACCT27/253000:.1%}')
print(f'  {"総合原価":<20}{CST+ACCT27:>12,}円')
print(f'  {"利益":<20}{PRF:>+12,}円   **利益率 {PRF/NET:.2%}**')
print(f'  {"手数料控除後利益":<20}{PRF-NET*0.03452:>+12,.0f}円   {((PRF-NET*0.03452)/NET):.2%}')
print(f'  MER {NET/ACCT27:.2f} / 分岐 {1/(1-CST/NET):.2f} / **余裕 {NET/ACCT27-1/(1-CST/NET):+.2f}**')
print(f'  注文 {ORD}件 / 点数 {ITEMS}（{ITEMS/ORD:.3f}個/注文）/ 客単価 {NET/ORD:,.0f}円')
assert abs((CST+ACCT27+PRF)-NET) < 1

print('\n■ 前日・7日平均との比較')
D26 = (542334, 146273, 231515, 164546)
D7 = [d for d in ALLD if d >= '2026-08-20']
def dcost(d):
    t = 0
    for n in S:
        if not n or d not in S[n] or not S[n][d][0]: continue
        gd = S[n][d][0]
        if n in VARC:
            for grp, gg in VG[n].get(d, {}).items():
                t += round(gg/3980)*(VARC[n][0] if grp == '白緑' else VARC[n][1])
        elif n in PRICEBYDATE:
            q = mixed_qty(gd, *MIXEDDAY[n][d]) if (n in MIXEDDAY and d in MIXEDDAY[n]) else round(gd/price_on(n, d))
            t += q*COST[n]
        else: t += round(gd/PRICE[n])*COST[n]
    return t
A7 = (sum(STORE[d] for d in D7)/7, sum(dcost(d) for d in D7)/7,
      sum(sum(AD[c].get(d, 0) for c in AD) for d in D7)/7, 0)
A7 = A7[:3] + (A7[0]-A7[1]-A7[2],)
print(f'  {"":<12}{"8/26(水)":>12}{"7日平均/日":>13}{"8/27(木)":>12}{"vs前日":>10}{"vs7日平均":>11}')
for i, nm in enumerate(['実売', '原価', '広告費', '利益']):
    v = [NET, CST, ACCT27, PRF][i]
    print(f'  {nm:<12}{D26[i]:>12,}{A7[i]:>13,.0f}{v:>12,}{v/D26[i]-1:>+10.1%}{v/A7[i]-1:>+11.1%}')
print(f'  {"利益率":<12}{D26[3]/D26[0]:>12.1%}{A7[3]/A7[0]:>13.1%}{PRF/NET:>12.1%}')

print('\n■ 3日移動平均利益（非常ブレーキ 130,000円）')
for lbl, v in [('8/23-25', (111840+133905+110183)/3), ('8/24-26', (133905+110183+164546)/3),
               ('**8/25-27**', (110183+164546+PRF)/3)]:
    print(f'  {lbl:<12}{v:>10,.0f}円  {"✅ライン上" if v >= 130000 else "🚨ライン割れ"}')

print('\n■ 同曜日（木）との比較')
th = [d for d in ALLD[-30:] if wd(d) == '木' and d not in HOL]
sa = sum(STORE[d] for d in th)/len(th)
print(f'  直近30日の木曜平均 {sa:,.0f}円（n={len(th)}）→ 8/27は {NET/sa-1:+.1%}')
print(f'  ⚠️ 木曜平均は夏物が生きていた頃を含むので分母が汚染されている。7日平均比のほうを見る')

print('\n■ CVR（Shopify実測）')
print(f'  セッション {SESS:,} / カート追加 {CART}（{CART/SESS:.2%}）/ 注文 {ORD} → **全店CVR {ORD/SESS:.2%}**')
for lbl, s_, o_ in [('8/25', 3280, 99), ('8/26', 2733, 105), ('8/27', SESS, ORD)]:
    print(f'  {lbl}  セッション {s_:,} / 注文 {o_} = {o_/s_:.2%}')

print('\n■ カタログ（8/27・注文はShopify注文UTMの実測）')
CO, CN, CORD = 18300, 1912, 6
gpo = (NET-CST)/ORD
print(f'  消化 旧 {CO:,} ＋ 夏以外 {CN:,}（10:47に停止）= {CO+CN:,}円')
print(f'  ラストクリック注文 **{CORD}件**（旧6 / 夏以外0）')
print(f'  CPA(注文) {(CO+CN)/CORD:,.0f}円 vs 全店の1注文あたり粗利 {gpo:,.0f}円 → 余裕 **{gpo-(CO+CN)/CORD:+,.0f}円** '
      f'{"✅黒字" if (CO+CN)/CORD < gpo else "🚨赤字"}')
print(f'  注文シェア {CORD/ORD:.2%} ÷ 消化シェア {(CO+CN)/ACCT27:.2%} = **{(CORD/ORD)/((CO+CN)/ACCT27):.2f}倍**（8/29基準0.8）')
print(f'\n  ★昨日10:47時点は「3件 / 7,403円 = CPA 2,468円（旧のみ1,860円）」だった。')
print(f'    10:45以降は 3件 / {CO+CN-7403:,}円 = CPA {(CO+CN-7403)/3:,.0f}円 で分岐超え。')
print(f'    **朝の1,860円は終日では持たなかった。終日CPAは {(CO+CN)/CORD:,.0f}円**')
