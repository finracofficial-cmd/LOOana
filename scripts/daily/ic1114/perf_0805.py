# -*- coding: utf-8 -*-
"""11/14(土) 08:0x 「今時点のパフォーマンスを効率で」「CVRがあきらかに悪い、なんで？」
0〜7時台を過去21日（10/24〜11/13）の同じ時刻と比べる。偶然かどうかは件数から（注文はポアソン、決済完了は二項）。日中の数字なので予算の判定には使わない"""
import json, csv, re, math, collections, statistics as st
D = 'scripts/daily/ic1114/'
T = '2026-11-14'
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3])) for r in json.load(open(D + 'store_sales_0007.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0007.json'))['rows']}
N = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'sess_0105.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0007.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-24'
def band(lab, f, fm, note=''):
    t = f(T); xs = [f(d) for d in P]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('過去21日の範囲の外（下）' if t < min(xs) else '過去21日の範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/21 → {out}{note}")
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
def binom_le(k, n, p): return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
print('■ 店全体（0〜7時台・過去21日の同時刻）')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('注文', lambda d: SS[d][1], '{}')
band('来訪', lambda d: SE[d][0], '{}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('決済画面到達÷カート%', lambda d: SE[d][2] / SE[d][1] * 100, '{:.0f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
band('クリック率%（Meta）', lambda d: MA[d][2] / MA[d][1] * 100, '{:.2f}')
band('CPM（Meta）', lambda d: MA[d][0] / MA[d][1] * 1000, '{:,.0f}')
band('Metaカート÷着地%', lambda d: MA[d][4] / MA[d][3] * 100, '{:.1f}')
# 偶然の判定（過去21日を合わせた率から）
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪{SE[T][0]}×過去21日の購入率{cvr*100:.2f}%＝期待 {lam:.1f}）・この数以下になる確率 {pois_le(SS[T][1], lam)*100:.1f}%")
cr = sum(SE[d][1] for d in P) / sum(SE[d][0] for d in P); print(f"  → カート {SE[T][1]}（期待 {cr*SE[T][0]:.1f}）・以下になる確率 {pois_le(SE[T][1], cr*SE[T][0])*100:.0f}%")
rc = sum(SE[d][2] for d in P) / sum(SE[d][1] for d in P); print(f"  → 決済画面 {SE[T][2]}（カート{SE[T][1]}×{rc*100:.0f}%＝期待 {rc*SE[T][1]:.1f}）・以下になる確率 {binom_le(SE[T][2], SE[T][1], min(rc,0.999))*100:.0f}%")
cp = sum(SE[d][3] for d in P) / sum(SE[d][2] for d in P); print(f"  → 決済完了 {SE[T][3]}（決済画面{SE[T][2]}×{cp*100:.0f}%＝期待 {cp*SE[T][2]:.1f}）・以下になる確率 {binom_le(SE[T][3], SE[T][2], cp)*100:.1f}%")
print('■ 1〜5時台だけ（過去21日）')
for lab, i in [('来訪', 0), ('カート', 1), ('決済画面', 2), ('決済完了', 3)]:
    xs = [N[d][i] for d in P]; print(f"  {lab}: 今日 {N[T][i]}・過去21日 {min(xs)}〜{max(xs)}（中央値 {st.median(xs)}）・今日より低い日 {sum(x < N[T][i] for x in xs)}/21")
cp5 = sum(N[d][3] for d in P) / sum(N[d][0] for d in P); print(f"  → 1〜5時台の決済完了 {N[T][3]}（来訪{N[T][0]}×{cp5*100:.2f}%＝期待 {cp5*N[T][0]:.1f}）・以下になる確率 {pois_le(N[T][3], cp5*N[T][0])*100:.1f}%")
x6 = [SE[d][3] - N[d][3] for d in P]; print(f"  0時台＋6〜7時台の決済完了: 今日 {SE[T][3]-N[T][3]}・過去21日 {min(x6)}〜{max(x6)}（中央値 {st.median(x6)}）")
# 0〜7時台と終日の関係
FS, FA = collections.defaultdict(int), collections.defaultdict(float)
for x in csv.DictReader(open('data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open('data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
H = [d for d in P if d in FA]
xa = [SS[d][0] / MA[d][0] for d in H]; ya = [FS[d] / FA[d] for d in H]
print(f"■ 0〜7時台と終日の売上÷広告費の関係（{H[0]}〜{H[-1]}・{len(H)}日）: r={st.correlation(xa, ya):.2f}")
# 商品別（0〜7時台）: 注文 と 今日の広告費からの期待（過去7日の同時刻の 注文÷広告費）
nm = lambda t: re.sub(r'^(LOOTY|LOTTY)\s*', '', re.sub(r'【[^】]*】', '', t).strip()).strip()
PO = collections.defaultdict(int)
for d, t, g, dc, o in json.load(open(D + 'sales_prod_0007.json'))['rows']:
    if int(g): PO[(d, nm(t))] += int(o)
MC = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'meta_camp_0007.txt'):
    if l[0] != '#': p = l.strip().split(','); MC[(p[0], p[1])] = [int(x) for x in p[2:]]
P7 = [f'2026-11-{x:02d}' for x in range(7, 14)]
print('■ 商品別（0〜7時台）: 注文（今日の広告費からの期待・過去7日の同時刻の率）・広告費')
for camp in sorted({c for (d, c) in MC if d == T and MC[(d, c)][0] > 0}, key=lambda c: -MC[(T, c)][0]):
    a = MC[(T, camp)][0]; o = PO.get((T, camp), 0)
    if camp.startswith('カタログ'): print(f"  {camp}: 広告費 {a:,}（商品に分けられない）"); continue
    a7 = sum(MC[(d, camp)][0] for d in P7); o7 = sum(PO.get((d, camp), 0) for d in P7)
    if not a7: print(f"  {camp}: {o}注文・広告費 {a:,}（過去7日の比べる数字なし）"); continue
    lam = o7 / a7 * a
    print(f"  {camp}: {o}注文（期待 {lam:.1f}）・以下になる確率 {pois_le(o, lam)*100:.0f}%・広告費 {a:,}")
