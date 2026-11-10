# -*- coding: utf-8 -*-
"""11/10(火) 16:45: 0〜15時台の広告効率を、過去7日（11/3〜11/9）と祝日でない火曜（10/20・10/27）の同時刻と比べる。
MER=(gross−値引)÷広告費。倍率=(gross−値引−原価)÷広告費。原価は product_tabs.py の COST・数量は gross÷売価。
この時刻の数字が終日をどれだけ当てるかも測る（10/20〜11/9・終日は data/daily/*.csv）。日中の数字なので判定・予算提案には使わない（5d-2）"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('\nMAP', i) if '\nMAP' in src[i:] else src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790   # 8/4から5,980・優先配送は8/23から790
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0, 0, 0, 0]); ST = {}
for d, n, gr, ds in rd('sales_prod_0015.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0015.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0015.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d in ST: assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0], d
DAYS = sorted(ST); T = '2026-11-10'
P7 = [d for d in DAYS if '2026-11-03' <= d <= '2026-11-09']; TUE = ['2026-10-20', '2026-10-27']
MAPC = {'ディスペンサー': '壁掛けディスペンサー'}
def units(n, gr):
    p = PRICE.get(n)
    return gr // p if p and gr % p == 0 else None
def cogs(d):
    c = 0; miss = 0
    for (dd, n), (gr, ds) in S.items():
        if dd != d or not gr: continue
        u = units(n, gr)
        if u is None or n not in COST: miss += gr; continue
        c += u * COST[n]
    return c, miss
acct = lambda d: sum(v[0] for (dd, _), v in A.items() if dd == d)
net = lambda d: ST[d][0] - ST[d][1]
def mer(d): return net(d) / acct(d)
def mult(d): c, _ = cogs(d); return (net(d) - c) / acct(d)
print('■ 店全体（0〜15時台）')
rows = []
for d in TUE + P7 + [T]:
    c, miss = cogs(d)
    rows.append((d, net(d), acct(d), mer(d), mult(d), ST[d][2], ST[d][3], miss))
    print(f"  {d}: 売上{net(d):,} 広告{acct(d):,} MER{mer(d):.2f} 倍率{mult(d):.2f} 注文{ST[d][2]} 来訪{ST[d][3]} 購入率{ST[d][2]/ST[d][3]*100:.2f}% 1来訪あたり広告{acct(d)/ST[d][3]:.0f}円 （原価不明gross {miss:,}）")
def rk(lab, f, fm='{:.2f}', ref=P7):
    t = f(T); xs = [f(d) for d in ref]
    return f"{lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}）今日より低い日{sum(x < t for x in xs)}/7 ／ 火曜 {', '.join(fm.format(f(d)) for d in TUE)}"
for lab, f, fm in [('MER', mer, '{:.2f}'), ('倍率', mult, '{:.2f}'), ('売上', net, '{:,.0f}'), ('広告費', acct, '{:,.0f}'),
                   ('注文', lambda d: ST[d][2], '{:.0f}'), ('来訪', lambda d: ST[d][3], '{:.0f}'), ('購入率%', lambda d: ST[d][2]/ST[d][3]*100, '{:.2f}'),
                   ('カゴ投入率%', lambda d: ST[d][4]/ST[d][3]*100, '{:.2f}'), ('チェックアウト完了%', lambda d: ST[d][6]/ST[d][5]*100, '{:.0f}'),
                   ('客単価', lambda d: net(d)/ST[d][2], '{:,.0f}'), ('CPM', lambda d: acct(d)/sum(v[1] for (dd,_),v in A.items() if dd==d)*1000, '{:,.0f}'),
                   ('CTR%', lambda d: sum(v[2] for (dd,_),v in A.items() if dd==d)/sum(v[1] for (dd,_),v in A.items() if dd==d)*100, '{:.2f}'),
                   ('1LPVあたり広告', lambda d: acct(d)/sum(v[3] for (dd,_),v in A.items() if dd==d), '{:.0f}'),
                   ('LPV→来訪(Shopify)比', lambda d: ST[d][3]/sum(v[3] for (dd,_),v in A.items() if dd==d), '{:.2f}')]:
    print('  ' + rk(lab, f, fm))
# 終日との関係（10/20〜11/9）
FS = collections.defaultdict(lambda: [0, 0]); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[(x['date'], x['name'])][0] += int(x['gross']); FS[(x['date'], x['name'])][1] += int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[(x['date'], x['campaign'])] += float(x['cost'])
def fullstore(d):
    s = sum(v[0] - v[1] for (dd, _), v in FS.items() if dd == d); a = sum(v for (dd, _), v in FA.items() if dd == d)
    c = 0
    for (dd, n), (gr, ds) in FS.items():
        if dd == d and gr:
            u = units(n, gr); c += (u or 0) * COST.get(n, 0)
    return s / a, (s - c) / a, s
HIST = [d for d in DAYS if d < T]
fx = [mer(d) for d in HIST]; fy = [fullstore(d)[0] for d in HIST]
mx = [mult(d) for d in HIST]; my = [fullstore(d)[1] for d in HIST]
print(f'\n■ 0〜15時台と終日の関係（{HIST[0]}〜{HIST[-1]}・{len(HIST)}日）: MER r={st.correlation(fx, fy):.2f}／倍率 r={st.correlation(mx, my):.2f}／売上シェア 中央値{st.median([net(d)/fullstore(d)[2] for d in HIST])*100:.0f}%（{min(net(d)/fullstore(d)[2] for d in HIST)*100:.0f}〜{max(net(d)/fullstore(d)[2] for d in HIST)*100:.0f}%）')
print('  終日の倍率 − 0〜15時台の倍率（同じ日）:', f'中央値{st.median([b - a for a, b in zip(mx, my)]):+.2f}（{min(b - a for a, b in zip(mx, my)):+.2f}〜{max(b - a for a, b in zip(mx, my)):+.2f}）')
print('  火曜の終日倍率:', {d: round(fullstore(d)[1], 2) for d in TUE + ['2026-11-03']})
# 商品別
def pm(d, n):
    c = MAPC.get(n, n); gr, ds = S[(d, n)]; a = A[(d, c)][0]
    if not a: return None, 0, a
    u = units(n, gr) if gr else 0
    return ((gr - ds - (u or 0) * COST.get(n, 0)) / a), (u or 0), a
NM = ['ワイド水切りワイパー', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ナノガラス脱毛パッド',
      '4-in-1マルチクリーナー', '快適マジックインソール', '姿勢サポートチェア', 'マグネットドアクッション']
pr = [(pm(d, n)[0], None) for n in NM for d in HIST]
print('\n■ 商品別（0〜15時台）: 今日 個数・広告費・倍率 ／ 過去7日 同時刻の倍率の中央値（範囲）')
for n in NM:
    m, u, a = pm(T, n); xs = [pm(d, n)[0] for d in P7 if pm(d, n)[2] >= 3000]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'} ／ {f'{st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・{len(xs)}日）' if xs else '—'}")
pp = []
for n in NM:
    for d in HIST:
        m, u, a = pm(d, n); c = MAPC.get(n, n); gr, ds = FS[(d, n)]; fa = FA[(d, c)]
        if m is None or a < 3000 or not fa: continue
        uu = units(n, gr) if gr else 0
        if uu is None: continue
        pp.append((m, (gr - ds - uu * COST[n]) / fa))
print(f'  商品別 0〜15時台の倍率 vs 終日（{len(pp)}件）: r={st.correlation([a for a,_ in pp],[b for _,b in pp]):.2f}。0〜15時台に1.25未満 {sum(a<1.25 for a,_ in pp)}件 → 終日も1.25未満 {sum(a<1.25 and b<1.25 for a,b in pp)}件')
print('\n■ 利益（0〜15時台・(売上−原価)−広告費）')
pf = lambda d: net(d) - cogs(d)[0] - acct(d)
print('  ' + rk('利益', pf, '{:,.0f}'))
w = {'ワイド水切りワイパー': '2026-11-09', 'クリアビューレインガードフィルム': '2026-11-09'}
for n in w:
    c = n
    for d in ['2026-11-08', '2026-11-09', T]:
        a = A[(d, c)]; gr, ds = S[(d, n)]
        print(f"  {n} {d}: 広告{a[0]:,} 表示{a[1]:,} クリック{a[2]} CTR{a[2]/a[1]*100:.2f}% LPV{a[3]} 個数{units(n, gr) if gr else 0} 個数/LPV {((units(n, gr) or 0) if gr else 0)/a[3]*100:.1f}%")
