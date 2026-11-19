# -*- coding: utf-8 -*-
"""11/19 「夏の時のような収益を出すために何をすればいいのか」: 計画の土台の数字。
summer_vs_now.json（週ごと・商品別 広告費と倍率。data/daily の積み直し）と data/daily から。商品の利益＝（倍率−1）×広告費"""
import json, collections, io, contextlib
O = {o['w']: o for o in json.load(open('scripts/daily/ic1119/summer_vs_now.json'))}
def per(ws):
    n = sum(O[w]['n'] for w in ws); a = sum(O[w]['a'] for w in ws); p = sum(O[w]['p'] for w in ws); s = sum(O[w]['s'] for w in ws); k = sum(O[w]['k'] for w in ws)
    P = collections.defaultdict(lambda: [0.0, 0.0])
    for w in ws:
        for nm, ad, m, q in O[w]['prods']: P[nm][0] += ad / n; P[nm][1] += (m - 1) * ad / n
    return n, a / n, (s - k) / a, p / n, P
SUM = ['2026-07-20', '2026-07-27', '2026-08-03', '2026-08-10', '2026-08-17', '2026-08-24']; SEP = ['2026-08-31', '2026-09-07', '2026-09-14', '2026-09-21']
E_NOV = ['2026-11-02']; NOW = ['2026-11-09', '2026-11-16']
print('■ 段階ごとの水準（広告費/日・倍率・利益/日）')
for lab, ws in (('夏 7/20〜8/30', SUM), ('9月 8/31〜9/27', SEP), ('11/2〜8（当たり3本が出ていた週）', E_NOV), ('11/9〜18', NOW)):
    n, a, m, p, P = per(ws); print(f'  {lab}: {a:,.0f}・{m:.2f}・{p:+,.0f}')
n, a, m, p, P9 = per(SEP); n2, a2, m2, p2, PN = per(NOW)
print('■ 9月の利益の内訳（商品の利益/日・広告費/日・倍率）と 11/9〜18 との差')
for nm, (ad, pf) in sorted(P9.items(), key=lambda x: -x[1][1])[:12]:
    ad2, pf2 = PN.get(nm, (0, 0)); print(f'  {nm[:16]}: {pf:+,.0f}（{ad:,.0f}・{pf/ad+1:.2f}） → 今 {pf2:+,.0f}（{ad2:,.0f}{"・%.2f" % (pf2/ad2+1) if ad2 else ""}）差 {pf2-pf:+,.0f}')
print('■ 11/9〜18 にあって 9月にない利益（上位）')
for nm, (ad, pf) in sorted(PN.items(), key=lambda x: -x[1][1])[:10]:
    if P9.get(nm, (0, 0))[0] < 1000: print(f'  {nm[:16]}: {pf:+,.0f}（{ad:,.0f}・{pf/ad+1:.2f}）')
# 新商品（10/20 以降に初めて広告を出した商品）: 出してからの通算の利益と、利益が出た日数
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1118.py').read(), g)
WIN, agg, A, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']
NEW = [('伸縮ワックス洗車ブラシ', '2026-10-19'), ('コードレスダブルミスト加湿器', '2026-10-20'), ('高見えレザードアポケット', '2026-10-22'), ('マグネットドアクッション', '2026-10-31'), ('ふわとろ高密度ブランケット', '2026-10-31'),
       ('ファスナー修理キット', '2026-11-03'), ('コードレス毛玉クリーナー', '2026-11-03'), ('ワイド水切りワイパー', '2026-11-04'), ('クリアビューレインガードフィルム', '2026-11-05'), ('シリコンホールド膝サポーター', '2026-11-08'),
       ('アーチフィット逆ヒールサンダル', '2026-11-10'), ('すき間収納シートポケット', '2026-11-11'), ('防風あったか裏起毛パンツ', '2026-11-11'), ('3WAY着る電気ブランケット', '2026-11-13'), ('360°マルチクリップ車載スマホホルダー', '2026-11-16'), ('裏起毛タッチ防寒グローブ', '2026-11-17')]
print('■ 10/19 以降に出した新商品（出し直しは除く）: 出してから 11/18 までの 広告費・倍率・利益・最初の7日の利益')
tot = 0; hit = 0; rows = []
for n_, st in NEW:
    ds = [d for d in ALLD if d >= st]; key = 'p' + n_; WIN[key] = ds; N, DC, Q, K = agg(ds, key); ad = A(ds, n_); pf = N.get(n_, 0) - K.get(n_, 0) - ad
    d7 = ds[:7]; k7 = 'p7' + n_; WIN[k7] = d7; N7, _, Q7, K7 = agg(d7, k7); a7 = A(d7, n_); p7 = N7.get(n_, 0) - K7.get(n_, 0) - a7
    rows.append((pf, n_, st, ad, p7)); tot += pf; hit += pf > 30000
for pf, n_, st, ad, p7 in sorted(rows, reverse=True): print(f'  {n_[:16]}（{st[5:]}〜）: 広告費 {ad:,.0f}・利益 {pf:+,.0f}・最初の7日 {p7:+,.0f}')
print(f'  {len(rows)}本の合計 {tot:+,.0f}（1本あたり {tot/len(rows):+,.0f}）・利益3万円超 {hit}本・赤字の合計 {sum(r[0] for r in rows if r[0] < 0):+,.0f}')
