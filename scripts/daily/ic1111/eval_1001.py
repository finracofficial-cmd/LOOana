# -*- coding: utf-8 -*-
"""11/11(水) 10:01: 0〜9時台を、過去7日（11/4〜11/10）・祝日でない水曜（10/21・10/28・11/4）・前日の同時刻と比べる。
MER=(gross−値引)÷広告費・倍率=(gross−値引−原価)÷広告費。日中の数字なので判定・予算提案には使わない（5d-2）。
レインガードと洗車ブラシは配信指標（CPM・CTR）と着地ページの来訪を日別に並べる"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0] * 6); ST = {}; AC = {}
for d, n, gr, ds in rd('sales_prod_0009.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0009.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0009.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d, *v in rd('meta_acct_0009.txt'): AC[d] = [int(x) for x in v]
for d in sorted({k[0] for k in A}): AC[d] = [sum(v[i] for (dd, _), v in A.items() if dd == d) for i in range(4)]
for d in sorted({k[0] for k in S}): assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0], d
T = '2026-11-11'; P7 = [d for d in sorted(ST) if '2026-11-04' <= d <= '2026-11-10']; WED = ['2026-10-21', '2026-10-28', '2026-11-04']; Y = '2026-11-10'
net = lambda d: ST[d][0] - ST[d][1]; ad = lambda d: AC[d][0]
def units(n, gr): p = PRICE.get(n); return gr // p if p and gr % p == 0 else None
def cogs(d): return sum((units(n, gr) or 0) * COST.get(n, 0) for (dd, n), (gr, ds) in S.items() if dd == d and gr)
print('■ 店全体（0〜9時台）')
def rk(lab, f, fm):
    t = f(T); xs = [f(d) for d in P7]
    print(f"  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}）今日より低い日{sum(x < t for x in xs)}/7 ／ 水曜 {'・'.join(fm.format(f(d)) for d in WED)} ／ 前日 {fm.format(f(Y))}")
for lab, f, fm in [('売上', net, '{:,.0f}'), ('注文', lambda d: ST[d][2], '{:.0f}'), ('広告費', ad, '{:,.0f}'), ('MER', lambda d: net(d) / ad(d), '{:.2f}'),
                   ('来訪', lambda d: ST[d][3], '{:.0f}'), ('購入率%', lambda d: ST[d][2] / ST[d][3] * 100, '{:.2f}'), ('カゴ投入率%', lambda d: ST[d][4] / ST[d][3] * 100, '{:.2f}'),
                   ('チェックアウト完了%', lambda d: ST[d][6] / ST[d][5] * 100, '{:.0f}'), ('客単価', lambda d: net(d) / ST[d][2], '{:,.0f}'),
                   ('CPM', lambda d: AC[d][0] / AC[d][1] * 1000, '{:,.0f}'), ('CTR%', lambda d: AC[d][2] / AC[d][1] * 100, '{:.2f}'), ('1クリックあたり広告費', lambda d: AC[d][0] / AC[d][2], '{:.0f}')]:
    rk(lab, f, fm)
mult = lambda d: (net(d) - cogs(d)) / ad(d)
print(f"  倍率（11/4以降のみ原価計算）: 今日 {mult(T):.2f} ／ 過去7日 中央値{st.median([mult(d) for d in P7]):.2f}（{min(mult(d) for d in P7):.2f}〜{max(mult(d) for d in P7):.2f}）今日より低い日{sum(mult(d) < mult(T) for d in P7)}/7 ／ 前日 {mult(Y):.2f}")
# 終日との関係（店全体MER・10/21〜11/10）
FS = collections.defaultdict(int); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
H = [d for d in sorted(ST) if d < T]
x = [net(d) / ad(d) for d in H]; y = [FS[d] / FA[d] for d in H]
print(f"\n■ 0〜9時台と終日の関係（{H[0]}〜{H[-1]}・{len(H)}日）: 店全体MER r={st.correlation(x, y):.2f}・終日MER−0〜9時台MER 中央値{st.median([b - a for a, b in zip(x, y)]):+.2f}（{min(b - a for a, b in zip(x, y)):+.2f}〜{max(b - a for a, b in zip(x, y)):+.2f}）・この時刻までの売上は終日の{st.median([net(d) / FS[d] for d in H]) * 100:.0f}%（{min(net(d) / FS[d] for d in H) * 100:.0f}〜{max(net(d) / FS[d] for d in H) * 100:.0f}%）")
print('\n■ 商品別（0〜9時台）: 今日 個数・広告費・倍率 ／ 過去7日の同時刻 倍率の中央値（範囲）・個数の中央値')
def pm(d, n):
    gr, ds = S[(d, n)]; a = A[(d, n)][0]; u = (units(n, gr) or 0) if gr else 0
    return (None if not a else (gr - ds - u * COST.get(n, 0)) / a), u, a
for n in ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ナノガラス脱毛パッド', '4-in-1マルチクリーナー',
          'マグネットドアクッション', '快適マジックインソール', '姿勢サポートチェア', '2WAYシートボックス', '高見えレザーヘッドレストフック']:
    m, u, a = pm(T, n); xs = [pm(d, n)[0] for d in P7 if pm(d, n)[2] >= 2000]; us = [pm(d, n)[1] for d in P7 if pm(d, n)[2] >= 2000]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'} ／ {f'{st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・{len(xs)}日）・{st.median(us):g}個' if xs else '—'}")
LP = {}; cur = None
for l in open(D + 'landing_0009.txt'):
    l = l.strip()
    if l.startswith('## '): cur = l[3:]; LP[cur] = {}
    elif l and l[0] != '#': p = l.split(','); LP[cur][p[0]] = [int(x) for x in p[1:]]
for lab, n in [('レインガード', 'クリアビューレインガードフィルム'), ('洗車ブラシ', '伸縮ワックス洗車ブラシ')]:
    print(f'\n■ {lab}（0〜9時台・日別）: 広告費・表示・CPM・クリック・CTR・Metaカート・Meta購入 ／ 着地の来訪・カート・完了 ／ Shopify個数・倍率')
    for d in sorted({k[0] for k in A}):
        a = A[(d, n)]
        if not a[0]: continue
        lp = LP[lab].get(d, [0, 0, 0, 0]); m, u, _ = pm(d, n)
        print(f"  {d[5:]}: {a[0]:,}・{a[1]:,}・CPM{a[0]/a[1]*1000:,.0f}・{a[2]}・CTR{a[2]/a[1]*100:.2f}%・カート{a[4]}・購入{a[5]} ／ 来訪{lp[0]}・カート{lp[1]}・完了{lp[3]} ／ {u}個・{m:.2f}")
print('\n■ アカウント全体のCPM・CTR（0〜9時台・日別）と、レインガード・ブラシのCPMの比')
for d in sorted({k[0] for k in A}):
    a = AC[d]; r = A[(d, 'クリアビューレインガードフィルム')]; b = A[(d, '伸縮ワックス洗車ブラシ')]
    cp = a[0] / a[1] * 1000
    print(f"  {d[5:]}: 全体CPM{cp:,.0f}・CTR{a[2]/a[1]*100:.2f}% ／ レインガード {'—' if not r[1] else f'{r[0]/r[1]*1000/cp:.2f}倍'} ／ ブラシ {'—' if not b[1] else f'{b[0]/b[1]*1000/cp:.2f}倍'}")
print('\n■ 終日（日別・rain_brush_freq_place_raw.txt）: CPM・CTR・フリークエンシー')
sec = None; PL = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(D + 'rain_brush_freq_place_raw.txt'):
    l = l.strip()
    if l.startswith('## '): sec = l; continue
    if not l or l[0] in '#[': continue
    p = l.replace('null', '0').split(',')
    if '日別' in sec: print(f"  {p[0][5:]} {p[1][:8]}: 広告{int(p[2]):,}・CPM{int(p[2])/int(p[3])*1000:,.0f}・CTR{int(p[6])/int(p[3])*100:.2f}%・フリークエンシー{float(p[5]):.2f}")
    elif '7日' in sec: print(f"  7日 {p[0][:8]}: リーチ{int(p[3]):,}・フリークエンシー{float(p[4]):.2f}")
    elif '配置別' in sec:
        k = p[1] + '/' + p[2]; v = PL[k][p[0]]; v[0] += int(p[3]); v[1] += int(p[4]); v[2] += int(p[5])
print('  レインガード 配置別CPM（広告費の大きい5配置）: 11/8 → 11/9 → 11/10 → 11/11(途中)')
for k in sorted(PL, key=lambda k: -sum(v[0] for v in PL[k].values()))[:5]:
    print('   ', k, ' → '.join(f"{PL[k][d][0]/PL[k][d][1]*1000:,.0f}" if PL[k][d][1] else '—' for d in ['2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11']))
print('\n■ 0〜9時台の倍率 → 終日の倍率（data/daily のCSV・レインガードとブラシ）')
SL = collections.defaultdict(lambda: [0, 0]); ADD = collections.defaultdict(int)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    SL[(r['date'], r['name'])][0] += int(r['gross']); SL[(r['date'], r['name'])][1] += int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    ADD[(r['date'], r['campaign'])] += int(r['cost'])
for nm in ['クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ']:
    out = []
    for d in sorted({k[0] for k in A}):
        if d == '2026-11-11': continue
        g, dc = SL[(d, nm)]; adv = sum(v for (dd, c), v in ADD.items() if dd == d and nm in c)
        if not adv: continue
        assert g % PRICE[nm] == 0, (nm, d, g)
        q = g // PRICE[nm]; m = (g - dc - q * COST[nm]) / adv
        out.append(f"{d[5:]} 終日{q}個・広告{adv:,}・{m:.2f}")
    print(' ', nm[:8], '／'.join(out))
print('\n■ 補足')
X = ['2WAYシートボックス', '高見えレザーヘッドレストフック']
for d in ['2026-11-08', '2026-11-09', '2026-11-10', '2026-11-11']:
    c = sum(v[0] for (dd, n), v in A.items() if dd == d and not any(x in n for x in X)); im = sum(v[1] for (dd, n), v in A.items() if dd == d and not any(x in n for x in X))
    print(f"  {d[5:]}: フック・シートボックスを除く全体CPM {c/im*1000:,.0f}（広告費{c:,}）")
for nm in ['クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ']:
    print(f"  {nm[:8]}: 売価{PRICE[nm]:,}・原価{COST[nm]:,}・今日0〜9時台の広告費{A[(T, nm)][0]:,} → 1個あたり倍率{(PRICE[nm]-COST[nm])/A[(T, nm)][0]:.2f}（値引なしの場合）・今日の値引{S[(T, nm)][1]:,}")
