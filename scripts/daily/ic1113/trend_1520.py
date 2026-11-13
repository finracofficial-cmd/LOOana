# -*- coding: utf-8 -*-
"""11/13(金) 15:2x 「ちょっと前と比較してパフォーマンス悪化してるから不安」「metaの広告設定は調整する必要あるの？」
①店全体の週別（10/2〜11/12 を金〜木の7日×6）: 売上・広告費・利益/日・倍率（data/daily・代表原価）
②広告の効率の週別（Meta アカウント終日・meta_acct_daily_1002_1112.txt）と店の購入率（Shopify 来訪→購入・sess_daily_1002_1112.json）
③利益の減り方を商品別に分ける: 10/16〜10/29（2週）→ 11/6〜11/12（1週）の利益/日"""
import os, sys, csv, json, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series = g['S'], g['series']
SER = {n: {r['date']: r for r in series(n)} for n in S}
SALE = collections.defaultdict(int); AD = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): SALE[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): AD[x['date']] += float(x['cost'])
COGS = collections.defaultdict(float)
for n in S:
    for d, r in SER[n].items(): COGS[d] += r['cost'] or 0
d0 = datetime.date(2026, 10, 2); DAYS = [(d0 + datetime.timedelta(i)).isoformat() for i in range(42)]
for d in DAYS: assert abs(sum(SER[n][d]['sales'] for n in S if d in SER[n]) - SALE[d]) <= 0, d   # 商品の合計 = 店全体（CSV）
MA = {}
for l in open(D + 'meta_acct_daily_1002_1112.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]   # cost, imp, reach, link_clicks, lpv, atc, purchase
for d in DAYS: assert abs(MA[d][0] - AD[d]) <= max(300, AD[d] * 0.003), (d, MA[d][0], AD[d])   # Meta終日 ≒ CSV（11/12はCSVが暫定値）
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'sess_daily_1002_1112.json'))['rows']}
W = [DAYS[i:i + 7] for i in range(0, 42, 7)]
print('■ 店全体の週別（金〜木）: 売上/日・広告費/日・利益/日・倍率・売上÷広告費')
for w in W:
    s = sum(SALE[d] for d in w); c = sum(COGS[d] for d in w); a = sum(AD[d] for d in w)
    print(f"  {w[0][5:]}〜{w[-1][5:]}: 売上 {s/7:,.0f}・広告費 {a/7:,.0f}・利益 {(s-c-a)/7:+,.0f}・倍率 {(s-c)/a:.2f}・売上÷広告費 {s/a:.2f}")
print('\n■ 広告の効率の週別（Meta アカウント・終日）／店の購入率（Shopify）')
for w in W:
    m = [sum(MA[d][j] for d in w) for j in range(7)]; e = [sum(SE[d][j] for d in w) for j in range(4)]
    fq = sum(MA[d][1] / MA[d][2] for d in w) / 7
    print(f"  {w[0][5:]}〜{w[-1][5:]}: CPM {m[0]/m[1]*1000:,.0f}・クリック率 {m[3]/m[1]*100:.2f}%・1クリック {m[0]/m[3]:.0f}円・Meta購入÷クリック {m[6]/m[3]*100:.2f}%・Meta購入1件 {m[0]/m[6]:,.0f}円・1日の頻度 {fq:.2f}｜来訪 {e[0]/7:,.0f}/日・購入率 {e[3]/e[0]*100:.2f}%・カート投入 {e[1]/e[0]*100:.2f}%")
print('\n■ 利益/日の変化を商品別に: 10/16〜10/29（14日）→ 11/6〜11/12（7日）')
def agg(n, a, b):
    rs = [r for d, r in SER[n].items() if a <= d <= b]
    return sum(r['ad'] for r in rs), sum(r['sales'] - (r['cost'] or 0) for r in rs)
P1, P2 = ('2026-10-16', '2026-10-29'), ('2026-11-06', '2026-11-12')
rows = []
for n in S:
    a1, g1 = agg(n, *P1); a2, g2 = agg(n, *P2)
    if a1 + a2 == 0 and g1 + g2 == 0: continue
    rows.append((n, a1 / 14, (g1 - a1) / 14, a2 / 7, (g2 - a2) / 7, g1 / a1 if a1 else None, g2 / a2 if a2 else None))
cat = lambda a, b: sum(AD[d] for d in DAYS if a <= d <= b) - sum(agg(n, a, b)[0] for n in S)
t1 = sum(r[2] for r in rows) - cat(*P1) / 14; t2 = sum(r[4] for r in rows) - cat(*P2) / 7
p1 = sum(SALE[d] - COGS[d] - AD[d] for d in DAYS if P1[0] <= d <= P1[1]) / 14; p2 = sum(SALE[d] - COGS[d] - AD[d] for d in DAYS if P2[0] <= d <= P2[1]) / 7
assert abs(t1 - p1) < 1 and abs(t2 - p2) < 1, (t1, p1, t2, p2)   # 商品別の合計 − カタログ = 店全体
f = lambda v: '—' if v is None else f'{v:.2f}'
big = sorted([r for r in rows if abs(r[4] - r[2]) >= 3000], key=lambda r: r[4] - r[2])
for r in big: print(f"  {r[0][:20]}: 利益 {r[2]:+,.0f} → {r[4]:+,.0f}（{r[4]-r[2]:+,.0f}）｜広告費 {r[1]:,.0f} → {r[3]:,.0f}・倍率 {f(r[5])} → {f(r[6])}")
rest = [r for r in rows if abs(r[4] - r[2]) < 3000]
print(f"  その他 {len(rest)}商品: {sum(r[4]-r[2] for r in rest):+,.0f}／カタログ広告費: {-cat(*P2)/7+cat(*P1)/14:+,.0f}")
print(f"  店全体: 利益/日 {p1:+,.0f} → {p2:+,.0f}（{p2-p1:+,.0f}）")
# 広告を出し続けている商品だけ（両期間とも広告費あり）で、同じ商品の効率を比べる
both = [r for r in rows if r[1] >= 3000 and r[3] >= 3000]
a1 = sum(r[1] for r in both); a2 = sum(r[3] for r in both); g1 = sum(r[2] + r[1] for r in both); g2 = sum(r[4] + r[3] for r in both)
print(f"\n■ 両方の期間で広告を出していた{len(both)}商品だけ: 広告費/日 {a1:,.0f} → {a2:,.0f}・倍率 {g1/a1:.2f} → {g2/a2:.2f}・利益/日 {g1-a1:+,.0f} → {g2-a2:+,.0f}")
for r in sorted(both, key=lambda r: -r[3]): print(f"    {r[0][:20]}: 倍率 {f(r[5])} → {f(r[6])}・広告費 {r[1]:,.0f} → {r[3]:,.0f}")
