# -*- coding: utf-8 -*-
"""11/13(金) 17:3x 今時点（0〜17時台）が偶然の範囲かを判定（CLAUDE.md 2026-11-13「偶然の範囲か」）
店全体: 同じ時刻で切った過去21日（10/23〜11/12）の最小〜最大と順位。商品別: 過去7日の同時刻の「広告費1円あたりの個数」から今日の広告費で期待される個数を出し、ポアソンで今日の個数以下（以上）になる確率"""
import os, json, math, re, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3])) for r in json.load(open(D + 'store_sales_0017.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0017.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0017.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
T = '2026-11-13'; H = [d for d in sorted(SS) if d < T]
def rank(lab, f, fm):
    xs = [f(d) for d in H]; t = f(T); lo, hi = min(xs), max(xs)
    v = '過去21日の範囲の外（' + ('下' if t < lo else '上') + '）' if (t < lo or t > hi) else '範囲内'
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(lo)}〜{fm.format(hi)}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {sum(x < t for x in xs)}/21 → {v}")
print('■ 店全体（0〜17時台・過去21日の同時刻）')
rank('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}'); rank('購入率%', lambda d: SE[d][3] / SE[d][0] * 100, '{:.2f}')
rank('クリック率%', lambda d: MA[d][2] / MA[d][1] * 100, '{:.2f}'); rank('CPM', lambda d: MA[d][0] / MA[d][1] * 1000, '{:,.0f}'); rank('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
rank('広告費', lambda d: MA[d][0], '{:,}'); rank('注文', lambda d: SS[d][1], '{}')
# 商品別
src = open(R + 'scripts/product_tabs.py').read(); g = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], g); PRICE = dict(g['PRICE']); PRICE.update({'ネックマッサージャー': 8980, '姿勢サポートチェア': 5980, '優先配送': 790})
nm = lambda t: re.sub(r'^(LOOTY|LOTTY)\s*', '', re.sub(r'【[^】]*】', '', t).strip()).strip()
U = collections.defaultdict(int)   # 注文数（CLAUDE.md: 商品別の偶然判定は注文数で）
for d, t, gr, dc, o in json.load(open(D + 'sales_prod_0017.json'))['rows']:
    n = nm(t)
    if int(gr): U[(d, n)] += int(o)
MC = {}
for l in open(D + 'meta_camp_0017.txt'):
    if l[0] != '#': p = l.strip().split(','); MC[(p[0], p[1])] = int(p[2])
P7 = [f'2026-11-{x:02d}' for x in range(6, 13)]
pois_le = lambda k, lam: sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
print('\n■ 商品別（0〜17時台）: 今日の注文数 と 今日の広告費から期待される注文数（過去7日の同時刻の 注文÷広告費 の合計比）')
for n in sorted({k[1] for k in MC if k[0] == T and MC[k] > 0}, key=lambda n: -MC[(T, n)]):
    a = MC[(T, n)]; u = U.get((T, n), 0)
    days = [d for d in P7 if MC.get((d, n), 0) >= 2000]
    if not days or n == 'カタログ全部（テスト）':
        print(f"  {n}: {u}注文・広告費 {a:,} → 比べる過去がない" + ('（全商品横断なので注文を商品に分けられない）' if n.startswith('カタログ') else '')); continue
    lam = sum(U.get((d, n), 0) for d in days) / sum(MC[(d, n)] for d in days) * a
    lo, hi = pois_le(u, lam), 1 - pois_le(u - 1, lam) if u else 1
    v = '偶然の範囲内' if min(lo, hi) >= 0.05 else ('偶然では起きにくい（少ない）' if lo < 0.05 else '偶然では起きにくい（多い）')
    print(f"  {n}: {u}注文（期待 {lam:.1f}）・この数以下になる確率 {lo:.0%}・以上 {hi:.0%} → {v}")
