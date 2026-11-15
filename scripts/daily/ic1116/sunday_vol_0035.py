# -*- coding: utf-8 -*-
"""11/15（日）の利益が祝日でない日曜の平均より少ないのは、量（広告費）か効率（倍率）か。利益＝（倍率−1）×広告費 で分ける。実測のみ（w1115.py の積み直し関数）"""
import io, contextlib, datetime, statistics as st
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1115.py').read(), g)
WIN, agg, ACCT, ALLD = g['WIN'], g['agg'], g['ACCT'], g['ALLD']
def tot(days):
    key = 's' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a
sun = [d for d in ALLD if datetime.date.fromisoformat(d).weekday() == 6 and '2026-09-20' <= d <= '2026-11-08' and d not in g['HOL']]
R = {d: tot([d]) for d in sun + ['2026-11-15']}
for d in sun + ['2026-11-15']:
    s, k, a = R[d]; print(f'{d}: 広告費 {a:,.0f}・倍率 {(s-k)/a:.2f}・利益 {s-k-a:,.0f}')
ma = st.mean(R[d][2] for d in sun); mm = st.mean((R[d][0]-R[d][1])/R[d][2] for d in sun)
s, k, a = R['2026-11-15']; m = (s-k)/a
print(f'日曜平均: 広告費 {ma:,.0f}・倍率 {mm:.2f}・利益（平均倍率×平均広告費で） {(mm-1)*ma:,.0f}')
print(f'11/15: 広告費 {a:,.0f}・倍率 {m:.2f}・利益 {(m-1)*a:,.0f}')
print(f'差の分け方: 量（広告費の差 × 日曜平均の倍率−1）{(a-ma)*(mm-1):+,.0f} ／ 効率（倍率の差 × 11/15の広告費）{(m-mm)*a:+,.0f}')
