# -*- coding: utf-8 -*-
"""11/22 ユーザー「柱は時期・競合の問題で、広告を増やして元に戻るとは限らない。パフォーマンスが落ちたから広告費を抑えた」を数字で確かめる。
①長く売れてきた4本の 7日ごとの 広告費/日・倍率（倍率が先に落ちたのか、広告費が先に減ったのか）
②商品ページに広告から着いた来訪の買う率（週ごと）: 出してからの週数で下がるか ③商品別の決済画面からの完了率（30日）
入力: data/daily/*.csv（w1121.py）・*_weekly_raw.json・landing_social_30d_raw.json"""
import io, contextlib, os, json, collections, math
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1121.py').read(), g)
WIN, agg, A, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']
days = [d for d in ALLD if d >= '2026-08-31']; blocks = [days[-7 * (k + 1):len(days) - 7 * k] for k in range(11, -1, -1)]; blocks = [b for b in blocks if len(b) == 7]
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
P('■ ① 7日ごとの 広告費/日（千円）と倍率: ' + '・'.join(b[0][5:] for b in blocks))
for n in ('ナノガラス脱毛パッド', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '快適マジックインソール'):
    out = []
    for b in blocks:
        WIN['p' + b[0]] = b; N, DC, Q, K = agg(b, 'p' + b[0]); a = A(b, n)
        out.append(f'{a/7/1000:.0f}千 {(N.get(n,0)-K.get(n,0))/a:.2f}' if a else '—')
    P(f'  {n}: ' + '｜'.join(out))
P('')
P('■ ② 広告から商品ページに着いた来訪の買う率（週ごと・来訪→購入）')
for lab, f in (('ガラスクリーナー（9/7〜）', 'glass_weekly_raw.json'), ('洗車ブラシ（10/23〜）', 'brush_weekly_raw.json'), ('ワイパー（11/4〜）', 'wiper_weekly_raw.json')):
    r = json.load(open(os.path.join(D0, f)))['rows']
    P(f'  {lab}: ' + '・'.join(f'{x[0][5:10]} {int(x[4])/int(x[1]):.1%}（{x[4]}/{int(x[1]):,}）' for x in r))
P('')
P('■ ③ 30日（10/23〜11/21）広告から着いた来訪・商品ページ別: 来訪・カート率・決済画面からの完了率（幅 ±1.96σ）・買う率')
NAME = {'nano-fine-fiber': 'ガラスクリーナー', 'vacuum-adsorption': 'W固定', 'washable-reusable': 'ナノ', 'sockliner': 'インソール', 'wax-mop': '洗車ブラシ', 'squeegee': 'ワイパー', 'dust-blower': '4-in-1', 'door-lock-damping': 'ドア', 'sealing-machine': 'シーラー', 'cushion-chair': 'チェア', 'nose-massager': 'ノーズ', 'oscillating-humidifier': 'コードレス加湿器', 'rearview-mirror': 'レインガードフィルム', 'seat-hook': 'フック', 'car-phone-holder-in-car': 'マルチクリップ'}
tot = [0, 0, 0, 0]
for p, s, c, co, d in json.load(open(os.path.join(D0, 'landing_social_30d_raw.json')))['rows']:
    nm = next((v for k, v in NAME.items() if k in p), None)
    if not nm: continue
    s, c, co, d = int(s), int(c), int(co), int(d); r = d / co; se = math.sqrt(r * (1 - r) / co)
    for i, v in enumerate((s, c, co, d)): tot[i] += v
    P(f'  {nm}: 来訪 {s:,}・カート率 {c/s:.1%}・完了率 {r:.0%}（{d}/{co}・±{1.96*se:.0%}）・買う率 {d/s:.2%}')
P(f'  上の合計: 来訪 {tot[0]:,}・カート率 {tot[1]/tot[0]:.1%}・完了率 {tot[3]/tot[2]:.0%}・買う率 {tot[3]/tot[0]:.2%}')
open(os.path.join(D0, 'pillar_1122.txt'), 'w').write('\n'.join(L) + '\n')
