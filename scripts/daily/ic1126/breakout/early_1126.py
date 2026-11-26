# -*- coding: utf-8 -*-
"""11/26 11時台「この状況を打開するなら新商品出すしかない？」
10/1 以降に広告を始めた23本（ic1122/plan/life_1122.txt の ②・開始日もそこから）について、出して1日目・2日目まで・3日目までの 個数・広告費・倍率を、
当たり（開始〜11/21 の利益 5万円以上）とそれ以外で並べる。数字は data/daily の CSV（w1125.py の関数）から積み直す。
1日目は出した時刻しだいで短い日がある（広告費で分かる）。個数は Shopify の売れた数（注文数ではない）"""
import io, contextlib, os, re, collections, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1125.py').read(), g)
A, ALLD, agg, WIN = g['A'], g['ALLD'], g['agg'], g['WIN']
rows = []; on = False
for l in open('scripts/daily/ic1122/plan/life_1122.txt'):
    if l.startswith('■ ②'): on = True; continue
    if l.startswith('■ ③'): break
    m = re.match(r'^  (.+?): (\d\d-\d\d)〜・(\d+)日・広告費 ([\d,]+)・利益 ([+\-][\d,]+)・最初の7日 ([\d.]+)・(停止|配信中)', l)
    if on and m: rows.append(dict(n=m.group(1), start='2026-' + m.group(2), p=int(m.group(5).replace(',', '').replace('+', '')), f7=float(m.group(6))))
assert len(rows) == 23
dn = lambda d, n: (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()
def cum(n, start, k):
    ds = [dn(start, i) for i in range(k)]; key = 'e' + n + start + str(k); WIN[key] = ds; N, DC, Q, K = agg(ds, key); a = A(ds, n)
    return Q.get(n, 0), a, ((N.get(n, 0) - K.get(n, 0)) / a if a else None)
out = []
def P(s=''): print(s); out.append(s)
f = lambda m: '—' if m is None else f'{m:.2f}'
for lab, sel in (('当たり（利益 5万円以上）', lambda r: r['p'] >= 50000), ('それ以外', lambda r: r['p'] < 50000)):
    v = sorted([r for r in rows if sel(r)], key=lambda r: -r['p']); P(f'■ {lab} {len(v)}本: 出して 1日目｜2日目まで｜3日目まで の 個数・広告費・倍率（最初の7日の倍率・利益）')
    for r in v:
        c = [cum(r['n'], r['start'], k) for k in (1, 2, 3)]; r['c'] = c
        P(f"  {r['n']}（{r['start'][5:]}〜）: " + '｜'.join(f"{q}個・{a:,.0f}円・{f(m)}" for q, a, m in c) + f"（7日 {r['f7']:.2f}・{r['p']:+,}）")
    for k, kl in ((0, '1日目'), (1, '2日目まで'), (2, '3日目まで')):
        P(f"  → {kl}: 0個だった {sum(r['c'][k][0] == 0 for r in v)}本・倍率 1.25 以上 {sum((r['c'][k][2] or 0) >= 1.25 for r in v)}本・1.5 以上 {sum((r['c'][k][2] or 0) >= 1.5 for r in v)}本／{len(v)}本")
hit = [r for r in rows if r['p'] >= 50000]; non = [r for r in rows if r['p'] < 50000]
P('■ 見切りの線を当てはめると（2日目まで・3日目までの通算の倍率）')
for k, kl in ((1, '2日目まで'), (2, '3日目まで')):
    for th in (1.0, 1.25, 1.5):
        cut_h = [r['n'] for r in hit if (r['c'][k][2] or 0) < th]; cut_n = [r for r in non if (r['c'][k][2] or 0) < th]
        P(f"  {kl}の倍率が {th} 未満なら止める: 当たり {len(hit)}本のうち止めてしまう {len(cut_h)}本（{'・'.join(cut_h) or 'なし'}）・それ以外 {len(non)}本のうち止められる {len(cut_n)}本（その商品の 開始〜11/21 の利益の合計 {sum(r['p'] for r in cut_n):+,}）")
P('■ 1日目に 0個だった商品（1日目の広告費 2,400円以上）')
z = [r for r in rows if r['c'][0][0] == 0 and r['c'][0][1] >= 2400]
P(f"  {len(z)}本・うち当たり {sum(r['p'] >= 50000 for r in z)}本｜" + '・'.join(f"{r['n']} {r['c'][0][1]:,.0f}円（その後 {r['p']:+,}）" for r in sorted(z, key=lambda r: -r['p'])))
P('  当たり6本の1日目: ' + '・'.join(f"{r['n']} {r['c'][0][0]}個／{r['c'][0][1]:,.0f}円" for r in hit))
open(D0 + 'early_1126.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
