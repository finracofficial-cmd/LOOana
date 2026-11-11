"""11/11の利益が低かった理由の分解と、まとめ買いの現状（CSV・保存済みの実測ファイルのみ。読み取り専用）。
原価: 商品別の代表原価×個数。ナノは30日実測ミックスの加重平均【近似】、裏起毛パンツ・すき間ポケットは daily_variant.csv の実測構成。"""
import csv, json, pickle, collections, itertools, re
R = pickle.load(open('/tmp/rep1111w.pkl', 'rb'))
COST = dict(R['COST']); PRICE = dict(R['PRICE']); MAP = R['MAP']
COST['ナノガラス脱毛パッド'] = (927 * 757 + 326 * 740) / 1253
S = collections.defaultdict(dict)
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    if r['date'] >= '2026-10-13': S[r['date']][r['name']] = (int(r['gross']), int(r['disc']))
A = collections.defaultdict(dict)
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    if r['date'] >= '2026-10-13': A[r['date']][r['campaign']] = A[r['date']].get(r['campaign'], 0) + float(r['cost'])
VG = {'防風あったか裏起毛パンツ': {'S':1140,'M':1148,'L':1219,'XL':1233,'XL灰':1338,'XXL':1251}, 'すき間収納シートポケット': {'標準':760,'赤':956}}
VC = collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_variant.csv')):
    if r['name'] in VG: VC[(r['date'], r['name'])] += int(r['gross']) / 3980 * VG[r['name']][r['cost_group']]
def hookcost(n, d): return 732 if (n == '高見えレザーヘッドレストフック' and d >= '2026-10-07') else COST[n]
def units(n, g): return g / PRICE[n] if n in PRICE else 0
def cogs(d, n, g):
    if n in VG: return VC[(d, n)]
    return units(n, g) * hookcost(n, d) if n in PRICE and n in COST else 0
SES = {}
for f in ['scripts/daily/o1105/sess_1021_1105_raw.txt', 'scripts/daily/o1111/sess_1027_1111_raw.txt']:
    for ln in open(f):
        if ln.startswith('#') or not ln.strip(): continue
        d, s, c, ck, cp = ln.strip().split(','); SES[d] = (int(s), int(c), int(ck), int(cp))
ORD = {r['date']: (int(r['orders']), int(r['ge7000']), int(r['ge8000']), int(r['ge10000'])) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
NOUNIT = {'優先配送', 'VIP特典'}
def day(d):
    net = sum(g - dc for g, dc in S[d].values()); gross = sum(g for g, _ in S[d].values()); disc = sum(dc for _, dc in S[d].values())
    c = sum(cogs(d, n, g) for n, (g, _) in S[d].items()); ad = sum(A[d].values())
    u = sum(units(n, g) for n, (g, _) in S[d].items() if n not in NOUNIT)
    gu = sum(g for n, (g, _) in S[d].items() if n not in NOUNIT and n in PRICE)
    o = ORD[d][0]; s = SES[d][0]
    return dict(net=net, gross=gross, disc=disc, cogs=c, ad=ad, profit=net - c - ad, orders=o, ses=s, units=u, gu=gu, b7=ORD[d][1], b8=ORD[d][2])
def avg(ds):
    xs = [day(d) for d in ds]; return {k: sum(x[k] for x in xs) / len(xs) for k in xs[0]}
D = ['2026-11-%02d' % i for i in range(4, 12)]
print('日別（原価は近似）: 日付 実売 原価 広告 利益 注文 客単価 来訪 CVR 広告÷来訪 粗利率 個数/注文 平均単価 値引率 7千円以上比率')
for d in D:
    x = day(d)
    print(d[5:], round(x['net']), round(x['cogs']), round(x['ad']), round(x['profit']), x['orders'], round(x['net'] / x['orders']), x['ses'],
          '%.2f%%' % (x['orders'] / x['ses'] * 100), round(x['ad'] / x['ses'], 1), '%.1f%%' % ((1 - x['cogs'] / x['net']) * 100),
          '%.3f' % (x['units'] / x['orders']), round(x['gu'] / x['units']), '%.2f%%' % (x['disc'] / x['gross'] * 100), '%.1f%%' % (x['b7'] / x['orders'] * 100))

def shapley(b, t):
    """利益 = 広告費 × (来訪/広告費) × (注文/来訪) × 客単価 × 粗利率 − 広告費 を5要因に分ける（全順列の平均）"""
    def f(x): return dict(ad=x['ad'], spy=x['ses'] / x['ad'], cvr=x['orders'] / x['ses'], aov=x['net'] / x['orders'], m=1 - x['cogs'] / x['net'])
    fb, ft = f(b), f(t); keys = list(fb)
    def prof(v): return v['ad'] * v['spy'] * v['cvr'] * v['aov'] * v['m'] - v['ad']
    con = dict.fromkeys(keys, 0.0); perms = list(itertools.permutations(keys))
    for p in perms:
        cur = dict(fb)
        for k in p:
            before = prof(cur); cur[k] = ft[k]; con[k] += prof(cur) - before
    con = {k: v / len(perms) for k, v in con.items()}
    assert abs(sum(con.values()) - (prof(ft) - prof(fb))) < 1
    return fb, ft, con, prof(ft) - prof(fb)
t = day('2026-11-11')
for lab, b in [('前週水 11/4', day('2026-11-04')), ('直近6日平均 11/5-11/10', avg(D[1:7]))]:
    fb, ft, con, tot = shapley(b, t)
    print(f'\n■ 11/11 − {lab}: 利益の差 {tot:+,.0f}円')
    nm = dict(ad='広告費の額', spy='広告費あたりの来訪数', cvr='来訪→注文の率', aov='客単価', m='粗利率')
    for k in con: print(f'  {nm[k]}: {fb[k]:,.4g} → {ft[k]:,.4g}  寄与 {con[k]:+,.0f}円')

# 客単価の分解（個数/注文 × 平均単価 × (1−値引率)）。優先配送・VIP特典は個数に入れない
def aovparts(x): return x['units'] / x['orders'], x['gu'] / x['units'], x['net'] / x['gu']
for lab, b in [('前週水 11/4', day('2026-11-04')), ('直近6日平均', avg(D[1:7]))]:
    ub, pb, rb = aovparts(b); ut, pt, rt = aovparts(t)
    print(f'\n■ 客単価 {lab} {b["net"]/b["orders"]:,.0f} → 11/11 {t["net"]/t["orders"]:,.0f}: 個数/注文 {ub:.3f}→{ut:.3f}（{(ut/ub-1)*100:+.1f}%）・商品の平均単価 {pb:,.0f}→{pt:,.0f}（{(pt/pb-1)*100:+.1f}%）・値引き後に残る率など {rb:.3f}→{rt:.3f}（{(rt/rb-1)*100:+.1f}%）')

# 商品別の利益: 11/11 と 6日平均・前週水
INV = {v: k for k, v in MAP.items()}
def pprof(d):
    out = collections.defaultdict(float)
    for n, (g, dc) in S[d].items(): out[n] += g - dc - cogs(d, n, g)
    for cp, c in A[d].items(): out[INV.get(cp, cp)] -= c
    return out
p11 = pprof('2026-11-11'); p04 = pprof('2026-11-04')
p6 = collections.defaultdict(float)
for d in D[1:7]:
    for n, v in pprof(d).items(): p6[n] += v / 6
rows = sorted(set(p11) | set(p6) | set(p04), key=lambda n: p11.get(n, 0) - p6.get(n, 0))
print('\n■ 商品別の利益（11/11 − 6日平均の小さい順）: 商品 11/11 6日平均 差 ｜ 前週水 差')
for n in rows:
    a, b, c = p11.get(n, 0), p6.get(n, 0), p04.get(n, 0)
    if abs(a - b) < 1500 and abs(a - c) < 1500: continue
    print(f'  {n[:16]}: {a:+,.0f} / {b:+,.0f} / {a-b:+,.0f} ｜ {c:+,.0f} / {a-c:+,.0f}')
print('  合計', round(sum(p11.values())), round(sum(p6.values())), round(sum(p11.values()) - sum(p6.values())), '｜', round(sum(p04.values())), round(sum(p11.values()) - sum(p04.values())))

# 個数（4,980円以上の商品）: 11/11 と 前週水・6日平均
def hi(d): return {n: units(n, g) for n, (g, _) in S[d].items() if PRICE.get(n, 0) >= 4980 and g}
print('\n■ 4,980円以上の商品の個数 11/11:', {k[:10]: round(v) for k, v in hi('2026-11-11').items()}, '\n   11/4:', {k[:10]: round(v) for k, v in hi('2026-11-04').items()})
h6 = collections.defaultdict(float)
for d in D[1:7]:
    for n, v in hi(d).items(): h6[n] += v / 6
print('   6日平均:', {k[:10]: round(v, 1) for k, v in h6.items()}, '合計', round(sum(h6.values()), 1))

# まとめ買いの現状: 商品別 個数÷注文（7日・30日）と値引率
def short(t):
    for n in sorted(PRICE, key=len, reverse=True):
        if n in t: return n
    return None
for lab, f, Q, N, DC in [('7日 11/5-11', 'ord7_raw.json', R['Q7'], R['N7'], R['DC7']), ('30日 10/13-11/11', 'ord30_raw.json', R['Q30'], R['N30'], R['DC30'])]:
    o = collections.defaultdict(int)
    for t_, c in json.load(open('scripts/daily/o1111/' + f))['rows']:
        n = short(t_)
        if n: o[n] += int(c)
    print(f'\n■ 商品別 個数÷注文（{lab}）: 商品 注文 個数 個数/注文 値引率')
    tq = to = 0
    for n in sorted(o, key=lambda n: -o[n]):
        q = Q.get(n, 0)
        if o[n] < (15 if '7日' in lab else 40) or n in NOUNIT or not q: continue
        g = N.get(n, 0) + DC.get(n, 0); tq += q; to += o[n]
        print(f'  {n[:16]}: {o[n]} / {q} / {q/o[n]:.2f} / {DC.get(n,0)/g*100:.1f}%')
    print(f'  上の商品の合計: 個数/注文 {tq/to:.3f}')
# 7,000円以上の注文の比率（週別）
print('\n■ 7,000円以上の注文の比率')
for lab, ds in [('10/14-20', ('2026-10-14', '2026-10-20')), ('10/21-27', ('2026-10-21', '2026-10-27')), ('10/28-11/3', ('2026-10-28', '2026-11-03')), ('11/4-10', ('2026-11-04', '2026-11-10')), ('11/11', ('2026-11-11', '2026-11-11'))]:
    xs = [v for d, v in ORD.items() if ds[0] <= d <= ds[1]]
    o = sum(x[0] for x in xs); b7 = sum(x[1] for x in xs); b10 = sum(x[3] for x in xs)
    print(f'  {lab}: 注文 {o}・7,000円以上 {b7}（{b7/o*100:.1f}%）・10,000円以上 {b10}（{b10/o*100:.1f}%）')
