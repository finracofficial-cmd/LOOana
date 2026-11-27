# -*- coding: utf-8 -*-
"""11/28 定例: 直近7日（11/21〜27）の広告費を「7日の倍率 1.25 以上／未満」の商品で分ける（w1127.py の積み直し関数をそのまま使う）。
店の倍率は全店の利益（広告なしで売れた商品も含む）から出し、1.25 未満の商品の利益と広告費を引いて「除いた場合」を出す"""
import io, contextlib, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1127.py').read(), g)
A, ALLD, ACCT, CAT, agg, WIN = g['A'], g['ALLD'], g['ACCT'], g['CAT'], g['agg'], g['WIN']; D7 = ALLD[-7:]
WIN['m7'] = D7; N, DC, Q, K = agg(D7, 'm7'); S = sum(N.values()); KK = sum(K.values()); tot = ACCT(D7); P = S - KK - tot
OUT = json.load(open('scripts/daily/o1127/an1128_out.json'))
hi = [o for o in OUT if o['m7'] is not None and o['m7'] >= 1.25]; lo = [o for o in OUT if o['m7'] is not None and o['m7'] < 1.25]
a = lambda L: sum(A(D7, o['n']) for o in L); p = lambda L: sum(o['p7'] for o in L)
cat = CAT(D7); out = []
out.append('■ 直近7日（11/21〜27）の広告費の中身')
out.append(f'  7日の倍率 1.25 以上の商品 {len(hi)}本: 広告費 {a(hi):,.0f}（{a(hi)/tot:.0%}）・利益 {p(hi):+,.0f} ／ ' + '・'.join(f"{o['n']} {o['m7']:.2f}" for o in sorted(hi, key=lambda o: -A(D7, o['n']))))
out.append(f'  7日の倍率 1.25 未満の商品 {len(lo)}本: 広告費 {a(lo):,.0f}（{a(lo)/tot:.0%}）・利益 {p(lo):+,.0f} ／ ' + '・'.join(f"{o['n']} {o['m7']:.2f}" for o in sorted(lo, key=lambda o: -A(D7, o['n']))))
rest = tot - a(hi) - a(lo) - cat   # 7日のうちに売上が1個もなく、商品の表に出ない広告費（11/21〜27 は 0円）
out.append(f'  カタログ 広告費 {cat:,.0f}（{cat/tot:.0%}）・表に出ない広告費 {rest:,.0f}・合計 {tot:,.0f}')
AD = g['AD']; known = {c for n in g['ALLN'] for c in (g['MULTI'][n] if n in g['MULTI'] else (g['MAP'].get(n, n),))}
other = {c: sum(AD[c].get(d, 0) for d in D7) for c in AD if sum(AD[c].get(d, 0) for d in D7) > 0}
miss = {c: v for c, v in other.items() if c not in {x for o in OUT for x in (g['MULTI'][o['n']] if o['n'] in g['MULTI'] else (g['MAP'].get(o['n'], o['n']),))} and not c.startswith('カタログ')}
out.append('    表に出ないキャンペーン: ' + '・'.join(f'{c} {v:,.0f}' for c, v in miss.items()))
assert abs(sum(miss.values()) - rest) < 1 and rest < 1000, (miss, rest)
live = '・'.join(o['n'] for o in lo if o['bud']) or 'なし'
out.append(f'  店全体: 利益 {P:+,.0f}・倍率 {(S-KK)/tot:.2f} ／ 1.25 未満の {len(lo)}本を除くと 利益 {P-p(lo):+,.0f}・広告費 {tot-a(lo):,.0f}・倍率 {(P-p(lo))/(tot-a(lo))+1:.2f}（そのうち配信中は {live}。ほかは停止済み）')
open('scripts/daily/o1127/mix_1128.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
