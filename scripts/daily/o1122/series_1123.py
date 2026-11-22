# -*- coding: utf-8 -*-
"""11/23 定例: 広告を出している商品の日ごとの倍率（11/14〜22）と注文数。予算の判断で「直近の流れ」を見るため。入力は w1122.py（daily_*.csv）と orders_by_product の各日のファイル"""
import io, contextlib, os, glob, collections
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1122.py').read(), g)
WIN, agg, A, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']
days = [d for d in ALLD if d >= '2026-11-14']
L = ['■ 日ごとの倍率（個数）: ' + '・'.join(d[5:] for d in days)]
for n in ('伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'スマートノーズEMS美顔器', '快適マジックインソール', 'マグネットドアクッション', '4-in-1マルチクリーナー', '360°マルチクリップ車載スマホホルダー', '高見えレザーヘッドレストフック', '充電式ダブルミスト卓上加湿器'):
    row = []
    for d in days:
        k = 's' + d; WIN[k] = [d]; N, DC, Q, K = agg([d], k); a = A([d], n)
        row.append('—' if not a else f"{(N.get(n,0)-K.get(n,0))/a:.2f}（{Q.get(n,0)}）")
    L.append(f'  {n}: ' + '・'.join(row))
open(os.path.join(D0, 'series_1123.txt'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
