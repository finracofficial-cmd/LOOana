# -*- coding: utf-8 -*-
"""11/24「全体的に売上を伸ばす・利益を上げる・商品ごとに何をすればいいか、網羅して」: 
① 店全体の週ごと（9/28〜11/23・日曜はじまり）の 利益/日・倍率・広告費/日
② 広告を出している商品の 週ごと（10/26〜11/23 の5週）の 倍率・利益/日、7日の 個数÷注文（まとめ買い）、出した日
入力: w1123.py（売上・原価・広告費の積み直し）・o1123/orders_7d_1117_1123_raw.json（7日の注文数・個数）"""
import io, contextlib, collections, csv, json, re, datetime
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, ACCT, MAP, MULTI = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT'], g['MAP'], g['MULTI']
def tot(days, key):
    WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
def span(a, b):
    x = datetime.date.fromisoformat(a); o = []
    while x <= datetime.date.fromisoformat(b): o.append(x.isoformat()); x += datetime.timedelta(1)
    return o
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
WKS = [(d, span(d, (datetime.date.fromisoformat(d) + datetime.timedelta(6)).isoformat())) for d in ['2026-09-28', '2026-10-05', '2026-10-12', '2026-10-19', '2026-10-26', '2026-11-02', '2026-11-09', '2026-11-16']]
WKS.append(('2026-11-23', ['2026-11-23']))
P('■ ① 店全体（週は日曜はじまり・11/23 は1日だけ）: 利益/日・倍率・広告費/日・実売/日')
for k, ds in WKS:
    N, Q, K = tot(ds, 'w' + k); s = sum(N.values()); kk = sum(K.values()); a = ACCT(ds); n = len(ds)
    P(f'  {k[5:]}〜（{n}日）: 利益 {(s-kk-a)/n:+,.0f}・倍率 {(s-kk)/a:.2f}・広告費 {a/n:,.0f}・実売 {s/n:,.0f}')
# ② 商品ごと
W5 = WKS[4:8] + [('2026-11-23', ['2026-11-23'])]
first = {}
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    if float(r['cost']) > 0: first.setdefault(r['campaign'], r['date']); first[r['campaign']] = min(first[r['campaign']], r['date'])
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
D7 = ALLD[-7:]; N7, Q7, K7 = tot(D7, 'p7')
names = [n for n in set(N7) | set(MAP) if A(D7, n) > 0]
camps = lambda n: MULTI.get(n, (MAP.get(n, n),))
# 7日の注文数（Shopify の商品ID → 名前は ic1121/aov の表）
IDN = {r[0]: nm(r[1]) for f in ('product_totals_1022_1120_raw.json', 'product_totals_0629_1120_raw.json') for r in json.load(open('scripts/daily/ic1121/aov/' + f))['rows'] if r[0]}
O7 = {IDN.get(r[0], r[0]): (int(r[1]), int(r[2])) for r in json.load(open('scripts/daily/o1123/orders_7d_1117_1123_raw.json'))['rows'] if r[0]}
P('■ ② 広告を出している商品（直近7日 11/17〜23 の広告費の多い順）: 最初に広告を出した日（今のキャンペーン）｜週ごとの倍率（10/26〜・11/2〜・11/9〜・11/16〜・11/23）｜7日の利益/日・注文・個数÷注文')
for n in sorted(names, key=lambda n: -A(D7, n)):
    st = min(first.get(c, '9999') for c in camps(n))
    ws = []
    for k, ds in W5:
        a = A(ds, n)
        if not a: ws.append('—'); continue
        N, Q, K = tot(ds, f'x{k}'); ws.append(f'{(N.get(n,0)-K.get(n,0))/a:.2f}')
    a7 = A(D7, n); p7 = N7.get(n, 0) - K7.get(n, 0) - a7; o, q = O7.get(n, (0, 0))
    P(f"  {n}: 開始 {st}｜{' → '.join(ws)}｜利益 {p7/7:+,.0f}/日・{o}注文・{(q/o if o else 0):.2f}個/注文・広告費 {a7/7:,.0f}/日")
open('scripts/daily/ic1124/plan_1124.txt', 'w').write('\n'.join(out) + '\n')

# ③ 9/28〜10/4 の週と 11/16〜22 の週で、商品ごとの利益/日（どこが減ったか）
def prod_week(ds, key):
    N, Q, K = tot(ds, key); names = set(N) | {n for n in MAP if A(ds, n)}
    return {n: (N.get(n, 0) - K.get(n, 0) - A(ds, n)) / len(ds) for n in names}, g['CAT'](ds) / len(ds)
a_, ca = prod_week(WKS[0][1], 'q0'); b_, cb = prod_week(WKS[7][1], 'q7')
P('■ ③ 商品ごとの利益/日: 9/28〜10/4 → 11/16〜22（差の大きい順・カタログは別）')
for n in sorted(set(a_) | set(b_), key=lambda n: -abs(b_.get(n, 0) - a_.get(n, 0)))[:16]:
    P(f'  {n}: {a_.get(n,0):+,.0f} → {b_.get(n,0):+,.0f}（{b_.get(n,0)-a_.get(n,0):+,.0f}）')
P(f'  カタログ（広告費/日）: {ca:,.0f} → {cb:,.0f}')
o9 = WKS[0][1]; o11 = WKS[7][1]
N, Q, K = tot(o9, 'r0'); s0 = sum(N.values()); k0 = sum(K.values()); a0 = ACCT(o9)
N, Q, K = tot(o11, 'r7'); s1 = sum(N.values()); k1 = sum(K.values()); a1 = ACCT(o11)
m0 = (s0 - k0) / a0 - 1; m1 = (s1 - k1) / a1 - 1
P(f'■ ④ 利益/日の差 {(s1-k1-a1)/7 - (s0-k0-a0)/7:+,.0f} の内訳（利益＝(倍率−1)×広告費）: 倍率の分 {(m1-m0)*a0/7:+,.0f}（{m0+1:.2f} → {m1+1:.2f}・前の広告費のまま）＋ 量の分 {m1*(a1-a0)/7:+,.0f}（広告費/日 {a0/7:,.0f} → {a1/7:,.0f}）')
open('scripts/daily/ic1124/plan_1124.txt', 'w').write('\n'.join(out) + '\n')
