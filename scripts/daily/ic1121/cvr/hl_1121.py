# -*- coding: utf-8 -*-
"""11/21 「cvrが高いタイミングと低い時の違いがよくわからない。安定して儲かるべきだよね」
買う率（購入÷来訪）が高い日と低い日で何が違うかを 10/4〜11/20 の48日で並べる。利益の揺れ方も数える。
入力: ../../o1120/sess_daily_1004_1120.json（来訪）・../../o1120/meta_acct_daily_1004_1120.txt（Meta 終日）・social_daily_raw.txt（social から来た来訪）・data/daily（売上・広告費・注文）・scripts/daily/w1120.py（原価の積み直し）"""
import collections, contextlib, csv, datetime as dt, io, json, math, os, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D0, '..', '..', '..', '..'))
S = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(os.path.join(D0, '..', '..', 'o1120', 'sess_daily_1004_1120.json')))['rows']}
M = {}
for l in open(os.path.join(D0, '..', '..', 'o1120', 'meta_acct_daily_1004_1120.txt')):
    if l[0] != '#': p = l.strip().split(','); M[p[0]] = [int(float(x)) for x in p[1:]]
SO = {}
for l in open(os.path.join(D0, 'social_daily_raw.txt')):
    if l[0] != '#': p = l.strip().split(','); SO[p[0]] = [int(x) for x in p[1:]]
NET = collections.defaultdict(int); AD = collections.defaultdict(float); ORD = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_sales.csv'))): NET[r['date']] += int(float(r['gross'])) - int(float(r['disc']))
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_ad.csv'))): AD[r['date']] += float(r['cost'])
for r in csv.DictReader(open(os.path.join(ROOT, 'data/daily/daily_order_bands.csv'))): ORD[r['date']] = int(r['orders'])
days = sorted(d for d in S if d in M and d in SO); assert len(days) == 48 and days[0] == '2026-10-04' and days[-1] == '2026-11-20'
for d in days: assert abs(M[d][0] - AD[d]) <= max(3, AD[d] * 0.002), (d, M[d][0], AD[d])
WD = '月火水木金土日'; wd = lambda d: WD[dt.date.fromisoformat(d).weekday()]
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
F = collections.OrderedDict()
F['買う率'] = lambda d: S[d][3] / S[d][0]
F['カート率'] = lambda d: S[d][1] / S[d][0]
F['決済画面÷カート'] = lambda d: S[d][2] / S[d][1]
F['完了÷決済画面'] = lambda d: S[d][3] / S[d][2]
F['来訪'] = lambda d: S[d][0]
F['来訪÷広告費1万円'] = lambda d: S[d][0] / AD[d] * 1e4
F['CPM'] = lambda d: AD[d] / M[d][1] * 1000
F['クリック率'] = lambda d: M[d][3] / M[d][1]
F['social の取り分'] = lambda d: SO[d][0] / S[d][0]
F['social の買う率'] = lambda d: SO[d][3] / SO[d][0]
F['social 以外の買う率'] = lambda d: (S[d][3] - SO[d][3]) / (S[d][0] - SO[d][0])
F['1注文の売上'] = lambda d: NET[d] / ORD[d]
F['広告費'] = lambda d: AD[d]
F['売上÷広告費'] = lambda d: NET[d] / AD[d]
cv = {d: F['買う率'](d) for d in days}
# ---- 1. 揺れのうち偶然の分 ----
tot_s = sum(S[d][0] for d in days); p = sum(S[d][3] for d in days) / tot_s
obs = st.pvariance([cv[d] for d in days]); binom = st.mean([p * (1 - p) / S[d][0] for d in days])
P(f'■ ① 買う率（購入÷来訪）の日ごとの揺れ（10/4〜11/20 の48日）: 平均 {p:.2%}・最小 {min(cv.values()):.2%}〜最大 {max(cv.values()):.2%}・日ごとのぶれ ±{math.sqrt(obs)/p:.0%}')
P(f'  数の少なさ（偶然）だけで出るぶれ ±{math.sqrt(binom)/p:.0%} → 揺れのうち偶然で説明がつく分 {min(1, binom/obs):.0%}（残り {max(0, 1-binom/obs):.0%}）')
z = [(cv[d] - p) / math.sqrt(p * (1 - p) / S[d][0]) for d in days]
P(f'  偶然だけなら20日に1日しか出ない高さ・低さの日: 高い {sum(x > 1.645 for x in z)}日・低い {sum(x < -1.645 for x in z)}日（偶然なら各 約{len(days)*0.05:.0f}日）')
# ---- 2. 高い16日と低い16日 ----
rk = sorted(days, key=lambda d: cv[d]); lo, hi = rk[:16], rk[-16:]
P('■ ② 買う率が高い16日 と 低い16日（平均）')
P(f"  高い日: {'・'.join(d[5:] for d in sorted(hi))}"); P(f"  低い日: {'・'.join(d[5:] for d in sorted(lo))}")
fmt = lambda k, v: f'{v:.2%}' if ('率' in k or '÷カート' in k or '完了' in k or '取り分' in k) else f'{v:,.0f}' if v > 50 else f'{v:.2f}'
def corr(xs, ys):
    mx, my = st.mean(xs), st.mean(ys); return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
def local(f):   # その日 ÷ 前後7日（その日を除く）の平均 − 1 ＝ ゆっくりした流れを除いた日ごとの上下
    out = []
    for i, d in enumerate(days):
        nb = [x for x in days[max(0, i - 7):i + 8] if x != d]; out.append(f(d) / st.mean(f(x) for x in nb) - 1)
    return out
lc = local(F['買う率'])
for k, f in F.items():
    a, b = st.mean(f(d) for d in hi), st.mean(f(d) for d in lo)
    r = corr(lc, local(f)) if k != '買う率' else 1
    P(f'  {k}: 高い日 {fmt(k, a)}・低い日 {fmt(k, b)}（差 {a/b-1:+.0%}）' + ('' if k == '買う率' else f'・買う率とのつながり {r:+.2f}'))
P(f'  つながり＝前後7日の平均からの上下どうしの相関。±{2/math.sqrt(len(days)):.2f} の内側は偶然と区別できない')
P('  曜日: 高い日 ' + '・'.join(f'{w}{sum(wd(d)==w for d in hi)}' for w in WD) + '／低い日 ' + '・'.join(f'{w}{sum(wd(d)==w for d in lo)}' for w in WD))
P('  曜日ごとの買う率（48日）: ' + '・'.join(f"{w} {sum(S[d][3] for d in days if wd(d)==w)/sum(S[d][0] for d in days if wd(d)==w):.2%}" for w in WD))
# ---- 3. どの段で違うか ----
P('■ ③ 買う率の上下は、どの段から来ているか（前後7日からの上下で見た取り分）')
steps = ['カート率', '決済画面÷カート', '完了÷決済画面']; lg = lambda v: [math.log(1 + x) for x in v]; y = lg(lc); vy = st.pvariance(y)
for k in steps:
    x = lg(local(F[k])); mx, my = st.mean(x), st.mean(y); cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / len(y)
    P(f'  {k}: {cov/vy:.0%}（日ごとのぶれ ±{st.pstdev(x):.0%}）')
# ---- 4. 売上÷広告費の上下はどこから ----
P('■ ④ 売上÷広告費の上下は、どこから来ているか（同じ見方）')
ym = lg(local(F['売上÷広告費'])); vm = st.pvariance(ym)
G = collections.OrderedDict([('来訪÷広告費（広告の単価とクリック）', F['来訪÷広告費1万円']), ('注文÷来訪（買う率）', lambda d: ORD[d] / S[d][0]), ('1注文の売上', F['1注文の売上'])])
for k, f in G.items():
    x = lg(local(f)); mx, my = st.mean(x), st.mean(ym); cov = sum((a - mx) * (b - my) for a, b in zip(x, ym)) / len(ym)
    P(f'  {k}: {cov/vm:.0%}（日ごとのぶれ ±{st.pstdev(x):.0%}）')
P(f"  来訪÷広告費 と 買う率 のつながり: {corr(local(F['来訪÷広告費1万円']), lc):+.2f}（マイナスなら「人が安く多く来た日は買う率が低い」）")
# ---- 5. 利益の揺れ ----
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    os.chdir(ROOT); exec(open(os.path.join(ROOT, 'scripts/daily/w1120.py')).read(), g)
WIN, agg, ACCT, ALLD = g['WIN'], g['agg'], g['ACCT'], g['ALLD']
def tot(ds):
    key = 'x' + '_'.join(ds); WIN[key] = ds; N, DC, Q, K = agg(ds, key); s = sum(N.values()); k = sum(K.values()); a = ACCT(ds); return s, k, a, s - k - a
d30 = ALLD[-30:]; T = {d: tot([d]) for d in d30}; pr = [T[d][3] for d in d30]; mul = [(T[d][0] - T[d][1]) / T[d][2] for d in d30]
P(f'■ ⑤ 利益の揺れ（直近30日 {d30[0][5:]}〜{d30[-1][5:]}）')
P(f'  1日の利益: 平均 {st.mean(pr):,.0f}・最小 {min(pr):,.0f}（{d30[pr.index(min(pr))][5:]}）〜最大 {max(pr):,.0f}（{d30[pr.index(max(pr))][5:]}）・赤字の日 {sum(x < 0 for x in pr)}日・ぶれ ±{st.pstdev(pr)/st.mean(pr):.0%}')
P(f'  倍率: 平均 {st.mean(mul):.2f}・最小 {min(mul):.2f}〜最大 {max(mul):.2f}・ぶれ ±{st.pstdev(mul)/st.mean(mul):.0%}')
m = st.mean(mul); sg = st.pstdev(mul) / m
P(f'  倍率が ±{sg:.0%} 揺れると、利益は ±{sg*m/(m-1):.0%} 揺れる（利益＝（倍率−1）×広告費。倍率 {m:.2f} のとき {m/(m-1):.1f}倍に広がる）')
for mm in (1.3, 1.5, 1.75, 2.0): P(f'    倍率 {mm:.2f} なら 同じ ±{sg:.0%} で利益は ±{sg*mm/(mm-1):.0%}')
r7 = [st.mean(pr[i - 6:i + 1]) for i in range(6, 30)]; P(f'  7日平均の利益: 最小 {min(r7):,.0f}〜最大 {max(r7):,.0f}・ぶれ ±{st.pstdev(r7)/st.mean(r7):.0%}')
w = collections.OrderedDict()
for d in d30:
    y_ = dt.date.fromisoformat(d); k = (y_ - dt.timedelta(days=y_.weekday())).isoformat(); w.setdefault(k, []).append(d)
P('  週ごと（月〜日）: ' + ' / '.join(f"{k[5:]}の週（{len(v)}日）利益 {sum(T[d][3] for d in v)/len(v):,.0f}/日・倍率 {sum(T[d][0]-T[d][1] for d in v)/sum(T[d][2] for d in v):.2f}・広告費 {sum(T[d][2] for d in v)/len(v):,.0f}/日" for k, v in w.items()))
open(os.path.join(D0, 'hl_1121.txt'), 'w').write('\n'.join(L) + '\n')
# ---- 追記: 「安く多く来た日は買う率が低い」を Meta の数字だけでも確かめる（Shopify の来訪の数え方に左右されない）
ex = ['■ ⑥ 同じことを Meta の数字だけで見る（前後7日からの上下どうしの相関・48日）']
MF = collections.OrderedDict([('クリック÷広告費', lambda d: M[d][3] / AD[d]), ('表示÷広告費（CPM の逆）', lambda d: M[d][1] / AD[d]), ('Meta の購入÷クリック', lambda d: M[d][6] / M[d][3]), ('Meta の購入÷広告費', lambda d: M[d][6] / AD[d])])
a = local(MF['クリック÷広告費']); b = local(MF['Meta の購入÷クリック']); c = local(MF['表示÷広告費（CPM の逆）'])
ex.append(f'  クリック÷広告費 と 購入÷クリック: {corr(a, b):+.2f}／表示÷広告費 と 購入÷クリック: {corr(c, b):+.2f}／Shopify の 来訪÷広告費 と 買う率: {corr(local(F["来訪÷広告費1万円"]), lc):+.2f}')
for k, f in MF.items(): ex.append(f'  {k} の日ごとのぶれ ±{st.pstdev(lg(local(f))):.0%}')
ex.append(f'  ぶれ: 買う率 ±{st.pstdev(lg(lc)):.0%}・来訪÷広告費 ±{st.pstdev(lg(local(F["来訪÷広告費1万円"]))):.0%} → 2つを掛けた 注文÷広告費 ±{st.pstdev(lg(local(lambda d: ORD[d] / AD[d]))):.0%}（打ち消しがなければ ±{math.sqrt(st.pvariance(lg(lc)) + st.pvariance(lg(local(F["来訪÷広告費1万円"])))):.0%}）')
print('\n'.join(ex)); open(os.path.join(D0, 'hl_1121.txt'), 'a').write('\n'.join(ex) + '\n')
