# -*- coding: utf-8 -*-
"""11/18 よく売れる・長く売れる商品の違い。weekly_life.json（Shopify の週ごとの倍率）＋ meta_weekly_raw.txt（Meta の週ごと）＋ reach_life_raw.txt（期間全体の人数）
最初の2週の CPM・クリック率・購入÷クリック と、倍率1.25以上が続いた週数・その後の落ち方を並べ、順位相関を出す"""
import json, collections, math
L = json.load(open('weekly_life.json'))
FIX = {'ディスペンサー': '壁掛けディスペンサー', 'ネックマッサージャー2': 'ネックマッサージャー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン': '4WAY', '完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶', '3WAYサーキュレーター扇風機': '3WAYサーキュレーター'}
def prod(c):
    if c in FIX: return FIX[c]
    b = c.rstrip('0123456789 ').rstrip('v').rstrip()
    for p in L:
        if b == p or b.startswith(p) or p.startswith(b): return p
num = lambda x: 0 if x == 'null' else float(x)
M = collections.defaultdict(lambda: [0.0] * 8)  # (p, isoweek) -> cost imp reach(重複あり) _ clk lpv atc pur
for l in open('meta_weekly_raw.txt'):
    if l[0] == '#': continue
    w, c, *v = l.strip().split(','); p = prod(c)
    if not p: continue
    wn = int(w.split('|')[1]) - 27
    for i, x in enumerate(v): M[(p, wn)][i] += num(x)
R = {}
for l in open('reach_life_raw.txt'):
    if l[0] == '#': continue
    c, cost, imp, reach, fq, clk, pur = l.strip().split(','); p = prod(c)
    if p: R[p] = (float(cost), float(imp), float(reach), float(fq), num(clk), num(pur))
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r
def rho(a, b):
    ra, rb = rank(a), rank(b); n = len(a); ma, mb = sum(ra) / n, sum(rb) / n
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
rows = []
for p, o in L.items():
    ws = sorted(w for (q, w) in M if q == p and M[(q, w)][0] >= 10000)
    if len(ws) < 2: continue
    f2 = ws[:2]; m = [sum(M[(p, w)][i] for w in f2) for i in range(8)]
    later = ws[2:4]; ml = [sum(M[(p, w)][i] for w in later) for i in range(8)] if later else None
    cpm = m[0] / m[1] * 1000; ctr = m[4] / m[1] * 100; ppc = m[7] / m[4] * 100 if m[4] else 0; apc = m[6] / m[4] * 100 if m[4] else 0
    dec = (ml[7] / ml[4]) / (m[7] / m[4]) if ml and ml[4] and m[7] else None
    r = R.get(p)
    rows.append(dict(p=p, cpm=cpm, ctr=ctr, ppc=ppc, apc=apc, dec=dec, run=o['longest'], good=o['good'], active=o['active'], b12=o['b12'], profit=o['profit'], season=o['season'],
                     ongoing=o['series'][-1] is not None, reach=r[2] if r else None, fq=r[3] if r else None, pur_per_1k=r[5] / r[2] * 1000 if r and r[2] else None, first=o['first']))
rows.sort(key=lambda x: -x['run'])
print('商品・続いた最長週（*＝今も出している）・最初2週: CPM／クリック率／カート÷クリック／購入÷クリック・3〜4週目の購入÷クリック（最初2週比）・期間全体: 届いた人数／1人あたり表示回数／1000人あたり購入')
for x in rows:
    print(f"  {x['p'][:14]:<14} {x['run']:>2}週{'*' if x['ongoing'] else ' '} {x['season'] or '?':<2}｜CPM {x['cpm']:>5,.0f}・クリック率 {x['ctr']:.2f}%・カート {x['apc']:.1f}%・購入 {x['ppc']:.2f}%｜3〜4週目 {('%.0f%%' % (x['dec']*100)) if x['dec'] else '—':>5}｜人数 {x['reach'] or 0:>9,.0f}・{(x['fq'] or 0):.2f}回・{(x['pur_per_1k'] or 0):.2f}件")
print()
for lab, sub in (('全商品', rows), ('夏物を除く', [x for x in rows if x['season'] != '夏'])):
    print(f'■ 続いた最長週との順位相関（{lab}・{len(sub)}商品・|ρ|≥{2/math.sqrt(len(sub)-1):.2f} でおおよそ偶然では起きにくい）')
    for k, lab2 in (('cpm', '最初2週の CPM'), ('ctr', 'クリック率'), ('apc', 'カート÷クリック'), ('ppc', '購入÷クリック'), ('b12', '最初2週の倍率')):
        print(f'   {lab2}: ρ = {rho([x[k] for x in sub], [x["run"] for x in sub]):+.2f}')
    s2 = [x for x in sub if x['reach']]
    print(f'   期間全体の届いた人数: ρ = {rho([x["reach"] for x in s2], [x["run"] for x in s2]):+.2f}（{len(s2)}商品）')
    s3 = [x for x in sub if x['dec']]
    print(f'   3〜4週目の落ち方（購入÷クリックの比）と最初2週の CPM: ρ = {rho([x["cpm"] for x in s3], [x["dec"] for x in s3]):+.2f}（{len(s3)}商品）')
lo = [x for x in rows if x['cpm'] < 2500]; hi = [x for x in rows if x['cpm'] >= 2500]
md = lambda v: sorted(v)[len(v) // 2]
print(f"■ 最初2週の CPM 2,500円未満 {len(lo)}商品: 続いた週の中央値 {md([x['run'] for x in lo])}・利益の合計 {sum(x['profit'] for x in lo):+,}／2,500円以上 {len(hi)}商品: {md([x['run'] for x in hi])}・{sum(x['profit'] for x in hi):+,}")
json.dump(rows, open('why_life.json', 'w'), ensure_ascii=False, indent=0)
# 量（よく売れる）: 最初2週の CPM と、利益の合計・1週の広告費の最大
PK = {}
for (p, w), v in M.items(): PK[p] = max(PK.get(p, 0), v[0])
for x in rows: x['peak'] = PK.get(x['p'], 0)
print(f"■ 量との順位相関（全{len(rows)}商品）: 最初2週の CPM と 利益の合計 ρ = {rho([x['cpm'] for x in rows], [x['profit'] for x in rows]):+.2f}・1週の広告費の最大 ρ = {rho([x['cpm'] for x in rows], [x['peak'] for x in rows]):+.2f}／最初2週の倍率と利益の合計 ρ = {rho([x['b12'] for x in rows], [x['profit'] for x in rows]):+.2f}")
for lab, f in (('通年×CPM2,500未満', lambda x: x['season'] != '夏' and x['cpm'] < 2500), ('通年×CPM2,500以上', lambda x: x['season'] != '夏' and x['cpm'] >= 2500), ('夏物', lambda x: x['season'] == '夏')):
    s = [x for x in rows if f(x)]
    print(f"  {lab}: {len(s)}商品・続いた週の中央値 {md([x['run'] for x in s])}・8週以上 {sum(x['run'] >= 8 for x in s)}・1週の広告費の最大の中央値 {md([x['peak'] for x in s]):,.0f}・{'・'.join(x['p'][:8] + str(x['run']) for x in sorted(s, key=lambda x: -x['run']))}")
