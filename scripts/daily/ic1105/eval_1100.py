# -*- coding: utf-8 -*-
"""11/05 11:14: 店全体（Shopify 0〜10時台＋注文は11:14まで EXACT）と商品別の個数（0〜10時台）を過去7日の同じ時間帯と比べる。
広告費あたりの売上は Meta が確定している0〜9時台で見る（今日の10時台はキャッシュ経由で着地が未確認）"""
import os, statistics as st, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
ST = {r[0]: list(map(int, r[1:])) for r in rd('store_0010.txt')}
S9 = {r[0]: list(map(int, r[1:])) for r in rd('store_0009.txt')}
H10 = collections.defaultdict(lambda: [0, 0])
for d, n, g, ds, q in rd('sales_prod_10.txt'): H10[d][0] += int(g); H10[d][1] += int(ds)
for d in ST: assert (S9[d][0] + H10[d][0], S9[d][1] + H10[d][1]) == (ST[d][0], ST[d][1]), d   # 0〜9時台＋10時台（商品別の合計）＝0〜10時台（店全体）
print('assert OK: 0〜9時台＋10時台の商品別合計 == 0〜10時台の店全体（8日）')
T = '2026-11-05'; P = sorted(d for d in ST if d < T)
def rk(lab, f, fm='{:,.0f}'):
    t = f(T); xs = [f(d) for d in P]
    print(f'  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}・{fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日{sum(x < t for x in xs)}/7')
rk('注文（11:14まで）', lambda d: ST[d][6])
rk('売上（値引後・0〜10時台）', lambda d: ST[d][0] + ST[d][1]); rk('来訪（0〜10時台）', lambda d: ST[d][3])
rk('来訪→購入%（0〜10時台）', lambda d: ST[d][2] / ST[d][3] * 100, '{:.2f}'); rk('カゴ投入率%', lambda d: ST[d][4] / ST[d][3] * 100, '{:.2f}')
U = collections.defaultdict(int)
PRICE = {'伸縮ワックス洗車ブラシ': 4980, '姿勢サポートチェア': 5980, '4-in-1マルチクリーナー': 6980, 'コードレスダブルミスト加湿器': 4980}
for f in ('sales_prod_0009.txt', 'sales_prod_10.txt'):
    for d, n, g, ds, q in rd(f): U[(d, n)] += int(g) // PRICE.get(n, 3980) if int(g) % PRICE.get(n, 3980) == 0 else int(q)
print('\n商品別の個数（0〜10時台）: 今日 ／ 過去7日の中央値（範囲）')
for n in ['伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション', '快適マジックインソール', 'ポータブルヒートシーラー', '姿勢サポートチェア', '4-in-1マルチクリーナー', 'コードレスダブルミスト加湿器', 'ワイド水切りワイパー', 'ナノバブルシャワーヘッド']:
    xs = [U[(d, n)] for d in P]
    print(f'  {n}: {U[(T, n)]} ／ {st.median(xs)}（{min(xs)}〜{max(xs)}）')
