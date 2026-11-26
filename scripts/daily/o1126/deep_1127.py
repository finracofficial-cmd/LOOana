# -*- coding: utf-8 -*-
"""11/27 定例の深掘り（11/26 の実績）。
① 11/26 の利益を、前7日（11/19〜25）の平均との差（倍率の分・量の分）に分ける。W固定を除いた形も出す
② 消化（広告費 ÷ その日の最終日予算の合計）を日ごとに並べる
③ 同じキャンペーンの中での CPM・クリック率・クリック1回の値段: 11/26 ↔ そのキャンペーンの前7日（11/19〜25）
④ W固定スマホ車載ホルダー（注文2件・偶然では起きにくい低さ）の中身: Meta のクリックと、Shopify の商品ページの段ごとの数
⑤ 伸縮ワックス洗車ブラシの再開初日（11/26 17:21〜）
⑥ 入口別（social／direct）の来訪と買う率: 11/26 ↔ 11/19〜25
入力: w1126.py（CSV）・budget-snapshots.csv・ad_level_1026_1126.txt・meta_ad_1126_raw.json・lp_1126_raw.json・lp_1119_1125_raw.json・sess_source_1126_raw.json・../o11xx/sess_source_*_raw.json・../ic1126/brush/*_raw.json"""
import io, contextlib, json, os, csv, math, collections, datetime, glob
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1126.py').read(), g)
A, ALLD, agg, WIN, ACCT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT']
out = []
def P(s=''): print(s); out.append(s)
T = '2026-11-26'; PV = ('2026-11-19', '2026-11-25')
def tot(days):
    k = 'x' + days[0] + days[-1]; WIN[k] = days; N, DC, Q, K = agg(days, k); return sum(N.values()), sum(K.values()), ACCT(days), N, K
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
# ---- ① ----
s, k, a, N, K = tot([T]); p = s - k - a; D7p = ALLD[-8:-1]; assert (D7p[0], D7p[-1]) == PV; s7, k7, a7, _, _ = tot(D7p); m7 = (s7 - k7) / a7; m = (s - k) / a
P(f"■ ① 11/26 の利益 {p:,.0f}（倍率 {m:.2f}・広告費 {a:,.0f}・暫定）↔ 前の7日（11/19〜25）の平均 {(s7-k7-a7)/7:,.0f}/日（倍率 {m7:.2f}・広告費 {a7/7:,.0f}/日）")
P(f"  差 {p-(s7-k7-a7)/7:+,.0f} ＝ 倍率の分 {(m-m7)*a:+,.0f} ＋ 量の分 {(m7-1)*(a-a7/7):+,.0f}")
for n in ('ナノガラス脱毛パッド', '伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー'):
    gp = N.get(n, 0) - K.get(n, 0); ad = A([T], n); gp7 = (lambda t: t[3].get(n, 0) - t[4].get(n, 0))(tot(D7p)); ad7 = A(D7p, n)
    P(f"  {n}: 利益 {gp-ad:+,.0f}（倍率 {gp/ad:.2f}・広告費 {ad:,.0f}）↔ 前7日の平均 {(gp7-ad7)/7:+,.0f}/日（{gp7/ad7:.2f}・{ad7/7:,.0f}）")
w = 'W固定スマホ車載ホルダー'; gw = N.get(w, 0) - K.get(w, 0); aw = A([T], w)
P(f"  W固定を除くと: 利益 {p-(gw-aw):,.0f}・倍率 {((s-k)-gw)/(a-aw):.2f}")
# ---- ② 消化 ----
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
P('■ ② 消化（その日の広告費 ÷ 翌日 00時台の記録の日予算の合計。途中で出した・止めた商品がある日はずれる）')
line = []
for d in ALLD[-14:]:
    b = sum(SN[nxt(d)].values()) if nxt(d) in SN else 0; line.append(f"{d[5:]}（{g['wd'](d)}）{ACCT([d])/b:.0%}" if b else f"{d[5:]} —")
P('  ' + '・'.join(line))
b26 = sum(SN['2026-11-27'].values()); bb = sum(v for (c, a_), v in SN['2026-11-27'].items() if c == '伸縮ワックス洗車ブラシ'); ab = A([T], '伸縮ワックス洗車ブラシ'); a3 = sum(A([T], n) for n in ('姿勢サポートチェア', '3WAY着る電気ブランケット', '2WAYシートボックス'))
P(f"  11/26: {a:,.0f} ÷ {b26:,} ＝ {a/b26:.1%}（広告費は暫定）｜17:21 に再開したブラシ（予算 {bb:,}・広告費 {ab:,.0f}）と 00時台に止めた3本（{a3:,.0f}）を除くと {(a-ab-a3)/(b26-bb):.1%}")
# ---- ③ 同じキャンペーンの中 ----
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
for l in open(D0 + 'ad_level_1026_1126.txt'):
    if l[0] == '#': continue
    d, c, a_, ad, cost, imp, clk = l.strip().split(','); x = R[c][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
P('■ ③ 同じキャンペーンの中: 前7日（11/19〜25）→ 11/26 の CPM｜クリック率｜クリック1回の値段')
tt = [0, 0, 0]; tp = [0, 0, 0]
for c in sorted(R, key=lambda c: -R[c].get(T, [0])[0]):
    t = R[c].get(T, [0, 0, 0]); pv = [v for d, v in R[c].items() if PV[0] <= d <= PV[1]]; pc, pi, pk = (sum(v[i] for v in pv) for i in range(3))
    if t[0] < 1000: continue
    if pi < 5000: P(f"  {c}: （前7日の配信が少ない）→ CPM {t[0]/t[1]*1000:,.0f}・クリック率 {t[2]/t[1]:.2%}・クリック1回 {t[0]/max(1,t[2]):.0f}円"); continue
    for i in range(3): tt[i] += t[i]
    tp[0] += pc / pi * t[1]; tp[2] += pk / pi * t[1]; tp[1] += t[1]   # 前7日は「11/26 の表示の割合」で重みをつける（顔ぶれの違いを除く）
    P(f"  {c}: CPM {pc/pi*1000:,.0f} → {t[0]/t[1]*1000:,.0f}（{(t[0]/t[1])/(pc/pi)-1:+.0%}）｜{pk/pi:.2%} → {t[2]/t[1]:.2%}｜{pc/pk:.0f} → {t[0]/max(1,t[2]):.0f}円（{(t[0]/max(1,t[2]))/(pc/pk)-1:+.0%}）")
P(f"  上の合計（11/26 の表示の割合でそろえた）: CPM {tp[0]/tp[1]*1000:,.0f} → {tt[0]/tt[1]*1000:,.0f}（{(tt[0]/tt[1])/(tp[0]/tp[1])-1:+.0%}）｜クリック率 {tp[2]/tp[1]:.2%} → {tt[2]/tt[1]:.2%}｜クリック1回 {tp[0]/tp[2]:.0f} → {tt[0]/tt[2]:.0f}円（{(tt[0]/tt[2])/(tp[0]/tp[2])-1:+.0%}）")
# ---- ④ W固定 ----
LP = lambda f: {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D0 + f))['rows']}
l1, l7 = LP('lp_1126_raw.json'), LP('lp_1119_1125_raw.json'); HW = '/products/vacuum-adsorption-car-mobile-phone-folding-360-rotating-suction-cup-bracket'
x1, x7 = l1[HW], l7[HW]; cw = 'W固定スマホ車載ホルダー'; t = R[cw][T]; pv = [v for d, v in R[cw].items() if PV[0] <= d <= PV[1]]; pc, pi, pk = (sum(v[i] for v in pv) for i in range(3))
P('■ ④ W固定スマホ車載ホルダー（11/26 注文 2件・倍率 0.46。11/25 は 1.23＝2日続けて 1.25 未満）')
P(f"  Meta: 広告費 {t[0]:,}・クリック {t[2]}（クリック率 {t[2]/t[1]:.2%}・クリック1回 {t[0]/t[2]:.0f}円）↔ 前7日 {pc/7:,.0f}/日・{pk/7:.0f}クリック/日（{pk/pi:.2%}・{pc/pk:.0f}円）＝クリックの数と値段は前7日と同じ水準")
P(f"  商品ページに着いた来訪（Shopify）: 11/26 {x1[0]}・カート {x1[1]}（{x1[1]/x1[0]:.1%}）・決済画面 {x1[2]}・購入 {x1[3]}（{x1[3]/x1[0]:.2%}）↔ 11/19〜25 {x7[0]:,}・カート {x7[1]}（{x7[1]/x7[0]:.1%}）・決済画面 {x7[2]}・購入 {x7[3]}（{x7[3]/x7[0]:.2%}）")
e = x1[0] * x7[3] / x7[0]; ec = x1[0] * x7[1] / x7[0]; r = x7[3] / x7[2]
bino = lambda k_, n_, p_: sum(math.comb(n_, i) * p_ ** i * (1 - p_) ** (n_ - i) for i in range(k_ + 1))
P(f"  来訪 {x1[0]} × 前7日の買う率 ＝ 見込み {e:.1f}件 → 実際 {x1[3]}件（{x1[3]}件以下 {ple(x1[3], e):.0%}）｜カートは見込み {ec:.1f} → {x1[1]}（{x1[1]}以下 {ple(x1[1], ec):.0%}）｜決済画面 {x1[2]}人のうち購入 {x1[3]}（前7日の完了率 {r:.0%} なら {x1[3]}人以下 {bino(x1[3], x1[2], r):.0%}）")
P('  ＝クリックは来ていて、カートも入っている。少なかったのは決済画面から先。ページ・決済に不具合があったかはこの数字では分からない（カートと購入が 0 ではないので、止まっていたわけではない）')
# ---- ⑤ ブラシの初日 ----
z = lambda x: 0 if x in ('null', '') else int(x)
M = [l.strip().split(',') for l in json.load(open(D0 + 'meta_ad_1126_raw.json'))['data']['data'].split('\n')[1:] if l.strip()]
rs = [r_ for r_ in M if r_[1] == '伸縮ワックス洗車ブラシ']; assert len(rs) == 1 and rs[0][3] == 'A'
cost, imp, clk, lpv, atc, pu = (z(rs[0][i]) for i in (4, 5, 6, 7, 8, 9)); HB = '/products/car-wash-cotton-thread-telescopic-wax-mop'; xb = l1[HB]
nb = '伸縮ワックス洗車ブラシ'; gb = N.get(nb, 0) - K.get(nb, 0)
P('■ ⑤ 伸縮ワックス洗車ブラシの再開初日（11/26 17:21〜・旧キャンペーン・広告A だけ・8,000円）')
P(f"  Meta（暫定）: 広告費 {cost:,}・表示 {imp:,}・クリック {clk}（クリック率 {clk/imp:.2%}）・クリック1回 {cost/clk:.0f}円・CPM {cost/imp*1000:,.0f}・来訪 {lpv}（÷クリック {lpv/clk:.2f}）・カート {atc}・購入 {pu}（Meta）")
P(f"  Shopify: 注文 1件・1個・粗利 {gb:,.0f} → 倍率 {gb/cost:.2f}・利益 {gb-cost:+,.0f}｜商品ページに着いた来訪（終日）{xb[0]}・カート {xb[1]}・決済画面 {xb[2]}・購入 {xb[3]}")
def meta_tbl(f):
    raw = json.load(open(f, encoding='utf-8'))['data']['data']; head, *lines = raw.split('\n'); cols = head[head.index('{') + 1:head.index('}')].split(',')
    return [dict(zip(cols, r_)) for r_ in csv.reader(io.StringIO('\n'.join(l.strip() for l in lines)))]
BM = collections.defaultdict(lambda: [0.0, 0.0])
for r_ in meta_tbl('scripts/daily/ic1126/brush/brush_daily_1023_1126_raw.json'): BM[r_['date']][0] += float(r_['cost']); BM[r_['date']][1] += 0 if r_['link_clicks'] in ('null', '') else float(r_['link_clicks'])
BO = {r_[0][:10]: (int(r_[1]), float(r_[2]) + float(r_[3]) - round(float(r_[2]) / g['PRICE'][nb]) * g['COST'][nb]) for r_ in json.load(open('scripts/daily/ic1126/brush/brush_sales_daily_1023_1126_raw.json', encoding='utf-8'))['rows']}
def rng(a_, b_):
    a_, b_ = datetime.date.fromisoformat(a_), datetime.date.fromisoformat(b_); return [(a_ + datetime.timedelta(n_)).isoformat() for n_ in range((b_ - a_).days + 1)]
for lab, ds in (('最初の2週（10/23〜11/5）', rng('2026-10-23', '2026-11-05')), ('止める前の12日（11/6〜17）', rng('2026-11-06', '2026-11-17'))):
    kk = sum(BM[d][1] for d in ds); oo = sum(BO[d][0] for d in ds if d in BO); gg = sum(BO[d][1] for d in ds if d in BO); cc = sum(BM[d][0] for d in ds)
    P(f"  {lab}: クリック1回 {cc/kk:.0f}円・注文÷クリック {oo/kk:.2%}・クリック1回の粗利 {gg/kk:.0f}円（倍率 1.25 の線 {gg/kk/1.25:.0f}円・1.5 の線 {gg/kk/1.5:.0f}円）→ {clk}クリックの見込み {clk*oo/kk:.1f}件")
P(f"  1注文の粗利 3,380円（1個・値引きなし）で 倍率 1.5 に要るのは 広告費 {gb/1.5:,.0f}円あたり1件。事故停止の線（購入0のまま 10,140円）には当たらない（1件売れた）")
# ---- ⑥ 入口別 ----
src = {r_[0]: [int(x) for x in r_[1:]] for r_ in json.load(open(D0 + 'sess_source_1126_raw.json'))['rows']}
prev = collections.defaultdict(lambda: [0, 0, 0, 0]); nday = 0
for d in ('1119', '1120', '1121', '1122', '1123', '1124', '1125'):
    f = glob.glob(f'scripts/daily/o{d}/sess_source_{d}_raw.json')
    if not f: continue
    nday += 1
    for r_ in json.load(open(f[0]))['rows']:
        for i in range(4): prev[r_[0]][i] += int(r_[1 + i])
P(f'■ ⑥ 入口別（11/26 ↔ 11/19〜25 のうち記録のある {nday}日の平均）')
for k_ in ('social', 'direct'):
    t_ = src[k_]; pv_ = prev[k_]
    P(f"  {k_}: 来訪 {t_[0]:,}（平均 {pv_[0]/nday:,.0f}）・カート率 {t_[1]/t_[0]:.2%}（{pv_[1]/pv_[0]:.2%}）・買う率 {t_[3]/t_[0]:.2%}（{pv_[3]/pv_[0]:.2%}）")
ts = sum(v[0] for v in src.values()); lk = sum(z(r_[6]) for r_ in M)
P(f"  direct の割合: 11/26 {src['direct'][0]/ts:.0%}｜{nday}日の平均 {prev['direct'][0]/sum(v[0] for v in prev.values()):.0%}｜Meta のリンククリック（11/26）{lk:,} → social の来訪 ÷ クリック {src['social'][0]/lk:.2f}・全部の来訪 ÷ クリック {ts/lk:.2f}")
open(D0 + 'deep_1127.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
