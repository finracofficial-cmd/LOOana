# -*- coding: utf-8 -*-
"""11/11(水) 20:19: 0〜19時台を、過去7日（11/4〜11/10）・祝日でない水曜（10/21・10/28・11/4）・前日の同時刻と比べる。
MER=(gross−値引)÷広告費・倍率=(gross−値引−原価)÷広告費。日中の数字なので判定・予算提案には使わない（5d-2）。
レインガードと洗車ブラシは配信指標（CPM・CTR）と着地ページの来訪を日別に並べる。eval_1001.py（0〜9時台）の2時間後の再確認"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790
# 広告を出していない商品（スキルの原価表 2026-07-25版・売価は当日の売上から）: 過去日の倍率をそろえるためだけに使う
for _n, _p, _c in [('ムダ毛シェーバー', 6980, 2798), ('ネックマッサージャー', 8980, 3034), ('壁掛けディスペンサー', 6980, 2528), ('バランスケアスリッパ', 4980, 1304), ('携帯電動シェーバー', 4980, 1743), ('完全遮光・形状記憶・晴雨兼用・UV日傘', 4980, 1309)]:
    PRICE[_n] = _p; COST[_n] = _c   # product_tabs側の売価が古く割り切れないものがあるので上書きする
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0] * 6); ST = {}; AC = {}
for d, n, gr, ds in rd('sales_prod_0019.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0019.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0019.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d, *v in rd('meta_acct_0019.txt'): AC[d] = [int(x) for x in v]
for d in sorted({k[0] for k in A}): AC[d] = [sum(v[i] for (dd, _), v in A.items() if dd == d) for i in range(4)]
for d in sorted({k[0] for k in S}): assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0], d
T = '2026-11-11'; P7 = [d for d in sorted(ST) if '2026-11-04' <= d <= '2026-11-10']; WED = ['2026-10-21', '2026-10-28', '2026-11-04']; Y = '2026-11-10'
net = lambda d: ST[d][0] - ST[d][1]; ad = lambda d: AC[d][0]
def units(n, gr): p = PRICE.get(n); return gr // p if p and gr % p == 0 else None
def cogs(d): return sum((units(n, gr) or 0) * COST.get(n, 0) for (dd, n), (gr, ds) in S.items() if dd == d and gr)
print('■ 店全体（0〜19時台）')
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
print(f"\n■ 0〜19時台と終日の関係（{H[0]}〜{H[-1]}・{len(H)}日）: 店全体MER r={st.correlation(x, y):.2f}・終日MER−0〜19時台MER 中央値{st.median([b - a for a, b in zip(x, y)]):+.2f}（{min(b - a for a, b in zip(x, y)):+.2f}〜{max(b - a for a, b in zip(x, y)):+.2f}）・この時刻までの売上は終日の{st.median([net(d) / FS[d] for d in H]) * 100:.0f}%（{min(net(d) / FS[d] for d in H) * 100:.0f}〜{max(net(d) / FS[d] for d in H) * 100:.0f}%）")
print('\n■ 商品別（0〜19時台）: 今日 個数・広告費・倍率 ／ 過去7日の同時刻 倍率の中央値（範囲）・個数の中央値')
def pm(d, n):
    gr, ds = S[(d, n)]; a = A[(d, n)][0]; u = (units(n, gr) or 0) if gr else 0
    return (None if not a else (gr - ds - u * COST.get(n, 0)) / a), u, a
for n in ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ナノガラス脱毛パッド', '4-in-1マルチクリーナー',
          'マグネットドアクッション', '快適マジックインソール', '姿勢サポートチェア', '2WAYシートボックス', '高見えレザーヘッドレストフック']:
    m, u, a = pm(T, n); xs = [pm(d, n)[0] for d in P7 if pm(d, n)[2] >= 2000]; us = [pm(d, n)[1] for d in P7 if pm(d, n)[2] >= 2000]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'} ／ {f'{st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・{len(xs)}日）・{st.median(us):g}個' if xs else '—'}")
print('\n■ 原価・売価が当たらなかった売上（0〜19時台）')
for d in P7 + [T]:
    miss = [(n, gr) for (dd, n), (gr, ds) in S.items() if dd == d and gr and (units(n, gr) is None or n not in COST)]
    if miss: print(' ', d[5:], miss)
# ---- 時間帯別（0〜11時台 / 12〜19時台）: Shopifyは差分、Metaは12〜19時台を直接取得 ----
ST11 = {}; A11 = {}; A12 = {}; S11 = collections.defaultdict(lambda: [0, 0])
for d, *v in rd('store_0011.txt'): ST11[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d, n, *v in rd('meta_camp_0011.txt'): A11[(d, n)] = [int(x) for x in v]
for d, n, *v in rd('meta_camp_1219.txt'): A12[(d, n)] = [int(x) for x in v]
for d, n, gr, ds in rd('sales_prod_0011.txt'): S11[(d, n)][0] += int(gr); S11[(d, n)][1] += -int(ds)
bad = [(d, n, A11.get((d, n), [0])[0] + v[0] - A[(d, n)][0]) for (d, n), v in A12.items() if d < T and abs(A11.get((d, n), [0])[0] + v[0] - A[(d, n)][0]) > 2]
print('\n■ 過去日の広告費の突合（12:01取得の0〜11時台 + 12〜19時台 − 0〜19時台）で2円超ずれる行:', bad or 'なし')
ad12 = lambda d: sum(v[0] for (dd, _), v in A12.items() if dd == d); ad11 = lambda d: ad(d) - ad12(d)
net11 = lambda d: ST11[d][0] - ST11[d][1]; net12 = lambda d: net(d) - net11(d)
print('\n■ 時間帯別（日別）: 0〜11時台 売上・注文・広告費・MER ／ 12〜19時台 売上・注文・来訪・広告費・MER')
for d in P7 + [T]:
    print(f"  {d[5:]}: {net11(d):,}・{ST11[d][2]}件・{ad11(d):,}・{net11(d)/ad11(d):.2f} ／ {net12(d):,}・{ST[d][2]-ST11[d][2]}件・{ST[d][3]-ST11[d][3]}・{ad12(d):,}・{net12(d)/ad12(d):.2f}")
for lab, f in [('0〜11時台のMER', lambda d: net11(d) / ad11(d)), ('12〜19時台のMER', lambda d: net12(d) / ad12(d)), ('12〜19時台の注文', lambda d: ST[d][2] - ST11[d][2]), ('12〜19時台の広告費', ad12), ('12〜19時台の来訪', lambda d: ST[d][3] - ST11[d][3]),
               ('12〜19時台の購入率%', lambda d: (ST[d][2] - ST11[d][2]) / (ST[d][3] - ST11[d][3]) * 100), ('12〜19時台の1クリックあたり広告費', lambda d: ad12(d) / sum(v[2] for (dd, _), v in A12.items() if dd == d))]:
    xs = [f(d) for d in P7]; print(f"  {lab}: 今日 {f(T):,.2f} ／ 過去7日 中央値{st.median(xs):,.2f}（{min(xs):,.2f}〜{max(xs):,.2f}）今日より低い日{sum(x < f(T) for x in xs)}/7")
print(f"  今日の0〜11時台の広告費（取り直し）: {ad11(T):,}（12:01取得時 {sum(v[0] for (dd, _), v in A11.items() if dd == T):,}）")
print('\n■ 12〜19時台だけ（商品別・今日）: 個数・広告費 ／ 過去7日の12〜19時台 個数の中央値・広告費の中央値 ／ 直近3日の個数')
for n in ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション', '快適マジックインソール', '4-in-1マルチクリーナー', '姿勢サポートチェア', '防風あったか裏起毛パンツ', 'コードレスダブルミスト加湿器']:
    u12 = lambda d: (units(n, S[(d, n)][0]) or 0) - (units(n, S11[(d, n)][0]) or 0)
    ds_ = [d for d in P7 if A12.get((d, n), [0])[0] > 0]
    print(f"  {n}: {u12(T)}個・{A12.get((T, n), [0])[0]:,}円 ／ " + (f"{st.median([u12(d) for d in ds_]):g}個・{st.median([A12[(d, n)][0] for d in ds_]):,.0f}円（{len(ds_)}日）" if ds_ else '—') + ' ／ ' + '・'.join(str(u12(d)) for d in P7[-3:]))
print('\n■ レインガード（0〜19時台・日別）: 広告費・CPM・CTR・Meta購入 ／ 個数・倍率')
for d in sorted({k[0] for k in A}):
    a = A[(d, 'クリアビューレインガードフィルム')]
    if a[0]: m, u, _ = pm(d, 'クリアビューレインガードフィルム'); print(f"  {d[5:]}: {a[0]:,}・CPM{a[0]/a[1]*1000:,.0f}・CTR{a[2]/a[1]*100:.2f}%・購入{a[5]} ／ {u}個・{m:.2f}")
prof = lambda d: net(d) - cogs(d) - ad(d)
xs = [prof(d) for d in P7]
print(f"\n■ 0〜19時台の 売上−原価−広告費: 今日 {prof(T):,} ／ 過去7日 中央値{st.median(xs):,.0f}（{min(xs):,}〜{max(xs):,}）今日より低い日{sum(x < prof(T) for x in xs)}/7 ／ 日別 " + '・'.join(f"{d[8:]}日 {prof(d):,}" for d in P7))
X = ['2WAYシートボックス', '高見えレザーヘッドレストフック']
gx = sum(S[(T, n)][0] - S[(T, n)][1] - (units(n, S[(T, n)][0]) or 0) * COST.get(n, 0) for n in X); ax = sum(A[(T, n)][0] for n in X)
print(f"  フック・シートボックス（朝に再開して停止）: 広告費{ax:,}・粗利{gx:,} → 除くと倍率 {(net(T) - cogs(T) - gx) / (ad(T) - ax):.2f}")
print('\n■ 商品別の 粗利−広告費（0〜19時台・今日）')
tot = 0
for n in sorted({k[1] for k in A if k[0] == T} | {k[1] for k in S if k[0] == T}, key=lambda n: -(S[(T, n)][0] - S[(T, n)][1] - (units(n, S[(T, n)][0]) or 0) * COST.get(n, 0) - A[(T, n)][0])):
    gp = S[(T, n)][0] - S[(T, n)][1] - (units(n, S[(T, n)][0]) or 0) * COST.get(n, 0); a_ = A[(T, n)][0]; tot += gp - a_
    if gp or a_: print(f"  {n}: {units(n, S[(T, n)][0]) or 0}個・粗利{gp:,}・広告{a_:,}・差 {gp - a_:+,}")
assert tot == prof(T), (tot, prof(T))
