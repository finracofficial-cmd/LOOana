# -*- coding: utf-8 -*-
"""11/28 定例の深掘り（11/27 の実績）。
① 11/27 の利益を、前7日（11/20〜26）の平均との差（倍率の分・量の分）に分ける。差の大きい商品も並べる
② 消化（広告費 ÷ その日の最終日予算の合計）を日ごとに並べる
③ 同じキャンペーンの中での CPM・クリック率・クリック1回の値段: 11/27 ↔ そのキャンペーンの前7日（11/20〜26）
④ W固定スマホ車載ホルダー（3日続けて 1.25 未満）: 商品ページの段ごとの数を 11/25〜27 の3日でまとめて見る
⑤ 新商品2本の初日（サンバイザー・ガラスクロス）と、伸縮ワックス洗車ブラシの再開の最終
⑥ アカウントのクリック1回の値段（日別）
⑦ 入口別（social／direct）の来訪と買う率: 11/27 ↔ 11/20〜26
入力: w1127.py（CSV）・budget-snapshots.csv・ad_level_1026_1127.txt・meta_ad_1126_raw.json・meta_ad_1127_raw.json・lp_1127_raw.json・lp_1120_1126_raw.json・lp_wfix_daily_1112_1127_raw.json・lp_new_products_1127_raw.json・
      new_products_sales_1127_1128_0445_raw.json・meta_acct_daily_1004_1127.txt・sess_source_1127_raw.json・../o11xx/sess_source_*_raw.json・../ic1126/breakout/early_1126.txt・../ic1127/cloth/products_recent_2156_raw.json"""
import io, contextlib, json, os, csv, math, collections, datetime, glob
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1127.py').read(), g)
A, ALLD, agg, WIN, ACCT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT']
out = []
def P(s=''): print(s); out.append(s)
T = '2026-11-27'; PV = ('2026-11-20', '2026-11-26')
def tot(days):
    k = 'x' + days[0] + days[-1]; WIN[k] = days; N, DC, Q, K = agg(days, k); return sum(N.values()), sum(K.values()), ACCT(days), N, K
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
# ---- ① ----
s, k, a, N, K = tot([T]); p = s - k - a; D7p = ALLD[-8:-1]; assert (D7p[0], D7p[-1]) == PV; s7, k7, a7, _, _ = tot(D7p); m7 = (s7 - k7) / a7; m = (s - k) / a
P(f"■ ① 11/27 の利益 {p:,.0f}（倍率 {m:.2f}・広告費 {a:,.0f}・暫定）↔ 前の7日（11/20〜26）の平均 {(s7-k7-a7)/7:,.0f}/日（倍率 {m7:.2f}・広告費 {a7/7:,.0f}/日）")
P(f"  差 {p-(s7-k7-a7)/7:+,.0f} ＝ 倍率の分 {(m-m7)*a:+,.0f} ＋ 量の分 {(m7-1)*(a-a7/7):+,.0f}")
_, _, _, N7, K7 = tot(D7p); mv = []
for n in set(N) | set(N7) | {x for x in g['MAP'] if A([T], x) or A(D7p, x)}:
    gp = N.get(n, 0) - K.get(n, 0); ad = A([T], n); gp7 = N7.get(n, 0) - K7.get(n, 0); ad7 = A(D7p, n); mv.append((gp - ad - (gp7 - ad7) / 7, n, gp, ad, gp7, ad7))
P('  前7日の平均との差が大きい商品（±8,000円以上）:')
for dlt, n, gp, ad, gp7, ad7 in sorted(mv):
    if abs(dlt) >= 8000: P(f"    {n}: 利益 {gp-ad:+,.0f}（倍率 {gp/ad if ad else 0:.2f}・広告費 {ad:,.0f}）↔ 前7日の平均 {(gp7-ad7)/7:+,.0f}/日（{gp7/ad7 if ad7 else 0:.2f}・{ad7/7:,.0f}）＝ {dlt:+,.0f}")
# ---- ② 消化 ----
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
P('■ ② 消化（その日の広告費 ÷ 翌日 00時台の記録の日予算の合計。途中で出した・止めた商品がある日はずれる）')
line = []
for d in ALLD[-14:]:
    b = sum(SN[nxt(d)].values()) if nxt(d) in SN else 0; line.append(f"{d[5:]}（{g['wd'](d)}）{ACCT([d])/b:.0%}" if b else f"{d[5:]} —")
P('  ' + '・'.join(line))
b27 = sum(SN['2026-11-28'].values()); newb = sum(v for (c, a_), v in SN['2026-11-28'].items() if c in ('2WAY防眩サンバイザー', 'クリア仕上げガラスクロス')); newa = sum(A([T], n) for n in ('2WAY防眩サンバイザー', 'クリア仕上げガラスクロス')); ab = A([T], '伸縮ワックス洗車ブラシ')
P(f"  11/27: {a:,.0f} ÷ {b27:,} ＝ {a/b27:.1%}（広告費は暫定）｜途中で出した2本（予算 {newb:,}・広告費 {newa:,.0f}）と 14:18 に止めたブラシ（{ab:,.0f}）を除くと {(a-newa-ab)/(b27-newb):.1%}")
# ---- ③ 同じキャンペーンの中 ----
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(D0 + 'ad_level_1026_1127.txt'):
    if l[0] == '#': continue
    d, c, a_, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
P('■ ③ 同じキャンペーンの中: 前7日（11/20〜26）→ 11/27 の CPM｜クリック率｜クリック1回の値段')
tt = [0, 0, 0]; tp = [0, 0, 0]
for c in sorted(R, key=lambda c: -R[c].get(T, [0])[0]):
    t = R[c].get(T, [0, 0, 0]); pv = [v for d, v in R[c].items() if PV[0] <= d <= PV[1]]; pc, pi, pk = (sum(v[i] for v in pv) for i in range(3))
    if t[0] < 1000: continue
    if pi < 5000: P(f"  {c}: （前7日の配信が少ない）→ CPM {t[0]/t[1]*1000:,.0f}・クリック率 {t[2]/t[1]:.2%}・クリック1回 {t[0]/max(1,t[2]):.0f}円"); continue
    for i in range(3): tt[i] += t[i]
    tp[0] += pc / pi * t[1]; tp[2] += pk / pi * t[1]; tp[1] += t[1]   # 前7日は「11/27 の表示の割合」で重みをつける（顔ぶれの違いを除く）
    P(f"  {c}: CPM {pc/pi*1000:,.0f} → {t[0]/t[1]*1000:,.0f}（{(t[0]/t[1])/(pc/pi)-1:+.0%}）｜{pk/pi:.2%} → {t[2]/t[1]:.2%}｜{pc/pk:.0f} → {t[0]/max(1,t[2]):.0f}円（{(t[0]/max(1,t[2]))/(pc/pk)-1:+.0%}）")
P(f"  上の合計（11/27 の表示の割合でそろえた）: CPM {tp[0]/tp[1]*1000:,.0f} → {tt[0]/tt[1]*1000:,.0f}（{(tt[0]/tt[1])/(tp[0]/tp[1])-1:+.0%}）｜クリック率 {tp[2]/tp[1]:.2%} → {tt[2]/tt[1]:.2%}｜クリック1回 {tp[0]/tp[2]:.0f} → {tt[0]/tt[2]:.0f}円（{(tt[0]/tt[2])/(tp[0]/tp[2])-1:+.0%}）")
# ---- ④ W固定（3日まとめて） ----
bino = lambda k_, n_, p_: sum(math.comb(n_, i) * p_ ** i * (1 - p_) ** (n_ - i) for i in range(k_ + 1))
wd_ = [[r_[0][:10]] + [int(x) for x in r_[1:]] for r_ in json.load(open(D0 + 'lp_wfix_daily_1112_1127_raw.json'))['rows']]; assert wd_[-1][0] == T and wd_[0][0] == '2026-11-12'
l3 = [r_ for r_ in wd_ if r_[0] >= '2026-11-25']; b13 = [r_ for r_ in wd_ if r_[0] <= '2026-11-24']; assert len(l3) == 3 and len(b13) == 13
s3, c3, k3, d3 = (sum(r_[i] for r_ in l3) for i in (1, 2, 3, 4)); sb, cb, kb, db = (sum(r_[i] for r_ in b13) for i in (1, 2, 3, 4))
cw = 'W固定スマホ車載ホルダー'; t = R[cw][T]; pv = [v for d, v in R[cw].items() if PV[0] <= d <= PV[1]]; pc, pi, pk = (sum(v[i] for v in pv) for i in range(3))
mw = {d: (lambda x: (x[3].get(cw, 0) - x[4].get(cw, 0)) / A([d], cw))(tot([d])) for d in ALLD[-3:]}
P('■ ④ W固定スマホ車載ホルダー（倍率 ' + '・'.join(f'{d[5:]} {v:.2f}' for d, v in mw.items()) + '＝3日続けて 1.25 未満。11/27 00:17 に -sab を 10,400→8,500）')
P(f"  Meta（11/27）: 広告費 {t[0]:,}・クリック {t[2]}（クリック率 {t[2]/t[1]:.2%}・クリック1回 {t[0]/t[2]:.0f}円）↔ 前7日 {pc/7:,.0f}/日・{pk/7:.0f}クリック/日（{pk/pi:.2%}・{pc/pk:.0f}円）")
P('  商品ページに着いた来訪（Shopify・日別）: ' + '・'.join(f'{r_[0][5:]} 来訪 {r_[1]}／カート {r_[2]}／決済画面 {r_[3]}／購入 {r_[4]}' for r_ in l3))
e3 = s3 * db / sb; ec3 = s3 * cb / sb
P(f"  3日の計: 来訪 {s3}・カート {c3}（{c3/s3:.1%}）・決済画面 {k3}・購入 {d3}（{d3/s3:.2%}）↔ 11/12〜24 の13日: カート {cb/sb:.1%}・購入 {db/sb:.2%}・購入÷決済画面 {db/kb:.0%}")
P(f"  来訪 {s3} × 13日の買う率 ＝ 見込み {e3:.1f}件 → 実際 {d3}件（{d3}件以下 {ple(d3, e3):.0%}）｜カートは見込み {ec3:.1f} → {c3}（{c3}以下 {ple(c3, ec3):.0%}）｜決済画面 {k3}人のうち購入 {d3}（13日の完了率 {db/kb:.0%} なら {d3}人以下 {bino(d3, k3, db/kb):.0%}）")
P(f"  ＝クリックの数と値段・カートまではふだんどおり。少ないのは決済画面から先で、3日まとめると「偶然でも起きるが端」。理由は未確認（商品は 11/27 00:4x の直読で ACTIVE・在庫あり・3,980円）")
# ---- ⑤ 新商品の初日・ブラシの最終 ----
z = lambda x: 0 if x in ('null', '') else int(x)
def mrows(f): return [l.strip().split(',') for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:] if l.strip()]
M = mrows('meta_ad_1127_raw.json'); M26 = mrows('meta_ad_1126_raw.json')
LPN = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
for pth, srcn, *v in json.load(open(D0 + 'lp_new_products_1127_raw.json'))['rows']:
    for i in range(4): LPN[pth.split('/')[-1][:30]][srcn][i] += int(v[i])
PR = {p_['handle']: p_ for p_ in json.load(open('scripts/daily/ic1127/cloth/products_recent_2156_raw.json'))['data']['products']['nodes']}
NS = {(re_[0], re_[1][:10]): (int(re_[2]), int(re_[5])) for re_ in json.load(open(D0 + 'new_products_sales_1127_1128_0445_raw.json'))['rows']}
E = {}; grp = None
import re
for l in open('scripts/daily/ic1126/breakout/early_1126.txt', encoding='utf-8'):
    if l.startswith('■ 当たり'): grp = 'hit'
    elif l.startswith('■ それ以外'): grp = 'oth'
    elif l.startswith('■'): grp = None
    m_ = re.match(r'^  (.+?)（(\d\d-\d\d)〜）: (\d+)個・([\d,]+)円・[\d.]+｜(\d+)個・([\d,]+)円・([\d.]+)｜', l)
    if grp and m_: E[m_.group(1)] = dict(g=grp, q1=int(m_.group(3)), c1=int(m_.group(4).replace(',', '')), q2=int(m_.group(5)), c2=int(m_.group(6).replace(',', '')), m2=float(m_.group(7)))
assert len(E) == 23
P('■ ⑤ 新商品2本の初日（11/27・広告費は暫定）')
for nm_, hd, t0, lab in (('2WAY防眩サンバイザー', 'car-day-and-night-sun-goggles', '14:57', '最初の配信 14:57〜'), ('クリア仕上げガラスクロス', 'thickened-magic-cleaning-cloth', '22:32', '最初の配信 22:32〜')):
    rs = [r_ for r_ in M if r_[1] == nm_]; assert len(rs) == 1 and rs[0][3] == 'A'; cost, imp, clk, lpv, atc, pu = (z(rs[0][i]) for i in (4, 5, 6, 7, 8, 9))
    pr_ = [p_ for h_, p_ in PR.items() if h_.startswith(hd)][0]; price = int(float(pr_['variants']['nodes'][0]['price'])); cmax = max(int(float(v_['inventoryItem']['unitCost']['amount'])) for v_ in pr_['variants']['nodes']); gp_ = price - cmax
    lp_ = LPN[pr_['handle'][:30]]; tot_ = [sum(v[i] for v in lp_.values()) for i in range(4)]; soc = lp_.get('social', [0] * 4)
    s2 = 2 / math.sqrt(clk); o27 = sum(v[0] for (t_, d_), v in NS.items() if nm_ in t_ and d_ == T); o28 = sum(v[1] for (t_, d_), v in NS.items() if nm_ in t_ and d_ == '2026-11-28')
    P(f"  {nm_}（{lab}）: 広告費 {cost:,}（日予算 8,000 の {cost/8000:.0%}）・表示 {imp:,}・クリック {clk}（クリック率 {clk/imp:.2%}）・クリック1回 {cost/clk:.0f}円（{clk}クリックの幅 {cost/clk*math.exp(-s2):.0f}〜{cost/clk*math.exp(s2):.0f}円）・CPM {cost/imp*1000:,.0f}・来訪÷クリック {lpv/clk:.2f}・カート（Meta）{atc}・購入（Meta）{pu}")
    P(f"    Shopify: 商品ページに着いた来訪 {tot_[0]}（social {soc[0]}）・カート {tot_[1]}・決済画面 {tot_[2]}・購入まで行った来訪 {tot_[3]}｜11/27 の注文 {o27}件｜11/28 は 04:45 までに {o28}個（途中の数字）")
    P(f"    1個の粗利 {gp_:,}円（原価 {cmax:,}）→ クリック1回 {cost/clk:.0f}円のままなら、倍率 1.25 に要るのは {gp_/(cost/clk*1.25):.0f}クリックに1個・1.5 は {gp_/(cost/clk*1.5):.0f}クリックに1個 → {clk}クリックの見込み {clk*cost/clk*1.25/gp_:.1f}〜{clk*cost/clk*1.5/gp_:.1f}個・0個になる確率 {math.exp(-cost*1.25/gp_):.0%}〜{math.exp(-cost*1.5/gp_):.0%}")
    P(f"    見る線: 事故停止 {gp_*3:,}円（あと {gp_*3-cost:,}円＝日予算の {(gp_*3-cost)/8000:.0%}）｜2日目（11/28）の終日までの通算（広告費 約 {cost+8000:,}円）で 倍率 1.25 ＝ {(cost+8000)*1.25/gp_:.1f}個・1.5 ＝ {(cost+8000)*1.5/gp_:.1f}個・1.94 ＝ {(cost+8000)*1.94/gp_:.1f}個")
big = [e for e in E.values() if e['c1'] >= 2400]; hz = [e for e in big if e['g'] == 'hit']; oz = [e for e in big if e['g'] == 'oth']; z0 = [(n_, e) for n_, e in E.items() if e['q1'] == 0 and e['c1'] >= 2400]
P(f"  過去の23本の1日目（2,400円以上使った商品）: 当たり {len(hz)}本は全部 1個以上（{min(e['q1'] for e in hz)}〜{max(e['q1'] for e in hz)}個）・それ以外 {len(oz)}本は {sum(1 for e in oz if e['q1']==0)}本が 0個。0個だった {len(z0)}本のうち2日目までの通算が 1.5 以上になったのは {sum(1 for n_, e in z0 if e['m2']>=1.5)}本（" + '・'.join(f"{n_} {e['m2']:.2f}" for n_, e in z0 if e['m2'] >= 1.5) + '。どちらも当たりにはなっていない）')
P('  ＝サンバイザーの初日（4,005円・0個）は「1日目に 2,400円以上で 0個」の形。ガラスクロスは配信が1時間半ほどで、まだ何も言えない量')
nb = '伸縮ワックス洗車ブラシ'; b26 = [r_ for r_ in M26 if r_[1] == nb]; b27 = [r_ for r_ in M if r_[1] == nb]; assert len(b26) == 1 and len(b27) == 1
bc = z(b26[0][4]) + z(b27[0][4]); bk = z(b26[0][6]) + z(b27[0][6]); bi = z(b26[0][5]) + z(b27[0][5]); ba = z(b26[0][8]) + z(b27[0][8]); days_b = ['2026-11-26', T]; sb_, kb_, _, Nb, Kb = tot(days_b); gb = Nb.get(nb, 0) - Kb.get(nb, 0)
P(f"  伸縮ワックス洗車ブラシ（11/26 17:21 再開〜11/27 14:18 停止・型 A）の最終: 広告費 {bc:,}（11/26 確定 {z(b26[0][4]):,}＋11/27 {z(b27[0][4]):,}）・クリック {bk}（クリック率 {bk/bi:.2%}・クリック1回 {bc/bk:.0f}円）・カート（Meta）{ba}・注文 1件・粗利 {gb:,.0f} → 倍率 {gb/bc:.2f}・利益 {gb-bc:+,.0f}（relaunch-log の 1〜2日目 0.45 のまま）")
# ---- ⑥ アカウントのクリック1回の値段 ----
AC = [l.strip().split(',') for l in open(D0 + 'meta_acct_daily_1004_1127.txt') if l[0] != '#']; AC = [(r_[0], int(r_[1]), int(r_[2]), int(r_[4])) for r_ in AC][-14:]
P('■ ⑥ アカウントのクリック1回の値段（日別・14日）: ' + '・'.join(f'{d[5:]} {c/k_:.0f}円' for d, c, i_, k_ in AC))
c7 = sum(x[1] for x in AC[-8:-1]); k7_ = sum(x[3] for x in AC[-8:-1]); i7 = sum(x[2] for x in AC[-8:-1]); lst = AC[-1]
P(f"  11/27: CPM {lst[1]/lst[2]*1000:,.0f}・クリック率 {lst[3]/lst[2]:.2%}・クリック1回 {lst[1]/lst[3]:.0f}円 ↔ 前7日 CPM {c7/i7*1000:,.0f}・{k7_/i7:.2%}・{c7/k7_:.0f}円｜95円以上の日は " + '・'.join(d[5:] for d, c, i_, k_ in AC if c / k_ >= 95) + '（顔ぶれをそろえた比較は ③）')
# ---- ⑦ 入口別 ----
src = {r_[0]: [int(x) for x in r_[1:]] for r_ in json.load(open(D0 + 'sess_source_1127_raw.json'))['rows']}
prev = collections.defaultdict(lambda: [0, 0, 0, 0]); nday = 0
for d in ('1120', '1121', '1122', '1123', '1124', '1125', '1126'):
    f = glob.glob(f'scripts/daily/o{d}/sess_source_{d}_raw.json')
    if not f: continue
    nday += 1
    for r_ in json.load(open(f[0]))['rows']:
        for i in range(4): prev[r_[0]][i] += int(r_[1 + i])
P(f'■ ⑦ 入口別（11/27 ↔ 11/20〜26 のうち記録のある {nday}日の平均）')
for k_ in ('social', 'direct'):
    t_ = src[k_]; pv_ = prev[k_]
    P(f"  {k_}: 来訪 {t_[0]:,}（平均 {pv_[0]/nday:,.0f}）・カート率 {t_[1]/t_[0]:.2%}（{pv_[1]/pv_[0]:.2%}）・買う率 {t_[3]/t_[0]:.2%}（{pv_[3]/pv_[0]:.2%}）")
ts = sum(v[0] for v in src.values()); lk = sum(z(r_[6]) for r_ in M)   # M＝11/27 の広告別（⑤で読んだ）
P(f"  direct の割合: 11/27 {src['direct'][0]/ts:.0%}｜{nday}日の平均 {prev['direct'][0]/sum(v[0] for v in prev.values()):.0%}｜Meta のリンククリック（11/27）{lk:,} → social の来訪 ÷ クリック {src['social'][0]/lk:.2f}・全部の来訪 ÷ クリック {ts/lk:.2f}")
open(D0 + 'deep_1128.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
