# -*- coding: utf-8 -*-
"""11/19 17時台 「分析して。ちょっと復活した？」: 0〜15時台を過去21日（10/29〜11/18）の同じ時刻と比べる・時間帯別・商品別。
日中の数字なので、予算の判定・提案には使わない。入力は raw.txt だけ"""
import collections, math, statistics as st, os
D0 = os.path.dirname(os.path.abspath(__file__))
D = collections.defaultdict(dict); MH = {}; T = {}; P = []; C = []
for l in open(os.path.join(D0, 'raw.txt')):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] in ('S', 'V', 'M'): D[p[0]][p[1]] = [int(x) for x in p[2:]]
    elif p[0] == 'MH': MH[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'T': T[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'P': P.append((p[1], *[int(x) for x in p[2:]]))
    elif p[0] == 'C': C.append((p[1], *[int(x) for x in p[2:]]))
TD = '2026-11-19'; CUT = range(0, 16)
D['M'][TD] = [sum(MH[h][i] for h in CUT) for i in range(5)]
assert sum(T[h][0] for h in CUT) == D['S'][TD][0] and sum(T[h][3] for h in CUT) == D['S'][TD][3]
past = [d for d in sorted(D['S']) if d < TD]; assert len(past) == 21
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
def met(d):
    s, c, k, dn = D['S'][d]; o, g, dc = D['V'][d]; ad, imp, lpv, atc, pu = D['M'][d]
    return collections.OrderedDict([('注文', o), ('売上（値引後）', g - dc), ('広告費', ad), ('売上÷広告費', (g - dc) / ad), ('注文÷広告費1万円', o / ad * 1e4), ('CPM', ad / imp * 1000),
        ('来訪÷広告費1万円', s / ad * 1e4), ('カート率%', c / s * 100), ('完了÷決済画面%', dn / k * 100), ('買う率%（購入÷来訪）', dn / s * 100), ('1注文の売上', (g - dc) / o)])
out = []
out.append('■ ① 0〜15時台: 今日 と 過去21日（10/29〜11/18）の同じ時刻')
for k, v in met(TD).items():
    xs = [met(d)[k] for d in past]; lo = sum(x < v for x in xs)
    w = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
    out.append(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {st.median(xs):,.2f}・差 {v/st.median(xs)-1:+.0%}）・今日より低い日 {lo}/21 → {w}')
m = met(TD); med = {k: st.median(met(d)[k] for d in past) for k in m}
out.append(f"  注文÷広告費の差 {m['注文÷広告費1万円']/med['注文÷広告費1万円']-1:+.0%} の中身: 来訪÷広告費 {m['来訪÷広告費1万円']/med['来訪÷広告費1万円']-1:+.0%}・買う率 {m['買う率%（購入÷来訪）']/med['買う率%（購入÷来訪）']-1:+.0%}")
s_, c_, k_, d_ = D['S'][TD]; base = lambda i, j: sum(D['S'][d][i] for d in past) / sum(D['S'][d][j] for d in past)
for lab, obs, n, r in (('カートに入れた来訪', c_, s_, base(1, 0)), ('購入（来訪から）', d_, s_, base(3, 0))):
    lam = n * r; out.append(f'  {lab}: {obs}（{n}×過去21日の率 {r:.2%}＝見込み {lam:.1f}）・この数以下になる確率 {ple(obs, lam):.0%}')
out.append('■ ② 直近の流れ（同じ 0〜15時台）: 注文・売上÷広告費・CPM・カート率・買う率')
for d in past[-7:] + [TD]:
    x = met(d); out.append(f"  {d[5:]}: {x['注文']}件・{x['売上÷広告費']:.2f}・CPM {x['CPM']:,.0f}・{x['カート率%']:.2f}%・{x['買う率%（購入÷来訪）']:.2f}%")
cvr = base(3, 0); cart = base(1, 0)
out.append(f'■ ③ 今日の時間帯別（ふだん＝過去21日の 0〜15時台: カート率 {cart:.2%}・買う率 {cvr:.2%}）')
for lab, hs in (('0〜9時台', range(0, 10)), ('10〜13時台', range(10, 14)), ('14〜15時台', range(14, 16))):
    s = sum(T[h][0] for h in hs); c = sum(T[h][1] for h in hs); dn = sum(T[h][3] for h in hs); ad = sum(MH[h][0] for h in hs); imp = sum(MH[h][1] for h in hs); lpv = sum(MH[h][2] for h in hs); atc = sum(MH[h][3] for h in hs)
    e = s * cvr; ec = s * cart
    pr = f'{dn} 件以下の確率 {ple(dn, e):.1%}' if dn < e else f'{dn} 件以上の確率 {pge(dn, e):.0%}'
    prc = f'{c} 件以下 {ple(c, ec):.1%}' if c < ec else f'{c} 件以上 {pge(c, ec):.1%}'
    out.append(f'  {lab}: 来訪 {s}・カート追加 {c}（{c/s:.1%}・見込み {ec:.1f}・{prc}）・購入 {dn}（{dn/s:.2%}・見込み {e:.1f}・{pr}）｜広告費 {ad:,}・CPM {ad/imp*1000:,.0f}・Meta カート÷着地 {atc/lpv:.1%}')
out.append(f"  16時台（取り込み途中）: 来訪 {T[16][0]}・カート追加 {T[16][1]}・購入 {T[16][3]}・広告費 {MH[16][0]:,}")
tot_o = sum(T[h][3] for h in range(0, 17)); out.append(f'  今日ここまで（0〜16時台）の購入 {tot_o}・広告費 {sum(MH[h][0] for h in range(0, 17)):,}')
out.append('■ ④ 商品別（今日 17時ごろまで。広告費が出ている全キャンペーン＋カタログ。日中の数字なので良い悪いは決めない）')
out.append('  商品: 注文・個数・売上（値引後）・広告費・売上÷広告費 ｜ クリック率・Meta カート')
used = set()
for cn, cost, imp, clk, atc, pu in sorted(C, key=lambda x: -x[1]):
    key = cn.replace(' v3', '').replace('v2', '').replace('v5', '').strip()
    hit = [x for x in P if x[0] in key or key in x[0]]
    if cn.startswith('カタログ'): out.append(f'  {cn}: —・—・—・{cost:,}・— ｜ {clk/imp:.2%}・{atc}'); continue
    if hit: n, o, g, dc, q = hit[0]; used.add(n); out.append(f'  {cn}: {o}件・{q}個・{g-dc:,}・{cost:,}・{(g-dc)/cost:.2f} ｜ {clk/imp:.2%}・{atc}')
    else: out.append(f'  {cn}: 0件・0個・0・{cost:,}・0.00 ｜ {clk/imp:.2%}・{atc}')
rest = [x for x in P if x[0] not in used]
out.append('  広告なしで売れたもの: ' + ' / '.join(f'{n} {o}件 {g-dc:,}円' for n, o, g, dc, q in rest))
out.append(f"  合計: 売上（値引後） {sum(g-dc for n,o,g,dc,q in P):,}・広告費 {sum(x[1] for x in C):,}・売上÷広告費 {sum(g-dc for n,o,g,dc,q in P)/sum(x[1] for x in C):.2f}")
open(os.path.join(D0, 'today_h17.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
