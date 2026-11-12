# -*- coding: utf-8 -*-
"""11/12 11:28: 商品ごとの評価（終日データ 11/5〜11/11 が判定の土台。今日の分は途中なので参考）。
倍率=(売上−原価)÷広告費（原価は代表原価×個数。ナノは加重平均【近似】）。Meta日別はキャンペーン別の実測（scripts/daily/o11*/meta_camp_*）。
着地ページの率は Shopify sessions（商品ページに最初に着いた来訪 → カート投入 → 購入完了）。"""
import os, csv, json, glob, pickle, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
P = pickle.load(open('/tmp/rep1111w.pkl', 'rb')); COST = dict(P['COST']); PRICE = dict(P['PRICE']); MAP = P['MAP']
COST['ナノガラス脱毛パッド'] = (927 * 757 + 326 * 740) / 1253; COST['高見えレザーヘッドレストフック'] = 732
S = collections.defaultdict(dict); A = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['date'] >= '2026-11-05': S[r['name']][r['date']] = (int(r['gross']), int(r['disc']))
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if r['date'] >= '2026-11-05': A[r['campaign']][r['date']] = A[r['campaign']].get(r['date'], 0) + float(r['cost'])
M = {}
for f in sorted(glob.glob(R + 'scripts/daily/o11*/meta_camp_*_raw.txt')):
    for ln in open(f):
        if not ln.startswith('2026-'): continue
        p = ln.strip().split(','); M[(p[0], p[1])] = [0.0 if x in ('null', '') else float(x) for x in p[2:8]]
raw = json.load(open(D + 'eval_products_raw.json'))
LPK = {'vacuum-adsorption': 'W固定スマホ車載ホルダー', 'nano-fine-fiber': '伸縮ガラスクリーナー', 'washable-reusable-fuzz': 'ナノガラス脱毛パッド', 'soft-silicone-car-squeegee': 'ワイド水切りワイパー',
       'silicone-magnetic-door': 'マグネットドアクッション', 'car-wash-cotton': '伸縮ワックス洗車ブラシ', 'portable-small-wireless-mini-dust': '4-in-1マルチクリーナー',
       'waterproof-film': 'クリアビューレインガードフィルム', 'soft-super-sports': '快適マジックインソール', 'seat-hook': '高見えレザーヘッドレストフック'}
LP = collections.defaultdict(dict)
for k in ('lp_1022_1104', 'lp_1105_1108', 'lp_1109_1111'):
    for path, s, c, ck, cp in raw[k]['rows']:
        for key, n in LPK.items():
            if key in path: LP[n][k] = (int(s), int(c), int(ck), int(cp))
O7 = collections.defaultdict(int)
for t, c in json.load(open(R + 'scripts/daily/o1111/ord7_raw.json'))['rows']:
    for n in sorted(PRICE, key=len, reverse=True):
        if n in t: O7[n] += int(c); break
TS = {}
for t, o, u, g, dc in raw['today_sales']['rows']:
    for n in sorted(PRICE, key=len, reverse=True):
        if n in t: TS[n] = (int(o), int(g) // PRICE[n], int(g) + int(dc)); break
TM = {}
for ln in open(D + 'meta_camp_today_1128.txt'):
    if ln[0] == '#' or not ln.strip(): continue
    n, *v = ln.strip().split(','); TM[n] = [float(x) for x in v]
D7 = ['2026-11-%02d' % i for i in range(5, 12)]; E = D7[:4]; L = D7[4:]
def win(n, ds):
    c = MAP.get(n, n)
    net = sum(S[n][d][0] - S[n][d][1] for d in ds if d in S[n]); u = sum(S[n][d][0] / PRICE[n] for d in ds if d in S[n])
    ad = sum(A[c].get(d, 0) for d in ds); k = u * COST[n]
    return net, k, ad, u
def meta(n, ds):
    c = MAP.get(n, n); t = [sum(M.get((d, c), [0] * 6)[i] for d in ds) for i in range(6)]
    return (t[0] / t[1] * 1000, t[2] / t[1] * 100, t[0] / t[2]) if t[1] and t[2] else None
ORDER = ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '伸縮ワックス洗車ブラシ', 'クリアビューレインガードフィルム', 'マグネットドアクッション', '4-in-1マルチクリーナー', '快適マジックインソール']
for n in ORDER:
    net7, k7, a7, u7 = win(n, D7); netE, kE, aE, uE = win(n, E); netL, kL, aL, uL = win(n, L)
    dm = []
    for d in D7:
        x = win(n, [d]); dm.append('—' if x[2] < 500 else f'{(x[0]-x[1])/x[2]:.2f}')
    mE, mL = meta(n, E), meta(n, L)
    print(f'■ {n}（{PRICE[n]:,}円・1個の粗利 {PRICE[n]-COST[n]:,.0f}円）')
    print(f'  倍率: 7日 {(net7-k7)/a7:.2f}（利益 {net7-k7-a7:+,.0f}・広告 {a7:,.0f}）／11/5-8 {(netE-kE)/aE:.2f} → 11/9-11 {(netL-kL)/aL:.2f}（利益 {netL-kL-aL:+,.0f}）／日別 ' + '・'.join(dm))
    if mE and mL: print(f'  広告: 1クリック {mE[2]:.0f}→{mL[2]:.0f}円（{(mL[2]/mE[2]-1)*100:+.0f}%）・表示単価 {mE[0]:,.0f}→{mL[0]:,.0f}・クリック率 {mE[1]:.2f}→{mL[1]:.2f}%')
    lp = LP[n]; seg = []
    for k, lab in (('lp_1022_1104', '10/22-11/4'), ('lp_1105_1108', '11/5-8'), ('lp_1109_1111', '11/9-11')):
        if k in lp:
            s, c, ck, cp = lp[k]; seg.append(f'{lab} 来訪{s}・カート{c/s*100:.1f}%・購入{cp/s*100:.2f}%・決済完了{(cp/ck*100 if ck else 0):.0f}%')
    print('  ページ: ' + ' ／ '.join(seg))
    cl = MAP.get(n, n); cE = sum(M.get((d, cl), [0]*6)[2] for d in E); cL = sum(M.get((d, cl), [0]*6)[2] for d in L)
    print(f'  クリック100回あたりの個数: {uE/cE*100:.1f}→{uL/cL*100:.1f}個 ／ 1注文あたり {u7/O7[n]:.2f}個（7日） ／ 注文1件の広告費 11/5-8 {aE/(uE/(u7/O7[n])):,.0f}→11/9-11 {aL/(uL/(u7/O7[n])):,.0f}円（倍率1.25になるのは {(PRICE[n]-COST[n])*(u7/O7[n])*0.97/1.25:,.0f}円以下・値引き3%を見込む）')
    t = TS.get(n, (0, 0, 0)); tm = TM.get(MAP.get(n, n), [0]*6)
    print(f'  今日（11:28まで・参考）: {t[1]}個・広告 {tm[0]:,.0f}円・クリック {tm[2]:.0f}')
print('\n■ 出したばかり（今日の途中経過・判定は予定日）')
for n in ['防風あったか裏起毛パンツ', 'UV歯ブラシ除菌器', 'バランスケアスリッパ', '高見えレザーヘッドレストフック']:
    t = TS.get(n, (0, 0, 0)); tm = TM.get(MAP.get(n, n), [0]*6)
    print(f"  {n}: 今日 {t[1]}個・広告 {tm[0]:,.0f}円・表示 {tm[1]:.0f}・クリック {tm[2]:.0f}" + (f"（クリック率 {tm[2]/tm[1]*100:.2f}%・1クリック {tm[0]/tm[2]:.0f}円）" if tm[2] else ''))
x = win('防風あったか裏起毛パンツ', ['2026-11-11'])
print(f"  裏起毛パンツ 11/11: {x[3]:.0f}個・広告 {x[2]:,.0f}円")
print('  今日の合計（11:28まで）: 注文', sum(v[0] for v in TS.values()), '・広告費', f"{sum(v[0] for v in TM.values()):,.0f}円")
