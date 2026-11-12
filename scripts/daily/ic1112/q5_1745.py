# -*- coding: utf-8 -*-
"""11/12(木) 17:4x ユーザーの5つの質問（表示単価はなぜ高い／今が最適か／当たり商品／客単価／過去に売れた商品はなぜ売れなくなったか・新しい広告セットにすべきか）に答えるための集計。
入力: q5_1745_raw.json（Meta: キャンペーン×年齢 11/5〜11/11、UV歯ブラシ除菌器・バランスケアスリッパの月別×広告セット）・日次CSV（代表原価の近似）。"""
import os, sys, csv, json, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
RAW = json.load(open(D + 'q5_1745_raw.json')); iv = lambda x: 0 if x in ('null', '') else int(x)
# ---------- ① 年齢ごとの表示単価 ----------
CA = collections.defaultdict(dict)
for r in RAW['camp_age_1105_1111']['rows']:
    c, a, co, im, cl, pu = next(csv.reader([r]))
    if a != 'Unknown': CA[c][a] = [iv(co), iv(im), iv(cl), iv(pu)]
AG = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
tot = {a: [sum(v.get(a, [0, 0, 0, 0])[j] for v in CA.values()) for j in range(4)] for a in AG}
print('■① 年齢ごと（全商品・11/5〜11/11）: CPM／1クリック円／購入÷クリック%／購入1件の広告費')
for a in AG: t = tot[a]; print(f"  {a}: {t[0]/t[1]*1000:,.0f}／{t[0]/t[2]:.0f}／{t[3]/t[2]*100:.2f}／{t[0]/t[3]:,.0f}（広告費の{t[0]/sum(x[0] for x in tot.values())*100:.0f}%）")
print('  商品ごと: 全体のCPM・45歳以上に使った割合・年齢別CPM（25-34／45-54／55-64／65+）')
for c in sorted(CA, key=lambda c: -sum(v[0] for v in CA[c].values())):
    v = CA[c]; s = sum(x[0] for x in v.values()); i = sum(x[1] for x in v.values())
    if s < 60000: continue
    f = lambda a: '—' if a not in v or v[a][1] < 500 else f"{v[a][0]/v[a][1]*1000:,.0f}"
    print(f"    {c}: {s/i*1000:,.0f}・{sum(v.get(a, [0])[0] for a in ('45-54', '55-64', '65+'))/s*100:.0f}%・{f('25-34')}／{f('45-54')}／{f('55-64')}／{f('65+')}")
# 年齢の配分だけで説明できる分: 各商品を「全商品の年齢別CPM」で買った場合
print('  年齢の配分だけで決まるCPM（その商品の年齢別の表示数 × 全商品の年齢別CPM）と実際:')
for c in ['ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '伸縮ガラスクリーナー', 'ワイド水切りワイパー', '伸縮ワックス洗車ブラシ', 'クリアビューレインガードフィルム', 'マグネットドアクッション']:
    v = CA[c]; i = sum(x[1] for x in v.values()); exp = sum(v[a][1] * tot[a][0] / tot[a][1] for a in v) / i * 1000
    print(f"    {c}: 配分から {exp:,.0f}・実際 {sum(x[0] for x in v.values())/i*1000:,.0f}")
# ---------- ② ナノガラス脱毛パッド: 予算の大きさと倍率 ----------
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
series = g['series']; N = [r for r in series('ナノガラス脱毛パッド') if r['ad'] >= 3000]
print('\n■② ナノガラス脱毛パッド: 期間ごとの 広告費/日・倍率・利益/日')
for lab, lo, hi in [('7月', '2026-07-01', '2026-07-31'), ('8月', '2026-08-01', '2026-08-31'), ('9月', '2026-09-01', '2026-09-30'), ('10/1〜10/28', '2026-10-01', '2026-10-28'), ('10/29〜10/31', '2026-10-29', '2026-10-31'), ('11/1〜11/11', '2026-11-01', '2026-11-11')]:
    xs = [r for r in N if lo <= r['date'] <= hi]; a = sum(r['ad'] for r in xs); gpx = sum(r['sales'] - r['cost'] for r in xs)
    print(f"  {lab}: {a/len(xs):,.0f}・{gpx/a:.2f}・{(gpx-a)/len(xs):+,.0f}（{len(xs)}日・1.25未満の日 {sum((r['sales']-r['cost'])/r['ad'] < 1.25 for r in xs)}）")
b1 = [r for r in N if '2026-10-01' <= r['date'] <= '2026-10-28']; b2 = [r for r in N if '2026-11-01' <= r['date'] <= '2026-11-11']
g1 = sum(r['sales'] - r['cost'] for r in b1) / len(b1); a1 = sum(r['ad'] for r in b1) / len(b1); g2 = sum(r['sales'] - r['cost'] for r in b2) / len(b2); a2 = sum(r['ad'] for r in b2) / len(b2)
print(f"  10/1〜10/28 と 11/1〜11/11 の差: 広告費/日 {a1-a2:+,.0f} に対して粗利/日 {g1-g2:+,.0f} ＝ 足していた分の倍率 {(g1-g2)/(a1-a2):.2f}【別の時期どうしの比較】")
print('  広告費の大きさ別（6/29〜11/11・日ごと）: ' + ' ｜ '.join(f"{lo//1000}〜{hi//1000}千円 {len(xs)}日・倍率 {sum(r['sales']-r['cost'] for r in xs)/sum(r['ad'] for r in xs):.2f}・利益/日 {sum(r['sales']-r['cost']-r['ad'] for r in xs)/len(xs):+,.0f}" for lo, hi in [(10000, 30000), (30000, 50000), (50000, 70000), (70000, 90000), (90000, 130000)] for xs in [[r for r in N if lo <= r['ad'] < hi]] if xs))
# ---------- ⑤ UV歯ブラシ除菌器・バランスケアスリッパの月別 ----------
MU = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * 5)); SETS = collections.defaultdict(lambda: collections.defaultdict(list))
for r in RAW['uv_slipper_month']['rows']:
    ym, c, s, co, im, re, fq, cl, lp, pu = next(csv.reader([r])); m = ym.split('|')[1]
    for j, v in enumerate((co, im, cl, lp, pu)): MU[c][m][j] += iv(v)
    SETS[c][m].append((s, iv(co), iv(im), iv(cl), iv(pu), float(fq)))
for c in ['UV歯ブラシ除菌器', 'バランスケアスリッパ']:
    print(f"\n■⑤ {c}: 月ごとの 広告費／CPM／CTR%／1クリック円／購入÷クリック%／購入1件の広告費（Metaの数え方）")
    for m in sorted(MU[c]):
        v = MU[c][m]; print(f"  {int(m)}月: {v[0]:,}／{v[0]/v[1]*1000:,.0f}／{v[2]/v[1]*100:.2f}／{v[0]/v[2]:.0f}／{v[4]/v[2]*100:.2f}／{v[0]/v[4]:,.0f}  ｜ " + '・'.join(f"{s} {co:,}円（1件 {co/max(pu,1):,.0f}・同じ人に{fq:.2f}回）" for s, co, im, cl, pu, fq in SETS[c][m]))
