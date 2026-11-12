# -*- coding: utf-8 -*-
"""11/12(木) 17:5x 「CVRの低下は男性向けになってるからかな」
入力: cvr_gender_1750_raw.json（Shopify 来訪→購入の月別・週別／Meta 月×性別、月×キャンペーン×性別、月×性別のカート・決済・購入）。期間 7/1〜11/11（11月は11日分）。
見ること: ①店の購入率は下がっているか ②男性の購入率は女性より低いか ③性別の割合が動いた分で購入率はどれだけ動いたか ④同じ商品の中で男女を比べる"""
import os, csv, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; iv = lambda x: 0 if x in ('null', '', None) else int(x)
RAW = json.load(open(D + 'cvr_gender_1750_raw.json'))
MO = ['07', '08', '09', '10', '11']

print('■ 店全体（Shopify・来訪→購入）')
for r in RAW['shop_month']['rows']:
    s, c, k, p = map(int, r[1:5])
    print(f"  {int(r[0][5:7])}月: 来訪 {s:,}・購入率 {p/s*100:.2f}%｜カートに入れた {c/s*100:.2f}%・決済画面に来た人のうち購入 {p/k*100:.1f}%")
print('  週別（月曜始まり・最後の週は11/9〜11/11）: ' + ' → '.join(f"{r[0][5:]} {int(r[4])/int(r[1])*100:.2f}%" for r in RAW['shop_week']['rows']))

G = collections.defaultdict(dict)   # 月 → 性別 → [広告費, 表示, クリック, 購入]
for r in RAW['month_gender']['rows']:
    ym, s, co, im, cl, pu = next(csv.reader([r])); G[ym.split('|')[1]][s] = [iv(co), iv(im), iv(cl), iv(pu)]
F = collections.defaultdict(dict)   # 月 → 性別 → [クリック, カート, 決済開始, 購入, 購入金額]
for r in RAW['month_gender_funnel']['rows']:
    ym, s, cl, atc, ic, pu, val = next(csv.reader([r])); F[ym.split('|')[1]][s] = [iv(cl), iv(atc), iv(ic), iv(pu), iv(val)]
for m in MO:
    for s in G[m]: assert G[m][s][2] == F[m][s][0] and G[m][s][3] == F[m][s][3], (m, s)

print('\n■ Meta（クリック→購入）月別。女性の割合はクリックの割合')
rate = lambda v: v[3] / v[2] * 100
for m in MO:
    f, ma = G[m]['female'], G[m]['male']; t = [sum(G[m][s][j] for s in G[m]) for j in range(4)]
    print(f"  {int(m)}月: 全体 {rate(t):.2f}%（{t[3]:,}件÷{t[2]:,}）｜女性 {rate(f):.2f}%・男性 {rate(ma):.2f}%｜女性の割合 クリック {f[2]/(f[2]+ma[2])*100:.0f}%・広告費 {f[0]/(f[0]+ma[0])*100:.0f}%")
print('  カートに入れた÷クリック（女性／男性）: ' + ' → '.join(f"{int(m)}月 {F[m]['female'][1]/F[m]['female'][0]*100:.1f}／{F[m]['male'][1]/F[m]['male'][0]*100:.1f}%" for m in MO))
print('  購入÷カートに入れた（女性／男性）: ' + ' → '.join(f"{int(m)}月 {F[m]['female'][3]/F[m]['female'][1]*100:.0f}／{F[m]['male'][3]/F[m]['male'][1]*100:.0f}%" for m in MO))
print('  購入1件の金額（Meta計上・女性／男性）: ' + ' → '.join(f"{int(m)}月 {F[m]['female'][4]/F[m]['female'][3]:,.0f}／{F[m]['male'][4]/F[m]['male'][3]:,.0f}円" for m in MO))
print('  購入1件の広告費（女性／男性）: ' + ' → '.join(f"{int(m)}月 {G[m]['female'][0]/G[m]['female'][3]:,.0f}／{G[m]['male'][0]/G[m]['male'][3]:,.0f}円" for m in MO))

print('\n■ 性別の割合が動いた分と、それぞれの性別の中で動いた分（Meta クリック→購入・女性と男性だけ）')
def decomp(a, b):
    sa = {s: G[a][s][2] for s in ('female', 'male')}; sb = {s: G[b][s][2] for s in ('female', 'male')}
    ta, tb = sum(sa.values()), sum(sb.values()); mix = within = 0
    for s in ('female', 'male'):
        wa, wb = sa[s] / ta, sb[s] / tb; ra, rb = rate(G[a][s]), rate(G[b][s])
        mix += (wb - wa) * (ra + rb) / 2; within += (wa + wb) / 2 * (rb - ra)
    ra = sum(G[a][s][3] for s in sa) / ta * 100; rb = sum(G[b][s][3] for s in sb) / tb * 100
    assert abs((rb - ra) - (mix + within)) < 1e-9
    print(f"  {int(a)}月 → {int(b)}月: {ra:.2f}% → {rb:.2f}%（{rb-ra:+.2f}pt）＝ 性別の割合が動いた分 {mix:+.3f}pt ＋ 性別の中で動いた分 {within:+.3f}pt")
for a, b in (('07', '08'), ('08', '11'), ('07', '11')): decomp(a, b)

C = collections.defaultdict(lambda: collections.defaultdict(lambda: {'female': [0, 0, 0, 0], 'male': [0, 0, 0, 0]}))
chk = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in RAW['month_camp_gender']['rows']:
    ym, c, s, co, im, cl, pu = next(csv.reader([r])); m = ym.split('|')[1]
    for j, v in enumerate((co, im, cl, pu)): chk[(m, s)][j] += iv(v)
    if s in ('female', 'male'):
        for j, v in enumerate((co, im, cl, pu)): C[c][m][s][j] += iv(v)
# クリック・購入は月×性別の取得と完全一致。広告費は行ごとの四捨五入と、表示だけの小さな行の欠けで最大44円（9月・男性）ずれる
for (m, s), v in chk.items(): assert v[2] == G[m][s][2] and v[3] == G[m][s][3] and abs(v[0] - G[m][s][0]) <= 100, (m, s, v, G[m][s])

print('\n■ 同じ商品の中で男女を比べる（7/1〜11/11の合計・男女それぞれクリック500回以上かつ購入15件以上の商品）')
rows = []
for c, ms in C.items():
    f = [sum(ms[m]['female'][j] for m in ms) for j in range(4)]; ma = [sum(ms[m]['male'][j] for m in ms) for j in range(4)]
    if min(f[2], ma[2]) >= 500 and min(f[3], ma[3]) >= 15: rows.append((c, f, ma))
rows.sort(key=lambda x: -(x[1][0] + x[2][0]))
lo = sum(rate(ma) < rate(f) for c, f, ma in rows)
for c, f, ma in rows:
    print(f"  {c[:20]}: 女性 {rate(f):.2f}%（{f[3]}件÷{f[2]:,}）・男性 {rate(ma):.2f}%（{ma[3]}件÷{ma[2]:,}）｜購入1件の広告費 {f[0]/f[3]:,.0f}／{ma[0]/ma[3]:,.0f}円")
print(f"  → {len(rows)}商品のうち、男性の購入率が女性より低い {lo}商品・高い {len(rows)-lo}商品")
# 商品の構成をそろえて男女を比べる（各商品のクリック数の男女合計を重みに）
w = sum(f[2] + ma[2] for c, f, ma in rows)
print(f"  商品の構成をそろえた購入率: 女性 {sum((f[2]+ma[2])*rate(f) for c,f,ma in rows)/w:.2f}%・男性 {sum((f[2]+ma[2])*rate(ma) for c,f,ma in rows)/w:.2f}%")

print('\n■ 今の主力（11/1〜11/11・広告費5万円以上）: 女性の割合と購入率（全体・女性・男性）')
now = []
for c, ms in C.items():
    if '11' in ms:
        f, ma = ms['11']['female'], ms['11']['male']
        if f[0] + ma[0] >= 50000: now.append((c, f, ma))
for c, f, ma in sorted(now, key=lambda x: -(x[1][0] + x[2][0])):
    r = lambda v: f"{v[3]/v[2]*100:.1f}%（{v[3]}件）" if v[2] >= 100 else '—'
    print(f"  {c[:20]}: 広告費 {(f[0]+ma[0])/10000:.1f}万・女性 {f[0]/(f[0]+ma[0])*100:.0f}%｜全体 {(f[3]+ma[3])/(f[2]+ma[2])*100:.1f}%・女性 {r(f)}・男性 {r(ma)}")

print('\n■ 直近（multi_1630_raw.json・年齢×性別を性別に合計）: 女性の割合（クリック）と購入÷クリック（女性／男性）')
R2 = json.load(open(D + 'multi_1630_raw.json'))
for key, lab in (('age_gender_1105_1109', '11/5〜11/9'), ('age_gender_1110_1111', '11/10〜11/11')):
    t = {'female': [0, 0, 0, 0], 'male': [0, 0, 0, 0]}
    for r in R2[key]['rows']:
        a, s, co, im, cl, pu, pv = r.split(',')
        if s in t:
            for j, v in enumerate((co, im, cl, pu)): t[s][j] += iv(v)
    f, ma = t['female'], t['male']
    print(f"  {lab}: 女性の割合 {f[2]/(f[2]+ma[2])*100:.0f}%｜全体 {(f[3]+ma[3])/(f[2]+ma[2])*100:.2f}%・女性 {rate(f):.2f}%（{f[3]}件）・男性 {rate(ma):.2f}%（{ma[3]}件）")
