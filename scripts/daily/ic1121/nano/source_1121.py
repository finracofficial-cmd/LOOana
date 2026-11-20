# -*- coding: utf-8 -*-
"""11/21 ナノのページの買う率が下がった分を、来訪の入口（参照元）で分ける。
入力: source_raw.txt（Shopify・参照元別／日別）・../../ic1120/nano/raw.txt の ND 行（Meta ナノ 日別: date,cost,imp,reach,link_click,purchase）"""
import os, math
D0 = os.path.dirname(os.path.abspath(__file__)); R = {}
for l in open(os.path.join(D0, 'source_raw.txt')):
    if l[0] == '#' or not l.strip(): continue
    p = l.strip().split(','); R.setdefault(p[0], {})[p[1]] = [int(x) for x in p[2:]]
ND = {}
for l in open(os.path.join(D0, '..', '..', 'ic1120', 'nano', 'raw.txt')):
    if l.startswith('ND,'): p = l.strip().split(','); ND[p[1]] = [int(x) for x in p[2:]]
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
def rng(a, b): return [d for d in sorted(R['DD']) if a <= d <= b]
B, A = rng('2026-10-22', '2026-10-28'), rng('2026-10-31', '2026-11-18'); assert len(B) == 7 and len(A) == 19
clkB, clkA = sum(ND[d][3] for d in B), sum(ND[d][3] for d in A)
SB, SA = R['SB'], R['SA']; totB = sum(v[0] for v in SB.values()); totA = sum(v[0] for v in SA.values()); doneB = sum(v[3] for v in SB.values()); doneA = sum(v[3] for v in SA.values())
# 日別の合計と期間の合計が合うこと（direct・social）
for k, s in (('DD', 'direct'), ('DS', 'social')):
    assert sum(R[k][d][0] for d in B) == SB[s][0] and sum(R[k][d][0] for d in A) == SA[s][0], k
    assert sum(R[k][d][2] for d in B) == SB[s][3] and sum(R[k][d][2] for d in A) == SA[s][3], k
def ci(a, na, b, nb):  # 比（後÷前）と幅（±1.96σ・対数）
    r = (b / nb) / (a / na); se = math.sqrt(1 / a + 1 / b); return r, r * math.exp(-1.96 * se), r * math.exp(1.96 * se)
P('■ ナノのページに着いた来訪: 表記の前（10/22〜28）→ 後（10/31〜11/18）・入口別')
P(f'  合計: 来訪 {totB:,} → {totA:,}・購入 {doneB} → {doneA}・買う率 {doneB/totB*100:.2f}% → {doneA/totA*100:.2f}%')
for s in ('social', 'direct'):
    b, a = SB[s], SA[s]; r, lo, hi = ci(b[3], b[0], a[3], a[0])
    P(f'  {s}: 来訪 {b[0]:,}（{b[0]/totB*100:.0f}%）→ {a[0]:,}（{a[0]/totA*100:.0f}%）・1日 {b[0]/7:.0f} → {a[0]/19:.0f}（{(a[0]/19)/(b[0]/7):.2f}倍）・買う率 {b[3]/b[0]*100:.2f}%（{b[3]}件）→ {a[3]/a[0]*100:.2f}%（{a[3]}件）＝{r:.2f}倍（幅 {lo:.2f}〜{hi:.2f}）')
ob = [sum(SB[s][i] for s in SB if s not in ('social', 'direct')) for i in (0, 3)]; oa = [sum(SA[s][i] for s in SA if s not in ('social', 'direct')) for i in (0, 3)]
P(f'  そのほか（search・unknown・email）: 来訪 {ob[0]} → {oa[0]}・購入 {ob[1]} → {oa[1]}')
P('')
P(f'■ 広告のクリック1回あたり（Meta のリンククリック {clkB:,} → {clkA:,}）')
for s in ('social', 'direct'):
    b, a = SB[s], SA[s]
    P(f'  {s}: 来訪÷クリック {b[0]/clkB:.3f} → {a[0]/clkA:.3f}（{(a[0]/clkA)/(b[0]/clkB):.2f}倍）・購入÷クリック {b[3]/clkB*100:.2f}% → {a[3]/clkA*100:.2f}%（{(a[3]/clkA)/(b[3]/clkB):.2f}倍）')
r = (doneA / clkA) / (doneB / clkB); se = math.sqrt(1 / doneB + 1 / doneA)
P(f'  全部: 来訪÷クリック {totB/clkB:.3f} → {totA/clkA:.3f}（{(totA/clkA)/(totB/clkB):.2f}倍）・購入÷クリック {doneB/clkB*100:.2f}% → {doneA/clkA*100:.2f}%（{r:.2f}倍・幅 {r*math.exp(-1.96*se):.2f}〜{r*math.exp(1.96*se):.2f}）')
P('')
P('■ 買う率の下がり 2.95% → 2.49% を「入口の割合の変化」と「入口ごとの買う率の変化」に分ける')
mix = sum(SA[s][0] / totA * (SB[s][3] / SB[s][0] if SB[s][0] else 0) for s in SA if s in SB)
P(f'  前の買う率のまま、入口の割合だけ後にした場合: {mix*100:.2f}%（{mix/(doneB/totB):.3f}倍）')
P(f'  残り（入口ごとの買う率の変化）: {mix*100:.2f}% → {doneA/totA*100:.2f}%（{(doneA/totA)/mix:.3f}倍）')
P('')
P('■ direct の来訪は広告の量にどれだけ連動しているか（日別・10/15〜11/20・37日）')
ds = sorted(R['DD']); x = [R['DS'][d][0] for d in ds]; y = [R['DD'][d][0] for d in ds]; n = len(ds); assert n == 37
mx, my = sum(x) / n, sum(y) / n; sxx = sum((i - mx) ** 2 for i in x); sxy = sum((i - mx) * (j - my) for i, j in zip(x, y)); b1 = sxy / sxx; b0 = my - b1 * mx
res = [j - (b0 + b1 * i) for i, j in zip(x, y)]; s2 = sum(e * e for e in res) / (n - 2); se0 = math.sqrt(s2 * (1 / n + mx * mx / sxx)); se1 = math.sqrt(s2 / sxx)
r2 = 1 - sum(e * e for e in res) / sum((j - my) ** 2 for j in y)
P(f'  direct ＝ {b0:.0f}（±{1.96*se0:.0f}）＋ {b1:.2f}（±{1.96*se1:.2f}）× social・決定係数 {r2:.2f}')
P(f'  ＝ social が 0 でも1日 {b0:.0f} 件ほど direct が残る計算。前は direct {SB["direct"][0]/7:.0f}/日 のうち {b0/(SB["direct"][0]/7)*100:.0f}%、後は {SA["direct"][0]/19:.0f}/日 のうち {b0/(SA["direct"][0]/19)*100:.0f}%')
for a, b_ in (('2026-10-15', '2026-10-21'), ('2026-10-22', '2026-10-28'), ('2026-10-31', '2026-11-06'), ('2026-11-07', '2026-11-13'), ('2026-11-14', '2026-11-20')):
    dd = rng(a, b_); d_ = sum(R['DD'][d][0] for d in dd); s_ = sum(R['DS'][d][0] for d in dd); dp = sum(R['DD'][d][2] for d in dd); sp = sum(R['DS'][d][2] for d in dd)
    P(f'  {a[5:]}〜{b_[5:]}: direct {d_/len(dd):.0f}/日・social {s_/len(dd):.0f}/日・direct÷social {d_/s_:.2f}・買う率 direct {dp/d_*100:.2f}%（{dp}件）・social {sp/s_*100:.2f}%（{sp}件）')
P('')
P('■ 端末: 前 mobile {:.1f}% → 後 {:.1f}%'.format(R['VB']['mobile'][0] / totB * 100, R['VA']['mobile'][0] / totA * 100))
open(os.path.join(D0, 'source_1121.txt'), 'w').write('\n'.join(L) + '\n')
