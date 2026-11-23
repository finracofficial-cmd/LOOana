# -*- coding: utf-8 -*-
"""11/23「フックは過去たくさん売れてた。もっと売るには？CPM 高いし売れないのが問題か」: 9/9〜の期間ごとに、広告（CPM・クリック率・クリック1回の値段・購入÷クリック）とお店（個数・倍率・ページの買う率）を並べる。
入力: hook_daily_0909_1122_raw.json（Meta・キャンペーン名にヘッドレストフックを含む・日別）・hook_*_agegender_*・hook_*_placement_*・hook_*reach_*（Meta）・
hook_landing_sessions_0909_1123_raw.json（Shopify・フックの商品ページに着いた来訪・日別）・data/daily/daily_sales.csv（個数・売上）。原価は 10/7 から 732円（それまで 黒 1,275／茶灰 1,344 → daily_variant.csv）"""
import json, os, csv, collections, math
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D0 + '../../../../'
def table(f):
    out = []
    for l in json.load(open(D0 + f))['data']['data'].split('\n')[1:]:
        l = l.strip()
        if l: out.append(l.split(','))
    return out
z = lambda x: 0 if x in ('null', '') else int(round(float(x)))
M = collections.defaultdict(lambda: [0] * 6)   # 日別（全キャンペーン合算）: cost, imp, clk, lpv, atc, pur
for r in table('hook_daily_0909_1122_raw.json'):
    for i in range(6): M[r[0]][i] += z(r[2 + i])
S = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == '高見えレザーヘッドレストフック': S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
VG = collections.defaultdict(dict)
for r in csv.DictReader(open(R + 'data/daily/daily_variant.csv')):
    if r['name'] == '高見えレザーヘッドレストフック': VG[r['date']][r['cost_group']] = int(r['gross'])
def cogs(d):
    g = S[d][0]
    if not g: return 0
    if d >= '2026-10-07': return g // 3980 * 732
    v = VG.get(d); assert v and sum(v.values()) == g, (d, v, g); return v.get('黒', 0) // 3980 * 1275 + v.get('茶灰', 0) // 3980 * 1344
L = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D0 + 'hook_landing_sessions_0909_1123_raw.json'))['rows']}   # 来訪・カート・決済画面・購入
import datetime
def days(a, b):
    x = datetime.date.fromisoformat(a); o = []
    while x <= datetime.date.fromisoformat(b): o.append(x.isoformat()); x += datetime.timedelta(1)
    return o
PER = [('A 9/11〜10/6（よく売れた時期）', '2026-09-11', '2026-10-06'), ('B 10/7〜10/15', '2026-10-07', '2026-10-15'), ('C 10/16〜10/26（日予算 8,000〜10,000）', '2026-10-16', '2026-10-26'),
       ('D 10/27〜11/3（止める前）', '2026-10-27', '2026-11-03'), ('E v5 11/18〜11/22', '2026-11-18', '2026-11-22')]
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('■ ① フックの期間ごと（広告は Meta・個数と売上は Shopify）')
P('  期間: 日数｜広告費/日・個数/日・倍率｜CPM・クリック率・クリック1回｜Meta 購入・購入÷クリック・1購入の広告費｜ページに着いた来訪・カート率・購入÷来訪')
X = {}
for lab, a, b in PER:
    ds = days(a, b); c = [sum(M[d][i] for d in ds) for i in range(6)]; g = sum(S[d][0] for d in ds); dc = sum(S[d][1] for d in ds); q = g // 3980; k = sum(cogs(d) for d in ds)
    ls = [sum(L.get(d, [0, 0, 0, 0])[i] for d in ds) for i in range(4)]
    X[lab[0]] = dict(n=len(ds), cost=c[0], imp=c[1], clk=c[2], pur=c[5], q=q, net=g - dc, k=k, ls=ls)
    P(f"  {lab}: {len(ds)}日｜{c[0]/len(ds):,.0f}・{q/len(ds):.1f}個・{(g-dc-k)/c[0]:.2f}｜{c[0]/c[1]*1000:,.0f}・{c[2]/c[1]:.2%}・{c[0]/c[2]:,.0f}円｜{c[5]}件・{c[5]/c[2]:.2%}・{c[0]/c[5]:,.0f}円｜{ls[0]:,}・{ls[1]/ls[0]:.1%}・{ls[3]/ls[0]:.2%}")
a, e = X['A'], X['E']
P(f"  A → E: CPM ×{(e['cost']/e['imp'])/(a['cost']/a['imp']):.2f}・クリック率 ×{(e['clk']/e['imp'])/(a['clk']/a['imp']):.2f}・クリック1回 ×{(e['cost']/e['clk'])/(a['cost']/a['clk']):.2f}・購入÷クリック ×{(e['pur']/e['clk'])/(a['pur']/a['clk']):.2f}・1購入の個数 {a['q']/a['pur']:.2f} → {e['q']/e['pur']:.2f}")
pois = lambda k, l: math.exp(-l + k * math.log(l) - math.lgamma(k + 1)); ple = lambda k, l: sum(pois(i, l) for i in range(k + 1))
c, d = X['C'], X['D']; exp_d = d['clk'] * c['pur'] / c['clk']
P(f"  C → D: クリック1回 {c['cost']/c['clk']:,.0f} → {d['cost']/d['clk']:,.0f}円（×{(d['cost']/d['clk'])/(c['cost']/c['clk']):.2f}）・購入÷クリック {c['pur']/c['clk']:.2%} → {d['pur']/d['clk']:.2%}（C の率なら {exp_d:.1f}件のところ {d['pur']}件・この数以下 {ple(d['pur'], exp_d):.1%}）")
exp_e = e['clk'] * a['pur'] / a['clk']; P(f"  E: A の 購入÷クリック（{a['pur']/a['clk']:.2%}）なら {exp_e:.1f}件のところ {e['pur']}件（この数以下 {ple(e['pur'], exp_e):.0%}）")
P(f"  倍率 1.25 に必要な 1購入の広告費: 1購入の粗利（E の実績 {(e['net']-e['k'])/e['pur']:,.0f}円）÷1.25 ＝ {(e['net']-e['k'])/e['pur']/1.25:,.0f}円。購入÷クリック {e['pur']/e['clk']:.2%} のままなら クリック1回 {(e['net']-e['k'])/e['pur']/1.25*e['pur']/e['clk']:,.0f}円まで（今は {e['cost']/e['clk']:,.0f}円）")
# ---- 週ごとの流れ（元のキャンペーン）
P('■ ② 元のキャンペーンの週ごと: 広告費/日・個数/日・倍率｜CPM・クリック率・クリック1回・購入÷クリック')
w0 = datetime.date(2026, 9, 9)
for i in range(8):
    ds = days((w0 + datetime.timedelta(7 * i)).isoformat(), (w0 + datetime.timedelta(7 * i + 6)).isoformat()); c = [sum(M[d][j] for d in ds) for j in range(6)]; g = sum(S[d][0] for d in ds); dc = sum(S[d][1] for d in ds); k = sum(cogs(d) for d in ds)
    P(f"  {ds[0][5:]}〜{ds[-1][5:]}: {c[0]/7:,.0f}・{g//3980/7:.1f}個・{(g-dc-k)/c[0]:.2f}｜{c[0]/c[1]*1000:,.0f}・{c[2]/c[1]:.2%}・{c[0]/c[2]:,.0f}円・{c[5]/c[2]:.2%}")
# ---- だれに出ているか
def seg(f):
    t = collections.OrderedDict()
    for r in table(f):
        if r[1] not in ('female', 'male') or r[0] in ('Unknown',): continue
        age = r[0] if r[0] in ('45-54', '55-64', '65+') else '18-44'
        x = t.setdefault((r[1], age), [0, 0, 0, 0])
        for i in range(4): x[i] += z(r[2 + i])
    return t
P('■ ③ だれに出ているか（性別×年代）: 広告費の割合｜CPM・クリック率・クリック1回｜購入÷クリック（件数）')
for lab, f in (('A 9/11〜10/6', 'hook_agegender_0911_1006_raw.json'), ('C+D 10/16〜11/3', 'hook_agegender_1016_1103_raw.json'), ('E v5 11/18〜11/23', 'hook_v5_agegender_1118_1123_raw.json')):
    t = seg(f); tot = sum(v[0] for v in t.values())
    for gname, jp in (('female', '女性'), ('male', '男性')):
        v = [sum(x[i] for (g_, a_), x in t.items() if g_ == gname) for i in range(4)]
        P(f"  {lab} {jp}計: {v[0]/tot:.0%}｜{v[0]/v[1]*1000:,.0f}・{v[2]/v[1]:.2%}・{v[0]/v[2]:,.0f}円｜{v[3]/v[2]:.1%}（{v[3]}件）")
    P('    ' + '・'.join(f"{'女' if g_=='female' else '男'}{a_} {x[0]/tot:.0%}（CPM {x[0]/x[1]*1000:,.0f}・{x[2]/x[1]:.1%}・{x[3]}件）" for (g_, a_), x in sorted(t.items(), key=lambda kv: -kv[1][0])[:6]))
P('■ ④ どこに出ているか（配置）: 広告費の割合・CPM・クリック率')
for lab, f in (('A 9/11〜10/6', 'hook_placement_0911_1006_raw.json'), ('E v5 11/18〜11/23', 'hook_v5_placement_1118_1123_raw.json')):
    rows = [(r[0] + ' ' + r[1], z(r[2]), z(r[3]), z(r[4])) for r in table(f) if z(r[2]) > 500]; tot = sum(r[1] for r in rows)
    P(f'  {lab}: ' + '・'.join(f'{n} {c/tot:.0%}（{c/i*1000:,.0f}・{k/i:.1%}）' for n, c, i, k in sorted(rows, key=lambda r: -r[1])[:6]))
P('■ ⑤ 同じ人に何度も出ているか（Meta の リーチ・1人あたりの表示回数）')
for lab, f in (('A 9/11〜10/6', 'hook_reach_0911_1006_raw.json'), ('C 10/16〜10/26', 'hook_reach_1016_1026_raw.json'), ('D 10/27〜11/3', 'hook_reach_1027_1103_raw.json'), ('元のキャンペーン全部 9/9〜11/3', 'hook_reach_0909_1103_raw.json'), ('E v5 11/18〜11/23', 'hook_v5_reach_1118_1123_raw.json')):
    r = table(f)[0]; P(f'  {lab}: 届いた人 {z(r[1]):,}・1人あたり {float(r[2]):.2f}回・表示 {z(r[3]):,}')
open(D0 + 'hook_1123.txt', 'w').write('\n'.join(out) + '\n')
