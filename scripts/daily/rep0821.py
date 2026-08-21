# -*- coding: utf-8 -*-
"""2026-08-18 の定例。前日=2026-08-17。

売上・値引・バリアント = Shopify実測 ／ 広告費 = Meta実測（8/15まで揃った）
窓はすべて 8/16 終端。
"""
import csv, collections, datetime, runpy

g = runpy.run_path('scripts/daily/w0820.py')
S, AD, STORE, IDX = g['S'], g['AD'], g['STORE'], g['IDX']
N1, N3, N7, N30 = g['N1'], g['N3'], g['N7'], g['N30']
K1, K3, K7, K30 = g['K1'], g['K3'], g['K7'], g['K30']
Q1, Q7 = g['Q1'], g['Q7']
D1, D3, D7, D30, CUM = g['D1'], g['D3'], g['D7'], g['D30'], g['CUM']
NC, KC = g['NC'], g['KC']
A, ACCT, CAT, MAP = g['A'], g['ACCT'], g['CAT'], g['MAP']
COST, PRICE = g['COST'], g['PRICE']
HOL, wd = g['HOL'], g['wd']
FEE = 0.03452

print('■ ① 全体（すべて8/20終端・Shopify実測 × Meta実測）')
print(f'  {"窓":<12}{"実売":>12}{"原価":>11}{"広告費":>11}{"総合原価":>11}{"利益":>12}{"利益率":>8}'
      f'{"MER":>7}{"分岐":>7}{"余裕":>7}{"手数料後利益":>13}')
for lbl, N, K, days in [('前日8/20', N1, K1, D1), ('3日', N3, K3, D3), ('7日', N7, K7, D7),
                        ('30日', N30, K30, D30), ('当月累積', NC, KC, CUM)]:
    net = sum(N.values()); cost = sum(K.values()); ad = ACCT(days)
    pr = net - cost - ad; af = pr - net * FEE
    print(f'  {lbl:<12}{net:>12,}{cost:>11,.0f}{ad:>11,.0f}{cost+ad:>11,.0f}{pr:>+12,.0f}{pr/net:>8.1%}'
          f'{net/ad:>7.2f}{1/(1-cost/net):>7.2f}{net/ad-1/(1-cost/net):>+7.2f}{af:>+13,.0f}')
    assert abs((cost + ad + pr) - net) < 1, lbl          # 恒等式の検算

D0 = D1[0]
base = [d for d in STORE if d <= D0][-30:]
same = [d for d in base if wd(d) == wd(D0) and d not in HOL and d != D0]
sa = sum(STORE[d] for d in same) / len(same)
print(f'\n  8/20（{wd(D0)}）vs 同曜日平均 {sa:,.0f}円 → {STORE[D0]/sa-1:+.1%}（n={len(same)}）'
      f' ／ 7日平均比 {STORE[D0]/(sum(N7.values())/7)-1:+.1%}')
print(f'  曜日指数: ' + ' / '.join(f'{k}{v:.1f}' for k, v in sorted(IDX.items(), key=lambda x: -x[1])))

print('\n■ ② 商品別（7日 8/14-20）')
print(f'  {"商品":<26}{"実売":>10}{"販売数":>7}{"原価":>9}{"広告費":>10}{"利益":>10}{"利益率":>8}'
      f'{"MER":>6}{"分岐":>6}{"目標":>6}{"余裕":>7}   判定')
rows = []
for n in sorted(N7, key=lambda x: -N7[x]):
    net = N7[n]; cost = K7.get(n, 0); ad = A(D7, n); q = Q7.get(n, 0)
    if net <= 0: continue
    be = 1 / (1 - cost / net) if net > cost else float('inf')
    tg = 1 / (1 - cost / net - 0.35) if (1 - cost / net - 0.35) > 0 else float('inf')
    if ad > 0:
        mer = net / ad; yo = mer - be
        v = '🚨赤字' if yo < 0 else ('🔧テコ入れ' if yo < 0.30 else ('🚀増額候補' if mer >= tg else '✅維持'))
        print(f'  {n:<26}{net:>10,}{q:>7.0f}{cost:>9,.0f}{ad:>10,.0f}{net-cost-ad:>+10,.0f}'
              f'{(net-cost-ad)/net:>8.1%}{mer:>6.2f}{be:>6.2f}{tg:>6.2f}{yo:>+7.2f}   {v}')
        rows.append((n, net, cost, ad, mer, be, tg, yo))
    else:
        print(f'  {n:<26}{net:>10,}{q:>7.0f}{cost:>9,.0f}{0:>10}{net-cost:>+10,.0f}'
              f'{(net-cost)/net:>8.1%}{"—":>6}{be:>6.2f}{"—":>6}{"—":>7}   📦広告なし')
# 売上ゼロ・広告費のみの商品も必ず出す（取りこぼすと広告費の照合が落ちる）
ZERO = [c for c in AD if c != 'カタログ全部（テスト）' and A(D7, {v: k for k, v in MAP.items()}.get(c, c)) > 0
        and {v: k for k, v in MAP.items()}.get(c, c) not in N7]
for c in ZERO:
    n = {v: k for k, v in MAP.items()}.get(c, c); ad = A(D7, n)
    be = 1 / (1 - COST[n] / PRICE[n]); tg = 1 / (1 - COST[n] / PRICE[n] - 0.35)
    print(f'  {n:<26}{0:>10}{0:>7}{0:>9}{ad:>10,.0f}{-ad:>+10,.0f}{"—":>8}'
          f'{0.0:>6.2f}{be:>6.2f}{tg:>6.2f}{-be:>+7.2f}   ' +
          ('🆕出稿直後' if A(D1, n) > 0 else '⏹停止済（7日窓に残消化）'))
    rows.append((n, 0, 0, ad, 0.0, be, tg, -be))
print(f'  {"カタログ全部（テスト）※全商品横断":<26}{"—":>10}{"—":>7}{"—":>9}{CAT(D7):>10,.0f}{"—":>10}')
assert abs(sum(A(D7, n) for n in N7) + sum(A(D7, {v: k for k, v in MAP.items()}.get(c, c)) for c in ZERO)
           + CAT(D7) - ACCT(D7)) < 1
print(f'  ※ 広告費列の合計 = Metaアカウント実消化 {ACCT(D7):,.0f}円（検算OK）')
