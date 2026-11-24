# -*- coding: utf-8 -*-
"""11/24 20時台「単価低いし、CVR低いし、広告効率下がってるの謎」
9/29〜11/23 を7日ずつ8つに分け、①倍率＝(クリック÷広告費)×(注文÷クリック)×(1注文の売上)×(粗利÷売上) に分解 ②1注文の売上を 個数÷注文・1個の値段 に分ける
③広告費を「出してからの日数」（その商品の広告が14日以上止まったあとに始まった日から数える）で分け、倍率の低下が「同じ年齢の商品が落ちた」のか「お金の行き先が古い商品に寄った」のかを分ける。
入力: w1123.py（商品別の売上・値引・原価・広告費）・data/daily/daily_order_bands.csv（注文数）・sess_0928_1123_raw.json（Shopify 来訪）・meta_acct_0928_1123_raw.json（Meta 表示・リンククリック）"""
import io, contextlib, json, csv, math, os, collections, datetime
os.chdir('/home/user/LOOana'); D0 = 'scripts/daily/ic1124/why/'
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, ACCT, CAT, PRICE, S, AD, MAP, MULTI = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT'], g['CAT'], g['PRICE'], g['S'], g['AD'], g['MAP'], g['MULTI']
ORD = {r['date']: int(r['orders']) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
SES = {r[0]: (int(r[1]), int(r[4])) for r in json.load(open(D0 + 'sess_0928_1123_raw.json'))['rows']}
MET = {}
for l in json.load(open(D0 + 'meta_acct_0928_1123_raw.json'))['data']['data'].split('\n')[1:]:
    if l.strip(): d, c, i, k = l.strip().split(','); MET[d] = (float(c), int(i), int(k))
days = [d for d in ALLD if '2026-09-29' <= d <= '2026-11-23']; assert len(days) == 56
blocks = [days[i:i + 7] for i in range(0, 56, 7)]
# 日ごとの商品別（売上・原価・個数）
DAY = {}
for d in days:   # バリアント別の原価が 7/17 からなので、使う 9/29〜11/23 だけ
    WIN['w' + d] = [d]; N, DC, Q, K = agg([d], 'w' + d); DAY[d] = (N, Q, K)
prods = set(n for d in days for n in DAY[d][0])
# 商品ごとの「出してからの日数」: 広告が14日以上止まったあとに始まった日から
age = {}
for n in prods:
    run = None; last = None
    for d in [x for x in ALLD if x <= '2026-11-23']:
        if A([d], n) > 0:
            dd = datetime.date.fromisoformat(d)
            if last is None or (dd - last).days > 14: run = dd
            last = dd; age[(n, d)] = (dd - run).days
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('■ ① 7日ずつの店全体（9/29〜11/23）: 倍率 ＝ クリック÷広告費 × 注文÷クリック × 1注文の売上 × 粗利÷売上')
P('  期間       | 広告費/日 | 倍率 | クリック1回 | CPM   | クリック率 | 来訪÷クリック | 買う率（注文÷来訪） | 注文÷クリック | 1注文の売上 | 個数÷注文 | 1個の値段 | 4,980円以上の売上の割合 | 原価÷売上')
R = []
for b in blocks:
    ad = sum(MET[d][0] for d in b); imp = sum(MET[d][1] for d in b); clk = sum(MET[d][2] for d in b)
    assert abs(ad - ACCT(b)) / ad < 0.01, (b[0], ad, ACCT(b))
    net = sum(sum(DAY[d][0].values()) for d in b); cogs = sum(sum(DAY[d][2].values()) for d in b)
    q = sum(v for d in b for n, v in DAY[d][1].items() if PRICE.get(n, 0) >= 1000)
    hi = sum(v for d in b for n, v in DAY[d][0].items() if PRICE.get(n, 0) >= 4980)
    o = sum(ORD[d] for d in b); ses = sum(SES[d][0] for d in b)
    r = dict(lab=f'{b[0][5:]}〜{b[-1][5:]}', ad=ad, m=(net - cogs) / ad, cpc=ad / clk, cpm=ad / imp * 1000, ctr=clk / imp, sc=ses / clk, cvr=o / ses, oc=o / clk, aov=net / o, ipo=q / o, ppi=net / q, hi=hi / net, cr=cogs / net, net=net, cogs=cogs, o=o, clk=clk)
    R.append(r)
    P(f"  {r['lab']} | {ad/7:>9,.0f} | {r['m']:.2f} | {r['cpc']:>5.0f}円 | {r['cpm']:>5,.0f} | {r['ctr']:.2%} | {r['sc']:.2f} | {r['cvr']:.2%} | {r['oc']:.2%} | {r['aov']:>6,.0f} | {r['ipo']:.2f} | {r['ppi']:>6,.0f} | {r['hi']:.0%} | {r['cr']:.1%}")
a = R[0:2]; z = R[-2:]
def pool(rs):
    ad = sum(r['ad'] for r in rs); clk = sum(r['clk'] for r in rs); o = sum(r['o'] for r in rs); net = sum(r['net'] for r in rs); cogs = sum(r['cogs'] for r in rs)
    return dict(m=(net - cogs) / ad, cpc=ad / clk, oc=o / clk, aov=net / o, gm=(net - cogs) / net)
pa, pz = pool(a), pool(z); tot = math.log(pz['m'] / pa['m'])
P(f"■ 倍率の低下を分ける（最初の2週 9/29〜10/12 → 最後の2週 11/10〜11/23）: 倍率 {pa['m']:.2f} → {pz['m']:.2f}（{pz['m']/pa['m']-1:+.1%}）")
for k, lab, sgn in (('cpc', 'クリック1回の値段', -1), ('oc', '注文÷クリック（買う率の側）', 1), ('aov', '1注文の売上（単価）', 1), ('gm', '粗利÷売上（原価の側）', 1)):
    c = sgn * math.log(pz[k] / pa[k])
    P(f"  {lab}: {pa[k]:,.4g} → {pz[k]:,.4g}（{pz[k]/pa[k]-1:+.1%}）→ 倍率の低下のうち {c/tot:.0%}")
# ③ 年齢別
B = (('出して2週以内', 0, 13), ('3〜6週目', 14, 41), ('7週目以降', 42, 10**6))
P('■ ③ 広告費を「出してからの日数」で分ける（商品の広告費と粗利。カタログ・広告なしの商品は別）')
SH = []
for b, r in zip(blocks, R):
    ad = collections.Counter(); gp = collections.Counter(); cnt = collections.defaultdict(set)
    for d in b:
        N, Q, K = DAY[d]
        for n in prods:
            x = A([d], n)
            if x > 0:
                k = next(lab for lab, lo, hi in B if lo <= age[(n, d)] <= hi); ad[k] += x; gp[k] += N.get(n, 0) - K.get(n, 0); cnt[k].add(n)
            else:
                gp['広告なしの商品'] += N.get(n, 0) - K.get(n, 0)
    ad['カタログ'] = CAT(b)
    tot_ad = r['ad']; SH.append((ad, gp, tot_ad))
    P(f"  {r['lab']}: " + '・'.join(f"{lab} 広告費の {ad[lab]/tot_ad:.0%}（{len(cnt[lab])}本）倍率 {gp[lab]/ad[lab]:.2f}" for lab, _, _ in B if ad[lab]) + f"・カタログ {ad['カタログ']/tot_ad:.0%}・広告なしの商品の粗利 {gp['広告なしの商品']/7:,.0f}/日")
# 倍率の低下を「年齢ごとの倍率が落ちた分」と「お金の行き先が変わった分」に分ける（商品の広告費の中だけ）
def mix(i):
    ad, gp, _ = SH[i]; T = sum(ad[l] for l, _, _ in B); return {l: ad[l] / T for l, _, _ in B}, {l: (gp[l] / ad[l] if ad[l] else 0) for l, _, _ in B}
def pooled(ids):
    ad = collections.Counter(); gp = collections.Counter()
    for i in ids:
        for l, _, _ in B: ad[l] += SH[i][0][l]; gp[l] += SH[i][1][l]
    T = sum(ad.values()); return {l: ad[l] / T for l, _, _ in B}, {l: gp[l] / ad[l] for l, _, _ in B}
w0, m0 = pooled([0, 1]); w1, m1 = pooled([6, 7])
base = sum(w0[l] * m0[l] for l in w0); now = sum(w1[l] * m1[l] for l in w1)
within = sum(w0[l] * (m1[l] - m0[l]) for l in w0); shift = sum((w1[l] - w0[l]) * m1[l] for l in w0)
P(f"  商品の広告費だけの倍率 {base:.2f} → {now:.2f}（{now-base:+.2f}）＝ 同じ年齢の中で倍率が落ちた分 {within:+.2f}＋お金の行き先が変わった分 {shift:+.2f}")
P('    ' + '・'.join(f"{l}: 広告費の割合 {w0[l]:.0%} → {w1[l]:.0%}・倍率 {m0[l]:.2f} → {m1[l]:.2f}" for l, _, _ in B))
open(D0 + 'why_1124.txt', 'w').write('\n'.join(out) + '\n')
# ④ 10/27 から（リンククリックがキャンペーン別にある期間）: 年齢別の クリック1回の値段 ↔ クリック1回の粗利
REV = {}
for n in prods:
    for c in (MULTI[n] if n in MULTI else (MAP.get(n, n),)): REV[c] = n
CK = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0]))
for l in open('scripts/daily/o1123/ad_level_1026_1123.txt'):
    if l[0] == '#': continue
    d, c, a_, ad_, cost, imp, clk = l.strip().split(',')
    if c in REV and float(cost) > 0: v = CK[(REV[c], d)][c]; v[0] += float(cost); v[1] += int(clk)
P('■ ④ 年齢別の クリック1回の値段 ↔ クリック1回の粗利（10/27 から。商品の広告だけ・カタログは除く）')
for lab2, ds in (('10/27〜11/09', [d for d in days if '2026-10-27' <= d <= '2026-11-09']), ('11/10〜11/23', [d for d in days if d >= '2026-11-10'])):
    agg2 = collections.defaultdict(lambda: [0.0, 0, 0.0]); names = collections.defaultdict(set)
    for d in ds:
        N, Q, K = DAY[d]
        for n in prods:
            if (n, d) not in age: continue
            k = next(lab for lab, lo, hi in B if lo <= age[(n, d)] <= hi)
            cost = sum(v[0] for v in CK[(n, d)].values()); clk = sum(v[1] for v in CK[(n, d)].values())
            x = agg2[k]; x[0] += cost; x[1] += clk; x[2] += N.get(n, 0) - K.get(n, 0); names[k].add(n)
    P(f'  {lab2}: ' + '・'.join(f"{k} クリック1回 {x[0]/x[1]:.0f}円 ↔ 粗利 {x[2]/x[1]:.0f}円（{x[1]:,}クリック・{len(names[k])}本）" for k, x in ((l, agg2[l]) for l, _, _ in B) if x[1]))
open(D0 + 'why_1124.txt', 'w').write('\n'.join(out) + '\n')
# ⑤ 値段帯ごと（10/27〜11/23・広告を出した商品の日だけ）: クリック1回の値段 ↔ クリック1回の粗利・個数÷クリック・1個の粗利
P('■ ⑤ 値段帯ごと（10/27〜11/23・その商品に広告費が出た日だけ）')
band = lambda p: '3,980円' if p <= 3980 else '4,980円' if p <= 4980 else '5,980〜8,980円'
BB = collections.defaultdict(lambda: [0.0, 0, 0.0, 0, set()])
for d in [x for x in days if x >= '2026-10-27']:
    N, Q, K = DAY[d]
    for n in prods:
        cost = sum(v[0] for v in CK[(n, d)].values()); clk = sum(v[1] for v in CK[(n, d)].values())
        if cost <= 0 or clk == 0: continue
        x = BB[band(PRICE[n])]; x[0] += cost; x[1] += clk; x[2] += N.get(n, 0) - K.get(n, 0); x[3] += Q.get(n, 0); x[4].add(n)
for k in ('3,980円', '4,980円', '5,980〜8,980円'):
    x = BB[k]
    P(f"  {k}（{len(x[4])}本）: クリック1回 {x[0]/x[1]:.0f}円 ↔ 粗利 {x[2]/x[1]:.0f}円・倍率 {x[2]/x[0]:.2f}・個数÷クリック {x[3]/x[1]:.2%}・1個の粗利 {x[2]/x[3]:,.0f}円｜" + '・'.join(sorted(x[4])))
# ⑥ 原価: 直近28日の原価/日（値下げ交渉の大きさの目安）
c28 = sum(sum(DAY[d][2].values()) for d in days[-28:]) / 28
top = collections.Counter()
for d in days[-28:]:
    for n, v in DAY[d][2].items(): top[n] += v / 28
P(f'■ ⑥ 原価 直近28日（10/27〜11/23）: {c28:,.0f}円/日 → 5% 下がれば {c28*0.05:,.0f}円/日・10% なら {c28*0.10:,.0f}円/日｜多い順: ' + '・'.join(f'{n} {v:,.0f}' for n, v in top.most_common(6)))
open(D0 + 'why_1124.txt', 'w').write('\n'.join(out) + '\n')
