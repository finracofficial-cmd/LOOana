# -*- coding: utf-8 -*-
"""11/08 06:24: 店全体の0〜5時台（注文は06:24まで EXACT）を過去7日（11/1〜11/7）の同じ時間帯と比べる。0〜5時台が終日に占める割合も出す"""
import os, csv, statistics as st, math
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
X = {l.split(',')[0]: list(map(int, l.strip().split(',')[1:])) for l in open(D + 'cut_0005.txt') if l[0] != '#'}
T = '2026-11-08'; P = sorted(d for d in X if d < T)
def rk(lab, f, fm='{:,.0f}'):
    t = f(T); xs = [f(d) for d in P]
    print(f'  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}・{fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日{sum(x < t for x in xs)}/7')
rk('注文（06:24まで）', lambda d: X[d][7]); rk('注文（0〜5時台）', lambda d: X[d][2])
rk('売上（値引後）', lambda d: X[d][0] + X[d][1]); rk('来訪', lambda d: X[d][3])
rk('来訪→購入%', lambda d: X[d][2] / X[d][3] * 100, '{:.2f}'); rk('カゴ投入率%', lambda d: X[d][4] / X[d][3] * 100, '{:.2f}')
rk('チェックアウト→完了%', lambda d: X[d][6] / X[d][5] * 100, '{:.0f}')
rk('広告費', lambda d: X[d][8]); rk('CPM', lambda d: X[d][8] / X[d][9] * 1000); rk('CTR%', lambda d: X[d][10] / X[d][9] * 100, '{:.2f}')
lam = X[T][3] * sum(X[d][2] for d in P) / sum(X[d][3] for d in P); k = X[T][2]
print(f'  来訪{X[T][3]}×過去7日の購入率 = {lam:.1f}件 → 実際{k}件・この数以下になる確率 {sum(math.exp(-lam)*lam**i/math.factorial(i) for i in range(k+1))*100:.1f}%')
B = {r[0]: int(r[1]) for r in csv.reader(open(R + 'data/daily/daily_order_bands.csv')) if r and r[0].startswith('2026')}
sh = [X[d][2] / B[d] for d in P]; print(f'  0〜5時台の注文が終日に占める割合（過去7日）: {min(sh):.0%}〜{max(sh):.0%}（平均{st.mean(sh):.0%}）')
print(f'  0〜5時台の注文と終日の注文の相関（7日）: r={st.correlation([X[d][2] for d in P], [B[d] for d in P]):.2f}')
