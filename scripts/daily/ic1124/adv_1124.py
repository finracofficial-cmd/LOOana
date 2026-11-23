# -*- coding: utf-8 -*-
"""11/24 06時台「今日も広告効果を最大化させるためのアドバイスを幅広に」: 
① 直近7日（11/17〜23）の商品ごとの「クリック1回の値段」と「クリック1回の粗利」（＝払ってよい値段の元）
② 広告を出していない日に売れた商品（11/10〜23）
入力: w1123.py（売上・原価・広告費の積み直し）・o1123/ad_level_1026_1123.txt（Meta のリンククリック）"""
import io, contextlib, collections, csv
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, MAP, MULTI = g['A'], g['ALLD'], g['agg'], g['WIN'], g['MAP'], g['MULTI']; D7 = ALLD[-7:]
WIN['a7'] = D7; N, DC, Q, K = agg(D7, 'a7')
CL = collections.defaultdict(int); CO = collections.defaultdict(int)
for l in open('scripts/daily/o1123/ad_level_1026_1123.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(',')
    if d in D7: CL[c] += int(clk); CO[c] += int(cost)
camps = lambda n: MULTI.get(n, (MAP.get(n, n),))
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('■ ① 直近7日（11/17〜23）: クリック1回の値段 ｜ クリック1回の粗利（Shopify の 売上−値引−原価 ÷ Meta のリンククリック）｜ 倍率 1.25・1.5 で払える値段 ｜ 個数')
rows = []
for n in set(N) | {n for n in MAP if A(D7, n)}:
    a = A(D7, n); k = sum(CL[c] for c in camps(n))
    if not a or not k: continue
    gp = N.get(n, 0) - K.get(n, 0); rows.append((n, a, k, gp, Q.get(n, 0)))
for n, a, k, gp, q in sorted(rows, key=lambda r: -r[1]):
    cpc = a / k; v = gp / k
    tag = '←値段が 1.25 の線より高い' if cpc > v / 1.25 else ('（1.5 の線まで余裕あり）' if cpc <= v / 1.5 else '')
    P(f'  {n}: 広告費 {a:,.0f}・クリック {k:,} → 1回 {cpc:.0f}円 ｜ 粗利 {v:.0f}円 ｜ 1.25 で {v/1.25:.0f}円・1.5 で {v/1.5:.0f}円まで ｜ {q}個 {tag}')
# ② 広告なしで売れた日
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['campaign']][r['date']] += float(r['cost'])
S = collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['name']][r['date']] += int(r['gross'])
W14 = [d for d in ALLD if '2026-11-10' <= d <= '2026-11-23']
P('■ ② 11/10〜23 に、その商品の広告費が 0 の日に売れた個数（売価で割った個数・優先配送とVIP特典は除く）')
for n in sorted(S):
    if n in ('優先配送',) or n.startswith('VIP'): continue
    pr = g['PRICE'].get(n)
    if not pr: continue
    days = [d for d in W14 if S[n].get(d) and not sum(AD[c].get(d, 0) for c in camps(n))]
    if days: P(f'  {n}: {sum(S[n][d] // pr for d in days)}個（{len(days)}日）・最後に広告費があった日 {max([d for c in camps(n) for d, v in AD[c].items() if v > 0] or ["—"])}')
open('scripts/daily/ic1124/adv_1124.txt', 'w').write('\n'.join(out) + '\n')
