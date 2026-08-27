# -*- coding: utf-8 -*-
"""「最近なぜパフォーマンスが改善したか」を実測だけで分解する。
売上・値引・バリアント=Shopify実測 / 広告費=Meta実測（すべて data/daily/*.csv）。"""
import runpy, datetime, collections
g = runpy.run_path('scripts/daily/w0826.py')
S, AD, STORE, HOL, wd = g['S'], g['AD'], g['STORE'], g['HOL'], g['wd']
COST, PRICE, MAP, VARC, VG = g['COST'], g['PRICE'], g['MAP'], g['VARC'], g['VG']
PRICEBYDATE, MIXEDDAY, price_on, mixed_qty = g['PRICEBYDATE'], g['MIXEDDAY'], g['price_on'], g['mixed_qty']
ALLD = sorted(STORE)
INV = {v: k for k, v in MAP.items()}

def qty(n, d):
    gd = S[n][d][0] if d in S[n] else 0
    if not gd: return 0
    if n in PRICEBYDATE:
        if n in MIXEDDAY and d in MIXEDDAY[n]: return mixed_qty(gd, *MIXEDDAY[n][d])
        return round(gd/price_on(n, d))
    return round(gd/PRICE[n])
def cst(n, d):
    if n in VARC:
        t = 0
        for grp, gg in VG[n].get(d, {}).items():
            t += round(gg/3980)*(VARC[n][0] if grp == '白緑' else VARC[n][1])
        return t
    return qty(n, d)*COST[n]
def sale(n, d): return (S[n][d][0]-S[n][d][1]) if d in S[n] else 0
def ad(n, ds): return sum(AD[MAP.get(n, n)].get(x, 0) for x in ds)
def W(n, ds, f): return sum(f(n, x) for x in ds)
ACCT = lambda ds: sum(sum(AD[c].get(x, 0) for c in AD) for x in ds)
def day(d):
    net = STORE[d]; c = sum(cst(n, d) for n in S if n)
    return net, c, ACCT([d]), net - c - ACCT([d])

print('■ 日次利益の推移（3日移動平均つき・非常ブレーキ130,000円）')
P = {d: day(d) for d in ALLD[-20:]}
ks = list(P)
print(f'  {"日":<13}{"実売":>10}{"原価":>10}{"広告":>10}{"利益":>10}{"利益率":>8}{"3日移動平均":>12}')
for i, d in enumerate(ks):
    net, c, a, p = P[d]
    m = [P[x][3] for x in ks[max(0, i-2):i+1]]
    print(f'  {d[5:]}({wd(d)}){"":<5}{net:>10,}{c:>10,}{a:>10,.0f}{p:>+10,.0f}{p/net:>8.1%}'
          f'{sum(m)/len(m):>12,.0f}{"  🚨" if sum(m)/len(m) < 130000 else "  ✅"}')

P1 = [d for d in ALLD if '2026-08-13' <= d <= '2026-08-19']   # 前の週（谷）
P2 = [d for d in ALLD if '2026-08-20' <= d <= '2026-08-26']   # 直近の週
print(f'\n■ 底の週 {P1[0][5:]}-{P1[-1][5:]} → 直近 {P2[0][5:]}-{P2[-1][5:]}（どちらも木〜水・曜日構成は同じ）')
def agg(ds):
    net = sum(STORE[d] for d in ds); c = sum(cst(n, d) for n in S if n for d in ds)
    a = ACCT(ds); return net, c, a, net-c-a
A, B = agg(P1), agg(P2)
print(f'  {"":<16}{"底の週":>13}{"直近":>13}{"変化":>11}')
for nm, i in [('実売', 0), ('原価', 1), ('広告費', 2), ('利益', 3)]:
    print(f'  {nm:<16}{A[i]:>13,.0f}{B[i]:>13,.0f}{B[i]/A[i]-1:>+11.1%}')
for nm, f in [('利益率', lambda x: x[3]/x[0]), ('原価率', lambda x: x[1]/x[0]),
              ('広告費率', lambda x: x[2]/x[0]), ('MER', lambda x: x[0]/x[2])]:
    fa, fb = f(A), f(B)
    if nm == 'MER':
        print(f'  {nm:<16}{fa:>13.2f}{fb:>13.2f}{fb/fa-1:>+11.1%}')
    else:
        print(f'  {nm:<16}{fa:>13.2%}{fb:>13.2%}{(fb-fa)*100:>+10.2f}pt')

print('\n■ ★利益率の分解: 利益率 = 1 − 原価率 − 広告費率')
print(f'  底の週  1 − {A[1]/A[0]:.2%} − {A[2]/A[0]:.2%} = {A[3]/A[0]:.2%}')
print(f'  直近    1 − {B[1]/B[0]:.2%} − {B[2]/B[0]:.2%} = {B[3]/B[0]:.2%}')
print(f'  → 改善 {(B[3]/B[0]-A[3]/A[0])*100:+.2f}pt の内訳: '
      f'原価率の寄与 **{-(B[1]/B[0]-A[1]/A[0])*100:+.2f}pt** ／ 広告費率の寄与 **{-(B[2]/B[0]-A[2]/A[0])*100:+.2f}pt**')

print('\n■ ★商品別 利益の変化（上位・実測）')
ALLN = sorted({n for n in S if n}, key=lambda n: -(W(n, P2, sale)-W(n, P2, cst)-ad(n, P2)))
rows = []
for n in ALLN:
    pa = W(n, P1, sale)-W(n, P1, cst)-ad(n, P1)
    pb = W(n, P2, sale)-W(n, P2, cst)-ad(n, P2)
    if abs(pa) < 1 and abs(pb) < 1: continue
    rows.append((n, pa, pb, pb-pa))
print(f'  {"商品":<26}{"底の週":>11}{"直近":>11}{"変化":>11}')
for n, pa, pb, d_ in sorted(rows, key=lambda x: -x[3]):
    if abs(d_) < 8000: continue
    print(f'  {n:<26}{pa:>+11,.0f}{pb:>+11,.0f}{d_:>+11,.0f}')
print(f'  {"── 上記以外の小口 計":<26}{"":>11}{"":>11}'
      f'{sum(x[3] for x in rows if abs(x[3])<8000):>+11,.0f}')
print(f'  {"── 全商品 計":<26}{sum(x[1] for x in rows):>+11,.0f}{sum(x[2] for x in rows):>+11,.0f}'
      f'{sum(x[3] for x in rows):>+11,.0f}')
CATd = sum(AD[c].get(d, 0) for c in ('カタログ全部（テスト）','カタログ全部（テスト） 夏以外') for d in P2) \
     - sum(AD[c].get(d, 0) for c in ('カタログ全部（テスト）','カタログ全部（テスト） 夏以外') for d in P1)
print(f'  {"── カタログ広告費（横断）":<26}{"":>11}{"":>11}{-CATd:>+11,.0f}')
print(f'  {"── 全店の利益変化":<26}{A[3]:>+11,.0f}{B[3]:>+11,.0f}{B[3]-A[3]:>+11,.0f}')


print('\n■ ★3日窓でも見る（谷 8/18-20 → 直近 8/24-26）')
Q1 = ['2026-08-18','2026-08-19','2026-08-20']; Q2 = ['2026-08-24','2026-08-25','2026-08-26']
X, Y = agg(Q1), agg(Q2)
print(f'  {"":<16}{"8/18-20":>13}{"8/24-26":>13}{"変化":>12}')
for nm, i in [('実売', 0), ('原価', 1), ('広告費', 2), ('利益', 3)]:
    print(f'  {nm:<16}{X[i]:>13,.0f}{Y[i]:>13,.0f}{Y[i]/X[i]-1:>+12.1%}')
for nm, f in [('利益率', lambda x: x[3]/x[0]), ('原価率', lambda x: x[1]/x[0]), ('広告費率', lambda x: x[2]/x[0])]:
    fx, fy = f(X), f(Y)
    print(f'  {nm:<16}{fx:>13.2%}{fy:>13.2%}{(fy-fx)*100:>+10.2f}pt')
print(f'  MER  {X[0]/X[2]:.2f} → {Y[0]/Y[2]:.2f}（{(Y[0]/Y[2])/(X[0]/X[2])-1:+.1%}）')
print(f'  → 利益 {X[3]:,.0f} → {Y[3]:,.0f}円（{Y[3]/X[3]-1:+.1%}）。**実売はほぼ横ばいで、広告費だけが減った**')

print('\n■ ★全店CVR（Shopifyセッション基準・実測）')
SES = {'2026-08-13':5126,'2026-08-14':5035,'2026-08-15':4871,'2026-08-16':5349,'2026-08-17':3438,
'2026-08-18':3523,'2026-08-19':3190,'2026-08-20':3356,'2026-08-21':3120,'2026-08-22':3220,
'2026-08-23':3438,'2026-08-24':3192,'2026-08-25':3280,'2026-08-26':2733}
ORDD = {'2026-08-13':125,'2026-08-14':120,'2026-08-15':142,'2026-08-16':143,'2026-08-17':98,
'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,'2026-08-22':98,
'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105}
for lbl, ds in [('8/13-19', P1), ('8/20-26', P2)]:
    o = sum(ORDD[d] for d in ds); se = sum(SES[d] for d in ds)
    print(f'  {lbl}  注文 {o} / セッション {se:,} = **{o/se:.2%}**')
print(f'  8/26単日: 注文105 / セッション2,733 = **{105/2733:.2%}**（この2週間の最高）')

print('\n■ ★削ったのは「脂肪」か「筋肉」か — 商品別に Δ広告費 と Δ実売 を並べる')
print('  Δ実売 ÷ Δ広告費 が「削った帯の限界MER」。全店の分岐は約1.37')
print(f'  {"商品":<26}{"Δ広告費":>11}{"Δ実売":>11}{"限界MER":>9}  読み')
tot_da = tot_dn = 0
for n in sorted({x for x in S if x}, key=lambda n: ad(n, P1)-ad(n, P2), reverse=True):
    da = ad(n, P2) - ad(n, P1); dn = W(n, P2, sale) - W(n, P1, sale)
    if abs(da) < 20000: continue
    tot_da += da; tot_dn += dn
    r = dn/da if da else 0
    v = '✅削って正解（分岐割れ）' if (da < 0 and r < 1.37) else (
        '⚠️削って損（分岐超え）' if da < 0 else ('✅増やして正解' if r >= 1.37 else '⚠️増やして損'))
    print(f'  {n:<26}{da:>+11,.0f}{dn:>+11,.0f}{r:>9.2f}  {v}')
print(f'  {"── 上記の計":<26}{tot_da:>+11,.0f}{tot_dn:>+11,.0f}{tot_dn/tot_da:>9.2f}')

print('\n■ ★全店で1本の式にまとめる（8/13-19 → 8/20-26）')
dn = B[0]-A[0]; dc = B[1]-A[1]; da = B[2]-A[2]; dp = B[3]-A[3]
print(f'  Δ実売 {dn:+,.0f} ／ Δ原価 {dc:+,.0f} ／ Δ広告費 {da:+,.0f} → Δ利益 {dp:+,.0f}（検算 {dn-dc-da:+,.0f}）')
mm = dn/da; mg = (dn-dc)/dn
print(f'  削った帯の 限界MER = {dn:,.0f} ÷ {da:,.0f} = **{mm:.3f}**（全店の分岐 {A[0]/(A[0]-A[1]):.2f}）')
print(f'  削った帯の 粗利率 = ({dn:,.0f} − {dc:,.0f}) ÷ {dn:,.0f} = **{mg:.1%}**（全店平均 {1-B[1]/B[0]:.1%}）')
print(f'  → 削減1円あたりの利益 = 1 − {mm:.3f} × {mg:.3f} = **{1-mm*mg:+.3f}円**')
print(f'  → {abs(da):,.0f}円 × {1-mm*mg:.3f} = **{abs(da)*(1-mm*mg):+,.0f}円**（実測 {dp:+,.0f}円・一致）')
print('\n  ★つまり: 削って失った売上は「粗利率65.8%の売上」で、浮いた広告費は100%残る。')
print('    平均粗利率74.3%より薄い帯を削れたので、1円削るごとに0.19円の利益が残った')

print('\n■ ⚠️ この読み方の限界（正直に）')
print('  ・季節商品（4WAY・日傘・サングラス・アームカバー）は広告を削らなくても売上が落ちる時期。')
print('    Δ実売の全部を広告のせいにはできないので、これらの「限界MER」は過大に出る＝削って損に見えやすい')
print('  ・害虫ブロッカーの停止はPSE（電気用品安全法）が理由で、経済判断ではない')
print('  ・したがって商品別の限界MERは「参考」。全店の集計値のほうが信頼できる')
