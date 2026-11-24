# -*- coding: utf-8 -*-
"""11/24 16時台「今日は単価低いのか、なぜ？」: 0〜15時台の 1注文の売上 を 1注文の個数 × 1個の値段 × (1−値引の割合) に分け、11/3〜11/23 の同じ時刻と比べる。
入力: sales_h15_raw.json（日別の注文・売上）・prod_h15_1124_raw.json／prod_h15_1103_1123_raw.json（商品別・LOOTY の商品だけ数える）・multi_h15_raw.json（2個以上の注文・LOOTY の商品だけ）"""
import json, os, re, collections, math, statistics as st
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'
nm = lambda t: re.sub(r'【[^】]*】', '', t).replace('LOOTY', '', 1).strip()
V = {r[0]: (int(r[1]), int(r[2]), -int(r[3])) for r in json.load(open(D0 + 'sales_h15_raw.json'))['rows']}
T = '2026-11-24'; past = [d for d in sorted(V) if d < T]
def prods(f): return [(nm(r[0]), int(r[1]), int(r[2]), -int(r[3]), int(r[4])) for r in json.load(open(D0 + f))['rows'] if 'LOOTY' in r[0]]
P1, P21 = prods('prod_h15_1124_raw.json'), prods('prod_h15_1103_1123_raw.json')
MU = collections.Counter(r[0] for r in json.load(open(D0 + 'multi_h15_raw.json'))['rows'])
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
def parts(rows, orders, gross_all, disc_all):
    g = sum(r[2] for r in rows); q = sum(r[4] for r in rows); hi = sum(r[4] for r in rows if r[4] and r[2] // r[4] >= 4980)
    return dict(aov=(gross_all - disc_all) / orders, ipo=q / orders, ppi=g / q, dr=disc_all / gross_all, hi=hi / q, q=q, hiq=hi)
o1, g1, d1 = V[T]; o21 = sum(V[d][0] for d in past); g21 = sum(V[d][1] for d in past); d21 = sum(V[d][2] for d in past)
a, b = parts(P1, o1, g1, d1), parts(P21, o21, g21, d21)
P('■ 0〜15時台の 1注文の売上 を分ける: 今日 ↔ 11/3〜11/23 の21日の合計')
P(f"  1注文の売上 {a['aov']:,.0f} ↔ {b['aov']:,.0f}（{a['aov']/b['aov']-1:+.1%}）")
P(f"  ＝ 1注文の個数 {a['ipo']:.2f} ↔ {b['ipo']:.2f}（{a['ipo']/b['ipo']-1:+.1%}）× 1個の値段（値引前）{a['ppi']:,.0f} ↔ {b['ppi']:,.0f}（{a['ppi']/b['ppi']-1:+.1%}）× 値引の割合 {a['dr']:.1%} ↔ {b['dr']:.1%}")
P(f"  4,980円以上の商品の個数の割合: {a['hi']:.0%}（{a['hiq']}/{a['q']}個） ↔ {b['hi']:.0%}（{b['hiq']}/{b['q']}個）")
m1 = MU[T]; m21 = sum(MU[d] for d in past); e = o1 * m21 / o21
lo = sum(math.exp(-e + i * math.log(e) - math.lgamma(i + 1)) for i in range(m1 + 1))
P(f"  2個以上の注文: {m1}/{o1}件（{m1/o1:.0%}） ↔ {m21}/{o21}件（{m21/o21:.0%}）→ 見込み {e:.1f}件・この数以下 {lo:.0%}")
# 4,980円以上の商品の、21日の内訳と今日
hi21 = collections.Counter(); 
for n, o, g, d, q in P21:
    if q and g // q >= 4980: hi21[n] += q
hi1 = {n: q for n, o, g, d, q in P1 if q and g // q >= 4980}
P('  21日の 4,980円以上の個数（多い順）: ' + '・'.join(f'{n} {q}' for n, q in hi21.most_common(12)) + ' ／ 今日: ' + '・'.join(f'{n} {q}' for n, q in hi1.items()))
eq = sum(hi21.values()) / o21 * o1; lo2 = sum(math.exp(-eq + i * math.log(eq) - math.lgamma(i + 1)) for i in range(sum(hi1.values()) + 1))
P(f"  4,980円以上の個数の見込み（21日の 個数÷注文 × 今日の注文 {o1}）{eq:.1f}個 → 実際 {sum(hi1.values())}個・この数以下 {lo2:.0%}（まとめ買いで個数はかたまるので、実際のぶれはこれより大きい）")
P('■ 日ごとの 1注文の売上（0〜15時台）: ' + '・'.join(f'{d[5:]} {(V[d][1]-V[d][2])/V[d][0]:,.0f}' for d in past + [T]))
# 今も広告を出している商品だけで見た 21日の 1注文の売上
P('  21日のうち、今は広告を止めている 4,980円以上の商品（洗車ブラシ 11/18・旧加湿器 11/12・チェア 11/11・ブランケット 11/18・シェーバー v2 11/20 など）の個数: ' + str(sum(q for n, q in hi21.items() if n in ('伸縮ワックス洗車ブラシ', 'コードレスダブルミスト加湿器', '姿勢サポートチェア', '3WAY着る電気ブランケット', '携帯電動シェーバー', 'ネックマッサージャー', 'ムダ毛シェーバー', '壁掛けディスペンサー', 'バランスケアスリッパ', '2WAYシートボックス', 'シリコンホールド膝サポーター'))) + f"個（21日の 4,980円以上 {sum(hi21.values())}個のうち）")
open(D0 + 'aov_h15.txt', 'w').write('\n'.join(out) + '\n')
# 今も広告を出している 4,980円以上の商品だけで見込みを出し直す
NOW = ('4-in-1マルチクリーナー', 'スマートノーズEMS美顔器', '充電式ダブルミスト卓上加湿器', 'コードレス毛玉クリーナー', 'UV歯ブラシ除菌器')
qn = sum(hi21[n] for n in NOW); e3 = qn / o21 * o1; k3 = sum(hi1.get(n, 0) for n in NOW)
lo3 = sum(math.exp(-e3 + i * math.log(e3) - math.lgamma(i + 1)) for i in range(k3 + 1))
P(f"■ 今も広告を出している 4,980円以上の商品（{'・'.join(NOW)}）だけで見ると: 21日 {qn}個 → 今日の見込み {e3:.1f}個・実際 {k3}個・この数以下 {lo3:.0%}")
e4 = hi21['4-in-1マルチクリーナー'] / o21 * o1; P(f"  うち 4-in-1: 見込み {e4:.1f}個・実際 0個・0個の確率 {math.exp(-e4):.0%}")
open(D0 + 'aov_h15.txt', 'w').write('\n'.join(out) + '\n')
