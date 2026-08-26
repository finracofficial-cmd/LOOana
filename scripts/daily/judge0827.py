# -*- coding: utf-8 -*-
"""2026-08-27 の判定材料。CSV実測のみ（w0826.py 経由）。"""
import runpy, datetime, collections
g = runpy.run_path('scripts/daily/w0826.py')
S, AD, STORE, IDX = g['S'], g['AD'], g['STORE'], g['IDX']
COST, PRICE, MAP, HOL, wd = g['COST'], g['PRICE'], g['MAP'], g['HOL'], g['wd']
ALLD = sorted(STORE)

def ad(n, days): return sum(AD[MAP.get(n, n)].get(d, 0) for d in days)
def sale(n, days): return sum(S[n][d][0]-S[n][d][1] for d in days if d in S[n])
def gross(n, days): return sum(S[n][d][0] for d in days if d in S[n])
PRICEBYDATE, MIXEDDAY = g['PRICEBYDATE'], g['MIXEDDAY']
price_on, mixed_qty, VG, VARC = g['price_on'], g['mixed_qty'], g['VG'], g['VARC']
def qty(n, days):
    if n in VARC:   # バリアントで原価が違う商品は日次バリアントCSVから積む
        t = 0
        for d in days:
            for grp, gg in VG[n].get(d, {}).items():
                x = gg/3980 if n == 'ナノガラス脱毛パッド' else gg/(6980 if grp == '3本' else 5980)
                t += round(x)
        return t
    if n in PRICEBYDATE:
        t = 0
        for d in days:
            gd = S[n][d][0] if d in S[n] else 0
            if not gd: continue
            if n in MIXEDDAY and d in MIXEDDAY[n]: t += mixed_qty(gd, *MIXEDDAY[n][d]); continue
            x = gd/price_on(n, d); assert abs(x-round(x)) < 1e-6, (n, d, gd); t += round(x)
        return t
    q = gross(n, days)/PRICE[n]; assert abs(q-round(q))<1e-6, (n, gross(n,days)); return round(q)
def unitcost(n, days):
    if n in VARC:
        t = 0
        for d in days:
            for grp, gg in VG[n].get(d, {}).items():
                x = round(gg/3980) if n == 'ナノガラス脱毛パッド' else round(gg/(6980 if grp == '3本' else 5980))
                t += x*(VARC[n][0] if grp in ('白緑','3本') else VARC[n][1])
        return t
    return qty(n, days)*COST[n]
def profit(n, days): return sale(n, days) - unitcost(n, days) - ad(n, days)
def days_back(k, end='2026-08-26'):
    i = ALLD.index(end); return ALLD[i-k+1:i+1]

print('■ 全店 日次利益と3日移動平均（非常ブレーキ 130,000円）')
ACCT = lambda d: sum(AD[c].get(d, 0) for c in AD)
DP = {}
for d in ALLD:
    net = STORE[d]
    cost = sum(g['K30'].get(n,0) for n in [])  # 使わない
DAY = {}
for d in ALLD[-12:]:
    net = STORE[d]
    c = 0
    for n in S:
        if d not in S[n] or not S[n][d][0]: continue
        c += unitcost(n, [d])
    DAY[d] = None if c is None else net - c - ACCT(d)
ks = [d for d in ALLD[-12:]]
print(f'  {"日":<14}{"実売":>10}{"広告":>10}{"利益":>10}{"利益率":>8}{"3日移動平均":>12}')
for i, d in enumerate(ks):
    p = DAY[d]
    m3 = [DAY[x] for x in ks[max(0,i-2):i+1]]
    a3 = sum(m3)/len(m3) if all(v is not None for v in m3) else None
    print(f'  {d[5:]}({wd(d)}){"":<6}{STORE[d]:>10,}{ACCT(d):>10,.0f}'
          f'{(f"{p:+,.0f}" if p is not None else "—"):>10}{(f"{p/STORE[d]:.1%}" if p else "—"):>8}'
          f'{(f"{a3:,.0f}" if a3 else "—"):>12}')

print('\n■ 判定① 快適マジックインソール — 増額判定（基準: 1日あたり利益 ≥ 23,589円）')
D7 = days_back(7)
p7 = profit('快適マジックインソール', D7)
print(f'  7日(8/20-26) 実売 {sale("快適マジックインソール",D7):,} / 販売 {qty("快適マジックインソール",D7)}個'
      f' / 広告 {ad("快適マジックインソール",D7):,.0f} / 利益 {p7:+,.0f}')
print(f'  **1日あたり利益 {p7/7:,.0f}円 vs 基準 23,589円 → {"✅合格" if p7/7>=23589 else "🚨不合格"}**')
for k in (3, 5, 7):
    dd = days_back(k); pp = profit('快適マジックインソール', dd)
    net = sale('快適マジックインソール', dd); a = ad('快適マジックインソール', dd)
    be = 1/(1-unitcost('快適マジックインソール',dd)/net)
    tg = 1/(1-unitcost('快適マジックインソール',dd)/net-0.35)
    print(f'  {k}日窓 MER {net/a:.2f} / 分岐 {be:.2f} / 目標 {tg:.2f} / 余裕 {net/a-be:+.2f}'
          f' / 1日あたり利益 {pp/k:,.0f}円')

print('\n■ 判定② ムダ毛シェーバー — 8/24の 20,000→17,000 減額の効果判定')
PRE = ['2026-08-21','2026-08-22','2026-08-23']; POST = ['2026-08-24','2026-08-25','2026-08-26']
for lbl, dd in [('減額前 8/21-23', PRE), ('減額後 8/24-26', POST)]:
    net = sale('ムダ毛シェーバー', dd); q = qty('ムダ毛シェーバー', dd); a = ad('ムダ毛シェーバー', dd)
    p = net - unitcost('ムダ毛シェーバー', dd) - a
    print(f'  {lbl}  実売 {net:>8,} / {q:>3}個 / 広告 {a:>8,.0f} / MER {net/a:>5.2f}'
          f' / 利益 {p:>+9,.0f} / 1日あたり {p/3:>+8,.0f}')
dn = sale('ムダ毛シェーバー', POST) - sale('ムダ毛シェーバー', PRE)
da = ad('ムダ毛シェーバー', POST) - ad('ムダ毛シェーバー', PRE)
print(f'  Δ広告 {da:+,.0f}円 / Δ実売 {dn:+,.0f}円 → 削った帯の限界MER {dn/da:.2f}（分岐1.67）')
print(f'  ※ |Δ広告費| {abs(da):,.0f}円 は3日で {abs(da)/3:,.0f}円/日。3,000円/日の測定下限に'
      f'{"届いている" if abs(da)/3>=3000 else "届いていない → 判定保留"}')

print('\n■ 判定③ ナノバブルシャワーヘッド 中間ゲート（8/28・3日累計 Shopify実注文 ≥ 5件）')
for d in days_back(4):
    q = qty('ナノバブルシャワーヘッド', [d]) if d in S['ナノバブルシャワーヘッド'] else 0
    print(f'  {d[5:]}({wd(d)})  販売 {q}個 / 広告 {ad("ナノバブルシャワーヘッド",[d]):,.0f}円')
d3 = days_back(3)
print(f'  8/24-26 累計 {qty("ナノバブルシャワーヘッド",d3)}個 / 広告 {ad("ナノバブルシャワーヘッド",d3):,.0f}円')

print('\n■ 判定④ ナノガラス コピー修正（8/28・点数/注文 1.06 → 1.15）')
print(f'  7日 販売数 {qty("ナノガラス脱毛パッド",D7)}個 ／ 注文数はShopify注文UTMではなく商品別ordersが必要（別クエリ）')

print('\n■ 8/26に配信ゼロだったキャンペーン（7日窓に残消化があるもの）')
for c in sorted(AD, key=lambda x: -sum(AD[x].get(d,0) for d in D7)):
    a7 = sum(AD[c].get(d,0) for d in D7); a1 = AD[c].get('2026-08-26', 0)
    if a7 > 0 and a1 == 0:
        last = max((d for d in AD[c] if AD[c][d] > 0), default='—')
        print(f'  {c:<28} 7日消化 {a7:>9,.0f}円 / 最終消化 {last[5:]} → **停止済み**')
