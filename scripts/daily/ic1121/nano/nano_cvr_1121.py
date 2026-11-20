# -*- coding: utf-8 -*-
"""11/21 「ナノガラスは名称変更前後でcvr変わってないので、違いはないってこと？」
ナノのページに着いた来訪の買う率を、表記の前（【本日終了⏰】10/22〜28）と後（【在庫セール⏰】10/31〜11/18）で比べる。広告費あたりの来訪・注文も並べる。
入力: nano_page_daily_raw.txt・../../o1120/sess_daily_1004_1120.json（店全体の来訪）・data/daily（ナノの売上と広告費）・../../ic1119/nano_orders_1022_1118.json は使わない（注文は前回の結果 252／164 をそのまま引く）"""
import csv, json, math, os, collections
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D0, '..', '..', '..', '..'))
N = {}
for l in open(os.path.join(D0, 'nano_page_daily_raw.txt')):
    if l[0] != '#': p = l.strip().split(','); N[p[0]] = [int(x) for x in p[1:]]
S = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(os.path.join(D0, '..', '..', 'o1120', 'sess_daily_1004_1120.json')))['rows']}
AD = collections.defaultdict(float); NET = collections.defaultdict(int)
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_ad.csv'))):
    if r['campaign'] == 'ナノガラス脱毛パッド': AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_sales.csv'))):
    if r['name'] == 'ナノガラス脱毛パッド': NET[r['date']] += int(float(r['gross'])) - int(float(r['disc']))
def rng(a, b): return [d for d in sorted(N) if a <= d <= b]
B, A = rng('2026-10-22', '2026-10-28'), rng('2026-10-31', '2026-11-18'); assert len(B) == 7 and len(A) == 19
def agg(ds):
    s = sum(N[d][0] for d in ds); c = sum(N[d][1] for d in ds); k = sum(N[d][2] for d in ds); dn = sum(N[d][3] for d in ds); ad = sum(AD[d] for d in ds); net = sum(NET[d] for d in ds)
    os_ = sum(S[d][0] - N[d][0] for d in ds); od = sum(S[d][3] - N[d][3] for d in ds)
    return dict(s=s, c=c, k=k, dn=dn, ad=ad, net=net, os=os_, od=od)
b, a = agg(B), agg(A); L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
def ci(k1, n1, k0, n0):
    r = (k1 / n1) / (k0 / n0); se = math.sqrt(1 / k1 + 1 / k0); return r, r * math.exp(-1.96 * se), r * math.exp(1.96 * se)
P('■ ナノのページに着いた来訪（表記の前 10/22〜28【本日終了⏰】 → 後 10/31〜11/18【在庫セール⏰】）')
for lab, x in (('前', b), ('後', a)):
    P(f"  {lab}: 来訪 {x['s']:,}・カート率 {x['c']/x['s']:.2%}・完了÷決済画面 {x['dn']/x['k']:.0%}・購入 {x['dn']}・買う率 {x['dn']/x['s']:.2%}｜広告費 {x['ad']:,.0f}・来訪÷広告費1万円 {x['s']/x['ad']*1e4:.0f}・購入÷広告費1万円 {x['dn']/x['ad']*1e4:.2f}・売上÷広告費 {x['net']/x['ad']:.2f}")
r, lo, hi = ci(a['dn'], a['s'], b['dn'], b['s']); P(f'  買う率: 後÷前 {r:.2f}（偶然のぶれを含めた幅 {lo:.2f}〜{hi:.2f}）')
r2, lo2, hi2 = ci(a['c'], a['s'], b['c'], b['s']); P(f'  カート率: 後÷前 {r2:.2f}（幅 {lo2:.2f}〜{hi2:.2f}）')
P(f"  来訪÷広告費: 後÷前 {(a['s']/a['ad'])/(b['s']/b['ad']):.2f}・購入÷広告費: 後÷前 {(a['dn']/a['ad'])/(b['dn']/b['ad']):.2f}・広告費/日 {b['ad']/7:,.0f} → {a['ad']/19:,.0f}")
r3, lo3, hi3 = ci(a['od'], a['os'], b['od'], b['os'])
P(f"■ 同じ期間の、ナノ以外のページの買う率: 前 {b['od']/b['os']:.2%}（{b['od']}/{b['os']:,}）→ 後 {a['od']/a['os']:.2%}（{a['od']}/{a['os']:,}）・後÷前 {r3:.2f}（幅 {lo3:.2f}〜{hi3:.2f}）")
P('■ 後の期間を週ごとに（ナノのページ）')
for lab, x, y in (('10/31〜11/6', '2026-10-31', '2026-11-06'), ('11/7〜11/13', '2026-11-07', '2026-11-13'), ('11/14〜11/18', '2026-11-14', '2026-11-18')):
    w = agg(rng(x, y)); P(f"  {lab}: 来訪 {w['s']:,}・買う率 {w['dn']/w['s']:.2%}（{w['dn']}件）・来訪÷広告費1万円 {w['s']/w['ad']*1e4:.0f}")
open(os.path.join(D0, 'nano_cvr_1121.txt'), 'w').write('\n'.join(L) + '\n')
