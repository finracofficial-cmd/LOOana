# -*- coding: utf-8 -*-
"""11/24 定例: 直近7日（11/17〜23）の広告費を「7日の倍率 1.25 以上／未満」の商品で分ける（w1123.py の積み直し関数をそのまま使う）。
店の倍率は全店の利益（広告なしで売れた商品も含む）から出し、1.25 未満の商品の利益と広告費を引いて「除いた場合」を出す"""
import io, contextlib, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, ACCT, CAT, agg, WIN = g['A'], g['ALLD'], g['ACCT'], g['CAT'], g['agg'], g['WIN']; D7 = ALLD[-7:]
WIN['m7'] = D7; N, DC, Q, K = agg(D7, 'm7'); S = sum(N.values()); KK = sum(K.values()); tot = ACCT(D7); P = S - KK - tot
OUT = json.load(open('scripts/daily/o1123/an1124_out.json'))
hi = [o for o in OUT if o['m7'] is not None and o['m7'] >= 1.25]; lo = [o for o in OUT if o['m7'] is not None and o['m7'] < 1.25]
a = lambda L: sum(A(D7, o['n']) for o in L); p = lambda L: sum(o['p7'] for o in L)
cat = CAT(D7); out = []
out.append('■ 直近7日（11/17〜23）の広告費の中身')
out.append(f'  7日の倍率 1.25 以上の商品 {len(hi)}本: 広告費 {a(hi):,.0f}（{a(hi)/tot:.0%}）・利益 {p(hi):+,.0f} ／ ' + '・'.join(f"{o['n']} {o['m7']:.2f}" for o in sorted(hi, key=lambda o: -A(D7, o['n']))))
out.append(f'  7日の倍率 1.25 未満の商品 {len(lo)}本: 広告費 {a(lo):,.0f}（{a(lo)/tot:.0%}）・利益 {p(lo):+,.0f} ／ ' + '・'.join(f"{o['n']} {o['m7']:.2f}" for o in sorted(lo, key=lambda o: -A(D7, o['n']))))
out.append(f'  カタログ 広告費 {cat:,.0f}（{cat/tot:.0%}）・合計 {tot:,.0f}（照合 {a(hi)+a(lo)+cat:,.0f}）')
assert abs(a(hi) + a(lo) + cat - tot) < 1
out.append(f'  店全体: 利益 {P:+,.0f}・倍率 {(S-KK)/tot:.2f} ／ 1.25 未満の {len(lo)}本を除くと 利益 {P-p(lo):+,.0f}・広告費 {tot-a(lo):,.0f}・倍率 {(P-p(lo))/(tot-a(lo))+1:.2f}（そのうち 停止済み: フック・シェーバー・ブランケット・シーラー・グローブ）')
open('scripts/daily/o1123/mix_1124.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
