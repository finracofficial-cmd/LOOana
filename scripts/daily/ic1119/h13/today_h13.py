# -*- coding: utf-8 -*-
"""11/19 13時台 「今日のパフォーマンスの悪さを徹底的に分析」: 0〜12時台を過去21日（10/29〜11/18）の同じ時刻と比べる。
①結果 ②どの段で落ちたか（Shopify の来訪→カート→決済画面→完了・Meta の CPM）③時間帯 ④商品ページ ⑤技術的な故障かどうか（支払い方法・離脱）。日中の数字なので予算の判断には使わない"""
import collections, math, statistics as st
D = collections.defaultdict(dict); H = {}; T = {}; MH = {}; L = []; AB = {}; PW = []
for l in open('raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] in 'OSVM' and len(p[0]) == 1: D[p[0]][p[1]] = [int(x) for x in p[2:]]
    elif p[0] == 'H': H[int(p[1])] = int(p[2])
    elif p[0] == 'T': T[int(p[1])] = int(p[2])
    elif p[0] == 'MH': MH[int(p[1])] = [int(x) for x in p[2:]]
    elif p[0] == 'L': L.append((p[1], *[int(x) for x in p[2:]]))
    elif p[0] == 'AB': AB[p[1]] = int(p[2])
    elif p[0] == 'PW': PW.append((p[1], *[int(x) for x in p[2:]]))
TD = '2026-11-19'; D['M'][TD] = [sum(v[i] for v in MH.values()) for i in range(5)]
past = [d for d in sorted(D['O']) if d < TD]; assert len(past) == 21
def met(d):
    o = D['O'][d][0]; s, c, k, dn = D['S'][d]; vo, g, dc = D['V'][d]; ad, imp, lpv, atc, pu = D['M'][d]
    return collections.OrderedDict([('注文', o), ('売上（値引後）', g - dc), ('広告費', ad), ('売上÷広告費', (g - dc) / ad), ('注文÷広告費1万円', o / ad * 1e4), ('CPM', ad / imp * 1000),
        ('来訪（Shopify）÷広告費1万円', s / ad * 1e4), ('1人あたりの広告費（円）', ad / s), ('カート率%', c / s * 100), ('決済画面÷カート%', k / c * 100), ('完了÷決済画面%', dn / k * 100), ('買う率%（完了÷来訪）', dn / s * 100), ('客単価', (g - dc) / vo)])
print('■ ① 0〜12時台: 今日 と 過去21日（10/29〜11/18）の同じ時刻')
for k, v in met(TD).items():
    xs = [met(d)[k] for d in past]; lo = sum(x < v for x in xs)
    out = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
    print(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {st.median(xs):,.2f}・差 {v/st.median(xs)-1:+.0%}）・今日より低い日 {lo}/21 → {out}')
m = met(TD); med = {k: st.median(met(d)[k] for d in past) for k in m}
print(f"  注文÷広告費の差 {m['注文÷広告費1万円']/med['注文÷広告費1万円']-1:+.0%} の中身: 来訪÷広告費 {m['来訪（Shopify）÷広告費1万円']/med['来訪（Shopify）÷広告費1万円']-1:+.0%} × 買う率 {m['買う率%（完了÷来訪）']/med['買う率%（完了÷来訪）']-1:+.0%}（買う率の中: カート率 {m['カート率%']/med['カート率%']-1:+.0%}・決済画面÷カート {m['決済画面÷カート%']/med['決済画面÷カート%']-1:+.0%}・完了÷決済画面 {m['完了÷決済画面%']/med['完了÷決済画面%']-1:+.0%}）")
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
s_, c_, k_, d_ = D['S'][TD]; base = lambda i, j: sum(D['S'][d][i] for d in past) / sum(D['S'][d][j] for d in past)
for lab, obs, n, r in (('カートに入れた来訪', c_, s_, base(1, 0)), ('購入完了（来訪から）', d_, s_, base(3, 0)), ('購入完了（決済画面から）', d_, k_, base(3, 2))):
    lam = n * r; print(f'  {lab}: {obs}（{n}×過去21日の率 {r:.2%}＝期待 {lam:.1f}）・この数以下になる確率 {ple(obs, lam):.0%}')
print('■ ② 直近の流れ（同じ時刻）: 注文・注文÷広告費1万円・CPM・1人あたり広告費・カート率・完了÷決済画面・買う率')
for d in past[-7:] + [TD]:
    x = met(d); print(f"  {d[5:]}: {x['注文']}件・{x['注文÷広告費1万円']:.2f}・CPM {x['CPM']:,.0f}・{x['1人あたりの広告費（円）']:.0f}円・{x['カート率%']:.2f}%・{x['完了÷決済画面%']:.0f}%・{x['買う率%（完了÷来訪）']:.2f}%")
print('■ ③ 時間帯（今日の注文 と 過去21日の1日平均）・Meta の今日の時間別')
tot_t = 0; tot_e = 0
for lab, hs in (('0〜5時台', range(0, 6)), ('6〜9時台', range(6, 10)), ('10〜12時台', range(10, 13))):
    t = sum(T[h] for h in hs); e = sum(H[h] for h in hs) / 21; ad = sum(MH[h][0] for h in hs); imp = sum(MH[h][1] for h in hs); lpv = sum(MH[h][2] for h in hs); atc = sum(MH[h][3] for h in hs)
    pr = ple(t, e) if t < e else 1 - ple(t - 1, e)
    print(f"  {lab}: 注文 {t}（ふだん {e:.1f}・{'少ない' if t < e else '多い'}側 {pr:.1%}）｜広告費 {ad:,}・CPM {ad/imp*1000:,.0f}・着地 {lpv}・Meta カート {atc}（カート÷着地 {atc/lpv:.1%}）")
print('  ※ 12時台の Meta の着地・カートは取り込み途中（広告費 11,428 に対し着地 59）。ふだんの注文は広告費が今日より多い日も含む平均')
print('■ ④ 商品ページ別（今日 13時ごろまで・Shopify）: 来訪・カート・決済画面・完了')
for n, s, c, k, dn in L: print(f'  {n}: {s}・{c}（{c/s:.1%}）・{k}・{dn}')
ts = sum(x[1] for x in L); tk = sum(x[3] for x in L); tdn = sum(x[4] for x in L); print(f'  14ページの合計: 来訪 {ts}・決済画面 {tk}・完了 {tdn}（{tdn/tk:.0%}）')
print('■ ⑤ 故障かどうか')
print(f"  連絡先を入れて離れた決済（0〜12時台）: 今日 {AB[TD]}・11/18 {AB['2026-11-18']}・11/17 {AB['2026-11-17']}・11/16 {AB['2026-11-16']}・11/12 {AB['2026-11-12']}")
print('  今日の支払い方法: カード 22・スマホ決済 2・ペイディ 1（3つとも通っている）。11/18: カード 59・スマホ決済 5・ペイディ 0')
print('  カード以外の割合（週）: ' + ' '.join(f"{w[5:]} {(b+c)/(a+b+c):.0%}" for w, a, b, c in PW))
