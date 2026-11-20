# -*- coding: utf-8 -*-
"""11/21 「時間でパフォーマンスが下がる理由を深掘り」。入力: raw.txt（この場所）・../../ic1120/pm/raw.txt（午後の日別）・../../ic1120/h11/raw.txt と ../../ic1120/h17/raw.txt（0〜10時台・0〜16時台の日別の売上と広告費）・
../../o1120/hourly_1120_raw.txt（11/20 の時間別）・data/daily（終日の売上と広告費）"""
import collections, csv, datetime as dt, math, os, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D0, '..', '..', '..', '..'))
def load(p):
    R = collections.defaultdict(list)
    for l in open(p):
        if l[0] != '#': x = l.strip().split(','); R[x[0]].append(x[1:])
    return R
R = load(os.path.join(D0, 'raw.txt')); RP = load(os.path.join(D0, '..', '..', 'ic1120', 'pm', 'raw.txt'))
R10 = load(os.path.join(D0, '..', '..', 'ic1120', 'h11', 'raw.txt')); R16 = load(os.path.join(D0, '..', '..', 'ic1120', 'h17', 'raw.txt'))
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1)) if l > 0 else 1.0
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
def bin_le(k, n, p): return sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log(1 - p)) for i in range(k + 1))
WD = '月火水木金土日'; wd = lambda d: WD[dt.date.fromisoformat(d).weekday()]
BL = collections.OrderedDict([('朝 0〜10時台', range(0, 11)), ('午後 11〜16時台', range(11, 17)), ('夜 17〜23時台', range(17, 24))])
# ---------- A. 時刻別のふだんの形（10/18〜11/14 の28日をまとめたもの）----------
HM = {int(r[0]): [int(x) for x in r[1:]] for r in R['HM']}; HS = {int(r[0]): [int(x) for x in r[1:]] for r in R['HS']}; HV = {int(r[0]): [int(x) for x in r[1:]] for r in R['HV']}
tc = sum(v[0] for v in HM.values())
P('■ A. 時刻ごとのふだんの形（10/18〜11/14 の28日の合計）: 広告費の取り分・CPM・クリック率・来訪÷広告費1万円・カート率・完了÷決済画面・買う率・1注文の売上・売上÷広告費')
def prof(hs):
    c = sum(HM[h][0] for h in hs); i = sum(HM[h][1] for h in hs); k = sum(HM[h][2] for h in hs); s = sum(HS[h][0] for h in hs); ca = sum(HS[h][1] for h in hs); ck = sum(HS[h][2] for h in hs); dn = sum(HS[h][3] for h in hs)
    o = sum(HV[h][0] for h in hs); net = sum(HV[h][1] - HV[h][2] for h in hs)
    return dict(share=c / tc, cpm=c / i * 1000, ctr=k / i, vis=s / c * 1e4, cart=ca / s, comp=dn / ck, cvr=dn / s, aov=net / o, mer=net / c, dn=dn, s=s, o=o)
f = lambda x: f"{x['share']:.0%}・{x['cpm']:,.0f}・{x['ctr']:.2%}・{x['vis']:.0f}・{x['cart']:.1%}・{x['comp']:.0%}・{x['cvr']:.2%}・{x['aov']:,.0f}・{x['mer']:.2f}"
for h in range(24): P(f'  {h}時台: ' + f(prof([h])))
allp = prof(range(24))
for lab, hs in BL.items():
    x = prof(hs); se = math.sqrt(x['cvr'] * (1 - x['cvr']) / x['s'])
    P(f'  {lab}: ' + f(x) + f"（買う率の偶然の幅 ±{2*se/x['cvr']:.0%}・全体 {allp['cvr']:.2%} との差 {x['cvr']/allp['cvr']-1:+.0%}・売上÷広告費は全体 {allp['mer']:.2f} との差 {x['mer']/allp['mer']-1:+.0%}）")
ms = [prof([h])['mer'] for h in range(6, 24)]; P(f'  6〜23時台の売上÷広告費: 最小 {min(ms):.2f}〜最大 {max(ms):.2f}（全体 {allp["mer"]:.2f}）')
# ---------- B. 時間帯×日（61日）----------
DAY = {'朝 0〜10時台': {r[0]: [int(x) for x in r[1:]] for r in R['DM']}, '午後 11〜16時台': {r[0]: [int(x) for x in r[1:]] for r in RP['D']}, '夜 17〜23時台': {r[0]: [int(x) for x in r[1:]] for r in R['DE']}}
days = sorted(DAY['朝 0〜10時台']); assert len(days) == 61 and all(sorted(v) == days for v in DAY.values())
P('■ B. 時間帯ごとの買う率は、偶然の分だけ揺れているのか（9/21〜11/20 の61日×3つの時間帯＝183コマ）')
P('  見込み＝そのコマの来訪 × 同じ時間帯の前後10日（その日を除く）の買う率')
res = {}; chi = 0; n = 0; lo5 = hi5 = 0
for b, dd in DAY.items():
    cb = 0
    for i, d in enumerate(days):
        nb = [x for x in days[max(0, i - 10):i + 11] if x != d]; r = sum(dd[x][3] for x in nb) / sum(dd[x][0] for x in nb); e = dd[d][0] * r; o = dd[d][3]
        z = (o - e) / math.sqrt(e); res[(b, d)] = (o, e, z); chi += z * z; cb += z * z; n += 1
        lo5 += ple(o, e) < 0.05; hi5 += pge(o, e) < 0.05
    P(f'  {b}: ばらつき（実際÷偶然だけの場合）{cb/len(days):.2f}')
P(f'  全体: ばらつき {chi/n:.2f}（1.00 なら偶然の分だけ・1 より大きいほど偶然以外の揺れがある）。偶然なら20回に1回しか出ない低さ: {lo5}コマ（偶然なら約 {n*0.05:.0f}）・同じく高さ: {hi5}コマ')
worst = sorted(res.items(), key=lambda kv: kv[1][2])[:8]
P('  低かった順: ' + ' / '.join(f'{d[5:]}（{wd(d)}）{b[:2].strip()} {o}件（見込み {e:.1f}）' for (b, d), (o, e, z) in worst))
best = sorted(res.items(), key=lambda kv: -kv[1][2])[:5]
P('  高かった順: ' + ' / '.join(f'{d[5:]}（{wd(d)}）{b[:2].strip()} {o}件（見込み {e:.1f}）' for (b, d), (o, e, z) in best))
def corr(xs, ys):
    mx, my = st.mean(xs), st.mean(ys); return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
zb = {b: [res[(b, d)][2] for d in days] for b in DAY}; bs = list(DAY)
P(f'  つながり（相関・61日。±0.25 の内側は偶然と区別できない）: 朝→同じ日の午後 {corr(zb[bs[0]], zb[bs[1]]):+.2f}・午後→同じ日の夜 {corr(zb[bs[1]], zb[bs[2]]):+.2f}・午後→次の日の午後 {corr(zb[bs[1]][:-1], zb[bs[1]][1:]):+.2f}・夜→次の日の朝 {corr(zb[bs[2]][:-1], zb[bs[0]][1:]):+.2f}')
# ---------- C. 曜日×時間帯 ----------
P('■ C. 曜日×時間帯の買う率（61日）。かっこは、その時間帯のほかの曜日と同じ率だとして、その件数以下（低い側）になる確率')
for b, dd in DAY.items():
    ts = sum(v[0] for v in dd.values()); tdn = sum(v[3] for v in dd.values()); row = []
    for w in WD:
        ds = [d for d in days if wd(d) == w]; a = sum(dd[d][0] for d in ds); k = sum(dd[d][3] for d in ds); p = bin_le(k, tdn, a / ts)
        row.append(f'{w} {k/a:.2%}（{p:.0%}）')
    P(f'  {b}（全体 {tdn/ts:.2%}）: ' + '・'.join(row))
P('  注意: 21個のます目を見ているので、偶然だけでも1つは「5%以下」が出る')
# ---------- D. 週ごとの流れ ----------
P('■ D. 週ごと（月〜日）の買う率: 朝・午後・夜')
wk = collections.OrderedDict()
for d in days:
    y = dt.date.fromisoformat(d); m = (y - dt.timedelta(days=y.weekday())).isoformat(); wk.setdefault(m, {b: [0, 0] for b in DAY})
    for b in DAY: wk[m][b][0] += DAY[b][d][0]; wk[m][b][1] += DAY[b][d][3]
for m, v in wk.items(): P(f'  {m[5:]}の週: ' + '・'.join(f'{v[b][1]/v[b][0]:.2%}' for b in DAY))
# ---------- E. 売上÷広告費を時間帯別に（10/30〜11/20）----------
P('■ E. 時間帯別の売上÷広告費（10/30〜11/19 の21日と 11/20）')
dayf = lambda rows: {r[0]: [int(x) for x in r[1:]] for r in rows}
V10, M10, V16, M16 = dayf(R10['V']), dayf(R10['M']), dayf(R16['V']), dayf(R16['M'])
NET = collections.defaultdict(int); ADF = collections.defaultdict(float)
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_sales.csv'))): NET[r['date']] += int(float(r['gross'])) - int(float(r['disc']))
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_ad.csv'))): ADF[r['date']] += float(r['cost'])
past = [d for d in sorted(M16) if d <= '2026-11-19']; assert len(past) == 21
def blk(d):
    a = (V10[d][1] - V10[d][2], M10[d][0]); b_ = (V16[d][1] - V16[d][2] - a[0], M16[d][0] - a[1]); c = (NET[d] - (V16[d][1] - V16[d][2]), ADF[d] - M16[d][0]); return [a, b_, c]
T = load(os.path.join(D0, '..', '..', 'o1120', 'hourly_1120_raw.txt')); TV = {int(r[0]): [int(x) for x in r[1:]] for r in T['V']}; TM = {int(r[0]): [int(x) for x in r[1:]] for r in T['MH']}
today = [(sum(TV.get(h, [0, 0, 0])[1] - TV.get(h, [0, 0, 0])[2] for h in hs), sum(TM[h][0] for h in hs)) for hs in BL.values()]
for i, b in enumerate(BL):
    xs = [blk(d)[i][0] / blk(d)[i][1] for d in past]; t = today[i][0] / today[i][1]
    P(f'  {b}: 21日の中央値 {st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・日ごとのぶれ ±{st.pstdev([math.log(x) for x in xs]):.0%}）｜11/19 {xs[-1]:.2f}・11/20 {t:.2f}（21日のうち 11/20 より低い日 {sum(x < t for x in xs)}）')
sh = [[blk(d)[i][1] / sum(x[1] for x in blk(d)) for d in past] for i in range(3)]
P('  広告費の取り分（21日の中央値）: ' + '・'.join(f'{b[:2].strip()} {st.median(sh[i]):.0%}' for i, b in enumerate(BL)) + '／11/20: ' + '・'.join(f'{today[i][1]/sum(x[1] for x in today):.0%}' for i in range(3)))
# ---------- F. 来た元 ----------
P('■ F. 来た元別の買う率（10/18〜11/14）: 時間帯ごと')
for r in R['RF']:
    v = [int(x) for x in r[2:]]; P(f'  {r[0]} {r[1]}: 来訪 {v[0]:,}・買う率 {v[3]/v[0]:.2%}・完了÷決済画面 {v[3]/v[2]:.0%}')
open(os.path.join(D0, 'tod_1121.txt'), 'w').write('\n'.join(L) + '\n')
