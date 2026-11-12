# -*- coding: utf-8 -*-
"""11/13 朝の「今日動かすもの」: CLAUDE.md の基準（2026-11-12）を 11/12 終日の数字に当てはめる。入力は日次CSV（w1112.py の積み直し）と budget-snapshots.csv。
基準: ①終日だけ ②2日続けて1.25未満→−20% ③上げ: A 出して10日以内＝前日1.86以上・通算1.86以上・消化95%以上→+4,000まで（毎日可）／B それ以外＝7日1.5以上・消化95%以上→+20%（直近2日が続けて1.25未満なら上げない）
④同じ商品は2日あける（Aの増額は例外）⑤新商品 2日目 クリック率 4.5%超で延長／2.5%未満かつカート0で停止 → 7日1.25以上で継続 ⑥購入0のまま（売価−原価）×3 で停止"""
import io, contextlib, csv, collections, datetime
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1112.py').read(), g)
WIN, agg, A, ACCT, ALLD = g['WIN'], g['agg'], g['A'], g['ACCT'], g['ALLD']
T = '2026-11-12'
def W(days):
    key = 'm' + '_'.join(days); WIN[key] = days; N, DC, Q, K = agg(days, key); return N, Q, K
cache = {}
def mult(n, days):
    k = (n, tuple(days))
    if k not in cache:
        N, Q, K = W(days); a = A(days, n); cache[k] = (None if not a else (N.get(n, 0) - K.get(n, 0)) / a, a, N.get(n, 0) - K.get(n, 0) - a, Q.get(n, 0))
    return cache[k]
# 予算の記録: 日付ラベルごとの最後のスナップショット → 商品（キャンペーン）ごとの合計と、最後に変わった日
rows = [r for r in csv.reader(open('data/budget-snapshots.csv')) if r and r[0] != 'snapshot_date']
labels = []
for r in rows:
    if r[0] not in labels: labels.append(r[0])
snap = collections.OrderedDict((l, collections.defaultdict(int)) for l in labels)
for r in rows: snap[r[0]][r[1]] += int(float(r[3]))
cur = snap[labels[-1]]; assert labels[-1] == '2026-11-12m' and sum(cur.values()) == 145000, (labels[-1], sum(cur.values()))
def last_change(c):
    prev = None; out = None
    for l, v in snap.items():
        if prev is not None and v.get(c, 0) != prev: out = l[:10]
        prev = v.get(c, 0)
    return out
def budget_on(c, d):   # その日の終わりの予算（その日のラベルの最後のスナップショット）
    ls = [l for l in labels if l[:10] <= d]; return snap[ls[-1]].get(c, 0)
INV = {v: k for k, v in g['MAP'].items()}
LAUNCH = {}
for c in cur:
    n = INV.get(c, c); ds = [d for d in ALLD if A([d], n) >= 1000]; LAUNCH[c] = ds[0] if ds else None
print('■ 稼働中の広告セット（2026-11-12m・12セット・145,000円）を基準に当てはめる')
D7 = ALLD[-7:]
for c in sorted(cur, key=lambda c: -cur[c]):
    n = INV.get(c, c); b = cur[c]; lc = last_change(c)
    if c == 'カタログ全部（テスト）':
        print(f"  {c}: 日予算 {b:,}・最後に動かした日 {lc}・商品に分けられないので倍率なし"); continue
    m12, a12, p12, q12 = mult(n, ['2026-11-12']); m11, *_ = mult(n, ['2026-11-11']); m7, a7, p7, _ = mult(n, D7)
    day_no = (datetime.date(2026, 11, 13) - datetime.date.fromisoformat(LAUNCH[c])).days + 1
    since = [d for d in ALLD if d >= LAUNCH[c]]; mc = mult(n, since)[0] if day_no <= 15 else None   # 通算は出して10日以内の判定（3-A）にだけ使う
    # 消化: 予算が同じだった直近の日（最大3日）
    same = [d for d in ALLD[-3:] if budget_on(c, d) == b and all(budget_on(c, x) == b for x in ALLD[-3:] if x >= d)]
    cons = [A([d], n) / b for d in same]
    gap = (datetime.date(2026, 11, 13) - datetime.date.fromisoformat(lc)).days if lc else 99
    f = lambda v: '—' if v is None else f'{v:.2f}'
    print(f"  {c}: 日予算 {b:,}｜11/11 {f(m11)}・11/12 {f(m12)}（{q12}個・広告 {a12:,.0f}・{p12:+,.0f}）｜7日 {f(m7)}（{p7:+,.0f}）｜出してから {day_no}日目・通算 {f(mc)}｜"
          f"最後に動かした日 {lc}（{gap}日前）｜同じ予算の日の消化 " + '・'.join(f"{d[5:]} {x*100:.0f}%" for d, x in zip(same, cons)))
# 広告セット別（W固定スマホ車載ホルダー・伸縮ガラスクリーナー）Meta計上: 11/11 は o1111/adsets_1111_raw.txt、11/12 は o1112/adsets_1112_raw.txt
print('\n■ 広告セット別（Meta計上）広告費・購入・購入1件の広告費')
for f_, d in (('scripts/daily/o1111/adsets_1111_raw.txt', '11/11'), ('scripts/daily/o1112/adsets_1112_raw.txt', '11/12')):
    for l in open(f_):
        p = l.strip().split(',')
        if len(p) > 6 and p[0] in ('W固定スマホ車載ホルダー', '伸縮ガラスクリーナー'):
            cost, pu = int(p[4]), (0 if p[5] == 'null' else int(p[5]))
            print(f"  {d} {p[1]}: 広告 {cost:,}・購入 {pu}・{cost/max(pu,1):,.0f}円")
# 11/10 の減額の答え合わせ（減額前3日 11/7-9 と 後3日 11/10-12）
print('\n■ 11/10 00:29 の減額の答え合わせ（前3日 11/7〜9 → 後3日 11/10〜12・商品全体）')
for n in ('W固定スマホ車載ホルダー', '伸縮ガラスクリーナー'):
    mb, ab, pb, qb = mult(n, ['2026-11-07', '2026-11-08', '2026-11-09']); ma, aa, pa, qa = mult(n, ['2026-11-10', '2026-11-11', '2026-11-12'])
    gb, ga = pb + ab, pa + aa
    print(f"  {n}: 広告費 {ab:,.0f} → {aa:,.0f}（{aa-ab:+,.0f}）・粗利 {gb:,.0f} → {ga:,.0f}（{ga-gb:+,.0f}）・倍率 {mb:.2f} → {ma:.2f}・利益 {pb:+,.0f} → {pa:+,.0f}"
          f"｜減った粗利÷減った広告費 {((gb-ga)/(ab-aa)) if ab!=aa else float('nan'):.2f}")
# 新商品の2日目: 防風あったか裏起毛パンツ（Meta 11/12 終日）
for l in open('scripts/daily/o1112/meta_camp_1111_1112_raw.txt'):
    p = l.strip().split(',')
    if len(p) > 7 and p[1] == '防風あったか裏起毛パンツ':
        print(f"\n■ 防風あったか裏起毛パンツ {p[0]}: 広告 {int(p[2]):,}・表示 {int(p[3]):,}・クリック {p[4]}（{int(p[4])/int(p[3])*100:.2f}%）・LPV {p[5]}・Metaカート {p[6]}・Meta購入 {p[7]}")
m, a, pr, q = mult('防風あったか裏起毛パンツ', ['2026-11-11', '2026-11-12']); print(f"  2日の通算（Shopify）: {q}個・広告 {a:,.0f}・倍率 {m:.2f}・利益 {pr:+,.0f}")
# 3日平均の利益・Meta計上の購入÷Shopifyの注文
def tot(days):
    N, Q, K = W(days); s = sum(N.values()); k = sum(K.values()); a = ACCT(days); return s - k - a
p3 = [tot([d]) for d in ALLD[-3:]]; print(f"\n■ 3日平均の利益 {sum(p3)/3:,.0f}（{' / '.join(f'{x:+,.0f}' for x in p3)}）")
mp = collections.defaultdict(int)
for l in open('scripts/daily/o1112/meta_camp_1111_1112_raw.txt'):
    p = l.strip().split(',')
    if len(p) > 7 and p[0][:2] == '20': mp[p[0]] += int(p[7])
print(f"■ Meta計上の購入 ÷ Shopifyの注文: 11/11 {mp['2026-11-11']}/72 = {mp['2026-11-11']/72:.2f}・11/12 {mp['2026-11-12']}/68 = {mp['2026-11-12']/68:.2f}")
