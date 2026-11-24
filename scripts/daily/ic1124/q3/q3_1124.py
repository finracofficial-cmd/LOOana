# -*- coding: utf-8 -*-
"""11/24 20時台「UV も毛玉もだめそうやな？ 卓上加湿器は様子見か？」
① 3商品の日別（11/23 までの終日は w1123.py・今日は 20時までの取得: prod_2000_1124_raw.json／meta_3_2000_1124_raw.json）
② 10/1 以降に広告を始めた23本（ic1122/plan/life_1122.txt の②の開始日）: 最初の2日・3日の倍率 → 最初の7日の倍率・開始〜11/23 の利益
③ 7日の判定日までに 1.25・1.5 へ届くのに要る個数と、今のペースが続いたときに届く確率（ポアソン）
倍率＝(売上（値引後）−原価)÷広告費。今日の分は途中（20時まで）なので、判定には使わず「参考」として足す"""
import io, contextlib, re, json, math, os
os.chdir('/home/user/LOOana')
D0 = 'scripts/daily/ic1124/q3/'
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, COST, PRICE = g['A'], g['ALLD'], g['agg'], g['WIN'], g['COST'], g['PRICE']
def one(n, ds, key):
    WIN[key] = ds; N, DC, Q, K = agg(ds, key); return A(ds, n), N.get(n, 0) - K.get(n, 0), Q.get(n, 0)
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
fmt = lambda p: '1%未満' if p < 0.01 else f'{p:.0%}'
def pois_ge(e, k): return 1 - sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(k)) if k > 0 else 1.0
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
TP = {nm(r[0]): (int(r[1]), int(r[2]) + int(r[3]), int(r[4])) for r in json.load(open(D0 + 'prod_2000_1124_raw.json'))['rows'] if 'LOOTY' in r[0]}
TM = {}
for l in json.load(open(D0 + 'meta_3_2000_1124_raw.json'))['data']['data'].split('\n')[1:]:
    if not l.strip(): continue
    c, ad, cost, imp, clk, cart, pur = l.strip().split(',')
    k = 'UV歯ブラシ除菌器' if 'UV' in c else 'コードレス毛玉クリーナー' if '毛玉' in c else '充電式ダブルミスト卓上加湿器'
    v = TM.setdefault(k, [0, 0, 0]); v[0] += round(float(cost)); v[1] += 0 if clk == 'null' else int(clk); v[2] += 0 if cart == 'null' else int(cart)
# ② 10/1 以降に始めた23本
rows = []; on = False
for l in open('scripts/daily/ic1122/plan/life_1122.txt'):
    if l.startswith('■ ②'): on = True; continue
    if l.startswith('■ ③'): break
    m = re.match(r'^  (.+?): (\d\d-\d\d)〜', l)
    if on and m: rows.append((m.group(1), '2026-' + m.group(2)))
assert len(rows) == 23
P('■ ② 10/1 以降に広告を始めた23本: 最初の2日・3日の倍率 → 最初の7日の倍率｜開始〜11/23 の利益（広告を出した日で数える）')
R2 = []
for n, st in rows:
    ds = [d for d in ALLD if d >= st and A([d], n) > 0]
    if len(ds) < 2: continue
    f = lambda k: one(n, ds[:k], f'q3{n}{k}')
    (a2, g2, _), (a3, g3, _), (a7, g7, _), (al, gl, _) = f(2), f(3), f(7), f(len(ds))
    R2.append((n, g2 / a2, g3 / a3 if len(ds) >= 3 else None, g7 / a7, len(ds), gl - al))
for n, r2, r3, r7, k, p in sorted(R2, key=lambda x: x[1]):
    P(f"  {n}: 2日 {r2:.2f}・3日 {'—' if r3 is None else f'{r3:.2f}'} → 7日 {r7:.2f}（{min(k,7)}日）｜{k}日・利益 {p:+,.0f}")
lo = [x for x in R2 if x[1] < 1.25 and x[4] >= 3]
P(f"  最初の2日が 1.25 未満で3日以上出した {len(lo)}本 → 7日 1.25 以上 {sum(1 for x in lo if x[3] >= 1.25)}本・1.5 以上 {sum(1 for x in lo if x[3] >= 1.5)}本・利益5万円以上 {sum(1 for x in lo if x[5] >= 50000)}本")
hi = [x for x in R2 if x[1] >= 1.25 and x[4] >= 3]
P(f"  最初の2日が 1.25 以上で3日以上出した {len(hi)}本 → 7日 1.5 以上 {sum(1 for x in hi if x[3] >= 1.5)}本・利益5万円以上 {sum(1 for x in hi if x[5] >= 50000)}本")
# ① ③ 3商品
P('■ ① ③ 3商品（11/23 までは終日・今日は 20時まで＝途中）')
for n, st, end, last in (('UV歯ブラシ除菌器', '2026-11-22', '11/28', 4), ('コードレス毛玉クリーナー', '2026-11-22', '11/28', 4), ('充電式ダブルミスト卓上加湿器', '2026-11-19', '11/25', 1)):
    ds = [d for d in ALLD if d >= st and A([d], n) > 0]
    a, gp, q = one(n, ds, 'q3c' + n)
    for d in ds:
        a1, g1, q1 = one(n, [d], 'q3d' + n + d); P(f'  {n} {d[5:]}: 広告費 {a1:,.0f}・{q1}個・倍率 {g1/a1:.2f}')
    to, tn, tq = TP.get(n, (0, 0, 0)); ta, tc, tcart = TM[n]
    gpu = gp / q  # 1個の粗利（開始〜11/23 の実績）
    tg = tn - tq * COST[n] if tq else 0
    P(f'  {n} 今日（20時まで）: 広告費 {ta:,}・{tc}クリック（1回 {ta/tc:.0f}円）・カート {tcart}（Meta）・{to}注文{tq}個（Shopify）｜1.25 に届くクリック1回の値段（〜11/23 のクリック1回の粗利 ÷ 1.25）は下の q5 の値で見る')
    A_all, G_all = a + ta, gp + tg
    P(f'  {n} 開始〜今日20時: 広告費 {A_all:,.0f}・{q + tq}個・倍率 {G_all/A_all:.2f}・1個の粗利 {gpu:,.0f}（〜11/23）')
    # 判定日まで: 今日の残り（日予算8,000 の実績の使い方: 〜11/23 の広告費/日）＋ last 日
    full = [one(n, [d], 'q3f' + n + d)[0] for d in ds[1:][-2:]]; per = sum(full) / len(full)   # 1日の広告費＝初日（途中から出した）を除いた直近2日まで の平均
    rest_today = max(0, per - ta); fut_ad = rest_today + per * last
    tot_ad = A_all + fut_ad
    for tgt in (1.25, 1.5):
        need = max(0, math.ceil((tgt * tot_ad - G_all) / gpu))
        rate = (q + tq) / A_all; e = rate * fut_ad
        P(f'    7日（〜{end}）で {tgt}: 広告費の合計 見込み {tot_ad:,.0f}（今日の残り {rest_today:,.0f}＋{last}日 × {per:,.0f}）→ あと {need}個 要る｜今のペース（{(q+tq)/A_all*10000:.2f}個/1万円）なら {e:.1f}個 → 届く確率 {fmt(pois_ge(e, need))}')
    r_now = G_all / A_all; r_23 = gp / a
    P(f'    判定日まで待つ損得（今日の残り＋{last}日の広告費 {fut_ad:,.0f} × (倍率−1)）: 今日20時までの {r_now:.2f} なら {(r_now-1)*fut_ad:+,.0f}円・11/23 までの {r_23:.2f} なら {(r_23-1)*fut_ad:+,.0f}円')
open(D0 + 'q3_1124.txt', 'w').write('\n'.join(out) + '\n')
