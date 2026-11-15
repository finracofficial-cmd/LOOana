# -*- coding: utf-8 -*-
"""11/15(日) 20:3x 「20時38分までのパフォーマンスどう？効率含めて」（perf_1240.py を 0〜19時台に置き換え）
0〜19時台を過去21日（10/25〜11/14）の同じ時刻と比べる。偶然かどうかは件数から（注文はポアソン、決済完了は二項）。日中の数字なので予算の判定には使わない
入力: store_sales_0019.json・store_sess_0019.json・meta_acct_0019.txt・meta_camp_0019.txt・sales_prod_0019.txt（すべて 20:3x 取得）"""
import json, csv, math, collections, statistics as st
R = __file__.rsplit('/scripts/', 1)[0] + '/'
D = R + 'scripts/daily/ic1115/'
T = '2026-11-15'
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3]), int(r[1])) for r in json.load(open(D + 'store_sales_0019.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0019.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0019.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-25'
def band(lab, f, fm):
    t = f(T); xs = [f(d) for d in P]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('過去21日の範囲の外（下）' if t < min(xs) else '過去21日の範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/21 → {out}")
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
def binom_le(k, n, p): return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
print('■ 店全体（0〜19時台・過去21日の同時刻）')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('注文', lambda d: SS[d][1], '{}')
band('来訪', lambda d: SE[d][0], '{}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('決済画面到達÷カート%', lambda d: SE[d][2] / SE[d][1] * 100, '{:.0f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
print('  クリック率・CPM・来訪÷クリック: 11/15 の Meta のクリックと表示の取り込みが遅れている（クリック 1,146 ＜ 着地 1,654）ので比べない')
band('来訪÷広告費1万円', lambda d: SE[d][0] / MA[d][0] * 10000, '{:.0f}')
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪{SE[T][0]}×過去21日の購入率{cvr*100:.2f}%＝期待 {lam:.1f}）・この数以下になる確率 {pois_le(SS[T][1], lam)*100:.1f}%")
cr = sum(SE[d][1] for d in P) / sum(SE[d][0] for d in P); print(f"  → カート {SE[T][1]}（期待 {cr*SE[T][0]:.1f}）・以下になる確率 {pois_le(SE[T][1], cr*SE[T][0])*100:.1f}%")
cp = sum(SE[d][3] for d in P) / sum(SE[d][2] for d in P); print(f"  → 決済完了 {SE[T][3]}（決済画面{SE[T][2]}×{cp*100:.0f}%＝期待 {cp*SE[T][2]:.1f}）・以下になる確率 {binom_le(SE[T][3], SE[T][2], cp)*100:.1f}%")
FS, FA = collections.defaultdict(int), collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
H = [d for d in P if d in FA]
print(f"■ 0〜19時台と終日の売上÷広告費の関係（{H[0]}〜{H[-1]}・{len(H)}日）: r={st.correlation([SS[d][0]/MA[d][0] for d in H], [FS[d]/FA[d] for d in H]):.2f}")
# 商品別
PO = collections.defaultdict(int); PG = collections.defaultdict(int)
for l in open(D + 'sales_prod_0019.txt'):
    if l[0] != '#': d, n, g, dc, o = l.strip().split(','); PO[(d, n)] += int(o); PG[d] += int(g)
for d in PG: assert PG[d] == SS[d][2], (d, PG[d], SS[d][2])   # 商品別の売上（値引前）の合計＝店全体
MC = collections.defaultdict(lambda: [0] * 6); MCD = collections.defaultdict(int)
for l in open(D + 'meta_camp_0019.txt'):
    if l[0] != '#': p = l.strip().split(','); MC[(p[0], p[1])] = [int(x) for x in p[2:]]; MCD[p[0]] += int(p[2])
for d in MCD: assert abs(MCD[d] - MA[d][0]) <= max(5, MA[d][0] * 0.01), (d, MCD[d], MA[d][0])   # キャンペーン別の合計＝アカウント
ALIAS = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック'}
P7 = [f'2026-11-{x:02d}' for x in range(8, 15)]
print('■ 商品別（0〜19時台・今日広告費が出た全キャンペーン）: 注文（今日の広告費からの期待・過去7日の同時刻の 注文÷広告費）・広告費・クリック率')
for camp in sorted({c for (d, c) in MC if d == T and MC[(d, c)][0] > 0}, key=lambda c: -MC[(T, c)][0]):
    a, im, cl = MC[(T, camp)][:3]; n = ALIAS.get(camp, camp); o = PO.get((T, n), 0)
    ctr = f'Meta カート {MC[(T, camp)][4]}'
    if camp.startswith('カタログ'): print(f"  {camp}: 広告費 {a:,}（商品に分けられない）・{ctr}"); continue
    a7 = sum(MC[(d, camp)][0] for d in P7); o7 = sum(PO.get((d, n), 0) for d in P7)
    if not a7: print(f"  {camp}: {o}注文・広告費 {a:,}・{ctr}（過去7日の比べる数字なし）"); continue
    lam = o7 / a7 * a
    print(f"  {camp}: {o}注文（期待 {lam:.1f}）・以下になる確率 {pois_le(o, lam)*100:.0f}%・広告費 {a:,}・{ctr}")
