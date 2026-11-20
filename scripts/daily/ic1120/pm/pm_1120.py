# -*- coding: utf-8 -*-
"""11/20 18時台 「午後がこんなに悪くなることあるんかな」: 過去60日の午後（11〜16時台）と並べる・曜日別・どこで弱かったか。入力は raw.txt だけ"""
import collections, datetime as dt, math, os
D0 = os.path.dirname(os.path.abspath(__file__)); R = collections.defaultdict(list)
for l in open(os.path.join(D0, 'raw.txt')):
    if l[0] != '#': p = l.strip().split(','); R[p[0]].append(p[1:])
D = {r[0]: [int(x) for x in r[1:]] for r in R['D']}; TD = '2026-11-20'; past = [d for d in sorted(D) if d < TD]; assert len(past) == 60
WD = '月火水木金土日'; wd = lambda d: WD[dt.date.fromisoformat(d).weekday()]
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def bin_le(k, n, p): return sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log(1 - p)) for i in range(k + 1))
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
s, c, k, dn = D[TD]; rate = lambda d: D[d][3] / D[d][0]; comp = lambda d: D[d][3] / D[d][2]
P(f'■ ① 今日の午後（11〜16時台）: 来訪 {s}・カート追加 {c}・決済画面 {k}・購入 {dn}・買う率 {dn/s:.2%}・完了÷決済画面 {dn/k:.0%}')
low = sorted(past + [TD], key=rate)
P('  買う率の低い順（61日・9/21〜11/20）: ' + ' / '.join(f'{d[5:]}（{wd(d)}）{rate(d):.2%}' for d in low[:10]))
P(f'  今日より買う率が低い午後: 過去60日のうち {sum(rate(d) < rate(TD) for d in past)} 日。完了÷決済画面が今日（{comp(TD):.0%}）以下: {sum(comp(d) <= comp(TD) for d in past)} 日（' + '・'.join(f'{d[5:]} {comp(d):.0%}' for d in past if comp(d) <= comp(TD)) + '）')
P(f'  来訪が今日（{s}）以下の午後: {sum(D[d][0] <= s for d in past)} 日・購入が {dn} 件以下: {sum(D[d][3] <= dn for d in past)} 日（' + '・'.join(d[5:] for d in past if D[d][3] <= dn) + '）')
for lab, ds in (('過去60日', past), ('直近21日（10/30〜11/19）', past[-21:])):
    r = sum(D[d][3] for d in ds) / sum(D[d][0] for d in ds); P(f'  {lab}の率 {r:.2%} なら見込み {s*r:.1f}件・{dn}件以下になる確率 {ple(dn, s*r):.1%}')
P('■ ② 午後の買う率の流れ（週ごと・月〜日）')
wk = collections.OrderedDict()
for d in past + [TD]:
    y = dt.date.fromisoformat(d); m = (y - dt.timedelta(days=y.weekday())).isoformat(); wk.setdefault(m, [0, 0, 0]); wk[m][0] += D[d][0]; wk[m][1] += D[d][3]; wk[m][2] += D[d][2]
for m, (a, b, kk) in wk.items(): P(f'  {m[5:]}の週: 来訪 {a:,}・購入 {b}・買う率 {b/a:.2%}・完了÷決済画面 {b/kk:.0%}')
P('■ ③ 曜日別の午後（過去60日＋今日）: 日数・来訪・購入・買う率・完了÷決済画面')
W = collections.defaultdict(lambda: [0, 0, 0, 0])
for d in past + [TD]: w = W[wd(d)]; w[0] += 1; w[1] += D[d][0]; w[2] += D[d][3]; w[3] += D[d][2]
ts = sum(w[1] for w in W.values()); tdn = sum(w[2] for w in W.values())
for x in WD:
    n, a, b, kk = W[x]; oth_r = (tdn - b) / (ts - a); p = bin_le(b, tdn, a / ts)
    P(f'  {x}: {n}日・{a:,}・{b}・{b/a:.2%}・{b/kk:.0%}（ほかの曜日 {oth_r:.2%}・同じ率だとして {b}件以下になる確率 {p:.1%}）')
fr = [d for d in past + [TD] if wd(d) == '金']; P('  金曜の午後（日ごと）: ' + ' / '.join(f'{d[5:]} {rate(d):.2%}（{D[d][3]}件）' for d in fr))
P('  注意: 7つの曜日を見てから低いものを拾っているので、1つの曜日が偶然 低く出る確率は上の数字より高い（7倍が目安）')
def cmp(tag, lab):
    P(f'■ {lab}（今日の午後 と ふだんの午後）: 来訪・購入（ふだんの率からの見込み）')
    B = {r[1]: [int(x) for x in r[2:]] for r in R[tag] if r[0] == 'base'}
    for r in R[tag]:
        if r[0] != 'today': continue
        t = [int(x) for x in r[2:]]; b = B.get(r[1])
        if not b or b[0] < 30: P(f'  {r[1]}: {t[0]}・{t[3]}（ふだんの数が少なく比べられない）'); continue
        lam = t[0] * b[3] / b[0]; P(f'  {r[1]}: {t[0]}・{t[3]}（見込み {lam:.1f}・{t[3]}件以下 {ple(t[3], lam):.0%}）｜決済画面 {t[2]}・ふだんの完了÷決済画面 {b[3]/b[2]:.0%}')
cmp('DV', '④ 端末別'); cmp('RF', '⑤ 来た元別'); cmp('LP', '⑥ 最初に開いたページ別（ふだん＝11/13〜18 の午後）')
T = {int(r[0]): [int(x) for x in r[1:]] for r in R['T']}
P(f'■ ⑦ 夕方: 17時台 来訪 {T[17][0]}・カート追加 {T[17][1]}・購入 {T[17][3]}／18時台（18:2x まで）来訪 {T[18][0]}・購入 {T[18][3]}')
open(os.path.join(D0, 'pm_1120.txt'), 'w').write('\n'.join(L) + '\n')
