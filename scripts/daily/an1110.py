# -*- coding: utf-8 -*-
"""11/10 定例の数値（昨日=11/09 月）。w1109.py の積み直し関数（qty/agg/A/ACCT）をそのまま使う（実測のみ）"""
import io, contextlib, statistics as st, datetime
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1109.py').read(), g)
WIN, agg, A, ACCT, ALLD, MAP = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['MAP']
def W(days):
    key = 'x' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
def tot(days):
    N, Q, K = W(days); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a, s - k - a
for d in ['2026-11-08', '2026-11-09']:
    s, k, a, p = tot([d]); print(f'{d}: 実売{s:,} 原価{k:,} 広告{a:,.0f} 利益{p:,.0f}（{p/s:.1%}）MER{s/a:.2f} 倍率{(s-k)/a:.2f}')
last15 = ALLD[-15:]; P = {d: tot([d])[3] for d in last15}
print('利益 15日順位', sorted(last15, key=lambda d: -P[d]).index('2026-11-09') + 1, '/15', {d[5:]: round(P[d]) for d in last15})
wed = [d for d in ALLD if datetime.date.fromisoformat(d).weekday() == 0 and '2026-09-14' <= d <= '2026-11-02' and d not in g['HOL']]
ws = [tot([d])[0] for d in wed]; s4 = tot(['2026-11-09'])[0]; s28 = tot(['2026-11-02'])[0]
print('祝日でない月曜', [d[5:] for d in wed], f'平均実売{st.mean(ws):,.0f}・前週月{s28:,}', f'→ 11/9 {s4/st.mean(ws)-1:+.1%} ／ {s4/s28-1:+.1%}')
wp = [tot([d])[3] for d in wed]; print('祝日でない月曜 利益平均', round(st.mean(wp)), [round(x) for x in wp])
print('前週月 11/02 利益', round(tot(['2026-11-02'])[3]))
m3 = [round(tot([d])[3]) for d in ['2026-11-07', '2026-11-08', '2026-11-09']]; print('3日移動平均利益', round(st.mean(m3)), m3)
p7 = tot(ALLD[-7:]); pp7 = tot(ALLD[-14:-7]); print(f'7日利益 {p7[3]:,.0f}（{p7[3]/p7[0]:.1%}）前7日 {pp7[3]:,.0f}')
cum = [d for d in ALLD if d >= '2026-11-01']; c = tot(cum); print(f'11月累計利益 {c[3]:,.0f}（{len(cum)}日・{c[3]/len(cum):,.0f}/日）')
print('\n商品: 11/9 個数・倍率・利益 ／ 11/8 倍率 ／ ★=2日続けて1.25未満 ／ 3日(11/7-9) ／ 7日(11/3-9)倍率・利益')
D1, D0, D3, D7 = ['2026-11-09'], ['2026-11-08'], ALLD[-3:], ALLD[-7:]
X = {k: W(v) for k, v in [('d1', D1), ('d0', D0), ('d3', D3), ('d7', D7)]}
names = set(X['d7'][0]) | {n for n, c in MAP.items() if A(D7, n)}
def mm(k, days, n):
    N, Q, K = X[k]; a = A(days, n); s = N.get(n, 0); kk = K.get(n, 0)
    return (None if not a else (s - kk) / a), s - kk - a, Q.get(n, 0), a
for n in sorted(names, key=lambda n: -A(D7, n)):
    if not A(D7, n) and n not in X['d1'][0]: continue
    m1, p1, q1, a1 = mm('d1', D1, n); m0, *_ = mm('d0', D0, n); m3_, p3, *_ = mm('d3', D3, n); m7, p7_, *_ = mm('d7', D7, n)
    f = lambda v: '—' if v is None else f'{v:.2f}'
    flag = '★' if (m1 is not None and m0 is not None and m1 < 1.25 and m0 < 1.25) else ''
    print(f"  {n}: {q1}個・{f(m1)}・{p1:+,.0f}（広告{a1:,.0f}） ／ {f(m0)} ／ {flag} ／ 3日{f(m3_)} ／ 7日{f(m7)}・{p7_:+,.0f}")
print('カタログ 11/9', g['CAT'](D1), '7日', g['CAT'](D7))
