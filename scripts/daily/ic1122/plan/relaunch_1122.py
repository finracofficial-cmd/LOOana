# -*- coding: utf-8 -*-
"""11/22 ユーザー「過去の広告の復活はどのパターンがささるかな？EMSはCRを替えたのは功を奏したのかな？」
入力: data/relaunch-log.csv（型・1〜2日目・7日）・data/daily/*.csv（w1121.py）・o1121/ad_level_1026_1121.txt（ノーズ v2 の広告別）
ノーズの6月の数字（広告費 25,711・クリック率 0.67%・5個・5,980円）は data/decisions.md 11/14 の記録からの転記（CSV は 6/29 からで6月の配信は入っていない）"""
import io, contextlib, os, csv, collections, math
D0 = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.join(D0, '..', '..', '..', '..'))
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1121.py').read(), g)
WIN, agg, A, ALLD = g['WIN'], g['agg'], g['A'], g['ALLD']
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
def run(n, a, b):
    ds = [d for d in ALLD if a <= d <= b]; WIN['r' + n + a] = ds; N, DC, Q, K = agg(ds, 'r' + n + a); ad = A(ds, n)
    return len(ds), Q.get(n, 0), ad, (N.get(n, 0) - K.get(n, 0)) / ad if ad else 0
P('■ 出し直しの型ごとの結果（data/relaunch-log.csv・倍率は商品の 粗利÷広告費）')
rows = list(csv.DictReader(open('data/relaunch-log.csv')))
A_ = [r for r in rows if r['型'] == 'A']
f = lambda s: float(s.split('（')[0]) if s and s[0].isdigit() else None
a7 = sorted(x for x in (f(r['7日の倍率']) for r in A_) if x is not None); a12 = sorted(x for x in (f(r['1〜2日目の倍率']) for r in A_) if x is not None)
P(f'  A（前のキャンペーンをそのまま再開）: {len(A_)}回・1〜2日目 中央値 {a12[len(a12)//2]:.2f}・7日続いたのは {len(a7)}回（{a7[0]:.2f}〜{a7[-1]:.2f}・中央値 {(a7[len(a7)//2-1]+a7[len(a7)//2])/2:.2f}）・残り {len(A_)-len(a7)}回は数日で停止')
for lab, items in (('C1（新しいキャンペーン×同じ動画）', [('快適マジックインソール', '2026-11-16', '2026-11-21', 'v3'), ('携帯電動シェーバー', '2026-11-14', '2026-11-19', 'v2（広告A が同じ動画・B は新しい動画）'), ('壁掛けディスペンサー', '2026-11-18', '2026-11-19', 'v2')]),
                   ('D（新しいキャンペーン×新しい動画）', [('スマートノーズEMS美顔器', '2026-11-14', '2026-11-21', 'v2'), ('高見えレザーヘッドレストフック', '2026-11-15', '2026-11-21', 'v2〜v5'), ('ポータブルヒートシーラー', '2026-11-18', '2026-11-19', 'v2')])):
    P(f'  {lab}:')
    for n, a, b, v in items:
        k, q, ad, m = run(n, a, b); P(f'    {n} {v}: {a[5:]}〜{b[5:]}（{k}日）・{q}個・広告費 {ad:,.0f}・倍率 {m:.2f}')
P('  出し直す直前の倍率: インソール 11/9〜15 1.54（旧キャンペーン）・シェーバー 9〜10月の再開 7日 1.60・ノーズ 6月 0.69・フック 11/11 の複製 0.43・シーラー 11/1〜7 1.11・ディスペンサー 10/17 の再開 7日 0.98')
P('')
P('■ ノーズ（EMS）: 6月（前の動画・5,980円）→ v2（新しい動画・6,980円・11/14〜21）')
k, q, ad, m = run('スマートノーズEMS美顔器', '2026-11-14', '2026-11-21')
J_AD, J_Q, J_CTR, J_PRICE, COST = 25711, 5, 0.0067, 5980, 2453     # 6月の数字は decisions.md 11/14 からの転記
R = collections.defaultdict(lambda: [0, 0, 0])
for l in open('scripts/daily/o1121/ad_level_1026_1121.txt'):
    if l[0] == '#': continue
    d, c, a, adn, cost, imp, clk = l.strip().split(',')
    if c == 'スマートノーズEMS美顔器v2': x = R[adn]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
imp = sum(x[1] for x in R.values()); clk = sum(x[2] for x in R.values())
P(f'  クリック率: 0.67% → {clk/imp:.2%}（{clk/imp/J_CTR:.1f}倍。広告A {R["A"][2]/R["A"][1]:.2%}・広告B {R["B"][2]/R["B"][1]:.2%}・配信の {R["B"][0]/(R["A"][0]+R["B"][0]):.0%} が B）')
u0, u1 = J_Q / J_AD * 1e4, q / ad * 1e4; se = math.sqrt(1 / J_Q + 1 / q)
P(f'  広告費1万円あたりの個数: {u0:.2f}（{J_Q}個）→ {u1:.2f}（{q}個）＝{u1/u0:.2f}倍（6月が{J_Q}個と少ないので幅は {u1/u0*math.exp(-1.96*se):.1f}〜{u1/u0*math.exp(1.96*se):.1f}倍）')
P(f'  倍率: {J_Q*(J_PRICE-COST)/J_AD:.2f} → {m:.2f}。もし v2 が 5,980円のままで同じ個数だったら {q*(J_PRICE-COST)/ad:.2f}（値上げの分が {m - q*(J_PRICE-COST)/ad:+.2f}）')
open(os.path.join(D0, 'relaunch_1122.txt'), 'w').write('\n'.join(L) + '\n')
