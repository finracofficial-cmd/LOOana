# -*- coding: utf-8 -*-
"""今週（11/8〜14）の効率が前週（11/1〜7）より下がった中身（2026-11-15 00:5x ユーザー「利益率低下＝効率が悪くなってる証拠？なんで悪いの」）
売上÷広告費 ＝ 表示÷広告費 × クリック÷表示 × 来訪÷クリック × 注文÷来訪 × 実売÷注文
入力: meta_acct_daily_1004_1114.txt（Meta アカウント日別）・sess_daily_1004_1114.json（Shopify 来訪）・data/daily（実売・広告費・注文数・商品別）・prod_orders_wk.txt（商品別注文数）
偶然のぶれ: 数える数（クリック・来訪・注文）は ±2×√(1/前+1/今)。注文÷来訪は日ごとのぶれが偶然より大きい（φ=1.32・11/14 調べ）ので √1.32 倍する。表示単価・客単価は数えるものではないので幅を出さない"""
import csv, sys, json, math, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
H = R + 'scripts/daily/ic1115/'
MA = {}
for l in open(H + 'meta_acct_daily_1004_1114.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(H + 'sess_daily_1004_1114.json'))['rows']}
NET = collections.defaultdict(int); AD = collections.defaultdict(float); OR = {}; ADC = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): NET[r['date']] += int(r['gross']) - int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost']); ADC[r['campaign']][r['date']] += float(r['cost'])
for r in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv')): OR[r['date']] = int(r['orders'])
END = datetime.date(2026, 11, 14)
W = lambda w: [(END - datetime.timedelta(7 * w + k)).isoformat() for k in range(6, -1, -1)]
for d in W(5) + W(0): assert abs(MA[d][0] - AD[d]) / AD[d] < 0.002, (d, MA[d][0], AD[d])   # Meta の取り直しと data/daily の広告費が 0.2% 以内
def agg(ds):
    a = sum(AD[d] for d in ds); n = sum(NET[d] for d in ds); im = sum(MA[d][1] for d in ds); cl = sum(MA[d][3] for d in ds)
    se = sum(SE[d][0] for d in ds); o = sum(OR[d] for d in ds); ca = sum(SE[d][1] for d in ds); ck = sum(SE[d][2] for d in ds); cp = sum(SE[d][3] for d in ds)
    f = dict(表示単価=a / im * 1000, クリック率=cl / im, 来訪per_click=se / cl, 購入率=o / se, 客単価=n / o)
    assert abs(n / a - (im / a) * (cl / im) * (se / cl) * (o / se) * (n / o)) < 1e-9
    return dict(a=a, n=n, im=im, cl=cl, se=se, o=o, ca=ca, ck=ck, cp=cp, mer=n / a, **f)
print('週（7日）       売上÷広告費 表示単価(1000回) クリック率 来訪÷クリック 購入率(注文÷来訪) 客単価  ｜カート率 決済到達 決済完了')
WK = {}
for w in range(5, -1, -1):
    ds = W(w); x = agg(ds); WK[w] = x
    print(f"{ds[0][5:]}〜{ds[-1][5:]}    {x['mer']:.2f}      {x['表示単価']:6,.0f}円      {x['クリック率']*100:.2f}%     {x['来訪per_click']:.2f}          {x['購入率']*100:.2f}%       {x['客単価']:,.0f}  ｜{x['ca']/x['se']*100:.1f}%  {x['ck']/x['se']*100:.1f}%  {x['cp']/x['ck']*100:.0f}%")
A, B = WK[1], WK[0]
print('\n今週（11/8〜14）÷前週（11/1〜7）。売上÷広告費 の変化を要素に分ける（対数で足し算になる）')
tot = math.log(B['mer'] / A['mer'])
parts = [('表示÷広告費（表示単価の逆）', A['表示単価'] / B['表示単価'], None),
         ('クリック率', B['クリック率'] / A['クリック率'], 2 * math.sqrt(1 / A['cl'] + 1 / B['cl'])),
         ('来訪÷クリック', B['来訪per_click'] / A['来訪per_click'], 2 * math.sqrt(1 / A['se'] + 1 / B['se'])),
         ('購入率（注文÷来訪）', B['購入率'] / A['購入率'], 2 * math.sqrt(1.32) * math.sqrt(1 / A['o'] + 1 / B['o'])),
         ('客単価', B['客単価'] / A['客単価'], None)]
assert abs(sum(math.log(r) for _, r, _ in parts) - tot) < 1e-9
print(f"  売上÷広告費 {A['mer']:.2f} → {B['mer']:.2f}（{(B['mer']/A['mer']-1)*100:+.1f}%）")
for k, r, band in parts:
    s = f"  {k}: {(r-1)*100:+.1f}%（売上÷広告費 の変化の {math.log(r)/tot*100:.0f}%）"
    if band is not None: s += f" ／ 偶然のぶれ ±{band*100:.1f}% → {'偶然の範囲内' if abs(math.log(r)) <= band else '偶然では起きにくい'}"
    print(s)
print(f"  注文 {A['o']}→{B['o']}・来訪 {A['se']:,}→{B['se']:,}・クリック {A['cl']:,}→{B['cl']:,}・表示 {A['im']:,}→{B['im']:,}・広告費 {A['a']:,.0f}→{B['a']:,.0f}")
# 量と効率に分ける（利益/日）
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
SER = {n: {r['date']: r for r in g['series'](n)} for n in g['S']}
CO = collections.defaultdict(float)
for n in SER:
    for d, r in SER[n].items(): CO[d] += r['cost'] or 0
def pm(ds):
    a = sum(AD[d] for d in ds); n = sum(NET[d] for d in ds); c = sum(CO[d] for d in ds)
    return a / 7, (n - c) / a, (n - c - a) / 7
a1, m1, p1 = pm(W(1)); a2, m2, p2 = pm(W(0))
vol = (m1 - 1) * (a2 - a1); eff = (m2 - m1) * a2
assert abs(vol + eff - (p2 - p1)) < 1e-6
print(f"\n利益/日 {p1:+,.0f} → {p2:+,.0f}（{p2-p1:+,.0f}）＝ 広告費が減った分 {vol:+,.0f} ＋ 倍率が下がった分 {eff:+,.0f}（倍率 {m1:.2f}→{m2:.2f}・広告費/日 {a1:,.0f}→{a2:,.0f}）")
# 商品別
PO = collections.defaultdict(dict)
for l in open(H + 'prod_orders_wk.txt'):
    if l[0] != '#': w, n, o, gr = l.strip().split(','); PO[w][n] = (int(o), int(gr))
print('\n商品別（広告費が出た全商品・今週か前週）: 利益/週 前週→今週（差）・倍率・注文 前週→今週（注文で偶然のぶれ）')
out = []
for n in SER:
    camp = g['CAMP'].get(n, n)
    ad1 = sum(SER[n][d]['ad'] for d in W(1)); ad2 = sum(SER[n][d]['ad'] for d in W(0))
    if ad1 <= 0 and ad2 <= 0: continue
    def st_(ds):
        s = sum(SER[n][d]['sales'] for d in ds); c = sum((SER[n][d]['cost'] or 0) for d in ds); a = sum(SER[n][d]['ad'] for d in ds)
        return s, c, a, s - c - a
    s1, c1, x1, q1 = st_(W(1)); s2, c2, x2, q2 = st_(W(0))
    gr1 = sum(int(r['gross']) for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')) if r['name'] == n and r['date'] in W(1))
    gr2 = sum(int(r['gross']) for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')) if r['name'] == n and r['date'] in W(0))
    o1, g1 = PO['A'].get(n, (0, 0)); o2, g2 = PO['B'].get(n, (0, 0))
    assert g1 == gr1 and g2 == gr2, (n, g1, gr1, g2, gr2)   # Shopify の取り直しと data/daily の売上（値引前）が一致
    out.append((q2 - q1, n, q1, q2, (s1 - c1) / x1 if x1 else None, (s2 - c2) / x2 if x2 else None, o1, o2, x1, x2))
out.sort()
for dq, n, q1, q2, m1_, m2_, o1, o2, x1, x2 in out:
    mm = lambda v: f'{v:.2f}' if v is not None else '—'
    if o1 and o2:
        z = (math.log(o2 / x2) - math.log(o1 / x1)) / math.sqrt(1 / o1 + 1 / o2) if x1 and x2 else None
        ch = '' if z is None else ('・広告費あたり注文の変化は偶然の範囲内' if abs(z) <= 1 else ('・端' if abs(z) <= 2 else '・偶然では起きにくい'))
    else: ch = ''
    print(f"  {n}: {q1:+,.0f}→{q2:+,.0f}（{dq:+,.0f}）・倍率 {mm(m1_)}→{mm(m2_)}・注文 {o1}→{o2}・広告費 {x1:,.0f}→{x2:,.0f}{ch}")
ca1 = sum(ADC['カタログ全部（テスト）'][d] for d in W(1)); ca2 = sum(ADC['カタログ全部（テスト）'][d] for d in W(0))
print(f"  カタログ全部（テスト）: 広告費 {ca1:,.0f}→{ca2:,.0f}（商品に分けられない・利益から引く {-(ca2-ca1):+,.0f}）")
tot_d = sum(o[0] for o in out) - (ca2 - ca1)
oth = 7 * (p2 - p1) - tot_d
print(f"  照合: 商品の差の合計 − カタログの差 ＝ {tot_d:+,.0f}／週。店全体の差 {7*(p2-p1):+,.0f}／週。残り {oth:+,.0f} は広告を出していない商品")
