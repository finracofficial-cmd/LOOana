# -*- coding: utf-8 -*-
"""11/20 11時台 「今時点のパフォーマンスを分析して」: 0〜10時台を過去21日（10/30〜11/19）の同じ時刻と比べる・時間帯別・商品別。
日中の数字なので、予算の判定・提案には使わない。入力は raw.txt だけ"""
import collections, math, re, statistics as st, os
D0 = os.path.dirname(os.path.abspath(__file__))
D = collections.defaultdict(dict); MH = {}; T = {}; TV = {}; H = {}; PD = collections.defaultdict(dict); C = []
for l in open(os.path.join(D0, 'raw.txt')):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] in ('S', 'V', 'M'): D[p[0]][p[1]] = [int(x) for x in p[2:]]
    elif p[0] == 'MH': MH[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'T': T[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'TV': TV[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'H': H[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'PD': PD[p[1]][p[2]] = [int(x) for x in p[3:]]
    elif p[0] == 'C': C.append((p[1], *[int(x) for x in p[2:]]))
TD = '2026-11-20'; CUT = range(0, 11)
# 今日の Meta（0〜10時台）: cost, imp, LPV, ATC, purchase
D['M'][TD] = [sum(MH[h][i] for h in CUT) for i in (0, 1, 3, 4, 5)]
# 照合: 時間別の合計＝日別、商品別の合計＝日別、キャンペーン別の合計＝時間別
assert sum(T[h][0] for h in CUT) == D['S'][TD][0] and sum(T[h][3] for h in CUT) == D['S'][TD][3]
assert sum(TV.get(h, [0, 0, 0])[0] for h in CUT) == D['V'][TD][0] and sum(TV.get(h, [0, 0, 0])[1] for h in CUT) == D['V'][TD][1]
for d in PD: assert sum(v[1] for v in PD[d].values()) == D['V'][d][1] and sum(v[2] for v in PD[d].values()) == D['V'][d][2], d
assert sum(c[1] for c in C) == D['M'][TD][0] and sum(c[2] for c in C) == D['M'][TD][1]
past = [d for d in sorted(D['S']) if d < TD]; assert len(past) == 21 and past[0] == '2026-10-30'
assert sum(H[h][0] for h in CUT) == sum(D['S'][d][0] for d in past) and sum(H[h][3] for h in CUT) == sum(D['S'][d][3] for d in past)
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
def pge(k, l): return 1 - ple(k - 1, l) if k > 0 else 1.0
def met(d):
    s, c, k, dn = D['S'][d]; o, g, dc = D['V'][d]; ad, imp, lpv, atc, pu = D['M'][d]
    return collections.OrderedDict([('注文', o), ('売上（値引後）', g - dc), ('広告費', ad), ('売上÷広告費', (g - dc) / ad), ('注文÷広告費1万円', o / ad * 1e4), ('CPM', ad / imp * 1000),
        ('来訪÷広告費1万円', s / ad * 1e4), ('カート率%', c / s * 100), ('完了÷決済画面%', dn / k * 100), ('買う率%（購入÷来訪）', dn / s * 100), ('1注文の売上', (g - dc) / o)])
out = []
out.append('■ ① 0〜10時台: 今日（11/20 金）と 過去21日（10/30〜11/19）の同じ時刻')
for k, v in met(TD).items():
    xs = [met(d)[k] for d in past]; lo = sum(x < v for x in xs)
    w = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
    out.append(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {st.median(xs):,.2f}・差 {v/st.median(xs)-1:+.0%}）・今日より低い日 {lo}/21 → {w}')
m = met(TD); med = {k: st.median(met(d)[k] for d in past) for k in m}
out.append(f"  売上÷広告費の差 {m['売上÷広告費']/med['売上÷広告費']-1:+.0%} の中身（それぞれ中央値との差）: 来訪÷広告費 {m['来訪÷広告費1万円']/med['来訪÷広告費1万円']-1:+.0%}・買う率 {m['買う率%（購入÷来訪）']/med['買う率%（購入÷来訪）']-1:+.0%}・1注文の売上 {m['1注文の売上']/med['1注文の売上']-1:+.0%}")
s_, c_, k_, d_ = D['S'][TD]; base = lambda i, j: sum(D['S'][d][i] for d in past) / sum(D['S'][d][j] for d in past)
for lab, obs, n, r in (('カートに入れた来訪', c_, s_, base(1, 0)), ('購入（来訪から）', d_, s_, base(3, 0))):
    lam = n * r; pr = f'この数以上になる確率 {pge(obs, lam):.1%}' if obs >= lam else f'この数以下になる確率 {ple(obs, lam):.1%}'
    out.append(f'  {lab}: {obs}（来訪 {n}×過去21日の率 {r:.2%}＝見込み {lam:.1f}）・{pr}')
o_ = D['V'][TD][0]; ad_ = D['M'][TD][0]
for lab, ds in (('過去21日', past), ('直近7日（11/13〜19）', past[-7:])):
    r = sum(D['V'][d][0] for d in ds) / sum(D['M'][d][0] for d in ds); lam = ad_ * r
    out.append(f'  注文（広告費から・{lab}の率）: {o_}（広告費 {ad_:,}×1万円あたり {r*1e4:.2f}件＝見込み {lam:.1f}）・この数以上になる確率 {pge(o_, lam):.1%}')
out.append('■ ② 直近の流れ（同じ 0〜10時台）: 注文・広告費・売上÷広告費・CPM・カート率・買う率')
for d in past[-7:] + [TD]:
    x = met(d); out.append(f"  {d[5:]}: {x['注文']}件・{x['広告費']:,}・{x['売上÷広告費']:.2f}・CPM {x['CPM']:,.0f}・{x['カート率%']:.2f}%・{x['買う率%（購入÷来訪）']:.2f}%")
cvr = base(3, 0); cart = base(1, 0)
out.append('■ ③ 今日の時間帯別（見込み＝今日の来訪 × 過去21日のその時刻の率。時刻ごとに掛けて足した）')
for lab, hs in (('0〜6時台', range(0, 7)), ('7〜9時台', range(7, 10)), ('10時台', range(10, 11))):
    s = sum(T[h][0] for h in hs); c = sum(T[h][1] for h in hs); dn = sum(T[h][3] for h in hs); ad = sum(MH[h][0] for h in hs); imp = sum(MH[h][1] for h in hs)
    o = sum(TV.get(h, [0, 0, 0])[0] for h in hs); sal = sum(TV.get(h, [0, 0, 0])[1] - TV.get(h, [0, 0, 0])[2] for h in hs)
    e = sum(T[h][0] * H[h][3] / H[h][0] for h in hs); ec = sum(T[h][0] * H[h][1] / H[h][0] for h in hs)
    pr = f'{dn} 件以下の確率 {ple(dn, e):.1%}' if dn < e else f'{dn} 件以上の確率 {pge(dn, e):.1%}'
    prc = f'{c} 件以下 {ple(c, ec):.1%}' if c < ec else f'{c} 件以上 {pge(c, ec):.1%}'
    out.append(f'  {lab}: 来訪 {s}・カート追加 {c}（{c/s:.1%}・見込み {ec:.1f}・{prc}）・購入 {dn}（{dn/s:.2%}・見込み {e:.1f}・{pr}）｜注文 {o}・売上 {sal:,}・広告費 {ad:,}・売上÷広告費 {sal/ad:.2f}・CPM {ad/imp*1000:,.0f}')
hs = CUT; e = sum(T[h][0] * H[h][3] / H[h][0] for h in hs); dn = sum(T[h][3] for h in hs)
out.append(f'  0〜10時台の合計（時刻ごとの率で）: 購入 {dn}・見込み {e:.1f}・{dn} 件以上の確率 {pge(dn, e):.1%}')
out.append('  過去21日の買う率（時刻別）: ' + ' / '.join(f'{h}時 {H[h][3]/H[h][0]:.2%}' for h in range(0, 14)))
out.append(f"  11時台（11:35 まで・取り込み途中）: 来訪 {T[11][0]}・カート追加 {T[11][1]}・購入 {T[11][3]}・広告費 {MH[11][0]:,}")
out.append('■ ④ 商品別（今日 0〜10時台。広告費が出ている全キャンペーン＋カタログ。日中の数字なので良い悪いは決めない）')
out.append('  商品: 今日の注文・個数・売上（値引後）・広告費・売上÷広告費 ｜ クリック率・Meta カート ｜ 直近7日（11/13〜19）の同じ時刻の注文（日ごと）・平均 → 今日の注文数がその平均から出る確率')
week = past[-7:]; used = set(); tp = PD[TD]
for cn, cost, imp, clk, atc, pu in sorted(C, key=lambda x: -x[1]):
    key = re.sub(r'\s*v\d+$', '', cn).strip()
    if cn.startswith('カタログ'): out.append(f'  {cn}: —・—・—・{cost:,}・— ｜ {clk/imp:.2%}・{atc} ｜ —'); continue
    o, g, dc, q = tp.get(key, [0, 0, 0, 0]); used.add(key)
    hist = [PD[d].get(key, [0])[0] for d in week]; lam = sum(hist) / 7
    if lam == 0: pr = '直近7日は0件'
    elif o >= lam: pr = f'{o}件以上 {pge(o, lam):.0%}'
    else: pr = f'{o}件以下 {ple(o, lam):.0%}'
    out.append(f'  {cn}: {o}件・{q}個・{g-dc:,}・{cost:,}・{(g-dc)/cost:.2f} ｜ {clk/imp:.2%}・{atc} ｜ {"/".join(str(x) for x in hist)}・平均 {lam:.1f} → {pr}')
rest = [(n, v) for n, v in tp.items() if n not in used]
out.append('  広告なしで売れたもの: ' + (' / '.join(f'{n} {v[0]}件 {v[1]-v[2]:,}円' for n, v in rest) if rest else 'なし'))
tot = sum(v[1] - v[2] for v in tp.values()); out.append(f"  合計: 売上（値引後） {tot:,}・広告費 {sum(x[1] for x in C):,}・売上÷広告費 {tot/sum(x[1] for x in C):.2f}")
open(os.path.join(D0, 'today_h11.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
