# -*- coding: utf-8 -*-
"""11/25 定例の深掘り（11/24 の実績）。
① 広告セット別（W固定・ガラス）の直近7日: 広告費・消化・クリック・Meta の購入（増額をどの広告セットに出すか）
② 11/24 の利益を「今日から止まっている商品（UV v2・毛玉 v2）」を除いた形に直す
③ 決済画面からの完了・入口別の買う率が偶然の範囲か ④ 4,980円以上の商品の割合（11/24 ↔ 前の30日）⑤ Meta 計上の購入 ↔ Shopify の注文
入力: ad_level_1026_1124.txt・ad_purchase_*.txt・budget-snapshots.csv・w1124.py・sess_daily_1004_1124.json・sess_source_1124_raw.json・../ic1124/cvr/sess_source_week_0929_1123_raw.json"""
import io, contextlib, json, os, csv, math, collections, datetime
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1124.py').read(), g)
A, ALLD, agg, WIN, ACCT, PRICE = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT'], g['PRICE']
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
T = '2026-11-24'; D7 = ALLD[-7:]
# ① 広告セット別
R = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
for l in open(D0 + 'ad_level_1026_1124.txt'):
    if l[0] == '#': continue
    d, c, a, ad, cost, imp, clk = l.strip().split(','); x = R[(c, a)][d]; x[0] += int(cost); x[1] += int(imp); x[2] += int(clk)
PF = [('scripts/daily/o1119/ad_purchase_1118_1119.txt', ('2026-11-18',)), ('scripts/daily/o1120/ad_purchase_1119_1120.txt', ('2026-11-19',)), ('scripts/daily/o1121/ad_purchase_1120_1121.txt', ('2026-11-20',)), ('scripts/daily/o1122/ad_purchase_1121_1122.txt', ('2026-11-21',)), ('scripts/daily/o1123/ad_purchase_1122_1123.txt', ('2026-11-22',)), ('scripts/daily/o1124/ad_purchase_1123_1124.txt', ('2026-11-23', '2026-11-24'))]
for f, keep in PF:
    for l in open(f):
        if l[0] == '#': continue
        p = l.strip().split(',')
        if p[0] in keep: R[(p[1], p[2])][p[0]][3] += int(p[7])
SN = collections.defaultdict(dict)
for r in csv.DictReader(open('data/budget-snapshots.csv')): SN[r['snapshot_date']][(r['campaign'], r['adset'])] = int(r['daily_budget'])
nxt = lambda d: (datetime.date.fromisoformat(d) + datetime.timedelta(1)).isoformat()
P('■ ① 広告セット別の直近7日（11/18〜24）: 広告費・Meta の購入・購入1件の広告費・クリック1回｜11/24 の消化（広告費÷その日の最終の日予算）')
for k in [('W固定スマホ車載ホルダー', 'W固定スマホ車載ホルダー'), ('W固定スマホ車載ホルダー', 'W固定スマホ車載ホルダー -sab'), ('伸縮ガラスクリーナー', '伸縮ガラスクリーナー'), ('伸縮ガラスクリーナー', '伸縮ガラスクリーナー sabu')]:
    v = [R[k][d] for d in D7]; c = sum(x[0] for x in v); clk = sum(x[2] for x in v); pu = sum(x[3] for x in v); t = R[k][T]; b = SN[nxt(T)][k]
    daily = '・'.join(f"{d[8:]}日 {R[k][d][0]/SN[nxt(d)][k]:.0%}" for d in D7[-3:])
    P(f"  {k[1]}: 広告費 {c:,}・購入 {pu}・1件 {c/pu:,.0f}円・クリック1回 {c/clk:.0f}円｜11/24 広告費 {t[0]:,}÷日予算 {b:,}＝{t[0]/b:.0%}・購入 {t[3]}（消化 {daily}）")
# ② 止めた商品を除く
WIN['dp'] = [T]; N, DC, Q, K = agg([T], 'dp'); S = sum(N.values()); KK = sum(K.values()); ad = ACCT([T]); prof = S - KK - ad
P(f'■ ② 11/24: 売上 {S:,}・原価 {KK:,}・広告費 {ad:,.0f}・利益 {prof:,.0f}・倍率 {(S-KK)/ad:.2f}')
ex = ('UV歯ブラシ除菌器', 'コードレス毛玉クリーナー')
s2 = S - sum(N.get(n, 0) for n in ex); k2 = KK - sum(K.get(n, 0) for n in ex); a2 = ad - sum(A([T], n) for n in ex)
P(f"  20時台に止めた UV v2・毛玉 v2（広告費 {sum(A([T], n) for n in ex):,.0f}・粗利 {sum(N.get(n,0)-K.get(n,0) for n in ex):,}）を除くと: 利益 {s2-k2-a2:,.0f}・倍率 {(s2-k2)/a2:.2f}")
ex3 = ex + ('充電式ダブルミスト卓上加湿器',)
s3 = S - sum(N.get(n, 0) for n in ex3); k3 = KK - sum(K.get(n, 0) for n in ex3); a3 = ad - sum(A([T], n) for n in ex3)
P(f"  さらに卓上加湿器（広告費 {A([T], '充電式ダブルミスト卓上加湿器'):,.0f}・0個）も除くと: 利益 {s3-k3-a3:,.0f}・倍率 {(s3-k3)/a3:.2f}")
# ③ 決済画面からの完了・入口別
SD = json.load(open(D0 + 'sess_daily_1004_1124.json'))['rows']; base = [r for r in SD if '2026-10-25' <= r[0] <= '2026-11-23']; t = [r for r in SD if r[0] == T][0]
pc = sum(int(r[4]) for r in base) / sum(int(r[3]) for r in base); e = int(t[3]) * pc; sd = math.sqrt(int(t[3]) * pc * (1 - pc))
P(f"■ ③ 決済画面からの完了: 11/24 {t[4]}/{t[3]}＝{int(t[4])/int(t[3]):.0%}（前の30日 {pc:.0%}・見込み {e:.1f}件・{(int(t[4])-e)/sd:+.1f}σ）／カート率 {int(t[2])/int(t[1]):.2%}（前の30日 {sum(int(r[2]) for r in base)/sum(int(r[1]) for r in base):.2%}）")
wk = collections.defaultdict(lambda: [0, 0])
for w, src, s, c, ch, done in json.load(open('scripts/daily/ic1124/cvr/sess_source_week_0929_1123_raw.json'))['rows']:
    if '2026-10-26' <= w <= '2026-11-16': wk[src][0] += int(s); wk[src][1] += int(done)
for r in json.load(open(D0 + 'sess_source_1124_raw.json'))['rows']:
    if r[0] in ('social', 'direct'):
        p0 = wk[r[0]][1] / wk[r[0]][0]; e = int(r[1]) * p0; k = int(r[4])
        P(f"  {r[0]}: 来訪 {r[1]}・購入 {k}（{k/int(r[1]):.2%}）｜10/26〜11/22 の4週 {p0:.2%} → 見込み {e:.1f}件・{(k-e)/math.sqrt(e):+.1f}σ")
# ④ 4,980円以上の割合
def hi(days, key):
    WIN[key] = days; N, DC, Q, K = agg(days, key); q = sum(v for n, v in Q.items() if PRICE.get(n, 0) >= 1000); h = sum(v for n, v in Q.items() if PRICE.get(n, 0) >= 4980); return h, q
h1, q1 = hi([T], 'h1'); h30, q30 = hi(ALLD[-31:-1], 'h30'); e = q1 * h30 / q30
lo = sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(h1 + 1))
P(f'■ ④ 4,980円以上の商品: 11/24 {h1}/{q1}個（{h1/q1:.0%}）｜前の30日 {h30}/{q30}個（{h30/q30:.0%}）→ 見込み {e:.1f}個・この数以下 {lo:.1%}（個数はまとめ買いでかたまるので、実際のぶれはこれより大きい）')
# ⑤ Meta 計上の購入
mp = sum(x[T][3] for x in R.values()); mc = sum(x[T][2] for x in R.values()); mi = sum(x[T][1] for x in R.values())
P(f'■ ⑤ Meta（11/24・暫定）: 表示 {mi:,}・クリック {mc:,}・クリック1回 {ad/mc:.0f}円・CPM {ad/mi*1000:,.0f}・Meta の購入 {mp}件 ↔ Shopify の注文 72件')
open(D0 + 'deep_1125.txt', 'w').write('\n'.join(out) + '\n')
