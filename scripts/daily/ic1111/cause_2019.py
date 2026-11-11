# -*- coding: utf-8 -*-
"""11/11(水) 20時台: 今日（0〜19時台）が悪い理由をデータで分解する。あわせて新商品（10/1以降に広告を始めた商品）の実績を data/daily のCSVで数え直す。
原因として書けるのは、ここで数字が出たものだけ。数字で確かめられないものは「未確認」とする"""
import os, csv, collections, statistics as st, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790
for _n, _p, _c in [('ムダ毛シェーバー', 6980, 2798), ('ネックマッサージャー', 8980, 3034), ('壁掛けディスペンサー', 6980, 2528), ('バランスケアスリッパ', 4980, 1304), ('携帯電動シェーバー', 4980, 1743), ('完全遮光・形状記憶・晴雨兼用・UV日傘', 4980, 1309)]:
    PRICE[_n] = _p; COST[_n] = _c
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0] * 6); ST = {}
for d, n, gr, ds in rd('sales_prod_0019.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0019.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0019.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
T = '2026-11-11'; P7 = ['2026-11-0%d' % k for k in range(4, 10)] + ['2026-11-10']; W = '2026-11-04'
units = lambda n, gr: gr // PRICE[n] if n in PRICE and gr % PRICE[n] == 0 else 0
def tot(ds):
    net = sum(ST[d][0] - ST[d][1] for d in ds); od = sum(ST[d][2] for d in ds); ses = sum(ST[d][3] for d in ds)
    ad = sum(v[0] for (dd, _), v in A.items() if dd in ds); imp = sum(v[1] for (dd, _), v in A.items() if dd in ds); ck = sum(v[2] for (dd, _), v in A.items() if dd in ds)
    un = sum(units(n, gr) for (dd, n), (gr, _) in S.items() if dd in ds and n != '優先配送'); gross = sum(ST[d][0] for d in ds); disc = sum(ST[d][1] for d in ds)
    return dict(net=net, od=od, ses=ses, ad=ad, imp=imp, ck=ck, un=un, gross=gross, disc=disc)
t = tot([T])
print('■ MERの分解（0〜19時台）: MER = 広告費1円あたりクリック × クリックあたり注文 × 客単価')
for lab, b in [('過去7日（11/4〜11/10の合計）', tot(P7)), ('先週の水曜（11/4）', tot([W]))]:
    f = lambda x: (x['net'] / x['ad'], x['ck'] / x['ad'], x['od'] / x['ck'], x['net'] / x['od'], x['ad'] / x['imp'] * 1000, x['ck'] / x['imp'] * 100, x['un'] / x['od'], x['gross'] / x['un'], x['disc'] / x['gross'] * 100)
    a, c = f(t), f(b)
    print(f"  対 {lab}: MER {c[0]:.2f}→{a[0]:.2f}（{(a[0]/c[0]-1)*100:+.0f}%）＝ クリック単価 {1/c[1]:.0f}→{1/a[1]:.0f}円（クリック数/円 {(a[1]/c[1]-1)*100:+.0f}%）× クリックあたり注文 {c[2]*100:.2f}→{a[2]*100:.2f}%（{(a[2]/c[2]-1)*100:+.0f}%）× 客単価 {c[3]:,.0f}→{a[3]:,.0f}（{(a[3]/c[3]-1)*100:+.0f}%）")
    print(f"      クリック単価の中身: CPM {c[4]:,.0f}→{a[4]:,.0f}（{(a[4]/c[4]-1)*100:+.0f}%）・CTR {c[5]:.2f}→{a[5]:.2f}%（{(a[5]/c[5]-1)*100:+.0f}%）")
    print(f"      客単価の中身: 1注文あたり個数 {c[6]:.2f}→{a[6]:.2f}・1個あたり売価 {c[7]:,.0f}→{a[7]:,.0f}円・値引率 {c[8]:.1f}→{a[8]:.1f}%")
print('\n■ CPM: 商品ごとの上がり方と、配分の変化（0〜19時台・過去7日合計との比較。今日だけの商品は除く）')
base = {}
for (d, n), v in A.items():
    if d in P7 and v[1]: b = base.setdefault(n, [0, 0]); b[0] += v[0]; b[1] += v[1]
com = [n for (d, n), v in A.items() if d == T and v[1] > 200 and n in base]
act = sum(A[(T, n)][0] for n in com); imp = sum(A[(T, n)][1] for n in com); exp = sum(A[(T, n)][1] * base[n][0] / base[n][1] for n in com)
b_all = sum(base[n][0] for n in com) / sum(base[n][1] for n in com) * 1000
print(f"  共通{len(com)}商品: 過去7日のCPM {b_all:,.0f} → 今日 {act/imp*1000:,.0f}（{(act/imp*1000/b_all-1)*100:+.0f}%）。うち商品ごとのCPM上昇 {(act/exp-1)*100:+.0f}%・配分の変化 {(exp/imp*1000/b_all-1)*100:+.0f}%")
for n in sorted(com, key=lambda n: -A[(T, n)][0]):
    v = A[(T, n)]; bc = base[n][0] / base[n][1] * 1000
    print(f"    {n}: CPM {bc:,.0f}→{v[0]/v[1]*1000:,.0f}（{(v[0]/v[1]*1000/bc-1)*100:+.0f}%）")
print(f"  CPMが過去7日より高い商品: {sum(A[(T, n)][0]/A[(T, n)][1] > base[n][0]/base[n][1] for n in com)}/{len(com)}")
print('\n■ 利益の差はどの商品から来たか（0〜19時台の 粗利−広告費。今日 − 過去7日の1日平均 ／ 今日 − 先週水曜）')
def gpa(d, n): gr, ds = S[(d, n)]; return gr - ds - units(n, gr) * COST.get(n, 0) - A[(d, n)][0]
names = sorted({k[1] for k in list(A) + list(S) if k[0] in P7 + [T]})
rows = [(n, gpa(T, n), sum(gpa(d, n) for d in P7) / 7, gpa(W, n)) for n in names]
print(f"  合計: 今日 {sum(r[1] for r in rows):,} ／ 過去7日平均 {sum(r[2] for r in rows):,.0f}（差 {sum(r[1]-r[2] for r in rows):+,.0f}） ／ 先週水曜 {sum(r[3] for r in rows):,}（差 {sum(r[1]-r[3] for r in rows):+,}）")
for n, a, b, w in sorted(rows, key=lambda r: r[1] - r[2]):
    if abs(a - b) >= 2000 or abs(a - w) >= 4000: print(f"    {n}: 今日 {a:+,} ／ 7日平均 {b:+,.0f}（差 {a-b:+,.0f}） ／ 先週水曜 {w:+,}（差 {a-w:+,}）")
ext = ['クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ワイド水切りワイパー']
print(f"  車の外まわり3商品（レインガード・ブラシ・ワイパー）の差の合計: 対7日平均 {sum(r[1]-r[2] for r in rows if r[0] in ext):+,.0f} ／ それ以外 {sum(r[1]-r[2] for r in rows if r[0] not in ext):+,.0f}")
# ---- 終日（CSV）: 曜日別MER・新商品 ----
FS = collections.defaultdict(lambda: [0, 0]); FA = collections.defaultdict(int)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[(x['date'], x['name'])][0] += int(x['gross']); FS[(x['date'], x['name'])][1] += int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[(x['date'], x['campaign'])] += int(x['cost'])
def dr(a, b):
    d = dt.date.fromisoformat(a)
    while d.isoformat() <= b: yield d.isoformat(); d += dt.timedelta(1)
HOL = {'2026-10-12', '2026-11-03'}
wk = collections.defaultdict(list)
for d in dr('2026-10-12', '2026-11-10'):
    if d in HOL: continue
    n_ = sum(v[0] - v[1] for (dd, _), v in FS.items() if dd == d); a_ = sum(v for (dd, _), v in FA.items() if dd == d)
    wk[dt.date.fromisoformat(d).weekday()].append(n_ / a_)
print('\n■ 曜日別の終日MER（10/12〜11/10・祝日除く・平均）: ' + '・'.join(f"{'月火水木金土日'[k]} {st.mean(wk[k]):.2f}（{len(wk[k])}日）" for k in range(7)))
first = {}
for (d, c), v in sorted(FA.items()):
    if v > 0 and c not in first: first[c] = d
def full(n, a, b):
    G = Dc = Q = AD = 0
    for d in dr(a, b):
        gr, ds = FS[(d, n)]; G += gr; Dc += ds; Q += units(n, gr); AD += FA[(d, n)]
    return Q, AD, G - Dc - Q * COST.get(n, 0)
print('\n■ 10/1以降に広告を始めた商品（開始日〜11/10・終日・CSV）')
new = sorted([c for c, d in first.items() if d >= '2026-10-01' and c in COST], key=lambda c: first[c])
res = [(c, first[c]) + full(c, first[c], '2026-11-10') for c in new]
for c, d0, q, ad, gp in sorted(res, key=lambda r: -(r[4] - r[3])):
    print(f"    {c}（{d0[5:]}〜）: {q}個・広告{ad:,}・粗利−広告 {gp-ad:+,}")
hit = [r for r in res if r[4] - r[3] >= 20000]; miss = [r for r in res if r[4] - r[3] < 0]
print(f"  {len(res)}本: 黒字2万円以上 {len(hit)}本（計{sum(r[4]-r[3] for r in hit):+,}）・赤字 {len(miss)}本（計{sum(r[4]-r[3] for r in miss):+,}・広告費計{sum(r[3] for r in miss):,}）・全体 {sum(r[4]-r[3] for r in res):+,}")
print('\n■ 直近7日（11/4〜11/10・終日）の 粗利−広告費: 10/1以降の商品 と それ以前の商品')
allc = sorted({c for (d, c) in FA if '2026-11-04' <= d <= '2026-11-10'})
n7 = [(c,) + full(c, '2026-11-04', '2026-11-10') for c in allc if c in COST]
for lab, f in [('10/1以降に開始', lambda c: first[c] >= '2026-10-01'), ('それ以前に開始', lambda c: first[c] < '2026-10-01')]:
    xs = [r for r in n7 if f(r[0])]
    print(f"  {lab}: {len(xs)}本・広告{sum(r[2] for r in xs):,}・粗利−広告 {sum(r[3]-r[2] for r in xs):+,}・倍率{sum(r[3] for r in xs)/sum(r[2] for r in xs):.2f} ／ " + '・'.join(f"{r[0][:8]} {r[3]-r[2]:+,}" for r in sorted(xs, key=lambda r: -(r[3]-r[2]))))
print('  ※原価表にないキャンペーン:', [c for c in allc if c not in COST])
print('\n■ 当たり商品の、開始からの週ごとの倍率（終日）')
for c in ['伸縮ワックス洗車ブラシ', 'ポータブルヒートシーラー', 'マグネットドアクッション', 'ワイド水切りワイパー', 'クリアビューレインガードフィルム']:
    d0 = dt.date.fromisoformat(first[c]); out = []
    for k in range(4):
        a = (d0 + dt.timedelta(7 * k)).isoformat(); b = min((d0 + dt.timedelta(7 * k + 6)).isoformat(), '2026-11-10')
        if a > '2026-11-10': break
        q, ad, gp = full(c, a, b)
        if ad: out.append(f"{k+1}週目（{a[5:]}〜{b[5:]}）{gp/ad:.2f}・{gp-ad:+,}")
    print(f"  {c}（{first[c][5:]}〜）: " + ' ／ '.join(out))
print('  レインガードの日別倍率: ' + '・'.join(f"{d[5:]} {full('クリアビューレインガードフィルム', d, d)[2]/max(full('クリアビューレインガードフィルム', d, d)[1],1):.2f}" for d in dr('2026-11-06', '2026-11-10')))
