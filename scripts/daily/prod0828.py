# -*- coding: utf-8 -*-
"""全商品のパフォーマンス推移（7日 8/21-27 vs 前7日 8/14-20 / 3日も併記）。CSV実測のみ。"""
import runpy
g = runpy.run_path('scripts/daily/w0827.py')
S, AD, STORE, MAP = g['S'], g['AD'], g['STORE'], g['MAP']
COST, PRICE, wd = g['COST'], g['PRICE'], g['wd']
PRICEBYDATE, MIXEDDAY = g['PRICEBYDATE'], g['MIXEDDAY']
price_on, mixed_qty, VG, VARC = g['price_on'], g['mixed_qty'], g['VG'], g['VARC']
ALLD = sorted(STORE)

def ad(n, days): return sum(AD[MAP.get(n, n)].get(d, 0) for d in days)
def sale(n, days): return sum(S[n][d][0]-S[n][d][1] for d in days if d in S[n])
def gross(n, days): return sum(S[n][d][0] for d in days if d in S[n])
def qty(n, days):
    if n in VARC:
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
    q = gross(n, days)/PRICE[n]; assert abs(q-round(q)) < 1e-6, (n, gross(n, days)); return round(q)
def unitcost(n, days):
    if n in VARC:
        t = 0
        for d in days:
            for grp, gg in VG[n].get(d, {}).items():
                x = round(gg/3980) if n == 'ナノガラス脱毛パッド' else round(gg/(6980 if grp == '3本' else 5980))
                t += x*(VARC[n][0] if grp in ('白緑', '3本') else VARC[n][1])
        return t
    return qty(n, days)*COST[n]

def win(end, k):
    i = ALLD.index(end); return ALLD[i-k+1:i+1]
W1 = win('2026-08-20', 7)   # 前7日 8/14-20
W2 = win('2026-08-27', 7)   # 直近7日 8/21-27
W3 = win('2026-08-27', 3)   # 直近3日 8/25-27

def block(n, days):
    net = sale(n, days)
    if net <= 0: return None
    c = unitcost(n, days); a = ad(n, days); q = qty(n, days)
    be = 1/(1-c/net) if net > c else None
    return dict(net=net, cost=c, ad=a, q=q, profit=net-c-a,
                mer=(net/a if a else None), be=be,
                slack=(net/a-be if a and be else None),
                cpa=(a/q if a and q else None), becpa=((net-c)/q if q else None))

names = sorted(S, key=lambda n: -sale(n, W2))
print('■ 全商品パフォーマンス 直近7日(8/21-27) vs 前7日(8/14-20) ※すべてCSV実測')
print(f'{"商品":<26}{"7日実売":>10}{"7日利益":>10}{"利益率":>7}{"MER":>6}{"分岐":>6}{"余裕":>7}'
      f'{"前週MER":>8}{"ΔMER":>7}  判定')
rows = []
for n in names:
    b2 = block(n, W2)
    if not b2: continue
    b1 = block(n, W1); b3 = block(n, W3)
    dm = (b2['mer']-b1['mer']) if (b2['mer'] and b1 and b1['mer']) else None
    # 判定
    if b2['mer'] is None:
        v = '広告なし（純利益商品）'
    elif b2['be'] and b2['mer'] < b2['be']:
        v = '🚨 赤字（7日で分岐割れ）'
    elif dm is not None and dm <= -0.40 and b2['slack'] is not None and b2['slack'] < 0.60:
        v = '⚠️ 悪化（余裕が縮んでいる）'
    elif b2['slack'] is not None and b2['slack'] >= 1.00 and (dm is None or dm > 0):
        v = '🚀 好調'
    else:
        v = '✅ 維持'
    rows.append((n, b1, b2, b3, dm, v))
    f = lambda v, s='{:.2f}': (s.format(v) if v is not None else '—')
    print(f'{n:<26}{b2["net"]:>10,}{b2["profit"]:>+10,}{b2["profit"]/b2["net"]:>7.1%}'
          f'{f(b2["mer"]):>6}{f(b2["be"]):>6}{f(b2["slack"], "{:+.2f}"):>7}'
          f'{f(b1["mer"] if b1 else None):>8}{f(dm, "{:+.2f}"):>7}  {v}')

print('\n■ 落ちている商品だけ抜き出し（ΔMER が負の順）')
neg = [r for r in rows if r[4] is not None and r[4] < 0]
neg.sort(key=lambda r: r[4])
print(f'{"商品":<26}{"前週MER":>8}{"今週MER":>8}{"ΔMER":>7}{"3日MER":>8}{"実売 前週→今週":>22}{"利益 前週→今週":>24}')
for n, b1, b2, b3, dm, v in neg:
    print(f'{n:<26}{b1["mer"]:>8.2f}{b2["mer"]:>8.2f}{dm:>+7.2f}'
          f'{("%.2f" % b3["mer"]) if b3 and b3["mer"] else "—":>8}'
          f'{b1["net"]:>11,}→{b2["net"]:>10,}'
          f'{b1["profit"]:>+12,}→{b2["profit"]:>+11,}')

print('\n■ CPA と分岐CPA（倍率 = 分岐CPA ÷ 実CPA。1.0未満が赤字）')
print(f'{"商品":<26}{"7日実CPA":>10}{"分岐CPA":>9}{"倍率":>7}{"前週倍率":>9}{"3日倍率":>8}')
for n, b1, b2, b3, dm, v in rows:
    if not b2['cpa']: continue
    r2 = b2['becpa']/b2['cpa']
    r1 = (b1['becpa']/b1['cpa']) if b1 and b1['cpa'] else None
    r3 = (b3['becpa']/b3['cpa']) if b3 and b3['cpa'] else None
    print(f'{n:<26}{b2["cpa"]:>10,.0f}{b2["becpa"]:>9,.0f}{r2:>7.2f}'
          f'{("%.2f" % r1) if r1 else "—":>9}{("%.2f" % r3) if r3 else "—":>8}')
