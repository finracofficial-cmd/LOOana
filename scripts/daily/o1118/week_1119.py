# -*- coding: utf-8 -*-
"""11/19 定例: ①直近7日（11/12〜18）と前7日（11/5〜11）の利益の差を「効率（倍率）」と「量（広告費）」に分ける ②商品別の7日利益の差
③店全体のカート率（カートに入れた来訪÷来訪）の日別を30日のふだんの範囲と比べる。入力は data/daily（w1118.py の積み直し）と o1118/sess_daily_1004_1118.json"""
import io, contextlib, json, math, statistics as st
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, A, ACCT, ALLD, CAT = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD'], g['CAT']
def W(days):
    key = 'y' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
L7, P7 = ALLD[-7:], ALLD[-14:-7]
assert L7[0] == '2026-11-12' and P7[0] == '2026-11-05'
def tot(days):
    N, Q, K = W(days); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s, k, a
s1, k1, a1 = tot(L7); s0, k0, a0 = tot(P7)
m1, m0 = (s1 - k1) / a1, (s0 - k0) / a0; p1, p0 = s1 - k1 - a1, s0 - k0 - a0
print(f'直近7日 11/12〜18: 広告費/日 {a1/7:,.0f}・倍率 {m1:.3f}・利益/日 {p1/7:,.0f}')
print(f'前7日 11/5〜11: 広告費/日 {a0/7:,.0f}・倍率 {m0:.3f}・利益/日 {p0/7:,.0f}')
eff = (m1 - m0) * a1 / 7; vol = (m0 - 1) * (a1 - a0) / 7
assert abs(eff + vol - (p1 - p0) / 7) < 1
print(f'利益/日の差 {(p1-p0)/7:+,.0f} ＝ 効率の分 {eff:+,.0f}（倍率 {m0:.2f}→{m1:.2f} を今の量で） ＋ 量の分 {vol:+,.0f}（広告費/日 {a0/7:,.0f}→{a1/7:,.0f} を前の倍率で）')
N1, Q1, K1 = W(L7); N0, Q0, K0 = W(P7)
names = set(N1) | set(N0) | {n for n in g['MAP'] if A(L7, n) or A(P7, n)} | {'高見えレザーヘッドレストフック', '快適マジックインソール', 'ポータブルヒートシーラー', '壁掛けディスペンサー'}
rows = []
for n in names:
    if n in ('', '優先配送') or n.startswith('VIP'): continue
    q1 = N1.get(n, 0) - K1.get(n, 0) - A(L7, n); q0 = N0.get(n, 0) - K0.get(n, 0) - A(P7, n)
    if not (A(L7, n) or A(P7, n) or N1.get(n) or N0.get(n)): continue
    rows.append((q1 - q0, n, q0, q1, A(P7, n), A(L7, n)))
c1, c0 = CAT(L7), CAT(P7)
print('\n商品別 7日の利益（前7日 → 直近7日・差）と広告費/日（前 → 直近）')
for dlt, n, q0, q1, b0, b1 in sorted(rows):
    print(f'  {n}: {q0/7:+,.0f}/日 → {q1/7:+,.0f}/日（{dlt/7:+,.0f}）・広告費/日 {b0/7:,.0f} → {b1/7:,.0f}')
print(f'  カタログ（広告費だけ）: {-c0/7:+,.0f}/日 → {-c1/7:+,.0f}/日（{-(c1-c0)/7:+,.0f}）')
chk = sum(r[0] for r in rows) - (c1 - c0)
oth = (p1 - p0) - chk
print(f'  合計 {chk/7:+,.0f}/日（全店の差 {(p1-p0)/7:+,.0f}/日・残り＝優先配送などの売上 {oth/7:+,.0f}/日）')
# ③ カート率
R = json.load(open('scripts/daily/o1118/sess_daily_1004_1118.json'))['rows']
R = {r[0]: [int(x) for x in r[1:]] for r in R}
days = sorted(R)
print('\n店全体のカート率（カートに入れた来訪÷来訪）: 前日までの30日（祝日除く）の中央値 ×÷ e^σ（ふだん）・e^2σ（偶然では起きにくい）')
for T in days[-5:]:
    base = [d for d in days if d < T][-31:]
    base = [d for d in base if d not in g['HOL']][-30:]
    lr = [math.log(R[d][1] / R[d][0]) for d in base]; mu = st.median(lr); sd = st.pstdev(lr)
    x = math.log(R[T][1] / R[T][0]); z = (x - mu) / sd
    v = '偶然の範囲内' if abs(z) <= 1 else ('偶然でも起きるが端' if abs(z) <= 2 else '偶然では起きにくい')
    print(f'  {T}: {R[T][1]}/{R[T][0]} = {R[T][1]/R[T][0]:.2%}（中央値 {math.exp(mu):.2%}・ふだん {math.exp(mu-sd):.2%}〜{math.exp(mu+sd):.2%}）→ {v}・購入/来訪 {R[T][3]/R[T][0]:.2%}')
