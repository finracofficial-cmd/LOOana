# -*- coding: utf-8 -*-
"""2026-08-28 朝の判定材料。CSV実測のみ（w0828.py 経由）。"""
import runpy
g = runpy.run_path('scripts/daily/w0828.py')
S, AD, STORE, IDX = g['S'], g['AD'], g['STORE'], g['IDX']
COST, PRICE, MAP, HOL, wd = g['COST'], g['PRICE'], g['MAP'], g['HOL'], g['wd']
ALLD = sorted(STORE)
PRICEBYDATE, MIXEDDAY = g['PRICEBYDATE'], g['MIXEDDAY']
price_on, mixed_qty, VG, VARC = g['price_on'], g['mixed_qty'], g['VG'], g['VARC']

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
def profit(n, days): return sale(n, days) - unitcost(n, days) - ad(n, days)
def days_back(k, end='2026-08-28'):
    i = ALLD.index(end); return ALLD[i-k+1:i+1]
ACCT = lambda d: sum(AD[c].get(d, 0) for c in AD)

print('■ 全店 日次利益と3日移動平均（非常ブレーキ 130,000円）')
DAY = {}
for d in ALLD[-12:]:
    c = sum(unitcost(n, [d]) for n in S if d in S[n] and S[n][d][0])
    DAY[d] = STORE[d] - c - ACCT(d)
ks = ALLD[-12:]
print(f'  {"日":<14}{"実売":>10}{"広告":>10}{"利益":>10}{"利益率":>8}{"3日移動平均":>12}')
for i, d in enumerate(ks):
    p = DAY[d]
    m3 = [DAY[x] for x in ks[max(0, i-2):i+1]]
    a3 = sum(m3)/len(m3) if len(m3) == 3 else None
    mark = '' if a3 is None else ('  🚨' if a3 < 130000 else '  ✅')
    print(f'  {d[5:]}({wd(d)}){"":<6}{STORE[d]:>10,}{ACCT(d):>10,.0f}{p:>+10,.0f}'
          f'{p/STORE[d]:>8.1%}{(f"{a3:,.0f}" if a3 else "—"):>12}{mark}')

print('\n■ 判定① ナノガラス2 単独（8/28宣言: 3日連続で倍率<1.00なら60,000→40,000）')
print('  ※ 広告セット単位の帰属は注文UTMが要る。ここでは商品単位の日次倍率で代用し、')
print('    セット別は別途 utm クエリで確認する')
for d in days_back(4):
    q = qty('ナノガラス脱毛パッド', [d]); a = ad('ナノガラス脱毛パッド', [d])
    net = sale('ナノガラス脱毛パッド', [d]); c = unitcost('ナノガラス脱毛パッド', [d])
    print(f'  {d[5:]}({wd(d)})  {q:>3}点 / 広告 {a:>7,.0f} / 実CPA {a/q:>6,.0f} / '
          f'分岐CPA {(net-c)/q:>6,.0f} → 倍率 {((net-c)/q)/(a/q):.2f}')

print('\n■ 判定② 2WAY・サングラス・ナノバブル（8/28宣言: 2日連続で購入ゼロなら即-50%）')
for n in ('2WAYシートボックス', '偏光・調光サングラス', 'ナノバブルシャワーヘッド'):
    row = f'  {n:<22}'
    for d in days_back(3):
        q = qty(n, [d]) if d in S[n] else 0
        row += f'  {d[5:]}: {q}点'
    print(row + ('   → 🚨2日連続ゼロ' if all((qty(n,[d]) if d in S[n] else 0)==0
                 for d in days_back(2)) else '   → ✅該当せず'))

print('\n■ 3窓判定（3日/5日/7日・すべて8/27終端）')
NAMES = sorted({n for n in S if ad(n, days_back(7)) > 0}, key=lambda n: -ad(n, days_back(7)))
print(f'  {"商品":<24}{"3日":>26}{"5日":>26}{"7日":>26}  判定')
for n in NAMES:
    cells, mers, mgs, ok = [], [], [], True
    for k in (3, 5, 7):
        dd = days_back(k); net = sale(n, dd); a = ad(n, dd); c = unitcost(n, dd)
        if not a or not net: cells.append('—'); ok = False; continue
        b = 1/(1-c/net); t = 1/(1-c/net-0.35) if (1-c/net-0.35) > 0 else None
        m = net/a; mers.append((m, b, t)); mgs.append(m-b)
        cells.append(f'MER{m:5.2f} 分岐{b:4.2f} 余裕{m-b:+5.2f}')
    if not ok or len(mers) < 3:
        print(f'  {n:<24}' + ''.join(f'{c:>26}' for c in cells) + '  データ不足')
        continue
    if all(m < b for m, b, t in mers): j = '🚨 停止/−50%（3窓とも分岐割れ）'
    elif all(g < 0.30 for g in mgs): j = '⚠️ −25%（3窓とも余裕<0.30）'
    elif all(t and m >= t for m, b, t in mers): j = '🚀 増額候補（3窓とも目標超え・要消化率）'
    else: j = '据え置き'
    print(f'  {n:<24}' + ''.join(f'{c:>26}' for c in cells) + f'  {j}')

print('\n■ 8/27に配信ゼロだったキャンペーン（7日窓に残消化があるもの）')
D7 = days_back(7)
for c in sorted(AD, key=lambda x: -sum(AD[x].get(d, 0) for d in D7)):
    a7 = sum(AD[c].get(d, 0) for d in D7); a1 = AD[c].get('2026-08-28', 0)
    if a7 > 0 and a1 == 0:
        last = max((d for d in AD[c] if AD[c][d] > 0), default='—')
        print(f'  {c:<28} 7日消化 {a7:>9,.0f}円 / 最終消化 {last[5:]} → **停止済み**')
