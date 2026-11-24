# -*- coding: utf-8 -*-
"""11/24「売れてる商品は毎日ぶれなく稼ぎ続けてる」の確認: 直近14日（11/10〜23）の商品ごとの 日別の倍率の幅・1.25 未満の日数・1日の注文数（中央値）。入力: w1123.py・o1123 までの orders_by_product（注文数は Shopify の日別 個数÷1注文の個数ではなく、ShopifyQL の orders を使いたいので daily の個数で代用しない）"""
import io, contextlib, statistics as st
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN = g['A'], g['ALLD'], g['agg'], g['WIN']
D = ALLD[-14:]; DAY = {}
for d in D:
    WIN['s' + d] = [d]; N, Dc, Q, K = agg([d], 's' + d); DAY[d] = (N, Q, K)
out = []
for n in ('伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', 'ワイド水切りワイパー', '快適マジックインソール', '4-in-1マルチクリーナー', 'マグネットドアクッション', 'スマートノーズEMS美顔器'):
    ms = []; qs = []
    for d in D:
        a = A([d], n)
        if a > 0: N, Q, K = DAY[d]; ms.append((N.get(n, 0) - K.get(n, 0)) / a); qs.append(Q.get(n, 0))
    s = f'  {n}: {len(ms)}日・倍率 {min(ms):.2f}〜{max(ms):.2f}（中央値 {st.median(ms):.2f}）・1.25 未満の日 {sum(m < 1.25 for m in ms)}日・1日の個数 中央値 {st.median(qs):.0f}'
    print(s); out.append(s)
open('scripts/daily/ic1124/daily_spread_1124.txt', 'w').write('■ 直近14日（11/10〜23）の日別の倍率（広告を出した日だけ）\n' + '\n'.join(out) + '\n')
