# -*- coding: utf-8 -*-
"""8/14の落ち込みの中身、8/15の今時点、そして出血している商品が単日の話か窓の話か。"""
import csv, collections, datetime, math, runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path('/home/user/LOOana/scripts/adhoc/day0815.py')
S, AD, COST, PRICE, MAP, STORE, ad = ns['S'], ns['AD'], ns['COST'], ns['PRICE'], ns['MAP'], ns['STORE'], ns['ad']
acct = lambda ds: sum(sum(AD[c].get(d, 0) for c in AD) for d in ds)

# ── 8/14 を1週間前の同じ曜日（8/07 金）と比べて、どこが落ちたかを分解する ──
def day(d):
    q = sum(round(v[d][0] / PRICE[n]) for n, v in S.items() if n in PRICE and d in v and v[d][0])
    return STORE[d], q, acct([d])
ORD = {'2026-08-07': 173, '2026-08-14': 120}      # Shopify実測（TIMESERIES day の orders）
print('■ 8/14(金) を 8/07(金) と比べる ── 何が落ちたのか')
a, b = '2026-08-07', '2026-08-14'
na, qa, ca = day(a); nb, qb, cb = day(b)
oa, ob = ORD[a], ORD[b]
rows = [('実売', na, nb), ('広告費', ca, cb), ('注文数', oa, ob), ('点数', qa, qb),
        ('点数/注文', qa/oa, qb/ob), ('単価/点', na/qa, nb/qb), ('AOV(実売/注文)', na/oa, nb/ob)]
for lbl, x, y in rows:
    f = ',.3f' if '/' in lbl and '点数/' in lbl else ',.0f'
    print(f"  {lbl:<16}{x:>10{f}} → {y:>10{f}}   {y/x-1:>+7.1%}")
# 対数分解: 売上 = 注文数 × 点数/注文 × 単価/点
tot = math.log(nb/na)
parts = [('注文数', math.log(ob/oa)), ('点数/注文', math.log((qb/ob)/(qa/oa))), ('単価/点', math.log((nb/qb)/(na/qa)))]
print(f"\n  売上{nb/na-1:+.1%} の内訳（対数分解）")
for lbl, v in parts:
    print(f"    {lbl:<10}{v/tot:>6.1%} を説明（{math.exp(v)-1:+.1%}）")
print(f"  ＝ 落ち込みのほぼ全部が「注文数」。まとめ買いも単価もほとんど動いていない。")
print(f"\n  広告費は {ca:,.0f} → {cb:,.0f}（{cb/ca-1:+.1%}）＝ ほぼ据え置き")
print(f"  なのに注文が {oa} → {ob} なので、CPA が {ca/oa:,.0f}円 → {cb/ob:,.0f}円（{(cb/ob)/(ca/oa)-1:+.1%}）")

# ── 8/15 の今時点（同じ時刻で切って比べる。着地の予測はしない） ──
H = {  # JST日付: [(JST時, gross, disc, items, orders)]  ShopifyQL TIMESERIES hour 実測
 '2026-08-12': [(0,12940,0,3,3),(1,7960,0,2,2),(2,3980,0,1,1),(3,0,0,0,0),(4,4980,0,1,1),(5,3980,0,1,1),(6,40356,3584,10,5)],
 '2026-08-13': [(0,12940,0,3,3),(1,6980,0,1,1),(2,3980,0,1,1),(3,0,0,0,0),(4,3980,0,1,1),(5,27416,796,7,5),(6,27880,2241,6,3)],
 '2026-08-14': [(0,3980,0,1,1),(1,23900,996,5,4),(2,0,0,0,0),(3,0,0,0,0),(4,0,0,0,0),(5,33840,1792,8,6),(6,23880,796,6,5)],
 '2026-08-15': [(0,24416,796,7,5),(1,13940,0,3,3),(2,3980,0,1,1),(3,3980,0,1,1),(4,11940,1791,3,1),(5,0,0,0,0),(6,4980,0,1,1)],
}
print('\n■ 8/15 の今時点（各日 0:00〜07:00 JST で切って同時点比較。取得は 06:24 JST）')
print(f"  {'日付':<12}{'曜':<3}{'実売':>9}{'注文':>5}{'点数':>5}{'点数/注文':>10}")
WD = '月火水木金土日'
res = {}
for d, hs in H.items():
    net = sum(g - dc for _, g, dc, _, _ in hs); it = sum(i for *_, i, _ in hs); od = sum(o for *_, o in hs)
    res[d] = (net, it, od)
    w = WD[datetime.date(*map(int, d.split('-'))).weekday()]
    print(f"  {d:<12}{w:<3}{net:>9,}{od:>5}{it:>5}{it/od:>10.3f}")
n0, i0, o0 = res['2026-08-14']; n1, i1, o1 = res['2026-08-15']
print(f"\n  昨日の同時点比  実売 {n1/n0-1:+.1%} / 注文 {o1/o0-1:+.1%} / 点数per注文 {(i1/o1)/(i0/o0)-1:+.1%}")
print(f"  ⚠️ 注文{o1}件しかない時間帯の比較なので、ここから1日を判断してはいけない。")

# ── 出血している商品は単日の話か、窓でも続いているか ──
D1 = ['2026-08-14']; D3 = ['2026-08-12','2026-08-13','2026-08-14']
D7 = [f'2026-08-{i:02d}' for i in range(8, 15)]
print('\n■ 8/14に赤字だった商品 ── 単日の事故か、続いているか')
print(f"  {'商品':<20}{'前日利益':>10}{'3日利益':>10}{'3日MER':>8}{'7日利益':>10}{'7日MER':>8}{'分岐':>6}")
def blk(n, ds):
    g = sum(S[n][d][0] for d in ds if d in S[n]); dc = sum(S[n][d][1] for d in ds if d in S[n])
    if not g: return 0, 0, 0
    q = round(g / PRICE[n]); c = ad(n, ds); net = g - dc
    return net - q * COST[n] - c, (net / c if c else 0), c
for n in ['接触冷感UVパーカー','完全遮光・形状記憶','2WAYシートボックス','5WAY腰掛けファン','ムダ毛シェーバー']:
    p1, _, _ = blk(n, D1); p3, m3, _ = blk(n, D3); p7, m7, _ = blk(n, D7)
    br = 1 / (1 - COST[n] / PRICE[n])
    print(f"  {n:<20}{p1:>+10,.0f}{p3:>+10,.0f}{m3:>8.2f}{p7:>+10,.0f}{m7:>8.2f}{br:>6.2f}")
bleed = sum(blk(n, D1)[0] for n in ['接触冷感UVパーカー','完全遮光・形状記憶','2WAYシートボックス','5WAY腰掛けファン','ムダ毛シェーバー'])
print(f"\n  8/14 のこの5商品の合計 {bleed:+,.0f}円。全体利益 +72,293円 に対してこれだけ削られている。")
