# -*- coding: utf-8 -*-
"""11/17(火) 20:3x 「パフォーマンスがわるい！その要因を分析せよ」
0〜19時台を過去21日（10/27〜11/16）の同じ時刻と比べ、売上÷広告費の低さを分ける。
①店全体: 売上÷広告費 ＝ 表示÷広告費（CPMの逆）× 着地÷表示 × 来訪÷着地 × 注文÷来訪 × 客単価
②商品別: 以前からある商品は 11/10〜14 の同時刻の「売上÷広告費」を今日の広告費に掛けて期待の売上を出し、実際との差を円で出す。
   新しい商品（ノーズ v2・マルチクリップ・シェーバー v2・インソール v3・ブランケット・グローブ）は比べる過去が短いので、今日の売上÷広告費をそのまま出す
日中の数字なので予算の判定には使わない。入力: store_sales_0019.json・store_sess_0019.json・meta_acct_0019.txt・meta_camp_0019.txt・sales_prod_0019.txt"""
import json, math, collections, statistics as st
D = __file__.rsplit('/', 1)[0] + '/'
T = '2026-11-17'
def ple(k, l): return sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(k + 1))
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3])) for r in json.load(open(D + 'store_sales_0019.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0019.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0019.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]   # cost, imp, click, LPV, atc, pur
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-27'
def band(lab, f, fm):
    t = f(T); xs = [f(d) for d in P]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('範囲の外（下）' if t < min(xs) else '範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/21 → {out}")
print('■ 店全体（0〜19時台・過去21日の同時刻）')
band('売上（値引後）', lambda d: SS[d][0], '{:,}')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('注文', lambda d: SS[d][1], '{}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('CPM', lambda d: MA[d][0] / MA[d][1] * 1000, '{:,.0f}')
band('着地÷表示%', lambda d: MA[d][3] / MA[d][1] * 100, '{:.2f}')
band('来訪÷着地', lambda d: SE[d][0] / MA[d][3], '{:.2f}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪 {SE[T][0]} × 過去21日の購入率 {cvr*100:.2f}% ＝ 期待 {lam:.1f}）・この数以下 {ple(SS[T][1], lam)*100:.0f}%")
F = [('表示÷広告費（CPMの逆）', lambda d: MA[d][1] / MA[d][0]), ('着地÷表示', lambda d: MA[d][3] / MA[d][1]), ('来訪÷着地', lambda d: SE[d][0] / MA[d][3]),
     ('注文÷来訪', lambda d: SS[d][1] / SE[d][0]), ('客単価', lambda d: SS[d][0] / SS[d][1])]
tot = math.log(SS[T][0] / MA[T][0]) - st.median(math.log(SS[d][0] / MA[d][0]) for d in P)
print(f"■ 売上÷広告費の差（過去21日の中央値比 {math.exp(tot)-1:+.0%}）の分け方（中央値の日と比べる）:")
for lab, f in F:
    m = st.median(math.log(f(d)) for d in P); lo = sum(f(d) < f(T) for d in P)
    print(f"  {lab}: {math.exp(math.log(f(T)) - m)-1:+.0%}（21日中 今日より低い日 {lo}）")
# 商品別
ALIAS = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール'}
NEW = {'スマートノーズEMS美顔器', '360°マルチクリップ車載スマホホルダー', '携帯電動シェーバー', '3WAY着る電気ブランケット', '裏起毛タッチ防寒グローブ', '快適マジックインソール'}
PS = collections.defaultdict(lambda: [0, 0])
for l in open(D + 'sales_prod_0019.txt'):
    if l[0] != '#': d, n, g, dc, o = l.strip().split(','); PS[(d, n)][0] += int(g) + int(dc); PS[(d, n)][1] += int(o)
MC = collections.defaultdict(lambda: [0] * 5)
for l in open(D + 'meta_camp_0019.txt'):
    if l[0] != '#':
        p = l.strip().split(','); n = ALIAS.get(p[1], p[1]); MC[(p[0], n)] = [a + int(b) for a, b in zip(MC[(p[0], n)], p[2:])]
P5 = [f'2026-11-{x}' for x in range(10, 15)]
today = sorted({n for (d, n) in MC if d == T and MC[(d, n)][0] > 0}, key=lambda n: -MC[(T, n)][0])
At = MA[T][0]; Ab = sum(MA[d][0] for d in P5)
print(f"■ 商品別（0〜19時台）。期待＝11/10〜14 の同時刻の 売上÷広告費 × 今日の広告費。取り分＝広告費に占める割合")
rows = []; gap = 0; exp_tot = 0
for n in today:
    a = MC[(T, n)][0]; s, o = PS.get((T, n), [0, 0]); im, lp, pu = MC[(T, n)][1], MC[(T, n)][2], MC[(T, n)][4]
    ab = sum(MC[(d, n)][0] for d in P5); sb = sum(PS.get((d, n), [0, 0])[0] for d in P5); ob = sum(PS.get((d, n), [0, 0])[1] for d in P5)
    lpb = sum(MC[(d, n)][2] for d in P5); imb = sum(MC[(d, n)][1] for d in P5)
    head = f"  {n}: 広告費 {a:,}（取り分 {a/At*100:.0f}%・11/10〜14 {ab/Ab*100:.0f}%）・売上 {s:,}・{o}注文・売上÷広告費 {s/a:.2f}"
    if n.startswith('カタログ'): print(head + '（売上は商品に分けられない）'); continue
    if n in NEW or not ab or not ob:
        print(head + f"（新しい商品・CPM {a/im*1000:,.0f}・着地/1万円 {lp/a*1e4:.0f}）" if im else head); exp_tot += s; continue
    e = sb / ab * a; lamo = ob / ab * a; p = ple(o, lamo) if o < lamo else 1 - ple(o - 1, lamo)
    gap += s - e; exp_tot += e
    print(head + f"・11/10〜14 {sb/ab:.2f}・期待の売上 {e:,.0f}・差 {s-e:+,.0f}・注文 期待 {lamo:.1f}（{'少ない' if o < lamo else '多い'}側 {p*100:.0f}%）・CPM {a/im*1000:,.0f}（{ab/imb*1000:,.0f}）・着地/1万円 {lp/a*1e4:.0f}（{lpb/ab*1e4:.0f}）")
other = SS[T][0] - sum(PS.get((T, n), [0, 0])[0] for n in today)
print(f"  広告を出していない商品・優先配送など: 売上 {other:,}")
print(f"■ まとめ: 以前からある商品が 11/10〜14 と同じ効率なら 今日の売上÷広告費は {(exp_tot+other)/At:.2f}（実際 {SS[T][0]/At:.2f}・以前からある商品の差の合計 {gap:+,.0f}円）")
sb_all = sum(SS[d][0] for d in P5); print(f"  参考: 11/10〜14 の店全体の売上÷広告費（0〜19時台）{sb_all/Ab:.2f}・過去21日の中央値 {st.median(SS[d][0]/MA[d][0] for d in P):.2f}")
