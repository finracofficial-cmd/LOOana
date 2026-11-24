# -*- coding: utf-8 -*-
"""11/24: 出し直しの候補の週ごと（日曜はじまり・広告を出した日だけ）の 広告費/日・倍率。入力: w1123.py"""
import io, contextlib, datetime, collections
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD0, agg, WIN = g['A'], g['ALLD'], g['agg'], g['WIN']
ALLD = [d for d in ALLD0 if d >= '2026-07-17']
out = []
for n in ('姿勢サポートチェア', 'ムダ毛シェーバー', 'ナノバブルシャワーヘッド', 'バランスケアスリッパ', '2WAYシートボックス', '伸縮ワックス洗車ブラシ', '偏光・調光サングラス', 'ネックマッサージャー'):
    ds = [d for d in ALLD if A([d], n) > 0]; wk = collections.OrderedDict()
    for d in ds:
        x = datetime.date.fromisoformat(d); k = (x - datetime.timedelta(days=(x.weekday() + 1) % 7)).isoformat(); wk.setdefault(k, []).append(d)
    parts = []
    for k, v in wk.items():
        WIN['c' + n + k] = v; N, D, Q, K = agg(v, 'c' + n + k); a = A(v, n)
        parts.append(f"{k[5:]} {a/len(v):,.0f}円×{len(v)}日 {(N.get(n,0)-K.get(n,0))/a:.2f}")
    s = f'■ {n}: ' + '・'.join(parts); print(s); out.append(s)
open('scripts/daily/ic1124/cand_weekly_1124.txt', 'w').write('\n'.join(out) + '\n')
