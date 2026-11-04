# -*- coding: utf-8 -*-
"""11/04 20時台: 商品別の倍率（(売上−値引−原価)÷広告費）を、今日0〜18時台 vs 過去7日（10/28〜11/3）の同じ0〜18時台で比べる。
あわせて「0〜18時台の倍率」が終日の倍率をどれだけ当てるか（10/28〜11/3・広告3,000円以上）を測る。終日は data/daily/*.csv"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read().split('\n'); g = {}
exec('\n'.join(src[17:33]), g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980
def rd(f):
    return [l.strip().split(',') for l in open(D + f) if l.strip() and not l.startswith('#')]
S = collections.defaultdict(lambda: [0, 0, 0]); A = collections.defaultdict(int)
for d, n, gr, ds, q in rd('sales_prod_0018.txt'): S[(d, n)] = [int(gr), int(ds), int(q)]
for d, n, c in rd('meta_allcamp_0018.txt'): A[(d, n)] += int(c)
for d, gr, ds, o in rd('sales_store_0018.txt'):
    sg = sum(v[0] for (dd, _), v in S.items() if dd == d); sd = sum(v[1] for (dd, _), v in S.items() if dd == d)
    assert (sg, sd) == (int(gr), int(ds)), (d, sg, int(gr), sd, int(ds))
print('assert OK: 商品別の合計 == 店全体（8日とも gross・値引が一致）')
def units(n, gr, q):
    p = PRICE.get(n); return gr // p if p and gr % p == 0 else q
def mult(sales, cost, ad): return (sales - cost) / ad if ad else None
def cut(d, n):
    gr, ds, q = S[(d, n)]; u = units(n, gr, q); return gr + ds, u * COST[n], A[(d, n)]
DAYS = ['2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31', '2026-11-01', '2026-11-02', '2026-11-03']; T = '2026-11-04'
# 終日（CSV）
FS = collections.defaultdict(lambda: [0, 0]); FA = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[(r['date'], r['name'])] = [int(r['gross']), int(r['disc'])]
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[(r['date'], r['campaign'])] += float(r['cost'])
def full(d, n):
    gr, ds = FS[(d, n)]; p = PRICE.get(n); u = gr // p if p and gr % p == 0 else None
    return None if u is None or not FA[(d, n)] else (gr - ds - u * COST[n]) / FA[(d, n)]
P = ['伸縮ワックス洗車ブラシ', 'マグネットドアクッション', 'W固定スマホ車載ホルダー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', '快適マジックインソール', 'ポータブルヒートシーラー', '姿勢サポートチェア', '4-in-1マルチクリーナー', 'コードレスダブルミスト加湿器']
# 当て方の検証
pairs = []
for n in P:
    for d in DAYS:
        s, c, a = cut(d, n)
        if a >= 3000 and full(d, n) is not None: pairs.append((n, d, mult(s, c, a), full(d, n)))
x = [p[2] for p in pairs]; y = [p[3] for p in pairs]
band = lambda v: 0 if v < 1.25 else (2 if v >= 1.86 else 1)
print(f'\n0〜18時台の倍率 vs 終日の倍率（{len(pairs)}件・商品×日）: 相関 r={st.correlation(x, y):.2f}・終日÷19時の中央値 {st.median([b / a for a, b in zip(x, y) if a > 0]):.2f}')
print(f'  帯（1.25未満／1.25〜1.86／1.86以上）が19時と終日で一致: {sum(band(a) == band(b) for a, b in zip(x, y))}/{len(pairs)}')
bad = [(a, b) for a, b in zip(x, y) if a < 1.25]
print(f'  19時に1.25未満だった{len(bad)}件 → 終日も1.25未満 {sum(b < 1.25 for a, b in bad)}件・終日の値 {sorted(round(b, 2) for a, b in bad)}')
good = [(a, b) for a, b in zip(x, y) if a >= 1.86]
print(f'  19時に1.86以上だった{len(good)}件 → 終日も1.86以上 {sum(b >= 1.86 for a, b in good)}件・1.25未満に落ちた {sum(b < 1.25 for a, b in good)}件')
print('\n商品別（0〜18時台）: 今日 ／ 過去7日の同時刻（中央値・範囲・今日より低い日）／ 昨日11/3終日（CSV・11/3広告費は暫定）')
for n in P + ['コードレス毛玉クリーナー', 'ワイド水切りワイパー']:
    s, c, a = cut(T, n); t = mult(s, c, a)
    xs = [mult(*cut(d, n)) for d in DAYS if A[(d, n)] >= 3000]
    y3 = full('2026-11-03', n)
    past = f"中央値{st.median(xs):.2f}・{min(xs):.2f}〜{max(xs):.2f}・今日より低い日{sum(v < t for v in xs)}/{len(xs)}" if len(xs) >= 2 else '比較できる日なし'
    print(f"  {n}: 今日 {t:.2f}（売上{s:,}・広告{a:,}）／ {past} ／ 昨日終日 {y3:.2f}" if y3 is not None else f"  {n}: 今日 {t:.2f}（売上{s:,}・広告{a:,}）／ {past} ／ 昨日終日 —")
ts = sum(cut(T, n)[0] - cut(T, n)[1] for n in COST if (T, n) in S); ta = sum(v for (d, _), v in A.items() if d == T)
print(f'\n店全体（全商品の粗利÷全広告費・カタログ込み）今日0〜18時台 {ts/ta:.2f}', end='')
xs = []
for d in DAYS:
    xs.append(sum(cut(d, n)[0] - cut(d, n)[1] for n in COST if (d, n) in S) / sum(v for (dd, _), v in A.items() if dd == d))
print(f' ／ 過去7日 中央値{st.median(xs):.2f}・{min(xs):.2f}〜{max(xs):.2f}・今日より低い日{sum(v < ts/ta for v in xs)}/7')
