# -*- coding: utf-8 -*-
"""11/19 「ナノガラスは名前を変えてから倍率高くてどのくらいだった？」: 名前を変える前（10/22〜28）・途中（10/29〜30）・後（10/31〜11/18）の日別と期間の 倍率・利益。data/daily（w1118.py の積み直し）"""
import io, contextlib
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, A, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']; n = 'ナノガラス脱毛パッド'
def w(ds):
    key = 'q' + ds[0] + ds[-1] + str(len(ds)); WIN[key] = ds; N, DC, Q, K = agg(ds, key); a = A(ds, n); s = N.get(n, 0); k = K.get(n, 0)
    return a, (s - k) / a, s - k - a, Q.get(n, 0)
for d in [x for x in ALLD if '2026-10-22' <= x <= '2026-11-18']:
    a, m, p, q = w([d]); print(f'  {d}: 広告 {a:,.0f}・{q}個・倍率 {m:.2f}・利益 {p:+,.0f}')
for lab, a_, b_ in (('前 10/22〜28', '2026-10-22', '2026-10-28'), ('途中 10/29〜30', '2026-10-29', '2026-10-30'), ('後 10/31〜11/6', '2026-10-31', '2026-11-06'),
                    ('後 11/7〜13', '2026-11-07', '2026-11-13'), ('後 11/14〜18', '2026-11-14', '2026-11-18'), ('後 10/31〜11/18', '2026-10-31', '2026-11-18')):
    ds = [x for x in ALLD if a_ <= x <= b_]; a, m, p, q = w(ds)
    print(f'{lab}（{len(ds)}日）: 広告費/日 {a/len(ds):,.0f}・倍率 {m:.2f}・利益/日 {p/len(ds):+,.0f}・個数/日 {q/len(ds):.1f}')
