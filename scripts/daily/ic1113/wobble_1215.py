# -*- coding: utf-8 -*-
"""11/13(金) 12:1x 「Metaがブレた話を含めて、既存の広告は昔と比べてだいぶブレているのか？」
長く出している4商品（ナノガラス脱毛パッド・W固定スマホ車載ホルダー・快適マジックインソール・伸縮ガラスクリーナー）について、日ごとのブレを月ごとに比べる。
①売れ方のブレ: 1日の個数（Shopify・売価3,980円で割り切れることを確認）を、その週（月〜日）の平均の売れ方×その日の広告費で期待した個数と比べる。
  ばらつき指数 ＝ Σ(実際−期待)² ÷ Σ期待。1前後なら「1日の個数が少ないことによる自然なぶれ」だけ、1より大きいほど余分にブレている
②倍率（（売上−原価）÷広告費）の前日との差の中央値（個数が少ないと大きく出る）
③Meta側のブレ: CPM・クリック率・1クリックの広告費の、その週の平均からの日ごとのずれ（相対・中央値）。Meta計上の購入にも①と同じばらつき指数
入力: data/daily/*.csv・scripts/daily/ic1113/meta_daily_4prod_0801_1112.txt。広告費3,000円未満の日は除く"""
import os, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
P = ['ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '快適マジックインソール', '伸縮ガラスクリーナー']
COST = {'ナノガラス脱毛パッド': 752, 'W固定スマホ車載ホルダー': 1069, '快適マジックインソール': 677, '伸縮ガラスクリーナー': None}
src = open(R + 'scripts/product_tabs.py').read(); g = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], g)
for n in P: COST[n] = g['COST'][n]; assert g['PRICE'][n] == 3980, n
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] in P: S[(r['name'], r['date'])][0] += int(r['gross']); S[(r['name'], r['date'])][1] += int(r['disc'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if r['campaign'] in P: A[(r['campaign'], r['date'])] += float(r['cost'])
M = {}
for l in open(D + 'meta_daily_4prod_0801_1112.txt'):
    if l[0] == '#': continue
    d, n, c, i, cl, pu = l.strip().split(','); M[(n, d)] = (int(c), int(i), int(cl), int(pu))
for (n, d), v in M.items(): assert abs(v[0] - A[(n, d)]) <= max(5, 0.002 * v[0]), (n, d, v[0], A[(n, d)])   # Meta日別 = 日次CSV
MON = [('8月', '2026-08-01', '2026-08-31'), ('9月', '2026-09-01', '2026-09-30'), ('10月前半', '2026-10-01', '2026-10-15'), ('10月後半', '2026-10-16', '2026-10-31'), ('11月(1-12日)', '2026-11-01', '2026-11-12')]
wk = lambda d: datetime.date.fromisoformat(d).isocalendar()[:2]
def rows(n, a, b):
    out = []
    d0 = datetime.date.fromisoformat(a)
    while d0.isoformat() <= b:
        d = d0.isoformat(); ad = A.get((n, d), 0)
        if ad >= 3000:
            gr, dc = S.get((n, d), [0, 0]); assert gr % 3980 == 0, (n, d, gr); u = gr // 3980
            out.append(dict(d=d, ad=ad, u=u, m=(gr - dc - u * COST[n]) / ad, meta=M.get((n, d))))
        d0 += datetime.timedelta(1)
    return out
def disp(rs, key):   # 週ごとの売れ方で期待値を作る
    byw = collections.defaultdict(list)
    for r in rs: byw[wk(r['d'])].append(r)
    num = den = 0
    for w, x in byw.items():
        if len(x) < 4: continue
        rate = sum(key(r) for r in x) / sum(r['ad'] for r in x)
        for r in x: lam = rate * r['ad']; num += (key(r) - lam) ** 2; den += lam
    return num / den if den else None
def rel(rs, f):     # 週の平均からの相対ずれ（中央値）
    byw = collections.defaultdict(list)
    for r in rs:
        if r['meta']: byw[wk(r['d'])].append(f(r['meta']))
    dev = []
    for x in byw.values():
        if len(x) >= 4: m = st.mean(x); dev += [abs(v / m - 1) for v in x]
    return st.median(dev) if dev else None
print('商品・時期: 日数｜1日の広告費（中央値）｜1日の個数（平均）｜①ばらつき指数（Shopify個数）｜Meta購入のばらつき指数｜②倍率の前日との差（中央値）｜③CPM・クリック率・1クリックの週平均からのずれ（中央値）')
SUM = collections.defaultdict(list)
for n in P:
    for lab, a, b in MON:
        rs = rows(n, a, b)
        if len(rs) < 8: continue
        di = disp(rs, lambda r: r['u']); dm = disp([r for r in rs if r['meta']], lambda r: r['meta'][3])
        sw = st.median(abs(rs[i]['m'] - rs[i - 1]['m']) for i in range(1, len(rs)))
        cpm = rel(rs, lambda v: v[0] / v[1]); ctr = rel(rs, lambda v: v[2] / v[1]); cpc = rel(rs, lambda v: v[0] / v[2])
        SUM[lab].append((di, dm, sw, cpm, ctr, cpc, st.mean(r['u'] for r in rs)))
        print(f"  {n[:10]}・{lab}: {len(rs)}日｜{st.median(r['ad'] for r in rs):,.0f}円｜{st.mean(r['u'] for r in rs):.1f}個｜{di:.2f}｜{dm:.2f}｜{sw:.2f}｜{cpm*100:.0f}%・{ctr*100:.0f}%・{cpc*100:.0f}%")
print('\n時期ごとの中央値（4商品）: ①ばらつき指数（Shopify）・Meta購入のばらつき指数・②倍率の前日との差・③CPM・クリック率・1クリックのずれ・1日の個数')
for lab, *_ in MON:
    v = SUM[lab]
    if v: print(f"  {lab}: {st.median(x[0] for x in v):.2f}・{st.median(x[1] for x in v):.2f}・{st.median(x[2] for x in v):.2f}・{st.median(x[3] for x in v)*100:.0f}%・{st.median(x[4] for x in v)*100:.0f}%・{st.median(x[5] for x in v)*100:.0f}%・{st.median(x[6] for x in v):.1f}個（{len(v)}商品）")
