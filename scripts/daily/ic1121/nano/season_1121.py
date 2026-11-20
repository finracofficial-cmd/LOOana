# -*- coding: utf-8 -*-
"""11/21 「季節的なことも加味すると、前後で変わってなくない？」
ナノのページの買う率・カート率を 7/6 の週から並べ、表記を変える前（〜10/19 の週）のゆっくりした流れを先へ延ばして、11月の実際と比べる。入力は weekly_raw.txt"""
import math, os, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__)); N = {}; A = {}
for l in open(os.path.join(D0, 'weekly_raw.txt')):
    if l[0] != '#': p = l.strip().split(','); (N if p[0] == 'N' else A)[p[1]] = [int(x) for x in p[2:]]
wk = sorted(N); L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
P('■ 週ごと（月曜始まり）: ナノのページの 来訪・カート率・買う率 ｜ ナノ以外のページの買う率')
for w in wk:
    n = N[w]; o = [a - b for a, b in zip(A[w], n)]
    P(f'  {w[5:]}: {n[0]:,}・{n[1]/n[0]:.2%}・{n[3]/n[0]:.2%}（{n[3]}件） ｜ {o[3]/o[0]:.2%}' + ('  ← 名前を変えた週（10/29〜31）' if w == '2026-10-26' else ''))
pre = [w for w in wk if w <= '2026-10-19']; post = [w for w in wk if w >= '2026-11-02']; assert len(pre) == 16 and len(post) == 3
def fit(idx, cnt, base):
    # 週の番号に対する直線（来訪の数で重みづけ）
    x = [wk.index(w) for w in pre]; y = [cnt(w) / base(w) for w in pre]; wt = [base(w) for w in pre]; sw = sum(wt)
    mx = sum(a * b for a, b in zip(x, wt)) / sw; my = sum(a * b for a, b in zip(y, wt)) / sw
    sl = sum(w_ * (a - mx) * (b - my) for a, b, w_ in zip(x, y, wt)) / sum(w_ * (a - mx) ** 2 for a, w_ in zip(x, wt)); ic = my - sl * mx
    res = [b - (ic + sl * a) for a, b in zip(x, y)]; extra = st.pstdev(res)
    return sl, ic, extra, my
for lab, j in (('買う率', 3), ('カート率', 1)):
    for who, D in (('ナノのページ', N), ('ナノ以外のページ', {w: [a - b for a, b in zip(A[w], N[w])] for w in wk})):
        sl, ic, sd, my = fit(None, lambda w: D[w][j], lambda w: D[w][0])
        obs = sum(D[w][j] for w in post); ses = sum(D[w][0] for w in post); pred = sum((ic + sl * wk.index(w)) * D[w][0] for w in post)
        flat = my * ses
        # 見込みの幅: 週ごとのばらつき（直線からのずれ）と数の少なさを合わせる
        rel = math.sqrt((sd / (pred / ses)) ** 2 / len(post) + 1 / pred)
        P(f'■ {who}の{lab}: 7/6〜10/19 の16週の流れ 1週あたり {sl*100:+.3f}ポイント（平均 {my:.2%}・直線からの週ごとのずれ ±{sd*100:.2f}ポイント）')
        P(f'  11/2〜11/20 の実際 {obs/ses:.2%}（{obs}件/{ses:,}）｜流れを延ばした見込み {pred/ses:.2%}（{pred:.0f}件）→ 実際÷見込み {obs/pred:.2f}（偶然と週ごとのぶれを含めた幅 ±{1.96*rel:.0%}）｜流れを入れず16週の平均と比べると {obs/flat:.2f}')
P('■ 月ごとのナノのページの買う率（週のまとまりで）')
for lab, a, b in (('7月（7/6〜8/2）', '2026-07-06', '2026-07-27'), ('8月（8/3〜8/30）', '2026-08-03', '2026-08-24'), ('9月（8/31〜9/27）', '2026-08-31', '2026-09-21'), ('10月（9/28〜10/25）', '2026-09-28', '2026-10-19'), ('11月（11/2〜11/20）', '2026-11-02', '2026-11-16')):
    ws = [w for w in wk if a <= w <= b]; s = sum(N[w][0] for w in ws); c = sum(N[w][1] for w in ws); d = sum(N[w][3] for w in ws)
    P(f'  {lab}: 来訪 {s:,}・カート率 {c/s:.2%}・買う率 {d/s:.2%}（{d}件）')
open(os.path.join(D0, 'season_1121.txt'), 'w').write('\n'.join(L) + '\n')
