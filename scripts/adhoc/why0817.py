# -*- coding: utf-8 -*-
"""「なぜ業績が落ちたのか／夏以外に強い需要はあるのか」の実測分解。

売上・原価 = Shopify実測（daily_sales.csv / daily_variant.csv）
広告費     = Meta実測（daily_ad.csv）
月次       = data/raw/monthly_by_product_20260815.csv（Shopify実測・2026-01〜08/14）
推計は一切しない。取れないものは「取得不可」と書く。
"""
import csv, collections, datetime, runpy

g = runpy.run_path('/home/user/LOOana/scripts/daily/w0816.py')
S, AD, A, MAP, COST, PRICE = g['S'], g['AD'], g['A'], g['MAP'], g['COST'], g['PRICE']
VG, VARC = g['VG'], g['VARC']

# ── 季節/通年の区分（SKILL の分類に従う）──
SEA = {'4WAY','3WAYサーキュレーター','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン',
 '接触冷感UVパーカー','接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット',
 '形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','害虫ブロッカー','湯上がりガーゼワンピース'}

def wk(a, b):
    x = datetime.date.fromisoformat(a); y = datetime.date.fromisoformat(b); o = []
    while x <= y: o.append(x.isoformat()); x += datetime.timedelta(1)
    return o
def net(n, d): return sum(S[n][x][0] - S[n][x][1] for x in d if x in S[n])
def gross(n, d): return sum(S[n][x][0] for x in d if x in S[n])
def cost(n, d):
    if n in VARC:
        GP = {'ナノガラス脱毛パッド': 3980, '壁掛けディスペンサー': None}
        c = 0
        for x in d:
            for grp, gg in VG[n].get(x, {}).items():
                p = 3980 if n == 'ナノガラス脱毛パッド' else (6980 if grp == '3本' else 5980)
                u = VARC[n][0] if grp in ('白緑', '3本') else VARC[n][1]
                c += round(gg / p) * u
        return c
    if n not in PRICE or n not in COST: return 0
    return round(gross(n, d) / PRICE[n]) * COST[n]

WEEKS = [(f'{s[5:]}-{e[8:]}', wk(s, e)) for s, e in
         [('2026-06-29','2026-07-05'),('2026-07-06','2026-07-12'),('2026-07-13','2026-07-19'),
          ('2026-07-20','2026-07-26'),('2026-07-27','2026-08-02'),('2026-08-03','2026-08-09'),
          ('2026-08-10','2026-08-16')]]

print('■ ① 全店の週次（Shopify実売 × Meta広告費・すべて実測）')
print(f'  {"週":<12}{"実売":>12}{"原価":>11}{"広告費":>11}{"利益":>12}{"利益率":>8}{"MER":>7}')
for lbl, d in WEEKS:
    ns = sum(net(n, d) for n in S if n); k = sum(cost(n, d) for n in S if n)
    a = sum(sum(AD[c].get(x, 0) for c in AD) for x in d)
    print(f'  {lbl:<12}{ns:>12,}{k:>11,}{a:>11,.0f}{ns-k-a:>+12,.0f}{(ns-k-a)/ns:>8.1%}{ns/a:>7.2f}')

print('\n■ ② 季節商品 vs 通年商品（同じ週で並べる）')
print(f'  {"週":<12}' + ''.join(f'{h:>13}' for h in
      ['季節 実売','季節 広告','季節 利益','通年 実売','通年 広告','通年 利益']))
hist = []
for lbl, d in WEEKS:
    row = {}
    for tag, names in [('季節', [n for n in S if n in SEA]), ('通年', [n for n in S if n and n not in SEA])]:
        ns = sum(net(n, d) for n in names); k = sum(cost(n, d) for n in names)
        a = sum(A(d, n) for n in names)
        row[tag] = (ns, a, ns - k - a)
    hist.append((lbl, row))
    print(f'  {lbl:<12}' + ''.join(f'{v:>13,.0f}' for t in ('季節','通年') for v in row[t]))
f, l = hist[0][1], hist[-1][1]
print(f'\n  6/29週 → 8/10週の変化')
for t in ('季節', '通年'):
    print(f'    {t}: 実売 {f[t][0]:,} → {l[t][0]:,}（{l[t][0]/f[t][0]-1:+.1%}） / '
          f'MER {f[t][0]/f[t][1]:.2f} → {l[t][0]/l[t][1]:.2f} / '
          f'利益 {f[t][2]:+,.0f} → {l[t][2]:+,.0f}（{l[t][2]-f[t][2]:+,.0f}）')
    print(f'        利益率 {f[t][2]/f[t][0]:.1%} → {l[t][2]/l[t][0]:.1%}')
tot_d = (l['季節'][2] + l['通年'][2]) - (f['季節'][2] + f['通年'][2])
print(f'    全体の利益減 {tot_d:+,.0f}円/週 のうち 季節 {l["季節"][2]-f["季節"][2]:+,.0f}'
      f'（{(l["季節"][2]-f["季節"][2])/tot_d:.0%}） / 通年 {l["通年"][2]-f["通年"][2]:+,.0f}'
      f'（{(l["通年"][2]-f["通年"][2])/tot_d:.0%}）')

print('\n■ ③ 「広告費を減らしたから」なのか「効率が落ちたから」なのかを分ける')
print('   利益 = 広告費 × (MER × 粗利率 − 1)。この2因子に分解する')
print(f'  {"週":<12}{"広告費":>11}{"MER":>7}{"粗利率":>8}{"広告1円あたり利益":>18}{"利益":>12}')
for lbl, d in WEEKS:
    ns = sum(net(n, d) for n in S if n); k = sum(cost(n, d) for n in S if n)
    a = sum(sum(AD[c].get(x, 0) for c in AD) for x in d)
    gm = 1 - k / ns; per = ns / a * gm - 1
    print(f'  {lbl:<12}{a:>11,.0f}{ns/a:>7.2f}{gm:>8.1%}{per:>+18.3f}{a*per:>+12,.0f}')
a0 = sum(sum(AD[c].get(x, 0) for c in AD) for x in WEEKS[0][1])
a1 = sum(sum(AD[c].get(x, 0) for c in AD) for x in WEEKS[-1][1])
def perw(d):
    ns = sum(net(n, d) for n in S if n); k = sum(cost(n, d) for n in S if n)
    a = sum(sum(AD[c].get(x, 0) for c in AD) for x in d)
    return a, ns / a * (1 - k / ns)   # P = MER × 粗利率（利益 = A×(P−1)）
A0, P0 = perw(WEEKS[0][1]); A1, P1 = perw(WEEKS[-1][1])
t1=(A1-A0)*(P0-1); t2=A1*(P1-P0)
print(f'\n  分解（6/29週 → 8/10週・利益 {A0*(P0-1):+,.0f} → {A1*(P1-1):+,.0f}）')
print(f'    ①「広告費を減らした」ぶん     = (A1−A0)×(P0−1) = {t1:+,.0f}円/週（{t1/(t1+t2):.0%}）')
print(f'    ②「1円あたり効率が落ちた」ぶん = A1×(P1−P0)     = {t2:+,.0f}円/週（{t2/(t1+t2):.0%}）')
assert abs((t1+t2)-(A1*(P1-1)-A0*(P0-1)))<1, '分解の検算NG'
print(f'    合計 {t1+t2:+,.0f}円/週（実際の差 {A1*(P1-1)-A0*(P0-1):+,.0f}円 と一致）')

print('\n■ ④ 通年商品だけの推移（「夏以外に需要はあるのか」の唯一の実測）')
YEAR = ['ナノガラス脱毛パッド','ムダ毛シェーバー','W固定スマホ車載ホルダー','2WAYシートボックス',
        '快適マジックインソール','姿勢サポートチェア','バランスケアスリッパ','携帯電動シェーバー']
print(f'  {"商品":<24}' + ''.join(f'{lbl:>13}' for lbl, _ in WEEKS))
for n in YEAR:
    cells = ''
    for lbl, d in WEEKS:
        a = A(d, n)
        cells += f'{(net(n,d)/a):>13.2f}' if a > 0 else f'{"—":>13}'
    print(f'  {n:<24}{cells}   ← 週次MER')
print('\n  通年グループ合計')
for k_, f_ in [('実売', lambda d: sum(net(n, d) for n in YEAR)),
               ('広告費', lambda d: sum(A(d, n) for n in YEAR)),
               ('利益', lambda d: sum(net(n, d) - cost(n, d) - A(d, n) for n in YEAR))]:
    print(f'  {k_:<24}' + ''.join(f'{f_(d):>13,.0f}' for _, d in WEEKS))

print('\n■ ⑤ 自店の月次（Shopify実測・2026-01〜08/14。冬春に何が売れていたか）')
M = collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/raw/monthly_by_product_20260815.csv', encoding='utf-8')):
    M[r['month']][r['product']] += int(r['gross_sales'])
for m in sorted(M):
    tot = sum(M[m].values()); top = sorted(M[m].items(), key=lambda x: -x[1])[:3]
    print(f'  {m}  gross {tot:>11,}  商品数 {len(M[m]):>2}   ' +
          ' / '.join(f'{n[:14]} {v:,}' for n, v in top))
