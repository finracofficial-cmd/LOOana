# -*- coding: utf-8 -*-
"""11/23 13時台「クリックが高くても単価が高くて売れていればいい？／クリックの高い広告はどうすれば下げられる？／フックは女性に限定したほうがいい？」の数字。
入力: w1122.py（daily_*.csv）・o1122/orders_7d_1116_1122_raw.json・o1122/ad_level_1026_1122.txt・この cpc/ の Meta 取得（性別×年代・配置・キャンペーン×性別・広告ごとの Meta の評価）・ic1123/hook の取得"""
import io, contextlib, os, json, re, collections, math
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1122.py').read(), g)
WIN, agg, A, ALLD, MULTI, MAP = g['WIN'], g['agg'], g['A'], g['ALLD'], g['MULTI'], g['MAP']; D7 = ALLD[-7:]
def table(f, base=D0):
    out = []
    for l in json.load(open(base + f))['data']['data'].split('\n')[1:]:
        l = l.strip()
        if l: out.append(l.split(','))
    return out
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
IDN = {r[0]: nm(r[1]) for f in ('product_totals_1022_1120_raw.json', 'product_totals_0629_1120_raw.json') for r in json.load(open('scripts/daily/ic1121/aov/' + f))['rows'] if r[0]}
O7 = {IDN[r[0]]: int(r[1]) for r in json.load(open('scripts/daily/o1122/orders_7d_1116_1122_raw.json'))['rows'] if r[0] in IDN}
CL = collections.defaultdict(int); IM = collections.defaultdict(int)
for l in open('scripts/daily/o1122/ad_level_1026_1122.txt'):
    if l[0] == '#': continue
    d, c, a_, ad, cost, imp, clk = l.strip().split(',')
    if D7[0] <= d <= D7[-1]: CL[c] += int(clk); IM[c] += int(imp)
WIN['c7'] = D7; N, DC, Q, K = agg(D7, 'c7')
P('■ ① クリックの値段と「クリック1回が生む粗利」（11/16〜22・広告費の多い順）')
P('  商品: クリック1回の値段｜注文÷クリック × 1注文の粗利 ＝ クリック1回の粗利｜倍率（＝粗利÷値段）｜倍率 1.25 で払える上限')
rows = []
for n in set(N) | set(MAP) | set(MULTI):
    a = A(D7, n)
    if a < 3000: continue
    camps = MULTI.get(n, (MAP.get(n, n),)); clk = sum(CL[c] for c in camps); o = O7.get(n, 0); m = N.get(n, 0) - K.get(n, 0)
    if not clk: continue
    rows.append((a, n, a / clk, o / clk, (m / o if o else 0), m / clk, m / a, m / clk / 1.25, o))
for a, n, cpc, r, mo, mc, bai, cap, o in sorted(rows, reverse=True):
    P(f'  {n}: {cpc:,.0f}円｜{r:.1%} × {mo:,.0f}円 ＝ {mc:,.0f}円｜{bai:.2f}｜{cap:,.0f}円まで（注文 {o}）' + ('　←値段が上限より高い' if cpc > cap else ''))
# ---- ② だれに出すといくらか（アカウント全体）
P('■ ② 性別×年代（アカウント全体・10/26〜11/22）: CPM・クリック率・クリック1回・購入÷クリック・1購入の広告費（Meta 計上）')
seg = {}
for r in table('acct_agegender_1026_1122_raw.json'):
    if r[1] in ('female', 'male') and r[0] != 'Unknown': seg[(r[1], r[0])] = [z(x) for x in r[2:6]]
for (gd, age), v in sorted(seg.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    P(f"  {'女性' if gd=='female' else '男性'} {age}: CPM {v[0]/v[1]*1000:,.0f}・{v[2]/v[1]:.2%}・{v[0]/v[2]:.0f}円・{v[3]/v[2]:.2%}・{v[0]/v[3]:,.0f}円")
cp = [v[0] / v[2] for v in seg.values()]; ca = [v[0] / v[3] for v in seg.values()]; cm = [v[0] / v[1] * 1000 for v in seg.values()]
P(f'  12の区分の幅: CPM {min(cm):,.0f}〜{max(cm):,.0f}（{max(cm)/min(cm):.1f}倍）・クリック1回 {min(cp):.0f}〜{max(cp):.0f}円（{max(cp)/min(cp):.1f}倍）・1購入の広告費 {min(ca):,.0f}〜{max(ca):,.0f}円（{max(ca)/min(ca):.1f}倍）')
P('■ ③ 配置（アカウント全体・10/26〜11/22）: CPM・クリック率・クリック1回・購入÷クリック・1購入の広告費')
for r in sorted(table('acct_placement_purchase_1026_1122_raw.json'), key=lambda r: -z(r[2]))[:6]:
    v = [z(x) for x in r[2:6]]; P(f'  {r[0]} {r[1]}: CPM {v[0]/v[1]*1000:,.0f}・{v[2]/v[1]:.2%}・{v[0]/v[2]:.0f}円・{v[3]/v[2]:.2%}・{v[0]/v[3]:,.0f}円')
# ---- ④ フック: 同じ人たちに出ているほかの広告と比べる・性別で分ける
H = D0 + '../hook/'
hv = {}
for r in table('hook_v5_agegender_1118_1123_raw.json', H):
    if r[1] in ('female', 'male') and r[0] != 'Unknown': hv[(r[1], r[0])] = [z(x) for x in r[2:6]]
ti = sum(v[1] for k, v in hv.items() if k in seg)
ecpm = sum(v[1] * seg[k][0] / seg[k][1] * 1000 for k, v in hv.items() if k in seg) / ti; ectr = sum(v[1] * seg[k][2] / seg[k][1] for k, v in hv.items() if k in seg) / ti
hc, hi, hk = sum(v[0] for v in hv.values()), sum(v[1] for v in hv.values()), sum(v[2] for v in hv.values())
P('■ ④ フック v5（11/18〜23）')
P(f'  フック v5 と同じ性別×年代の割合で、店の広告のふだんの値段を当てはめると: CPM {ecpm:,.0f}・クリック率 {ectr:.2%}・クリック1回 {ecpm/1000/ectr:.0f}円')
P(f'  フック v5 の実際: CPM {hc/hi*1000:,.0f}（×{hc/hi*1000/ecpm:.2f}）・クリック率 {hk/hi:.2%}（×{hk/hi/ectr:.2f}）・クリック1回 {hc/hk:.0f}円（×{hc/hk/(ecpm/1000/ectr):.2f}）')
old = sum(v[0] for k, v in hv.items() if k[1] in ('55-64', '65+')) / hc; acc_old = sum(v[0] for k, v in seg.items() if k[1] in ('55-64', '65+')) / sum(v[0] for v in seg.values())
P(f'  広告費のうち 55歳以上: フック v5 {old:.0%}・店全体 {acc_old:.0%}')
def gsum(f, base):
    t = {'female': [0, 0, 0, 0], 'male': [0, 0, 0, 0]}
    for r in table(f, base):
        if r[1] in t and r[0] != 'Unknown':
            for i in range(4): t[r[1]][i] += z(r[2 + i])
    return t
pool = {'female': [0, 0, 0, 0], 'male': [0, 0, 0, 0]}
for lab, f in (('9/11〜10/6', 'hook_agegender_0911_1006_raw.json'), ('10/16〜11/3', 'hook_agegender_1016_1103_raw.json'), ('v5 11/18〜23', 'hook_v5_agegender_1118_1123_raw.json')):
    t = gsum(f, H)
    for k in t:
        for i in range(4): pool[k][i] += t[k][i]
    P(f'  {lab}: ' + ' ／ '.join(f"{'女性' if k=='female' else '男性'} クリック1回 {v[0]/v[2]:.0f}円・購入÷クリック {v[3]/v[2]:.1%}（{v[3]}件）・1購入の広告費 {v[0]/v[3]:,.0f}円" for k, v in t.items()))
f_, m_ = pool['female'], pool['male']; p = (f_[3] + m_[3]) / (f_[2] + m_[2]); se = math.sqrt(p * (1 - p) * (1 / f_[2] + 1 / m_[2])); zz = (m_[3] / m_[2] - f_[3] / f_[2]) / se
P(f"  3つの期間の合計: 女性 購入÷クリック {f_[3]/f_[2]:.2%}（{f_[3]}/{f_[2]:,}）・1購入 {f_[0]/f_[3]:,.0f}円 ／ 男性 {m_[3]/m_[2]:.2%}（{m_[3]}/{m_[2]:,}）・1購入 {m_[0]/m_[3]:,.0f}円（買う割合の差 z={zz:.1f}・2 を超えると偶然では起きにくい）")
# ---- ⑤ Meta が広告につけている評価（11/16〜22・表示 2,000 以上）
P('■ ⑤ Meta の評価（品質・反応・購入の見込み。同じ人をねらうほかの広告との比べ）とクリック1回の値段')
JP = {'Above average': '平均より上', 'Average': '平均', 'Below average (bottom 35%)': '下位35%', 'Below average (bottom 20%)': '下位20%', 'Below average (bottom 10%)': '下位10%', 'No rating': '評価なし'}
for l in json.load(open(D0 + 'ad_ranking_1116_1122_raw.json'))['data']['data'].split('\n')[1:]:
    l = l.strip()
    if not l: continue
    m = re.match(r'^(.*?),(.*?),(.*?),(Above average|Average|Below average \(bottom \d+%\)|No rating),(Above average|Average|Below average \(bottom \d+%\)|No rating),(Above average|Average|Below average \(bottom \d+%\)|No rating),(\d+),(\d+|null),(\d+|null),(\d+|null)$', l); assert m, l
    c, s_, ad, q1, q2, q3, cost, imp, clk, pu = m.groups()
    if z(imp) < 2000 or q1 == 'No rating': continue
    P(f'  {s_} {ad}: 品質 {JP[q1]}・反応 {JP[q2]}・購入 {JP[q3]}｜CPM {z(cost)/z(imp)*1000:,.0f}・クリック1回 {z(cost)/z(clk):.0f}円')
open(D0 + 'cpc_1123.txt', 'w').write('\n'.join(out) + '\n')
