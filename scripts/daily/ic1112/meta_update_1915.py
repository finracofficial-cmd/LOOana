# -*- coding: utf-8 -*-
"""11/12(木) 19:1x 「Metaのアップデートでおかしくなってる説。世の中を調べて」に対する、こちらのデータでの確認
①Meta計上の購入 ÷ Shopifyの注文（0〜17時台・11/5〜11/12）: 11/12からPixelの数え方が変わったなら今日だけずれるはず（meta_hour_1830.txt・store_0017.txt）
②新商品の寿命: 8/1以降に広告を始めた商品（通算の広告費5万円以上）を出した月で分け、開始から1〜7日・8〜14日・15〜28日の倍率と、
  初めて「2日続けて1.25未満」になった日（開始からの日数）を並べる。日次CSV（代表原価の近似）。"""
import os, sys, csv, collections, datetime, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'; iv = lambda x: 0 if x in ('null', '') else int(x)
# ①
MP = collections.defaultdict(int)
for l in open(D + 'meta_hour_1830.txt'):
    if l[0] == '#' or not l.strip(): continue
    r = next(csv.reader([l.strip()])); MP[r[0]] += iv(r[-1])
SO = {}
for l in open(D + 'store_0017.txt'):
    if l[0] != '#' and l.strip(): r = l.strip().split(','); SO[r[0]] = (int(r[3]), int(r[7]))
print('■① Meta計上の購入 ÷ Shopify（0〜17時台）: 日付 Meta購入／Shopify注文／Shopify購入完了の来訪 → 比')
for d in sorted(MP): print(f"  {d[5:]}: {MP[d]}／{SO[d][0]}／{SO[d][1]} → {MP[d]/SO[d][0]:.2f}")
r7 = [MP[d] / SO[d][0] for d in sorted(MP) if d < '2026-11-12']
print(f"  11/5〜11/11 の比 {min(r7):.2f}〜{max(r7):.2f}（中央値 {st.median(r7):.2f}）・今日 {MP['2026-11-12']/SO['2026-11-12'][0]:.2f}")
# ②
src = open(R + 'scripts/product_tabs.py').read()
g = dict(csv=csv, sys=sys, collections=collections, datetime=datetime, SALES=R + 'data/daily/daily_sales.csv', AD=R + 'data/daily/daily_ad.csv', SNAP=R + 'data/budget-snapshots.csv', INTO=None)
exec(src[src.index('COST = {'):src.index('# ---- スタイル ----')], g); exec(src[src.index('def _mixed_qty'):src.index('def block(')], g)
S, series = g['S'], g['series']; LAST = '2026-11-11'
print('\n■② 8/1以降に広告を始めた商品（通算の広告費5万円以上）: 開始日・1〜7日／8〜14日／15〜28日の倍率（広告費）・初めて2日続けて1.25未満になった日')
rows = []
for n in S:
    rs = [r for r in series(n) if r['date'] <= LAST]; ad = [r for r in rs if r['ad'] >= 1000]
    if not ad or ad[0]['date'] < '2026-08-01' or sum(r['ad'] for r in rs) < 50000: continue
    start = datetime.date.fromisoformat(ad[0]['date']); byday = {r['date']: r for r in rs}
    def win(a, b):
        x = [byday.get((start + datetime.timedelta(i)).isoformat()) for i in range(a - 1, b)]; x = [r for r in x if r and r['ad'] > 0]
        if not x or (start + datetime.timedelta(b - 1)).isoformat() > LAST: return None
        A_ = sum(r['ad'] for r in x); return (sum(r['sales'] - (r['cost'] or 0) for r in x) / A_, A_)
    m = [(i + 1, byday.get((start + datetime.timedelta(i)).isoformat())) for i in range((datetime.date.fromisoformat(LAST) - start).days + 1)]
    m = [(k, (r['sales'] - (r['cost'] or 0)) / r['ad']) for k, r in m if r and r['ad'] >= 1000]
    fail = next((m[i][0] for i in range(1, len(m)) if m[i][1] < 1.25 and m[i - 1][1] < 1.25 and m[i][0] == m[i - 1][0] + 1), None)
    rows.append((n, start.isoformat(), win(1, 7), win(8, 14), win(15, 28), fail, len(m)))
f = lambda w: '—' if w is None else f"{w[0]:.2f}（{w[1]/1000:,.0f}千）"
for n, s, a, b, c, fl, k in sorted(rows, key=lambda x: x[1]):
    print(f"  {s[5:]} {n[:16]}: {f(a)}／{f(b)}／{f(c)}｜2日続けて1.25未満: {'なし' if fl is None else f'{fl}日目'}（広告を出した日数 {k}）")
print('\n  開始した月ごと（1〜7日が1.5以上だった商品＝当たりだけ）: 8〜14日の倍率の中央値・初めて2日続けて1.25未満になった日の中央値')
for mo in ('08', '09', '10', '11'):
    h = [x for x in rows if x[1][5:7] == mo and x[2] and x[2][0] >= 1.5]
    b = [x[3][0] for x in h if x[3]]; fl = [x[5] for x in h if x[5]]
    print(f"  {int(mo)}月: 当たり {len(h)}本（{'・'.join(x[0][:10] for x in h)}）｜8〜14日 {('%.2f' % st.median(b)) if b else '—'}（{len(b)}本）｜2日続けて1.25未満になった日 {fl}")

# ③ Meta側（0〜17時台・キャンペーン別）: クリック率・1クリックの広告費・購入÷クリック を、以前からの5本と新しい4本で日別に
print('\n■③ Meta（0〜17時台）: クリック率／1クリックの広告費／購入÷クリック（meta_camp_0017.txt）')
GR = {'以前からの5本': ['伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '4-in-1マルチクリーナー', '快適マジックインソール'],
      '新しい4本': ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション']}
C = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'meta_camp_0017.txt'):
    if l[0] == '#' or not l.strip(): continue
    d, n, *v = next(csv.reader([l.strip()]))
    for k, ns in GR.items():
        if n in ns:
            for j, x in enumerate(v): C[(k, d)][j] += iv(x)
for k in GR:
    ds = sorted({d for (kk, d) in C if kk == k})
    print(f"  {k}: " + ' ｜ '.join(f"{d[5:]} {C[(k,d)][2]/C[(k,d)][1]*100:.2f}%・{C[(k,d)][0]/C[(k,d)][2]:.0f}円・{C[(k,d)][5]/C[(k,d)][2]*100:.1f}%" for d in ds))
