# -*- coding: utf-8 -*-
"""11/19 「夏の時みたく大量に売り捌きたい」: 7/20〜11/18 を週（月〜日）ごとに 実売・広告費・倍率・利益・注文の多い商品の数 で並べる。
夏と今で「量」がどこから来ていたか（広告費を大きく使えた商品が何本あったか・1本あたりの広告費・その倍率）を見る。入力は data/daily（w1118.py の積み直し）"""
import io, contextlib, collections, datetime, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, A, ACCT, ALLD, MAP, CAT = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['MAP'], g['CAT']
def W(days):
    key = 'z' + days[0] + days[-1]; WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
wk = collections.defaultdict(list)
for d in ALLD:
    x = datetime.date.fromisoformat(d); wk[(x - datetime.timedelta(x.weekday())).isoformat()].append(d)
OUT = []
print('週（月〜）: 日数・実売/日・広告費/日・倍率・利益/日・利益率 ｜ 広告費が週5万円以上の商品の数・上位3商品の広告費/日（倍率）')
for w in sorted(wk):
    if w < '2026-07-20': continue   # ナノ・ディスペンサーのバリエーション別原価が 7/17 からしかない（それ以前は原価を正しく出せない）ので 7/20 の週から
    ds = wk[w]; N, Q, K = W(ds); s = sum(N.values()); k = sum(K.values()); a = ACCT(ds); p = s - k - a; n = len(ds)
    prods = []
    for nm in set(N) | {x for x in MAP if A(ds, x)}:
        ad = A(ds, nm)
        if ad <= 0: continue
        prods.append((ad, nm, (N.get(nm, 0) - K.get(nm, 0)) / ad, Q.get(nm, 0)))
    prods.sort(reverse=True); big = [x for x in prods if x[0] >= 50000]
    top = '・'.join(f'{nm[:8]} {ad/n:,.0f}({m:.2f})' for ad, nm, m, q in prods[:3])
    print(f'  {w}: {n}日・{s/n:,.0f}・{a/n:,.0f}・{(s-k)/a:.2f}・{p/n:+,.0f}・{p/s:.0%} ｜ {len(big)}本・{top}')
    OUT.append(dict(w=w, n=n, s=s, a=a, k=k, p=p, big=len(big), prods=[(nm, ad, m, q) for ad, nm, m, q in prods]))
json.dump(OUT, open('scripts/daily/ic1119/summer_vs_now.json', 'w'), ensure_ascii=False, default=str)
# 夏（7/6〜8/30）と直近4週（10/20〜11/16）・最新週の比較
def per(a_, b_):
    ws = [o for o in OUT if a_ <= o['w'] <= b_]; n = sum(o['n'] for o in ws)
    s = sum(o['s'] for o in ws); a = sum(o['a'] for o in ws); k = sum(o['k'] for o in ws); p = sum(o['p'] for o in ws)
    P = collections.defaultdict(lambda: [0, 0, 0])
    for o in ws:
        for nm, ad, m, q in o['prods']: P[nm][0] += ad; P[nm][1] += m * ad; P[nm][2] += q
    tops = sorted(P.items(), key=lambda x: -x[1][0])
    return n, s, a, k, p, tops
for lab, a_, b_ in (('夏 7/20〜8/30（6週）', '2026-07-20', '2026-08-24'), ('9月 8/31〜9/27（4週）', '2026-08-31', '2026-09-21'), ('10/20〜11/16（4週）', '2026-10-20', '2026-11-10'), ('11/16〜18', '2026-11-16', '2026-11-16')):
    n, s, a, k, p, tops = per(a_, b_)
    print(f'\n■ {lab}: 実売/日 {s/n:,.0f}・広告費/日 {a/n:,.0f}・倍率 {(s-k)/a:.2f}・利益/日 {p/n:+,.0f}')
    cum = 0
    for nm, (ad, mm, q) in tops[:8]:
        cum += ad
        print(f'   {nm[:14]:14} 広告費/日 {ad/n:>8,.0f}（全体の{ad/a:.0%}）・倍率 {mm/ad:.2f}・個数/日 {q/n:.1f}')
    for th in (30000, 50000, 80000):
        print(f'   1日あたり広告費 {th:,}円以上の商品: {sum(1 for nm,(ad,mm,q) in tops if ad/n >= th)}本', end='')
    print()

# ナノの週ごと（広告費/日・倍率）: 8万円/日でどれだけ続いたか
print('\n■ ナノの週ごと（広告費/日・倍率・個数/日）')
for o in OUT:
    for nm, ad, m, q in o['prods']:
        if nm == 'ナノガラス脱毛パッド': print(f"  {o['w']}: {ad/o['n']:,.0f}・{m:.2f}・{q/o['n']:.1f}")
