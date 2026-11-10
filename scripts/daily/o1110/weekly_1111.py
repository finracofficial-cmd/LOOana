# -*- coding: utf-8 -*-
"""11/11 判定用: 7日(11/4-10)倍率・週消化率（日ごとの終日予算＝その日の最後のスナップショット）・14日/30日倍率。CSV実測のみ"""
import io, contextlib, csv, collections
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1110.py').read(), g)
WIN, agg, A, ALLD, MAP = g['WIN'], g['agg'], g['A'], g['ALLD'], g['MAP']
def W(days):
    key = 'x' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, K
snap = collections.OrderedDict()
for r in list(csv.reader(open('data/budget-snapshots.csv', encoding='utf-8')))[1:]:
    if r: snap.setdefault(r[0], collections.defaultdict(int))[r[1]] += int(r[3])
def eod(d, camp):   # その日の最後のスナップショットの予算
    ks = [k for k in snap if k[:10] == d]; return snap[ks[-1]].get(camp, 0) if ks else None
D7 = ALLD[-7:]; D14 = ALLD[-14:]; D30 = ALLD[-30:]; D2 = ALLD[-2:]
X = {k: W(v) for k, v in [('7', D7), ('14', D14), ('30', D30), ('2', D2)]}
def mult(k, days, n):
    N, K = X[k]; a = A(days, n); return None if not a else (N.get(n, 0) - K.get(n, 0)) / a
print('7日', D7[0], '-', D7[-1])
for n in ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', '4-in-1マルチクリーナー', '伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'マグネットドアクッション',
          'W固定スマホ車載ホルダー', '姿勢サポートチェア', '快適マジックインソール', 'ポータブルヒートシーラー']:
    c = MAP.get(n, n); bud = [eod(d, c) for d in D7]; sp = [g['AD'][c].get(d, 0) for d in D7]
    on = [(b, s) for b, s in zip(bud, sp) if b]
    rate = sum(s for _, s in on) / sum(b for b, _ in on)
    r2 = sum(sp[-2:]) / sum(bud[-2:])
    f = lambda v: '—' if v is None else f'{v:.2f}'
    print(f"{n}: 7日倍率{f(mult('7', D7, n))} 週消化{rate:.0%}（稼働{len(on)}日） 直近2日消化{r2:.0%} 予算{bud[-1]:,} ／ 2日{f(mult('2', D2, n))} 14日{f(mult('14', D14, n))} 30日{f(mult('30', D30, n))}")
# --- 追加: 現在の予算になってからの消化率（予算が今の値と同じ連続日）とインソール新CR 7日・チェアの連続日 ---
for n in ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション', '快適マジックインソール', '姿勢サポートチェア']:
    c = MAP.get(n, n); cur = eod(ALLD[-1], c); dd = []
    for d in reversed(ALLD):
        if eod(d, c) == cur: dd.append(d)
        else: break
    sp = sum(g['AD'][c].get(d, 0) for d in dd)
    print(f"  {n}: 予算{cur:,}の終日が続いた {len(dd)}日（{dd[-1][5:]}〜）消化{sp/(cur*len(dd)):.0%}")
N, K = W(ALLD[-7:]); n = '快適マジックインソール'; a = A(ALLD[-7:], n)
print(f"インソール新CR 7日（{ALLD[-7]}〜{ALLD[-1]}）: 粗利{N[n]-K[n]:,} 広告{a:,.0f} 倍率{(N[n]-K[n])/a:.2f} 利益{N[n]-K[n]-a:+,.0f}")
for n in ['姿勢サポートチェア', '4-in-1マルチクリーナー', 'クリアビューレインガードフィルム', 'ワイド水切りワイパー']:
    out = []
    for d in ALLD[-5:]:
        NN, KK = W([d]); aa = A([d], n); out.append(f"{d[5:]}:{(NN.get(n,0)-KK.get(n,0))/aa:.2f}" if aa else f"{d[5:]}:—")
    print(' ', n, ' '.join(out))
