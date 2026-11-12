# -*- coding: utf-8 -*-
"""11/12(木) 18:0x 「ではなんでこんな状況になってる。その上で今後何をするべき？」
日次CSV（data/daily）だけを使う。倍率＝（売上−原価）÷広告費（代表原価の近似）。
①10/13〜10/26 と 11/5〜11/11 を商品別に並べる（広告費/日・倍率・利益/日）②9/1以降に出した商品が利益のどれだけを占めるか ③今の広告セットの直近7日"""
import os, sys, csv, collections, datetime
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series = g['S'], g['series']
SER = {n: {r['date']: r for r in series(n)} for n in S}
def agg(n, a, b):
    rs = [r for d, r in SER[n].items() if a <= d <= b]
    return sum(r['ad'] for r in rs), sum(r['sales'] - (r['cost'] or 0) for r in rs)
days = lambda a, b: (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days + 1
P1, P2 = ('2026-10-13', '2026-10-26'), ('2026-11-05', '2026-11-11')
print(f"■ 商品別: {P1[0][5:]}〜{P1[1][5:]}（14日）→ {P2[0][5:]}〜{P2[1][5:]}（7日）　広告費/日・倍率・利益/日")
rows = []
for n in S:
    a1, g1 = agg(n, *P1); a2, g2 = agg(n, *P2)
    if a1 + a2 < 30000: continue
    rows.append((n, a1 / 14, g1 / a1 if a1 else 0, (g1 - a1) / 14, a2 / 7, g2 / a2 if a2 else 0, (g2 - a2) / 7))
T = [sum(r[i] for r in rows) for i in (1, 3, 4, 6)]
for r in sorted(rows, key=lambda r: r[6] - r[3]):
    print(f"  {r[0][:18]}: 広告費 {r[1]:,.0f} → {r[4]:,.0f}・倍率 {r[2]:.2f} → {r[5]:.2f}・利益 {r[3]:+,.0f} → {r[6]:+,.0f}（{r[6]-r[3]:+,.0f}）")
print(f"  合計（広告費3万円以上の商品）: 広告費/日 {T[0]:,.0f} → {T[2]:,.0f}・利益/日 {T[1]:+,.0f} → {T[3]:+,.0f}")

first = {}
for n in S:
    ds = sorted(d for d, r in SER[n].items() if r['ad'] >= 1000)
    if ds: first[n] = ds[0]
print('\n■ 9/1〜11/11 の利益（広告を出した商品・カタログの広告費は含めない）を、出した時期で分ける')
A, B = '2026-09-01', '2026-11-11'; grp = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for n, f in first.items():
    a, gp = agg(n, A, B)
    if a <= 0: continue
    k = '9/1以降に出した商品' if f >= A else '8月までに出した商品'
    grp[k][0] += 1; grp[k][1] += a; grp[k][2] += gp - a; grp[k][3] += (gp - a) >= 100000; grp[k][4] += (gp - a) < 0
for k, v in grp.items(): print(f"  {k}: {v[0]}本・広告費 {v[1]:,.0f}・利益 {v[2]:+,.0f}（倍率 {(v[2]+v[1])/v[1]:.2f}）・利益10万円以上 {v[3]}本・赤字 {v[4]}本")
new = sorted(((n, f) for n, f in first.items() if f >= A), key=lambda x: x[1])
bym = collections.defaultdict(lambda: [0, 0])
for n, f in new:
    a, gp = agg(n, A, B); bym[f[5:7]][0] += 1; bym[f[5:7]][1] += (gp - a) >= 100000
print('  出した本数（うち利益10万円以上）: ' + '・'.join(f"{int(m)}月 {v[0]}本（{v[1]}本）" for m, v in sorted(bym.items())))
big = [(n, f, *agg(n, A, B)) for n, f in new]; big = [(n, f, a, gp) for n, f, a, gp in big if gp - a >= 100000]
for n, f, a, gp in sorted(big, key=lambda x: -(x[3] - x[2])):
    dd = sorted(d for d, r in SER[n].items() if r['ad'] >= 1000 and d <= B)
    print(f"    {n[:18]}（{f[5:]}〜・広告を出した日数 {len(dd)}日）: 広告費 {a:,.0f}（1日 {a/len(dd):,.0f}）・利益 {gp-a:+,.0f}・倍率 {gp/a:.2f}")

print('\n■ 今の広告セットの商品: 直近7日（11/5〜11/11）と直近2日')
CAMP = g['CAMP']; snap = list(csv.reader(open(R + 'data/budget-snapshots.csv'))); last = snap[-1][0]; bud = collections.defaultdict(int)
for r in snap:
    if r[0] == last: bud[r[1]] += int(float(r[3]))
print(f"  （予算は {last} の記録・合計 {sum(bud.values()):,}円）")
for n in sorted(S, key=lambda n: -bud.get(CAMP.get(n, n), 0)):
    b = bud.get(CAMP.get(n, n), 0)
    if not b: continue
    a7, g7 = agg(n, '2026-11-05', '2026-11-11'); d = [SER[n].get(x) for x in ('2026-11-10', '2026-11-11')]
    m = lambda r: f"{(r['sales']-(r['cost'] or 0))/r['ad']:.2f}" if r and r['ad'] > 0 else '—'
    print(f"  {n[:18]}: 日予算 {b:,}・7日 広告費 {a7:,.0f}（1日 {a7/7:,.0f}）・倍率 {g7/a7 if a7 else 0:.2f}・利益 {g7-a7:+,.0f}｜11/10 {m(d[0])}・11/11 {m(d[1])}")

print('\n■ 日ごと（10/27〜11/11）: 広告を出した商品の利益を3つに分ける　新しい4本＝ワイド水切りワイパー・クリアビューレインガードフィルム・伸縮ワックス洗車ブラシ・マグネットドアクッション')
NEW4 = ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション']; NANO = 'ナノガラス脱毛パッド'
for n in NEW4 + [NANO]: assert n in S, n
d0 = datetime.date(2026, 10, 27)
for i in range(16):
    d = (d0 + datetime.timedelta(i)).isoformat(); t = collections.defaultdict(lambda: [0, 0])
    for n in S:
        r = SER[n].get(d)
        if not r or r['ad'] <= 0: continue
        k = '新4' if n in NEW4 else 'ナノ' if n == NANO else '他'
        t[k][0] += r['ad']; t[k][1] += r['sales'] - (r['cost'] or 0) - r['ad']
    tot = [sum(v[j] for v in t.values()) for j in (0, 1)]
    print(f"  {d[5:]}: 広告費 {tot[0]:>8,.0f}・利益 {tot[1]:>+9,.0f}｜新しい4本 {t['新4'][0]:>7,.0f}／{t['新4'][1]:>+8,.0f}・ナノ {t['ナノ'][0]:>7,.0f}／{t['ナノ'][1]:>+8,.0f}・その他 {t['他'][0]:>7,.0f}／{t['他'][1]:>+8,.0f}")

print('\n■ 土台（新しい4本を除いた、広告を出した商品の利益/日）と、新しい4本')
for lab, (a, b) in (('10/13〜10/26', P1), ('10/27〜11/2', ('2026-10-27', '2026-11-02')), ('11/3〜11/9', ('2026-11-03', '2026-11-09')), ('11/5〜11/11', P2), ('11/10〜11/11', ('2026-11-10', '2026-11-11'))):
    n = days(a, b); base = [0, 0]; new4 = [0, 0]; nano = [0, 0]
    for p in S:
        ad, gp = agg(p, a, b)
        if ad <= 0: continue
        t = new4 if p in NEW4 else base; t[0] += ad; t[1] += gp - ad
        if p == NANO: nano = [ad, gp - ad]
    print(f"  {lab}: 土台 広告費 {base[0]/n:,.0f}・利益 {base[1]/n:+,.0f}（うちナノ {nano[0]/n:,.0f}・{nano[1]/n:+,.0f}）｜新しい4本 広告費 {new4[0]/n:,.0f}・利益 {new4[1]/n:+,.0f}｜合計 {(base[1]+new4[1])/n:+,.0f}")
tot = newp = 0
for p in S:
    ad, gp = agg(p, *P2)
    if ad <= 0: continue
    tot += gp - ad
    if first.get(p, '0') >= A: newp += gp - ad
print(f"\n■ 11/5〜11/11 の利益（広告を出した商品）のうち、9/1以降に出した商品の分: {newp:,.0f} ÷ {tot:,.0f} ＝ {newp/tot*100:.0f}%")
print('  【試算】ナノガラス脱毛パッドを 16,000円から +20% ずつ: ' + ' → '.join(f"{16000*1.2**k:,.0f}" for k in range(10)) + '（9回で8万円台。2日あけて3日ごとなら約27日）')
