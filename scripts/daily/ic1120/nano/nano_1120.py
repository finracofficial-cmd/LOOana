# -*- coding: utf-8 -*-
"""11/20 「ナノガラスはなぜ悪い？」: 今朝（0〜10時台）を過去21日の同じ時刻と比べる／終日の CPM の流れ／配置・年代・ほかの商品との比較。
入力は raw.txt と data/daily の CSV だけ。日中の数字なので予算の提案には使わない"""
import collections, csv, math, os, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D0, '..', '..', '..', '..'))
R = collections.defaultdict(list)
for l in open(os.path.join(D0, 'raw.txt')):
    if l[0] == '#': continue
    p = l.strip().split(','); R[p[0]].append(p[1:])
NS = {r[0]: [int(x) for x in r[1:]] for r in R['NS']}; NP = {r[0]: [int(x) for x in r[1:]] for r in R['NP']}; NM = {r[0]: [int(x) for x in r[1:]] for r in R['NM']}
NH = {int(r[0]): [int(x) for x in r[1:]] for r in R['NH']}; NT = {int(r[0]): [int(x) for x in r[1:]] for r in R['NT']}
ND = {r[0]: [int(x) for x in r[1:]] for r in R['ND']}
TD = '2026-11-20'; CUT = range(0, 11)
NM[TD] = [sum(NH[h][i] for h in CUT) for i in range(6)]
assert sum(NT[h][0] for h in CUT) == NP[TD][0] and sum(NT[h][3] for h in CUT) == NP[TD][3]
past = [d for d in sorted(NS) if d < TD]; assert len(past) == 21
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
o, g, dc, q = NS[TD]; s_, c_, k_, d_ = NP[TD]; ad, imp, clk, lpv, atc, pu = NM[TD]
P('■ ① 今朝（0〜10時台）のナノ: 注文', o, '件・売上（値引後）', f'{g-dc:,}', '・広告費', f'{ad:,}', '・売上÷広告費', f'{(g-dc)/ad:.2f}')
r_page = sum(NP[d][3] for d in past) / sum(NP[d][0] for d in past); r_cart = sum(NP[d][1] for d in past) / sum(NP[d][0] for d in past)
P(f'  ナノのページに着いた来訪 {s_}・カート追加 {c_}（過去21日の率 {r_cart:.2%}＝見込み {s_*r_cart:.1f}）・購入 {d_}（率 {r_page:.2%}＝見込み {s_*r_page:.1f}・{d_}件以下になる確率 {ple(d_, s_*r_page):.0%}）')
for lab, ds in (('過去21日', past), ('直近7日', past[-7:])):
    r = sum(NS[d][0] for d in ds) / sum(NM[d][0] for d in ds); lam = ad * r
    P(f'  注文（広告費から・{lab}の率 1万円あたり {r*1e4:.2f}件）: 見込み {lam:.1f}件・{o}件以下になる確率 {ple(o, lam):.0%}')
xs = [(NS[d][1] - NS[d][2]) / NM[d][0] for d in past]
P(f'  同じ時刻の売上÷広告費: 過去21日 {min(xs):.2f}〜{max(xs):.2f}（中央値 {st.median(xs):.2f}）・今日より低い日 {sum(x < (g-dc)/ad for x in xs)}/21')
P('■ ② 同じ時刻（0〜10時台）の流れ: 注文・広告費・CPM・ページの来訪・来訪÷広告費1万円・ページの買う率')
for d in past[-10:] + [TD]:
    m = NM[d]; n = NP[d]
    P(f'  {d[5:]}: {NS[d][0]}件・{m[0]:,}・CPM {m[0]/m[1]*1000:,.0f}・{n[0]}・{n[0]/m[0]*1e4:.0f}・{n[3]/n[0]:.1%}')
cp = {d: NM[d][0] / NM[d][1] * 1000 for d in past + [TD]}; base = [cp[d] for d in past if d <= '2026-11-16']
P(f'  CPM: 10/30〜11/16 の同じ時刻は {min(base):,.0f}〜{max(base):,.0f}（中央値 {st.median(base):,.0f}）。11/17 {cp["2026-11-17"]:,.0f}・11/18 {cp["2026-11-18"]:,.0f}・11/19 {cp["2026-11-19"]:,.0f}・今日 {cp[TD]:,.0f}')
vis = {d: NP[d][0] / NM[d][0] * 1e4 for d in past + [TD]}; vb = [vis[d] for d in past if d <= '2026-11-16']
P(f'  来訪÷広告費1万円: 10/30〜11/16 は {min(vb):.0f}〜{max(vb):.0f}（中央値 {st.median(vb):.0f}）。11/17 {vis["2026-11-17"]:.0f}・11/18 {vis["2026-11-18"]:.0f}・11/19 {vis["2026-11-19"]:.0f}・今日 {vis[TD]:.0f}')
P('■ ③ 終日の CPM（ナノのキャンペーン）: 日付・広告費・CPM・1人あたりの表示回数')
for d in sorted(ND):
    if d >= '2026-11-08': c, i, re_, cl, pu_ = ND[d]; P(f'  {d[5:]}: {c:,}・{c/i*1000:,.0f}・{i/re_:.2f}')
def per(a, b): ds = [d for d in ND if a <= d <= b]; return [sum(ND[d][j] for d in ds) for j in range(5)], len(ds)
for lab, a, b in (('10/15〜10/29（1日 約7.9万円のころ）', '2026-10-15', '2026-10-29'), ('10/30〜11/9', '2026-10-30', '2026-11-09'), ('11/10〜11/16（前）', '2026-11-10', '2026-11-16'), ('11/18〜11/19（後）', '2026-11-18', '2026-11-19')):
    (c, i, re_, cl, pu_), n = per(a, b); cs = [ND[d][0] / ND[d][1] * 1000 for d in ND if a <= d <= b]
    P(f'  {lab}: 広告費/日 {c/n:,.0f}・CPM {c/i*1000:,.0f}（日ごと {min(cs):,.0f}〜{max(cs):,.0f}）・クリック率 {cl/i:.2%}・購入÷クリック {pu_/cl:.2%}・購入/1万円 {pu_/c*1e4:.2f}（購入 {pu_}）')
(cb, ib, _, clb, pb), nb = per('2026-11-10', '2026-11-16'); (ca, ia, _, cla, pa), na = per('2026-11-18', '2026-11-19')
P(f'  前→後: CPM {ca/ia/(cb/ib)-1:+.0%}・クリック率 {(cla/ia)/(clb/ib)-1:+.0%}・購入÷クリック {(pa/cla)/(pb/clb)-1:+.0%}・購入/1万円 {(pa/ca)/(pb/cb)-1:+.0%}')
lam = ca * pb / cb; P(f'  後の2日の購入 {pa}件: 前の率なら見込み {lam:.1f}件・{pa}件以下になる確率 {ple(pa, lam):.0%}（Meta 計上）')
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(int)
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_sales.csv'))):
    if r['name'] == 'ナノガラス脱毛パッド': S[r['date']][0] += int(float(r['gross'])); S[r['date']][1] += int(float(r['disc']))
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_ad.csv'))):
    if r['campaign'] == 'ナノガラス脱毛パッド': A[r['date']] += int(float(r['cost']))
def mer(a, b): ds = [d for d in S if a <= d <= b]; return sum(S[d][0] - S[d][1] for d in ds) / sum(A[d] for d in ds)
P(f"  Shopify の売上÷広告費（終日・data/daily）: 11/10〜16 {mer('2026-11-10','2026-11-16'):.2f} → 11/18〜19 {mer('2026-11-18','2026-11-19'):.2f}（日ごと: " + '・'.join(f"{d[5:]} {(S[d][0]-S[d][1])/A[d]:.2f}" for d in sorted(S) if d >= '2026-11-10') + '）')
def mix(tagb, taga, keyf, lab, minimp=100):
    B = collections.defaultdict(lambda: [0, 0]); Aa = collections.defaultdict(lambda: [0, 0])
    for r in R[tagb]: k = keyf(r); B[k][0] += int(r[2]); B[k][1] += int(r[3])
    for r in R[taga]: k = keyf(r); Aa[k][0] += int(r[2]); Aa[k][1] += int(r[3])
    keys = [k for k in B if B[k][1] >= minimp and Aa[k][1] >= minimp]
    tb = sum(B[k][1] for k in keys); ta = sum(Aa[k][1] for k in keys)
    cpb = sum(B[k][0] for k in keys) / tb * 1000; cpa = sum(Aa[k][0] for k in keys) / ta * 1000
    fixed = sum(B[k][1] / tb * (Aa[k][0] / Aa[k][1] * 1000) for k in keys)
    P(f'■ {lab}（前 11/10〜16 → 後 11/18〜19。表示100回以上の区分だけ）: CPM {cpb:,.0f} → {cpa:,.0f}（{cpa/cpb-1:+.0%}）＝ 同じ区分の中の値上がり {fixed/cpb-1:+.0%} × 高い区分に寄った分 {cpa/fixed-1:+.0%}')
    for k in sorted(keys, key=lambda k: -B[k][1]):
        P(f'  {k}: CPM {B[k][0]/B[k][1]*1000:,.0f} → {Aa[k][0]/Aa[k][1]*1000:,.0f}（{(Aa[k][0]/Aa[k][1])/(B[k][0]/B[k][1])-1:+.0%}）・表示の取り分 {B[k][1]/tb:.0%} → {Aa[k][1]/ta:.0%}')
mix('PB', 'PA', lambda r: r[0] + ' ' + r[1], '④ 配置別')
mix('AB', 'AA', lambda r: r[0], '⑤ 年代別')
P('■ ⑥ ほかの商品の CPM（終日・前 11/10〜16 → 後 11/18〜19）')
CBd = {r[0]: (int(r[1]), int(r[2])) for r in R['CB']}; CAd = {r[0]: (int(r[1]), int(r[2])) for r in R['CA']}
for k in sorted(CBd, key=lambda k: -(CAd[k][0] / CAd[k][1]) / (CBd[k][0] / CBd[k][1])):
    b = CBd[k][0] / CBd[k][1] * 1000; a = CAd[k][0] / CAd[k][1] * 1000; P(f'  {k}: {b:,.0f} → {a:,.0f}（{a/b-1:+.0%}）')
open(os.path.join(D0, 'nano_1120.txt'), 'w').write('\n'.join(L) + '\n')
