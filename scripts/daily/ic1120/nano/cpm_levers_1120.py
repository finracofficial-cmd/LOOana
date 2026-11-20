# -*- coding: utf-8 -*-
"""11/20 12時台 「CPM の高騰は抑えられないんだっけ？」: ナノについて、手になりうるものをデータで確かめる。入力は raw.txt だけ"""
import collections, math, os
D0 = os.path.dirname(os.path.abspath(__file__)); R = collections.defaultdict(list)
for l in open(os.path.join(D0, 'raw.txt')):
    if l[0] != '#': p = l.strip().split(','); R[p[0]].append(p[1:])
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
P('■ 広告 A の評価（Meta）')
for r in R['QR']: P(f'  {r[0]}: エンゲージメント {r[1]}・コンバージョン {r[2]}・品質の値 {r[3]}（表示 {int(r[5]):,}）')
P('  → 11/17〜19 も「平均以上」のまま。品質の値も 5 で同じ。11/18〜19 の2日だけだと評価なし（期間が短い）')
P('■ 予算の大きさと CPM（終日）')
ND = {r[0]: [int(x) for x in r[1:]] for r in R['ND']}
for lab, a, b in (('10/15〜10/29', '2026-10-15', '2026-10-29'), ('10/30〜11/9', '2026-10-30', '2026-11-09'), ('11/10〜11/13', '2026-11-10', '2026-11-13'), ('11/14〜11/17', '2026-11-14', '2026-11-17'), ('11/18〜11/19', '2026-11-18', '2026-11-19')):
    ds = [d for d in ND if a <= d <= b]; c = sum(ND[d][0] for d in ds); i = sum(ND[d][1] for d in ds)
    P(f'  {lab}: 広告費/日 {c/len(ds):,.0f}・CPM {c/i*1000:,.0f}')
P('■ 配置別の 購入/広告費1万円（Meta 計上・前 11/10〜16 と 後 11/18〜19）')
T = collections.defaultdict(lambda: [0, 0, 0])
for tag in ('PB', 'PA'):
    for r in R[tag]:
        k = r[0] + ' ' + r[1]; T[k][0] += int(r[2]); T[k][1] += int(r[3]); T[k][2] += int(r[5])
        T[(tag, k)][0] += int(r[2]); T[(tag, k)][1] += int(r[3]); T[(tag, k)][2] += int(r[5])
for k in ('instagram instagram_reels', 'instagram feed', 'instagram instagram_stories', 'threads threads_feed', 'facebook feed'):
    b = T[('PB', k)]; a = T[('PA', k)]; t = T[k]
    P(f'  {k}: 前 {b[2]}件/{b[0]:,}円＝{b[2]/b[0]*1e4:.1f}・後 {a[2]}件/{a[0]:,}円＝{a[2]/a[0]*1e4:.1f}・合計 {t[2]}件＝{t[2]/t[0]*1e4:.2f}・CPM {t[0]/t[1]*1000:,.0f}')
re_, fe = T['instagram instagram_reels'], T['instagram feed']; n = re_[2] + fe[2]; p = fe[0] / (re_[0] + fe[0])
pv = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(fe[2] + 1))
P(f'  リールとフィードの効率が同じなら、フィードの購入は {n}件中 {n*p:.1f}件の見込み。実際 {fe[2]}件・この数以下になる確率 {pv:.1%}')
P('  注意: Meta が「最後に見た配置」に付けた購入。配置を絞ったときに同じ効率で買えるかは別（未検証）')
open(os.path.join(D0, 'cpm_levers_1120.txt'), 'w').write('\n'.join(L) + '\n')
