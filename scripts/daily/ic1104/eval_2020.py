# -*- coding: utf-8 -*-
"""11/04 20:20カット: 商品別の倍率＝(売上−値引−原価)÷広告費。
売上 = 0:00〜20:20（ShopifyQL 0〜18時台＋19時台＋各日20:00〜20:20の注文明細）、広告費 = 0〜19時台（Metaは1時間単位のため19:59まで）。
同じ定義で過去7日（10/28〜11/3）と比べ、終日（data/daily/*.csv）をどれだけ当てるかも測る"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read().split('\n'); g = {}
exec('\n'.join(src[17:33]), g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980
def rd(f): return [l.strip().split(',') for l in open(D + f) if l.strip() and not l.startswith('#')]
S = collections.defaultdict(lambda: [0, 0, 0]); A = collections.defaultdict(int)
def chk(fp, fs):
    T = collections.defaultdict(lambda: [0, 0])
    for d, n, gr, ds, q in rd(fp): T[d][0] += int(gr); T[d][1] += int(ds)
    for d, gr, ds, *_ in rd(fs): assert T[d] == [int(gr), int(ds)], (fp, d, T[d], gr, ds)
chk('sales_prod_0018.txt', 'sales_store_0018.txt'); chk('sales_prod_19.txt', 'sales_store_19.txt')
print('assert OK: 商品別の合計 == 店全体（0〜18時台・19時台とも8日一致）')
for f in ('sales_prod_0018.txt', 'sales_prod_19.txt'):
    for d, n, gr, ds, q in rd(f): v = S[(d, n)]; v[0] += int(gr); v[1] += int(ds); v[2] += int(q)
for d, o, n, q, gr, ds in rd('orders_2000_2020.txt'): v = S[(d, n)]; v[0] += int(gr); v[1] -= int(ds); v[2] += int(q)
A18 = collections.defaultdict(int); A19 = collections.defaultdict(int)
for d, n, c in rd('meta_allcamp_0018.txt'): A[(d, n)] += int(c); A18[d] += int(c)
for d, n, c in rd('meta_allcamp_19.txt'): A[(d, n)] += int(c); A19[d] += int(c)
DAYS = ['2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31', '2026-11-01', '2026-11-02', '2026-11-03']; T = '2026-11-04'
r = [A19[d] / A18[d] for d in DAYS]
print(f'Meta 19時台÷0〜18時台: 今日 {A19[T]/A18[T]:.3f}（19時台 {A19[T]:,}円）／ 過去7日 {min(r):.3f}〜{max(r):.3f} ＝ 今日の19時台は取り込み済みとみてよいか確認')
def units(n, gr, q):
    p = PRICE.get(n); return gr // p if p and gr % p == 0 else q
def cut(d, n):
    gr, ds, q = S[(d, n)]; return gr + ds, units(n, gr, q) * COST[n], A[(d, n)]
mult = lambda s, c, a: (s - c) / a
FS = collections.defaultdict(lambda: [0, 0]); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[(x['date'], x['name'])] = [int(x['gross']), int(x['disc'])]
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[(x['date'], x['campaign'])] += float(x['cost'])
def full(d, n):
    gr, ds = FS[(d, n)]; p = PRICE.get(n); u = gr // p if p and gr % p == 0 else None
    return None if u is None or not FA[(d, n)] else (gr - ds - u * COST[n]) / FA[(d, n)]
P = ['伸縮ワックス洗車ブラシ', 'マグネットドアクッション', 'W固定スマホ車載ホルダー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', '快適マジックインソール', 'ポータブルヒートシーラー', '姿勢サポートチェア', '4-in-1マルチクリーナー', 'コードレスダブルミスト加湿器']
pairs = [(mult(*cut(d, n)), full(d, n)) for n in P for d in DAYS if A[(d, n)] >= 3000 and full(d, n) is not None]
x = [a for a, b in pairs]; y = [b for a, b in pairs]; band = lambda v: 0 if v < 1.25 else (2 if v >= 1.86 else 1)
print(f'\n20:20の倍率 vs 終日（{len(pairs)}件）: 相関 r={st.correlation(x, y):.2f}・終日÷20:20 中央値 {st.median([b / a for a, b in pairs if a > 0]):.2f}・帯の一致 {sum(band(a) == band(b) for a, b in pairs)}/{len(pairs)}')
bad = [b for a, b in pairs if a < 1.25]; good = [b for a, b in pairs if a >= 1.86]
print(f'  20:20に1.25未満 {len(bad)}件 → 終日も1.25未満 {sum(b < 1.25 for b in bad)}件・最大 {max(bad):.2f}')
print(f'  20:20に1.86以上 {len(good)}件 → 終日も1.86以上 {sum(b >= 1.86 for b in good)}件・1.25未満 {sum(b < 1.25 for b in good)}件')
print('\n商品別（売上は20:20まで・広告費は19:59まで）')
for n in P + ['コードレス毛玉クリーナー', 'ワイド水切りワイパー']:
    s, c, a = cut(T, n); t = mult(s, c, a); xs = [mult(*cut(d, n)) for d in DAYS if A[(d, n)] >= 3000]
    y3 = full('2026-11-03', n); u = units(n, *[S[(T, n)][0], S[(T, n)][2]])
    past = f"中央値{st.median(xs):.2f}・{min(xs):.2f}〜{max(xs):.2f}・今日より低い日{sum(v < t for v in xs)}/{len(xs)}" if len(xs) >= 2 else '比較なし'
    print(f"  {n}: 今日 {t:.2f}（{u}個・売上{s:,}・広告{a:,}）／ {past} ／ 昨日終日 {'—' if y3 is None else f'{y3:.2f}'}")
def store(d):
    return sum(cut(d, n)[0] - cut(d, n)[1] for (dd, n) in list(S) if dd == d and n in COST) / sum(v for (dd, _), v in A.items() if dd == d)
xs = [store(d) for d in DAYS]
print(f'\n店全体（粗利÷全広告費・カタログ込み）今日 {store(T):.2f} ／ 過去7日 中央値{st.median(xs):.2f}・{min(xs):.2f}〜{max(xs):.2f}・今日より低い日{sum(v < store(T) for v in xs)}/7')
