# -*- coding: utf-8 -*-
"""Meta画面のCPA と Shopify実購入ベースのCPA を突き合わせる。7日(8/18-24) ＋ かっさ/足クサの日別。"""
import pickle, math
R = pickle.load(open('/tmp/rep0824w.pkl', 'rb'))
MAP = R['MAP']; INV = {v: k for k, v in MAP.items()}
N7, K7, A7, Q7 = R['N7'], R['K7'], R['A7'], R['Q7']

# 7日(8/18-24) Meta実測: cost, 購入数, 計上売上
META = {'ナノガラス脱毛パッド':(559791,243,1028742),'W固定スマホ車載ホルダー':(245253,98,442772),
'形状記憶日傘':(200878,52,288718),'カタログ全部（テスト）':(141166,37,200898),'ムダ毛シェーバー':(137388,37,253440),
'快適マジックインソール':(123811,67,344865),'偏光・調光サングラス':(101086,31,133522),'2WAYシートボックス':(96954,30,180019),
'姿勢サポートチェア':(77916,24,196443),'完全遮光・接触冷感UVハット':(70578,28,158556),
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(47379,10,56425),'3D足臭リセットブラシ':(43334,13,58108),
'接触冷感UVアームカバー':(39723,9,41989),'バランスケアスリッパ':(38200,15,82018),'接触冷感UVパーカー':(19070,6,23880),
'むくみ取りかっさ':(12921,8,38208),'完全遮光・形状記憶・晴雨兼用・UV日傘':(2641,1,4980)}
# 7日 Shopify実注文（ShopifyQL GROUP BY product_title 実測）
SORD = {'ナノガラス脱毛パッド':260,'W固定スマホ車載ホルダー':115,'快適マジックインソール':69,'形状記憶日傘':47,
'ムダ毛シェーバー':36,'2WAYシートボックス':34,'偏光・調光サングラス':34,'完全遮光・接触冷感UVハット':30,
'姿勢サポートチェア':24,'4WAY':16,'バランスケアスリッパ':15,'3D足臭リセットブラシ':13,
'接触冷感UVアームカバー':10,'完全遮光・形状記憶':10,'むくみ取りかっさ':8,'接触冷感UVパーカー':7}
STORE_ORD, STORE_NET, STORE_COST = 722, sum(N7.values()), sum(K7.values())
GPO_STORE = (STORE_NET - STORE_COST) / STORE_ORD              # 全店の粗利/注文

print('■ 7日(8/18-24) CPA突き合わせ — Meta画面の数字 vs Shopify実購入')
print(f'  {"商品":<24}{"広告費":>9}{"Meta購入":>9}{"SH注文":>8}{"Meta/SH":>9}'
      f'{"Meta CPA":>10}{"実CPA":>9}{"分岐CPA":>9}{"倍率":>7}  判定')
ROWS = []
for cp, (cost, mp, mv) in sorted(META.items(), key=lambda x: -x[1][0]):
    n = INV.get(cp, cp)
    if cp == 'カタログ全部（テスト）':
        mcpa = cost / mp; gpo = GPO_STORE; scpa = None
        ratio = gpo / mcpa
        print(f'  {"カタログ全部（テスト）":<24}{cost:>9,}{mp:>9}{"帰属不能":>8}{"—":>9}'
              f'{mcpa:>10,.0f}{"—":>9}{gpo:>9,.0f}{ratio:>7.2f}  '
              f'{"🚨分岐割れ（Metaの甘い計上で測ってもマイナス）" if ratio < 1 else "要注意"}')
        ROWS.append((cp, cost, mp, None, mcpa, None, gpo, ratio)); continue
    so = SORD.get(n)
    if not so: continue
    net = N7.get(n, 0); k = K7.get(n, 0)
    gpo = (net - k) / so                                       # 分岐CPA(注文) = 粗利/注文
    scpa = cost / so; mcpa = cost / mp if mp else None
    ratio = gpo / scpa
    v = ('🚨全負け圏' if ratio <= 1.3 else ('✅全勝圏' if ratio > 2.0 else '🔧中間'))
    print(f'  {n:<24}{cost:>9,}{mp:>9}{so:>8}{mp/so:>9.0%}'
          f'{mcpa:>10,.0f}{scpa:>9,.0f}{gpo:>9,.0f}{ratio:>7.2f}  {v}')
    ROWS.append((n, cost, mp, so, mcpa, scpa, gpo, ratio))
tm = sum(r[2] for r in ROWS if r[2]); ts = sum(r[3] for r in ROWS if r[3])
print(f'\n  Σ Meta計上購入 {tm}件（カタログ37含む） vs 出稿中16商品のShopify注文 {ts}件 / 全店注文 {STORE_ORD}件')
print(f'  → Metaは商品キャンペーンで {sum(r[2] for r in ROWS if r[3])}件しか計上できておらず、'
      f'出稿中16商品のShopify {ts}件に対し {sum(r[2] for r in ROWS if r[3])/ts-1:+.0%}')
print(f'  全店の粗利/注文（＝カタログの分岐CPA）= {GPO_STORE:,.0f}円')

print('\n■ むくみ取りかっさ — 日別（広告費はMeta実測・注文はShopify実測）')
KA = [('8/23', 1819, 0, 0), ('8/24', 11102, 8, 8), ('8/25(14:47)', 6062, 0, 0)]
ct = ot = 0
for d, c, mp, so in KA:
    ct += c; ot += so
    cpa = f'{c/so:,.0f}円' if so else '—（注文ゼロ）'
    print(f'  {d:<12} 消化 {c:>7,}円 / Meta購入 {mp} / Shopify注文 {so} / CPA {cpa}')
print(f'  累計       消化 {ct:>7,}円 / Shopify注文 {ot} / 実CPA {ct/ot:,.0f}円 / 分岐CPA 3,450円 → 倍率 {3450/(ct/ot):.2f}')

print('\n■ 3D足臭リセットブラシ — 日別')
AS = [('8/23', 10322, 3, 3), ('8/24', 10408, 3, 3), ('8/25(14:47)', 5335, 0, 0)]
ct2 = ot2 = 0
for d, c, mp, so in AS:
    ct2 += c; ot2 += so
    cpa = f'{c/so:,.0f}円' if so else '—（注文ゼロ）'
    print(f'  {d:<12} 消化 {c:>7,}円 / Meta購入 {mp} / Shopify注文 {so} / CPA {cpa}')
gpo_as = (N7['3D足臭リセットブラシ'] - K7['3D足臭リセットブラシ']) / 13
print(f'  7日        消化 43,334円 / Shopify注文 13 / 実CPA {43334/13:,.0f}円 / 分岐CPA {gpo_as:,.0f}円 → 倍率 {gpo_as/(43334/13):.2f}')

print('\n■ 「今日ゼロ」は珍しいことか（二項分布・昨日のCVRが続く前提）')
for nm, clk, p0 in [('むくみ取りかっさ', 44, 8/90), ('3D足臭リセットブラシ', 22, 13/173),
                    ('偏光・調光サングラス', 41, 34/1143)]:
    exp = clk * p0; p0z = (1 - p0) ** clk
    print(f'  {nm:<22} 今日のクリック {clk:>3} / 想定CVR {p0:.1%} / 期待注文 {exp:.1f}件 / '
          f'ゼロになる確率 {p0z:.1%}  {"← 珍しい" if p0z < 0.05 else "← 普通に起きる"}')

print('\n■ カタログ全部（テスト）の中身')
c, mp, mv = META['カタログ全部（テスト）']
imp, clk = 33711, 1270
print(f'  消化 {c:,}円 / インプ {imp:,} / クリック {clk:,} / Meta購入 {mp}件 / Meta計上売上 {mv:,}円')
print(f'  CTR {clk/imp:.2%}（店内でも高い方） / CPM {c/imp*1000:,.0f}円 / CPC {c/clk:,.0f}円 / Meta CVR {mp/clk:.2%}')
print(f'  Meta基準ROAS {mv/c:.2f}（全店MER 1.84 を下回る）')
na = META['ナノガラス脱毛パッド']
print(f'  比較 ナノガラス: CPM {na[0]/282813*1000:,.0f}円 / CTR {6536/282813:.2%} / Shopify CVR {260/6536:.2%}')
print(f'  → カタログはCTRは高いがCPMが {c/imp*1000/(na[0]/282813*1000):.1f}倍。'
      f'クリックは取れているのに1件あたりが高すぎる')
