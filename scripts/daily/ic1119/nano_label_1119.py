# -*- coding: utf-8 -*-
"""11/19 「ナノガラス脱毛はかわらなかったんよな？」: 11/14 の分析（ic1114/nano_label_2030.py）を 11/18 まで延ばす。
商品名を「在庫セール」入りに変えたのは 10/29 08:00〜10/31 00:30（4回）。前 10/22〜28 ↔ 後 10/31〜11/18（10/29・30 は変更の途中なので除く）。
倍率は data/daily（w1118.py の積み直し）、注文は ic1119/nano_orders_1022_1118.json（Shopify）。偶然かは注文で判定（ポアソン）。ナノ以外の店全体の動きも並べる"""
import io, contextlib, json, math
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, A, ACCT, ALLD = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD']
O = {d: int(o) for d, o in json.load(open('scripts/daily/ic1119/nano_orders_1022_1118.json'))['rows']}
n = 'ナノガラス脱毛パッド'
def win(a_, b_):
    ds = [d for d in ALLD if a_ <= d <= b_]; key = 'n' + a_ + b_; WIN[key] = ds; N, DC, Q, K = agg(ds, key)
    a = A(ds, n); s = N.get(n, 0); k = K.get(n, 0); o = sum(O[d] for d in ds)
    sa = sum(N.values()) - s; ka = sum(K.values()) - k; aa = ACCT(ds) - a
    return ds, a, (s - k) / a, o, (sa - ka) / aa
P = win('2026-10-22', '2026-10-28')
print(f'前 10/22〜28（{len(P[0])}日）: 広告費/日 {P[1]/len(P[0]):,.0f}・倍率 {P[2]:.2f}・注文 {P[3]}・広告費1万円あたり注文 {P[3]/P[1]*1e4:.2f} ｜ ナノ以外の倍率 {P[4]:.2f}')
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
for a_, b_ in (('2026-10-31', '2026-11-06'), ('2026-11-07', '2026-11-13'), ('2026-11-14', '2026-11-18'), ('2026-10-31', '2026-11-18')):
    X = win(a_, b_); lam = P[3] / P[1] * X[1]; o = X[3]
    p = ple(o, lam) if o < lam else 1 - ple(o - 1, lam)
    v = '偶然では起きにくい' if p < 0.025 else ('偶然でも起きるが端' if p < 0.16 else '偶然の範囲内')
    print(f'後 {a_[5:]}〜{b_[5:]}（{len(X[0])}日）: 広告費/日 {X[1]/len(X[0]):,.0f}・倍率 {X[2]:.2f}・注文 {o}・1万円あたり {o/X[1]*1e4:.2f}・前の効率なら期待 {lam:.1f}・{"少ない" if o < lam else "多い"}側 {p:.0%} → {v} ｜ ナノ以外の倍率 {X[4]:.2f}')
X = win('2026-10-29', '2026-10-30'); print(f'変更の途中 10/29〜30: 広告費/日 {X[1]/2:,.0f}・倍率 {X[2]:.2f}・注文 {X[3]}')
