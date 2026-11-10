# -*- coding: utf-8 -*-
"""11/11 00時台: 過去に広告を出した商品の「配信期間（ラン）」ごとの実績（CSV実測・6/29〜11/10）。
ラン=広告費が出た日の連なり（間が3日以上空いたら別のラン）。倍率=(実売−原価)÷広告費・利益=実売−原価−広告費（その期間の商品売上をすべて含む）。
再開＝7日以上あけて出し直したラン。w1110.py の積み直し関数（原価はバリアント・売価変更に対応）をそのまま使う"""
import io, contextlib, datetime, collections
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1110.py').read(), g)
WIN, agg, ALLD, MAP, AD, S, COST = g['WIN'], g['agg'], g['ALLD'], g['MAP'], g['AD'], g['S'], g['COST']
INV = {v: k for k, v in MAP.items()}
D = lambda s: datetime.date.fromisoformat(s)
def W(days, n):   # その商品だけを積む（全商品をaggすると、バリアントCSVのない夏の期間でナノのassertに当たる）
    key = 'r' + n + days[0] + days[-1] + str(len(days)); WIN[key] = days
    sal = sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
    q, k = g['qty'](n, days, key)
    return sal, k, q
ACTIVE = {'クリアビューレインガードフィルム', 'ワイド水切りワイパー', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ', '伸縮ガラスクリーナー', '4-in-1マルチクリーナー',
          '快適マジックインソール', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '姿勢サポートチェア'}   # 11/11 00:15 Meta直読で配信中
runs = {}
for c in AD:
    if 'カタログ' in c: continue
    n = INV.get(c, c)
    days = sorted(d for d in AD[c] if AD[c][d] >= 500 and d in ALLD)
    if not days: continue
    rs = [[days[0]]]
    for d in days[1:]:
        if (D(d) - D(rs[-1][-1])).days >= 3: rs.append([d])
        else: rs[-1].append(d)
    out = []
    for r in rs:
        span = [d for d in ALLD if r[0] <= d <= r[-1]]
        try: s, k, q = W(span, n)
        except Exception as e: out.append((r[0], r[-1], len(r), None, None, None, None, str(e)[:40])); continue
        a = sum(AD[c].get(d, 0) for d in span)
        out.append((r[0], r[-1], len(r), a, q, s - k - a, (s - k) / a if a else None, ''))
    runs[n] = out
print('■ いま広告を止めている商品（6/29以降に広告あり）: 通算と最後のラン。並びは通算利益の大きい順')
rows = []
for n, out in runs.items():
    if n in ACTIVE: continue
    ok = [o for o in out if o[3] is not None]
    if not ok: print('  集計不可', n, out); continue
    ta = sum(o[3] for o in ok); tp = sum(o[5] for o in ok); tq = sum(o[4] for o in ok)
    last = ok[-1]
    # 最後のランの終わり14日
    c = MAP.get(n, n); ld = [d for d in ALLD if last[0] <= d <= last[1]][-14:]
    s, k, q = W(ld, n); a = sum(AD[c].get(d, 0) for d in ld)
    rows.append((tp, n, ta, tq, len(ok), last, (s - k) / a if a else None, len(ld)))
for tp, n, ta, tq, nr, last, m14, nd in sorted(rows, reverse=True):
    print(f"  {n}: 通算 利益{tp:+,.0f}・広告{ta:,.0f}・{tq}個・ラン{nr}回 ／ 最後 {last[0][5:]}〜{last[1][5:]}（{last[2]}日）倍率{last[6]:.2f}・利益{last[5]:+,.0f} ／ 最後の{nd}日の倍率 {m14:.2f}" if m14 is not None else f"  {n}: {tp:+,.0f}")
print('\n■ 再開の実績（7日以上あけて出し直したラン・全商品）: 前のラン → 出し直したラン')
tot = collections.Counter(); sp = 0
for n, out in runs.items():
    ok = [o for o in out if o[3] is not None]
    for i in range(1, len(ok)):
        gap = (D(ok[i][0]) - D(ok[i-1][1])).days - 1
        if gap < 7: continue
        p, c2 = ok[i-1], ok[i]
        res = '黒字' if c2[5] > 0 else '赤字'
        tot[res] += 1; sp += c2[5]
        print(f"  {n}: 前 {p[0][5:]}〜{p[1][5:]}（{p[2]}日）倍率{p[6]:.2f}・利益{p[5]:+,.0f} → {gap}日あけて {c2[0][5:]}〜{c2[1][5:]}（{c2[2]}日）広告{c2[3]:,.0f}・{c2[4]}個・倍率{c2[6]:.2f}・利益{c2[5]:+,.0f}{'（配信中）' if n in ACTIVE and c2 is ok[-1] else ''}")
print('  再開ランの結果', dict(tot), '利益の合計', f'{sp:+,.0f}')
print('\n■ 直近30日（10/12〜11/10）に広告なしで売れた商品（広告費0の日の販売）')
d30 = ALLD[-30:]
for n in sorted(S):
    if n in ACTIVE or not n: continue
    c = MAP.get(n, n); dd = [d for d in d30 if d in S[n] and S[n][d][0] and AD[c].get(d, 0) < 500]
    if not dd: continue
    try: s, k, q = sum(S[n][d][0] - S[n][d][1] for d in dd), None, None
    except Exception: continue
    print(f"  {n}: {len(dd)}日・実売{s:,}（最後に売れた日 {dd[-1][5:]}）")

print('\n■ フック停止（11/3 13:54）の答え合わせ: 止める前7日（10/27〜11/2）と止めた後7日（11/4〜11/10）')
n = '高見えレザーヘッドレストフック'; c = MAP.get(n, n)
for lab, days in [('前', [d for d in ALLD if '2026-10-27' <= d <= '2026-11-02']), ('後', [d for d in ALLD if '2026-11-04' <= d <= '2026-11-10'])]:
    sal, k, q = W(days, n); a = sum(AD[c].get(d, 0) for d in days)
    print(f"  {lab}: 広告{a:,.0f}・{q}個・粗利{sal-k:,}・利益{sal-k-a:+,.0f}")
print('\n■ 候補の最後のランを前半・後半に分けた倍率（落ちて止めたのか、落ちる前に止めたのか）')
for n in ['高見えレザーヘッドレストフック', 'ポータブルヒートシーラー', '携帯電動シェーバー', 'UV歯ブラシ除菌器', 'ナノバブルシャワーヘッド', 'ネックマッサージャー', '2WAYシートボックス', 'むくみ取りかっさ', 'もちふわ肉球サンダル', 'ムダ毛シェーバー']:
    c = MAP.get(n, n); ok = [o for o in runs[n] if o[3] is not None and o[2] >= 7]
    if not ok: print(' ', n, '7日以上のランなし'); continue
    last = ok[-1]; span = [d for d in ALLD if last[0] <= d <= last[1]]; h = len(span) // 2
    out = []
    for dd in (span[:h], span[h:], span[-7:]):
        sal, k, q = W(dd, n); a = sum(AD[c].get(d, 0) for d in dd); out.append(f"{dd[0][5:]}〜{dd[-1][5:]} {(sal-k)/a:.2f}（{q}個・広告{a:,.0f}）")
    print(f"  {n}: 前半 {out[0]} ／ 後半 {out[1]} ／ 最後7日 {out[2]}")
print('\n■ 10/1以降に出した商品: 最初の1個が売れるまでの広告費（日次CSV・その日の終わりまでの累計）と、その後の通算')
first = {c: min(d for d in AD[c] if AD[c][d] >= 500) for c in AD if any(v >= 500 for v in AD[c].values())}
for c, f in sorted(first.items(), key=lambda x: x[1]):
    if f < '2026-10-01' or 'カタログ' in c: continue
    n = INV.get(c, c); days = [d for d in ALLD if d >= f and AD[c].get(d, 0) >= 500]
    cum = 0; hit = None
    for d in [d for d in ALLD if d >= f]:
        cum += AD[c].get(d, 0)
        if d in S[n] and S[n][d][0]: hit = (d, cum); break
    tot = [o for o in runs.get(n, []) if o[3] is not None]
    tp = sum(o[5] for o in tot); ta = sum(o[3] for o in tot)
    d1 = AD[c].get(f, 0); s1 = S[n][f][0] if f in S[n] else 0
    print(f"  {n}（{f[5:]}開始）: 初日 広告{d1:,.0f}・売上{s1:,} ／ 最初の販売日 {hit[0][5:] if hit else 'なし'}（そこまでの広告費 {hit[1] if hit else cum:,.0f}）／ 通算 広告{ta:,.0f}・利益{tp:+,.0f}")
