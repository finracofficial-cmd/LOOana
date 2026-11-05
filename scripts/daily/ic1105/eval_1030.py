# -*- coding: utf-8 -*-
"""11/05 10:30: 店全体（注文は10:30まで EXACT、売上・来訪・広告は0〜9時台）と商品別（0〜9時台）を過去7日（10/29〜11/4）の同じ時間帯と比べる。
商品別の倍率=(売上−値引−原価)÷広告費。この時刻の倍率が終日をどれだけ当てるかも測る（終日は data/daily/*.csv）"""
import os, csv, collections, statistics as st, math
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read().split('\n'); g = {}
exec('\n'.join(src[17:33]), g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0, 0]); A = collections.defaultdict(lambda: [0, 0, 0, 0]); ST = {}
for d, n, gr, ds, q in rd('sales_prod_0009.txt'): S[(d, n)] = [int(gr), int(ds), int(q)]
for d, n, *v in rd('meta_camp_0009.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0009.txt'): ST[d] = [int(x) for x in v]
for d in ST:
    assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0] and sum(v[1] for (dd, _), v in S.items() if dd == d) == ST[d][1], d
print('assert OK: 商品別の合計 == 店全体（0〜9時台・8日）')
T = '2026-11-05'; P = sorted(d for d in ST if d < T)
def acct(d): return sum(v[0] for (dd, _), v in A.items() if dd == d)
def rk(lab, f, fm='{:,.0f}'):
    t = f(T); xs = [f(d) for d in P]
    print(f'  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}・{fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日{sum(x < t for x in xs)}/7')
print('■ 店全体')
rk('注文（10:30まで）', lambda d: ST[d][7])
rk('注文（0〜9時台）', lambda d: ST[d][2]); rk('来訪（0〜9時台）', lambda d: ST[d][3])
rk('来訪→購入%', lambda d: ST[d][2] / ST[d][3] * 100, '{:.2f}'); rk('カゴ投入率%', lambda d: ST[d][4] / ST[d][3] * 100, '{:.2f}')
rk('売上（gross−値引・0〜9時台）', lambda d: ST[d][0] + ST[d][1]); rk('広告費（0〜9時台）', acct)
rk('売上÷広告費', lambda d: (ST[d][0] + ST[d][1]) / acct(d), '{:.2f}')
imp = lambda d: sum(v[1] for (dd, _), v in A.items() if dd == d); clk = lambda d: sum(v[2] for (dd, _), v in A.items() if dd == d)
rk('CPM', lambda d: acct(d) / imp(d) * 1000); rk('CTR%', lambda d: clk(d) / imp(d) * 100, '{:.2f}'); rk('1来訪(Shopify)あたり広告費', lambda d: acct(d) / ST[d][3], '{:.1f}')
lam = ST[T][3] * sum(ST[d][2] for d in P) / sum(ST[d][3] for d in P); k = ST[T][2]
print(f'  来訪{ST[T][3]}×過去7日の購入率 = {lam:.1f}件 → 実際{k}件・この数以下 {sum(math.exp(-lam)*lam**i/math.factorial(i) for i in range(k+1))*100:.0f}%')
def units(n, gr, q):
    p = PRICE.get(n); return gr // p if p and gr % p == 0 else q
def mult(d, n):
    gr, ds, q = S[(d, n)]; a = A[(d, n)][0]
    return None if not a else (gr + ds - units(n, gr, q) * COST.get(n, 0)) / a
FS = collections.defaultdict(lambda: [0, 0]); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[(x['date'], x['name'])] = [int(x['gross']), int(x['disc'])]
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[(x['date'], x['campaign'])] += float(x['cost'])
def full(d, n):
    gr, ds = FS[(d, n)]; p = PRICE.get(n); u = gr // p if p and gr % p == 0 else None
    return None if u is None or not FA[(d, n)] else (gr - ds - u * COST[n]) / FA[(d, n)]
NM = ['伸縮ワックス洗車ブラシ', 'マグネットドアクッション', 'W固定スマホ車載ホルダー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', '快適マジックインソール', 'ポータブルヒートシーラー', '姿勢サポートチェア', '4-in-1マルチクリーナー', 'コードレスダブルミスト加湿器']
pr = [(mult(d, n), full(d, n)) for n in NM for d in P if A[(d, n)][0] >= 2000 and full(d, n) is not None]
x = [a for a, b in pr]; y = [b for a, b in pr]
print(f'\n0〜9時台の商品別倍率 vs 終日（{len(pr)}件）: 相関 r={st.correlation(x, y):.2f}。0〜9時台に1.25未満 {sum(a < 1.25 for a in x)}件 → 終日も1.25未満 {sum(a < 1.25 and b < 1.25 for a, b in pr)}件')
print('\n■ 商品別（0〜9時台）: 今日 個数・広告費・倍率 ／ 過去7日の同時刻 個数の中央値・倍率の中央値')
for n in NM + ['ワイド水切りワイパー', 'ナノバブルシャワーヘッド']:
    gr, ds, q = S[(T, n)]; u = units(n, gr, q) if gr else 0; a = A[(T, n)][0]; m = mult(T, n)
    pu = [units(n, S[(d, n)][0], S[(d, n)][2]) if S[(d, n)][0] else 0 for d in P if A[(d, n)][0]]; pm = [mult(d, n) for d in P if A[(d, n)][0] >= 2000]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'} ／ 個数中央値 {st.median(pu) if pu else '—'}・倍率中央値 {f'{st.median(pm):.2f}' if pm else '—'}（{len(pm)}日）")
