# -*- coding: utf-8 -*-
"""3窓判定（3日/5日/7日・すべて8/26終端）＋ 削減1円あたりの利益変化の頑健性チェック。"""
import runpy
g = runpy.run_path('scripts/daily/w0826.py')
S, AD, STORE = g['S'], g['AD'], g['STORE']
COST, PRICE, MAP, VARC, VG = g['COST'], g['PRICE'], g['MAP'], g['VARC'], g['VG']
PRICEBYDATE, MIXEDDAY, price_on, mixed_qty = g['PRICEBYDATE'], g['MIXEDDAY'], g['price_on'], g['mixed_qty']
ALLD = sorted(STORE); END = '2026-08-26'
W = {k: ALLD[ALLD.index(END)-k+1:ALLD.index(END)+1] for k in (3, 5, 7)}

def ad(n, d): return sum(AD[MAP.get(n, n)].get(x, 0) for x in d)
def sale(n, d): return sum(S[n][x][0]-S[n][x][1] for x in d if x in S[n])
def cst(n, d):
    if n in VARC:
        t = 0
        for x in d:
            for grp, gg in VG[n].get(x, {}).items():
                t += round(gg/3980)*(VARC[n][0] if grp == '白緑' else VARC[n][1])
        return t
    if n in PRICEBYDATE:
        q = 0
        for x in d:
            gd = S[n][x][0] if x in S[n] else 0
            if not gd: continue
            if n in MIXEDDAY and x in MIXEDDAY[n]: q += mixed_qty(gd, *MIXEDDAY[n][x]); continue
            q += round(gd/price_on(n, x))
        return q*COST[n]
    g_ = sum(S[n][x][0] for x in d if x in S[n])
    return round(g_/PRICE[n])*COST[n]

LIVE = [n for n in S if n and ad(n, ['2026-08-26']) > 0]
print('■ 3窓判定（3日/5日/7日・すべて8/26終端・稼働中のみ）')
print(f'  {"商品":<24}{"3日MER":>8}{"5日MER":>8}{"7日MER":>8}{"分岐":>7}{"目標":>7}{"7日消化率":>10}  判定')
ACT = []
BUD = {'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':35000,'快適マジックインソール':22000,
 'ムダ毛シェーバー':17000,'2WAYシートボックス':13000,'姿勢サポートチェア':12000,
 '3D足臭リセットブラシ':10000,'むくみ取りかっさ':10000,'バランスケアスリッパ':10000,
 '完全遮光・接触冷感UVハット':8000,'ナノバブルシャワーヘッド':8000,'偏光・調光サングラス':7000}
for n in sorted(LIVE, key=lambda x: -sale(x, W[7])):
    if n not in BUD: continue
    m = {}; be = tg = None
    for k in (3, 5, 7):
        d = W[k]; net = sale(n, d); a = ad(n, d)
        m[k] = net/a if a else 0
        if k == 7:
            r = cst(n, d)/net; be = 1/(1-r); tg = 1/(1-r-0.35) if r < 0.65 else float('inf')
    use = min(7, len([1 for x in W[7] if ad(n, [x]) > 0]))   # 稼働日数
    sr = ad(n, W[7])/(BUD[n]*use) if use else 0
    if all(m[k] < be for k in m): v = '🚨 停止/−50%'
    elif all(m[k]-be < 0.30 for k in m): v = '🔻 −25%'
    elif all(m[k] >= tg for k in m) and sr >= 0.95: v = '🚀 +25%'
    else: v = '⏸ 据え置き'
    print(f'  {n:<24}{m[3]:>8.2f}{m[5]:>8.2f}{m[7]:>8.2f}{be:>7.2f}{tg:>7.2f}{sr:>10.1%}  {v}')
    ACT.append((n, m, be, tg, sr, v))

print('\n■ 削減1円あたりの利益変化 = 1 − 限界MER × 粗利率（限界MER = 平均×0.6/0.7/0.8 の3端）')
print('  ★3端すべてで符号が同じときだけ動かす')
print(f'  {"商品":<24}{"7日MER":>8}{"粗利率":>8}{"×0.6":>8}{"×0.7":>8}{"×0.8":>8}  符号')
for n, m, be, tg, sr, v in sorted(ACT, key=lambda x: -x[1][7]):
    net = sale(n, W[7]); gm = 1 - cst(n, W[7])/net
    e = [1 - m[7]*f*gm for f in (0.6, 0.7, 0.8)]
    sg = '削ると+' if all(x > 0 for x in e) else ('削ると−' if all(x < 0 for x in e) else '⚠️端で逆転')
    print(f'  {n:<24}{m[7]:>8.2f}{gm:>8.1%}{e[0]:>+8.3f}{e[1]:>+8.3f}{e[2]:>+8.3f}  {sg}')

print('\n■ 増額したときの1円あたり利益 = 限界MER × 粗利率 − 1（同じ3端）')
print(f'  {"商品":<24}{"×0.6":>8}{"×0.7":>8}{"×0.8":>8}{"7日消化率":>10}  符号')
for n, m, be, tg, sr, v in sorted(ACT, key=lambda x: -x[1][7]):
    net = sale(n, W[7]); gm = 1 - cst(n, W[7])/net
    e = [m[7]*f*gm - 1 for f in (0.6, 0.7, 0.8)]
    sg = '増やすと+' if all(x > 0 for x in e) else ('増やすと−' if all(x < 0 for x in e) else '⚠️端で逆転')
    print(f'  {n:<24}{e[0]:>+8.3f}{e[1]:>+8.3f}{e[2]:>+8.3f}{sr:>10.1%}  {sg}')

print('\n■ 分岐割れが何日連続か（日次・稼働中）')
for n in ['3D足臭リセットブラシ','偏光・調光サングラス','ナノバブルシャワーヘッド','姿勢サポートチェア']:
    print(f'  {n}')
    run = 0
    for d in ALLD[-8:]:
        a = ad(n, [d]); net = sale(n, [d])
        if a <= 0:
            print(f'    {d[5:]}  広告0円'); continue
        c = cst(n, [d]); be = 1/(1-c/net) if net > c else float('inf')
        mer = net/a; ng = mer < be
        run = run+1 if ng else 0
        print(f'    {d[5:]}  実売 {net:>7,} / 広告 {a:>7,.0f} / MER {mer:>5.2f} / 分岐 {be:>5.2f}'
              f' / 利益 {net-c-a:>+8,.0f}  {"🚨割れ" if ng else "✅"}  連続{run}日')
