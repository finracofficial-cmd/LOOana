# -*- coding: utf-8 -*-
"""11/24 21時台「10月末の当たりが3〜6週目に入って落ちてきた → なんで落ちるの？」
ワイパー（11/4〜）・ドア（10/31〜）・洗車ブラシ（10/23〜11/18）と、長く出しているガラス（9/7〜）を、10/27〜11/23 の7日ずつで並べる。
① 週ごと: 広告費・CPM・クリック率・クリック1回・Meta の購入÷クリック・倍率（Shopify の売上と原価）
② 性別×年代（12区分）で、クリック率と CPM の変化を「同じ区分の中で落ちた分」と「表示の行き先が変わった分」に分ける
③ 届いた人の数（10/23 からの累計）: 11/9 まで → 11/23 まで で、新しく届いた人と、1人あたりの表示回数
入力: seg_*_raw.json（Meta・週ごとの性別×年代）・reach_*_raw.json（Meta・累計の到達）・w1123.py（Shopify の売上・原価）"""
import io, contextlib, json, os, collections
os.chdir('/home/user/LOOana'); D0 = 'scripts/daily/ic1124/decay/'
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN = g['A'], g['ALLD'], g['agg'], g['WIN']
W = (('1027_1102', '10/27〜11/02'), ('1103_1109', '11/03〜11/09'), ('1110_1116', '11/10〜11/16'), ('1117_1123', '11/17〜11/23'))
START = {'伸縮ガラスクリーナー': '2026-09-07', '伸縮ワックス洗車ブラシ': '2026-10-23', 'マグネットドアクッション': '2026-10-31', 'ワイド水切りワイパー': '2026-11-04'}
def rows(f):
    out = []
    for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:]:
        if not l.strip(): continue
        c, age, gen, cost, imp, clk, pur = l.strip().split(',')
        z = lambda x: 0 if x in ('null', '') else float(x)
        out.append((c, age, gen, z(cost), z(imp), z(clk), z(pur)))
    return out
SEG = {k: rows(f'seg_{k}_raw.json') for k, _ in W}
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
core = lambda age, gen: gen == 'male' and age in ('45-54', '55-64', '65+')
for c in ('ワイド水切りワイパー', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ', '伸縮ガラスクリーナー'):
    P(f'■ {c}（{START[c][5:]} から）')
    prev = None
    for k, lab in W:
        r = [x for x in SEG[k] if x[0] == c and x[1] != 'Unknown' and x[2] in ('male', 'female')]
        cost = sum(x[3] for x in r); imp = sum(x[4] for x in r); clk = sum(x[5] for x in r); pur = sum(x[6] for x in r)
        if cost < 3000: P(f'  {lab}: 広告費 {cost:,.0f}（ほぼ止まっている）'); continue
        ds = [d for d in ALLD if d >= '2026-' + k[:2] + '-' + k[2:4] and d <= '2026-' + k[5:7] + '-' + k[7:9]]
        WIN['dk' + c + k] = ds; N, DC, Q, K = agg(ds, 'dk' + c + k); a = A(ds, c)
        wk = (int((sum(1 for d in ALLD if START[c] <= d <= ds[-1]) - 1) / 7) + 1)
        cs = {(x[1], x[2]): x for x in r}
        ci = sum(x[4] for x in r if core(x[1], x[2])); cc = sum(x[5] for x in r if core(x[1], x[2]))
        P(f"  {lab}（{wk}週目まで）: 広告費 {cost:,.0f}・CPM {cost/imp*1000:,.0f}・クリック率 {clk/imp:.2%}・クリック1回 {cost/clk:.0f}円・購入÷クリック（Meta）{pur/clk:.2%}・倍率 {(N.get(c,0)-K.get(c,0))/a:.2f}"
          f"｜表示のうち 男性45歳以上 {ci/imp:.0%}（クリック率 {cc/ci:.2%}）・それ以外 {(imp-ci)/imp:.0%}（{(clk-cc)/(imp-ci):.2%}）")
        if prev:
            # クリック率の変化を分ける: Σ w × ctr
            pw = {s: v[4] / prev[1] for s, v in prev[0].items()}; nw = {s: v[4] / imp for s, v in cs.items()}
            pc = {s: v[5] / v[4] for s, v in prev[0].items() if v[4] > 0}; nc = {s: v[5] / v[4] for s, v in cs.items() if v[4] > 0}
            ss = [s for s in pw if s in nw and s in pc and s in nc]
            within = sum(pw[s] * (nc[s] - pc[s]) for s in ss); mix = sum((nw[s] - pw[s]) * nc[s] for s in ss)
            pm = {s: v[3] / v[4] for s, v in prev[0].items() if v[4] > 0}; nm = {s: v[3] / v[4] for s, v in cs.items() if v[4] > 0}
            wi2 = sum(pw[s] * (nm[s] - pm[s]) for s in ss) * 1000; mx2 = sum((nw[s] - pw[s]) * nm[s] for s in ss) * 1000
            P(f"      前の週から: クリック率 {(clk/imp - prev[2]):+.2%}（同じ区分の中 {within:+.2%}・行き先 {mix:+.2%}）｜CPM {cost/imp*1000 - prev[3]:+,.0f}（同じ区分の中 {wi2:+,.0f}・行き先 {mx2:+,.0f}）")
        prev = (cs, imp, clk / imp, cost / imp * 1000)
R1 = {l.split(',')[0].strip(): l.strip().split(',') for l in json.load(open(D0 + 'reach_1023_1109_raw.json'))['data']['data'].split('\n')[1:] if l.strip()}
R2 = {l.split(',')[0].strip(): l.strip().split(',') for l in json.load(open(D0 + 'reach_1023_1123_raw.json'))['data']['data'].split('\n')[1:] if l.strip()}
P('■ ③ 届いた人（10/23 からの累計・Meta の到達）')
for c in ('ワイド水切りワイパー', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ'):
    r1, i1 = int(R1[c][1]), int(R1[c][3]); r2, i2 = int(R2[c][1]), int(R2[c][3])
    P(f"  {c}: 11/9 まで {r1:,}人・{i1:,}回（1人 {i1/r1:.2f}回）→ 11/23 まで {r2:,}人・{i2:,}回（1人 {i2/r2:.2f}回）｜11/10〜23 の表示 {i2-i1:,}回のうち、初めて届いた人 {r2-r1:,}人（表示 {(r2-r1)/(i2-i1):.0%} が新しい人）")
open(D0 + 'decay_1124.txt', 'w').write('\n'.join(out) + '\n')
