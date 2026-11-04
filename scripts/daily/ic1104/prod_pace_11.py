# -*- coding: utf-8 -*-
"""11/04 0〜11時の商品別注文数（Shopify orders 一覧・商品名を短縮して転記）を、7日(10/28-11/3)の注文ペース×11時までの割合（過去16日の中央値）と比べる。ポアソンで偶然の範囲か見る"""
import io, contextlib, re, math, statistics as st, os, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
g = {'__file__': D + 'ic1104_11.py', '__name__': 'x'}
with contextlib.redirect_stdout(io.StringIO()): exec(open(g['__file__']).read(), g)
rows, T = g['rows'], g['T']
s = open(D + '../mk1104full.py').read()
od = eval(re.search(r"ORDD = (\{.*?\})\n", s, re.S).group(1)); ORD = eval(re.search(r"ORD = (\{.*?\})\n", s, re.S).group(1))
L = [l.rstrip('\n').split('\t') for l in open(D + 'orders_0011.tsv')]
assert len(L) == g['oc']['d1104'] == 27
C = collections.Counter(n for _, items in L for n in set(items.split('|')) if n != 'VIP特典')
sh = [rows[d][0] / od[d.isoformat()] for d in rows if d < T]; m = st.median(sh)
print(f'11時までの注文の割合 中央値{m:.1%}（{min(sh):.1%}〜{max(sh):.1%}・16日）')
P = lambda k, l: sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
for n in ['伸縮ワックス洗車ブラシ', 'W固定スマホ車載ホルダー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'マグネットドアクッション', '姿勢サポートチェア', 'ポータブルヒートシーラー', '4-in-1マルチクリーナー', '快適マジックインソール']:
    k = C.get(n, 0); lam = ORD[n] / 7 * m
    print(f"{n}: 今日{k}件／普段のペース{lam:.1f}件（7日{ORD[n]}件）　この数以下{P(k, lam):.0%}・この数以上{1 - P(k - 1, lam) if k else 1:.0%}")
