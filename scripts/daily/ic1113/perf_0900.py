# -*- coding: utf-8 -*-
"""11/13(金) 09:0x 「パフォーマンスを分析して。広告効率とか」
0〜8時台を、過去7日（11/6〜11/12）・前週金（11/6）・前日（11/12）の同じ時刻と比べる。店全体・広告の効率（CPM・クリック率・1クリック・着地・カート・購入）・商品別。
日中の数字なので判定・予算の提案には使わない（SKILL 5d-2）。今日の8時台は広告費・着地がまだ増える。倍率は代表原価の近似（product_tabs.py の COST/PRICE）"""
import os, sys, csv, json, re, collections, statistics as st, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'; iv = lambda x: 0 if x in ('null', '') else int(x)
src = open(R + 'scripts/product_tabs.py').read(); g = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE.update({'ネックマッサージャー': 8980, '姿勢サポートチェア': 5980, '優先配送': 790})   # 値段が日付で変わった商品は今の値段
nm = lambda t: re.sub(r'^(LOOTY|LOTTY)\s*', '', re.sub(r'【[^】]*】', '', t).strip()).strip()
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3])) for r in json.load(open(D + 'store_sales_0008.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0008.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0008.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
MC = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'meta_camp_0008.txt'):
    if l[0] != '#': p = l.strip().split(','); MC[(p[0], p[1])] = [int(x) for x in p[2:]]
PS = collections.defaultdict(lambda: [0, 0])
for d, t, gr, dc in json.load(open(D + 'sales_prod_0008.json'))['rows']:
    n = nm(t)
    if int(gr): PS[(d, n)][0] += int(gr); PS[(d, n)][1] += -int(dc)
for d in {k[0] for k in PS}: assert sum(v[0] - v[1] for k, v in PS.items() if k[0] == d) == SS[d][0], d   # 商品の合計 = 店全体
for d in {k[0] for k in MC}: assert abs(sum(v[0] for k, v in MC.items() if k[0] == d) - MA[d][0]) <= 10, d   # キャンペーンの合計 = アカウント
T, F, Y = '2026-11-13', '2026-11-06', '2026-11-12'; P7 = [f'2026-11-{d:02d}' for d in range(6, 13)]
def cogs(d):
    c = 0
    for (dd, n), (gr, dc) in PS.items():
        if dd == d and gr and PRICE.get(n) and n != '優先配送': assert gr % PRICE[n] == 0, (d, n, gr); c += gr // PRICE[n] * COST.get(n, 0)
    return c
def rk(lab, f, fm):
    t = f(T); xs = [f(d) for d in P7]
    print(f"  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値 {fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}・今日より低い日 {sum(x < t for x in xs)}/7）／ 前週金 {fm.format(f(F))} ／ 前日 {fm.format(f(Y))}")
print('■ 店全体（0〜8時台）')
rk('売上', lambda d: SS[d][0], '{:,}'); rk('注文', lambda d: SS[d][1], '{}'); rk('広告費（今日の8時台は着地途中）', lambda d: MA[d][0], '{:,}')
rk('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}'); rk('倍率（近似）', lambda d: (SS[d][0] - cogs(d)) / MA[d][0], '{:.2f}')
rk('粗利−広告費', lambda d: SS[d][0] - cogs(d) - MA[d][0], '{:+,}')
rk('来訪', lambda d: SE[d][0], '{}'); rk('購入完了÷来訪%', lambda d: SE[d][3] / SE[d][0] * 100, '{:.2f}'); rk('カゴ投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
rk('決済画面→完了%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}'); rk('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
print('■ 広告の効率（0〜8時台・Meta）')
rk('CPM', lambda d: MA[d][0] / MA[d][1] * 1000, '{:,.0f}'); rk('クリック率%', lambda d: MA[d][2] / MA[d][1] * 100, '{:.2f}'); rk('1クリック円', lambda d: MA[d][0] / MA[d][2], '{:.0f}')
rk('着地÷クリック', lambda d: MA[d][3] / MA[d][2], '{:.2f}'); rk('来訪÷クリック', lambda d: SE[d][0] / MA[d][2], '{:.2f}'); rk('Metaカート÷着地%', lambda d: MA[d][4] / MA[d][3] * 100, '{:.1f}')
rk('Meta購入÷クリック%', lambda d: MA[d][5] / MA[d][2] * 100, '{:.2f}'); rk('注文1件の広告費', lambda d: MA[d][0] / SS[d][1], '{:,.0f}')
# 来訪の差を 広告費 × 1円あたりのクリック × クリックあたりの来訪 に分ける（過去7日の平均との比・対数で按分）
import math
a = {k: st.mean(v(d) for d in P7) for k, v in {'ad': lambda d: MA[d][0], 'cpy': lambda d: MA[d][2] / MA[d][0], 'spc': lambda d: SE[d][0] / MA[d][2]}.items()}
t = {'ad': MA[T][0], 'cpy': MA[T][2] / MA[T][0], 'spc': SE[T][0] / MA[T][2]}
tot = math.log(SE[T][0] / st.mean(SE[d][0] for d in P7)); parts = {k: math.log(t[k] / a[k]) for k in t}
print(f"  来訪の差（過去7日平均比 {SE[T][0]/st.mean(SE[d][0] for d in P7)-1:+.0%}）の内訳（対数で按分）: 広告費 {parts['ad']/tot*100 if tot else 0:.0f}%・1円あたりのクリック {parts['cpy']/tot*100 if tot else 0:.0f}%・クリックあたりの来訪 {parts['spc']/tot*100 if tot else 0:.0f}%（残り {(tot-sum(parts.values()))/tot*100 if tot else 0:.0f}%）")
# 終日との関係
FS = collections.defaultdict(int); FA = collections.defaultdict(float); FO = {}
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
for x in csv.DictReader(open(R + 'data/daily/daily_order_bands.csv')): FO[x['date']] = int(x['orders'])
H = [d for d in sorted(SS) if d < T]
x = [SS[d][0] / MA[d][0] for d in H]; y = [FS[d] / FA[d] for d in H]; df = [b - a_ for a_, b in zip(x, y)]
print(f"\n■ 0〜8時台と終日の関係（{H[0]}〜{H[-1]}・{len(H)}日）: 売上÷広告費 r={st.correlation(x, y):.2f}・終日−0〜8時台 中央値{st.median(df):+.2f}（{min(df):+.2f}〜{max(df):+.2f}）／注文 r={st.correlation([SS[d][1] for d in H], [FO[d] for d in H]):.2f}・0〜8時台の注文が終日に占める割合 中央値{st.median(SS[d][1]/FO[d] for d in H)*100:.0f}%")
print('  日別（0〜8時台 → 終日の売上÷広告費）: ' + ' '.join(f"{d[5:]} {SS[d][0]/MA[d][0]:.2f}→{FS[d]/FA[d]:.2f}" for d in H[-8:]))
# 商品別
print('\n■ 商品別（0〜8時台）: 今日 個数・広告費・倍率（粗利−広告費）・クリック率・1クリック・Metaカート・Meta購入 ／ 過去7日の同時刻 倍率の中央値（広告費2,000円以上の日）・個数の中央値・クリック率・1クリック')
names = sorted({k[1] for k in MC if k[0] == T and MC[k][0] > 0}, key=lambda n: -MC[(T, n)][0])
for n in names:
    def pm(d):
        gr, dc = PS.get((d, n), [0, 0]); a_ = MC[(d, n)][0]; u = gr // PRICE[n] if gr and PRICE.get(n) else 0
        return (None if not a_ else (gr - dc - u * COST.get(n, 0)) / a_), u, a_, gr - dc - u * COST.get(n, 0) - a_
    m, u, a_, p = pm(T); c = MC[(T, n)]
    xs = [pm(d) for d in P7 if MC[(d, n)][0] >= 2000]; cs = [MC[(d, n)] for d in P7 if MC[(d, n)][0] >= 2000]
    f = lambda v: '—' if v is None else f'{v:.2f}'
    hist = f"{st.median(x_[0] for x_ in xs):.2f}（{len(xs)}日）・{st.median(x_[1] for x_ in xs):g}個・{sum(c_[2] for c_ in cs)/sum(c_[1] for c_ in cs)*100:.2f}%・{sum(c_[0] for c_ in cs)/sum(c_[2] for c_ in cs):.0f}円" if xs else '—'
    print(f"  {n}: {u}個・{a_:,}円・{f(m)}（{p:+,}）・{c[2]/c[1]*100 if c[1] else 0:.2f}%・{c[0]/c[2] if c[2] else 0:.0f}円・カート{c[4]}・購入{c[5]} ／ {hist}")
nos = [(n, v) for (d, n), v in PS.items() if d == T and n not in names and v[0]]
print('  広告なしで売れた: ' + '・'.join(f"{n} {v[0]-v[1]:,}" for n, v in nos))
