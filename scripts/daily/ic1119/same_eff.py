# -*- coding: utf-8 -*-
"""11/19 「効率は同じなのに広告費を下げたから利益が少ない？」: summer_vs_now.json（週ごと・商品別 広告費と倍率）から
10月前半（10/12〜25）と直近（11/5〜18 は週の区切りがずれるので 11/2〜15 の2週）を、店全体とナノ・ほかの商品に分ける。
商品の利益＝（倍率−1）×広告費（カタログ広告費・広告なし商品・優先配送は店全体にだけ入る）"""
import json, collections
O = {o['w']: o for o in json.load(open('scripts/daily/ic1119/summer_vs_now.json'))}
def per(ws):
    n = sum(O[w]['n'] for w in ws); s = sum(O[w]['s'] for w in ws); k = sum(O[w]['k'] for w in ws); a = sum(O[w]['a'] for w in ws); p = sum(O[w]['p'] for w in ws)
    P = collections.defaultdict(lambda: [0.0, 0.0])
    for w in ws:
        for nm, ad, m, q in O[w]['prods']: P[nm][0] += ad; P[nm][1] += (m - 1) * ad
    return n, s, k, a, p, P
for lab, ws in (('夏 7/20〜8/30', ['2026-07-20', '2026-07-27', '2026-08-03', '2026-08-10', '2026-08-17', '2026-08-24']), ('9月 8/31〜9/27', ['2026-08-31', '2026-09-07', '2026-09-14', '2026-09-21']),
                ('10/12〜25', ['2026-10-12', '2026-10-19']), ('11/2〜15', ['2026-11-02', '2026-11-09'])):
    n, s, k, a, p, P = per(ws)
    na, npf = P['ナノガラス脱毛パッド']
    oa = a - na; op = p - npf
    print(f'{lab}: 店 広告費/日 {a/n:,.0f}・倍率 {(s-k)/a:.2f}・利益/日 {p/n:+,.0f} ｜ ナノ 広告費/日 {na/n:,.0f}・倍率 {npf/na+1:.2f}・利益/日 {npf/n:+,.0f} ｜ ナノ以外 広告費/日 {oa/n:,.0f}・倍率 {(op+oa)/oa:.2f}・利益/日 {op/n:+,.0f}')
